import json


def test_mcp_preview_tool() -> None:
    kle_data = '[["A", "B"]]'
    # Call the tool function registered on the FastMCP instance
    # Usually we can get the tool function or call it via mcp
    # Let's get the tool function from mcp or call it directly.
    # FastMCP tools are functions decorated with @mcp.tool().
    # If we define them in mcp_server.py, we can export them or import them.
    # Let's assume they are decorated functions imported directly:
    from kbd_engine.mcp_server import preview_layout

    # 1. Preview Layout
    resp_str = preview_layout(layout_json=kle_data)
    resp = json.loads(resp_str)
    assert resp["success"] is True
    assert "SW_0_0" in resp["placements"]
    assert "D_0_0" in resp["placements"]


def test_mcp_place_tool() -> None:
    from kbd_engine.mcp_server import place_layout

    kle_data = '[["A", "B"]]'

    resp_str = place_layout(layout_json=kle_data)
    resp = json.loads(resp_str)
    assert resp["success"] is True
    assert "Placed 6 components successfully" in resp["message"]


def test_mcp_validate_drc_tool() -> None:
    from kbd_engine.mcp_server import validate_layout_drc

    # Overlapping layout -> collision!
    # For a validation tool, we pass KLE JSON, it parses, places, and runs DRC.
    kle_data = '[["A", {"x": -0.8}, "B"]]'  # 0.8u offset -> distance ~15.24mm -> collision!
    resp_str = validate_layout_drc(layout_json=kle_data)
    resp = json.loads(resp_str)

    assert resp["success"] is True  # The tool execution succeeded
    assert len(resp["errors"]) > 0  # But DRC errors were found
    assert any("collision" in err.lower() or "clearance" in err.lower() for err in resp["errors"])


def test_mcp_place_tool_malformed_json() -> None:
    from kbd_engine.mcp_server import place_layout

    resp_str = place_layout(layout_json="{invalid json}")
    resp = json.loads(resp_str)
    assert resp["success"] is False
    assert "error" in resp
