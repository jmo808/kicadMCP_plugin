import pytest

from kbd_engine.ipc2152 import calculate_trace_width, oz_to_mil


def test_oz_to_mil() -> None:
    # 1 oz copper should be ~1.378 mils (35 microns)
    assert pytest.approx(oz_to_mil(1.0), rel=1e-3) == 1.378
    assert pytest.approx(oz_to_mil(0.5), rel=1e-3) == 0.689
    assert pytest.approx(oz_to_mil(2.0), rel=1e-3) == 2.756


def test_calculate_trace_width_external() -> None:
    # Test calculation for external trace:
    # Current = 1A, Temp Rise = 10°C, Copper Weight = 1oz (1.378 mils)
    # Area (sq mil) = (1.0 / (0.089 * 10^0.44))^(1 / 0.725)
    # Area = (1.0 / (0.089 * 2.7542))^(1.3793) = (1.0 / 0.2451)^1.3793 = 4.0796^1.3793 = 6.942 sq mil
    # Width (mil) = 6.942 / 1.378 = 5.038 mils
    # Width (mm) = 5.038 * 0.0254 = 0.1279 mm
    width = calculate_trace_width(
        current=1.0,
        temp_rise=10.0,
        copper_weight=1.0,
        is_external=True
    )
    assert pytest.approx(width, rel=1e-2) == 0.128


def test_calculate_trace_width_internal() -> None:
    # Test calculation for internal trace:
    # Current = 1A, Temp Rise = 10°C, Copper Weight = 1oz (1.378 mils)
    # Area (sq mil) = (1.0 / (0.063 * 10^0.44))^(1 / 0.725)
    # Area = (1.0 / (0.063 * 2.7542))^(1.3793) = (1.0 / 0.1735)^1.3793 = 5.763^1.3793 = 11.085 sq mil
    # Width (mil) = 11.085 / 1.378 = 8.044 mils
    # Width (mm) = 8.044 * 0.0254 = 0.2043 mm
    width = calculate_trace_width(
        current=1.0,
        temp_rise=10.0,
        copper_weight=1.0,
        is_external=False
    )
    assert pytest.approx(width, rel=1e-2) == 0.206


def test_calculate_trace_width_edge_cases() -> None:
    # Current = 0 should raise ValueError or return 0? Let's check requirements:
    # "edge cases (zero current, negative values raise errors)"
    with pytest.raises(ValueError, match="Current must be positive"):
        calculate_trace_width(0.0, 10.0, 1.0)

    with pytest.raises(ValueError, match="Current must be positive"):
        calculate_trace_width(-1.0, 10.0, 1.0)

    with pytest.raises(ValueError, match="Temperature rise must be positive"):
        calculate_trace_width(1.0, 0.0, 1.0)

    with pytest.raises(ValueError, match="Copper weight must be positive"):
        calculate_trace_width(1.0, 10.0, 0.0)
