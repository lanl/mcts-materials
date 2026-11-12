#!/usr/bin/env python3
"""Export run-dependent data for the gnuplot figures and the LaTeX tables.

  representative : Fig 4 / Fig 9 scatters, Fig 6 radial-tree layout, Tables 1-2, text numbers
  grid           : Fig 7 heatmap matrices, Fig 8 convergence curves (needs run_metrics_grid.csv)

python export_run_data.py representative grid
"""
import json, os, re, sys
from pathlib import Path
import numpy as np, pandas as pd

G = Path(__file__).resolve().parent; H = G.parent; D = G / "data"; T = H / "tables"
rank_u = pd.read_csv(H / "rankings/u_only_ranking.csv").set_index("compound")
rank_f = pd.read_csv(H / "rankings/full_ranking.csv").set_index("compound")


def ckey(identifier):
    f = str(identifier).split("|")[0]; els = dict(re.findall(r"([A-Z][a-z]?)(\d*)", f))
    giv = [e for e in els if e in ("Si", "Ge", "Sn", "Pb")][0]; m = [e for e in els if els[e] == "6" and e != giv][0]
    fb = [e for e in els if els[e] in ("", "1")][0]; return f"{fb}{m}6{giv}6"


def yaml_budget(run_dir):
    import yaml
    return yaml.safe_load(open(run_dir / "config.yaml"))["mcts"].get("max_evaluations")


def tex(c):
    f, m, x = re.match(r"([A-Z][a-z]?)([A-Z][a-z]?)6([A-Z][a-z]?)6", c).groups(); return f"{f}{m}$_6${x}$_6$"


def mcts_top(run_dir, ranking, n=15):
    """The n highest-reward compounds among ALL compounds the search evaluated
    (tree nodes and rollout materials, from evaluation_order.csv), ranked by the
    search's own reward, which equals the reference reward for cached data."""
    eo = pd.read_csv(run_dir / "evaluation_order.csv"); eo["compound"] = eo.identifier.map(ckey)
    eo = eo.drop_duplicates("compound")[["order", "compound"]]
    eo = eo.join(ranking[["rank", "e_above_hull", "r_S", "r_dos", "reward"]].rename(columns={"rank": "true_rank"}), on="compound")
    eo = eo.sort_values("reward", ascending=False).head(n).reset_index(drop=True)
    eo["mcts_rank"] = eo.index + 1
    return eo


