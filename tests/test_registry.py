import json
from pathlib import Path

import pytest

from kbd_engine.exceptions import RegistryError
from kbd_engine.registry import FootprintRegistry


def test_default_footprint_resolution() -> None:
    registry = FootprintRegistry()
    assert registry.resolve("switch") == "Button_Switch_Keyboard:SW_Cherry_MX_1.00u_PCB"
    assert registry.resolve("diode") == "Diode_SMD:D_SOD-123"
    assert registry.resolve("capacitor") == "Capacitor_SMD:C_0805_2012Metric"


def test_unknown_component_type() -> None:
    registry = FootprintRegistry()
    with pytest.raises(RegistryError) as exc_info:
        registry.resolve("unknown_comp")
    assert "unknown_comp" in str(exc_info.value)


def test_custom_registry_loading(tmp_path: Path) -> None:
    custom_data = {
        "switch": "custom_lib:SW_Hotswap",
        "oled": "custom_lib:OLED_0.91",
    }
    config_file = tmp_path / "custom_registry.json"
    with open(config_file, "w") as f:
        json.dump(custom_data, f)

    registry = FootprintRegistry(registry_file=str(config_file))
    # Check override
    assert registry.resolve("switch") == "custom_lib:SW_Hotswap"
    # Check new registration
    assert registry.resolve("oled") == "custom_lib:OLED_0.91"
    # Check default still exists if not overridden
    assert registry.resolve("diode") == "Diode_SMD:D_SOD-123"


def test_per_key_override() -> None:
    registry = FootprintRegistry()
    custom_data = {"overrides": {"SW_0_5": {"switch": "Button_Switch_Keyboard:SW_Cherry_MX_6.25u_PCB"}}}
    registry.load_mappings(custom_data)

    # Default switch
    assert registry.resolve("switch") == "Button_Switch_Keyboard:SW_Cherry_MX_1.00u_PCB"
    # Overridden switch for SW_0_5
    assert registry.resolve("switch", key_id="SW_0_5") == "Button_Switch_Keyboard:SW_Cherry_MX_6.25u_PCB"
    # Non-overridden key resolves default
    assert registry.resolve("switch", key_id="SW_0_0") == "Button_Switch_Keyboard:SW_Cherry_MX_1.00u_PCB"
