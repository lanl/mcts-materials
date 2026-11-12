#!/usr/bin/env python3
"""Baseline search strategies on the RM6X6 design spaces, run with the same evaluation
budgets, starting compounds and seeds as the MCTS searches.

Every method sees only the reward of the compounds it has evaluated (looked up in the
reference ranking, i.e. the same cached MACE + DFT reward the MCTS runs used) and
counts unique evaluated compounds, as the MCTS budget does.

Methods
  random      uniform random order (the start compound first)
  walk        random walk over neighboring compositions (the MCTS move set)
  greedy      steepest-ascent local search over the move set; random restart at a
              local optimum
  ga          genetic algorithm: population 20, tournament selection, uniform
              site-wise crossover, neighbor-move mutation, 2 elites
  bo          Bayesian optimization: Gaussian process (Matern 5/2, ARD) on element
              descriptors of the three sites, expected improvement over all
              unevaluated compositions
  al          active learning: extra-trees ensemble on the same descriptors,
              upper-confidence-bound acquisition (mean + std over trees)
  rule_mnfe   domain rule: all M = Mn or Fe compositions first (random order), then
              the rest at random

usage: python baselines.py <space: u_only|full> <method> <start_index> <seed>
       python baselines.py --all <space>   (writes every (method, start, seed) row)
"""
import json, sys, warnings
from pathlib import Path
import numpy as np, pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from mcts_framework.intermetallic import elements as EL

H = Path(__file__).resolve().parent; S = H.parent
warnings.filterwarnings("ignore")
SYM = {57: "La", 58: "Ce", 59: "Pr", 60: "Nd", 61: "Pm", 62: "Sm", 63: "Eu", 64: "Gd", 65: "Tb", 66: "Dy", 67: "Ho",
       68: "Er", 69: "Tm", 70: "Yb", 71: "Lu", 92: "U"}
from ase.data import atomic_numbers as Z, chemical_symbols as CS

R_ALL = ["La", "Ce", "Pr", "Nd", "Pm", "Sm", "Eu", "Gd", "Tb", "Dy", "Ho", "Er", "Tm", "Yb", "Lu", "U"]
M_ALL = ["Ti", "V", "Cr", "Mn", "Fe", "Co", "Ni", "Cu", "Zn", "Zr", "Nb", "Mo", "Tc", "Ru", "Rh", "Pd", "Ag", "Cd",
         "Hf", "Ta", "W", "Re", "Os", "Ir", "Pt", "Au", "Hg"]
X_ALL = ["Si", "Ge", "Sn", "Pb"]
BUDGET = {"u_only": 54, "full": 864}
MODE = {"u_only": "u_only", "full": "lanthanides_u"}


def name(r, m, x):
    return f"{r}{m}6{x}6"


class Space:
    def __init__(self, space):
        self.space = space
        rk = pd.read_csv(S / "rankings" / ("u_only_ranking.csv" if space == "u_only" else "full_ranking.csv"))
        self.reward = dict(zip(rk.compound, rk.reward)); self.rank = dict(zip(rk.compound, rk["rank"]))
        Rs = ["U"] if space == "u_only" else R_ALL
        self.comps = [(r, m, x) for r in Rs for m in M_ALL for x in X_ALL]
        assert all(name(*c) in self.reward for c in self.comps), "ranking misses a compound"
        self.idx = {c: i for i, c in enumerate(self.comps)}
        self.best = max(self.reward.values())
        self.mode = MODE[space]
        self._nb = {}

    def neighbors(self, c):
        """The MCTS expansion move set: every combination of single-step moves on the
        R, M and X axes (move_step 1, U bridge 'wide'), excluding the compound itself."""
        if c in self._nb:
            return self._nb[c]
        r, m, x = c
        ms = [CS[z] for z in EL.metal_moves(Z[m], 1)]
        xs = [CS[z] for z in EL.group_iv_moves(Z[x], 1)]
        rs = [CS[z] for z in EL.f_block_moves(Z[r], self.mode, 1, "wide")]
        out = [(a, b, d) for a in rs for b in ms for d in xs if (a, b, d) != c and (a, b, d) in self.idx]
        self._nb[c] = out
        return out

    def features(self):
        from pymatgen.core.periodic_table import Element
        def desc(sym):
            e = Element(sym)
            rad = e.atomic_radius or e.atomic_radius_calculated or 1.8
            return [e.Z, e.row, e.group, e.X if e.X == e.X else 1.2, float(rad)]
        F = np.array([desc(r) + desc(m) + desc(x) for r, m, x in self.comps], float)
        sd = F.std(0); sd[sd == 0] = 1
        return (F - F.mean(0)) / sd


