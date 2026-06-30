import subprocess
import sys
import time
from pathlib import Path
from unittest.mock import patch

import pytest

from kbd_engine.exceptions import RouterError
from kbd_engine.pcbnew_adapter import PcbnewAdapter
from kbd_engine.routers.rust_astar import RustAstarRouter
from kbd_engine.routing_models import NetClass, RoutingRequest


def setup_mock_board(adapter: PcbnewAdapter) -> None:
    # Add SW_0_0 footprint at x=10, y=10
    adapter.add_footprint(
        library_path="kbd_custom",
        footprint_name="SW_Cherry_MX",
        reference="SW_0_0",
        x=10.0,
        y=10.0,
        rotation=0.0,
    )
    # Add SW_0_1 footprint at x=30, y=10
    adapter.add_footprint(
        library_path="kbd_custom",
        footprint_name="SW_Cherry_MX",
        reference="SW_0_1",
        x=30.0,
        y=10.0,
        rotation=0.0,
    )


def test_router_pyo3_mode(tmp_path: Path) -> None:
    filepath = str(tmp_path / "test.kicad_pcb")
    adapter = PcbnewAdapter()
    setup_mock_board(adapter)
    adapter.save(filepath)

    request = RoutingRequest(
        board_file=filepath,
        netlist={"ROW_0": [("SW_0_0", "1"), ("SW_0_1", "1")]},
        net_classes={"ROW_0": "MatrixRow"},
        class_rules={"MatrixRow": NetClass("MatrixRow", track_width=0.25, clearance=0.2)},
        grid_pitch=1.0,
    )

    router = RustAstarRouter(mode="pyo3")
    result = router.route(request)

    assert result.success is True
    assert len(result.traces) > 0

    # Verify traces are added to the board
    new_adapter = PcbnewAdapter()
    new_adapter.load(filepath)
    assert len(new_adapter.board.tracks) > 0


def test_router_subprocess_mode(tmp_path: Path) -> None:
    filepath = str(tmp_path / "test.kicad_pcb")
    adapter = PcbnewAdapter()
    setup_mock_board(adapter)
    adapter.save(filepath)

    request = RoutingRequest(
        board_file=filepath,
        netlist={"ROW_0": [("SW_0_0", "1"), ("SW_0_1", "1")]},
        net_classes={"ROW_0": "MatrixRow"},
        class_rules={"MatrixRow": NetClass("MatrixRow", track_width=0.25, clearance=0.2)},
        grid_pitch=1.0,
    )

    router = RustAstarRouter(
        mode="subprocess", cli_path="./kbd_router/target/debug/kbd-router-cli"
    )
    result = router.route(request)

    assert result.success is True
    assert len(result.traces) > 0


def test_router_rest_mode(tmp_path: Path) -> None:
    filepath = str(tmp_path / "test.kicad_pcb")
    adapter = PcbnewAdapter()
    setup_mock_board(adapter)
    adapter.save(filepath)

    request = RoutingRequest(
        board_file=filepath,
        netlist={"ROW_0": [("SW_0_0", "1"), ("SW_0_1", "1")]},
        net_classes={"ROW_0": "MatrixRow"},
        class_rules={"MatrixRow": NetClass("MatrixRow", track_width=0.25, clearance=0.2)},
        grid_pitch=1.0,
    )

    # Start the server
    server_path = "./kbd_router/target/debug/kbd-router-server"
    server_proc = subprocess.Popen([server_path])
    time.sleep(1.0)

    try:
        router = RustAstarRouter(mode="rest", server_url="http://127.0.0.1:8080/route")
        result = router.route(request)
        assert result.success is True
        assert len(result.traces) > 0
    finally:
        server_proc.terminate()
        server_proc.wait()


def test_router_auto_mode_fallback(tmp_path: Path) -> None:
    filepath = str(tmp_path / "test.kicad_pcb")
    adapter = PcbnewAdapter()
    setup_mock_board(adapter)
    adapter.save(filepath)

    request = RoutingRequest(
        board_file=filepath,
        netlist={"ROW_0": [("SW_0_0", "1"), ("SW_0_1", "1")]},
        net_classes={"ROW_0": "MatrixRow"},
        class_rules={"MatrixRow": NetClass("MatrixRow", track_width=0.25, clearance=0.2)},
        grid_pitch=1.0,
    )

    # Mock kbd_router import failure to force fallback to subprocess
    with patch.dict(sys.modules, {"kbd_router": None}):
        router = RustAstarRouter(
            mode="auto", cli_path="./kbd_router/target/debug/kbd-router-cli"
        )
        result = router.route(request)
        assert result.success is True
        assert len(result.traces) > 0


def test_router_invalid_mode(tmp_path: Path) -> None:
    filepath = str(tmp_path / "test.kicad_pcb")
    request = RoutingRequest(
        board_file=filepath,
        netlist={"ROW_0": [("SW_0_0", "1"), ("SW_0_1", "1")]},
    )
    router = RustAstarRouter(mode="invalid_mode")
    with pytest.raises(RouterError) as exc_info:
        router.route(request)
    assert "Invalid integration mode" in str(exc_info.value)
