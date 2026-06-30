

def oz_to_mil(oz: float) -> float:
    """Convert copper weight in oz/ft^2 to thickness in mils.

    1 oz/ft^2 copper thickness is approximately 35 microns (1.378 mils).

    Args:
        oz: Copper weight in ounces.

    Returns:
        Thickness in mils.
    """
    return oz * 1.37795


def calculate_trace_width(
    current: float,
    temp_rise: float,
    copper_weight: float = 1.0,
    is_external: bool = True,
) -> float:
    """Calculate the minimum trace width required per IPC-2152 standard.

    All dimensions and widths are returned in millimeters (mm).

    Args:
        current: Expected current in Amperes. Must be positive.
        temp_rise: Maximum allowable temperature rise in °C. Must be positive.
        copper_weight: Copper thickness weight in oz/ft^2. Defaults to 1.0.
            Must be positive.
        is_external: True if the trace is on an external layer, False if
            internal.

    Returns:
        The calculated minimum trace width in mm.

    Raises:
        ValueError: If any input parameters are non-positive.

    DRC Notes:
        Calculates width according to the IPC-2152 Still Air curve-fit
        relationship. This represents the minimum width for temperature rise
        limits; standard design rules (DRC clearance and net class minimums)
        must still be checked separately.
    """
    if current <= 0:
        raise ValueError("Current must be positive")
    if temp_rise <= 0:
        raise ValueError("Temperature rise must be positive")
    if copper_weight <= 0:
        raise ValueError("Copper weight must be positive")

    # Select coefficients based on layer type
    if is_external:
        k = 0.089
    else:
        k = 0.063

    b = 0.44
    c = 0.725

    # Area (sq mils) = (I / (k * DT^b))^(1 / c)
    area = (current / (k * (temp_rise**b))) ** (1.0 / c)

    # Thickness (mils)
    thickness_mil = oz_to_mil(copper_weight)

    # Width (mils) = Area (sq mils) / Thickness (mils)
    width_mil = area / thickness_mil

    # Width (mm) = Width (mils) * 0.0254
    width_mm = width_mil * 0.0254

    return float(width_mm)