class Tracker:
    """Records unique evaluations in order; stops at the budget."""
    def __init__(self, sp, budget):
        self.sp, self.budget, self.order, self.seen = sp, budget, [], {}

    def eval(self, c):
        if c in self.seen:
            return self.seen[c]
        if len(self.order) >= self.budget:
            raise StopIteration
        v = self.sp.reward[name(*c)]; self.seen[c] = v; self.order.append(c)
        return v

    @property
    def full(self):
        return len(self.order) >= self.budget


# ------------------------------------------------------------------ methods
def m_random(sp, start, rng, tr):
    tr.eval(start)
    for i in rng.permutation(len(sp.comps)):
        tr.eval(sp.comps[i])


def m_rule_mnfe(sp, start, rng, tr):
    tr.eval(start)
    first = [c for c in sp.comps if c[1] in ("Mn", "Fe")]; rest = [c for c in sp.comps if c[1] not in ("Mn", "Fe")]
    for grp in (first, rest):
        for i in rng.permutation(len(grp)):
            tr.eval(grp[i])


def m_walk(sp, start, rng, tr):
    c = start; tr.eval(c)
    for _ in range(200 * tr.budget):
        nb = sp.neighbors(c); c = nb[rng.integers(len(nb))]; tr.eval(c)
    # if a walk cannot fill the budget (tiny space) finish at random
    for i in rng.permutation(len(sp.comps)):
        tr.eval(sp.comps[i])


def m_greedy(sp, start, rng, tr):
    c = start; v = tr.eval(c)
    while True:
        nb = sp.neighbors(c)
        vals = [(tr.eval(n), n) for n in nb]
        bv, bn = max(vals, key=lambda t: (t[0], rng.random()))
        if bv > v:
            c, v = bn, bv
        else:  # local optimum: restart from a random unevaluated compound
            cand = [k for k in sp.comps if k not in tr.seen]
            if not cand:
                return
            c = cand[rng.integers(len(cand))]; v = tr.eval(c)


def m_ga(sp, start, rng, tr, pop_n=20, elite=2, pmut=0.5):
    pop = [start] + [sp.comps[i] for i in rng.choice(len(sp.comps), pop_n - 1, replace=False)]
    fit = [tr.eval(c) for c in pop]
    while True:
        order = np.argsort(fit)[::-1]
        new = [pop[i] for i in order[:elite]]
        while len(new) < pop_n:
            def tour():
                k = rng.choice(len(pop), 3, replace=False); return pop[max(k, key=lambda i: fit[i])]
            a, b = tour(), tour()
            child = tuple(a[s] if rng.random() < 0.5 else b[s] for s in range(3))
            if rng.random() < pmut or child in (a, b):
                nb = sp.neighbors(child); child = nb[rng.integers(len(nb))]
            new.append(child)
        pop = new; fit = [tr.eval(c) for c in pop]


def _surrogate_loop(sp, start, rng, tr, kind, n_init=5):
    F = sp.features()
    tr.eval(start)
    for i in rng.choice(len(sp.comps), n_init - 1, replace=False):
        tr.eval(sp.comps[i])
    if kind == "bo":
        from sklearn.gaussian_process import GaussianProcessRegressor
        from sklearn.gaussian_process.kernels import Matern, WhiteKernel, ConstantKernel
        from scipy.stats import norm
        kern = ConstantKernel(1.0) * Matern(length_scale=np.ones(F.shape[1]), nu=2.5) + WhiteKernel(1e-3)
        gp = None
    else:
        from sklearn.ensemble import ExtraTreesRegressor
    step = 0
    while True:
        idx = [sp.idx[c] for c in tr.order]; y = np.array([tr.seen[c] for c in tr.order])
        mask = np.ones(len(sp.comps), bool); mask[idx] = False
        cand = np.where(mask)[0]
        if kind == "bo":
            ym, ys = y.mean(), y.std() + 1e-9
            if gp is None or step % 10 == 0:          # refit hyperparameters every 10 evaluations
                gp = GaussianProcessRegressor(kern, normalize_y=False, n_restarts_optimizer=0, random_state=0)
                gp.fit(F[idx], (y - ym) / ys); kern_fit = gp.kernel_
            else:
                gp = GaussianProcessRegressor(kern_fit, optimizer=None); gp.fit(F[idx], (y - ym) / ys)
            mu, sd = gp.predict(F[cand], return_std=True); sd = np.maximum(sd, 1e-9)
            best = (y.max() - ym) / ys; z = (mu - best) / sd
            acq = (mu - best) * norm.cdf(z) + sd * norm.pdf(z)
        else:
            et = ExtraTreesRegressor(100, min_samples_leaf=1, random_state=int(rng.integers(1 << 30)), n_jobs=1)
            et.fit(F[idx], y)
            P = np.stack([t.predict(F[cand]) for t in et.estimators_])
            acq = P.mean(0) + P.std(0)
        pick = cand[np.argmax(acq + 1e-12 * rng.random(len(cand)))]
        tr.eval(sp.comps[pick]); step += 1


