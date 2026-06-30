import json
import os
from typing import Any

from kbd_engine.exceptions import RegistryError


class FootprintRegistry:
    """Registry that maps logical component types to physical KiCad footprints."""

    def __init__(self, registry_file: str | None = None) -> None:
        self.mappings: dict[str, str] = {}
        self.overrides: dict[str, dict[str, str]] = {}

        # Load built-in defaults
        default_path = os.path.join(os.path.dirname(__file__), "data", "default_registry.json")
        if os.path.exists(default_path):
            with open(default_path) as f:
                try:
                    self.load_mappings(json.load(f))
                except json.JSONDecodeError as e:
                    raise RegistryError(f"Malformed default registry file: {e}") from e

        # Load custom overrides/additions if specified
        if registry_file is not None:
            if not os.path.exists(registry_file):
                raise RegistryError(f"Registry file not found: {registry_file}")
            with open(registry_file) as f:
                try:
                    self.load_mappings(json.load(f))
                except json.JSONDecodeError as e:
                    raise RegistryError(f"Malformed registry file '{registry_file}': {e}") from e

    def load_mappings(self, data: dict[str, Any]) -> None:
        """Loads mappings from a dictionary structure, separating overrides."""
        for k, v in data.items():
            if k == "overrides":
                if not isinstance(v, dict):
                    raise RegistryError("Overrides must be a dictionary")
                for key_id, key_overrides in v.items():
                    if not isinstance(key_overrides, dict):
                        raise RegistryError(f"Overrides for key '{key_id}' must be a dictionary")
                    if key_id not in self.overrides:
                        self.overrides[key_id] = {}
                    for comp_type, fp in key_overrides.items():
                        self.overrides[key_id][comp_type] = str(fp)
            else:
                self.mappings[k] = str(v)

    def resolve(self, component_type: str, key_id: str | None = None) -> str:
        """Resolves a logical component type to its associated physical footprint reference.

        Checks per-key overrides first, then falls back to global mappings.
        """
        if key_id is not None and key_id in self.overrides:
            key_overrides = self.overrides[key_id]
            if component_type in key_overrides:
                return key_overrides[component_type]

        if component_type in self.mappings:
            return self.mappings[component_type]

        raise RegistryError(f"Unknown component type: '{component_type}'", component_type=component_type)
