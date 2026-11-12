"""
Periodic-table element groups and move rules for intermetallic search.

All logic here is ported verbatim (in behavior) from the validated
mcts_crystal implementation so that results reproduce exactly. The functions
are pure - they take atomic numbers and return lists of atomic numbers - so
they are easy to unit-test independently of ASE.

Element groups
--------------
    Group IV chain : Si(14) - Ge(32) - Sn(50) - Pb(82)
    3d metals      : Ti(22) - Zn(30)
    4d metals      : Zr(40) - Cd(48)
    5d metals      : Hf(72) - Hg(80)
    f-block        : lanthanides La(57)-Lu(71) + actinides Ac(89)-Pu(94)

© 2025. Triad National Security, LLC. All rights reserved.
"""

from typing import List, Optional

# --- Element group definitions -------------------------------------------

GROUP_IV_CHAIN: List[int] = [14, 32, 50, 82]  # Si, Ge, Sn, Pb (chain order)

# f-block atomic numbers that participate in substitution (lanthanides +
# allowed actinides). Used by substitute() to recognize the f-block site.
F_BLOCK_ELEMENTS: List[int] = list(range(57, 72)) + list(range(89, 95))

# Transition-metal ranges by row.
TM_3D = range(22, 31)  # Ti..Zn
TM_4D = range(40, 49)  # Zr..Cd
TM_5D = range(72, 81)  # Hf..Hg


# Pauling electronegativity of the elements of the design space (pymatgen's
# values; 1.2 where pymatgen has none: Eu, Yb). Used only for the descriptors
# of the MCTS model prior.
PAULING_EN = {
    22: 1.54, 23: 1.63, 24: 1.66, 25: 1.55, 26: 1.83, 27: 1.88, 28: 1.91, 29: 1.90, 30: 1.65,
    40: 1.33, 41: 1.60, 42: 2.16, 43: 1.90, 44: 2.20, 45: 2.28, 46: 2.20, 47: 1.93, 48: 1.69,
    72: 1.30, 73: 1.50, 74: 2.36, 75: 1.90, 76: 2.20, 77: 2.20, 78: 2.28, 79: 2.54, 80: 2.00,
    14: 1.90, 32: 2.01, 50: 1.96, 82: 2.33,
    57: 1.10, 58: 1.12, 59: 1.13, 60: 1.14, 61: 1.13, 62: 1.17, 63: 1.20, 64: 1.20, 65: 1.10,
    66: 1.22, 67: 1.23, 68: 1.24, 69: 1.25, 70: 1.20, 71: 1.27,
    89: 1.10, 90: 1.30, 91: 1.50, 92: 1.38, 93: 1.36, 94: 1.28,
}


def period_group(atomic_num: int):
    """(period, group) of an element of the design space; lanthanides and actinides take group 3."""
    z = atomic_num
    if z in TM_3D: return 4, z - 18
    if z in TM_4D: return 5, z - 36
    if z in TM_5D: return 6, z - 68
    if z in GROUP_IV_CHAIN: return {14: 3, 32: 4, 50: 5, 82: 6}[z], 14
    if 57 <= z <= 71: return 6, 3
    if 89 <= z <= 94: return 7, 3
    raise ValueError(f"element {z} is not in the design space")


def element_descriptors(atomic_num: int):
    """[Z, period, group, Pauling electronegativity, covalent radius (A)] of an element."""
    from ase.data import covalent_radii
    p, g = period_group(atomic_num)
    return [float(atomic_num), float(p), float(g), PAULING_EN[atomic_num], float(covalent_radii[atomic_num])]


# --- Move-rule functions --------------------------------------------------


def group_iv_moves(atomic_num: int, move_step: int = 1) -> List[int]:
    """
    Group IV moves: current element plus chain neighbors within move_step.

    No wrap-around (Si and Pb are chain ends). At move_step=1 this is just the
    immediate neighbors (e.g. Ge -> {Si, Ge, Sn}); larger move_step reaches
    farther along the Si-Ge-Sn-Pb chain. Returns a sorted list.
    """
    if atomic_num not in GROUP_IV_CHAIN:
        return [atomic_num]
    idx = GROUP_IV_CHAIN.index(atomic_num)
    moves = {atomic_num}
    for delta in range(1, move_step + 1):
        if idx - delta >= 0:
            moves.add(GROUP_IV_CHAIN[idx - delta])
        if idx + delta < len(GROUP_IV_CHAIN):
            moves.add(GROUP_IV_CHAIN[idx + delta])
    return sorted(moves)