METHODS = {"random": m_random, "walk": m_walk, "greedy": m_greedy, "ga": m_ga,
           "bo": lambda *a: _surrogate_loop(*a, kind="bo"), "al": lambda *a: _surrogate_loop(*a, kind="al"),
           "rule_mnfe": m_rule_mnfe}


def starts(space):
    if space == "u_only":
        st = json.load(open(S / "grid_starting_materials.json"))
        return [("U", pk["material"][:-2], pk["material"][-2:]) for picks in st.values() for pk in picks]
    import re
    fs = json.load(open(S / "full_starting_materials.json"))     # written by generate_study.py full
    return [tuple(re.match(r"([A-Z][a-z]?)([A-Z][a-z]?)6([A-Z][a-z]?)6", x["compound"]).groups()) for x in fs]


def run(space, method, k, seed):
    sp = Space(space); start = starts(space)[k]; rng = np.random.default_rng(1000 * k + seed)
    tr = Tracker(sp, BUDGET[space])
    try:
        METHODS[method](sp, start, rng, tr)
    except StopIteration:
        pass
    rk = np.array([sp.rank[name(*c)] for c in tr.order]); rw = np.array([sp.reward[name(*c)] for c in tr.order])
    run_best = np.maximum.accumulate(rw)
    out = {"space": space, "method": method, "start": name(*start), "start_index": k, "seed": seed, "n_eval": len(rk),
           "evals_to_best": int(np.argmax(rk == 1) + 1) if (rk == 1).any() else None,
           "evals_to_95": int(np.argmax(run_best >= 0.95 * sp.best) + 1) if (run_best >= 0.95 * sp.best).any() else None}
    for E in ((54,) if space == "u_only" else (432, 864)):
        head = rk[:E]; out[f"found_best@{E}"] = int((head == 1).any()); out[f"rank15@{E}"] = float(np.sort(head)[:15].mean())
    out["order"] = [name(*c) for c in tr.order]
    return out


if __name__ == "__main__":
    if sys.argv[1] == "--all":
        space = sys.argv[2]; meths = sys.argv[3].split(",") if len(sys.argv) > 3 else list(METHODS)
        from concurrent.futures import ProcessPoolExecutor
        ks = [int(x) for x in sys.argv[5].split(",")] if len(sys.argv) > 5 else list(range(len(starts(space))))
        jobs = [(space, m, k, s) for m in meths for k in ks for s in range(5)]
        rows = []
        with ProcessPoolExecutor(int(sys.argv[4]) if len(sys.argv) > 4 else 100) as ex:
            for r in ex.map(run, *zip(*jobs)):
                rows.append(r)
        df = pd.DataFrame([{k: v for k, v in r.items() if k != "order"} for r in rows])
        tag = ("_".join(meths) if len(meths) < len(METHODS) else "all") + (f"_starts{sys.argv[5].replace(',', '-')}" if len(sys.argv) > 5 else "")
        df.to_csv(H / f"baselines_{space}_{tag}.csv", index=False)
        with open(H / f"baselines_{space}_{tag}_orders.jsonl", "w") as fh:
            for r in rows:
                fh.write(json.dumps({k: r[k] for k in ("method", "start", "seed", "order")}) + "\n")
        print(df.groupby("method").mean(numeric_only=True).round(2).to_string())
    else:
        r = run(sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]))
        print({k: v for k, v in r.items() if k != "order"})
