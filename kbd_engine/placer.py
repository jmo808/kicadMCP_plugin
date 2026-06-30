import math
from typing import Any

from kbd_engine.exceptions import PlacementError
from kbd_engine.models import KeyMatrix, PlacementResult
from kbd_engine.registry import FootprintRegistry


class GridPlacer:
    """Calculates physical component coordinates (switches, diodes, capacitors) from a KeyMatrix."""

    def __init__(self, diode_offset_y: float = 5.0, capacitor_offset_x: float = 3.0) -> None:
        self.diode_offset_y = diode_offset_y
        self.capacitor_offset_x = capacitor_offset_x

    def place(self, key_matrix: KeyMatrix, registry: FootprintRegistry) -> PlacementResult:
        """Places components for all keys in the matrix.

        Applies rotation transformation to offsets for secondary components (diodes, capacitors)
        so they remain correctly positioned relative to each key switch.
        """
        placements: dict[str, dict[str, Any]] = {}

        for k in key_matrix.keys:
            # Determine reference designator suffix
            if k.matrix_row is not None and k.matrix_col is not None:
                suffix = f"{k.matrix_row}_{k.matrix_col}"
            else:
                suffix = f"{k.x}_{k.y}"

            rad = math.radians(k.rotation)

            # 1. Switch placement (placed exactly at key center)
            sw_ref = f"SW_{suffix}"
            placements[sw_ref] = {
                "x": k.x,
                "y": k.y,
                "rotation": k.rotation,
                "footprint": registry.resolve("switch", key_id=k.logical_key_id),
            }

            # 2. Diode placement (default offset below the switch, rotated with the switch)
            d_ref = f"D_{suffix}"
            rot_dx = -self.diode_offset_y * math.sin(rad)
            rot_dy = self.diode_offset_y * math.cos(rad)
            placements[d_ref] = {
                "x": k.x + rot_dx,
                "y": k.y + rot_dy,
                "rotation": k.rotation,
                "footprint": registry.resolve("diode", key_id=k.logical_key_id),
            }

            # 3. Capacitor placement (default offset to the right of the switch, rotated with the switch)
            c_ref = f"C_{suffix}"
            rot_cx = self.capacitor_offset_x * math.cos(rad)
            rot_cy = self.capacitor_offset_x * math.sin(rad)
            placements[c_ref] = {
                "x": k.x + rot_cx,
                "y": k.y + rot_cy,
                "rotation": k.rotation,
                "footprint": registry.resolve("capacitor", key_id=k.logical_key_id),
            }

        return PlacementResult(placements=placements, valid=True)


def apply_placement(result: PlacementResult, adapter: Any, dry_run: bool = False) -> None:
    """Applies the placements from a PlacementResult onto a KiCad board using the adapter.

    If dry_run is True, no footprint placing changes are written to the board.
    """
    if dry_run:
        return

    for ref, data in result.placements.items():
        footprint_str = data["footprint"]
        if ":" not in footprint_str:
            raise PlacementError(
                f"Footprint '{footprint_str}' for component '{ref}' does not follow the "
                "required 'Library_Name:Footprint_Name' format.",
                key_id=ref,
                x=data["x"],
                y=data["y"],
            )
        lib_path, fp_name = footprint_str.split(":", 1)
        adapter.add_footprint(
            library_path=lib_path,
            footprint_name=fp_name,
            reference=ref,
            x=data["x"],
            y=data["y"],
            rotation=data["rotation"],
        )
