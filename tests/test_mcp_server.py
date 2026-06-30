import json
import os


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


def test_mcp_get_routers() -> None:
    from kbd_engine.mcp_server import get_routers

    resp_str = get_routers()
    resp = json.loads(resp_str)
    assert resp["success"] is True
    assert "routers" in resp
    names = [r["name"] for r in resp["routers"]]
    assert "rust_astar" in names
    assert "freerouting" in names
    assert "quilter" in names


def test_mcp_set_net_classes(tmp_path: str) -> None:
    from kbd_engine.mcp_server import set_net_classes

    config_file = os.path.join(tmp_path, "net_classes.json")
    classes_data = {
        "classes": {
            "MatrixRow": {"track_width": 0.25, "clearance": 0.2},
            "MatrixCol": {"track_width": 0.25, "clearance": 0.2},
        },
        "patterns": {
            "ROW_.*": "MatrixRow",
            "COL_.*": "MatrixCol",
        },
    }

    resp_str = set_net_classes(classes_json=json.dumps(classes_data), config_path=config_file)
    resp = json.loads(resp_str)
    assert resp["success"] is True
    assert os.path.exists(config_file)

    # Malformed JSON test
    resp_str_err = set_net_classes(classes_json="{bad json}", config_path=config_file)
    resp_err = json.loads(resp_str_err)
    assert resp_err["success"] is False


def test_mcp_route_and_preview(tmp_path: str) -> None:
    import os
    from unittest.mock import patch

    from kbd_engine.mcp_server import route, route_preview
    from kbd_engine.pcbnew_adapter import PcbnewAdapter
    from kbd_engine.routing_models import RoutingResult, TraceSegment, Via

    # 1. Create a dummy board
    board_file = os.path.join(tmp_path, "test.kicad_pcb")
    adapter = PcbnewAdapter()
    # Add switches
    adapter.add_footprint(
        library_path="kbd_custom",
        footprint_name="SW_Cherry_MX",
        reference="SW_0_0",
        x=10.0,
        y=10.0,
        rotation=0.0,
    )
    adapter.add_footprint(
        library_path="kbd_custom",
        footprint_name="SW_Cherry_MX",
        reference="SW_0_1",
        x=30.0,
        y=10.0,
        rotation=0.0,
    )
    adapter.save(board_file)
    with open(board_file, "w") as f:
        f.write("")

    netlist = {"ROW_0": [["SW_0_0", "1"], ["SW_0_1", "1"]]}
    dummy_result = RoutingResult(
        traces=[TraceSegment(start=(7.5, 7.5), end=(27.5, 7.5), layer="F.Cu", width=0.25)],
        vias=[Via(position=(27.5, 7.5), drill=0.3, diameter=0.6, layers=("F.Cu", "B.Cu"))],
        success=True,
    )

    # Test route with dry_run=True
    with patch("kbd_engine.routers.rust_astar.RustAstarRouter.route", return_value=dummy_result):
        resp_str = route(
            board_file=board_file,
            netlist_json=json.dumps(netlist),
            router_name="rust_astar",
            dry_run=True,
        )
        resp = json.loads(resp_str)
        assert resp["success"] is True
        assert resp["traces_count"] == 1
        assert resp["vias_count"] == 1

        # Check board was not modified in dry_run
        adapter_check = PcbnewAdapter()
        adapter_check.load(board_file)
        assert len(adapter_check.board.tracks) == 0

    # Test route with dry_run=False
    with patch("kbd_engine.routers.rust_astar.RustAstarRouter.route", return_value=dummy_result):
        resp_str = route(
            board_file=board_file,
            netlist_json=json.dumps(netlist),
            router_name="rust_astar",
            dry_run=False,
        )
        resp = json.loads(resp_str)
        assert resp["success"] is True

        # Check board was modified
        adapter_check = PcbnewAdapter()
        adapter_check.load(board_file)
        # 1 trace + 1 via
        assert len(adapter_check.board.tracks) == 2

    # Test route_preview tool endpoint
    with patch("kbd_engine.routers.rust_astar.RustAstarRouter.route", return_value=dummy_result):
        resp_str = route_preview(
            board_file=board_file,
            netlist_json=json.dumps(netlist),
            router_name="rust_astar",
        )
        resp = json.loads(resp_str)
        assert resp["success"] is True
        assert len(resp["traces"]) == 1
        assert len(resp["vias"]) == 1
        assert resp["traces"][0]["start"] == [7.5, 7.5]
        assert resp["vias"][0]["position"] == [27.5, 7.5]


def test_mcp_route_error(tmp_path: str) -> None:
    from kbd_engine.mcp_server import route

    # Board file missing
    resp_str = route(
        board_file=os.path.join(tmp_path, "missing.kicad_pcb"),
        netlist_json="{}",
        router_name="rust_astar",
    )
    resp = json.loads(resp_str)
    assert resp["success"] is False
    assert "Board file not found" in resp["error"]

