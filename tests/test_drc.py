from kbd_engine.drc import DrcValidator
from kbd_engine.models import PlacementResult


def test_drc_validation_valid_placement() -> None:
    # 2 switches separated by 19.05 mm (standard spacing)
    placements = {
        "SW_0_0": {"x": 0.0, "y": 0.0, "rotation": 0.0, "footprint": "lib:SW_Cherry_MX"},
        "SW_0_1": {"x": 19.05, "y": 0.0, "rotation": 0.0, "footprint": "lib:SW_Cherry_MX"},
    }
    result = PlacementResult(placements=placements, valid=True)
    validator = DrcValidator(clearance_threshold_mm=0.5)

    errors = validator.validate(result)
    assert len(errors) == 0


def test_drc_validation_overlapping_footprints() -> None:
    # 2 switches separated by only 5 mm (collision!)
    placements = {
        "SW_0_0": {"x": 0.0, "y": 0.0, "rotation": 0.0, "footprint": "lib:SW_Cherry_MX"},
        "SW_0_1": {"x": 5.0, "y": 0.0, "rotation": 0.0, "footprint": "lib:SW_Cherry_MX"},
    }
    result = PlacementResult(placements=placements, valid=True)
    validator = DrcValidator(clearance_threshold_mm=0.5)

    errors = validator.validate(result)
    assert len(errors) > 0
    assert any("collision" in err.lower() or "clearance" in err.lower() for err in errors)
    assert any("SW_0_0" in err and "SW_0_1" in err for err in errors)


def test_drc_validation_clearance_violation() -> None:
    # A switch (radius ~9mm) and a diode (radius ~1mm) at (0, 9.5) -> distance is 9.5mm.
    # Radius sum is 10mm -> 9.5mm < 10mm + 0.5mm clearance threshold -> violation!
    placements = {
        "SW_0_0": {"x": 0.0, "y": 0.0, "rotation": 0.0, "footprint": "lib:SW_Cherry_MX"},
        "D_0_1": {"x": 0.0, "y": 9.5, "rotation": 0.0, "footprint": "lib:D_SOD-123"},
    }
    result = PlacementResult(placements=placements, valid=True)
    validator = DrcValidator(clearance_threshold_mm=1.0)

    errors = validator.validate(result)
    assert len(errors) > 0
    assert any("clearance" in err.lower() for err in errors)
