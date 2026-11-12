"""
Tests for progressive widening, the 'stats' expansion prior and the 'prior'
rollout policy.

Uses a 2-D integer grid: a material is a point (x, y), the moves are the eight
neighbors (so a node has up to eight children, enough for widening to matter),
and the reward is minus the distance to a target. The move tokens are the two
coordinates, so a candidate's estimated reward is the mean reward of evaluated
points sharing its x or its y.

© 2026. Triad National Security, LLC. All rights reserved.
"""

from typing import Dict, Hashable, List

import pytest

from mcts_framework.core.material import Material
from mcts_framework.core.move_generator import MoveGenerator
from mcts_framework.core.evaluator import PropertyEvaluator
from mcts_framework.core.reward import RewardFunction
from mcts_framework.core.selection import UCB1
from mcts_framework.core.mcts import MCTS
from mcts_framework.core.config import MCTSConfig
from pydantic import ValidationError


class GridMaterial(Material):
    def __init__(self, x: int, y: int):
        self.x, self.y = x, y

    def get_identifier(self) -> str:
        return f"{self.x},{self.y}"

    def copy(self) -> "GridMaterial":
        return GridMaterial(self.x, self.y)


class GridMoves(MoveGenerator[GridMaterial]):
    def __init__(self, lo: int = -6, hi: int = 6):
        self.lo, self.hi = lo, hi

    def generate_moves(self, m: GridMaterial) -> List[GridMaterial]:
        out = []
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == dy == 0:
                    continue
                x, y = m.x + dx, m.y + dy
                if self.lo <= x <= self.hi and self.lo <= y <= self.hi:
                    out.append(GridMaterial(x, y))
        return out

    def move_tokens(self, m: GridMaterial) -> List[Hashable]:
        return [("x", m.x), ("y", m.y)]

    def random_material(self, m: GridMaterial, rng) -> GridMaterial:
        return GridMaterial(rng.randint(self.lo, self.hi), rng.randint(self.lo, self.hi))

    def descriptors(self, m: GridMaterial):
        import numpy as np
        return np.array([m.x, m.y], float)

    def all_materials(self, m: GridMaterial) -> List[GridMaterial]:
        return [GridMaterial(x, y) for x in range(self.lo, self.hi + 1) for y in range(self.lo, self.hi + 1)]


class DistanceEvaluator(PropertyEvaluator):
    def __init__(self, tx: int, ty: int):
        super().__init__()
        self.tx, self.ty = tx, ty

    async def _compute(self, m: GridMaterial) -> Dict[str, float]:
        return {"d": abs(m.x - self.tx) + abs(m.y - self.ty)}


class NegDistance(RewardFunction):
    def compute_reward(self, p: Dict[str, float]) -> float:
        return -p["d"]

    def get_property_names(self) -> List[str]:
        return ["d"]


def make(target=(4, 4), start=(0, 0), **kw) -> MCTS:
    return MCTS(
        root_material=GridMaterial(*start),
        move_generator=GridMoves(),
        property_evaluator=DistanceEvaluator(*target),
        reward_function=NegDistance(),
        selection_strategy=UCB1(),
        seed=kw.pop("seed", 0),
        termination_limit=1000,
        search_mode="thorough",
        **kw,
    )


# --- widening cap ---------------------------------------------------------


def test_widening_cap_values():
    m = make(progressive_widening=0.5, pw_base=2.0, n_rollout=0)
    assert [m.widening_cap(n) for n in (0, 1, 2, 4, 9, 16, 100)] == [2, 2, 3, 4, 6, 8, 20]
    assert make(n_rollout=0).widening_cap(1) > 10**6  # off: unlimited


def test_widening_cap_is_at_least_one():
    m = make(progressive_widening=0.5, pw_base=0.1, n_rollout=0)
    assert m.widening_cap(0) == 1 and m.widening_cap(1) == 1


