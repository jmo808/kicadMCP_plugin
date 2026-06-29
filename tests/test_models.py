import pytest

from kbd_engine.models import Key, KeyMatrix, PlacementResult


def test_key_creation_and_defaults() -> None:
    # Test simple 1u key
    key = Key(x=19.05, y=0.0)
    assert key.x == 19.05
    assert key.y == 0.0
    assert key.width == 1.0
    assert key.height == 1.0
    assert key.rotation == 0.0
    assert key.matrix_row is None
    assert key.matrix_col is None
    assert key.logical_key_id == "SW_19.05_0.0"


def test_key_with_matrix_coords() -> None:
    key = Key(x=0.0, y=0.0, matrix_row=0, matrix_col=1)
    assert key.matrix_row == 0
    assert key.matrix_col == 1
    assert key.logical_key_id == "SW_0_1"


def test_key_immutability() -> None:
    key = Key(x=0.0, y=0.0)
    with pytest.raises(AttributeError):
        key.x = 10.0  # type: ignore[misc]


def test_key_matrix() -> None:
    key1 = Key(x=0.0, y=0.0, matrix_row=0, matrix_col=0)
    key2 = Key(x=19.05, y=0.0, matrix_row=0, matrix_col=1)

    matrix = KeyMatrix(keys=[key1, key2])
    assert len(matrix.keys) == 2
    assert matrix.rows == 1
    assert matrix.cols == 2
    assert matrix.get_key_at(0, 0) == key1
    assert matrix.get_key_at(0, 1) == key2
    assert matrix.get_key_at(0, 2) is None


def test_placement_result() -> None:
    placements = {
        "SW_0_0": {"x": 0.0, "y": 0.0, "rotation": 0.0, "footprint": "SW_Cherry_MX"},
        "D_0_0": {"x": 0.0, "y": 5.0, "rotation": 0.0, "footprint": "Diode_SMD"},
    }
    result = PlacementResult(placements=placements, valid=True)
    assert result.placements == placements
    assert result.valid is True
    assert len(result.errors) == 0

    invalid_result = PlacementResult(placements={}, valid=False, errors=["Clearance violation SW_0_0"])
    assert invalid_result.valid is False
    assert len(invalid_result.errors) == 1
