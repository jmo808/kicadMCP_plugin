from pathlib import Path

from kbd_engine.pcbnew_adapter import PcbnewAdapter


def test_adapter_board_lifecycle(tmp_path: Path) -> None:
    filepath = str(tmp_path / "test.kicad_pcb")
    adapter = PcbnewAdapter()

    # Load / Save
    assert adapter.board is not None
    adapter.save(filepath)

    new_adapter = PcbnewAdapter()
    new_adapter.load(filepath)
    assert new_adapter.board is not None


def test_add_footprint() -> None:
    adapter = PcbnewAdapter()
    # Let's add a switch footprint. We expect coordinates in mm (e.g., 19.05, 0.0)
    # Rotation in degrees (e.g. 90.0)
    fp = adapter.add_footprint(
        library_path="kbd_custom",
        footprint_name="SW_Cherry_MX",
        reference="SW1",
        x=19.05,
        y=0.0,
        rotation=90.0,
    )

    assert fp is not None
    footprints = adapter.get_footprints()
    assert len(footprints) == 1
    assert footprints[0]["reference"] == "SW1"
    # KiCad internal units check (1 mm = 1,000,000 IU/nanometers)
    assert footprints[0]["x"] == 19.05
    assert footprints[0]["y"] == 0.0
    assert footprints[0]["rotation"] == 90.0


def test_add_track() -> None:
    adapter = PcbnewAdapter()
    # Add a track from (0, 0) to (19.05, 0) on F.Cu layer with width 0.25mm
    track = adapter.add_track(start_x=0.0, start_y=0.0, end_x=19.05, end_y=0.0, layer="F.Cu", width=0.25)
    assert track is not None

    # Verify track properties via mock
    assert track.start.x == 0
    assert track.start.y == 0
    assert track.end.x == 19050000  # 19.05 mm in nanometers
    assert track.end.y == 0


def test_net_class_methods() -> None:
    adapter = PcbnewAdapter()
    adapter.create_net_class(
        name="Power",
        track_width=0.5,
        clearance=0.25,
        via_diameter=0.8,
        via_drill=0.4,
    )
    assert "Power" in adapter.board.GetNetClasses().classes

    adapter.set_net_class("VCC", "Power")
    assert adapter.board.GetNetSettings().assignments["VCC"] == "Power"


def test_apply_routing() -> None:
    from kbd_engine.pcbnew_adapter import apply_routing
    from kbd_engine.routing_models import RoutingResult, TraceSegment, Via

    adapter = PcbnewAdapter()
    result = RoutingResult(
        traces=[TraceSegment(start=(0.0, 0.0), end=(10.0, 10.0), layer="F.Cu", width=0.25)],
        vias=[Via(position=(10.0, 10.0), drill=0.3, diameter=0.6, layers=("F.Cu", "B.Cu"))],
        success=True,
    )

    # 1. Dry run mode: board is not modified
    dry_result = apply_routing(result, adapter, dry_run=True)
    assert dry_result == result
    assert len(adapter.board.tracks) == 0

    # 2. Normal mode: board is modified
    normal_result = apply_routing(result, adapter, dry_run=False)
    assert normal_result == result
    assert len(adapter.board.tracks) == 2  # 1 track + 1 via (since via inherits from track)


def test_apply_net_classes() -> None:
    from kbd_engine.net_classes import NetClassManager
    from kbd_engine.pcbnew_adapter import apply_net_classes

    adapter = PcbnewAdapter()
    # Add a footprint with pads to generate nets on mock board
    fp = adapter.add_footprint(
        library_path="kbd_custom",
        footprint_name="SW_Cherry_MX",
        reference="SW_0_0",
        x=10.0,
        y=10.0,
        rotation=0.0,
    )
    # Set net names on footprint pads
    pads = fp.GetPads() if hasattr(fp, "GetPads") else fp.Pads()
    pads[0].SetNetname("ROW_0")
    pads[1].SetNetname("COL_0")

    # Create manager with default rules
    manager = NetClassManager()

    apply_net_classes(manager, adapter)

    # Verify assignments
    assignments = adapter.board.GetNetSettings().assignments
    assert assignments.get("ROW_0") == "MatrixRow"
    assert assignments.get("COL_0") == "MatrixCol"

