#!/usr/bin/env python3
"""Sensitivity of the reference rankings to the reward parameters (SI table).
Each parameter of r_S (E_thres, kappa) and r_DOS (a, b, E_win, s) is varied one at a time around the
values used in the paper; both rankings are recomputed from the same E_hull and DOS data and compared
with the reference ranking: #1 compound, its rank in the reference, top-15 overlap, Spearman correlation,
and the ranks of the synthesized U compounds. Writes reward_sensitivity.csv."""
import re, sys
from pathlib import Path
import h5py, numpy as np, pandas as pd
from scipy.stats import spearmanr
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from mcts_framework.intermetallic.dos_bandpass import bandpass_rdos, read_doscar
H = Path(__file__).resolve().parent; S = H.parent; DATA = S / "data"
N = 13
# DOS curves: lanthanides (f in core) from the projected-DOS file, U from the DOSCARs (as in the reward data)
dos = {}
with h5py.File(DATA / "projected_DOS.h5") as f:
    g = f["runs/RE_f_core"]; E = g["energy_eV"][:]; T = g["total_dos"][:]
    names = [x.decode() for x in g["metadata/formula_conventional"][:]]
    for n, t in zip(names, T):
        dos[n] = (E, t)
for key, path in pd.read_csv(DATA / "u_doscar_list.csv").itertuples(index=False):
    fe, x, m = key.split("-"); e, d, n = read_doscar(path); dos[f"{fe}{m}6{x}6"] = (e, d * N / n)
ref = pd.read_csv(S / "rankings/full_ranking.csv").set_index("compound")
missing = [c for c in ref.index if c not in dos]
print("DOS curves:", len(dos), "missing for ranking compounds:", len(missing), missing[:5])
ehull = np.where(ref.data_quality == "valid", ref.e_above_hull, 10.0)       # no hull (Yb): penalised as in the paper

def rdos_all(**kw):
    return np.array([bandpass_rdos(*dos[c], n_atoms=N, **kw)[0] if c in dos else 0.0 for c in ref.index])
base_rdos = rdos_all()
dev = np.abs(base_rdos - ref.r_dos.values)
print("reproduce stored r_DOS: max |diff| %.2e, n > 1e-3: %d" % (dev.max(), (dev > 1e-3).sum()))
if dev.max() > 1e-3:
    print(ref.assign(new=base_rdos, d=dev).sort_values("d").tail(5)[["r_dos", "new", "d"]])

isU = ref.f.values == "U"; idx = ref.index
SYN = ["UCr6Ge6", "UV6Sn6", "UCo6Ge6", "UNb6Sn6"]
def ranking(rd, et=0.054, kappa=120.0):
    r = np.exp(-np.tanh(kappa * (ehull - et))) * rd
    return pd.Series(r, index=idx)
def compare(new, refr, label, space):
    rn = new.rank(ascending=False, method="first"); rr = refr.rank(ascending=False, method="first")
    top = lambda s: set(s.sort_values(ascending=False).index[:15])
    row = {"space": space, "variation": label, "best": new.idxmax(), "best_ref_rank": int(rr[new.idxmax()]),
           "ref_best_new_rank": int(rn[refr.idxmax()]), "top15_overlap": len(top(new) & top(refr)),
           "spearman": spearmanr(new, refr).correlation}
    if space == "U":
        row.update({f"rank_{c}": int(rn[c]) for c in SYN})
    return row

base = ranking(base_rdos)
VAR = [("reference", {}, {})]
VAR += [(f"E_thres = {v:.2f} eV/atom", {}, {"et": v}) for v in (0.04, 0.05, 0.06, 0.07)]
VAR += [(f"kappa = {v:.0f} /eV", {}, {"kappa": v}) for v in (60, 240)]
VAR += [(f"a = {v:.3f} eV", {"smooth_ev": v}, {}) for v in (0.025, 0.1)]
VAR += [(f"b = {v:.2f} eV", {"background_ev": v}, {}) for v in (0.25, 1.0)]
VAR += [(f"E_win = {v:.2f} eV", {"window_ev": v}, {}) for v in (0.2, 0.4)]
VAR += [(f"s = {v:.2f} eV", {"sigma_ev": v}, {}) for v in (0.1, 0.2, 1e6)]
rows = []
for label, rkw, skw in VAR:
    rd = rdos_all(**rkw) if rkw else base_rdos
    new = ranking(rd, **skw)
    rows.append(compare(new, base, label, "full"))
    rows.append(compare(new[isU], base[isU], label, "U"))
out = pd.DataFrame(rows); out.to_csv(H / "reward_sensitivity.csv", index=False)
pd.set_option("display.width", 250)
print(out.round(3).to_string(index=False))
