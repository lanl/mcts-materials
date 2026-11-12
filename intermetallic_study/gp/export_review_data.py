#!/usr/bin/env python3
"""Data for the review-round figures:
  bench_<space>_<method>.dat   fraction of runs that have evaluated the best compound vs number evaluated
  bench_meta.gp                budgets and run counts
  eform_ehull_u.dat / _re.dat  MACE E_form vs E_hull on the GGA hull (SI figure)
"""
import json
from pathlib import Path
import numpy as np, pandas as pd
G = Path(__file__).resolve().parent; S = G.parent; R = S / "review"; D = G / "data"
ORDER = ["mcts", "al", "bo", "ga", "greedy", "walk", "random", "rule_mnfe"]
meta = []
for space, B in (("u_only", 54), ("full", 864)):
    df = pd.concat([pd.read_csv(R / f"mcts_{space}_metrics.csv")] + [pd.read_csv(f) for f in sorted(R.glob(f"baselines_{space}_final.csv"))], ignore_index=True)
    for m in ORDER:
        g = df[df.method == m]
        e = np.sort(g.evals_to_best.fillna(np.inf).to_numpy()); n = len(e)
        xs = np.arange(0, B + 1); frac = np.array([(e <= x).mean() for x in xs])
        np.savetxt(D / f"bench_{space}_{m}.dat", np.c_[xs, frac], fmt="%.4f")
        meta.append(f"N_{space}_{m} = {n}")
    meta.append(f"B_{space} = {B}")
(D / "bench_meta.gp").write_text("\n".join(meta) + "\n")
r = pd.read_csv(S / "rankings/full_ranking.csv"); c = pd.read_csv(S / "data/mace_cache_v3_gga.csv")
import re
def key(f):
    els = dict(re.findall(r"([A-Z][a-z]?)(\d*)", f))
    try:
        giv = [e for e in els if e in ("Si", "Ge", "Sn", "Pb")][0]; m = [e for e in els if els[e] == "6" and e != giv][0]
        fb = [e for e in els if els[e] in ("", "1")][0]; return f"{fb}{m}6{giv}6"
    except IndexError:
        return None
c["compound"] = c.name.map(key); c = c.drop_duplicates("compound").set_index("compound")
v = r[r.data_quality == "valid"].copy(); v["e_form"] = v.compound.map(c.e_form)
np.savetxt(D / "eform_ehull_u.dat", v[v.f == "U"][["e_form", "e_above_hull"]].to_numpy(), fmt="%.5f")
np.savetxt(D / "eform_ehull_re.dat", v[v.f != "U"][["e_form", "e_above_hull"]].to_numpy(), fmt="%.5f")
print("wrote bench_*, eform_ehull_*", len(v[v.f == "U"]), len(v[v.f != "U"]))
