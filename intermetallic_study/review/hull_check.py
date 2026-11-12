#!/usr/bin/env python3
"""E_hull reference check for the RM6X6 compounds.

1. 'old'  : the hull the search used, rebuilt as the code builds it (every MP thermo
            document of the chemical system and its subsystems, the r2SCAN entry when a
            document has one, GGA/GGA+U otherwise, all in one PhaseDiagram).
            Checked against the cached e_decomp of every compound.
2. 'gga'  : a consistent hull from the GGA/GGA+U thermo documents only (PBE level,
            MP2020-corrected entries), the reference MACE-MP-0 was trained on.
            E_hull = E_MACE(total, per atom) - E_hull_surface(composition), with the
            MACE total energy recovered from e_form and the matbench-discovery
            elemental reference energies used to compute e_form.
3. DFT    : E_hull_DFT = E_form_DFT - e_decomp_gga, i.e. the DFT formation energy of the
            RM6X6 compound placed on the same GGA hull of competing phases.
Writes hull_check.csv (one row per compound).
"""
import json, re, warnings
from pathlib import Path
import numpy as np, pandas as pd
warnings.filterwarnings("ignore")
from monty.json import MontyDecoder
from pymatgen.analysis.phase_diagram import PhaseDiagram
from pymatgen.core import Composition
from pymatgen.entries.computed_entries import ComputedEntry
from matbench_discovery.energy import mp_elemental_ref_energies as MBREF

H = Path(__file__).resolve().parent; S = H.parent; DATA = S / "data"
docs = {}
for l in open(H / "mp_thermo_docs.jsonl"):
    d = json.loads(l); docs[d["chemsys"]] = d["docs"]
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from mcts_framework.intermetallic import evaluator as _ev
_cls = [v for v in vars(_ev).values() if isinstance(v, type) and hasattr(v, "_setup_msonable_redirects")][0]
_cls._setup_msonable_redirects()          # the same deserialization shims the search code uses
dec = MontyDecoder()


def _fix_modules(d):
    """MP thermo documents serialize entries and energy adjustments under the old module
    path 'pymatgen.core.entries'; without remapping, the adjustments stay dicts, the
    entry energy cannot be computed and the entry is dropped from the hull."""
    if isinstance(d, dict):
        d = {k: _fix_modules(v) for k, v in d.items()}
        if d.get("@module") == "pymatgen.core.entries":
            d["@module"] = "pymatgen.entries.computed_entries"
        return d
    if isinstance(d, list):
        return [_fix_modules(v) for v in d]
    return d
_cache = {}


def entries(cs, mode):
    key = (cs, mode)
    if key in _cache:
        return _cache[key]
    out = []
    for doc in docs[cs]:
        if mode == "gga" and doc.get("thermo_type") != "GGA_GGA+U":
            continue
        for rt in (["r2SCAN", "GGA+U", "GGA", "GGA(+U)"] if mode == "old" else ["GGA+U", "GGA", "GGA(+U)"]):
            if rt in doc["entries"]:
                try:
                    e = dec.process_decoded(_fix_modules(doc["entries"][rt]))
                except Exception:
                    continue
                if hasattr(e, "energy_per_atom"):     # the search code skips undecodable entries the same way
                    out.append(e); break
    if mode == "gga":   # one entry per entry_id
        seen, uniq = set(), []
        for e in out:
            k = (str(e.entry_id), e.composition.reduced_formula, round(e.energy_per_atom, 6))
            if k not in seen:
                seen.add(k); uniq.append(e)
        out = uniq
    _cache[key] = out
    return out


def phase_diagram(els, mode):
    els = sorted(els); systems = ["-".join(els)] + els + ["-".join(sorted(p)) for p in
                                                           [(els[0], els[1]), (els[0], els[2]), (els[1], els[2])]]
    es = [e for cs in systems for e in entries(cs, mode)]
    try:
        return PhaseDiagram(es) if es else None
    except ValueError:          # e.g. no elemental Yb entry in MP: no hull, as in the search
        return None


cache = pd.read_csv(DATA / "mace_cache_mixed_hull.csv")   # MACE e_form and the E_hull values of the earlier, mixed r2SCAN/GGA hull
def ckey(f):
    els = dict(re.findall(r"([A-Z][a-z]?)(\d*)", f))
    giv = [e for e in els if e in ("Si", "Ge", "Sn", "Pb")][0]; m = [e for e in els if els[e] == "6" and e != giv][0]
    fb = [e for e in els if els[e] in ("", "1")][0]; return fb, m, giv
