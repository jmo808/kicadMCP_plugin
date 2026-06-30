import json
import os
import shutil
import subprocess
import urllib.request
from typing import Any, Optional

from kbd_engine.exceptions import RouterError
from kbd_engine.pcbnew_adapter import PcbnewAdapter
from kbd_engine.router import Router
from kbd_engine.routing_models import RoutingRequest, RoutingResult, TraceSegment, Via


class RustAstarRouter(Router):
    """Router implementation that delegates to the Rust A* engine."""

    def __init__(
        self,
        mode: str = "auto",
        cli_path: Optional[str] = None,
        server_url: str = "http://127.0.0.1:8080/route",
    ) -> None:
        """Initialize the Rust A* router.

        Args:
            mode: Integration mode: 'auto', 'pyo3', 'subprocess', or 'rest'.
            cli_path: Custom path to the kbd-router-cli binary.
            server_url: URL of the kbd-router-server HTTP service.
        """
        self.mode = mode
        self.cli_path = cli_path
        self.server_url = server_url

    def route(self, request: RoutingRequest) -> RoutingResult:
        """Route the board specified in the request using the Rust A* engine.

        Args:
            request: The routing request containing netlist, board, and rules.

        Returns:
            A RoutingResult containing the trace segments, vias, and status.

        Raises:
            RouterError: If a fatal routing error occurs.
        """
        if self.mode not in ("auto", "pyo3", "subprocess", "rest"):
            raise RouterError(f"Invalid integration mode: {self.mode}")

        # 1. Load the board to obtain coordinates for the nets/pins
        adapter = PcbnewAdapter()
        try:
            adapter.load(request.board_file)
        except Exception as e:
            raise RouterError(f"Failed to load board file: {e}") from e

        # Calculate board bounding box from footprint positions
        footprints = adapter.get_footprints()
        if footprints:
            board_width = max(fp["x"] for fp in footprints) + 20.0
            board_height = max(fp["y"] for fp in footprints) + 20.0
        else:
            board_width = 100.0
            board_height = 100.0

        # 2. Build the nets array for the Rust engine
        nets = []
        for net_name, pin_tuples in request.netlist.items():
            pins = []
            for ref, pad_name in pin_tuples:
                pos = adapter.get_pad_position(ref, pad_name)
                if pos is None:
                    raise RouterError(
                        f"Could not resolve position for pad '{pad_name}' on footprint '{ref}'"
                    )
                # Map to grid coordinates
                gx = int(round(pos[0] / request.grid_pitch))
                gy = int(round(pos[1] / request.grid_pitch))
                pins.append({"x": gx, "y": gy, "layer": 0})

            # Determine track width & clearance based on net class rules
            class_name = "Signal"
            for pattern, c_name in request.net_classes.items():
                if net_name == pattern:
                    class_name = c_name
                    break

            rule = request.class_rules.get(class_name)
            track_width = rule.track_width if rule else 0.2
            clearance = rule.clearance if rule else 0.2

            nets.append(
                {
                    "name": net_name,
                    "pins": pins,
                    "track_width": track_width,
                    "clearance": clearance,
                }
            )

        # Retrieve keepout/obstacle zones from extra_options
        obstacles = request.extra_options.get("obstacles", [])

        # Build JSON request payload
        request_dict = {
            "width": board_width,
            "height": board_height,
            "grid_pitch": request.grid_pitch,
            "nets": nets,
            "obstacles": obstacles,
        }
        request_json = json.dumps(request_dict)

        # 3. Determine integration mode to use
        mode_to_try = self.mode
        if mode_to_try == "auto":
            try:
                import kbd_router  # noqa: F401

                mode_to_try = "pyo3"
            except ImportError:
                if self.cli_path or self._detect_cli():
                    mode_to_try = "subprocess"
                else:
                    mode_to_try = "rest"

        # 4. Invoke the Rust routing engine
        result_json = ""
        if mode_to_try == "pyo3":
            try:
                import kbd_router

                result_json = kbd_router.route_board(request_json)  # type: ignore[attr-defined]
            except Exception as e:
                raise RouterError(f"PyO3 routing failed: {e}") from e

        elif mode_to_try == "subprocess":
            cli = self.cli_path or self._detect_cli()
            if not cli:
                raise RouterError("Subprocess mode selected but kbd-router-cli not found")
            try:
                proc = subprocess.run(
                    [cli],
                    input=request_json,
                    text=True,
                    capture_output=True,
                    check=True,
                )
                result_json = proc.stdout
            except Exception as e:
                raise RouterError(f"Subprocess routing failed: {e}") from e

        elif mode_to_try == "rest":
            try:
                req = urllib.request.Request(
                    self.server_url,
                    data=request_json.encode("utf-8"),
                    headers={"Content-Type": "application/json"},
                    method="POST",
                )
                with urllib.request.urlopen(req) as response:
                    result_json = response.read().decode("utf-8")
            except Exception as e:
                raise RouterError(f"REST routing failed: {e}") from e
        else:
            raise RouterError(f"Invalid integration mode: {self.mode}")

        # 5. Parse and apply results to the board
        result = self._parse_result(result_json)
        if result.success:
            for trace in result.traces:
                adapter.add_track(
                    start_x=trace.start[0],
                    start_y=trace.start[1],
                    end_x=trace.end[0],
                    end_y=trace.end[1],
                    layer=trace.layer,
                    width=trace.width,
                )
            for via in result.vias:
                adapter.add_via(
                    x=via.position[0],
                    y=via.position[1],
                    drill=via.drill,
                    diameter=via.diameter,
                )
            try:
                adapter.save(request.board_file)
            except Exception as e:
                raise RouterError(f"Failed to save routed board: {e}") from e

        return result

    def _detect_cli(self) -> Optional[str]:
        possible_paths = [
            "./kbd_router/target/debug/kbd-router-cli",
            "./kbd_router/target/release/kbd-router-cli",
            "kbd-router-cli",
        ]
        for path in possible_paths:
            if "/" in path:
                if os.path.exists(path):
                    return path
            else:
                if shutil.which(path):
                    return path
        return None

    def _parse_result(self, res_str: str) -> RoutingResult:
        try:
            data = json.loads(res_str)
        except json.JSONDecodeError as e:
            raise RouterError(f"Failed to parse router output JSON: {e}") from e

        traces = [
            TraceSegment(
                start=tuple(seg["start"]),  # type: ignore[arg-type]
                end=tuple(seg["end"]),  # type: ignore[arg-type]
                layer=seg["layer"],
                width=seg["width"],
            )
            for seg in data.get("traces", [])
        ]
        vias = [
            Via(
                position=tuple(v["position"]),  # type: ignore[arg-type]
                drill=v["drill"],
                diameter=v["diameter"],
                layers=tuple(v["layers"]),  # type: ignore[arg-type]
            )
            for v in data.get("vias", [])
        ]
        return RoutingResult(
            success=data.get("success", False),
            traces=traces,
            vias=vias,
            unrouted_nets=data.get("unrouted_nets", []),
            diagnostics=data.get("diagnostics", ""),
        )
