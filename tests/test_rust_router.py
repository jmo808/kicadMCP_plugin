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


def test_cli_subprocess() -> None:
    import os
    import subprocess

    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    cli_dir = os.path.join(project_root, "kbd_router")

    # Compile the binary
    subprocess.run(["cargo", "build", "--bin", "kbd-router-cli"], cwd=cli_dir, check=True)

    # Get binary path
    binary_path = os.path.join(cli_dir, "target", "debug", "kbd-router-cli")

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

    proc = subprocess.run(
        [binary_path],
        input=json.dumps(request),
        text=True,
        capture_output=True,
        check=True
    )

    result = json.loads(proc.stdout)
    assert result["success"] is True
    assert len(result["traces"]) == 1
    assert result["traces"][0]["start"] == [1.0, 1.0]
    assert result["traces"][0]["end"] == [5.0, 1.0]
    assert len(result["vias"]) == 0
    assert len(result["unrouted_nets"]) == 0


def test_server_http() -> None:
    import os
    import subprocess
    import time
    import urllib.request

    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    cli_dir = os.path.join(project_root, "kbd_router")

    # Compile the server
    subprocess.run(["cargo", "build", "--bin", "kbd-router-server"], cwd=cli_dir, check=True)

    # Get binary path
    binary_path = os.path.join(cli_dir, "target", "debug", "kbd-router-server")

    # Start server as background process
    server_proc = subprocess.Popen([binary_path])
    time.sleep(1.0)  # Wait for server to start

    try:
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

        req = urllib.request.Request(
            "http://127.0.0.1:8080/route",
            data=json.dumps(request).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )

        with urllib.request.urlopen(req) as response:
            resp_bytes = response.read()
            result = json.loads(resp_bytes.decode("utf-8"))

        assert result["success"] is True
        assert len(result["traces"]) == 1
        assert result["traces"][0]["start"] == [1.0, 1.0]
        assert result["traces"][0]["end"] == [5.0, 1.0]
        assert len(result["vias"]) == 0
        assert len(result["unrouted_nets"]) == 0

    finally:
        server_proc.terminate()
        server_proc.wait()


