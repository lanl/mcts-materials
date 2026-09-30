"""
Reward functions for intermetallic search.

Nine formulations, matching the validated mcts_crystal rollout methods:

    EhullReward                           : -tanh(120 * (e_hull - 0.05))          ('ehull')
    EhullRdosReward                       : beta * ehull_term + gamma * r_DOS      ('ehull_rdos')
    EhullRdosProductReward                : ehull_term * r_DOS                    ('ehull_rdos_product')
    EhullRdosProductShiftedReward         : ((ehull_term + 1) / 2) * r_DOS        ('ehull_rdos_product_shifted')
    EhullRdosProductOffsetReward          : (ehull_term + 1) * r_DOS              ('ehull_rdos_product_offset')
    EhullRdosProductExponentialReward     : exp(ehull_term) * r_DOS               ('ehull_rdos_product_exponential')
    EhullRdosProductTanhShiftedReward     : (ehull_term + 1.1) * r_DOS            ('ehull_rdos_product_tanh_shifted')
    EhullRdosProductDirectExponentialReward: exp(-e_hull) * r_DOS                 ('ehull_rdos_product_direct_exponential')
    RdosReward                            : r_DOS                                  ('rdos')

The ehull sharpness (120) and stability threshold (0.05 eV/atom) are
physics-informed constants, not tunable hyperparameters. beta and gamma are
the additive composite-score weights (defaults 1.0 / 0.0001 from the published
study). The product method takes NO gamma - a single global scalar cannot
change a purely multiplicative ranking - and because ehull_term is negative
for unstable compounds, an unstable compound yields a negative product
regardless of DOS quality. The shifted product method maps ehull_term from
[-1, +1] to [0, 1] before multiplying by rDOS, ensuring non-negative rewards.
The offset product method maps ehull_term from [-1, +1] to [0, 2], preserving
the full magnitude range while ensuring non-negative rewards. The exponential
product method applies exp(ehull_term) before multiplying by rDOS, providing
smooth decay that preserves rDOS information even for unstable compounds.

Properties consumed:
    e_above_hull : from the MACE/Materials Project evaluator.
    formula      : plain composition string, used to look up r_DOS.
    rdos         : optional precomputed r_DOS; if absent, looked up from the
                   DoscarRewardLookup using 'formula'.

© 2026. Triad National Security, LLC. All rights reserved.
"""

from typing import Dict, List, Optional

import numpy as np

from ..core.reward import RewardFunction
from .doscar import DoscarRewardLookup

# Physics-informed constants (do NOT sweep).
_EHULL_SHARPNESS = 120.0
_EHULL_THRESHOLD = 0.05  # eV/atom


def ehull_reward(e_hull: float) -> float:
    """
    Sharp tanh reward for energy above hull.

    f(E_hull) = -tanh(120 * (E_hull - 0.05)); ~+1 for stable (E_hull~0),
    0 at the 0.05 eV/atom boundary, ~-1 for unstable (E_hull>=0.1).
    """
    return float(-np.tanh(_EHULL_SHARPNESS * (e_hull - _EHULL_THRESHOLD)))


def _resolve_rdos(
    properties: Dict[str, float],
    doscar_lookup: DoscarRewardLookup,
) -> float:
    """
    Resolve the rDOS value for a set of properties.

    Prefers a precomputed 'rdos' entry; otherwise looks it up from the DOSCAR
    data by 'formula'. Returns 0.0 when neither is available.
    """
    if "rdos" in properties:
        return properties["rdos"]
    formula = properties.get("formula")
    if formula is None:
        return 0.0
    return doscar_lookup.get_reward(str(formula))


class EhullReward(RewardFunction):
    """Energy-above-hull reward only ('ehull')."""

    def compute_reward(self, properties: Dict[str, float]) -> float:
        return ehull_reward(properties["e_above_hull"])

    def get_property_names(self) -> List[str]:
        return ["e_above_hull"]


class RdosReward(RewardFunction):
    """rDOS-only reward ('rdos'); no MACE/Materials Project needed."""

    def __init__(self, doscar_lookup: DoscarRewardLookup):
        self.doscar_lookup = doscar_lookup

    def compute_reward(self, properties: Dict[str, float]) -> float:
        return _resolve_rdos(properties, self.doscar_lookup)

    def get_property_names(self) -> List[str]:
        return ["formula"]


