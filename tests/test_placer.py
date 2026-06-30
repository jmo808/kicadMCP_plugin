import pytest

from kbd_engine.models import Key, KeyMatrix
from kbd_engine.placer import GridPlacer
from kbd_engine.registry import FootprintRegistry


def test_grid_placer_basic_placement() -> None:
    # 2 keys in a row
    k0 = Key(x=0.0, y=0.0, matrix_row=0, matrix_col=0)
    k1 = Key(x=19.05, y=0.0, matrix_row=0, matrix_col=1)
    matrix = KeyMatrix(keys=[k0, k1])

    registry = FootprintRegistry()
    placer = GridPlacer(diode_offset_y=5.0, capacitor_offset_x=3.0)
    result = placer.place(matrix, registry)

    assert result.valid is True
    assert len(result.errors) == 0

    # 2 keys -> 2 switches, 2 diodes, 2 capacitors = 6 placed components
    assert len(result.placements) == 6

    # Check SW_0_0
    sw0 = result.placements["SW_0_0"]
    assert sw0["x"] == pytest.approx(0.0)
    assert sw0["y"] == pytest.approx(0.0)
    assert sw0["rotation"] == 0.0
    assert sw0["footprint"] == registry.resolve("switch")

    # Check D_0_0
    d0 = result.placements["D_0_0"]
    assert d0["x"] == pytest.approx(0.0)
    assert d0["y"] == pytest.approx(5.0)
    assert d0["rotation"] == 0.0
    assert d0["footprint"] == registry.resolve("diode")

    # Check C_0_0
    c0 = result.placements["C_0_0"]
    assert c0["x"] == pytest.approx(3.0)
    assert c0["y"] == pytest.approx(0.0)
    assert c0["rotation"] == 0.0
    assert c0["footprint"] == registry.resolve("capacitor")


def test_grid_placer_rotated_placement() -> None:
    # Key rotated 90 degrees (clockwise) at (0, 0)
    k0 = Key(x=0.0, y=0.0, rotation=90.0, matrix_row=0, matrix_col=0)
    matrix = KeyMatrix(keys=[k0])

    registry = FootprintRegistry()
    placer = GridPlacer(diode_offset_y=5.0, capacitor_offset_x=3.0)
    result = placer.place(matrix, registry)

    assert result.valid is True

    # Diode unrotated relative position is (0, 5).
    # Rotated 90 degrees around (0, 0):
    # x' = 0 * cos(90) - 5 * sin(90) = -5.0
    # y' = 0 * sin(90) + 5 * cos(90) = 0.0
    d0 = result.placements["D_0_0"]
    assert d0["x"] == pytest.approx(-5.0)
    assert d0["y"] == pytest.approx(0.0)
    assert d0["rotation"] == 90.0

    # Capacitor unrotated relative position is (3, 0).
    # Rotated 90 degrees around (0, 0):
    # x' = 3 * cos(90) - 0 * sin(90) = 0.0
    # y' = 3 * sin(90) + 0 * cos(90) = 3.0
    c0 = result.placements["C_0_0"]
    assert c0["x"] == pytest.approx(0.0)
    assert c0["y"] == pytest.approx(3.0)
    assert c0["rotation"] == 90.0
