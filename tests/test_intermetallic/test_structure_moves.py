"""
Tests for IntermetallicStructure identity and PeriodicTableMoves expansion.

Requires ASE and spglib; skipped automatically if unavailable.

© 2025. Triad National Security, LLC. All rights reserved.
"""

import numpy as np
import pytest

# Skip the whole module if optional deps are missing. importorskip must run
# before the ase/spglib imports below, which necessitates the E402 noqa.
ase = pytest.importorskip("ase")
pytest.importorskip("spglib")

from ase import Atoms  # noqa: E402
from ase.build import bulk  # noqa: E402

from mcts_framework.intermetallic import (  # noqa: E402
    IntermetallicStructure,
    PeriodicTableMoves,
)


# --- Identity ------------------------------------------------------------


def test_formula_matches_ase():
    atoms = bulk("Cu", "fcc", a=3.6)
    s = IntermetallicStructure(atoms)
    assert s.get_formula() == atoms.get_chemical_formula()


def test_identifier_has_spacegroup_and_wyckoff():
    atoms = bulk("Cu", "fcc", a=3.6)
    s = IntermetallicStructure(atoms)
    ident = s.get_identifier()
    # Format: '<formula>|SG<num>|<decoration>'
    parts = ident.split("|")
    assert len(parts) == 3
    assert parts[0] == "Cu"
    assert parts[1] == "SG225"  # fcc Cu is Fm-3m (225)


def test_identifier_order_independent():
    """Same structure, atoms listed in different order -> same identifier."""
    pos = [[0, 0, 0], [1.8, 1.8, 0], [1.8, 0, 1.8], [0, 1.8, 1.8]]
    cell = [[3.6, 0, 0], [0, 3.6, 0], [0, 0, 3.6]]

    a = Atoms("Cu4", positions=pos, cell=cell, pbc=True)
    b = Atoms("Cu4", positions=list(reversed(pos)), cell=cell, pbc=True)

    id_a = IntermetallicStructure(a).get_identifier()
    id_b = IntermetallicStructure(b).get_identifier()
    assert id_a == id_b


def test_different_composition_different_identifier():
    a = bulk("Cu", "fcc", a=3.6)
    b = bulk("Al", "fcc", a=3.6)
    id_a = IntermetallicStructure(a).get_identifier()
    id_b = IntermetallicStructure(b).get_identifier()
    assert id_a != id_b


def test_copy_is_independent():
    atoms = bulk("Cu", "fcc", a=3.6)
    s = IntermetallicStructure(atoms)
    s2 = s.copy()
    s2.atoms.set_atomic_numbers([13] * len(s2.atoms))  # mutate copy -> Al
    assert s.get_formula() != s2.get_formula()


# --- Moves ---------------------------------------------------------------


def _ternary_template():
    """A simple cubic ternary with one metal (W=74), one Group IV (Si=14),
    and one f-block (U=92) site on a 6 A cubic cell."""
    cell = [[6.0, 0, 0], [0, 6.0, 0], [0, 0, 6.0]]
    return Atoms(
        numbers=[74, 14, 92],
        scaled_positions=[[0, 0, 0], [0.5, 0.5, 0.5], [0.25, 0.25, 0.25]],
        cell=cell,
        pbc=True,
    )


def test_moves_u_only_freezes_f_block():
    atoms = _ternary_template()
    gen = PeriodicTableMoves(f_block_mode="u_only")
    children = gen.generate_moves(IntermetallicStructure(atoms))

    # All children must still contain U (92) - f-block frozen.
    for child in children:
        assert 92 in set(child.atoms.get_atomic_numbers())


def test_moves_produce_expected_count():
    """Children == |metal_moves| * |group_iv_moves| * |f_block_moves|."""
    from mcts_framework.intermetallic import elements

    atoms = _ternary_template()
    gen = PeriodicTableMoves(f_block_mode="lanthanides_u")
    children = gen.generate_moves(IntermetallicStructure(atoms))

    n_metal = len(elements.metal_moves(74))
    n_giv = len(elements.group_iv_moves(14))
    n_f = len(elements.f_block_moves(92, "lanthanides_u"))
    assert len(children) == n_metal * n_giv * n_f


def test_moves_preserve_geometry():
    """Children keep the same atom count and positions as the parent."""
    atoms = _ternary_template()
    gen = PeriodicTableMoves(f_block_mode="u_only")
    children = gen.generate_moves(IntermetallicStructure(atoms))

    for child in children:
        assert len(child.atoms) == len(atoms)
        assert np.allclose(child.atoms.get_positions(), atoms.get_positions())


def test_moves_include_self_transition():
    """Move sets include the identity element, so the parent composition is
    reachable; the MCTS layer handles dedup/backtrack filtering."""
    atoms = _ternary_template()
    gen = PeriodicTableMoves(f_block_mode="u_only")
    children = gen.generate_moves(IntermetallicStructure(atoms))
    formulas = {c.get_formula() for c in children}
    assert atoms.get_chemical_formula() in formulas


def test_move_tokens_are_the_three_site_occupants():
    from ase.io import read
    from pathlib import Path
    cif = Path(__file__).resolve().parents[2] / "examples" / "mat_Pb6U1W6_sg191.cif"
    s = IntermetallicStructure(read(str(cif)))
    assert PeriodicTableMoves().move_tokens(s) == [("metal", 74), ("group_iv", 82), ("f_block", 92)]


def test_random_material_draws_from_the_reachable_design_space():
    import random
    from ase.io import read
    from pathlib import Path
    from mcts_framework.intermetallic import elements
    cif = Path(__file__).resolve().parents[2] / "examples" / "mat_Pb6U1W6_sg191.cif"
    root = IntermetallicStructure(read(str(cif)))
    rng = random.Random(0)
    for mode, f_set in (("u_only", {92}), ("lanthanides_u", set(range(58, 72)) | {92})):
        mg = PeriodicTableMoves(mode, 1, "wide")
        seen = set()
        for _ in range(60):
            m = mg.random_material(root, rng)
            toks = dict(mg.move_tokens(m))
            assert toks["f_block"] in f_set and toks["group_iv"] in elements.GROUP_IV_CHAIN
            assert toks["metal"] in set(elements.TM_3D) | set(elements.TM_4D) | set(elements.TM_5D)
            assert len(m.atoms) == len(root.atoms)
            seen.add(m.get_identifier())
        assert len(seen) > 30   # draws vary


def test_descriptors_and_all_materials():
    from ase.io import read
    from pathlib import Path
    cif = Path(__file__).resolve().parents[2] / "examples" / "mat_Pb6U1W6_sg191.cif"
    root = IntermetallicStructure(read(str(cif)))
    mg = PeriodicTableMoves("lanthanides_u", 1, "wide")
    d = mg.descriptors(root)
    assert d.shape == (15,) and d[0] == 74 and d[5] == 82 and d[10] == 92     # W, Pb, U
    assert d[1] == 6 and d[2] == 6 and d[6] == 6 and d[7] == 14 and d[11] == 7 and d[12] == 3
    space = mg.all_materials(root)
    assert len(space) == 27 * 4 * 15 and len({s.get_identifier() for s in space}) == 27 * 4 * 15
    assert len(PeriodicTableMoves("u_only").all_materials(root)) == 108
