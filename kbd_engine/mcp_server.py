import json
import os
import shutil
from typing import Any

from fastmcp import FastMCP

from kbd_engine.drc import DrcValidator
from kbd_engine.exceptions import KbdEngineError
from kbd_engine.kle_parser import parse_kle_json
from kbd_engine.net_classes import NetClassManager
from kbd_engine.pcbnew_adapter import PcbnewAdapter, apply_net_classes, apply_routing
from kbd_engine.placer import GridPlacer, apply_placement
from kbd_engine.registry import FootprintRegistry
from kbd_engine.routers.freerouting import FreeRoutingRouter
from kbd_engine.routers.quilter import QuilterRouter
from kbd_engine.routers.rust_astar import RustAstarRouter
from kbd_engine.routing_models import RoutingRequest
from kbd_engine.via_inserter import ViaInserter

# Create FastMCP server instance
mcp = FastMCP("kbd_engine")


@mcp.tool()
def preview_layout(layout_json: str, registry_file: str | None = None) -> str:
    """Parses a KLE JSON layout, maps footprints, and computes their placements.

    Returns the calculated coordinates as a JSON string without modifying the board.
    """
    try:
        matrix = parse_kle_json(layout_json)
        registry = FootprintRegistry(registry_file=registry_file)
        placer = GridPlacer()
        result = placer.place(matrix, registry)

        return json.dumps(
            {
                "success": True,
                "placements": result.placements,
            }
        )
    except KbdEngineError as e:
        return json.dumps({"success": False, "error": str(e)})
    except Exception as e:
        return json.dumps({"success": False, "error": f"Unexpected error: {e}"})


@mcp.tool()
def place_layout(layout_json: str, registry_file: str | None = None) -> str:
    """Parses layout, computes placement, runs DRC validation, and applies footprints to the board.

    If DRC validation fails, placement is aborted to prevent board corruption.
    """
    try:
        matrix = parse_kle_json(layout_json)
        registry = FootprintRegistry(registry_file=registry_file)
        placer = GridPlacer()
        result = placer.place(matrix, registry)

        # Run DRC validation first
        validator = DrcValidator()
        drc_errors = validator.validate(result)
        if drc_errors:
            return json.dumps(
                {
                    "success": False,
                    "error": "Design Rule Check (DRC) validation failed. Placement aborted.",
                    "errors": drc_errors,
                }
            )

        # Apply placements to the board
        adapter = PcbnewAdapter()
        apply_placement(result, adapter, dry_run=False)

        return json.dumps(
            {
                "success": True,
                "message": f"Placed {len(result.placements)} components successfully on the board.",
            }
        )
    except KbdEngineError as e:
        return json.dumps({"success": False, "error": str(e)})
    except Exception as e:
        return json.dumps({"success": False, "error": f"Unexpected error: {e}"})


@mcp.tool()
def validate_layout_drc(layout_json: str, clearance_threshold_mm: float = 0.5) -> str:
    """Runs coordinate-based clearance and overlap DRC validation on a proposed layout.

    Returns a list of any violations found.
    """
    try:
        matrix = parse_kle_json(layout_json)
        registry = FootprintRegistry()
        placer = GridPlacer()
        result = placer.place(matrix, registry)

        validator = DrcValidator(clearance_threshold_mm=clearance_threshold_mm)
        drc_errors = validator.validate(result)

        return json.dumps(
            {
                "success": True,
                "errors": drc_errors,
            }
        )
    except KbdEngineError as e:
        return json.dumps({"success": False, "error": str(e)})
    except Exception as e:
        return json.dumps({"success": False, "error": f"Unexpected error: {e}"})


