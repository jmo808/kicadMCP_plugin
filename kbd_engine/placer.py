import math
from typing import Any

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
