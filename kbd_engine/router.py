from abc import ABC, abstractmethod

from kbd_engine.exceptions import RouterError
from kbd_engine.routing_models import RoutingRequest, RoutingResult


class Router(ABC):
    """Abstract Base Class defining the contract for all routing backends."""

    @abstractmethod
    def route(self, request: RoutingRequest) -> RoutingResult:
        """Route the board specified in the request.

        Args:
            request: The routing request containing netlist, board, and rules.

        Returns:
            A RoutingResult containing the trace segments, vias, and status.

        Raises:
            RouterError: If a fatal routing error occurs.
        """
        pass


class RouterDispatch:
    """Registry and dispatcher for selected routing backends."""

    def __init__(self) -> None:
        self._routers: dict[str, Router] = {}

    def register(self, name: str, router: Router) -> None:
        """Register a router backend under a given name.

        Args:
            name: The name of the router backend (e.g., 'rust_astar').
            router: The router instance to register.
        """
        self._routers[name] = router

    def get_router(self, name: str) -> Router:
        """Retrieve a registered router backend by name.

        Args:
            name: The name of the router.

        Returns:
            The registered Router instance.

        Raises:
            RouterError: If no router is registered under the given name.
        """
        if name not in self._routers:
            raise RouterError(f"Router '{name}' not found")
        return self._routers[name]