def representative():
    numbers = {}
    # --- U-only ---------------------------------------------------------
    SEED = int(os.environ.get("REP_SEED", "0"))  # seed of the representative uranium search (Table 1 and Fig 6)
    run = H / f"representative/u_only/seed_{SEED}"; s = json.load(open(run / "summary.json"))
    numbers["u_nodes"] = s["unique_materials"]; numbers["u_coverage_pct"] = round(100 * s["unique_materials"] / 108, 1)
    numbers["u_iterations"] = s["iterations"]; numbers["u_budget"] = yaml_budget(run)
    numbers["u_evaluations"] = s.get("evaluations"); numbers["u_evaluated_pct"] = round(100 * (s.get("evaluations") or 0) / 108, 1)
    top = mcts_top(run, rank_u)
    rows = [f"{r.mcts_rank} & {int(r.true_rank)} & {tex(r.compound)} & {r.e_above_hull:.4f} & {r.r_S:.4f} & {r.r_dos:.3f} & {r.reward:.3f} & {rank_u.loc[r.compound].synthesized} \\\\" for r in top.itertuples()]
    (T / "table1_top15_u_rows.tex").write_text("\n".join(rows) + "\n")
    numbers["u_top15_true_ranks"] = top.true_rank.astype(int).tolist()
    numbers["u_best_k_recovered"] = int(next((k for k in range(1, 16) if k not in set(top.true_rank.astype(int))), 16) - 1)
    numbers["u_start_rank"] = int(rank_u.loc["UCr6Sn6"]["rank"])
    sp = rank_u.reset_index()
    np.savetxt(D / "fig4_space.dat", sp[["r_dos", "e_above_hull"]].to_numpy(), fmt="%.5f")
    np.savetxt(D / "fig4_mcts_top15.dat", top[["r_dos", "e_above_hull", "mcts_rank"]].to_numpy(), fmt="%.5f %.5f %d")
    np.savetxt(D / "fig4_synth_yes.dat", sp[sp.synthesized == "Yes"][["r_dos", "e_above_hull"]].to_numpy(), fmt="%.5f")
    np.savetxt(D / "fig4_synth_no.dat", sp[sp.synthesized == "No"][["r_dos", "e_above_hull"]].to_numpy(), fmt="%.5f")
    # --- Fig 6: radial tree of the U-only run ----------------------------
    # Fig 6 shows the same search continued without a budget (identical seed and
    # evaluation order, so the budgeted tree is its first `unique_materials` nodes).
    full = H / f"representative/{os.environ.get('FIG6_RUN', 'u_only_full')}/seed_{SEED}"
    budget_ids = {n["identifier"] for n in json.load(open(run / "tree.json"))["nodes"]}
    tree = json.load(open((full if full.exists() else run) / "tree.json")); byid = {n["id"]: n for n in tree["nodes"]}
    numbers["u_full_nodes"] = len(tree["nodes"]); numbers["u_budget_nodes"] = len(budget_ids)
    kids = {}
    for n in tree["nodes"]:
        if n["parent"] is not None: kids.setdefault(n["parent"], []).append(n)
    nodes, edges = [], []

    def weight(nd):  # subtree size: spreads small subtrees more evenly than a leaf count
        return 1 + sum(weight(c) for c in kids.get(nd["id"], []))

    RING = float(os.environ.get("FIG6_RING", "1.0"))  # radial spacing per tree depth (node coordinates are in these units)

    def walk(nd, depth, a0, a1, parent_xy, parent_idx):
        ang = 0.5 * (a0 + a1); r = RING * depth; x, y = r * np.cos(ang), r * np.sin(ang)
        comp = ckey(nd["identifier"]); rr = rank_u.loc[comp] if comp in rank_u.index else None
        own = nd.get("own_reward")
        if own is None and rr is not None: own = float(rr.reward)  # the root is never self-evaluated
        q = nd["total_reward"] / nd["visits"] if nd.get("visits") else 0.0
        # label position: pushed outward along the radial direction so neighbouring labels separate
        lx, ly = (x + 0.42 * np.cos(ang), y + 0.42 * np.sin(ang)) if depth else (x, y - 0.45)
        nodes.append([x, y, float(own or 0.0), float(rr.r_S) if rr is not None else 0.0, float(rr.r_dos) if rr is not None else 0.0, q,
                      int(rr["rank"]) if rr is not None else 0, 1 if depth == 0 else 0, comp, lx, ly, 1 if nd["identifier"] in budget_ids else 0,
                      int(nd.get("visits") or 0), float(nd.get("subtree_best") or 0.0)])
        parents.append(parent_idx)
        ch = kids.get(nd["id"], [])
        if ch:
            tot = sum(weight(c) for c in ch); a = a0; me = len(nodes) - 1
            for c in ch:
                span = (a1 - a0) * weight(c) / tot; walk(c, depth + 1, a, a + span, (x, y), me); a += span

    parents = []
    walk(byid[tree["root_id"]], 0, 0, 2 * np.pi, None, None)
    # Relax overlapping nodes: push any pair closer than D_MIN apart (root fixed), with a weak pull
    # back towards the radial position so the tree keeps its shape.
    R_BIG = float(os.environ.get("FIG6_R_BIG", "0.50")); R_SMALL = float(os.environ.get("FIG6_R_SMALL", "0.25")); GAP = float(os.environ.get("FIG6_GAP", "0.10"))   # node radii in layout units (top-15 nodes are larger)
    SUF = os.environ.get("FIG6_SUFFIX", "")   # variant layouts are written to fig6_*<suffix>.dat
    rad_of = np.array([R_BIG if (0 < n[6] <= 15 or n[7] == 1) else R_SMALL for n in nodes])
    P = np.array([[n[0], n[1]] for n in nodes]); P0 = P.copy()
    for _ in range(600):
        disp = np.zeros_like(P)
        for i in range(len(P)):
            for j in range(i + 1, len(P)):
                d = P[j] - P[i]; L = np.hypot(*d); dmin = rad_of[i] + rad_of[j] + GAP
                if L < dmin:
                    push = (dmin - L) / 2 * (d / L if L > 1e-9 else np.array([1.0, 0.0]))
                    disp[i] -= push; disp[j] += push
        disp += 0.05 * (P0 - P); disp[0] = 0
        P += disp
        if np.abs(disp).max() < 1e-4: break
    if os.environ.get("FIG6_ROTATE", "1") == "1": P = P @ np.array([[0.0, 1.0], [-1.0, 0.0]])   # rotate 90 deg: the tree's long axis runs along the (wider) panel
    for k, n in enumerate(nodes):
        n[0], n[1] = float(P[k, 0]), float(P[k, 1])
        n[9], n[10] = n[0], n[1]                      # rank labels sit on the node
        n.append(float(rad_of[k]))
    for k, pk in enumerate(parents):
        if pk is not None: edges.append((P[pk, 0], P[pk, 1], P[k, 0] - P[pk, 0], P[k, 1] - P[pk, 1], rad_of[pk], rad_of[k]))
    with open(D / f"fig6_nodes{SUF}.dat", "w") as fh:
        fh.write("# x y own_reward r_S r_dos Q true_rank is_root compound label_x label_y in_budget visits v_n radius\n")
        for n in nodes: fh.write(" ".join(f"{v:.5f}" if isinstance(v, float) else str(v) for v in n) + "\n")
    xs = [n[0] for n in nodes] + [n[9] for n in nodes]; ys = [n[1] for n in nodes] + [n[10] for n in nodes]
    (D / f"fig6_bbox{SUF}.gp").write_text(f"XMIN = {min(xs)-0.3:.3f}; XMAX = {max(xs)+0.3:.3f}; YMIN = {min(ys)-0.3:.3f}; YMAX = {max(ys)+0.3:.3f}\nROOTX = {nodes[0][0]:.5f}; ROOTY = {nodes[0][1]:.5f}; ROOTR = {nodes[0][-1]:.3f}\n")
    np.savetxt(D / f"fig6_edges{SUF}.dat", np.array(edges), fmt="%.5f")
    numbers["u_tree_depth"] = int(max(np.hypot(n[0], n[1]) for n in nodes))
    # --- lanthanide + U --------------------------------------------------
    run = H / "representative/lanthanide_u/seed_0"; s = json.load(open(run / "summary.json"))
    numbers["f_nodes"] = s["unique_materials"]; numbers["f_coverage_pct"] = round(100 * s["unique_materials"] / 1728, 1)
    numbers["f_iterations"] = s["iterations"]; numbers["f_budget"] = yaml_budget(run)
    numbers["f_evaluations"] = s.get("evaluations"); numbers["f_evaluated_pct"] = round(100 * (s.get("evaluations") or 0) / 1728, 1)
    top = mcts_top(run, rank_f)
    rows = [f"{r.mcts_rank} & {int(r.true_rank)} & {tex(r.compound)} & {r.e_above_hull:.4f} & {r.r_S:.4f} & {r.r_dos:.3f} & {r.reward:.3f} \\\\" for r in top.itertuples()]
    (T / "table2_top15_full_rows.tex").write_text("\n".join(rows) + "\n")
    numbers["f_top15_true_ranks"] = top.true_rank.astype(int).tolist(); numbers["f_top15"] = top.compound.tolist()
    numbers["f_start_rank"] = int(rank_f.loc["TbCu6Sn6"]["rank"])
    sp = rank_f.reset_index(); valid = sp[sp.data_quality == "valid"]
    np.savetxt(D / "fig9_space.dat", valid[["r_dos", "e_above_hull"]].to_numpy(), fmt="%.5f")
    np.savetxt(D / "fig9_mcts_top15.dat", top[["r_dos", "e_above_hull", "mcts_rank"]].to_numpy(), fmt="%.5f %.5f %d")
    lit = []
    for l in (H / "data/experimental_compounds.txt").read_text().splitlines():
        m = re.match(r"\s*\d+\s+([A-Z][a-z]?)-([A-Z][a-z]?)-([A-Z][a-z]?)\s", l)
        if m: lit.append(f"{m[3]}{m[1]}6{m[2]}6")
    litd = valid[valid.compound.isin(lit)]
    np.savetxt(D / "fig9_literature.dat", litd[["r_dos", "e_above_hull"]].to_numpy(), fmt="%.5f")
    numbers["lit_n"] = int(len(litd)); numbers["lit_max_ehull"] = round(float(litd.e_above_hull.max()), 4)
    numbers["mcts15_max_ehull"] = round(float(top.e_above_hull.max()), 4); numbers["mcts15_max_ehull_compound"] = top.loc[top.e_above_hull.idxmax(), "compound"]
    for el, lab in (("f", "f"), ("M", "M"), ("X", "X")):
        numbers[f"f_top15_{lab}_counts"] = top.compound.map(lambda c: rank_f.loc[c][el]).value_counts().to_dict()
    json.dump(numbers, open(H / "tables/text_numbers_representative.json", "w"), indent=1)
    print(json.dumps(numbers, indent=1))


