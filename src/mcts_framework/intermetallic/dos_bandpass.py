"""
Band-pass electronic-structure reward computed directly from the DOS curve.

This is the "bandpass" rdos_method, a replacement for the peak-sum r_DOS in
``doscar.py`` (sum of height/width over extracted peaks). The peak-sum form
turned out to measure the DOSCAR energy-grid spacing rather than the physics:
every "peak" width came out as ~2 grid points, so h/w scaled with the grid
resolution of each calculation and flat, featureless DOS curves full of small
ripples scored highest. The band-pass form never extracts peaks or measures
widths:

    r_DOS = max_{|E| <= E_win} [ (D_a(E) - D_b(E)) * exp(-E^2 / (2 s^2)) ]_+

    D_a : total DOS per atom smoothed with a Gaussian of width a (0.05 eV)
    D_b : the same DOS smoothed with width b (0.50 eV) - the local background
    E   : energy relative to the Fermi level (eV)
    E_win = 0.30 eV search window, s = 0.15 eV proximity discount
    [ ]_+ : clipped at zero

D_a - D_b is a difference-of-Gaussians band-pass filter. At the centre of a
Gaussian feature of width w and unit height the response is

    w / sqrt(w^2 + a^2) - w / sqrt(w^2 + b^2)

i.e. ~0.6-0.7 for a feature narrower than ~0.3 eV, ~0.3 for one as wide as b
and ~0.1 for a 1 eV hump. Sharpness is therefore rewarded without ever
measuring a width; the background is removed locally; the max (not a sum)
scores one dominant feature instead of accumulating ripples; and the Gaussian
in E discounts features that sit off E_F. The DOS is per atom and on a uniform
eV grid, so values are comparable between calculations with different NEDOS,
energy ranges or codes. Typical values are 0-2.5 states/eV/atom.

Inputs accepted by :class:`BandpassDosRewardLookup` (see its docstring):
VASP DOSCAR files listed in a CSV, a long-format DOS CSV, the collaborator's
projected-DOS HDF5 export, or a CSV of precomputed rewards.

© 2026. Triad National Security, LLC. All rights reserved.
"""

from __future__ import annotations

import argparse
import logging
import math
from pathlib import Path
from typing import Dict, Iterable, Optional, Sequence, Tuple, Union

import numpy as np
import pandas as pd

from .doscar import DoscarRewardLookup

logger = logging.getLogger(__name__)

# Default parameters (eV). a < b is required; see module docstring.
SMOOTH_EV = 0.05
BACKGROUND_EV = 0.50
WINDOW_EV = 0.30
SIGMA_EV = 0.15
# Atoms per RM6X6 cell; DOS files are per cell, the reward is per atom.
N_ATOMS_RM6X6 = 13


# --- the equation --------------------------------------------------------


def gaussian_smooth(y: np.ndarray, sigma_pts: float) -> np.ndarray:
    """Gaussian-smooth a uniformly sampled 1-D array (edge-padded)."""
    if sigma_pts < 0.5:
        return np.asarray(y, dtype=float)
    radius = int(math.ceil(4 * sigma_pts))
    x = np.arange(-radius, radius + 1, dtype=float)
    kernel = np.exp(-0.5 * (x / sigma_pts) ** 2)
    kernel /= kernel.sum()
    padded = np.pad(np.asarray(y, dtype=float), radius, mode="edge")
    return np.convolve(padded, kernel, mode="valid")


def bandpass_response(width_ev: float, smooth_ev: float = SMOOTH_EV,
                      background_ev: float = BACKGROUND_EV) -> float:
    """Band-pass response at the centre of a unit-height Gaussian feature of the given width."""
    w = float(width_ev)
    return w / math.sqrt(w * w + smooth_ev ** 2) - w / math.sqrt(w * w + background_ev ** 2)


