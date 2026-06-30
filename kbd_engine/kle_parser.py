import json
import math

from kbd_engine.exceptions import ParseError
from kbd_engine.models import Key, KeyMatrix

PITCH = 19.05  # Standard keyboard pitch in mm


def parse_kle_json(kle_str: str) -> KeyMatrix:
    """Parses a KLE JSON string and returns a KeyMatrix.

    Converts coordinates from KLE pitch-based positioning to absolute mm.
    """
    try:
        data = json.loads(kle_str)
    except json.JSONDecodeError as e:
        raise ParseError(f"Invalid JSON syntax: {e}") from e

    if not isinstance(data, list):
        raise ParseError("KLE JSON must be a list of rows")

    keys: list[Key] = []

    # Global rotation/center state in KLE units
    r = 0.0
    rx = 0.0
    ry = 0.0

    # Row/key-relative state
    y = 0.0
    current_y = 0.0

    for row_idx, row in enumerate(data):
        if not isinstance(row, list):
            raise ParseError(f"Row {row_idx} is not a list")

        current_x = rx
        if row_idx == 0:
            current_y = ry
        else:
            current_y += 1.0 + y
            y = 0.0

        w = 1.0
        h = 1.0
        x = 0.0
        key_col_idx = 0

        for item_idx, item in enumerate(row):
            if isinstance(item, dict):
                # Rotation settings
                if "r" in item:
                    r = float(item["r"])
                if "rx" in item:
                    rx = float(item["rx"])
                    current_x = rx
                if "ry" in item:
                    ry = float(item["ry"])
                    current_y = ry

                # Position/dimension settings
                if "x" in item:
                    x += float(item["x"])
                if "y" in item:
                    y_val = float(item["y"])
                    y += y_val
                    current_y += y_val
                if "w" in item:
                    w = float(item["w"])
                if "h" in item:
                    h = float(item["h"])
            elif isinstance(item, str):
                # Calculate absolute layout coordinates before rotation
                abs_x = current_x + x
                abs_y = current_y

                # Apply rotation around center (rx, ry) if r is active
                if r != 0.0:
                    theta_rad = math.radians(r)
                    dx = abs_x - rx
                    dy = abs_y - ry
                    rot_x = dx * math.cos(theta_rad) - dy * math.sin(theta_rad) + rx
                    rot_y = dx * math.sin(theta_rad) + dy * math.cos(theta_rad) + ry
                else:
                    rot_x = abs_x
                    rot_y = abs_y

                # Convert from KLE grid units to absolute millimeters
                mm_x = rot_x * PITCH
                mm_y = rot_y * PITCH

                key = Key(
                    x=mm_x,
                    y=mm_y,
                    width=w,
                    height=h,
                    rotation=r,
                    matrix_row=row_idx,
                    matrix_col=key_col_idx,
                )
                keys.append(key)

                # Move cursor for next key in row
                current_x += x + w
                # Reset transient sizing/spacing parameters
                x = 0.0
                w = 1.0
                h = 1.0
                key_col_idx += 1
            else:
                raise ParseError(f"Unexpected item type in row {row_idx}, item {item_idx}: {item}")

    return KeyMatrix(keys=keys)
