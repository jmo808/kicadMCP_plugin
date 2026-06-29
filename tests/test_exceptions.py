from kbd_engine.exceptions import (
    DrcError,
    KbdEngineError,
    ParseError,
    PlacementError,
    RegistryError,
    RouterError,
)


def test_base_exception() -> None:
    exc = KbdEngineError("base error")
    assert str(exc) == "base error"


def test_parse_error() -> None:
    exc = ParseError("Malformed JSON", line=4, column=10)
    assert exc.line == 4
    assert exc.column == 10
    assert "Malformed JSON" in str(exc)
    assert "line 4, column 10" in str(exc)


def test_placement_error() -> None:
    exc = PlacementError("Overlap detected", key_id="SW_0_0", x=19.05, y=0.0)
    assert exc.key_id == "SW_0_0"
    assert exc.x == 19.05
    assert exc.y == 0.0
    assert "Overlap detected" in str(exc)
    assert "SW_0_0" in str(exc)


def test_registry_error() -> None:
    exc = RegistryError("Footprint not found", component_type="switch_custom")
    assert exc.component_type == "switch_custom"
    assert "Footprint not found" in str(exc)
    assert "switch_custom" in str(exc)


def test_drc_error() -> None:
    exc = DrcError("Clearance violation", violation_type="clearance", location=(10.0, 20.0))
    assert exc.violation_type == "clearance"
    assert exc.location == (10.0, 20.0)
    assert "Clearance violation" in str(exc)
    assert "10.0, 20.0" in str(exc)


def test_router_error() -> None:
    exc = RouterError("Unrouted net", net_name="Row0_Col1")
    assert exc.net_name == "Row0_Col1"
    assert "Unrouted net" in str(exc)
    assert "Row0_Col1" in str(exc)
