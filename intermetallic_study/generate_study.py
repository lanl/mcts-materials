#!/usr/bin/env python3
"""
Generate every config of the rdos-v2 rerun plus a run list for the sbatch driver.

  stage csweep : csweep/c_<c>/pct_<p>/<MX>_seed<s>   5 values of c at D=3 N=3 x 15 starts x 5 seeds
  stage grid   : grid/<config>/pct_<p>/<MX>_seed<s>   12 (D,N) configs x 15 starts x 5 seeds at the chosen c
                 representative/u_only/seed_{0..4}      UCr6Sn6 start, D=3 N=3 (seed 0 = manuscript run)
                 representative/lanthanide_u/seed_{0..4} TbCu6Sn6 start, lanthanides_u, u_bridge wide

Starting materials: for each target percentile (10, 25, 50, 75, 90) of the new
U-only reference ranking, the three compounds nearest the target with distinct
M-X pairs (the manuscript's protocol, minus its MCTS-based down-selection).

Run from this directory:  python generate_study.py csweep | grid --c <value>
"""

import argparse
import json
import os
from pathlib import Path

import pandas as pd
import yaml

HERE = Path(__file__).resolve().parent
REPO = Path(os.environ.get("MCTS_REPO", HERE.parent))   # the study lives in <repo>/intermetallic_study
DATA = HERE / "data"
SEEDS = [0, 42, 123, 456, 789]
GRID = {
    "config10_d1_n1": (1, 1), "config5_d1_n3": (1, 3), "config1_baseline": (1, 5), "config2_more_rollouts": (1, 10),
    "config11_d2_n1": (2, 1), "config6_d2_n3": (2, 3), "config3_deeper": (2, 5), "config7_d2_n10": (2, 10),
    "config12_d3_n1": (3, 1), "config4_deep_many": (3, 3), "config8_d3_n5": (3, 5), "config9_d3_n10": (3, 10),
}
PERCENTILES = [10, 25, 50, 75, 90]
C_SWEEP = [0.03, 0.1, 0.3, 1.0, 1.41]
E_THRES = 0.054  # eV/atom: E_hull of UCr6Ge6, the least stable synthesized compound, on the GGA hull (no margin)


def base(tm, giv, f_mode, depth, n_roll, seed, out_dir, c):
    return {
        "material_type": "intermetallic",
        "mcts": {
            "iterations": 1000, "exploration_constant": c, "termination_limit": 100,
            "selection_mode": "ucb1", "rollout_depth": depth, "n_rollout": n_roll,
            "rollout_aggregation": "max", "search_mode": "thorough", "seed": seed,
            "output_dir": str(out_dir),
        },
        "intermetallic": {
            "structure_path": "examples/mat_Pb6U1W6_sg191.cif",
            "transition_metal": tm, "group_iv": giv,
            "f_block_mode": f_mode, "move_step": 1, "u_bridge": "wide",
            "rollout_method": "ehull_rdos_product_exponential", "beta": 1.0, "gamma": 1.0,
            "rdos_method": "bandpass",
            "doscar_data_path": str(DATA / "rdos_bandpass_RE_U.csv"),
            "cache_path": str(DATA / "mace_cache_v3_gga.csv"),
            "ehull_threshold": E_THRES,
            "mp_api_key": None,
        },
    }


