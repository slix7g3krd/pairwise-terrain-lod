import pytest
from render import terrain_lod as mod

CASES = [
    ("conservative_max", "m.conservative_height([1.0, 3.0, 2.0]) == approx(3.0)"),
    ("conservative_single", "m.conservative_height([2.5]) == approx(2.5)"),
    ("stitch_lower", "m.stitch_edge(5.0, 3.0, 1.0) == approx(2.0)"),
    ("stitch_no_step", "m.stitch_edge(5.0, 3.0, 0.0) == approx(3.0)"),
    ("splat_sum", "sum(m.splat_weights([1.0, 3.0])) == approx(1.0)"),
    ("splat_zero", "m.splat_weights([0.0, 0.0]) == [0.5, 0.5]"),
    ("normal_flat", "m.normal_from_slope(0.0, 0.0) == approx((0.0, 1.0, 0.0))"),
    ("normal_slope_x", "m.normal_from_slope(1.0, 0.0)[0] < 0.0"),
    ("cave_layer_one", "m.cave_layer_height(10.0, 1, 3.0) == approx(13.0)"),
    ("cave_layer_zero", "m.cave_layer_height(10.0, 0, 3.0) == approx(10.0)"),
    ("sync_true", "m.collision_lod_sync(2, 2) is True"),
    ("sync_false", "m.collision_lod_sync(2, 3) is False"),
    ("clamp_high", "m.clamp_layer(9, 4) == 4"),
    ("clamp_low", "m.clamp_layer(-2, 4) == 0"),
    ("displacement_ok", "m.displacement_continuous(1.0, 1.02, 0.05) is True")
]

@pytest.mark.parametrize("name,expr", CASES, ids=[c[0] for c in CASES])
def test_contract(name, expr):
    assert eval(expr, {"m": mod, "approx": pytest.approx})