def test_invalid_widening_options_rejected():
    with pytest.raises(ValueError):
        make(progressive_widening=1.5)
    with pytest.raises(ValueError):
        make(pw_base=0.0)
    with pytest.raises(ValueError):
        make(expansion_prior="learned")
    with pytest.raises(ValueError):
        make(rollout_policy="greedy")
    with pytest.raises(ValueError):
        make(rollout_epsilon=2.0)


# --- expansion with and without widening -----------------------------------


@pytest.mark.asyncio
async def test_classic_expansion_attaches_every_child_before_descending():
    m = make(n_rollout=0, rollout_depth=0)
    await m.run(iterations=8)
    # root (0,0) has 8 neighbors: after 8 iterations they are all attached
    # and no grandchild exists yet
    assert len(m.root.children) == 8
    assert all(c.is_leaf() for c in m.root.children)


@pytest.mark.asyncio
async def test_widening_descends_before_the_root_is_fully_expanded():
    m = make(progressive_widening=0.5, pw_base=1.0, n_rollout=0, rollout_depth=0)
    await m.run(iterations=8)
    assert len(m.root.children) < 8
    assert any(not c.is_leaf() for c in m.root.children)
    # the cap is respected at every node
    for node in m.all_nodes():
        assert len(node.children) <= m.widening_cap(node.visits) or not node.expandable


@pytest.mark.asyncio
async def test_widening_keeps_materials_unique_and_consistent():
    m = make(progressive_widening=0.5, pw_base=2.0, n_rollout=2, rollout_depth=2)
    await m.run(iterations=120)
    ids = [n.material.get_identifier() for n in m.all_nodes()]
    assert len(ids) == len(set(ids))
    assert set(ids) == m.visited_materials
    assert m.best_reward == 0.0 and m.best_node.material.get_identifier() == "4,4"


# --- reward estimates -------------------------------------------------------


@pytest.mark.asyncio
async def test_estimate_is_none_before_any_evaluation_and_exact_after():
    m = make(expansion_prior="stats", n_rollout=0, rollout_depth=0)
    assert m.estimated_reward(GridMaterial(1, 1)) is None
    await m.run(iterations=3)
    child = m.root.children[0]
    assert m.estimated_reward(child.material) == child.own_reward


@pytest.mark.asyncio
async def test_estimate_averages_token_means():
    m = make(expansion_prior="stats", n_rollout=0, rollout_depth=0)
    m._record_reward(GridMaterial(1, 0), -7.0)   # token ("x",1): -7 ; ("y",0): -7
    m._record_reward(GridMaterial(2, 0), -5.0)   # token ("x",2): -5 ; ("y",0): mean -6
    m._record_reward(GridMaterial(2, 3), -3.0)   # ("x",2): mean -4 ; ("y",3): -3
    # unseen material (2,0)? known -> exact
    assert m.estimated_reward(GridMaterial(2, 0)) == -5.0
    # (2,5): x=2 mean -4, y=5 unseen -> overall mean -5 ; estimate -4.5
    assert m.estimated_reward(GridMaterial(2, 5)) == pytest.approx(-4.5)
    # recording the same material twice does not double count
    m._record_reward(GridMaterial(1, 0), -7.0)
    assert m._token_count[("x", 1)] == 1


@pytest.mark.asyncio
async def test_stats_prior_attaches_the_best_estimated_candidate_first():
    m = make(expansion_prior="stats", n_rollout=0, rollout_depth=0)
    # pretend the run has learned that larger x and y are better
    for x in range(-2, 3):
        m._record_reward(GridMaterial(x, 9), float(x))
        m._record_reward(GridMaterial(9, x), float(x))
    child = await m._expand(m.root)
    assert child.material.get_identifier() == "1,1"


@pytest.mark.asyncio
async def test_prior_rollout_walks_toward_better_estimates():
    m = make(rollout_policy="prior", rollout_epsilon=0.0, rollout_depth=3, n_rollout=1)
    for x in range(-2, 5):
        m._record_reward(GridMaterial(x, 9), float(x))
        m._record_reward(GridMaterial(9, x), float(x))
    walk = m._sample_walk(GridMaterial(0, 0))
    assert [w.get_identifier() for w in walk] == ["1,1", "2,2", "3,3"]


