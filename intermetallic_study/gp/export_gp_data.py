#!/usr/bin/env python3
"""Export the data files behind the run-independent gnuplot figures into gp/data/."""
import json, re
from pathlib import Path
import h5py, numpy as np, pandas as pd
from scipy.ndimage import gaussian_filter1d
from mcts_framework.intermetallic.dos_bandpass import (bandpass_response, read_doscar, SMOOTH_EV, BACKGROUND_EV, WINDOW_EV, SIGMA_EV)
from mcts_framework.intermetallic.rewards import ehull_reward
G = Path(__file__).resolve().parent; H = G.parent; DATA = H / "data"; D = G / "data"; D.mkdir(exist_ok=True)
TM_ORDER = ["Ti","V","Cr","Mn","Fe","Co","Ni","Cu","Zn","Zr","Nb","Mo","Tc","Ru","Rh","Pd","Ag","Cd","Hf","Ta","W","Re","Os","Ir","Pt","Au","Hg"]
RE_ORDER = ["La","Ce","Pr","Nd","Pm","Sm","Eu","Gd","Tb","Dy","Ho","Er","Tm","Yb","Lu"]; X_ORDER = ["Si","Ge","Sn","Pb"]
N_ATOMS = 13

with h5py.File(DATA / "projected_DOS.h5") as f:
    g = f["runs/RE_f_core"]; E = g["energy_eV"][:]; RE_TOT = g["total_dos"][:] / N_ATOMS; RE_EL = g["element_pdos"][:] / N_ATOMS
    dec = lambda a: [x.decode() for x in a]
    RE_META = pd.DataFrame({"compound": dec(g["metadata/formula_conventional"][:]), "f": dec(g["metadata/element_1"][:]), "X": dec(g["metadata/element_2"][:]), "M": dec(g["metadata/element_3"][:])})
    gu = f["runs/U_f_core"]; U_EL = gu["element_pdos"][:] / N_ATOMS; U_META = pd.DataFrame({"compound": dec(gu["metadata/formula_conventional"][:])})
U_RAW = {}
for key, path in pd.read_csv(DATA / "u_doscar_list.csv").itertuples(index=False):
    f_, x_, m_ = key.split("-"); e, d, n = read_doscar(path); U_RAW[f"{f_}{m_}6{x_}6"] = (e, d / n)
rank_u = pd.read_csv(H / "rankings/u_only_ranking.csv").set_index("compound"); rank_f = pd.read_csv(H / "rankings/full_ranking.csv").set_index("compound")

def curve(c):
    """(E on a uniform grid, total DOS, {f,M,X} projections interpolated onto E) per atom."""
    if c.startswith("U"):
        e, tot = U_RAW[c]; i = U_META.index[U_META.compound == c][0]; src = (E, U_EL[i])
    else:
        i = RE_META.index[RE_META.compound == c][0]; e, tot = E, RE_TOT[i]; src = (E, RE_EL[i])
    dE = np.diff(e).min(); eu = np.arange(e[0], e[-1], dE); tot = np.interp(eu, e, tot)
    proj = {r: np.interp(eu, src[0], src[1][k]) for k, r in ((0, "f"), (1, "X"), (2, "M"))}
    return eu, tot, proj

def scored(e, dos):
    dE = e[1] - e[0]; fine = gaussian_filter1d(dos, SMOOTH_EV / dE, mode="nearest"); bg = gaussian_filter1d(dos, BACKGROUND_EV / dE, mode="nearest")
    return fine, bg, np.clip(fine - bg, 0, None) * np.exp(-0.5 * (e / SIGMA_EV) ** 2) * (np.abs(e) <= WINDOW_EV)

def write_dos(c, name=None):
    e, tot, pr = curve(c); fine, bg, exc = scored(e, tot)
    np.savetxt(D / f"dos_{name or c}.dat", np.c_[e, fine, bg, exc, pr["f"], pr["M"], pr["X"], tot], fmt="%.5f", header="E fine_dos bg excess f_proj M_proj X_proj raw_dos")
    return c

# Fig 3
eh = np.linspace(-0.05, 0.2, 400); np.savetxt(D / "rS.dat", np.c_[eh, np.exp([ehull_reward(x, 0.054) for x in eh])], fmt="%.5f")
write_dos("DyFe6Sn6")
# DOS candidates (top 3 U, top 3 full) and trend panels
cands = {"u": rank_u.sort_values("rank").index[:3].tolist(), "f": rank_f.sort_values("rank").index[:3].tolist()}
for c in cands["u"] + cands["f"]: write_dos(c)
for r in RE_ORDER: write_dos(f"{r}Fe6Sn6")
for x in X_ORDER: write_dos(f"DyFe6{x}6")
for c in ["UFe6Sn6", "UTc6Ge6", "DyTc6Ge6", "UCr6Ge6", "UV6Sn6", "UCo6Ge6", "UNb6Sn6", "TmHg6Ge6", "EuCu6Sn6", "PmMn6Sn6"]: write_dos(c)   # PmMn6Sn6: band-structure compound
meta = {"cands": cands, "rank": {}}
for c in set(cands["u"] + cands["f"] + [f"{r}Fe6Sn6" for r in RE_ORDER] + [f"DyFe6{x}6" for x in X_ORDER] + ["UFe6Sn6","UTc6Ge6","DyTc6Ge6","UCr6Ge6","UV6Sn6","UCo6Ge6","UNb6Sn6","TmHg6Ge6","EuCu6Sn6","PmMn6Sn6"]):
    r = (rank_u if c.startswith("U") else rank_f).loc[c]; meta["rank"][c] = {"rank": int(r["rank"]), "r_dos": float(r.r_dos), "e_hull": float(r.e_above_hull)}
