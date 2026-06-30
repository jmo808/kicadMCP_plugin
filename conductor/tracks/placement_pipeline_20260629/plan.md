# Implementation Plan: Build Core Keyboard-to-PCB Placement Pipeline with MCP Server

## Phase 1: Project Scaffolding & Foundation [checkpoint: 0d148ca]

- [x] Task: Initialize Python package structure and development environment (89906de)
    - [x] Create `kbd_engine/` package with `__init__.py`
    - [x] Create `tests/` directory with `conftest.py`
    - [x] Create `pyproject.toml` with dependencies (fastmcp, pytest, ruff, mypy, pytest-cov)
    - [x] Create virtual environment and install dependencies
    - [x] Create `ruff.toml` configuration for linting/formatting
    - [x] Verify `pytest`, `ruff`, and `mypy` run successfully on empty package

- [x] Task: Define core data models (`kbd_engine/models.py`) (3abbe90)
    - [x] Write tests for `Key` dataclass (position, size, rotation, row/col assignment)
    - [x] Write tests for `KeyMatrix` dataclass (collection of Keys with matrix metadata)
    - [x] Write tests for `PlacementResult` dataclass (component positions and validation status)
    - [x] Implement `Key`, `KeyMatrix`, and `PlacementResult` dataclasses with type hints
    - [x] Verify all tests pass and models are frozen/immutable where appropriate

- [x] Task: Create custom exception hierarchy (`kbd_engine/exceptions.py`) (3739c9b)
    - [x] Write tests for exception classes carrying structured context (component ref, position, constraint)
    - [x] Implement `KbdEngineError` base exception and subclasses: `ParseError`, `PlacementError`, `RegistryError`, `DrcError`, `RouterError`
    - [x] Verify all tests pass

- [x] Task: Create pcbnew adapter layer (`kbd_engine/pcbnew_adapter.py`) (26e7791)
    - [x] Write tests for adapter interface using mock pcbnew module
    - [x] Implement thin adapter wrapping pcbnew API calls (create_footprint, set_position, add_track, run_drc)
    - [x] Create mock pcbnew module in `tests/mock_pcbnew.py` for testing without KiCad
    - [x] Verify all tests pass with mocked pcbnew

- [x] Task: Conductor - User Manual Verification 'Phase 1: Project Scaffolding & Foundation' (Protocol in workflow.md) (0d148ca)

## Phase 2: KLE Parser & Component Registry [checkpoint: 6f8228b]

- [x] Task: Implement KLE JSON parser (`kbd_engine/kle_parser.py`) (c4fa381)
    - [x] Write tests for parsing a minimal 4-key KLE JSON into KeyMatrix
    - [x] Write tests for parsing key sizes (1u, 1.25u, 1.5u, 2u, 6.25u)
    - [x] Write tests for parsing key rotation angles
    - [x] Write tests for error handling on malformed KLE JSON
    - [x] Implement `parse_kle_json()` function mapping KLE format to `KeyMatrix`
    - [x] Write tests for a full 60% layout KLE JSON
    - [x] Verify all tests pass

- [x] Task: Implement component abstraction registry (`kbd_engine/registry.py`) (f515117)
    - [x] Write tests for default footprint resolution (MX switch, SOD-123 diode, 0805 capacitor)
    - [x] Write tests for per-key component type overrides
    - [x] Write tests for loading custom registry from JSON configuration
    - [x] Write tests for `RegistryError` on unknown component types
    - [x] Implement `FootprintRegistry` class with built-in defaults and JSON extension
    - [x] Create default registry JSON (`kbd_engine/data/default_registry.json`)
    - [x] Verify all tests pass

- [x] Task: Conductor - User Manual Verification 'Phase 2: KLE Parser & Component Registry' (Protocol in workflow.md) (6f8228b)

## Phase 3: Grid Placement Engine

- [x] Task: Implement grid placement engine (`kbd_engine/placer.py`) (44b9557)
    - [x] Write tests for switch placement with default 19.05mm pitch on a 4-key row
    - [x] Write tests for diode placement with configurable Y-offset below each switch
    - [x] Write tests for capacitor placement adjacent to switches
    - [x] Write tests for staggered row offsets (standard QWERTY stagger pattern)
    - [x] Write tests for ortholinear grid placement (zero stagger)
    - [x] Implement `GridPlacer` class with `place(key_matrix, registry) → PlacementResult`
    - [x] Verify placement completes in <5 seconds for 60-key layout (NFR-01)
    - [x] Verify all tests pass

- [x] Task: Integrate placement with pcbnew adapter (`kbd_engine/placer.py`) (7ebad3f)
    - [x] Write tests for `apply_placement()` writing PlacementResult to a board via adapter
    - [x] Write tests for dry-run mode returning preview without modifying board
    - [x] Implement `apply_placement(result, adapter, dry_run=False)` function
    - [x] Verify all tests pass with mocked pcbnew

- [ ] Task: Conductor - User Manual Verification 'Phase 3: Grid Placement Engine' (Protocol in workflow.md)

## Phase 4: DRC Validation Gate

- [ ] Task: Implement DRC validation gate (`kbd_engine/drc.py`)
    - [ ] Write tests for DRC pass on valid placement (no violations)
    - [ ] Write tests for DRC failure detecting courtyard clearance violations
    - [ ] Write tests for DRC failure detecting overlapping footprints
    - [ ] Write tests for actionable error messages (component ref, coordinates, violated rule)
    - [ ] Implement `DrcValidator` class wrapping pcbnew DRC via adapter
    - [ ] Implement coordinate-based clearance check for dry-run mode (no board write)
    - [ ] Verify all tests pass

- [ ] Task: Conductor - User Manual Verification 'Phase 4: DRC Validation Gate' (Protocol in workflow.md)

## Phase 5: MCP Server & Integration

- [ ] Task: Implement MCP server (`kbd_engine/mcp_server.py`)
    - [ ] Write tests for `place` tool endpoint (KLE JSON input → placement result)
    - [ ] Write tests for `preview` tool endpoint (dry-run placement → JSON preview)
    - [ ] Write tests for `validate_drc` tool endpoint (run DRC on current board)
    - [ ] Write tests for error response formatting (structured JSON errors)
    - [ ] Implement FastMCP server with `place`, `preview`, and `validate_drc` tools
    - [ ] Implement structured JSON response format for all endpoints
    - [ ] Verify all tests pass

- [ ] Task: End-to-end integration test
    - [ ] Write integration test: KLE JSON → parse → place → DRC validate (full pipeline)
    - [ ] Write integration test: MCP `place` endpoint with dry_run=True returns valid preview JSON
    - [ ] Write integration test: MCP `place` endpoint with invalid KLE JSON returns actionable error
    - [ ] Verify all integration tests pass
    - [ ] Run `pytest --cov=kbd_engine --cov-report=html` and verify >80% coverage
    - [ ] Run `ruff check kbd_engine/ tests/` and verify zero errors
    - [ ] Run `mypy kbd_engine/` and verify zero errors

- [ ] Task: Conductor - User Manual Verification 'Phase 5: MCP Server & Integration' (Protocol in workflow.md)