@pytest.mark.asyncio
async def test_defaults_do_not_change_the_search():
    """With every option off, the run is identical to the classic algorithm."""
    a = make(n_rollout=2, rollout_depth=2, seed=3)
    b = make(n_rollout=2, rollout_depth=2, seed=3, expansion_prior="none",
             rollout_policy="random", progressive_widening=None)
    await a.run(iterations=60)
    await b.run(iterations=60)
    assert [n.material.get_identifier() for n in a.all_nodes()] == \
        [n.material.get_identifier() for n in b.all_nodes()]
    assert a.reward_history == b.reward_history


@pytest.mark.asyncio
async def test_widening_with_prior_reaches_the_target_with_fewer_evaluations():
    """From a far corner, widening + prior should need fewer evaluations than
    classic expansion on this smooth landscape (averaged over seeds)."""
    def evals_to_target(mcts: MCTS) -> int:
        for i, r in enumerate(mcts.reward_history):
            if r == 0.0:
                return mcts.evaluations_history[i]
        return 10**9

    classic, improved = [], []
    for seed in range(4):
        a = make(target=(5, 5), start=(-5, -5), n_rollout=2, rollout_depth=2, seed=seed)
        b = make(target=(5, 5), start=(-5, -5), n_rollout=2, rollout_depth=2, seed=seed,
                 progressive_widening=0.5, pw_base=2.0, expansion_prior="stats", rollout_policy="prior")
        await a.run(iterations=400)
        await b.run(iterations=400)
        classic.append(evals_to_target(a))
        improved.append(evals_to_target(b))
    assert sum(improved) < sum(classic)


# --- warm start -------------------------------------------------------------


@pytest.mark.asyncio
async def test_warm_start_evaluates_random_materials_before_the_search():
    m = make(warm_start=5, expansion_prior="stats", n_rollout=0, rollout_depth=0)
    await m.run(iterations=0)                                # warm start only
    ids = {w.get_identifier() for w in m.warm_start_materials}
    assert len(ids) == 5 and "0,0" not in ids
    assert ids == set(m._known_rewards)                      # rewards recorded ...
    assert m.root.is_leaf()                                  # ... but nothing attached
    await m.run(iterations=1)                                # no second warm start
    assert len(m.warm_start_materials) == 5
    first = m.root.children[0].material.get_identifier()
    # 5 seeds, plus the first child unless the prior attached a seed (already evaluated)
    assert m.evaluations_history[0] == 5 + (0 if first in ids else 1)


@pytest.mark.asyncio
async def test_warm_start_counts_against_the_budget():
    m = make(warm_start=5, n_rollout=0, rollout_depth=0, max_evaluations=7)
    await m.run(iterations=50)
    assert len(m.property_evaluator.cache) == 7


@pytest.mark.asyncio
async def test_warm_start_is_skipped_without_a_sampler():
    from mcts_framework.core.move_generator import MoveGenerator

    class NoSampler(GridMoves):
        random_material = MoveGenerator.random_material

    m = MCTS(GridMaterial(0, 0), NoSampler(), DistanceEvaluator(4, 4), NegDistance(), UCB1(),
             seed=0, warm_start=5, n_rollout=0, rollout_depth=0)
    await m.run(iterations=2)
    assert m.warm_start_materials == [] and m.evaluations_history[0] == 1


def test_warm_start_validation():
    with pytest.raises(ValueError):
        make(warm_start=-1)
    assert MCTSConfig().warm_start == 0 and MCTSConfig(warm_start=20).warm_start == 20
    with pytest.raises(ValidationError):
        MCTSConfig(warm_start=-1)


# --- exhausted leaves ---------------------------------------------------------


