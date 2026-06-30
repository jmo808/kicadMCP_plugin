import json


def test_python_bindings_empty_board() -> None:
    # We import inside the test to allow pytest to collect tests even if kbd_router is not built yet (Red Phase)
    import kbd_router

    request = {
        "width": 10.0,
        "height": 10.0,
        "grid_pitch": 1.0,
        "nets": [
            {
                "name": "NET_1",
                "pins": [
                    {"x": 1, "y": 1, "layer": 0},
                    {"x": 5, "y": 1, "layer": 0}
                ],
                "track_width": 0.2,
                "clearance": 0.2
            }
        ],
        "obstacles": []
    }

    result_str = kbd_router.route_board(json.dumps(request))  # type: ignore[attr-defined]
    result = json.loads(result_str)

    assert result["success"] is True
    assert len(result["traces"]) == 1
    assert result["traces"][0]["start"] == [1.0, 1.0]
    assert result["traces"][0]["end"] == [5.0, 1.0]
    assert len(result["vias"]) == 0
    assert len(result["unrouted_nets"]) == 0
