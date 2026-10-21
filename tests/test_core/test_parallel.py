"""
Tests for the concurrent parts of the search: in-flight de-duplication in
PropertyEvaluator, concurrent rollout evaluation, and parallel_steps.

© 2026. Triad National Security, LLC. All rights reserved.
"""

import asyncio
from typing import Dict

import pytest

from conftest import DistanceEvaluator, IntMaterial, LineMoves, NegDistanceReward
from mcts_framework.core.mcts import MCTS
from mcts_framework.core.selection import UCB1


class SlowEvaluator(DistanceEvaluator):
    """DistanceEvaluator that sleeps, and records how many _compute overlap."""

    def __init__(self, target: int, delay: float = 0.01):
        super().__init__(target)
        self.delay = delay
        self.active = 0
        self.max_active = 0

    async def _compute(self, material: IntMaterial) -> Dict[str, float]:
        self.active += 1
        self.max_active = max(self.max_active, self.active)
        try:
            await asyncio.sleep(self.delay)
            return await super()._compute(material)
        finally:
            self.active -= 1


def make_mcts(evaluator, **kwargs) -> MCTS:
    return MCTS(
        root_material=IntMaterial(kwargs.pop("start", 0)),
        move_generator=LineMoves(),
        property_evaluator=evaluator,
        reward_function=NegDistanceReward(),
        selection_strategy=UCB1(),
        seed=kwargs.pop("seed", 0),
        **kwargs,
    )


# --- PropertyEvaluator in-flight de-duplication --------------------------


@pytest.mark.asyncio
async def test_concurrent_evaluate_of_same_material_computes_once():
    ev = SlowEvaluator(target=5)
    results = await asyncio.gather(*(ev.evaluate(IntMaterial(3)) for _ in range(5)))
    assert ev.compute_calls == 1
    assert all(r == {"distance": 2} for r in results)
    assert ev.get_cached_result("3") == {"distance": 2}
    assert not ev.__dict__["_inflight"]  # cleaned up


@pytest.mark.asyncio
async def test_concurrent_evaluate_of_different_materials_overlaps():
    ev = SlowEvaluator(target=5)
    await asyncio.gather(*(ev.evaluate(IntMaterial(v)) for v in range(6)))
    assert ev.compute_calls == 6
    assert ev.max_active >= 2


# --- rollout walks evaluated concurrently --------------------------------


@pytest.mark.asyncio
async def test_rollout_walks_evaluate_concurrently():
    ev = SlowEvaluator(target=5)
    mcts = make_mcts(ev, n_rollout=4, rollout_depth=2)
    await mcts.run(iterations=3)
    assert ev.max_active >= 2


@pytest.mark.asyncio
async def test_parallel_rollouts_keep_rng_sequence_and_results_reproducible():
    runs = []
    for _ in range(2):
        mcts = make_mcts(DistanceEvaluator(target=5), n_rollout=3, rollout_depth=3, seed=11)
        await mcts.run(iterations=40)
        runs.append((mcts.reward_history, mcts.unique_materials_history, mcts.best_reward))
    assert runs[0] == runs[1]


@pytest.mark.asyncio
async def test_rollout_sample_matches_walk_max():
    # On a one-dimensional line the walk's best step is its closest point to
    # the target; _rollout_sample must return exactly that.
    mcts = make_mcts(DistanceEvaluator(target=5), n_rollout=1, rollout_depth=4, seed=3)
    import random

    for _ in range(10):
        mcts._rng = random.Random(_)
        walk = mcts._sample_walk(IntMaterial(0))
        mcts._rng = random.Random(_)
        value = await mcts._rollout_sample(IntMaterial(0))
        assert value == max(-abs(m.value - 5) for m in walk)


# --- parallel_steps ------------------------------------------------------


def test_parallel_steps_validation():
    with pytest.raises(ValueError):
        make_mcts(DistanceEvaluator(target=5), parallel_steps=0)


@pytest.mark.asyncio
async def test_parallel_steps_runs_full_budget_and_finds_target():
    ev = SlowEvaluator(target=5, delay=0.002)
    mcts = make_mcts(ev, parallel_steps=4, n_rollout=2, rollout_depth=2, search_mode="thorough")
    await mcts.run(iterations=30)
    assert len(mcts.reward_history) == 30
    assert len(mcts.unique_materials_history) == 30
    assert mcts.best_reward == 0  # reached the target
    assert ev.max_active >= 2
    # no material attached twice
    ids = [n.material.get_identifier() for n in mcts.all_nodes()]
    assert len(ids) == len(set(ids)) == len(mcts.visited_materials)


@pytest.mark.asyncio
async def test_parallel_steps_round_is_truncated_to_budget():
    mcts = make_mcts(DistanceEvaluator(target=5), parallel_steps=8)
    await mcts.run(iterations=5)
    assert len(mcts.reward_history) == 5