def metal_moves(atomic_num: int, move_step: int = 1) -> List[int]:
    """
    Transition-metal moves: within-row steps up to move_step, plus fixed
    single-period cross-row jumps.

    Within a d-row (3d 22-30, 4d 40-48, 5d 72-80) the element may move +/-1..
    move_step positions (clamped to the row). Cross-period jumps to the
    adjacent d-row(s) are always a single period step (+/-18 between 3d/4d,
    +/-32 between 4d/5d), independent of move_step. At move_step=1 this
    reproduces the original hand-tuned edge cases exactly (e.g. Ti->[22,23,40],
    Cd->[30,47,48,80]). Returns a sorted, de-duplicated list.
    """
    mv = {atomic_num}
    if 22 <= atomic_num <= 30:  # 3d
        for s in range(1, move_step + 1):
            if atomic_num - s >= 22:
                mv.add(atomic_num - s)
            if atomic_num + s <= 30:
                mv.add(atomic_num + s)
        mv.add(atomic_num + 18)  # cross-period up to 4d
    elif 40 <= atomic_num <= 48:  # 4d
        for s in range(1, move_step + 1):
            if atomic_num - s >= 40:
                mv.add(atomic_num - s)
            if atomic_num + s <= 48:
                mv.add(atomic_num + s)
        mv.add(atomic_num - 18)  # cross-period down to 3d
        if atomic_num + 32 <= 80:
            mv.add(atomic_num + 32)  # cross-period up to 5d
    elif 72 <= atomic_num <= 80:  # 5d
        for s in range(1, move_step + 1):
            if atomic_num - s >= 72:
                mv.add(atomic_num - s)
            if atomic_num + s <= 80:
                mv.add(atomic_num + s)
        mv.add(atomic_num - 32)  # cross-period down to 4d
    else:
        # Not a recognized transition metal - no move.
        return [atomic_num]
    return sorted(mv)


# U(92) bridge widths: which lanthanides U connects to (and which connect back
# to U). 'narrow' = Nd only; 'wide' = Nd/Gd/Er (light/mid/heavy). This is
# orthogonal to move_step (jump distance) and to wrap-around (mode).
_U_BRIDGE_LANTHANIDES = {
    "narrow": (60,),        # Nd
    "wide": (60, 64, 68),   # Nd, Gd, Er
}


