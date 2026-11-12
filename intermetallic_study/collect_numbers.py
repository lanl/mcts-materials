#!/usr/bin/env python3
"""Every number the v3 manuscript text needs, from the v3 results. Writes tables/numbers_v3.json."""
import json, re
from pathlib import Path
import numpy as np, pandas as pd

H = Path(__file__).resolve().parent
u = pd.read_csv(H / "rankings/u_only_ranking.csv").set_index("compound")
f = pd.read_csv(H / "rankings/full_ranking.csv").set_index("compound")
rep = json.load(open(H / "tables/text_numbers_representative.json"))
b = pd.read_csv(H / "budget_metrics.csv")
N = {"rep": rep}

# --- reference rankings
N["u_stable"] = int((u[u.data_quality == "valid"].e_above_hull < 0.054).sum())
N["f_stable"] = int((f[f.data_quality == "valid"].e_above_hull < 0.054).sum())
N["U_best_full_rank"] = int(f.loc["UTc6Ge6", "rank"])
N["max_rdos_lanthanide"] = float(f[f.f != "U"].r_dos.max()); N["max_rdos_U"] = float(u.r_dos.max())
N["max_rdos_stable"] = float(f[(f.e_above_hull < 0.054) & (f.data_quality == "valid")].r_dos.max())
top50 = f.sort_values("rank").head(50)
N["top50_M"] = top50.M.value_counts().to_dict(); N["top50_X"] = top50.X.value_counts().to_dict()
N["rewards_U_max"] = float(u.reward.max()); N["U_zero_reward"] = int((u.reward < 1e-3).sum())
syn = ["UCr6Ge6", "UV6Sn6", "UCo6Ge6", "UNb6Sn6"]
N["synth"] = {c: {"rank": int(u.loc[c, "rank"]), "ehull": float(u.loc[c, "e_above_hull"])} for c in syn}
fail = u[u.synthesized == "No"]
N["failed_top30"] = int((fail["rank"] <= 30).sum()); N["failed_ranks"] = fail.sort_values("rank")["rank"].astype(int).head(6).to_dict()
none = u[u.synthesized == "--"]; N["not_attempted"] = int(len(none)); N["not_attempted_outside30"] = int((none["rank"] > 30).sum())
N["n_failed"] = int(len(fail))
# --- literature compounds
lit = []
for l in (H / "data/experimental_compounds.txt").read_text().splitlines():
    m = re.match(r"\s*\d+\s+([A-Z][a-z]?)-([A-Z][a-z]?)-([A-Z][a-z]?)\s", l)
    if m: lit.append(f"{m[3]}{m[1]}6{m[2]}6")
lit = sorted(set(lit)); lv = f.loc[[c for c in lit if c in f.index]]; lv = lv[lv.data_quality == "valid"]
N["lit_n"] = int(len(lv)); N["lit_top50"] = int((lv["rank"] <= 50).sum())
N["lit_top_ranks"] = lv.sort_values("rank")["rank"].astype(int).head(4).to_dict()
low = lv[lv["rank"] > 50]; N["lit_low_range"] = [int(low["rank"].min()), int(low["rank"].max())]
N["lit_max_ehull"] = [lv.e_above_hull.idxmax(), float(lv.e_above_hull.max())]
N["lit_fe_mn"] = {"n": int(lv.M.isin(["Fe", "Mn"]).sum()), "in_top50": int((lv.M.isin(["Fe", "Mn"]) & (lv["rank"] <= 50)).sum())}
N["lit_fe_mn_outside"] = lv[lv.M.isin(["Fe", "Mn"]) & (lv["rank"] > 50)]["rank"].astype(int).to_dict()
# --- DOS trend numbers (labels file)
lab = dict(re.findall(r"(\w+) = ([-\d.]+)", (H / "gp/data/dos_labels.gp").read_text()))
N["dos_labels"] = {k: float(v) for k, v in lab.items()}
N["band_compounds_rank"] = {c: int(f.loc[c, "rank"]) for c in ("DyFe6Sn6", "TmFe6Sn6", "PmMn6Sn6", "GdFe6Sn6")}
# --- representative seeds
r = b[b.group == "representative"]
for cfg, B in (("u_only", 54), ("lanthanide_u", 864)):
    q = r[(r.config == cfg) & (r.budget == B)]
    N[f"rep_{cfg}"] = {"evals_to_best": [int(q.evals_to_best.min()), int(q.evals_to_best.max())],
                       "rank15": [float(q.rank15.min()), float(q.rank15.max())]}