json.dump(meta, open(D / "dos_meta.json", "w"), indent=1)
# gnuplot-readable macros with labels for the DOS panels
lines = []
for c, v in meta["rank"].items():
    lines.append(f'LAB_{c} = "r_{{DOS}} = {v["r_dos"]:.2f}\\nE_{{hull}} = {v["e_hull"]:.3f}\\nrank {v["rank"]}"')
    lines.append(f'RDOS_{c} = {v["r_dos"]:.3f}'); lines.append(f'EHULL_{c} = {v["e_hull"]:.3f}'); lines.append(f'RANK_{c} = {v["rank"]}')
for k, lst in cands.items():
    for i, c in enumerate(lst): lines.append(f'CAND_{k}{i+1} = "{c}"')
(D / "dos_labels.gp").write_text("\n".join(lines) + "\n")

# SI heatmap: binary float32 array (801 x 1620), rows grouped by M, then X, then R
order = RE_META.assign(mi=RE_META.M.map(TM_ORDER.index), xi=RE_META.X.map(X_ORDER.index), fi=RE_META.f.map(RE_ORDER.index)).sort_values(["mi","xi","fi"]).index
np.clip(RE_TOT[order], 0, np.percentile(RE_TOT, 98)).astype("float32").tofile(D / "dos_heatmap.bin")
(D / "dos_heatmap_meta.txt").write_text(f"{len(E)} {len(order)} {E[0]:.4f} {E[1]-E[0]:.5f} {np.percentile(RE_TOT, 98):.4f}\n")
# by-TM: per M file with E, median, then the 60 curves ordered X (Si,Ge,Sn,Pb) x R
for tm in TM_ORDER:
    sub = RE_META[RE_META.M == tm].assign(xi=lambda d: d.X.map(X_ORDER.index), fi=lambda d: d.f.map(RE_ORDER.index)).sort_values(["xi", "fi"])
    np.savetxt(D / f"tm_{tm}.dat", np.c_[E, np.median(RE_TOT[sub.index], axis=0), RE_TOT[sub.index].T], fmt="%.4f")
(D / "tm_medians.gp").write_text("\n".join(f'MED_{tm} = {rank_f[rank_f.M == tm].r_dos.median():.2f}' for tm in TM_ORDER) + "\n")
# band-pass response
w = np.linspace(0.01, 1.5, 300); np.savetxt(D / "bandpass_response.dat", np.c_[w, [bandpass_response(x) for x in w]], fmt="%.5f")
# c sweep summary: c quartile mean sem per metric
cs = pd.read_csv(H / "run_metrics_csweep.csv")
for q in ["0-25", "25-50", "50-75", "75-100"]:
    m = cs[cs.quartile == q].groupby("c").agg(fb=("found_best","mean"), fbs=("found_best","sem"), r=("mean_rank_top15","mean"), rs=("mean_rank_top15","sem"), x=("frac_explored","mean"), xs=("frac_explored","sem")).fillna(0)
    np.savetxt(D / f"csweep_{q}.dat", m.reset_index().to_numpy(), fmt="%.5f", header="c found sem rank15 sem explored sem")
# parity (lanthanides f-core, U f-valence) from the DFT formation-energy comparison
par = pd.read_csv(DATA / "formation_energy_parity_dft_vs_mace.csv")
for run in ["RE_f_core", "U_f_valence"]:
    s = par[par.run == run]; np.savetxt(D / f"parity_{run}.dat", s[["dft", "mace"]].to_numpy(), fmt="%.5f")
    err = s.mace - s.dft; r2 = 1 - (err**2).sum() / ((s.dft - s.dft.mean())**2).sum()
    (D / f"parity_{run}.gp").write_text(f'N_{run} = {len(s)}\nMAE_{run} = {1000*err.abs().mean():.0f}\nRMSE_{run} = {1000*np.sqrt((err**2).mean()):.0f}\nR2_{run} = {r2:.2f}\nRHO_{run} = {s.dft.corr(s.mace, method="spearman"):.2f}\n')
print("exported to", D)
