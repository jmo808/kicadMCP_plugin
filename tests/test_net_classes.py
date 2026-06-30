import json

from kbd_engine.net_classes import NetClassManager
from kbd_engine.pcbnew_adapter import PcbnewAdapter


def test_default_net_classes() -> None:
    manager = NetClassManager()
    assert "MatrixRow" in manager.classes
    assert "MatrixCol" in manager.classes
    assert "Power" in manager.classes
    assert "USB" in manager.classes
    assert "Signal" in manager.classes

    power = manager.classes["Power"]
    assert power.track_width == 0.5
    assert power.clearance == 0.25
    assert power.via_diameter == 0.8
    assert power.via_drill == 0.4


def test_pattern_matching() -> None:
    manager = NetClassManager()
    assert manager.match_net("ROW_0") == "MatrixRow"
    assert manager.match_net("COL_3") == "MatrixCol"
    assert manager.match_net("VCC") == "Power"
    assert manager.match_net("GND") == "Power"
    assert manager.match_net("+5V") == "Power"
    assert manager.match_net("USB_D+") == "USB"
    assert manager.match_net("D-") == "USB"
    assert manager.match_net("MCU_RESET") == "Signal"


def test_custom_net_classes_json(tmp_path) -> None:
    custom_rules = {
        "classes": {
            "Power": {
                "track_width": 0.8,
                "clearance": 0.3,
                "via_diameter": 1.0,
                "via_drill": 0.5
            },
            "RF": {
                "track_width": 0.6,
                "clearance": 0.5,
                "via_diameter": 0.8,
                "via_drill": 0.4
            }
        },
        "patterns": {
            "RF_.*": "RF",
            "VDD.*": "Power"
        }
    }
    config_file = tmp_path / "custom_rules.json"
    with open(config_file, "w") as f:
        json.dump(custom_rules, f)

    manager = NetClassManager(str(config_file))
    assert manager.classes["Power"].track_width == 0.8
    assert manager.classes["RF"].track_width == 0.6
    assert manager.match_net("RF_ANTENNA") == "RF"
    assert manager.match_net("VDD") == "Power"
    # Defaults should still exist if not overwritten, but wait: does custom json replace or extend?
    # Let's say it extends/overwrites.
    assert "MatrixRow" in manager.classes


def test_apply_to_board() -> None:
    adapter = PcbnewAdapter()
    manager = NetClassManager()
    net_names = ["ROW_0", "COL_0", "GND", "USB_D-", "RESET"]
    manager.apply_to_board(adapter, net_names)

    # Verify net classes are created on mock board
    classes = adapter.board.GetNetClasses().classes
    assert "MatrixRow" in classes
    assert "MatrixCol" in classes
    assert "Power" in classes
    assert "USB" in classes
    assert "Signal" in classes

    power_class = classes["Power"]
    assert power_class.track_width == int(0.5 * 1000000)
    assert power_class.clearance == int(0.25 * 1000000)
    assert power_class.via_dia == int(0.8 * 1000000)
    assert power_class.via_drill == int(0.4 * 1000000)

    # Verify assignments
    assignments = adapter.board.GetNetSettings().assignments
    assert assignments["ROW_0"] == "MatrixRow"
    assert assignments["COL_0"] == "MatrixCol"
    assert assignments["GND"] == "Power"
    assert assignments["USB_D-"] == "USB"
    assert assignments["RESET"] == "Signal"
