import io
import json
import urllib.error
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from kbd_engine.exceptions import RouterError
from kbd_engine.pcbnew_adapter import PcbnewAdapter
from kbd_engine.routers.quilter import QuilterRouter
from kbd_engine.routing_models import NetClass, RoutingRequest


def test_quilter_missing_api_key(tmp_path: Path) -> None:
    filepath = str(tmp_path / "test.kicad_pcb")
    adapter = PcbnewAdapter()
    adapter.save(filepath)

    request = RoutingRequest(board_file=filepath, netlist={})
    router = QuilterRouter(api_key="")

    with pytest.raises(RouterError) as exc_info:
        router.route(request)
    assert "API key is missing or empty" in str(exc_info.value)


def test_quilter_route_success(tmp_path: Path) -> None:
    filepath = str(tmp_path / "test.kicad_pcb")
    adapter = PcbnewAdapter()
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

    # Mock urllib.request.urlopen to simulate Quilter API
    call_count = 0

    from typing import Any
    def mock_urlopen(req: urllib.request.Request, *args: Any, **kwargs: Any) -> MagicMock:
        nonlocal call_count
        method = req.get_method()
        url = req.full_url

        resp = MagicMock()
        resp.__enter__.return_value = resp
        resp.code = 200

        if method == "POST" and url.endswith("/jobs"):
            resp.read.return_value = json.dumps({"job_id": "job_12345", "status": "pending"}).encode(
                "utf-8"
            )
        elif method == "GET" and "/jobs/job_12345" in url:
            call_count += 1
            if call_count == 1:
                resp.read.return_value = json.dumps({"status": "running"}).encode("utf-8")
            else:
                resp.read.return_value = json.dumps(
                    {"status": "completed", "ses": ses_content}
                ).encode("utf-8")
        return resp

    router = QuilterRouter(api_key="valid_key", poll_interval=0.01, timeout=5)
    with patch("urllib.request.urlopen", side_effect=mock_urlopen):
        result = router.route(request)

    assert result.success is True
    assert len(result.traces) == 1
    assert result.traces[0].start == (7.5, 7.5)
    assert result.traces[0].end == (27.5, 7.5)

    # Check that tracks were added to the saved board
    new_adapter = PcbnewAdapter()
    new_adapter.load(filepath)
    assert len(new_adapter.board.tracks) == 1


def test_quilter_route_auth_failure(tmp_path: Path) -> None:
    filepath = str(tmp_path / "test.kicad_pcb")
    adapter = PcbnewAdapter()
    adapter.save(filepath)

    request = RoutingRequest(board_file=filepath, netlist={})

    # Raise HTTPError 401
    err_body = io.BytesIO(json.dumps({"error": "Invalid token"}).encode("utf-8"))
    http_error = urllib.error.HTTPError(
        url="https://api.quilter.ai/v1/jobs",
        code=401,
        msg="Unauthorized",
        hdrs=None,  # type: ignore[arg-type]
        fp=err_body,
    )

    router = QuilterRouter(api_key="bad_key")
    with patch("urllib.request.urlopen", side_effect=http_error):
        with pytest.raises(RouterError) as exc_info:
            router.route(request)
        assert "authentication failed: Invalid token" in str(exc_info.value)


def test_quilter_route_rate_limiting(tmp_path: Path) -> None:
    filepath = str(tmp_path / "test.kicad_pcb")
    adapter = PcbnewAdapter()
    adapter.save(filepath)

    request = RoutingRequest(board_file=filepath, netlist={})

    err_body = io.BytesIO(json.dumps({"error": "Too many requests"}).encode("utf-8"))
    http_error = urllib.error.HTTPError(
        url="https://api.quilter.ai/v1/jobs",
        code=429,
        msg="Too Many Requests",
        hdrs=None,  # type: ignore[arg-type]
        fp=err_body,
    )

    router = QuilterRouter(api_key="valid_key")
    with patch("urllib.request.urlopen", side_effect=http_error):
        with pytest.raises(RouterError) as exc_info:
            router.route(request)
        assert "rate limit exceeded: Too many requests" in str(exc_info.value)


def test_quilter_route_job_failed(tmp_path: Path) -> None:
    filepath = str(tmp_path / "test.kicad_pcb")
    adapter = PcbnewAdapter()
    adapter.save(filepath)

    request = RoutingRequest(board_file=filepath, netlist={})

    from typing import Any
    def mock_urlopen(req: urllib.request.Request, *args: Any, **kwargs: Any) -> MagicMock:
        method = req.get_method()
        url = req.full_url
        resp = MagicMock()
        resp.__enter__.return_value = resp
        resp.code = 200

        if method == "POST" and url.endswith("/jobs"):
            resp.read.return_value = json.dumps({"job_id": "job_12345", "status": "pending"}).encode(
                "utf-8"
            )
        elif method == "GET" and "/jobs/job_12345" in url:
            resp.read.return_value = json.dumps(
                {"status": "failed", "error": "Board is unroutable"}
            ).encode("utf-8")
        return resp

    router = QuilterRouter(api_key="valid_key", poll_interval=0.01, timeout=5)
    with patch("urllib.request.urlopen", side_effect=mock_urlopen):
        with pytest.raises(RouterError) as exc_info:
            router.route(request)
        assert "job failed: Board is unroutable" in str(exc_info.value)


def test_quilter_route_timeout(tmp_path: Path) -> None:
    filepath = str(tmp_path / "test.kicad_pcb")
    adapter = PcbnewAdapter()
    adapter.save(filepath)

    request = RoutingRequest(board_file=filepath, netlist={})

    from typing import Any
    def mock_urlopen(req: urllib.request.Request, *args: Any, **kwargs: Any) -> MagicMock:
        method = req.get_method()
        url = req.full_url
        resp = MagicMock()
        resp.__enter__.return_value = resp
        resp.code = 200

        if method == "POST" and url.endswith("/jobs"):
            resp.read.return_value = json.dumps({"job_id": "job_12345", "status": "pending"}).encode(
                "utf-8"
            )
        elif method == "GET" and "/jobs/job_12345" in url:
            resp.read.return_value = json.dumps({"status": "running"}).encode("utf-8")
        return resp

    router = QuilterRouter(api_key="valid_key", poll_interval=0.01, timeout=0.05)
    with patch("urllib.request.urlopen", side_effect=mock_urlopen):
        with pytest.raises(RouterError) as exc_info:
            router.route(request)
        assert "timed out after 0.05 seconds" in str(exc_info.value)