@mcp.tool()
def get_routers() -> str:
    """List available routing backends and their installation/availability status."""
    java_available = shutil.which("java") is not None
    # Check for Quilter key
    quilter_key = os.environ.get("QUILTER_API_KEY")

    # Check for FreeRouting jar detection
    freerouting_available = java_available
    if freerouting_available:
        try:
            # Check if jar exists or path exists
            freerouting_available = FreeRoutingRouter()._detect_jar() is not None
        except Exception:
            freerouting_available = False

    routers = [
        {"name": "rust_astar", "status": "available", "type": "internal"},
        {
            "name": "freerouting",
            "status": "available" if freerouting_available else "unavailable",
            "type": "external",
        },
        {
            "name": "quilter",
            "status": "available" if quilter_key else "unavailable",
            "type": "api",
        },
    ]
    return json.dumps({"success": True, "routers": routers})


@mcp.tool()
def set_net_classes(classes_json: str, config_path: str = "./net_classes_config.json") -> str:
    """Configure net class rules and regular expression patterns for matching net names.

    Saves configuration to config_path.
    """
    try:
        data = json.loads(classes_json)
        if "classes" not in data or "patterns" not in data:
            raise ValueError("classes_json must contain 'classes' and 'patterns' keys")

        with open(config_path, "w") as f:
            json.dump(data, f, indent=2)

        return json.dumps(
            {
                "success": True,
                "message": f"Net classes saved successfully to {config_path}",
            }
        )
    except Exception as e:
        return json.dumps({"success": False, "error": f"Failed to set net classes: {e}"})


@mcp.tool()
def route(
    board_file: str,
    netlist_json: str,
    router_name: str = "rust_astar",
    router_options_json: str | None = None,
    net_classes_config_path: str | None = None,
    dry_run: bool = False,
) -> str:
    """Route traces and vias on the placed board using the selected router backend.

    Applies net classes matching, via insertion, and saves the routed layout (unless dry_run=True).
    """
    try:
        if not os.path.exists(board_file):
            return json.dumps({"success": False, "error": f"Board file not found: {board_file}"})

        # 1. Parse inputs
        netlist = json.loads(netlist_json)
        options = json.loads(router_options_json) if router_options_json else {}

        # 2. Match and load net classes rules
        if net_classes_config_path and os.path.exists(net_classes_config_path):
            ncm = NetClassManager(config_path=net_classes_config_path)
        else:
            # Fall back to default
            ncm = NetClassManager()

        # Map each net to its rule
        net_classes = {}
        class_rules = {}
        for net_name in netlist.keys():
            cls_name = ncm.match_net(net_name)
            net_classes[net_name] = cls_name
            if cls_name in ncm.classes:
                class_rules[cls_name] = ncm.classes[cls_name]

        # 3. Create RoutingRequest
        request = RoutingRequest(
            board_file=board_file,
            netlist=netlist,
            net_classes=net_classes,
            class_rules=class_rules,
        )

        # 4. Instantiate Router
        if router_name == "rust_astar":
            router: Any = RustAstarRouter(
                mode=options.get("mode", "pyo3"),
                server_url=options.get("server_url", "http://127.0.0.1:8080/route"),
            )
        elif router_name == "freerouting":
            router = FreeRoutingRouter(
                jar_path=options.get("jar_path"),
                timeout=options.get("timeout", 60),
            )
        elif router_name == "quilter":
            api_key = options.get("api_key") or os.environ.get("QUILTER_API_KEY")
            if not api_key:
                return json.dumps(
                    {
                        "success": False,
                        "error": "Quilter API key must be provided in options or environment variable QUILTER_API_KEY",
                    }
                )
            router = QuilterRouter(
                api_key=api_key,
                api_url=options.get("api_url", "https://api.quilter.ai/v1"),
                timeout=options.get("timeout", 120),
                poll_interval=options.get("poll_interval", 2),
            )
        else:
            return json.dumps({"success": False, "error": f"Unknown router: {router_name}"})

        # 5. Route the board
        result = router.route(request)

        # 6. Apply via insertion engine
        via_inserter = ViaInserter()
        result_with_vias = via_inserter.insert_vias(result)

        # 7. Apply to board representation
        adapter = PcbnewAdapter()
        adapter.load(board_file)
        apply_routing(result_with_vias, adapter, dry_run=dry_run)
        apply_net_classes(ncm, adapter)

        if not dry_run:
            adapter.save(board_file)

        return json.dumps(
            {
                "success": result_with_vias.success,
                "traces_count": len(result_with_vias.traces),
                "vias_count": len(result_with_vias.vias),
                "unrouted_nets": result_with_vias.unrouted_nets,
                "diagnostics": result_with_vias.diagnostics,
            }
        )
    except KbdEngineError as e:
        return json.dumps({"success": False, "error": str(e)})
    except Exception as e:
        return json.dumps({"success": False, "error": f"Unexpected error: {e}"})


