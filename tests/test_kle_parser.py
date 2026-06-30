import pytest

from kbd_engine.exceptions import ParseError
from kbd_engine.kle_parser import parse_kle_json


def test_parse_minimal_layout() -> None:
    # 4 keys in a 2x2 grid
    kle_data = """
    [
        ["A", "B"],
        ["C", "D"]
    ]
    """
    matrix = parse_kle_json(kle_data)
    assert len(matrix.keys) == 4

    # Check default spacing (19.05 mm standard keyboard pitch)
    # Row 0: Key 0 at (0, 0), Key 1 at (19.05, 0)
    # Row 1: Key 2 at (0, 19.05), Key 3 at (19.05, 19.05)
    k0 = matrix.keys[0]
    k1 = matrix.keys[1]
    k2 = matrix.keys[2]
    k3 = matrix.keys[3]

    assert k0.x == pytest.approx(0.0)
    assert k0.y == pytest.approx(0.0)
    assert k1.x == pytest.approx(19.05)
    assert k1.y == pytest.approx(0.0)
    assert k2.x == pytest.approx(0.0)
    assert k2.y == pytest.approx(19.05)
    assert k3.x == pytest.approx(19.05)
    assert k3.y == pytest.approx(19.05)


def test_parse_key_sizes() -> None:
    # Test keys with custom widths and spacing offsets
    # [ "A", {"w": 1.5, "x": 0.5}, "B", {"w": 2}, "C" ]
    kle_data = """
    [
        ["A", {"w": 1.5, "x": 0.5}, "B", {"w": 2}, "C"]
    ]
    """
    matrix = parse_kle_json(kle_data)
    assert len(matrix.keys) == 3

    k0 = matrix.keys[0]  # size 1u at x=0
    k1 = matrix.keys[1]  # size 1.5u after x=0.5 offset -> starts at 1.0u + 0.5u = 1.5u -> x = 1.5 * 19.05
    k2 = matrix.keys[2]  # size 2u after k1 (1.5u wide) -> starts at 1.5u + 1.5u = 3.0u -> x = 3.0 * 19.05

    assert k0.x == pytest.approx(0.0)
    assert k0.width == 1.0

    assert k1.x == pytest.approx(1.5 * 19.05)
    assert k1.width == 1.5

    assert k2.x == pytest.approx(3.0 * 19.05)
    assert k2.width == 2.0


def test_parse_key_rotations() -> None:
    # Test key rotation around a center point
    # [{"r": 15, "rx": 1, "ry": 1}, "A"]
    kle_data = """
    [
        [{"r": 15, "rx": 1, "ry": 1}, "A"]
    ]
    """
    matrix = parse_kle_json(kle_data)
    assert len(matrix.keys) == 1
    k0 = matrix.keys[0]

    assert k0.rotation == 15.0
    # Position should be calculated relative to center (1, 1) * 19.05
    assert k0.x != 0.0
    assert k0.y != 0.0


def test_parse_invalid_json() -> None:
    # Malformed JSON syntax
    with pytest.raises(ParseError) as exc_info:
        parse_kle_json("[invalid json")
    assert "JSON" in str(exc_info.value)


def test_parse_malformed_structure() -> None:
    # Valid JSON but not a list of rows
    with pytest.raises(ParseError) as exc_info:
        parse_kle_json('{"not": "a layout list"}')
    assert "list" in str(exc_info.value).lower()


def test_parse_full_60_percent_layout() -> None:
    # Simple representation of a 60% layout (first two rows)
    kle_data = """
    [
        ["Esc", "1", "2", "3", "4", "5", "6", "7", "8", "9", "0", "-", "=", "Backspace"],
        [{"w": 1.5}, "Tab", "Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P", "[", "]", {"w": 1.5}, "\\\\|"]
    ]
    """
    matrix = parse_kle_json(kle_data)
    # Row 1: 14 keys
    # Row 2: 14 keys
    assert len(matrix.keys) == 28

    # Check Tab position (row 1, first key, width 1.5)
    tab_key = matrix.keys[14]
    assert tab_key.width == 1.5
    assert tab_key.x == pytest.approx(0.0)
    assert tab_key.y == pytest.approx(19.05)
