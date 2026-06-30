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


def test_router_60_key_matrix_performance(tmp_path: Path) -> None:
    filepath = str(tmp_path / "test_60key.kicad_pcb")
    adapter = PcbnewAdapter()

    # 5 rows x 12 columns = 60 keys
    rows, cols = 5, 12
    for r in range(rows):
        for c in range(cols):
            # Place switch at 19.05mm grid spacing
            sw_ref = f"SW_{r}_{c}"
            adapter.add_footprint(
                library_path="kbd_custom",
                footprint_name="SW_Cherry_MX",
                reference=sw_ref,
                x=c * 19.05,
                y=r * 19.05,
                rotation=0.0,
            )
            # Place diode 5mm below switch
            d_ref = f"D_{r}_{c}"
            adapter.add_footprint(
                library_path="kbd_custom",
                footprint_name="Diode",
                reference=d_ref,
                x=c * 19.05,
                y=r * 19.05 + 5.0,
                rotation=0.0,
            )

    adapter.save(filepath)

    # Build netlist
    # - ROW_r connects D_r_c pin 2 for all c
    # - COL_c connects SW_r_c pin 1 for all r
    # - SW_D_r_c connects SW_r_c pin 2 to D_r_c pin 1
    netlist = {}
    net_classes = {}
    class_rules = {
        "Default": NetClass("Default", track_width=0.25, clearance=0.2)
    }

    for r in range(rows):
        row_net = f"ROW_{r}"
        netlist[row_net] = [(f"D_{r}_{c}", "2") for c in range(cols)]
        net_classes[row_net] = "Default"

    for c in range(cols):
        col_net = f"COL_{c}"
        netlist[col_net] = [(f"SW_{r}_{c}", "1") for r in range(rows)]
        net_classes[col_net] = "Default"

    for r in range(rows):
        for c in range(cols):
            local_net = f"SW_D_{r}_{c}"
            netlist[local_net] = [(f"SW_{r}_{c}", "2"), (f"D_{r}_{c}", "1")]
            net_classes[local_net] = "Default"

    request = RoutingRequest(
        board_file=filepath,
        netlist=netlist,
        net_classes=net_classes,
        class_rules=class_rules,
        grid_pitch=0.5,
    )

    router = RustAstarRouter(mode="pyo3")

    start_time = time.perf_counter()
    result = router.route(request)
    duration = time.perf_counter() - start_time

    print(f"\n60-key matrix routed in {duration:.4f} seconds")
    assert len(result.traces) > 0
    # Ensure performance requirement NFR-01 is satisfied (< 10 seconds)
    assert duration < 10.0

