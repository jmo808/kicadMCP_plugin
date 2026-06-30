import json
from typing import Any
from fastmcp import FastMCP

from kbd_engine.exceptions import KbdEngineError
from kbd_engine.kle_parser import parse_kle_json
from kbd_engine.registry import FootprintRegistry
from kbd_engine.placer import GridPlacer, apply_placement
from kbd_engine.drc import DrcValidator
from kbd_engine.pcbnew_adapter import PcbnewAdapter

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
