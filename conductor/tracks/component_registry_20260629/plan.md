# Implementation Plan: Component Abstraction Layer and Footprint Registry

## Phase 1: JSON Footprint Registry Model

- [ ] Task: Define JSON schema and data models (`kbd_engine/registry/models.py`)
    - [ ] Write tests for parsing `registry.json` containing logical-to-physical mappings
    - [ ] Write tests for default component configurations (e.g., default switch type)
    - [ ] Write tests for handling malformed JSON or missing required fields
    - [ ] Implement `FootprintRegistry` configuration models
    - [ ] Create initial `kbd_engine/data/registry.json` file
    - [ ] Verify all tests pass

- [ ] Task: Conductor - User Manual Verification 'Phase 1: JSON Footprint Registry Model' (Protocol in workflow.md)

## Phase 2: KiCad Library Resolution & Bundled Library

- [ ] Task: Scaffold custom bundled library (`kbd_engine/kicad_libs/kbd_custom.pretty/`)
    - [ ] Set up the directory structure for the bundled `.pretty` library
    - [ ] Include standard `.kicad_mod` files for Cherry MX (PTH/HotSwap), Choc, and basic diodes
    - [ ] Ensure the library path is dynamically resolved relative to the plugin installation path

- [ ] Task: Implement library resolution logic (`kbd_engine/registry/resolver.py`)
    - [ ] Write tests for resolving footprints from the custom `.pretty` library
    - [ ] Write tests for fallback resolution to standard KiCad libraries
    - [ ] Implement the path resolution and lookup logic
    - [ ] Verify all tests pass with mocked file paths

- [ ] Task: Conductor - User Manual Verification 'Phase 2: KiCad Library Resolution & Bundled Library' (Protocol in workflow.md)

## Phase 3: Strict Pre-validation (Fail Fast)

- [ ] Task: Implement footprint validation engine (`kbd_engine/registry/validator.py`)
    - [ ] Write tests for iterating over all required footprints for a layout
    - [ ] Write tests for interrogating the `pcbnew` footprint table to confirm existence
    - [ ] Write tests for immediately failing and returning a structured error if any footprint is missing
    - [ ] Write tests for successfully passing validation when all footprints exist
    - [ ] Implement the `PreFlightValidator`
    - [ ] Verify all tests pass with a mocked `pcbnew` environment

- [ ] Task: Conductor - User Manual Verification 'Phase 3: Strict Pre-validation (Fail Fast)' (Protocol in workflow.md)

## Phase 4: Component Instantiation Abstraction

- [ ] Task: Implement `ComponentFactory` (`kbd_engine/registry/factory.py`)
    - [ ] Write tests for instantiating a `pcbnew.Footprint` from a logical component type
    - [ ] Write tests for correct assignment of reference designators (e.g., `SW1`, `D1`)
    - [ ] Write tests for applying position (X, Y) and rotation to the instantiated footprint
    - [ ] Implement the factory pattern leveraging the `FootprintRegistry`
    - [ ] Verify all tests pass with a mocked `pcbnew` API

- [ ] Task: Conductor - User Manual Verification 'Phase 4: Component Instantiation Abstraction' (Protocol in workflow.md)

## Phase 5: Hybrid Override Resolution & E2E Integration

- [ ] Task: Implement hybrid component overrides
    - [ ] Write tests for parsing embedded footprint overrides from KLE metadata
    - [ ] Write tests for resolving explicit override maps provided in placement requests
    - [ ] Write tests enforcing resolution priority: Explicit Map > Embedded KLE > Global Default
    - [ ] Integrate override logic into the layout parsing pipeline
    - [ ] Verify all tests pass

- [ ] Task: End-to-End Placement Integration
    - [ ] Write integration test: Load layout -> Run strict pre-validation (Success) -> Instantiate mixed-type board
    - [ ] Write integration test: Load layout with intentionally invalid override -> Run strict pre-validation (Fail)
    - [ ] Ensure test coverage >80% for the entire `kbd_engine/registry` module
    - [ ] Run `ruff check` and `mypy` on the module to ensure zero static analysis errors

- [ ] Task: Conductor - User Manual Verification 'Phase 5: Hybrid Override Resolution & E2E Integration' (Protocol in workflow.md)
