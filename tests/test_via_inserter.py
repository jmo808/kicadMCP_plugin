from kbd_engine.routing_models import RoutingResult, TraceSegment, Via
from kbd_engine.via_inserter import ViaInserter


def test_via_inserter_basic() -> None:
    traces = [
        TraceSegment(start=(0.0, 0.0), end=(10.0, 10.0), layer="F.Cu", width=0.25),
        TraceSegment(start=(10.0, 10.0), end=(20.0, 10.0), layer="B.Cu", width=0.25),
    ]
    result = RoutingResult(traces=traces, vias=[], success=True)

    inserter = ViaInserter(drill=0.4, diameter=0.8)
    routed = inserter.insert_vias(result)

    assert len(routed.vias) == 1
    v = routed.vias[0]
    assert v.position == (10.0, 10.0)
    assert v.drill == 0.4
    assert v.diameter == 0.8
    assert v.layers == ("F.Cu", "B.Cu")


def test_via_inserter_no_transition() -> None:
    traces = [
        TraceSegment(start=(0.0, 0.0), end=(10.0, 10.0), layer="F.Cu", width=0.25),
        TraceSegment(start=(10.0, 10.0), end=(20.0, 10.0), layer="F.Cu", width=0.25),
    ]
    result = RoutingResult(traces=traces, vias=[], success=True)

    inserter = ViaInserter()
    routed = inserter.insert_vias(result)

    assert len(routed.vias) == 0


def test_via_inserter_merge_nearby() -> None:
    traces = [
        TraceSegment(start=(0.0, 0.0), end=(10.0, 10.0), layer="F.Cu", width=0.25),
        TraceSegment(start=(10.0, 10.0), end=(20.0, 10.0), layer="B.Cu", width=0.25),
        TraceSegment(start=(5.0, 5.0), end=(10.02, 10.0), layer="F.Cu", width=0.25),
        TraceSegment(start=(10.02, 10.0), end=(20.0, 5.0), layer="B.Cu", width=0.25),
    ]
    result = RoutingResult(traces=traces, vias=[], success=True)

    # With 0.1mm tolerance, (10,10) and (10.02, 10) are merged
    inserter = ViaInserter(merge_tolerance=0.1)
    routed = inserter.insert_vias(result)

    assert len(routed.vias) == 1
    # Centroid: (10.01, 10.0)
    assert routed.vias[0].position == (10.01, 10.0)


def test_via_inserter_deduplicate_existing() -> None:
    traces = [
        TraceSegment(start=(0.0, 0.0), end=(10.0, 10.0), layer="F.Cu", width=0.25),
        TraceSegment(start=(10.0, 10.0), end=(20.0, 10.0), layer="B.Cu", width=0.25),
    ]
    existing_via = Via(position=(10.0, 10.0), drill=0.3, diameter=0.6, layers=("F.Cu", "B.Cu"))
    result = RoutingResult(traces=traces, vias=[existing_via], success=True)

    inserter = ViaInserter()
    routed = inserter.insert_vias(result)

    assert len(routed.vias) == 1
    assert routed.vias[0] == existing_via