@pytest.mark.asyncio
async def test_exhausted_leaves_are_terminated_and_the_search_keeps_evaluating():
    """An exhausted leaf (no children, nothing left to attach) is terminated once simulated, so the
    search does not keep re-selecting it; the run then evaluates at least as many materials."""
    a = make(target=(4, 4), start=(0, 0), n_rollout=0, rollout_depth=0, exploration_constant=0.3, seed=1)
    b = make(target=(4, 4), start=(0, 0), n_rollout=0, rollout_depth=0, exploration_constant=0.3, seed=1, terminate_exhausted=True)
    await a.run(iterations=300)
    await b.run(iterations=300)
    exhausted = lambda m: [n for n in m.all_nodes() if n.is_leaf() and not n.expandable and n.own_reward is not None]
    assert exhausted(b) and all(n.terminated for n in exhausted(b))
    assert any(not n.terminated for n in exhausted(a))
    assert len(b.property_evaluator.cache) >= len(a.property_evaluator.cache)
    assert a.best_reward == 0.0 and b.best_reward == 0.0


def test_terminate_exhausted_config_default():
    assert MCTSConfig().terminate_exhausted is False and MCTSConfig(terminate_exhausted=True).terminate_exhausted is True


# --- model prior and global proposals --------------------------------------------


@pytest.mark.asyncio
async def test_model_prior_estimates_follow_the_gp():
    m = make(expansion_prior="model", n_rollout=0, rollout_depth=0)
    assert m._model_estimates([GridMaterial(1, 1)]) is None          # nothing evaluated yet
    for x in range(-3, 4):
        m._record_reward(GridMaterial(x, 0), -abs(x - 2.0))         # peak at x = 2
    acq = m._model_estimates([GridMaterial(2, 0), GridMaterial(-3, 0), GridMaterial(2, 1)])
    assert acq is not None and acq[0] > acq[1]                      # near the peak scores higher than far from it
    child = await m._expand(m.root)                                  # root (0,0): neighbors toward +x preferred
    assert child.material.x == 1


@pytest.mark.asyncio
async def test_global_proposals_attach_non_neighbors():
    m = make(target=(5, 5), start=(-5, -5), expansion_prior="model", global_proposals=2, n_rollout=0, rollout_depth=0, progressive_widening=0.5)
    await m.run(iterations=40)
    far = [n for n in m.all_nodes() if n.parent is not None and max(abs(n.material.x - n.parent.material.x), abs(n.material.y - n.parent.material.y)) > 1]
    assert far, "no global proposal was attached"
    ids = [n.material.get_identifier() for n in m.all_nodes()]
    assert len(ids) == len(set(ids))


@pytest.mark.asyncio
async def test_model_prior_falls_back_without_descriptors():
    from conftest import IntMaterial, LineMoves, DistanceEvaluator, NegDistanceReward
    m = MCTS(IntMaterial(0), LineMoves(), DistanceEvaluator(5), NegDistanceReward(), UCB1(), seed=0, expansion_prior="model", n_rollout=0, rollout_depth=0)
    await m.run(iterations=30)
    assert m.best_reward == 0.0


def test_model_prior_validation():
    with pytest.raises(ValueError):
        make(acquisition="pi")
    with pytest.raises(ValueError):
        make(global_proposals=-1)
    assert MCTSConfig(expansion_prior="model", global_proposals=2).global_proposals == 2
    with pytest.raises(ValidationError):
        MCTSConfig(acquisition="pi")


# --- config -----------------------------------------------------------------


def test_config_defaults_and_validation():
    cfg = MCTSConfig()
    assert cfg.progressive_widening is None and cfg.pw_base == 1.0
    assert cfg.expansion_prior == "none" and cfg.rollout_policy == "random"
    assert MCTSConfig(progressive_widening=0.5, expansion_prior="stats", rollout_policy="prior").pw_base == 1.0
    with pytest.raises(ValidationError):
        MCTSConfig(progressive_widening=0.0)
    with pytest.raises(ValidationError):
        MCTSConfig(progressive_widening=1.2)
    with pytest.raises(ValidationError):
        MCTSConfig(expansion_prior="learned")