q = r[(r.config == "lanthanide_u") & (r.budget == 432)]; N["rep_lanthanide_u"]["rank15_432"] = [float(q.rank15.min()), float(q.rank15.max())]
# --- grid at the budget
g = b[(b.group == "grid") & (b.budget == 54)]
cfg = g.groupby(["rollout_depth", "n_rollout"]).agg(found=("found_best", "mean"), rank15=("rank15", "mean"), e95=("evals_to_95", "mean"))
N["grid_cfg"] = {"found": [float(cfg.found.min()), float(cfg.found.max())], "rank15": [float(cfg.rank15.min()), float(cfg.rank15.max())],
                 "e95": [float(cfg.e95.min()), float(cfg.e95.max())]}
N["grid_sem_max"] = {"found": float(g.groupby(["rollout_depth", "n_rollout", "quartile"]).found_best.sem().max()),
                     "rank15": float(g.groupby(["rollout_depth", "n_rollout", "quartile"]).rank15.sem().max())}
qq = g.groupby("quartile").agg(found=("found_best", "mean"), e95=("evals_to_95", "mean"))
N["grid_quartile"] = {k: {"found": float(v.found), "e95": float(v.e95)} for k, v in qq.iterrows()}
# substitution distance of each start to the best compound (same metric as before)
TM = ["Ti", "V", "Cr", "Mn", "Fe", "Co", "Ni", "Cu", "Zn", "Zr", "Nb", "Mo", "Tc", "Ru", "Rh", "Pd", "Ag", "Cd", "Hf", "Ta", "W", "Re", "Os", "Ir", "Pt", "Au", "Hg"]
XS = ["Si", "Ge", "Sn", "Pb"]
pos = lambda m: (TM.index(m) // 9, TM.index(m) % 9)
best = u.index[0]; bm, bx = re.match(r"U([A-Z][a-z]?)6([A-Z][a-z]?)6", best).groups()
def dist(s):
    m, x = s[:-2], s[-2:]; (p1, g1), (p2, g2) = pos(m), pos(bm)
    return abs(p1 - p2) + abs(g1 - g2) + abs(XS.index(x) - XS.index(bx))
gs = g.copy(); gs["d"] = gs.start.map(dist)
per = gs.groupby("start").agg(d=("d", "first"), q=("quartile", "first"), found=("found_best", "mean"), e95=("evals_to_95", "mean"))
N["starts_by_distance"] = per.sort_values("d").round(3).reset_index().to_dict("records")
near, far = per[per.d <= 4], per[per.d >= 5]
N["dist_near"] = {"n": int(len(near)), "found": [float(near.found.min()), float(near.found.max())], "e95": [float(near.e95.min()), float(near.e95.max())]}
N["dist_far"] = {"n": int(len(far)), "found": [float(far.found.min()), float(far.found.max())], "e95": [float(far.e95.min()), float(far.e95.max())]}
# convergence medians (Fig 8)
best95 = 0.95 * u.reward.max(); cross = {}
for qn in ("0-25", "25-50", "50-75", "75-100"):
    d = np.loadtxt(H / f"gp/data/fig8b_{qn}.dat"); i = np.argmax(d[:, 1] >= best95); cross[qn] = int(d[i, 0]) if (d[:, 1] >= best95).any() else None
N["fig8_cross"] = cross
# c sweep (SI)
cs = pd.read_csv(H / "run_metrics_csweep.csv").groupby("c")[["found_best", "mean_rank_top15", "frac_explored", "frac_evaluated"]].mean()
N["csweep"] = cs.round(4).to_dict("index")
csb = b[(b.group == "csweep") & (b.budget == 54)].groupby("c").agg(found=("found_best", "mean"), rank15=("rank15", "mean"))
N["csweep_budget"] = {"found": [float(csb.found.min()), float(csb.found.max())], "rank15": [float(csb.rank15.min()), float(csb.rank15.max())]}
gm = pd.read_csv(H / "run_metrics_grid.csv"); gm = gm[gm.group == "grid"]
N["grid_unbudgeted_frac_evaluated"] = [float(gm.groupby("config").frac_evaluated.mean().min()), float(gm.groupby("config").frac_evaluated.mean().max())]
json.dump(N, open(H / "tables/numbers_v3.json", "w"), indent=1, default=lambda o: o.item() if hasattr(o, "item") else str(o))
print(json.dumps({k: v for k, v in N.items() if k not in ("rep", "dos_labels", "starts_by_distance", "csweep")}, indent=0, default=str)[:4000])
print(per.sort_values("d").round(2).to_string())
