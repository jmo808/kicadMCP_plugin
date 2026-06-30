import json

from kbd_engine.drc import DrcValidator
from kbd_engine.kle_parser import parse_kle_json
from kbd_engine.mcp_server import place_layout, preview_layout
from kbd_engine.placer import GridPlacer
from kbd_engine.registry import FootprintRegistry


def test_full_pipeline_e2e() -> None:
    # 1. Start with KLE JSON
    kle_data = """
    [
        ["K0", "K1"],
        ["K2", "K3"]
    ]
    """

    # 2. Parse
    matrix = parse_kle_json(kle_data)
    assert len(matrix.keys) == 4

    # 3. Resolve footprints & Place
    registry = FootprintRegistry()
    placer = GridPlacer()
    result = placer.place(matrix, registry)
    assert len(result.placements) == 12  # 4 keys * 3 components

    # 4. DRC Validate
    validator = DrcValidator()
    errors = validator.validate(result)
    assert len(errors) == 0


def test_mcp_preview_e2e() -> None:
    kle_data = '[["K0", "K1"]]'
    resp_str = preview_layout(layout_json=kle_data)
    resp = json.loads(resp_str)

    assert resp["success"] is True
    assert "placements" in resp
    assert "SW_0_0" in resp["placements"]


def test_mcp_place_invalid_layout_e2e() -> None:
    # Malformed JSON
    resp_str = place_layout(layout_json="{invalid")
    resp = json.loads(resp_str)

    assert resp["success"] is False
    assert "invalid" in resp["error"].lower()
