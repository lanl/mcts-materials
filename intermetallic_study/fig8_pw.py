#!/usr/bin/env python3
"""Fig 8 data (median / IQR of the running best reward vs evaluations, by start quartile) from the
widening+prior runs over the 15 grid starts (variants/<VARIANT>/u_only). Same output format as analyze_budget.py."""
import glob, json, os, re, sys
from pathlib import Path
import numpy as np, pandas as pd
H = Path(__file__).resolve().parent; D = H / "gp/data"
VARIANT = sys.argv[1] if len(sys.argv) > 1 else "x8_d1n1_a05_term"
rk = pd.read_csv(H / "rankings/u_only_ranking.csv").set_index("compound"); best = rk.reward.max()
pct = {pk["material"]: pk["percentile"] for picks in json.load(open(H / "grid_starting_materials.json")).values() for pk in picks}
def quart(p): return "0-25" if p < 25 else "25-50" if p < 50 else "50-75" if p < 75 else "75-100"
def ckey(s):
    els = dict(re.findall(r"([A-Z][a-z]?)(\d*)", s.split("|")[0])); giv = [e for e in els if e in ("Si", "Ge", "Sn", "Pb")][0]
    m = [e for e in els if els[e] == "6" and e != giv][0]; fb = [e for e in els if els[e] in ("", "1")][0]; return f"{fb}{m}6{giv}6"
curves = {}
for eo in sorted(glob.glob(str(H / f"variants/{VARIANT}/u_only/*/seed_*/evaluation_order.csv"))):
    start = Path(eo).parts[-3]; o = pd.read_csv(eo); c = list(dict.fromkeys(o.identifier.map(ckey)))[:54]
    run = np.maximum.accumulate([rk.loc[x, "reward"] for x in c]); run = np.r_[run, np.full(54 - len(run), run[-1])]
    curves.setdefault(quart(pct[start]), []).append(run)
for q, A in curves.items():
    A = np.array(A); np.savetxt(D / f"fig8b_{q}.dat", np.c_[np.arange(1, 55), np.median(A, 0), np.percentile(A, 25, 0), np.percentile(A, 75, 0)], fmt="%.5f")
    i = np.argmax(np.median(A, 0) >= 0.95 * best); print(q, len(A), "runs; median crosses 95% at", int(i + 1) if (np.median(A, 0) >= 0.95 * best).any() else None)
(D / "fig8b_meta.gp").write_text(f"BEST95 = {0.95 * best:.5f}\nBUDGET = 54\n")
