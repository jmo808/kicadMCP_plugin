class KbdEngineError(Exception):
    """Base exception for the KiCad Keyboard Automation Engine."""

    pass


class ParseError(KbdEngineError):
    """Raised when layout parsing fails."""

    def __init__(self, message: str, line: int | None = None, column: int | None = None) -> None:
        context = []
        if line is not None:
            context.append(f"line {line}")
        if column is not None:
            context.append(f"column {column}")

        full_message = message
        if context:
            full_message = f"{message} (at {', '.join(context)})"

        super().__init__(full_message)
        self.line = line
        self.column = column


class PlacementError(KbdEngineError):
    """Raised when layout placement fails."""

    def __init__(self, message: str, key_id: str | None = None, x: float | None = None, y: float | None = None) -> None:
        context = []
        if key_id is not None:
            context.append(f"key {key_id}")
        if x is not None and y is not None:
            context.append(f"pos ({x}, {y})")

        full_message = message
        if context:
            full_message = f"{message} ({', '.join(context)})"

        super().__init__(full_message)
        self.key_id = key_id
        self.x = x
        self.y = y


class RegistryError(KbdEngineError):
    """Raised when footprint registry lookup fails."""

    def __init__(self, message: str, component_type: str | None = None) -> None:
        full_message = message
        if component_type is not None:
            full_message = f"{message} (type: {component_type})"
        super().__init__(full_message)
        self.component_type = component_type


class DrcError(KbdEngineError):
    """Raised when design rule check (DRC) fails."""

    def __init__(
        self, message: str, violation_type: str | None = None, location: tuple[float, float] | None = None
    ) -> None:
        context = []
        if violation_type is not None:
            context.append(f"type: {violation_type}")
        if location is not None:
            context.append(f"loc: {location[0]}, {location[1]}")

        full_message = message
        if context:
            full_message = f"{message} ({', '.join(context)})"

        super().__init__(full_message)
        self.violation_type = violation_type
        self.location = location


class RouterError(KbdEngineError):
    """Raised when routing fails."""

    def __init__(self, message: str, net_name: str | None = None) -> None:
        full_message = message
        if net_name is not None:
            full_message = f"{message} (net: {net_name})"
        super().__init__(full_message)
        self.net_name = net_name
