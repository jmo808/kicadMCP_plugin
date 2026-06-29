# Implementation Plan: Automated DRC Validation and Rule Checking Pipeline

## Phase 1: Structured Report Models & Parser

- [ ] Task: Define DRC models (`kbd_engine/drc/models.py`)
    - [ ] Write tests for `DRCViolation` model validation and JSON serialization
    - [ ] Write tests for `DRCReport` container model (holding multiple violations, pass/fail status)
    - [ ] Implement Pydantic models for structured reporting
    - [ ] Verify all tests pass

- [ ] Task: Conductor - User Manual Verification 'Phase 1: Structured Report Models & Parser' (Protocol in workflow.md)

## Phase 2: Native Python DRC Engine

- [ ] Task: Implement Native DRC Runner (`kbd_engine/drc/native_runner.py`)
    - [ ] Write tests using a known-bad mock `pcbnew.BOARD` containing unrouted nets
    - [ ] Write tests verifying `pcbnew.DRC_CONTROL` execution populates standard KiCad markers
    - [ ] Write tests for extracting `pcbnew.MARKER_PCB` objects and converting them to `DRCViolation` models
    - [ ] Implement the `NativeDrcRunner` class
    - [ ] Verify all tests pass

- [ ] Task: Conductor - User Manual Verification 'Phase 2: Native Python DRC Engine' (Protocol in workflow.md)

## Phase 3: Headless CLI DRC Engine

- [ ] Task: Implement CLI DRC Runner (`kbd_engine/drc/cli_runner.py`)
    - [ ] Write tests for `subprocess.run` wrapper calling `kicad-cli drc check`
    - [ ] Write tests for parsing the generated KiCad JSON/text report file into `DRCViolation` models
    - [ ] Write tests handling external CLI failure (e.g., KiCad not installed)
    - [ ] Implement the `CliDrcRunner` class
    - [ ] Verify all tests pass

- [ ] Task: Conductor - User Manual Verification 'Phase 3: Headless CLI DRC Engine' (Protocol in workflow.md)

## Phase 4: Custom DRC Rules Injection

- [ ] Task: Define and inject keyboard rules (`kbd_engine/drc/rules.py`)
    - [ ] Write standard `.kicad_dru` text defining physical switch collisions and TRRS keepouts
    - [ ] Write tests for parsing and appending these rules to the `pcbnew.BOARD_DESIGN_SETTINGS`
    - [ ] Write integration test: create overlapping switch footprints, run Native DRC, verify custom rule violation is caught
    - [ ] Implement rule injection logic
    - [ ] Verify all tests pass

- [ ] Task: Conductor - User Manual Verification 'Phase 4: Custom DRC Rules Injection' (Protocol in workflow.md)

## Phase 5: Pipeline Integration & Strict/Lenient Modes

- [ ] Task: Integrate DRC into main generation pipeline (`kbd_engine/pipeline.py`)
    - [ ] Write tests ensuring DRC runner executes immediately after routing completes
    - [ ] Write tests for Strict Mode: Verify a raised `DrcValidationException` halts execution and prevents board save
    - [ ] Write tests for Lenient Mode: Verify execution succeeds but warnings are attached to the pipeline result
    - [ ] Integrate configuration toggle and runner dispatch
    - [ ] Verify >80% test coverage across the `kbd_engine/drc` module
    - [ ] Verify 100% `mypy` type checking passes

- [ ] Task: Conductor - User Manual Verification 'Phase 5: Pipeline Integration & Strict/Lenient Modes' (Protocol in workflow.md)
