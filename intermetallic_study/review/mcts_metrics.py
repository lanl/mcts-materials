#!/usr/bin/env python3
"""Score MCTS runs with the baseline metrics (unique-evaluation order from evaluation_order.csv).
U space: the D_roll = N_roll = 3 grid runs (15 starts x 5 seeds), truncated at 54 evaluations.
Full space: the 75 review runs (15 starts x 5 seeds, budget 864)."""
import glob, json, re, yaml
from pathlib import Path
import numpy as np, pandas as pd
H = Path(__file__).resolve().parent; S = H.parent

def ckey(identifier):
    f = str(identifier).split("|")[0]; els = dict(re.findall(r"([A-Z][a-z]?)(\d*)", f))
    giv = [e for e in els if e in ("Si", "Ge", "Sn", "Pb")][0]; m = [e for e in els if els[e] == "6" and e != giv][0]
    fb = [e for e in els if els[e] in ("", "1")][0]; return f"{fb}{m}6{giv}6"

rows = []
for space, pattern, rankfile, budgets in (("u_only", str(S / "grid/**/evaluation_order.csv"), "u_only_ranking.csv", (54,)),
                                          ("full", str(S / "full/**/evaluation_order.csv"), "full_ranking.csv", (432, 864))):
    rk = pd.read_csv(S / "rankings" / rankfile).set_index("compound"); best = rk.reward.max()
    for eo in sorted(glob.glob(pattern, recursive=True)):
        run = Path(eo).parent; cfg = yaml.safe_load(open(run / "config.yaml")); mc = cfg["mcts"]
        if space == "u_only" and not (mc["rollout_depth"] == 3 and mc["n_rollout"] == 3):
            continue
        o = pd.read_csv(eo); o["c"] = o.identifier.map(ckey); o = o.drop_duplicates("c")
        r = o.c.map(rk["rank"]).to_numpy(); w = o.c.map(rk.reward).to_numpy(); rb = np.maximum.accumulate(w)
        t = json.load(open(run / "tree.json")); root = [n for n in t["nodes"] if n["id"] == t["root_id"]][0]["identifier"]
        d = {"space": space, "method": "mcts", "start": ckey(root), "seed": mc["seed"], "n_eval": len(r),
             "evals_to_best": int(np.argmax(r == 1) + 1) if (r == 1).any() else None,
             "evals_to_95": int(np.argmax(rb >= 0.95 * best) + 1) if (rb >= 0.95 * best).any() else None}
        for E in budgets:
            d[f"found_best@{E}"] = int((r[:E] == 1).any()); d[f"rank15@{E}"] = float(np.sort(r[:E])[:15].mean())
        rows.append(d)
df = pd.DataFrame(rows)
for sp in ("u_only", "full"):
    df[df.space == sp].to_csv(H / f"mcts_{sp}_metrics.csv", index=False)
print(df.groupby("space").agg(n=("seed", "size"), starts=("start", "nunique"), n_eval_min=("n_eval", "min")).to_string())
print(sorted(df[df.space == "full"].start.unique()))
