import math
from typing import Any

from kbd_engine.models import PlacementResult


class DrcValidator:
    """Validator that performs Design Rule Checks (DRC) on component placements."""

    def __init__(self, clearance_threshold_mm: float = 0.5) -> None:
        self.clearance_threshold = clearance_threshold_mm

    def _get_radius(self, ref: str) -> float:
        """Determines approximate bounding courtyard radius in mm based on component type."""
        if ref.startswith("SW"):
            return 9.0  # ~18mm diameter switch box
        elif ref.startswith("D"):
            return 1.0  # SOD-123 diode
        elif ref.startswith("C"):
            return 1.0  # 0805 capacitor
        return 1.0

    def validate(self, result: PlacementResult, adapter: Any = None) -> list[str]:
        """Validates all placed components for physical overlap and clearance violations.

        Runs purely on coordinates, allowing dry-run validation without writing to a board.
        """
        errors: list[str] = []
        items = list(result.placements.items())

        for i in range(len(items)):
            ref_a, data_a = items[i]
            x_a, y_a = data_a["x"], data_a["y"]
            r_a = self._get_radius(ref_a)

            for j in range(i + 1, len(items)):
                ref_b, data_b = items[j]
                x_b, y_b = data_b["x"], data_b["y"]
                r_b = self._get_radius(ref_b)

                dist = math.sqrt((x_a - x_b) ** 2 + (y_a - y_b) ** 2)
                min_allowed_dist = r_a + r_b + self.clearance_threshold

                # 1. Check for physical overlap/collision
                if dist < (r_a + r_b):
                    errors.append(
                        f"Physical collision (clearance violation) between {ref_a} and {ref_b}: "
                        f"distance {dist:.2f} mm < physical limit {r_a + r_b:.2f} mm"
                    )
                # 2. Check for clearance violation
                elif dist < min_allowed_dist:
                    errors.append(
                        f"Courtyard clearance violation between {ref_a} and {ref_b}: "
                        f"distance {dist:.2f} mm < threshold {min_allowed_dist:.2f} mm"
                    )

        return errors
