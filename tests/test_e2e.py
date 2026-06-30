import json

from kbd_engine.drc import DrcValidator
from kbd_engine.kle_parser import parse_kle_json
from kbd_engine.mcp_server import place_layout, preview_layout
from kbd_engine.pcbnew_adapter import PcbnewAdapter
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


def test_e2e_kle_to_route_pipeline(tmp_path: str) -> None:
    import os
    from unittest.mock import patch

    from kbd_engine.mcp_server import route
    from kbd_engine.pcbnew_adapter import PcbnewAdapter
    from kbd_engine.routing_models import RoutingResult, TraceSegment

    # 1. Start with KLE layout
    kle_data = '[["K0", "K1"]]'

    # 2. Setup board path
    board_file = os.path.join(tmp_path, "e2e_test.kicad_pcb")
    adapter = PcbnewAdapter()

    # 3. Simulate placing layout
    from kbd_engine.mcp_server import place_layout
    # Mock PcbnewAdapter load/save inside place_layout
    with patch("kbd_engine.pcbnew_adapter.PcbnewAdapter.save", side_effect=lambda filepath: adapter.save(filepath)):
        resp_place = json.loads(place_layout(layout_json=kle_data))
        assert resp_place["success"] is True

    # Touch physical file for os.path.exists checks in route
    with open(board_file, "w") as f:
        f.write("")

    # 4. Route using Rust A* router (mocked)
    dummy_result = RoutingResult(
        traces=[
            TraceSegment(start=(7.5, 7.5), end=(27.5, 7.5), layer="F.Cu", width=0.25),
            TraceSegment(start=(27.5, 7.5), end=(27.5, 10.0), layer="B.Cu", width=0.25),
        ],
        vias=[],
        success=True,
    )

    netlist = {"ROW_0": [["SW_0_0", "1"], ["SW_0_1", "1"]]}

    with patch("kbd_engine.routers.rust_astar.RustAstarRouter.route", return_value=dummy_result):
        resp_route_str = route(
            board_file=board_file,
            netlist_json=json.dumps(netlist),
            router_name="rust_astar",
            dry_run=False,
        )
        resp_route = json.loads(resp_route_str)
        assert resp_route["success"] is True
        # Check that vias were automatically inserted at transition point (27.5, 7.5)
        assert resp_route["vias_count"] == 1

        # Check tracks and vias are written to board adapter
        adapter_check = PcbnewAdapter()
        adapter_check.load(board_file)
        # 2 tracks + 1 via
        assert len(adapter_check.board.tracks) == 3


def test_e2e_mcp_route_backends(tmp_path: str) -> None:
    import os
    from unittest.mock import patch

    from kbd_engine.mcp_server import route
    from kbd_engine.pcbnew_adapter import PcbnewAdapter
    from kbd_engine.routing_models import RoutingResult, TraceSegment

    board_file = os.path.join(tmp_path, "backends_test.kicad_pcb")
    adapter = PcbnewAdapter()
    adapter.save(board_file)
    with open(board_file, "w") as f:
        f.write("")

    dummy_result = RoutingResult(
        traces=[TraceSegment(start=(0, 0), end=(1, 1), layer="F.Cu", width=0.25)],
        vias=[],
        success=True,
    )
    netlist = {"ROW_0": [["SW_0_0", "1"]]}

    # Test FreeRouting mock
    with patch("kbd_engine.routers.freerouting.FreeRoutingRouter.route", return_value=dummy_result):
        resp = json.loads(
            route(
                board_file=board_file,
                netlist_json=json.dumps(netlist),
                router_name="freerouting",
                dry_run=True,
            )
        )
        assert resp["success"] is True

    # Test Quilter mock
    with patch("kbd_engine.routers.quilter.QuilterRouter.route", return_value=dummy_result):
        resp = json.loads(
            route(
                board_file=board_file,
                netlist_json=json.dumps(netlist),
                router_name="quilter",
                router_options_json=json.dumps({"api_key": "dummy_key"}),
                dry_run=True,
            )
        )
        assert resp["success"] is True


def test_e2e_routing_failure_details(tmp_path: str) -> None:
    import os
    from unittest.mock import patch

    from kbd_engine.mcp_server import route
    from kbd_engine.routing_models import RoutingResult

    board_file = os.path.join(tmp_path, "fail_test.kicad_pcb")
    adapter = PcbnewAdapter()
    adapter.save(board_file)
    with open(board_file, "w") as f:
        f.write("")

    failed_result = RoutingResult(
        traces=[],
        vias=[],
        unrouted_nets=["ROW_0"],
        success=False,
        diagnostics="Pin ROW_0 is blocked by a keepout boundary",
    )

    with patch("kbd_engine.routers.rust_astar.RustAstarRouter.route", return_value=failed_result):
        resp = json.loads(
            route(
                board_file=board_file,
                netlist_json='{"ROW_0": []}',
                router_name="rust_astar",
                dry_run=True,
            )
        )
        assert resp["success"] is False
        assert "ROW_0" in resp["unrouted_nets"]
        assert "blocked by a keepout" in resp["diagnostics"]