cache[["R", "M", "X"]] = cache.name.apply(lambda f: pd.Series(ckey(f)))
cache["compound"] = cache.R + cache.M + "6" + cache.X + "6"
RALL = ["La", "Ce", "Pr", "Nd", "Pm", "Sm", "Eu", "Gd", "Tb", "Dy", "Ho", "Er", "Tm", "Yb", "Lu", "U"]
cache = cache[cache.R.isin(RALL)]
cache = cache.drop_duplicates("compound").set_index("compound")

rows = []
for i, (c, r) in enumerate(cache.iterrows()):
    comp = Composition(f"{r.R}1{r.M}6{r.X}6"); els = [r.R, r.M, r.X]
    row = {"compound": c, "R": r.R, "M": r.M, "X": r.X, "e_form_mace": r.e_form, "e_hull_cache": r.e_above_hull,
           "e_decomp_cache": r.e_decomp, "dq": r.data_quality}
    for mode in ("old", "gga"):
        pd_ = phase_diagram(els, mode)
        if pd_ is None or not all(el in [str(x) for x in pd_.elements] for el in els):
            row[f"e_decomp_{mode}"] = np.nan; row[f"hull_E_{mode}"] = np.nan; continue
        dcmp = pd_.get_decomposition(comp)
        row[f"e_decomp_{mode}"] = sum(pd_.get_form_energy_per_atom(e) * f for e, f in dcmp.items())
        row[f"hull_E_{mode}"] = pd_.get_hull_energy_per_atom(comp)
        if mode == "gga":
            pdu = PhaseDiagram([ComputedEntry(e.composition, e.uncorrected_energy, entry_id=str(e.entry_id)) for e in pd_.all_entries])
            row["hull_E_gga_uncorr"] = pdu.get_hull_energy_per_atom(comp)
        row[f"elref_{mode}"] = sum(comp.get_atomic_fraction(el) * pd_.el_refs[el].energy_per_atom for el in comp.elements)
        row[f"n_entries_{mode}"] = len(pd_.all_entries)
    rows.append(row)
    if i % 200 == 0:
        print(i, flush=True)
df = pd.DataFrame(rows)
mb = lambda r: sum(Composition(f"{r.R}1{r.M}6{r.X}6").get_atomic_fraction(el) * MBREF[str(el)] for el in Composition(f"{r.R}1{r.M}6{r.X}6").elements)
df["elref_mb"] = df.apply(mb, axis=1)
df["E_tot_mace"] = df.e_form_mace + df.elref_mb                       # MACE total energy per atom
df["e_hull_old_recon"] = df.e_form_mace - df.e_decomp_old
from pymatgen.entries.compatibility import MaterialsProject2020Compatibility
from pymatgen.entries.computed_entries import ComputedEntry
_compat = MaterialsProject2020Compatibility(check_potcar=False)
def _corr(r):
    c = Composition(f"{r.R}1{r.M}6{r.X}6")
    out = _compat.process_entry(ComputedEntry(c, r.E_tot_mace * c.num_atoms, parameters={"run_type": "GGA", "hubbards": {}, "is_hubbard": False}))
    return np.nan if out is None else out.correction / c.num_atoms
df["mp2020_corr"] = df.apply(_corr, axis=1)
df["e_hull_gga"] = df.E_tot_mace + df.mp2020_corr - df.hull_E_gga       # MP2020-corrected on both sides (matbench-discovery convention)
df["e_hull_gga_uncorr"] = df.E_tot_mace - df.hull_E_gga_uncorr          # no corrections on either side
df["e_hull_gga_formref"] = df.e_form_mace - df.e_decomp_gga           # same, using the hull's own elemental refs
# DFT formation energies (lanthanides f in core, uranium f in valence, as in the parity figure)
par = pd.read_csv(DATA / "formation_energy_parity_dft_vs_mace.csv")
par = par[par.run.isin(["RE_f_core", "U_f_valence"])].drop_duplicates("compound").set_index("compound")
df = df.join(par[["dft", "mace", "suspect"]].rename(columns={"dft": "e_form_dft", "mace": "e_form_mace_parity"}), on="compound")
df["e_hull_dft_gga"] = df.e_form_dft + df.mp2020_corr - df.e_decomp_gga
df["e_hull_dft_old"] = df.e_form_dft - df.e_decomp_old
df.to_csv(H / "hull_check.csv", index=False, float_format="%.6g")
print("wrote hull_check.csv", len(df))
