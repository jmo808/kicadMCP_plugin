import pytest

from kbd_engine.exceptions import PlacementError
from kbd_engine.models import PlacementResult
from kbd_engine.pcbnew_adapter import PcbnewAdapter
from kbd_engine.placer import apply_placement


def test_apply_placement_dry_run() -> None:
    adapter = PcbnewAdapter()
    result = PlacementResult(
        placements={"SW_0_0": {"x": 0.0, "y": 0.0, "rotation": 0.0, "footprint": "lib:footprint"}}, valid=True
    )

    # In dry-run, no footprints should actually be added to the board
    apply_placement(result, adapter, dry_run=True)
    assert len(adapter.get_footprints()) == 0


def test_apply_placement_real() -> None:
    adapter = PcbnewAdapter()
    result = PlacementResult(
        placements={
            "SW_0_0": {
                "x": 19.05,
                "y": 0.0,
                "rotation": 45.0,
                "footprint": "Button_Switch_Keyboard:SW_Cherry_MX_1.00u_PCB",
            }
        },
        valid=True,
    )

    apply_placement(result, adapter, dry_run=False)
    fps = adapter.get_footprints()
    assert len(fps) == 1
    assert fps[0]["reference"] == "SW_0_0"
    assert fps[0]["x"] == 19.05
    assert fps[0]["y"] == 0.0
    assert fps[0]["rotation"] == 45.0


def test_apply_placement_invalid_footprint_format() -> None:
    adapter = PcbnewAdapter()
    result = PlacementResult(
        placements={
            # Missing library prefix (no colon)
            "SW_0_0": {"x": 0.0, "y": 0.0, "rotation": 0.0, "footprint": "SW_Cherry_MX_1.00u_PCB"}
        },
        valid=True,
    )

    with pytest.raises(PlacementError) as exc_info:
        apply_placement(result, adapter, dry_run=False)
    assert "format" in str(exc_info.value).lower()
