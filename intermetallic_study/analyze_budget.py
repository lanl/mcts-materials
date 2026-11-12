#!/usr/bin/env python3
"""
Budget-based metrics from evaluation_order.csv (every evaluated material in the
order it was first computed). For each run and each evaluation budget E:

  found_best@E   the true #1 compound is among the first E evaluated materials
  rank15@E       mean true rank of the 15 best (by true reward) of the first E
  evals_to_95    first E at which the best reward among the first E reaches 95 % of the optimum
  evals_to_best  first E at which the optimum has been evaluated

Writes budget_metrics.csv (one row per run and budget) and, for the figures,
gp/data/fig7b_<metric>_<quartile>.dat (D x N cells at the chosen budget) and
gp/data/fig8b_<quartile>.dat (median / IQR of the running best reward vs E,
config4 runs). Usage: python analyze_budget.py [--budget 54]
"""
import argparse, json, re
from pathlib import Path
import numpy as np, pandas as pd, yaml

HERE = Path(__file__).resolve().parent; D = HERE / "gp/data"
N_SPACE = {"u_only": 108, "lanthanides_u": 1728}


def ckey(identifier):
    f = str(identifier).split("|")[0]; els = dict(re.findall(r"([A-Z][a-z]?)(\d*)", f))
    giv = [e for e in els if e in ("Si", "Ge", "Sn", "Pb")][0]; m = [e for e in els if els[e] == "6" and e != giv][0]
    fb = [e for e in els if els[e] in ("", "1")][0]; return f"{fb}{m}6{giv}6"


def quartile(p):
    return "0-25" if p < 25 else "25-50" if p < 50 else "50-75" if p < 75 else "75-100"


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--budget", type=int, default=54); a = ap.parse_args()
    ranks = {}
    for space, fn in (("u_only", "u_only_ranking.csv"), ("lanthanides_u", "full_ranking.csv")):
        r = pd.read_csv(HERE / "rankings" / fn).set_index("compound"); ranks[space] = r
    starts = json.load(open(HERE / "grid_starting_materials.json"))
    start_pct = {pk["material"]: pk["percentile"] for picks in starts.values() for pk in picks}

    rows, curves = [], {}
    for root in ("csweep", "grid", "representative"):
        for eo in sorted((HERE / root).rglob("evaluation_order.csv")):
            run = eo.parent; cfg = yaml.safe_load(open(run / "config.yaml")); ic, mc = cfg["intermetallic"], cfg["mcts"]
            space = ic["f_block_mode"]; r = ranks[space]; n = N_SPACE[space]
            order = pd.read_csv(eo); order["compound"] = order.identifier.map(ckey)
            order = order.drop_duplicates("compound")
            rew = order.compound.map(r.reward).to_numpy(); rk = order.compound.map(r["rank"]).to_numpy()
            best = r.reward.max(); running = np.maximum.accumulate(rew)
            e95 = int(np.argmax(running >= 0.95 * best) + 1) if (running >= 0.95 * best).any() else None
            ebest = int(np.argmax(rk == 1) + 1) if (rk == 1).any() else None
            start = (ic.get("transition_metal") or "") + (ic.get("group_iv") or ""); sp = start_pct.get(start)
            rel = run.relative_to(HERE / root).parts
            budgets = [a.budget] if space == "u_only" else [int(round(f * n)) for f in (0.25, 0.5)]
            base = {"group": root, "config": rel[0] if len(rel) > 1 else root, "run_dir": str(run), "c": mc["exploration_constant"],
                    "rollout_depth": mc["rollout_depth"], "n_rollout": mc["n_rollout"], "start": start,
                    "quartile": quartile(sp) if sp is not None else None, "seed": mc["seed"], "n_evaluated": len(order),
                    "evals_to_95": e95, "evals_to_best": ebest}
            for E in budgets:
                head = rk[:E]
                rows.append({**base, "budget": E, "found_best": int((head == 1).any()),
                             "rank15": float(np.sort(head)[:15].mean()), "best_rank": int(head.min())})
            if root == "grid" and rel[0] == "config4_deep_many":
                curves.setdefault(base["quartile"], []).append(running)
    df = pd.DataFrame(rows); df.to_csv(HERE / "budget_metrics.csv", index=False, float_format="%.5g")

    g = df[(df.group == "grid") & (df.budget == a.budget)]
    print(f"grid at budget E = {a.budget} evaluations ({100*a.budget/108:.0f}% of the U space):")
    print(g.groupby(["rollout_depth", "n_rollout"]).agg(found=("found_best", "mean"), rank15=("rank15", "mean"),
                                                        e95=("evals_to_95", "median"), ebest=("evals_to_best", "median")).round(2).to_string())
    print("\n0-25 quartile:")
    print(g[g.quartile == "0-25"].groupby(["rollout_depth", "n_rollout"]).agg(found=("found_best", "mean"), rank15=("rank15", "mean"),
                                                                             e95=("evals_to_95", "median")).round(2).to_string())
    cs = df[(df.group == "csweep") & (df.budget == a.budget)]
    print("\nc sweep at budget:"); print(cs.groupby("c").agg(found=("found_best", "mean"), rank15=("rank15", "mean"), e95=("evals_to_95", "median")).round(2).to_string())
    rep = df[df.group == "representative"]
    print("\nrepresentative:"); print(rep[["config", "seed", "budget", "n_evaluated", "found_best", "rank15", "best_rank", "evals_to_95", "evals_to_best"]].to_string(index=False))

    # figure data
    depths, nrolls = [1, 2, 3], [1, 3, 5, 10]
    for metric in ("found_best", "rank15", "evals_to_95"):
        for q in ["0-25", "25-50", "50-75", "75-100"]:
            sub = g[g.quartile == q]
            with open(D / f"fig7b_{metric}_{q}.dat", "w") as fh:
                for i, d in enumerate(depths):
                    for j, nr in enumerate(nrolls):
                        v = sub[(sub.rollout_depth == d) & (sub.n_rollout == nr)][metric].dropna()
                        fh.write(f"{j} {i} {v.mean():.4f} {v.sem() if len(v) > 1 else 0:.4f} {len(v)}\n")
                    fh.write("\n")
    for q, cs_ in curves.items():
        L = max(len(c) for c in cs_); A = np.full((len(cs_), L), np.nan)
        for i, c in enumerate(cs_): A[i, :len(c)] = c; A[i, len(c):] = c[-1]
        np.savetxt(D / f"fig8b_{q}.dat", np.c_[np.arange(1, L + 1), np.nanmedian(A, 0), np.nanpercentile(A, 25, 0), np.nanpercentile(A, 75, 0)], fmt="%.5f")
    (D / "fig8b_meta.gp").write_text(f"BEST95 = {0.95 * ranks['u_only'].reward.max():.5f}\nBUDGET = {a.budget}\n")
    print("\nwrote budget_metrics.csv and gp/data/fig7b_*, fig8b_*")


if __name__ == "__main__":
    main()
