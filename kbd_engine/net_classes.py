import json
import os
import re

from kbd_engine.pcbnew_adapter import PcbnewAdapter
from kbd_engine.routing_models import NetClass


class NetClassManager:
    """Manages net class definitions and maps nets to their respective classes."""

    def __init__(self, config_path: str | None = None) -> None:
        """Initialize the manager with default and optional custom configurations.

        Args:
            config_path: Path to custom JSON net class configuration file.
        """
        self.classes: dict[str, NetClass] = {}
        self.patterns: dict[str, str] = {}

        # Load defaults
        default_path = os.path.join(
            os.path.dirname(__file__), "data", "default_net_classes.json"
        )
        self._load_config(default_path)

        # Load custom if specified
        if config_path:
            self._load_config(config_path)

    def _load_config(self, filepath: str) -> None:
        """Load rules and patterns from a configuration JSON file.

        Args:
            filepath: Path to the JSON configuration file.
        """
        with open(filepath) as f:
            data = json.load(f)

        # Parse classes
        for name, rules in data.get("classes", {}).items():
            self.classes[name] = NetClass(
                name=name,
                track_width=rules.get("track_width", 0.2),
                clearance=rules.get("clearance", 0.2),
                via_diameter=rules.get("via_diameter", 0.6),
                via_drill=rules.get("via_drill", 0.3),
            )

        # Parse patterns
        for pattern, class_name in data.get("patterns", {}).items():
            self.patterns[pattern] = class_name

    def match_net(self, net_name: str) -> str:
        """Find the matching net class name for a given net name.

        Defaults to 'Signal' if no patterns match.

        Args:
            net_name: Name of the net to match.

        Returns:
            The name of the matched net class.
        """
        for pattern, class_name in self.patterns.items():
            if re.match(pattern, net_name):
                return class_name
        return "Signal"

    def apply_to_board(self, adapter: PcbnewAdapter, net_names: list[str]) -> None:
        """Apply net class rules and assignments to the KiCad board.

        Args:
            adapter: PcbnewAdapter instance representing the board.
            net_names: List of all net names on the board to be assigned.
        """
        # 1. Create all net classes
        for name, nc in self.classes.items():
            adapter.create_net_class(
                name=name,
                track_width=nc.track_width,
                clearance=nc.clearance,
                via_diameter=nc.via_diameter,
                via_drill=nc.via_drill,
            )

        # 2. Assign each net to its net class
        for net_name in net_names:
            class_name = self.match_net(net_name)
            adapter.set_net_class(net_name, class_name)
