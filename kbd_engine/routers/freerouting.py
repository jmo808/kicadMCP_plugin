import os
import re
import shutil
import subprocess
import tempfile
from typing import Any

from kbd_engine.exceptions import RouterError
from kbd_engine.pcbnew_adapter import PcbnewAdapter
from kbd_engine.router import Router
from kbd_engine.routing_models import RoutingRequest, RoutingResult, TraceSegment, Via


def parse_sexpr(s: str) -> list[Any]:
    """Parse an S-expression string into a nested Python list."""
    token_rx = re.compile(r'\s*("(?:\\.|[^\\"])*"|[()"]|[^\s()"]+)')
    tokens = []
    for m in token_rx.finditer(s):
        token = m.group(1)
        if token.startswith('"') and token.endswith('"'):
            token = token[1:-1].replace('\\"', '"').replace('\\\\', '\\')
        tokens.append(token)

    def parse_list(tokens: list[str], i: int) -> tuple[list[Any], int]:
        res: list[Any] = []
        while i < len(tokens):
            t = tokens[i]
            if t == "(":
                sub, i = parse_list(tokens, i + 1)
                res.append(sub)
            elif t == ")":
                return res, i + 1
            else:
                res.append(t)
                i += 1
        return res, i

    if not tokens or tokens[0] != "(":
        raise ValueError("Invalid S-expression: must start with '('")
    result, _ = parse_list(tokens, 1)
    return result


