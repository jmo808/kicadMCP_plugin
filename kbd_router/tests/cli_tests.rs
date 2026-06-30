use std::io::Write;
use std::process::{Command, Stdio};

#[test]
fn test_cli_routing() {
    // Run kbd-router-cli using cargo run
    let mut cmd = Command::new("cargo")
        .args(&["run", "--bin", "kbd-router-cli"])
        .stdin(Stdio::piped())
        .stdout(Stdio::piped())
        .spawn()
        .expect("Failed to spawn kbd-router-cli");

    let request_json = r#"{
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
    }"#;

    {
        let stdin = cmd.stdin.as_mut().expect("Failed to open stdin");
        stdin.write_all(request_json.as_bytes()).expect("Failed to write to stdin");
    }

    let output = cmd.wait_with_output().expect("Failed to read stdout");
    assert!(output.status.success());
    let stdout_str = String::from_utf8(output.stdout).expect("Invalid UTF-8 output");
    assert!(stdout_str.contains(r#""success":true"#));
}
