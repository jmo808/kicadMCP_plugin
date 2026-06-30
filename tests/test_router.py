import pytest

from kbd_engine.exceptions import RouterError
from kbd_engine.router import Router, RouterDispatch
from kbd_engine.routing_models import RoutingRequest, RoutingResult


class DummyRouter(Router):
    def route(self, request: RoutingRequest) -> RoutingResult:
        return RoutingResult(success=True)


def test_router_abc_cannot_be_instantiated() -> None:
    with pytest.raises(TypeError):
        Router()  # type: ignore[abstract]


def test_dummy_router_routing() -> None:
    router = DummyRouter()
    request = RoutingRequest(
        board_file="test.kicad_pcb",
        netlist={},
    )
    result = router.route(request)
    assert result.success is True


def test_router_dispatch_registration_and_lookup() -> None:
    dispatch = RouterDispatch()
    dummy = DummyRouter()
    dispatch.register("dummy", dummy)

    assert dispatch.get_router("dummy") is dummy

    with pytest.raises(RouterError) as exc_info:
        dispatch.get_router("unknown")
    assert "Router 'unknown' not found" in str(exc_info.value)