class EhullRdosReward(RewardFunction):
    """
    Composite reward ('ehull_rdos'): beta * ehull_reward + gamma * r_DOS.

    Defaults beta=1.0, gamma=0.0001 reproduce the published study.
    """

    def __init__(
        self,
        doscar_lookup: DoscarRewardLookup,
        beta: float = 1.0,
        gamma: float = 0.0001,
    ):
        self.doscar_lookup = doscar_lookup
        self.beta = beta
        self.gamma = gamma

    def compute_reward(self, properties: Dict[str, float]) -> float:
        ehull_term = ehull_reward(properties["e_above_hull"])
        rdos = _resolve_rdos(properties, self.doscar_lookup)
        return self.beta * ehull_term + self.gamma * rdos

    def get_property_names(self) -> List[str]:
        return ["e_above_hull", "formula"]


class EhullRdosProductReward(RewardFunction):
    """
    Multiplicative composite reward ('ehull_rdos_product'):

        reward = ehull_reward(e_hull) * r_DOS

    Unlike mcts_crystal's product method, this drops the gamma factor: in a
    purely multiplicative reward a single global scalar multiplies every
    compound's score equally, so it cannot change the ranking (argmax is
    gamma-invariant for gamma > 0) - it only rescales magnitudes. Removing it
    keeps the reward meaningful without a redundant knob.

    Since ehull_reward is negative for unstable compounds (e_hull above the
    0.05 eV/atom threshold), an unstable compound yields a negative product
    regardless of how favorable its rDOS is - so this method gates on
    stability more strictly than the additive ehull_rdos.
    """

    def __init__(self, doscar_lookup: DoscarRewardLookup):
        self.doscar_lookup = doscar_lookup

    def compute_reward(self, properties: Dict[str, float]) -> float:
        ehull_term = ehull_reward(properties["e_above_hull"])
        rdos = _resolve_rdos(properties, self.doscar_lookup)
        return ehull_term * rdos

    def get_property_names(self) -> List[str]:
        return ["e_above_hull", "formula"]


class EhullRdosProductShiftedReward(RewardFunction):
    """
    Shifted multiplicative composite reward ('ehull_rdos_product_shifted'):

        reward = ((ehull_reward(e_hull) + 1) / 2) * r_DOS

    This transforms the ehull_reward from [-1, +1] to [0, 1] before multiplying
    by rDOS, ensuring all rewards are non-negative. The shift operation maps:
        - Stable compounds (ehull_reward ≈ +1) → 1.0
        - Boundary compounds (ehull_reward = 0) → 0.5
        - Unstable compounds (ehull_reward ≈ -1) → 0.0

    Unlike the original product method where unstable compounds yield negative
    rewards, this formulation smoothly scales rewards from 0 (very unstable)
    to 1 (very stable) before scaling by rDOS.
    """

    def __init__(self, doscar_lookup: DoscarRewardLookup):
        self.doscar_lookup = doscar_lookup

    def compute_reward(self, properties: Dict[str, float]) -> float:
        ehull_term = ehull_reward(properties["e_above_hull"])
        rdos = _resolve_rdos(properties, self.doscar_lookup)
        # Shift ehull_term from [-1, +1] to [0, 1]
        shifted_ehull = (ehull_term + 1.0) / 2.0
        return shifted_ehull * rdos

    def get_property_names(self) -> List[str]:
        return ["e_above_hull", "formula"]


class EhullRdosProductOffsetReward(RewardFunction):
    """
    Offset multiplicative composite reward ('ehull_rdos_product_offset'):

        reward = (ehull_reward(e_hull) + 1) * r_DOS

    This transforms the ehull_reward from [-1, +1] to [0, 2] before multiplying
    by rDOS, ensuring all rewards are non-negative. The offset operation maps:
        - Stable compounds (ehull_reward ≈ +1) → 2.0
        - Boundary compounds (ehull_reward = 0) → 1.0
        - Unstable compounds (ehull_reward ≈ -1) → 0.0

    Unlike ehull_rdos_product_shifted which normalizes to [0, 1], this version
    preserves the full [-1, +1] range magnitude as [0, 2], giving stable
    compounds twice the weight of boundary compounds.
    """

    def __init__(self, doscar_lookup: DoscarRewardLookup):
        self.doscar_lookup = doscar_lookup

    def compute_reward(self, properties: Dict[str, float]) -> float:
        ehull_term = ehull_reward(properties["e_above_hull"])
        rdos = _resolve_rdos(properties, self.doscar_lookup)
        # Offset ehull_term from [-1, +1] to [0, 2]
        offset_ehull = ehull_term + 1.0
        return offset_ehull * rdos

    def get_property_names(self) -> List[str]:
        return ["e_above_hull", "formula"]


