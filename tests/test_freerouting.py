import os
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from kbd_engine.exceptions import RouterError
from kbd_engine.pcbnew_adapter import PcbnewAdapter
from kbd_engine.routers.freerouting import FreeRoutingRouter, parse_sexpr
from kbd_engine.routing_models import NetClass, RoutingRequest

_orig_exists = os.path.exists


def mock_exists(path: str) -> bool:
    if path == "/mock/freerouting.jar":
        return True
    return _orig_exists(path)


def test_parse_sexpr() -> None:
    # Basic nested structure
    s = r'(pcb (parser (string_quote "\\")) (resolution um 1000))'
    parsed = parse_sexpr(s)
    assert parsed == ["pcb", ["parser", ["string_quote", "\\"]], ["resolution", "um", "1000"]]

    # String with spaces
    s2 = "(name \"ROW 0\")"
    assert parse_sexpr(s2) == ["name", "ROW 0"]

    # Invalid expression
    with pytest.raises(ValueError):
        parse_sexpr("name (ROW 0)")


def test_freerouting_parser_ses() -> None:
    ses = """
    (session board
      (routes
        (network
          (net ROW_0
            (wire
              (path F.Cu 0.25 (10.0 10.0) (20.0 10.0) (30.0 10.0))
            )
            (via via_type
              (at 30.0 10.0)
              (layers F.Cu B.Cu)
            )
          )
        )
      )
    )
    """
    router = FreeRoutingRouter()
    result = router.parse_ses(ses)

    assert result.success is True
    assert len(result.traces) == 2
    assert result.traces[0].start == (10.0, 10.0)
    assert result.traces[0].end == (20.0, 10.0)
    assert result.traces[0].layer == "F.Cu"
    assert result.traces[0].width == 0.25

    assert len(result.vias) == 1
    assert result.vias[0].position == (30.0, 10.0)
    assert result.vias[0].layers == ("F.Cu", "B.Cu")


def test_freerouting_missing_executor(tmp_path: Path) -> None:
    filepath = str(tmp_path / "test.kicad_pcb")
    # Save a mock board
    adapter = PcbnewAdapter()
    adapter.save(filepath)

    request = RoutingRequest(
        board_file=filepath,
        netlist={"ROW_0": [("SW_0_0", "1"), ("SW_0_1", "1")]},
    )

    # Force detect_jar to return None and mock shutil.which to return None
    router = FreeRoutingRouter(jar_path="/nonexistent/freerouting.jar")
    with patch("shutil.which", return_value=None), patch.object(
        router, "_detect_jar", return_value=None
    ):
        with pytest.raises(RouterError) as exc_info:
            router.route(request)
        assert "FreeRouting executor not found" in str(exc_info.value)


def test_freerouting_route_success(tmp_path: Path) -> None:
    filepath = str(tmp_path / "test.kicad_pcb")
    adapter = PcbnewAdapter()
    # Add SW_0_0 at 10,10 and SW_0_1 at 30,10
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
    adapter.save(filepath)

    request = RoutingRequest(
        board_file=filepath,
        netlist={"ROW_0": [("SW_0_0", "1"), ("SW_0_1", "1")]},
        net_classes={"ROW_0": "MatrixRow"},
        class_rules={"MatrixRow": NetClass("MatrixRow", track_width=0.25, clearance=0.2)},
    )

    ses_content = """
    (session board
      (routes
        (network
          (net ROW_0
            (wire (path F.Cu 0.25 (7.5 7.5) (27.5 7.5)))
          )
        )
      )
    )
    """

    from typing import Any
    def mock_run(cmd: list[str], *args: Any, **kwargs: Any) -> MagicMock:
        # cmd contains: java -jar freerouting.jar -de <dsn> -do <ses> -mp 10
        # extract ses path
        ses_idx = cmd.index("-do") + 1
        ses_path = cmd[ses_idx]
        with open(ses_path, "w") as f:
            f.write(ses_content)
        mock_proc = MagicMock()
        mock_proc.returncode = 0
        return mock_proc

    router = FreeRoutingRouter(jar_path="/mock/freerouting.jar")
    with patch("subprocess.run", side_effect=mock_run), patch("os.path.exists", side_effect=mock_exists):
        result = router.route(request)

    assert result.success is True
    assert len(result.traces) == 1
    assert result.traces[0].start == (7.5, 7.5)
    assert result.traces[0].end == (27.5, 7.5)

    # Check that tracks were added to the saved board
    new_adapter = PcbnewAdapter()
    new_adapter.load(filepath)
    assert len(new_adapter.board.tracks) == 1


def test_freerouting_route_timeout(tmp_path: Path) -> None:
    filepath = str(tmp_path / "test.kicad_pcb")
    adapter = PcbnewAdapter()
    adapter.save(filepath)

    request = RoutingRequest(
        board_file=filepath,
        netlist={},
    )

    router = FreeRoutingRouter(jar_path="/mock/freerouting.jar", timeout=5)
    with patch(
        "subprocess.run", side_effect=subprocess.TimeoutExpired(cmd=[], timeout=5)
    ), patch("os.path.exists", side_effect=mock_exists):
        with pytest.raises(RouterError) as exc_info:
            router.route(request)
        assert "timed out after 5 seconds" in str(exc_info.value)


def test_freerouting_route_failure(tmp_path: Path) -> None:
    filepath = str(tmp_path / "test.kicad_pcb")
    adapter = PcbnewAdapter()
    adapter.save(filepath)

    request = RoutingRequest(
        board_file=filepath,
        netlist={},
    )

    router = FreeRoutingRouter(jar_path="/mock/freerouting.jar")
    mock_proc = MagicMock()
    mock_proc.returncode = 1
    mock_proc.stdout = "Routing failed"
    mock_proc.stderr = "Out of memory"

    with patch("subprocess.run", return_value=mock_proc), patch("os.path.exists", side_effect=mock_exists):
        with pytest.raises(RouterError) as exc_info:
            router.route(request)
        assert "failed to generate routed session file" in str(exc_info.value)
        assert "Out of memory" in str(exc_info.value)
