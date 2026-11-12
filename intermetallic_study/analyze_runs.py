#!/usr/bin/env python3
"""
Per-run metrics for the rdos-v2 study (c sweep, D/N grid, representative runs).

For every run directory with a summary.json under the given roots, writes one
row to <out>.csv:
  group (csweep|grid|representative), config (c_0.3 / config4_deep_many / u_only),
  c, rollout_depth, n_rollout, start (MX), pct (target percentile), quartile
  (0-25 / 25-50 / 50-75 / 75-100 by the start's true percentile), seed,
  found_best (1/0), mean_rank_top15, frac_explored, unique, best_reward,
  n_iterations_to_best (iteration at which the best reward was first reached)

Metrics follow the manuscript (Sec. 4.2): "found best" = the true #1 compound
is in the tree; "mean rank top-15" = mean true rank of the 15 highest-reward
unique compounds evaluated; "fraction explored" = unique / 108.

Usage: python analyze_runs.py csweep grid representative -o run_metrics.csv
"""

import argparse
import json
import re
from pathlib import Path

import pandas as pd
import yaml

HERE = Path(__file__).resolve().parent
N_SPACE = {"u_only": 108, "lanthanides_u": 1728}


def compound_key(identifier: str) -> str:
    """'Ge6Tc6U|SG191|...' -> 'UTc6Ge6' (f-element first, then M6, then X6)."""
    f = str(identifier).split("|")[0]
    els = dict(re.findall(r"([A-Z][a-z]?)(\d*)", f))
    giv = [e for e in els if e in ("Si", "Ge", "Sn", "Pb")][0]
    m = [e for e in els if els[e] == "6" and e != giv][0]
    fb = [e for e in els if els[e] in ("", "1")][0]
    return f"{fb}{m}6{giv}6"


def quartile(p: float) -> str:
    return "0-25" if p < 25 else "25-50" if p < 50 else "50-75" if p < 75 else "75-100"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("roots", nargs="+")
    ap.add_argument("-o", "--out", default="run_metrics.csv")
    a = ap.parse_args()

    ranks = {}
    for space, fn in (("u_only", "u_only_ranking.csv"), ("lanthanides_u", "full_ranking.csv")):
        r = pd.read_csv(HERE / "rankings" / fn)
        ranks[space] = (r.set_index("compound")["rank"], r.set_index("compound")["percentile"], r.compound.iloc[0])
    starts = json.load(open(HERE / "grid_starting_materials.json"))
    start_pct = {pk["material"]: (int(pct), pk["percentile"]) for pct, picks in starts.items() for pk in picks}

    rows = []
    for root in a.roots:
        for summ in sorted((HERE / root).rglob("summary.json")):
            run = summ.parent
            cfg = yaml.safe_load(open(run / "config.yaml"))
            ic, mc = cfg["intermetallic"], cfg["mcts"]
            space = ic["f_block_mode"]
            rank, pct_of, best_compound = ranks[space]
            s = json.load(open(summ))
            bm = pd.read_csv(run / "best_materials.csv")
            bm["compound"] = bm["identifier"].map(compound_key)
            bm = bm.sort_values("own_reward", ascending=False).drop_duplicates("compound")
            top15 = bm.head(15)
            conv = pd.read_csv(run / "convergence.csv") if (run / "convergence.csv").exists() else None
            n_to_best = None
            if conv is not None and "best_reward" in conv.columns:
                hit = conv.index[conv["best_reward"] >= s["best_reward"] - 1e-12]
                n_to_best = int(hit[0]) + 1 if len(hit) else None
            rel = run.relative_to(HERE / root)
            parts = rel.parts
            start = (ic.get("transition_metal") or "") + (ic.get("group_iv") or "")
            tp = start_pct.get(start, (None, None))
            rows.append({
                "group": root, "config": parts[0] if len(parts) > 1 else root, "run_dir": str(run),
                "c": mc["exploration_constant"], "rollout_depth": mc["rollout_depth"], "n_rollout": mc["n_rollout"],
                "start": start, "pct": tp[0], "start_percentile": tp[1],
                "quartile": quartile(tp[1]) if tp[1] is not None else None, "seed": mc["seed"],
                "found_best": int(best_compound in set(bm["compound"])),
                "mean_rank_top15": float(top15["compound"].map(rank).mean()),
                "frac_explored": s["unique_materials"] / N_SPACE[space], "unique": s["unique_materials"],
                "evaluations": s.get("evaluations"), "frac_evaluated": (s.get("evaluations") or float("nan")) / N_SPACE[space],
                "best_reward": s["best_reward"], "best_compound": compound_key(s["best_material"]),
                "best_true_rank": int(rank.get(compound_key(s["best_material"]), -1)),
                "n_iterations_to_best": n_to_best,
            })
    df = pd.DataFrame(rows)
    df.to_csv(HERE / a.out, index=False, float_format="%.5g")
    print(f"{len(df)} runs -> {a.out}")
    if len(df):
        g = df.groupby(["group", "config"]).agg(n=("seed", "size"), found=("found_best", "mean"),
                                               rank15=("mean_rank_top15", "mean"), explored=("frac_explored", "mean"),
                                               evaluated=("frac_evaluated", "mean"))
        print(g.round(3).to_string())


if __name__ == "__main__":
    main()
