"""
Tests for the band-pass r_DOS (dos_bandpass.py): the equation on synthetic
curves, the DOSCAR reader, and the lookup's input formats.

© 2026. Triad National Security, LLC. All rights reserved.
"""

import numpy as np
import pandas as pd
import pytest

from mcts_framework.intermetallic.dos_bandpass import (
    BandpassDosRewardLookup,
    bandpass_rdos,
    bandpass_response,
    read_doscar,
)
from mcts_framework.intermetallic.rewards import RdosReward, create_intermetallic_reward

E = np.linspace(-3.0, 3.0, 1201)  # 0.005 eV grid


def gauss(x, mu, w):
    return np.exp(-0.5 * ((x - mu) / w) ** 2)


# --- the equation --------------------------------------------------------


def test_flat_dos_scores_zero():
    r, _ = bandpass_rdos(E, np.full_like(E, 0.7))
    assert r == pytest.approx(0.0, abs=1e-9)


def test_dip_at_fermi_scores_near_zero():
    # The shoulders of a dip show a small positive excess over the broad
    # background, so the score is not exactly 0 - but it must be tiny next to
    # a peak of the same depth (~0.7).
    r, _ = bandpass_rdos(E, 1.0 - 0.8 * gauss(E, 0.0, 0.1))
    assert r < 0.05


def test_sharp_peak_matches_closed_form_response():
    # A unit-height Gaussian of width 0.1 eV on a flat background: the band-pass
    # response at its centre is bandpass_response(0.1) ~ 0.70, and the
    # background cancels exactly.
    r, e_peak = bandpass_rdos(E, 0.5 + 1.0 * gauss(E, 0.0, 0.1))
    assert r == pytest.approx(bandpass_response(0.1), rel=0.03)
    assert abs(e_peak) < 0.01


def test_sharpness_ordering():
    sharp = bandpass_rdos(E, 0.5 + gauss(E, 0.0, 0.1))[0]
    medium = bandpass_rdos(E, 0.5 + gauss(E, 0.0, 0.5))[0]
    hump = bandpass_rdos(E, 0.5 + gauss(E, 0.0, 1.0))[0]
    assert sharp > medium > hump > 0
    assert hump < 0.15  # a 1 eV hump passes with ~10 % of its height


def test_off_fermi_peak_is_discounted_and_located():
    on = bandpass_rdos(E, 0.5 + gauss(E, 0.0, 0.1))[0]
    r, e_peak = bandpass_rdos(E, 0.5 + gauss(E, 0.25, 0.1))
    # e_peak is where the *discounted* score is largest, which the proximity
    # weight pulls from the feature centre (0.25) toward E_F.
    assert 0.1 < e_peak < 0.25
    assert r < 0.5 * on
    # outside the search window the feature is not scored at all
    r_out, _ = bandpass_rdos(E, 0.5 + gauss(E, 0.8, 0.1))
    assert r_out == pytest.approx(0.0, abs=1e-6)


def test_max_not_sum_ignores_ripples():
    # Many small ripples on a flat DOS (the EuCu6Sn6 failure mode of the
    # peak-sum reward) must not accumulate.
    ripples = 0.5 + 0.05 * np.sin(E / 0.02)
    assert bandpass_rdos(E, ripples)[0] < 0.1


def test_per_atom_normalisation():
    r1 = bandpass_rdos(E, 13 * (0.5 + gauss(E, 0.0, 0.1)), n_atoms=13)[0]
    r2 = bandpass_rdos(E, 0.5 + gauss(E, 0.0, 0.1), n_atoms=1)[0]
    assert r1 == pytest.approx(r2, rel=1e-9)


def test_non_uniform_grid_is_resampled():
    uniform = bandpass_rdos(E, 0.5 + gauss(E, 0.0, 0.1))[0]
    E2 = np.sort(np.concatenate([E[::2], np.array([0.0012, 0.0037])]))
    r = bandpass_rdos(E2, 0.5 + gauss(E2, 0.0, 0.1))[0]
    assert r == pytest.approx(uniform, rel=0.05)


def test_parameter_validation():
    with pytest.raises(ValueError):
        bandpass_rdos(E, np.ones_like(E), smooth_ev=0.6, background_ev=0.5)
    with pytest.raises(ValueError):
        bandpass_rdos(E[::-1], np.ones_like(E))


# --- DOSCAR reader -------------------------------------------------------


def _write_doscar(path, spin_polarised, efermi=8.5, n_ions=13):
    e = np.linspace(-5.0, 5.0, 201) + efermi
    dos = 2.0 + 10.0 * gauss(e - efermi, 0.0, 0.1)
    rows = []
    for ei, di in zip(e, dos):
        if spin_polarised:
            rows.append(f"{ei:.4f} {0.6 * di:.5f} {0.4 * di:.5f} 0 0")
        else:
            rows.append(f"{ei:.4f} {di:.5f} 0")
    header = [f"  {n_ions}  {n_ions}   1   0", " 0.1E+02 0.5E-09 0.5E-09 0.8E-09 0.5E-15",
              " 1.0E-004", "  CAR ", " Test", f" {e[-1]:.6f} {e[0]:.6f} {len(e)} {efermi:.6f} 1.0"]
    path.write_text("\n".join(header + rows + [" trailing partial-DOS block header", "0 0 0"]) + "\n")
    return dos


@pytest.mark.parametrize("spin", [False, True])
def test_read_doscar(tmp_path, spin):
    p = tmp_path / "DOSCAR"
    dos = _write_doscar(p, spin)
    energy, total, n_ions = read_doscar(p)
    assert n_ions == 13
    assert energy[0] == pytest.approx(-5.0) and energy[-1] == pytest.approx(5.0)
    assert np.allclose(total, dos, atol=1e-3)


