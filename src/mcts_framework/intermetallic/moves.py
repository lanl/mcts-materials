"""
Periodic-table move generator for intermetallic structures.

Generates child structures by substituting elements on the transition-metal,
Group IV, and f-block sites of the parent, using the validated move rules in
``elements.py``. Behavior mirrors mcts_crystal's expand(): the full set of
children is the Cartesian product of the allowed metal, Group IV, and f-block
moves.

© 2025. Triad National Security, LLC. All rights reserved.
"""

import itertools
import random
from typing import Hashable, List, Optional, TYPE_CHECKING

import numpy as np

from ..core.move_generator import MoveGenerator
from .structure import IntermetallicStructure
from . import elements

if TYPE_CHECKING:
    from ase import Atoms


class PeriodicTableMoves(MoveGenerator[IntermetallicStructure]):
    """
    Element-substitution move generator.

    For the parent structure, determines the current metal / Group IV /
    f-block occupant(s) and the allowed moves for each, then emits one child
    per (metal, group_iv, f_block) combination. The f-block axis is omitted
    when the structure has no f-block site.
    """

    def __init__(
        self,
        f_block_mode: str = "u_only",
        move_step: int = 1,
        u_bridge: str = "narrow",
    ):
        """
        Args:
            f_block_mode: One of the canonical f-block modes understood by
                elements.f_block_moves (u_only, lanthanides_u,
                lanthanides_u_no_wrap, full_f_block).
            move_step: Max positions a single substitution may jump along the
                transition-metal / Group IV / lanthanide axes (default 1 =
                adjacent only; e.g. 3 gives extended-range exploration). Fixed
                cross-period metal jumps and full_f_block are unaffected.
            u_bridge: which lanthanides U(92) connects to - 'narrow' (Nd only,
                default) or 'wide' (Nd/Gd/Er). Only affects the lanthanide/U
                modes; orthogonal to move_step.
        """
        self.f_block_mode = f_block_mode
        self.move_step = move_step
        self.u_bridge = u_bridge

    def generate_moves(
        self, material: IntermetallicStructure
    ) -> List[IntermetallicStructure]:
        atoms = material.atoms
        present = set(atoms.get_atomic_numbers())

        # Determine the allowed moves on each site axis from the current
        # occupants. Absent axes contribute a single "no-op" so the product
        # still works.
        metal_axis: List[int] = [0]
        giv_axis: List[int] = [0]
        fblock_axis: List[Optional[int]] = [None]

        for z in present:
            site = elements.classify_site(int(z))
            if site == "metal":
                metal_axis = elements.metal_moves(int(z), self.move_step)
            elif site == "group_iv":
                giv_axis = elements.group_iv_moves(int(z), self.move_step)
            elif site == "f_block":
                fblock_axis = list(
                    elements.f_block_moves(
                        int(z), self.f_block_mode, self.move_step, self.u_bridge
                    )
                )

        children: List[IntermetallicStructure] = []
        for metal in metal_axis:
            for giv in giv_axis:
                for fblock in fblock_axis:
                    new_atoms = self._substitute(atoms, metal, giv, fblock)
                    children.append(
                        IntermetallicStructure(new_atoms, symprec=material.symprec)
                    )
        return children

    def design_space_elements(self) -> dict:
        """The elements the move rules can reach on each site, by site name."""
        lanthanides = list(range(58, 72))  # Ce..Lu
        if self.f_block_mode == "u_only":
            f_block = [92]
        elif self.f_block_mode == "full_f_block":
            f_block = lanthanides + list(range(90, 95))  # + Th..Pu
        else:  # lanthanides_u, lanthanides_u_no_wrap: Ce-Lu and U (La is not connected)
            f_block = lanthanides + [92]
        return {
            "metal": list(elements.TM_3D) + list(elements.TM_4D) + list(elements.TM_5D),
            "group_iv": list(elements.GROUP_IV_CHAIN),
            "f_block": f_block,
        }

    def random_material(
        self, material: IntermetallicStructure, rng: random.Random
    ) -> Optional[IntermetallicStructure]:
        """A structure with each site occupied by a uniformly drawn allowed element."""
        space = self.design_space_elements()
        present = {elements.classify_site(int(z)) for z in set(material.atoms.get_atomic_numbers())}
        metal = rng.choice(space["metal"]) if "metal" in present else 0
        giv = rng.choice(space["group_iv"]) if "group_iv" in present else 0
        fblock = rng.choice(space["f_block"]) if "f_block" in present else None
        new_atoms = self._substitute(material.atoms, metal, giv, fblock)
        return IntermetallicStructure(new_atoms, symprec=material.symprec)

    def descriptors(self, material: IntermetallicStructure) -> Optional[np.ndarray]:
        """15 descriptors: [Z, period, group, electronegativity, covalent radius] of the
        metal, the Group IV element and the f element, in that order (raw, not standardized)."""
        occ = {}
        for z in set(material.atoms.get_atomic_numbers()):
            site = elements.classify_site(int(z))
            if site is not None:
                occ[site] = int(z)
        out = []
        for site in ("metal", "group_iv", "f_block"):
            if site in occ:
                out += elements.element_descriptors(occ[site])
        return np.array(out, float)

    def all_materials(self, material: IntermetallicStructure) -> List[IntermetallicStructure]:
        """Every structure of the design space reachable by the move rules: the product of the
        allowed elements on the sites the root occupies (e.g. 27 x 4 x 15 = 1,620 for lanthanides_u)."""
        space = self.design_space_elements()
        present = {elements.classify_site(int(z)) for z in set(material.atoms.get_atomic_numbers())}
        metals = space["metal"] if "metal" in present else [0]
        givs = space["group_iv"] if "group_iv" in present else [0]
        fbs = space["f_block"] if "f_block" in present else [None]
        out = []
        for m, g, f in itertools.product(metals, givs, fbs):
            out.append(IntermetallicStructure(self._substitute(material.atoms, m, g, f), symprec=material.symprec))
        return out

    def move_tokens(self, material: IntermetallicStructure) -> List[Hashable]:
        """The (site, element) pairs occupying the metal, Group IV and f-block sites."""
        tokens: List[Hashable] = []
        for z in sorted(set(material.atoms.get_atomic_numbers())):
            site = elements.classify_site(int(z))
            if site is not None:
                tokens.append((site, int(z)))
        return tokens

    @staticmethod
    def _substitute(
        atoms: "Atoms",
        metal: int,
        g_iv: int,
        f_block: Optional[int],
    ) -> "Atoms":
        """
        Return a copy of ``atoms`` with sites substituted.

        Each atom is remapped by site type:
            f-block site -> f_block (if provided)
            Group IV site -> g_iv
            everything else (metal) -> metal

        A target of 0 (the no-op sentinel) leaves that atom unchanged. Ported
        from mcts_crystal.node.substitute().
        """
        op = []
        for z in atoms.get_atomic_numbers():
            z = int(z)
            if z in elements.F_BLOCK_ELEMENTS and f_block is not None:
                op.append(f_block - z)
            elif z in elements.GROUP_IV_CHAIN:
                op.append((g_iv - z) if g_iv else 0)
            else:
                op.append((metal - z) if metal else 0)

        new_atoms = atoms.copy()
        new_atoms.set_atomic_numbers(new_atoms.get_atomic_numbers() + op)
        return new_atoms
