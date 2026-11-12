"""Configurable stability threshold and the GGA/GGA+U-only convex hull."""
import math

import pytest

from mcts_framework.intermetallic.rewards import create_intermetallic_reward, ehull_reward


def test_default_threshold_matches_paper():
    assert ehull_reward(0.07) == pytest.approx(0.0)
    r = create_intermetallic_reward("ehull")
    assert r.compute_reward({"e_above_hull": 0.07}) == pytest.approx(0.0)


@pytest.mark.parametrize("method", ["ehull", "ehull_rdos_product_exponential"])
def test_threshold_moves_the_switch(method):
    lookup = type("L", (), {"get_reward": staticmethod(lambda f: 1.0)})()
    r = create_intermetallic_reward(method, doscar_lookup=lookup, e_thres=0.07)
    v = r.compute_reward({"e_above_hull": 0.07, "formula": "UCr6Ge6", "rdos": 1.0})
    assert v == pytest.approx(0.0 if method == "ehull" else 1.0)
    # 0.06 eV/atom is now on the stable side
    assert r.compute_reward({"e_above_hull": 0.06, "formula": "x", "rdos": 1.0}) > (0.5 if method == "ehull" else 2.0)


def test_config_field_default():
    from mcts_framework.core.config import IntermetallicConfig
    fields = IntermetallicConfig.model_fields
    assert fields["ehull_threshold"].default == 0.07


def test_select_gga_entries_skips_r2scan_and_mixed_documents():
    pytest.importorskip("pymatgen")
    from pymatgen.entries.computed_entries import ComputedEntry
    from mcts_framework.intermetallic.evaluator import select_gga_entries

    gga = ComputedEntry("Fe", -8.47, entry_id="mp-13-GGA").as_dict()
    r2 = ComputedEntry("Fe", -30.0, entry_id="mp-13-r2SCAN").as_dict()
    docs = [
        {"thermo_type": "GGA_GGA+U", "entries": {"GGA": gga}},
        {"thermo_type": "GGA_GGA+U", "entries": {"GGA": gga}},          # same entry from another chemsys
        {"thermo_type": "GGA_GGA+U_R2SCAN", "entries": {"r2SCAN": r2}},
        {"thermo_type": "R2SCAN", "entries": {"r2SCAN": r2}},
    ]
    out = select_gga_entries(docs)
    assert len(out) == 1
    assert math.isclose(out[0].energy_per_atom, -8.47)


def test_corrected_entries_are_kept():
    """Entries serialized with energy adjustments under the old module path decode."""
    pytest.importorskip("pymatgen")
    from pymatgen.entries.computed_entries import CompositionEnergyAdjustment, ComputedEntry
    from mcts_framework.intermetallic.evaluator import select_gga_entries

    e = ComputedEntry("TiSi2", -21.0, entry_id="mp-x",
                      energy_adjustments=[CompositionEnergyAdjustment(0.071, 2, name="MP2020 anion correction (Si)")]).as_dict()
    def old_path(d):
        if isinstance(d, dict):
            d = {k: old_path(v) for k, v in d.items()}
            if "@module" in d:
                d["@module"] = "pymatgen.core.entries"
            return d
        return [old_path(v) for v in d] if isinstance(d, list) else d
    out = select_gga_entries([{"thermo_type": "GGA_GGA+U", "entries": {"GGA": old_path(e)}}])
    assert len(out) == 1 and math.isclose(out[0].energy, -21.0 + 0.142)


def test_mp2020_correction_for_silicide():
    pytest.importorskip("pymatgen")
    from mcts_framework.intermetallic.evaluator import mp2020_correction_per_atom
    assert mp2020_correction_per_atom("DyFe6Si6", -7.5) > 0
    assert mp2020_correction_per_atom("DyFe6Sn6", -6.5) == 0