class EhullRdosProductExponentialReward(RewardFunction):
    """
    Exponential multiplicative composite reward ('ehull_rdos_product_exponential'):

        reward = exp(ehull_reward(e_hull)) * r_DOS

    This applies an exponential transformation to ehull_reward before multiplying
    by rDOS. The exponential ensures all rewards are non-negative and preserves
    rDOS information even for unstable compounds:
        - Stable compounds (ehull_reward ≈ +1) → exp(+1) ≈ 2.72
        - Boundary compounds (ehull_reward = 0) → exp(0) = 1.0
        - Unstable compounds (ehull_reward ≈ -1) → exp(-1) ≈ 0.37

    Unlike linear transformations (shifted/offset) which zero out rewards for
    unstable materials, the exponential smoothly decays but never reaches zero,
    allowing high-rDOS unstable compounds to still be distinguished from
    low-rDOS unstable compounds. Provides strong separation between stable
    and unstable while preserving DOS information across the full stability range.
    """

    def __init__(self, doscar_lookup: DoscarRewardLookup):
        self.doscar_lookup = doscar_lookup

    def compute_reward(self, properties: Dict[str, float]) -> float:
        ehull_term = ehull_reward(properties["e_above_hull"])
        rdos = _resolve_rdos(properties, self.doscar_lookup)
        # Apply exponential to ehull_term
        exp_ehull = float(np.exp(ehull_term))
        return exp_ehull * rdos

    def get_property_names(self) -> List[str]:
        return ["e_above_hull", "formula"]


class EhullRdosProductTanhShiftedReward(RewardFunction):
    """
    Tanh-shifted multiplicative composite reward ('ehull_rdos_product_tanh_shifted'):

        reward = (ehull_reward(e_hull) + 1.1) * r_DOS

    This adds 1.1 to the tanh-transformed ehull_reward before multiplying by rDOS,
    ensuring all rewards are non-negative with an offset that provides a buffer
    above zero even for the most unstable compounds:
        - Stable compounds (ehull_reward ≈ +1) → 2.1
        - Boundary compounds (ehull_reward = 0) → 1.1
        - Unstable compounds (ehull_reward ≈ -1) → 0.1

    The 1.1 shift ensures that even compounds with ehull_reward ≈ -1 still
    contribute meaningfully to the search, scaled by their rDOS values.
    """

    def __init__(self, doscar_lookup: DoscarRewardLookup):
        self.doscar_lookup = doscar_lookup

    def compute_reward(self, properties: Dict[str, float]) -> float:
        ehull_term = ehull_reward(properties["e_above_hull"])
        rdos = _resolve_rdos(properties, self.doscar_lookup)
        # Shift ehull_term by +1.1
        shifted_ehull = ehull_term + 1.1
        return shifted_ehull * rdos

    def get_property_names(self) -> List[str]:
        return ["e_above_hull", "formula"]


