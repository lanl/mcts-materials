#!/usr/bin/env python3
"""Score the MCTS variants (variants/<name>/<space>/**/evaluation_order.csv) with the benchmark
metrics and print them next to the baselines. Writes variants_metrics.csv."""
import glob, json, re
from pathlib import Path
import numpy as np, pandas as pd
H = Path(__file__).resolve().parent; S = H.parent
RANK = {sp: pd.read_csv(S / f"rankings/{f}").set_index("compound")["rank"].to_dict() for sp, f in (("u_only", "u_only_ranking.csv"), ("full", "full_ranking.csv"))}
B = {"u_only": 54, "full": 864}
def ckey(s):
    els = dict(re.findall(r"([A-Z][a-z]?)(\d*)", s.split("|")[0])); giv = [e for e in els if e in ("Si", "Ge", "Sn", "Pb")][0]
    m = [e for e in els if els[e] == "6" and e != giv][0]; fb = [e for e in els if els[e] in ("", "1")][0]; return f"{fb}{m}6{giv}6"
def metrics(rk, B):
    f = lambda k: int(np.argmax(rk <= k) + 1) if (rk <= k).any() else np.inf
    return {"P_best": float((rk == 1).any()), "P_best_half": float((rk[:B // 2] == 1).any()), "e_best": f(1), "e_top3": f(3), "e_top15": f(15),
            "rank15": float(np.sort(rk)[:15].mean()), "n_eval": len(rk)}
rows = []
for eo in sorted(glob.glob(str(S / "variants/*/*/*/seed_*/evaluation_order.csv"))):
    p = Path(eo); name, space = p.parts[-5], p.parts[-4]
    o = pd.read_csv(eo); c = list(dict.fromkeys(o.identifier.map(ckey)))[:B[space]]
    rows.append({"method": name, "space": space, "start": p.parts[-3], "seed": p.parts[-2], **metrics(np.array([RANK[space][x] for x in c]), B[space])})
# baselines, scored the same way from their orders
for space in ("u_only", "full"):
    for fn in sorted(H.glob(f"baselines_{space}_all*_orders.jsonl")):
        for l in open(fn):
            d = json.loads(l)
            if d["start"] == "LaW6Ge6": continue
            rows.append({"method": d["method"], "space": space, "start": d["start"], "seed": d["seed"], **metrics(np.array([RANK[space][x] for x in d["order"][:B[space]]]), B[space])})
df = pd.DataFrame(rows); df.to_csv(H / "variants_metrics.csv", index=False)
pd.set_option("display.width", 220)
for space in ("u_only", "full"):
    d = df[df.space == space]
    g = d.groupby("method").agg(runs=("seed", "size"), P_best=("P_best", "mean"), P_best_half=("P_best_half", "mean"),
                                med_e_best=("e_best", "median"), med_e_top3=("e_top3", "median"), med_e_top15=("e_top15", "median"),
                                rank15=("rank15", "mean"), n_eval=("n_eval", "mean"))
    print(f"\n=== {space} (budget {B[space]}) ===")
    print(g.sort_values("P_best", ascending=False).round(2).to_string())