class FreeRoutingRouter(Router):
    """Router implementation that delegates to the external FreeRouting tool."""

    def __init__(self, jar_path: str | None = None, timeout: int = 60) -> None:
        """Initialize the FreeRouting router.

        Args:
            jar_path: Custom path to the freerouting.jar file.
            timeout: Timeout for the FreeRouting process in seconds.
        """
        self.jar_path = jar_path
        self.timeout = timeout

    def route(self, request: RoutingRequest) -> RoutingResult:
        """Route the board using FreeRouting.

        Args:
            request: The routing request containing netlist, board, and rules.

        Returns:
            A RoutingResult containing the trace segments, vias, and status.

        Raises:
            RouterError: If FreeRouting is missing or a fatal error occurs.
        """
        adapter = PcbnewAdapter()
        try:
            adapter.load(request.board_file)
        except Exception as e:
            raise RouterError(f"Failed to load board file: {e}") from e

        # Find freerouting execution command
        jar = self.jar_path or self._detect_jar()
        if jar and not os.path.exists(jar):
            jar = None

        if jar:
            cmd = ["java", "-jar", jar]
        elif shutil.which("freerouting"):
            cmd = ["freerouting"]
        else:
            raise RouterError(
                "FreeRouting executor not found (freerouting.jar or freerouting executable)"
            )

        # Generate DSN content
        try:
            dsn_content = self.export_dsn(adapter, request)
        except Exception as e:
            raise RouterError(f"Failed to export Specctra DSN: {e}") from e

        # Write to temporary file and execute FreeRouting
        with tempfile.TemporaryDirectory() as tmpdir:
            dsn_path = os.path.join(tmpdir, "board.dsn")
            ses_path = os.path.join(tmpdir, "board.ses")

            with open(dsn_path, "w") as f:
                f.write(dsn_content)

            run_cmd = cmd + ["-de", dsn_path, "-do", ses_path, "-mp", "10"]
            try:
                proc = subprocess.run(
                    run_cmd,
                    capture_output=True,
                    text=True,
                    timeout=self.timeout,
                    check=False,
                )
            except subprocess.TimeoutExpired as e:
                raise RouterError(f"FreeRouting timed out after {self.timeout} seconds") from e
            except Exception as e:
                raise RouterError(f"Failed to execute FreeRouting: {e}") from e

            if not os.path.exists(ses_path):
                raise RouterError(
                    f"FreeRouting failed to generate routed session file.\n"
                    f"Stdout: {proc.stdout}\nStderr: {proc.stderr}"
                )

            with open(ses_path) as f:
                ses_content = f.read()

            try:
                result = self.parse_ses(ses_content)
            except Exception as e:
                raise RouterError(f"Failed to parse FreeRouting SES output: {e}") from e

            # Apply routed tracks/vias to the board
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

    def _detect_jar(self) -> str | None:
        possible_paths = [
            "./freerouting.jar",
            "./kbd_engine/routers/freerouting.jar",
        ]
        for path in possible_paths:
            if os.path.exists(path):
                return path
        return None

    def export_dsn(self, adapter: PcbnewAdapter, request: RoutingRequest) -> str:
        footprints = adapter.get_footprints()
        if footprints:
            board_width = max(fp["x"] for fp in footprints) + 20.0
            board_height = max(fp["y"] for fp in footprints) + 20.0
        else:
            board_width = 100.0
            board_height = 100.0

        library_images = {}
        for fp in footprints:
            ref = fp["reference"]
            pads = adapter.get_footprint_pads(ref)
            fp_type = (
                "FP_SW"
                if ref.startswith("SW_")
                else ("FP_D" if ref.startswith("D_") else "FP_GENERIC")
            )
            if fp_type not in library_images:
                library_images[fp_type] = pads

        lines = [
            '(pcb "board"',
            "  (parser",
            '    (string_quote ")',
            "    (space_in_name off)",
            '    (host_cad "KiCad")',
            '    (host_version "8.0")',
            "  )",
            "  (resolution mm 1000000)",
            "  (unit mm)",
            "  (structure",
            "    (boundary",
            f"      (rect boundary 0.0 0.0 {board_width} {board_height})",
            "    )",
            "    (layer F.Cu (type signal) (property (index 0)))",
            "    (layer B.Cu (type signal) (property (index 1)))",
        ]

        obstacles = request.extra_options.get("obstacles", [])
        for obs in obstacles:
            layer_name = "F.Cu" if obs.get("layer", 0) == 0 else "B.Cu"
            lines.append(
                f"    (keepout (rect {layer_name} {obs['x_min']} {obs['y_min']} {obs['x_max']} {obs['y_max']}))"
            )
        lines.append("  )")

        lines.append("  (placement")
        for fp in footprints:
            ref = fp["reference"]
            fp_type = (
                "FP_SW"
                if ref.startswith("SW_")
                else ("FP_D" if ref.startswith("D_") else "FP_GENERIC")
            )
            lines.append(f"    (component {fp_type}")
            lines.append(f"      (place {ref} {fp['x']} {fp['y']} Front {fp['rotation']})")
            lines.append("    )")
        lines.append("  )")

        lines.append("  (library")
        for fp_type, pads in library_images.items():
            lines.append(f"    (image {fp_type}")
            for pad_name, (ox, oy) in pads:
                lines.append(f'      (pin round 1.0 (at {ox} {oy}) (name "{pad_name}"))')
            lines.append("    )")
        lines.append("  )")

        lines.append("  (network")
        for net_name, pin_tuples in request.netlist.items():
            pin_refs = [f"{ref}-{pad}" for ref, pad in pin_tuples]
            class_name = "Signal"
            for pattern, c_name in request.net_classes.items():
                if net_name == pattern:
                    class_name = c_name
                    break
            rule = request.class_rules.get(class_name)
            track_width = rule.track_width if rule else 0.25

            lines.append(f"    (net {net_name}")
            lines.append(f"      (pins {' '.join(pin_refs)})")
            lines.append(f"      (circuit (use_via via) (width {track_width}))")
            lines.append("    )")
        lines.append("  )")

        lines.append(")")
        return "\n".join(lines)

    def parse_ses(self, ses_content: str) -> RoutingResult:
        parsed = parse_sexpr(ses_content)
        traces = []
        vias = []

        def find_block(lst: list[Any], key: str) -> list[Any] | None:
            for item in lst:
                if isinstance(item, list) and len(item) > 0 and item[0] == key:
                    return item
            return None

        routes_block = find_block(parsed, "routes")
        if not routes_block:
            routes_block = self._find_block_recursive(parsed, "routes")

        if routes_block:
            network_block = find_block(routes_block, "network")
            if not network_block:
                network_block = self._find_block_recursive(routes_block, "network")

            if network_block:
                for item in network_block[1:]:
                    if isinstance(item, list) and len(item) > 1 and item[0] == "net":
                        for subitem in item[2:]:
                            if isinstance(subitem, list) and len(subitem) > 0:
                                if subitem[0] == "wire":
                                    path_block = find_block(subitem, "path")
                                    if path_block and len(path_block) >= 5:
                                        layer = path_block[1]
                                        width = float(path_block[2])
                                        coords = []
                                        for pt in path_block[3:]:
                                            if isinstance(pt, list) and len(pt) == 2:
                                                coords.append((float(pt[0]), float(pt[1])))
                                        for k in range(len(coords) - 1):
                                            traces.append(
                                                TraceSegment(
                                                    start=coords[k],
                                                    end=coords[k + 1],
                                                    layer=layer,
                                                    width=width,
                                                )
                                            )
                                elif subitem[0] == "via":
                                    pos = (0.0, 0.0)
                                    layers = ("F.Cu", "B.Cu")
                                    at_block = find_block(subitem, "at")
                                    if at_block and len(at_block) >= 3:
                                        pos = (float(at_block[1]), float(at_block[2]))

                                    layers_block = find_block(subitem, "layers")
                                    if layers_block and len(layers_block) >= 3:
                                        layers = (str(layers_block[1]), str(layers_block[2]))

                                    vias.append(
                                        Via(
                                            position=pos,
                                            drill=0.3,
                                            diameter=0.6,
                                            layers=layers,
                                        )
                                    )

        return RoutingResult(
            traces=traces,
            vias=vias,
            success=len(traces) > 0,
        )

    def _find_block_recursive(self, lst: Any, key: str) -> list[Any] | None:
        if not isinstance(lst, list):
            return None
        if len(lst) > 0 and lst[0] == key:
            return lst
        for item in lst:
            if isinstance(item, list):
                res = self._find_block_recursive(item, key)
                if res:
                    return res
        return None