@mcp.tool()
def route_preview(
    board_file: str,
    netlist_json: str,
    router_name: str = "rust_astar",
    router_options_json: str | None = None,
    net_classes_config_path: str | None = None,
) -> str:
    """Route traces and vias, returning detailed paths and locations in JSON format without modifying the board."""
    try:
        if not os.path.exists(board_file):
            return json.dumps({"success": False, "error": f"Board file not found: {board_file}"})

        # 1. Parse inputs
        netlist = json.loads(netlist_json)
        options = json.loads(router_options_json) if router_options_json else {}

        # 2. Match and load net classes rules
        if net_classes_config_path and os.path.exists(net_classes_config_path):
            ncm = NetClassManager(config_path=net_classes_config_path)
        else:
            ncm = NetClassManager()

        # Map each net to its rule
        net_classes = {}
        class_rules = {}
        for net_name in netlist.keys():
            cls_name = ncm.match_net(net_name)
            net_classes[net_name] = cls_name
            if cls_name in ncm.classes:
                class_rules[cls_name] = ncm.classes[cls_name]

        # 3. Create RoutingRequest
        request = RoutingRequest(
            board_file=board_file,
            netlist=netlist,
            net_classes=net_classes,
            class_rules=class_rules,
        )

        # 4. Instantiate Router
        if router_name == "rust_astar":
            router: Any = RustAstarRouter(
                mode=options.get("mode", "pyo3"),
                server_url=options.get("server_url", "http://127.0.0.1:8080/route"),
            )
        elif router_name == "freerouting":
            router = FreeRoutingRouter(
                jar_path=options.get("jar_path"),
                timeout=options.get("timeout", 60),
            )
        elif router_name == "quilter":
            api_key = options.get("api_key") or os.environ.get("QUILTER_API_KEY")
            if not api_key:
                return json.dumps(
                    {
                        "success": False,
                        "error": "Quilter API key must be provided in options or environment variable QUILTER_API_KEY",
                    }
                )
            router = QuilterRouter(
                api_key=api_key,
                api_url=options.get("api_url", "https://api.quilter.ai/v1"),
                timeout=options.get("timeout", 120),
                poll_interval=options.get("poll_interval", 2),
            )
        else:
            return json.dumps({"success": False, "error": f"Unknown router: {router_name}"})

        # 5. Route
        result = router.route(request)

        # 6. Apply via insertion engine
        via_inserter = ViaInserter()
        result_with_vias = via_inserter.insert_vias(result)

        # Map to structured paths
        traces_list = [
            {
                "start": trace.start,
                "end": trace.end,
                "layer": trace.layer,
                "width": trace.width,
            }
            for trace in result_with_vias.traces
        ]

        vias_list = [
            {
                "position": via.position,
                "drill": via.drill,
                "diameter": via.diameter,
                "layers": list(via.layers),
            }
            for via in result_with_vias.vias
        ]

        return json.dumps(
            {
                "success": result_with_vias.success,
                "traces": traces_list,
                "vias": vias_list,
                "unrouted_nets": result_with_vias.unrouted_nets,
            }
        )
    except KbdEngineError as e:
        return json.dumps({"success": False, "error": str(e)})
    except Exception as e:
        return json.dumps({"success": False, "error": f"Unexpected error: {e}"})