def bandpass_rdos(
    energy: np.ndarray,
    dos: np.ndarray,
    n_atoms: float = 1.0,
    *,
    smooth_ev: float = SMOOTH_EV,
    background_ev: float = BACKGROUND_EV,
    window_ev: float = WINDOW_EV,
    sigma_ev: float = SIGMA_EV,
) -> Tuple[float, float]:
    """
    Band-pass r_DOS of one DOS curve.

    Args:
        energy: energies relative to E_F (eV), ascending; need not be uniform.
        dos: total DOS at those energies (states/eV per cell).
        n_atoms: atoms per cell; the DOS is divided by this.
        smooth_ev, background_ev, window_ev, sigma_ev: see module docstring.

    Returns:
        (reward, e_peak): the reward in states/eV/atom (>= 0) and the energy
        at which the scored feature sits. (0.0, 0.0) if the window is empty.
    """
    if background_ev <= smooth_ev:
        raise ValueError("background_ev must exceed smooth_ev")
    E = np.asarray(energy, dtype=float)
    D = np.asarray(dos, dtype=float) / float(n_atoms)
    if E.ndim != 1 or E.shape != D.shape or E.size < 3:
        raise ValueError("energy and dos must be 1-D arrays of equal length >= 3")

    # Resample onto a uniform grid if needed (Gaussian widths are in samples).
    steps = np.diff(E)
    if steps.min() <= 0:
        raise ValueError("energy must be strictly ascending")
    if not np.allclose(steps, steps[0], rtol=1e-3, atol=1e-9):
        dE = float(steps.min())
        Eu = np.arange(E[0], E[-1] + 0.5 * dE, dE)
        D = np.interp(Eu, E, D)
        E = Eu
    dE = float(E[1] - E[0])

    excess = gaussian_smooth(D, smooth_ev / dE) - gaussian_smooth(D, background_ev / dE)
    in_window = np.abs(E) <= window_ev
    if not in_window.any():
        return 0.0, 0.0
    score = excess * np.exp(-0.5 * (E / sigma_ev) ** 2)
    score = np.where(in_window, score, -np.inf)
    i = int(np.argmax(score))
    return max(float(score[i]), 0.0), float(E[i])


# --- DOS readers ---------------------------------------------------------


def read_doscar(path: Union[str, Path]) -> Tuple[np.ndarray, np.ndarray, int]:
    """
    Read the total DOS block of a VASP DOSCAR.

    Returns (energy - E_F, total DOS, n_ions). Spin-polarised files (5
    columns: E, up, down, int_up, int_down) are summed over spin. Partial-DOS
    blocks after the total block are ignored.
    """
    with open(path) as fh:
        lines = fh.readlines()
    if len(lines) < 7:
        raise ValueError(f"{path}: not a DOSCAR (fewer than 7 lines)")
    n_ions = int(lines[0].split()[0])
    header = lines[5].split()
    nedos, efermi = int(header[2]), float(header[3])
    block = np.loadtxt(lines[6:6 + nedos])
    if block.ndim != 2 or block.shape[0] != nedos:
        raise ValueError(f"{path}: expected {nedos} DOS rows")
    energy = block[:, 0] - efermi
    if block.shape[1] >= 5:
        total = block[:, 1] + block[:, 2]
    else:
        total = block[:, 1]
    return energy, total, n_ions


def _read_h5_runs(path: Path, runs: Optional[Sequence[str]]):
    """Yield (key, energy, dos) from the projected-DOS HDF5 export, run by run."""
    try:
        import h5py
    except ImportError as exc:  # pragma: no cover - depends on environment
        raise ImportError("reading HDF5 DOS exports requires h5py (pip install h5py)") from exc
    with h5py.File(path, "r") as f:
        available = list(f["runs"].keys())
        chosen = list(runs) if runs else available
        missing = [r for r in chosen if r not in available]
        if missing:
            raise ValueError(f"{path}: runs {missing} not found; available: {available}")
        for run in chosen:
            g = f[f"runs/{run}"]
            energy = g["energy_eV"][:]
            dos = g["total_dos"][:]
            m = g["metadata"]
            dec = lambda a: [x.decode() if isinstance(x, bytes) else str(x) for x in a]  # noqa: E731
            keys = [f"{a}-{b}-{c}" for a, b, c in zip(dec(m["element_1"][:]), dec(m["element_2"][:]), dec(m["element_3"][:]))]
            for key, row in zip(keys, dos):
                yield run, key, energy, row