class EhullRdosProductDirectExponentialReward(RewardFunction):
    """
    Direct exponential multiplicative composite reward ('ehull_rdos_product_direct_exponential'):

        reward = exp(-e_hull) * r_DOS

    This applies the exponential directly to the negative of the raw e_hull value
    (energy above convex hull), without the tanh transformation:
        - Stable compounds (e_hull ≈ 0) → exp(0) = 1.0
        - Moderately unstable (e_hull = 0.1) → exp(-0.1) ≈ 0.90
        - Unstable (e_hull = 0.5) → exp(-0.5) ≈ 0.61
        - Very unstable (e_hull = 1.0) → exp(-1.0) ≈ 0.37

    Unlike the tanh-based methods which impose a sharp sigmoid boundary at 0.05 eV,
    this provides smooth exponential decay proportional to the raw stability.
    The decay is less aggressive than tanh for small e_hull values but maintains
    continuous sensitivity across the full stability range.
    """

    def __init__(self, doscar_lookup: DoscarRewardLookup):
        self.doscar_lookup = doscar_lookup

    def compute_reward(self, properties: Dict[str, float]) -> float:
        e_hull = properties["e_above_hull"]
        rdos = _resolve_rdos(properties, self.doscar_lookup)
        # Apply exponential directly to negative e_hull
        exp_ehull = float(np.exp(-e_hull))
        return exp_ehull * rdos

    def get_property_names(self) -> List[str]:
        return ["e_above_hull", "formula"]


def create_intermetallic_reward(
    rollout_method: str,
    doscar_lookup: Optional[DoscarRewardLookup] = None,
    beta: float = 1.0,
    gamma: float = 0.0001,
) -> RewardFunction:
    """
    Factory: build the reward function for a given rollout method.

    Args:
        rollout_method: One of 'ehull', 'ehull_rdos', 'ehull_rdos_product',
            'ehull_rdos_product_shifted', 'ehull_rdos_product_offset',
            'ehull_rdos_product_exponential', 'ehull_rdos_product_tanh_shifted',
            'ehull_rdos_product_direct_exponential', 'rdos'.
        doscar_lookup: Required for 'rdos', 'ehull_rdos', 'ehull_rdos_product',
            'ehull_rdos_product_shifted', 'ehull_rdos_product_offset',
            'ehull_rdos_product_exponential', 'ehull_rdos_product_tanh_shifted',
            'ehull_rdos_product_direct_exponential'.
        beta: E_hull weight for 'ehull_rdos' (unused by other methods).
        gamma: rDOS weight for 'ehull_rdos' (unused by other methods).

    Raises:
        ValueError: On unknown method or missing doscar_lookup.
    """
    if rollout_method == "ehull":
        return EhullReward()
    if rollout_method == "rdos":
        if doscar_lookup is None:
            raise ValueError("rollout_method='rdos' requires a doscar_lookup")
        return RdosReward(doscar_lookup)
    if rollout_method == "ehull_rdos":
        if doscar_lookup is None:
            raise ValueError("rollout_method='ehull_rdos' requires a doscar_lookup")
        return EhullRdosReward(doscar_lookup, beta=beta, gamma=gamma)
    if rollout_method == "ehull_rdos_product":
        if doscar_lookup is None:
            raise ValueError(
                "rollout_method='ehull_rdos_product' requires a doscar_lookup"
            )
        return EhullRdosProductReward(doscar_lookup)
    if rollout_method == "ehull_rdos_product_shifted":
        if doscar_lookup is None:
            raise ValueError(
                "rollout_method='ehull_rdos_product_shifted' requires a doscar_lookup"
            )
        return EhullRdosProductShiftedReward(doscar_lookup)
    if rollout_method == "ehull_rdos_product_offset":
        if doscar_lookup is None:
            raise ValueError(
                "rollout_method='ehull_rdos_product_offset' requires a doscar_lookup"
            )
        return EhullRdosProductOffsetReward(doscar_lookup)
    if rollout_method == "ehull_rdos_product_exponential":
        if doscar_lookup is None:
            raise ValueError(
                "rollout_method='ehull_rdos_product_exponential' requires a doscar_lookup"
            )
        return EhullRdosProductExponentialReward(doscar_lookup)
    if rollout_method == "ehull_rdos_product_tanh_shifted":
        if doscar_lookup is None:
            raise ValueError(
                "rollout_method='ehull_rdos_product_tanh_shifted' requires a doscar_lookup"
            )
        return EhullRdosProductTanhShiftedReward(doscar_lookup)
    if rollout_method == "ehull_rdos_product_direct_exponential":
        if doscar_lookup is None:
            raise ValueError(
                "rollout_method='ehull_rdos_product_direct_exponential' requires a doscar_lookup"
            )
        return EhullRdosProductDirectExponentialReward(doscar_lookup)
    raise ValueError(f"Unknown rollout_method: {rollout_method!r}")
