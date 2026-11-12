#!/usr/bin/env python3
"""Compare MCTS with the baselines at the same budget, starting compounds and seeds."""
import sys
from pathlib import Path
import numpy as np, pandas as pd
H = Path(__file__).resolve().parent
NAMES = {"mcts": "MCTS (this work)", "random": "Random search", "walk": "Random walk (MCTS moves)", "greedy": "Greedy local search",
         "ga": "Genetic algorithm", "bo": "Bayesian optimization (GP, EI)", "al": "Active learning (trees, UCB)",
         "rule_mnfe": "Rule: M = Mn or Fe first"}
for space, B in (("u_only", 54), ("full", 864)):
    files = [H / f"mcts_{space}_metrics.csv"] + [H / f"baselines_{space}_final.csv"]
    files = [f for f in files if f.exists() and "orders" not in f.name]
    if len(files) < 2:
        continue
    df = pd.concat([pd.read_csv(f) for f in files], ignore_index=True)
    out = []
    for m, g in df.groupby("method"):
        eb = g.evals_to_best.fillna(np.inf)
        row = {"method": NAMES.get(m, m), "runs": len(g), f"P(best) @{B}": g[f"found_best@{B}"].mean(),
               "median evals to best": np.median(eb), "evals to best IQR": "-".join(f"{v:.0f}" if v <= B else f">{B}" for v in np.percentile(eb.clip(upper=B + 1), [25, 75])),
               f"mean rank top-15 @{B}": g[f"rank15@{B}"].mean(), "median evals to 95%": np.median(g.evals_to_95.fillna(np.inf))}
        if space == "full":
            row["P(best) @432"] = g["found_best@432"].mean(); row["mean rank top-15 @432"] = g["rank15@432"].mean()
        out.append(row)
    t = pd.DataFrame(out).sort_values(f"P(best) @{B}", ascending=False)
    print(f"\n=== {space}: budget {B} evaluations, {df.start.nunique()} starts x 5 seeds ===")
    print(t.round(2).to_string(index=False))
    t.to_csv(H / f"comparison_{space}.csv", index=False)
