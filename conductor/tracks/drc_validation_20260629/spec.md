# Specification: Automated DRC Validation and Rule Checking Pipeline

## Overview

This track delivers a robust automated Design Rule Check (DRC) pipeline that runs immediately after the trace routing phase. The pipeline ensures that generated keyboard PCBs are electrically and physically sound before they are committed to disk or sent to a fab. It supports native Python execution (for real-time UI feedback) and Headless CLI execution (for CI/CD), injects custom keyboard-specific constraints, and provides configurable strict/lenient error handling.

## Functional Requirements

### FR-01: Dual-Mode Execution Engine
- **Native Python:** Implement a DRC runner utilizing `pcbnew.DRC_CONTROL` or `pcbnew.BOARD_DESIGN_SETTINGS` (depending on KiCad 9 API) to run checks natively within the plugin environment.
- **Headless CLI:** Implement a wrapper around `kicad-cli drc check` that can execute on a saved `.kicad_pcb` file, parse the resulting JSON/text report, and return structured error objects.

### FR-02: Structured Violation Reporting
- The DRC engine must parse KiCad's raw DRC markers/reports into structured Pydantic models (e.g., `DRCViolation` with fields for `severity`, `error_code`, `description`, `location_x`, `location_y`, `items`).
- These structured reports must be serializable over the WebSocket Bridge so the Web Editor can render DRC markers (red circles/arrows) exactly where they occur on the 3D preview.

### FR-03: Custom Keyboard Design Rules
- Define a custom `keyboard_rules.kicad_dru` (or inject rules programmatically via Python).
- **Physical Collision:** Add rules to ensure MX/Choc switch footprints do not physically overlap (enforcing standard 19.05mm spacing boundaries).
- **Keepout Zones:** Enforce TRRS/USB-C connector keepout zones (ensuring no traces or vias are placed too close to the mounting holes or connector shell).
- **Via Restrictions:** Ensure vias are not placed directly inside switch center holes or stabilizer cutouts.

### FR-04: Strict vs Lenient Modes
- Implement a configuration toggle (`drc_mode: "strict" | "lenient"`).
- **Strict Mode:** If *any* DRC error (clearance violation, unrouted net) is detected, the pipeline aborts, does not overwrite the final `.kicad_pcb`, and returns a `ValidationException` with the report.
- **Lenient Mode:** DRC errors are treated as warnings. The pipeline completes, saves the board, and returns a success response along with the list of warnings.

## Non-Functional Requirements

| ID | Requirement | Metric |
|---|---|---|
| NFR-01 | **Execution Speed** | Native DRC execution on a fully routed 100-key board must complete in < 2 seconds. |
| NFR-02 | **Idempotency** | Running the DRC check multiple times on the same board must yield identical structured reports without altering board state. |
| NFR-03 | **Testability** | Both native and CLI modes must be fully covered by automated tests using a known-bad mock `.kicad_pcb` file. |

## Acceptance Criteria

- [ ] Native Python DRC runner successfully executes and returns standard KiCad clearance errors.
- [ ] Headless CLI runner successfully executes `kicad-cli`, parses the output file, and returns matching structured errors.
- [ ] Custom rules are successfully injected and flag switch collisions and keepout violations.
- [ ] Strict mode aborts execution and raises an error when violations are found.
- [ ] Lenient mode completes execution and returns a structured warning list.
- [ ] Structured `DRCViolation` objects serialize cleanly to JSON for the Web Editor.
- [ ] Test suite achieves >80% coverage and verifies both strict/lenient behaviors.

## Out of Scope

- Implementing an auto-fixer that attempts to automatically resolve clearance errors (the pipeline identifies errors, it does not fix them).