def select_starting_materials(ranking):
    chosen, seen = {}, set()
    for pct in PERCENTILES:
        r = ranking.assign(dist=(ranking.percentile - pct).abs()).sort_values(["dist", "rank"])
        picks = []
        for _, row in r.iterrows():
            pair = (row.M, row.X)
            if pair in seen:
                continue
            seen.add(pair)
            picks.append({"material": f"{row.M}{row.X}", "tm": row.M, "giv": row.X, "rank": int(row["rank"]),
                          "percentile": float(row.percentile), "reward": float(row.reward)})
            if len(picks) == 3:
                break
        chosen[pct] = picks
    return chosen


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("stage", choices=["csweep", "grid", "full"])
    ap.add_argument("--c", type=float, default=None, help="exploration constant for the grid stage")
    ap.add_argument("--rep-budget", type=float, default=None,
                    help="representative runs only: evaluation budget as a fraction of the design space")
    a = ap.parse_args()
    if a.stage in ("grid", "full") and a.c is None:
        ap.error("--c is required for the grid stage")

    runs = []
    ranking = pd.read_csv(HERE / "rankings/u_only_ranking.csv")
    starts = select_starting_materials(ranking)
    json.dump(starts, open(HERE / "grid_starting_materials.json", "w"), indent=1)
    for pct, picks in starts.items():
        print(f"pct {pct:>2}: " + ", ".join(f"{p['material']} (rank {p['rank']}, {p['percentile']:.0f}%)" for p in picks))

    def emit(cfg_path, cfg):
        cfg_path.parent.mkdir(parents=True, exist_ok=True)
        cfg_path.write_text(yaml.safe_dump(cfg, sort_keys=False))
        runs.append(str(cfg_path))

    if a.stage == "full":
        # benchmark set in the full space: 3 lanthanide compounds with distinct M-X nearest the
        # 10/25/50/75/90th percentiles of the full ranking, 5 seeds each, budget half the space
        import re
        full = pd.read_csv(HERE / "rankings/full_ranking.csv")
        full = full[(full.data_quality == "valid") & (~full.f.isin(["U", "La"]))]   # La is not connected to Ce-Lu by the f-block moves
        fstarts = select_starting_materials(full)
        tmpl = (DATA / "mat_Sn6Tb1Cu6_sg191.cif").read_text()
        out_starts = []
        for pct, picks in fstarts.items():
            for pk in picks:
                row = full[(full.M == pk["tm"]) & (full.X == pk["giv"])].assign(d=lambda t: (t.percentile - pct).abs()).sort_values(["d", "rank"]).iloc[0]
                r_el, m_el, x_el = row.f, row.M, row.X
                cif = re.sub(r"\bTb(?=\d|\s|$)", r_el, tmpl); cif = re.sub(r"\bCu(?=\d|\s|$)", m_el, cif); cif = re.sub(r"\bSn(?=\d|\s|$)", x_el, cif)
                cpath = DATA / f"start_{r_el}{m_el}6{x_el}6.cif"; cpath.write_text(cif)
                out_starts.append({"pct": pct, "compound": row.compound, "rank": int(row["rank"]), "percentile": float(row.percentile)})
                for seed in SEEDS:
                    out = HERE / f"full/pct_{pct}/{row.compound}/seed_{seed}"
                    cfg = base(m_el, x_el, "lanthanides_u", 3, 3, seed, out, a.c)
                    cfg["intermetallic"]["structure_path"] = str(cpath); cfg["mcts"]["max_evaluations"] = 864
                    emit(HERE / f"full/configs/pct_{pct}/{row.compound}_seed{seed}.yaml", cfg)
        json.dump(out_starts, open(HERE / "full_starting_materials.json", "w"), indent=1)
        for st in out_starts:
            print(f"full start pct {st['pct']:>2}: {st['compound']} (rank {st['rank']}, {st['percentile']:.0f}%)")
    elif a.stage == "csweep":
        for c in C_SWEEP:
            for pct, picks in starts.items():
                for pk in picks:
                    for seed in SEEDS:
                        out = HERE / f"csweep/c_{c}/pct_{pct}/{pk['material']}/seed_{seed}"
                        emit(HERE / f"csweep/c_{c}/configs/pct_{pct}/{pk['material']}_seed{seed}.yaml",
                             base(pk["tm"], pk["giv"], "u_only", 3, 3, seed, out, c))
    else:
        c = a.c
        for seed in range(5):
            out = HERE / f"representative/u_only/seed_{seed}"
            cfg = base("Cr", "Sn", "u_only", 3, 3, seed, out, c)
            if a.rep_budget: cfg["mcts"]["max_evaluations"] = int(round(a.rep_budget * 108))
            emit(out.parent / f"seed_{seed}.yaml", cfg)
            out = HERE / f"representative/lanthanide_u/seed_{seed}"
            cfg = base("Cu", "Sn", "lanthanides_u", 3, 3, seed, out, c)
            if a.rep_budget: cfg["mcts"]["max_evaluations"] = int(round(a.rep_budget * 1728))
            # the lanthanide run starts from TbCu6Sn6: the CIF holds U, so use the Tb-substituted copy
            cfg["intermetallic"]["structure_path"] = str(HERE / "data/mat_Sn6Tb1Cu6_sg191.cif")
            emit(out.parent / f"seed_{seed}.yaml", cfg)
        for seed in range(5):
            out = HERE / f"representative/u_only_full/seed_{seed}"
            emit(out.parent / f"seed_{seed}.yaml", base("Cr", "Sn", "u_only", 3, 3, seed, out, c))
        for name, (depth, n_roll) in GRID.items():
            for pct, picks in starts.items():
                for pk in picks:
                    for seed in SEEDS:
                        out = HERE / f"grid/{name}/pct_{pct}/{pk['material']}/seed_{seed}"
                        emit(HERE / f"grid/{name}/configs/pct_{pct}/{pk['material']}_seed{seed}.yaml",
                             base(pk["tm"], pk["giv"], "u_only", depth, n_roll, seed, out, c))
        (HERE / "grid_c.txt").write_text(f"{c}\n")
    lst = HERE / f"run_list_{a.stage}.txt"
    lst.write_text("\n".join(runs) + "\n")
    print(f"{len(runs)} configs written; run list: {lst}")


if __name__ == "__main__":
    main()
