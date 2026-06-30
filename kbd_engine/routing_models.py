from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class NetClass:
    """Represents design rules for a class of nets.

    All dimensions/clearances are in millimeters (mm).
    """

    name: str
    track_width: float = 0.2
    clearance: float = 0.2
    via_diameter: float = 0.6
    via_drill: float = 0.3


@dataclass(frozen=True)
class TraceSegment:
    """Represents a segment of a routed trace on a specific layer."""

    start: tuple[float, float]
    end: tuple[float, float]
    layer: str
    width: float


@dataclass(frozen=True)
class Via:
    """Represents a via at a layer transition."""

    position: tuple[float, float]
    drill: float
    diameter: float
    layers: tuple[str, str]


@dataclass(frozen=True)
class RoutingRequest:
    """Represents a request to route a board with constraints."""

    board_file: str
    netlist: dict[str, list[tuple[str, str]]]
    net_classes: dict[str, str] = field(default_factory=dict)
    class_rules: dict[str, NetClass] = field(default_factory=dict)
    router: str = "rust_astar"
    grid_pitch: float = 0.5
    extra_options: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RoutingResult:
    """Represents the outcome of a routing operation."""

    traces: list[TraceSegment] = field(default_factory=list)
    vias: list[Via] = field(default_factory=list)
    unrouted_nets: list[str] = field(default_factory=list)
    success: bool = True
    diagnostics: str = ""