class BandpassDosRewardLookup(DoscarRewardLookup):
    """
    r_DOS lookup using the band-pass reward, keyed like :class:`DoscarRewardLookup`
    ('<f-block>-<group IV>-<metal>', e.g. 'Ce-Si-Ti'), so it drops into the
    same reward classes.

    ``source`` may be:

    * a CSV with columns ``COMPOUND_NAME, RDOS`` (precomputed rewards, e.g.
      written by :meth:`to_csv` or the module CLI); optional ``E_PEAK``;
    * a CSV with columns ``COMPOUND_NAME, DOSCAR`` listing one VASP DOSCAR
      file per compound (paths relative to the CSV's directory or absolute);
    * a long-format CSV with columns ``COMPOUND_NAME, ENERGY, DOS`` (energy
      relative to E_F in eV, DOS per cell), optional ``N_ATOMS``;
    * an HDF5 projected-DOS export (``runs/<run>/{energy_eV,total_dos,metadata}``),
      with ``run`` selecting one or more runs (all runs if None; the first run
      listed wins on duplicate keys).

    Missing or unreadable sources log a warning and yield 0.0 rewards, matching
    the peak-sum lookup's behaviour.
    """

    def __init__(
        self,
        source: Optional[Union[str, Path]] = None,
        *,
        run: Optional[Union[str, Sequence[str]]] = None,
        n_atoms: float = N_ATOMS_RM6X6,
        smooth_ev: float = SMOOTH_EV,
        background_ev: float = BACKGROUND_EV,
        window_ev: float = WINDOW_EV,
        sigma_ev: float = SIGMA_EV,
    ):
        self.rewards_dict: Dict[str, float] = {}
        self.peak_energy: Dict[str, float] = {}
        self.params = dict(smooth_ev=smooth_ev, background_ev=background_ev,
                           window_ev=window_ev, sigma_ev=sigma_ev)
        self.n_atoms = n_atoms
        if isinstance(run, str):
            run = [r.strip() for r in run.split(",") if r.strip()]
        self.runs = list(run) if run else None

        if source is None:
            logger.warning("No DOS source provided; rDOS rewards will be 0.0")
            return
        path = Path(source)
        if not path.exists():
            logger.warning("DOS source not found: %s; rDOS = 0.0", path)
            return
        try:
            self._load(path)
            logger.info("Computed %d band-pass DOS rewards from %s", len(self.rewards_dict), path)
        except Exception as exc:  # pragma: no cover - defensive, mirrors DoscarRewardLookup
            logger.error("Error computing band-pass DOS rewards: %s; rDOS = 0.0", exc)
            self.rewards_dict = {}
            self.peak_energy = {}

    # -- loading ----------------------------------------------------------

    def _score(self, key: str, energy: np.ndarray, dos: np.ndarray, n_atoms: Optional[float] = None) -> None:
        if key in self.rewards_dict:
            return  # first source wins
        r, e_peak = bandpass_rdos(energy, dos, self.n_atoms if n_atoms is None else n_atoms, **self.params)
        self.rewards_dict[key] = r
        self.peak_energy[key] = e_peak

    def _load(self, path: Path) -> None:
        if path.suffix.lower() in (".h5", ".hdf5"):
            for _run, key, energy, dos in _read_h5_runs(path, self.runs):
                self._score(key, energy, dos)
            return
        df = pd.read_csv(path)
        cols = set(df.columns)
        if {"COMPOUND_NAME", "RDOS"} <= cols:
            self.rewards_dict = dict(zip(df["COMPOUND_NAME"].astype(str), df["RDOS"].astype(float)))
            if "E_PEAK" in cols:
                self.peak_energy = dict(zip(df["COMPOUND_NAME"].astype(str), df["E_PEAK"].astype(float)))
        elif {"COMPOUND_NAME", "DOSCAR"} <= cols:
            for key, rel in zip(df["COMPOUND_NAME"].astype(str), df["DOSCAR"].astype(str)):
                fp = Path(rel)
                if not fp.is_absolute():
                    fp = path.parent / fp
                energy, dos, n_ions = read_doscar(fp)
                self._score(key, energy, dos, n_atoms=n_ions)
        elif {"COMPOUND_NAME", "ENERGY", "DOS"} <= cols:
            for key, g in df.groupby("COMPOUND_NAME", sort=False):
                g = g.sort_values("ENERGY")
                n = float(g["N_ATOMS"].iloc[0]) if "N_ATOMS" in cols else None
                self._score(str(key), g["ENERGY"].to_numpy(), g["DOS"].to_numpy(), n_atoms=n)
        else:
            raise ValueError(
                f"{path}: unrecognised columns {sorted(cols)}; expected COMPOUND_NAME with "
                "RDOS, DOSCAR, or ENERGY+DOS"
            )

    # -- export -----------------------------------------------------------

    def to_frame(self) -> pd.DataFrame:
        """Rewards as a DataFrame (COMPOUND_NAME, RDOS, E_PEAK)."""
        keys = list(self.rewards_dict)
        return pd.DataFrame({
            "COMPOUND_NAME": keys,
            "RDOS": [self.rewards_dict[k] for k in keys],
            "E_PEAK": [self.peak_energy.get(k, float("nan")) for k in keys],
        })

    def to_csv(self, path: Union[str, Path]) -> None:
        """Write a precomputed-rewards CSV that this class can load back."""
        self.to_frame().to_csv(path, index=False, float_format="%.6g")