# --- lookup inputs -------------------------------------------------------


def test_lookup_from_doscar_list(tmp_path):
    _write_doscar(tmp_path / "DOSCAR_1", False)
    _write_doscar(tmp_path / "DOSCAR_2", True)
    pd.DataFrame({"COMPOUND_NAME": ["Ce-Si-Ti", "U-Pb-W"], "DOSCAR": ["DOSCAR_1", "DOSCAR_2"]}).to_csv(
        tmp_path / "list.csv", index=False)
    lookup = BandpassDosRewardLookup(tmp_path / "list.csv")
    assert set(lookup.rewards_dict) == {"Ce-Si-Ti", "U-Pb-W"}
    # 10-high peak of width 0.1 on 13 atoms -> ~ 10 * 0.70 / 13
    assert lookup.get_reward("Ti6Si6Ce") == pytest.approx(10 * bandpass_response(0.1) / 13, rel=0.05)
    assert lookup.get_reward("W6Pb6U") == pytest.approx(lookup.get_reward("Ti6Si6Ce"), rel=0.05)
    assert lookup.get_reward("Fe2O3") == 0.0


def test_lookup_from_long_csv_and_roundtrip(tmp_path):
    rows = []
    for name, h in (("Ce-Si-Ti", 1.0), ("Nd-Sn-Fe", 3.0)):
        for e, d in zip(E, 0.5 + h * gauss(E, 0.0, 0.1)):
            rows.append((name, e, d, 1))
    pd.DataFrame(rows, columns=["COMPOUND_NAME", "ENERGY", "DOS", "N_ATOMS"]).to_csv(tmp_path / "dos.csv", index=False)
    lookup = BandpassDosRewardLookup(tmp_path / "dos.csv")
    assert lookup.get_reward("Fe6Sn6Nd") == pytest.approx(3 * lookup.get_reward("Ti6Si6Ce"), rel=0.02)

    lookup.to_csv(tmp_path / "rewards.csv")
    reloaded = BandpassDosRewardLookup(tmp_path / "rewards.csv")
    assert reloaded.rewards_dict == pytest.approx(lookup.rewards_dict, rel=1e-5)
    assert reloaded.peak_energy["Ce-Si-Ti"] == pytest.approx(0.0, abs=0.01)


def test_lookup_missing_source_is_zero(tmp_path):
    assert BandpassDosRewardLookup(None).get_reward("Ti6Si6Ce") == 0.0
    assert BandpassDosRewardLookup(tmp_path / "nope.csv").get_reward("Ti6Si6Ce") == 0.0


def test_lookup_rejects_unknown_csv(tmp_path):
    pd.DataFrame({"a": [1]}).to_csv(tmp_path / "bad.csv", index=False)
    # error is logged and swallowed, rewards stay empty
    assert BandpassDosRewardLookup(tmp_path / "bad.csv").rewards_dict == {}


def test_lookup_from_h5_runs(tmp_path):
    h5py = pytest.importorskip("h5py")
    with h5py.File(tmp_path / "dos.h5", "w") as f:
        for run, els, height in (("RE_f_core", [("Ce", "Si", "Ti")], 1.0),
                                 ("U_f_core", [("U", "Pb", "W"), ("U", "Sn", "Ti")], 2.0)):
            g = f.create_group(f"runs/{run}")
            g["energy_eV"] = E
            g["total_dos"] = np.array([13 * (0.5 + height * gauss(E, 0.0, 0.1))] * len(els))
            m = g.create_group("metadata")
            for i in range(3):
                m[f"element_{i + 1}"] = np.array([e[i].encode() for e in els])
    both = BandpassDosRewardLookup(tmp_path / "dos.h5")
    assert set(both.rewards_dict) == {"Ce-Si-Ti", "U-Pb-W", "U-Sn-Ti"}
    u_only = BandpassDosRewardLookup(tmp_path / "dos.h5", run="U_f_core")
    assert set(u_only.rewards_dict) == {"U-Pb-W", "U-Sn-Ti"}
    assert u_only.get_reward("W6Pb6U") == pytest.approx(2 * both.get_reward("Ti6Si6Ce"), rel=0.02)
    with pytest.raises(Exception):
        list(__import__("mcts_framework.intermetallic.dos_bandpass", fromlist=["_read_h5_runs"])
             ._read_h5_runs(tmp_path / "dos.h5", ["nope"]))


# --- plugs into the existing reward classes ------------------------------


def test_reward_classes_accept_bandpass_lookup(tmp_path):
    rows = [("Ce-Si-Ti", e, d, 1) for e, d in zip(E, 0.5 + gauss(E, 0.0, 0.1))]
    pd.DataFrame(rows, columns=["COMPOUND_NAME", "ENERGY", "DOS", "N_ATOMS"]).to_csv(tmp_path / "dos.csv", index=False)
    lookup = BandpassDosRewardLookup(tmp_path / "dos.csv")
    assert isinstance(create_intermetallic_reward("rdos", lookup), RdosReward)
    r = create_intermetallic_reward("ehull_rdos_product_exponential", lookup)
    stable = r.compute_reward({"e_above_hull": 0.0, "formula": "Ti6Si6Ce"})
    unstable = r.compute_reward({"e_above_hull": 0.5, "formula": "Ti6Si6Ce"})
    assert stable == pytest.approx(np.e * lookup.get_reward("Ti6Si6Ce"), rel=1e-3)
    assert unstable == pytest.approx(np.exp(-1) * lookup.get_reward("Ti6Si6Ce"), rel=1e-3)