def grid():
    m = pd.read_csv(H / "run_metrics_grid.csv"); g = m[m.group == "grid"]
    depths, nrolls = [1, 2, 3], [1, 3, 5, 10]; quartiles = ["0-25", "25-50", "50-75", "75-100"]
    for metric in ("found_best", "mean_rank_top15", "frac_explored", "frac_evaluated"):
        for q in quartiles:
            sub = g[g.quartile == q]
            with open(D / f"fig7_{metric}_{q}.dat", "w") as fh:
                for i, d in enumerate(depths):
                    for j, n in enumerate(nrolls):
                        v = sub[(sub.rollout_depth == d) & (sub.n_rollout == n)][metric]
                        fh.write(f"{j} {i} {v.mean():.4f} {v.sem() if len(v) > 1 else 0:.4f} {len(v)}\n")
                    fh.write("\n")
    # Fig 8: config4 (D=3, N=3) convergence by quartile: best reward vs unique compounds
    best = rank_u.reward.max()
    for q in quartiles:
        runs = g[(g.config == "config4_deep_many") & (g.quartile == q)]
        curves = []
        for rd in runs.run_dir:
            c = pd.read_csv(Path(rd) / "convergence.csv")
            by_u = c.groupby("unique_materials").best_reward.max().reindex(range(1, 109)).ffill()
            curves.append(by_u.to_numpy())
        a = np.array(curves)
        med, lo, hi = np.nanmedian(a, 0), np.nanpercentile(a, 25, 0), np.nanpercentile(a, 75, 0)
        np.savetxt(D / f"fig8_{q}.dat", np.c_[np.arange(1, 109), med, lo, hi], fmt="%.5f")
    (D / "fig8_meta.gp").write_text(f"BEST95 = {0.95 * best:.5f}\n")
    summary = g.groupby(["config", "rollout_depth", "n_rollout"]).agg(found=("found_best", "mean"), rank15=("mean_rank_top15", "mean"), explored=("frac_explored", "mean"), evaluated=("frac_evaluated", "mean")).round(3)
    summary.to_csv(T / "grid_summary.csv"); print(summary.to_string())
    q25 = g[g.quartile == "0-25"].groupby(["rollout_depth", "n_rollout"]).agg(found=("found_best", "mean"), rank15=("mean_rank_top15", "mean"), explored=("frac_explored", "mean"), evaluated=("frac_evaluated", "mean")).round(3)
    q25.to_csv(T / "grid_summary_q0-25.csv"); print("\n0-25 quartile:\n" + q25.to_string())


if __name__ == "__main__":
    T.mkdir(exist_ok=True)
    for stage in sys.argv[1:]:
        {"representative": representative, "grid": grid}[stage]()