# --- CLI: precompute a rewards CSV ----------------------------------------


def main(argv: Optional[Iterable[str]] = None) -> None:
    p = argparse.ArgumentParser(
        prog="python -m mcts_framework.intermetallic.dos_bandpass",
        description="Compute band-pass r_DOS for every compound in a DOS source and write "
                    "a COMPOUND_NAME,RDOS,E_PEAK CSV usable as doscar_data_path.",
    )
    p.add_argument("source", help="HDF5 export, DOSCAR-list CSV, or long-format DOS CSV")
    p.add_argument("-o", "--output", required=True, help="output CSV")
    p.add_argument("--run", default=None, help="HDF5 run(s), comma-separated (default: all)")
    p.add_argument("--n-atoms", type=float, default=N_ATOMS_RM6X6)
    p.add_argument("--smooth", type=float, default=SMOOTH_EV, help="a (eV)")
    p.add_argument("--background", type=float, default=BACKGROUND_EV, help="b (eV)")
    p.add_argument("--window", type=float, default=WINDOW_EV, help="E_win (eV)")
    p.add_argument("--sigma", type=float, default=SIGMA_EV, help="s (eV)")
    a = p.parse_args(None if argv is None else list(argv))
    lookup = BandpassDosRewardLookup(
        a.source, run=a.run, n_atoms=a.n_atoms, smooth_ev=a.smooth,
        background_ev=a.background, window_ev=a.window, sigma_ev=a.sigma,
    )
    if not lookup.rewards_dict:
        raise SystemExit(f"no rewards computed from {a.source}")
    lookup.to_csv(a.output)
    print(f"wrote {len(lookup.rewards_dict)} rewards to {a.output}")


if __name__ == "__main__":  # pragma: no cover
    main()
