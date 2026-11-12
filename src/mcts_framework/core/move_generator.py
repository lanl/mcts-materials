"""
Abstract base class for generating child materials.

© 2025. Triad National Security, LLC. All rights reserved.
"""

import random
from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Hashable, List, Optional

import numpy as np

from .material import Material

M = TypeVar('M', bound=Material)


class MoveGenerator(ABC, Generic[M]):
    """
    Abstract base class for generating child materials.

    Given a parent material, generates a list of "neighboring" materials
    that can be reached in one step (e.g., element substitution, functional
    group addition, composition change).

    Type Parameters:
        M: Material type (IntermetallicStructure, MolecularStructure, etc.)

    Examples:
        - Crystals: PeriodicTableMoves - substitute one element (Ti→V, Si→Ge)
        - Molecules: FunctionalGroupMoves - add one functional group
        - Alloys: CompositionMoves - change composition by ±5%
    """

    @abstractmethod
    def generate_moves(self, material: M) -> List[M]:
        """
        Generate all possible single-step moves from the given material.

        Args:
            material: Parent material

        Returns:
            List of child materials. May include duplicates (will be
            deduplicated by MCTS using material.get_identifier()).

        Notes:
            - This method should be deterministic for reproducibility
            - Invalid materials can be filtered via filter_invalid()
            - Empty list indicates no moves possible (dead end)
        """
        pass

    def move_tokens(self, material: M) -> List[Hashable]:
        """
        Optional: the hashable features a material shares with its neighbors.

        The search uses these to estimate the reward of a candidate it has not
        evaluated from the rewards of evaluated materials that share a token
        (see MCTS expansion_prior). For a crystal with three substitution
        sites the natural tokens are the three (site, element) pairs, so a
        candidate's estimate is the mean reward of everything evaluated with
        the same metal, the same Group IV element and the same f element.

        The default returns no tokens, in which case the search has no
        estimate for unevaluated candidates and expands them in the order
        generate_moves() returns them.
        """
        return []

    def random_material(self, material: M, rng: random.Random) -> Optional[M]:
        """
        Optional: a material drawn uniformly from the design space.

        Used by the MCTS warm start, which evaluates a few random materials
        before the tree search so that the reward estimates behind
        expansion_prior / rollout_policy start from a sample of the whole
        space rather than from the neighborhood of the root. `material` is
        the root, which fixes everything a draw must keep (the structure
        prototype, the sites); `rng` is the search's random generator.

        The default returns None: the design space cannot be sampled and the
        warm start is skipped.
        """
        return None

    def descriptors(self, material: M) -> Optional[np.ndarray]:
        """
        Optional: a fixed-length numeric descriptor vector of a material.

        Used by the MCTS model prior (expansion_prior='model'), which fits a
        Gaussian process of the reward over these descriptors. The default
        returns None: no descriptors, and the model prior cannot be used.
        """
        return None

    def all_materials(self, material: M) -> Optional[List[M]]:
        """
        Optional: every material of the design space, for global proposals.

        `material` is the root, which fixes the structure prototype. The
        default returns None: the space cannot be enumerated and the
        global-proposal option of MCTS is skipped.
        """
        return None

    def filter_invalid(self, materials: List[M]) -> List[M]:
        """
        Optional: filter out invalid materials.

        Override this method to apply chemical/physical constraints.
        Default implementation returns all materials unchanged.

        Args:
            materials: List of candidate materials

        Returns:
            Filtered list of valid materials

        Examples:
            - Remove unstable structures
            - Remove chemically impossible combinations
            - Remove materials violating constraints
        """
        return materials