def f_block_moves(
    atomic_num: int,
    mode: str,
    move_step: int = 1,
    u_bridge: str = "narrow",
) -> List[int]:
    """
    F-block moves under the given mode.

    Modes (canonical names; see core.config for the alias handling):
        u_only                 : [92] only.
        lanthanides_u          : +/-move_step with wrap-around (Ce<->Lu); U bridge.
        lanthanides_u_no_wrap  : +/-move_step, no wrap; U bridge.
        full_f_block           : Ce-Lu + Th-Pu, +/-1 plus vertical Ln<->An.

    Two orthogonal knobs control the lanthanide/U modes:
      - move_step: lanthanide jump range (default 1 = adjacent; larger = farther).
      - u_bridge : which lanthanides U(92) connects to - 'narrow' (Nd only) or
        'wide' (Nd/Gd/Er). Independent of jump distance and wrap-around.
    full_f_block ignores both (its +/-1 neighbor + vertical analog structure is
    fixed and has no U bridge).

    Returns a sorted, de-duplicated list of atomic numbers.
    """
    lanthanides = list(range(58, 72))  # Ce(58)..Lu(71)
    bridge = _U_BRIDGE_LANTHANIDES.get(u_bridge, _U_BRIDGE_LANTHANIDES["narrow"])

    def _add_u_bridge(possible: List[int]) -> None:
        """Connect U(92) to its bridge lanthanides, and those back to U."""
        if atomic_num == 92:
            possible.extend(bridge)
        elif atomic_num in bridge:
            possible.append(92)

    if mode == "u_only":
        possible = [92]

    elif mode == "lanthanides_u":
        possible = [atomic_num]
        if atomic_num in lanthanides:
            idx = lanthanides.index(atomic_num)
            for delta in range(-move_step, move_step + 1):
                if delta != 0:
                    possible.append(lanthanides[(idx + delta) % len(lanthanides)])
        _add_u_bridge(possible)

    elif mode == "lanthanides_u_no_wrap":
        # +/-move_step neighbors, NO wrap-around (Ce/Lu are chain ends).
        possible = [atomic_num]
        if atomic_num in lanthanides:
            idx = lanthanides.index(atomic_num)
            for delta in range(1, move_step + 1):
                if idx - delta >= 0:
                    possible.append(lanthanides[idx - delta])
                if idx + delta < len(lanthanides):
                    possible.append(lanthanides[idx + delta])
        _add_u_bridge(possible)

    else:  # full_f_block
        actinides = list(range(90, 95))  # Th(90)..Pu(94)
        all_f = lanthanides + actinides
        possible = [atomic_num]
        for delta in (-1, 1):
            neighbor = atomic_num + delta
            if neighbor in all_f:
                possible.append(neighbor)
        # Vertical Ln <-> An analog moves (+/-32).
        if 58 <= atomic_num <= 62:  # Ce..Sm -> Th..Pu
            analog = atomic_num + 32
            if analog in all_f:
                possible.append(analog)
        if 90 <= atomic_num <= 94:  # Th..Pu -> Ce..Sm
            analog = atomic_num - 32
            if analog in all_f:
                possible.append(analog)

    return sorted(set(possible))


def classify_site(atomic_num: int) -> Optional[str]:
    """
    Classify an atomic number into its substitution site type.

    Returns one of 'group_iv', 'metal', 'f_block', or None if the element is
    not part of any recognized substitution group.
    """
    if atomic_num in GROUP_IV_CHAIN:
        return "group_iv"
    if atomic_num in F_BLOCK_ELEMENTS:
        return "f_block"
    if 22 <= atomic_num <= 30 or 40 <= atomic_num <= 48 or 72 <= atomic_num <= 80:
        return "metal"
    return None


def validate_fblock_compat(atomic_numbers, f_block_mode: str) -> List[str]:
    """
    Check that a starting structure's f-block element(s) are compatible with
    f_block_mode, and return a list of non-fatal warning messages.

    Pure function over an iterable of atomic numbers (extracted from the loaded
    structure by the caller) - no file I/O, so config validation stays cheap and
    the check is unit-testable without ASE. Raises ValueError on a hard
    incompatibility (e.g. u_only without U); returns warning strings for the
    caller to emit (e.g. u_only with extra f-block elements, or no f-block at
    all). U is atomic number 92; lanthanides are La(57)-Lu(71).
    """
    f_block = {int(z) for z in atomic_numbers if int(z) in F_BLOCK_ELEMENTS}
    warnings_out: List[str] = []

    if not f_block:
        warnings_out.append(
            "No f-block elements found in the starting structure. The search "
            "will not explore f-block substitutions."
        )
        return warnings_out

    if f_block_mode == "u_only":
        if 92 not in f_block:
            raise ValueError(
                f"f_block_mode='u_only' requires U (atomic number 92) in the "
                f"starting structure, but found f-block elements: {sorted(f_block)}"
            )
        if len(f_block) > 1:
            warnings_out.append(
                f"f_block_mode='u_only' found multiple f-block elements "
                f"{sorted(f_block)} in the starting structure. Only U (92) will "
                f"participate in moves."
            )
    elif f_block_mode in ("lanthanides_u", "lanthanides_u_no_wrap"):
        valid = set(range(57, 72)) | {92}  # La-Lu + U
        invalid = f_block - valid
        if invalid:
            raise ValueError(
                f"f_block_mode='{f_block_mode}' requires lanthanides (La-Lu, "
                f"57-71) or U (92), but found: {sorted(invalid)}"
            )
    # full_f_block: every f-block element is valid; no check needed.

    return warnings_out
