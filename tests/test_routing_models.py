import pytest

from kbd_engine.routing_models import (
    NetClass,
    RoutingRequest,
    RoutingResult,
    TraceSegment,
    Via,
)


def test_net_class_creation_and_immutability() -> None:
    # Test valid creation
    nc = NetClass(name="Power", track_width=0.5, clearance=0.25, via_diameter=0.8, via_drill=0.4)
    assert nc.name == "Power"
    assert nc.track_width == 0.5
    assert nc.clearance == 0.25
    assert nc.via_diameter == 0.8
    assert nc.via_drill == 0.4

    # Test defaults
    default_nc = NetClass(name="Default")
    assert default_nc.track_width == 0.2
    assert default_nc.clearance == 0.2
    assert default_nc.via_diameter == 0.6
    assert default_nc.via_drill == 0.3

    # Test immutability
    with pytest.raises(AttributeError):
        nc.track_width = 0.8  # type: ignore[misc]


def test_trace_segment_and_via() -> None:
    segment = TraceSegment(start=(0.0, 0.0), end=(10.0, 0.0), layer="F.Cu", width=0.2)
    assert segment.start == (0.0, 0.0)
    assert segment.end == (10.0, 0.0)
    assert segment.layer == "F.Cu"
    assert segment.width == 0.2

    # Immutability
    with pytest.raises(AttributeError):
        segment.width = 0.5  # type: ignore[misc]

    via = Via(position=(5.0, 5.0), drill=0.3, diameter=0.6, layers=("F.Cu", "B.Cu"))
    assert via.position == (5.0, 5.0)
    assert via.drill == 0.3
    assert via.diameter == 0.6
    assert via.layers == ("F.Cu", "B.Cu")

    with pytest.raises(AttributeError):
        via.drill = 0.4  # type: ignore[misc]


def test_routing_request() -> None:
    netlist = {
        "ROW_0": [("SW_0_0", "2"), ("D_0_0", "1")],
        "COL_0": [("SW_0_0", "1"), ("SW_1_0", "1")],
    }
    net_classes = {
        "ROW_0": "MatrixRow",
        "COL_0": "MatrixCol",
    }
    class_rules = {
        "MatrixRow": NetClass(name="MatrixRow", track_width=0.2),
        "MatrixCol": NetClass(name="MatrixCol", track_width=0.2),
    }
    request = RoutingRequest(
        board_file="test.kicad_pcb",
        netlist=netlist,
        net_classes=net_classes,
        class_rules=class_rules,
        router="rust_astar",
        grid_pitch=0.5,
    )
    assert request.board_file == "test.kicad_pcb"
    assert request.netlist == netlist
    assert request.net_classes == net_classes
    assert request.class_rules == class_rules
    assert request.router == "rust_astar"
    assert request.grid_pitch == 0.5


def test_routing_result() -> None:
    traces = [
        TraceSegment(start=(0.0, 0.0), end=(5.0, 0.0), layer="F.Cu", width=0.2),
        TraceSegment(start=(5.0, 0.0), end=(5.0, 5.0), layer="B.Cu", width=0.2),
    ]
    vias = [
        Via(position=(5.0, 0.0), drill=0.3, diameter=0.6, layers=("F.Cu", "B.Cu")),
    ]
    result = RoutingResult(
        traces=traces,
        vias=vias,
        unrouted_nets=["USB_D+", "USB_D-"],
        success=False,
        diagnostics="Failed to route USB differential pair",
    )
    assert result.traces == traces
    assert result.vias == vias
    assert result.unrouted_nets == ["USB_D+", "USB_D-"]
    assert result.success is False
    assert result.diagnostics == "Failed to route USB differential pair"
