# Implementation Plan: Build Core Keyboard-to-PCB Placement Pipeline with MCP Server

## Phase 1: Project Scaffolding & Foundation

- [~] Task: Initialize Python package structure and development environment
    - [ ] Create `kbd_engine/` package with `__init__.py`
    - [ ] Create `tests/` directory with `conftest.py`
    - [ ] Create `pyproject.toml` with dependencies (fastmcp, pytest, ruff, mypy, pytest-cov)
    - [ ] Create virtual environment and install dependencies
    - [ ] Create `ruff.toml` configuration for linting/formatting
    - [ ] Verify `pytest`, `ruff`, and `mypy` run successfully on empty package

- [ ] Task: Define core data models (`kbd_engine/models.py`)
    - [ ] Write tests for `Key` dataclass (position, size, rotation, row/col assignment)
    - [ ] Write tests for `KeyMatrix` dataclass (collection of Keys with matrix metadata)
    - [ ] Write tests for `PlacementResult` dataclass (component positions and validation status)
    - [ ] Implement `Key`, `KeyMatrix`, and `PlacementResult` dataclasses with type hints
    - [ ] Verify all tests pass and models are frozen/immutable where appropriate

- [ ] Task: Create custom exception hierarchy (`kbd_engine/exceptions.py`)
    - [ ] Write tests for exception classes carrying structured context (component ref, position, constraint)
    - [ ] Implement `KbdEngineError` base exception and subclasses: `ParseError`, `PlacementError`, `RegistryError`, `DrcError`, `RouterError`
    - [ ] Verify all tests pass

- [ ] Task: Create pcbnew adapter layer (`kbd_engine/pcbnew_adapter.py`)
    - [ ] Write tests for adapter interface using mock pcbnew module
    - [ ] Implement thin adapter wrapping pcbnew API calls (create_footprint, set_position, add_track, run_drc)
    - [ ] Create mock pcbnew module in `tests/mock_pcbnew.py` for testing without KiCad
    - [ ] Verify all tests pass with mocked pcbnew

- [ ] Task: Conductor - User Manual Verification 'Phase 1: Project Scaffolding & Foundation' (Protocol in workflow.md)

## Phase 2: KLE Parser & Component Registry

- [ ] Task: Implement KLE JSON parser (`kbd_engine/kle_parser.py`)
    - [ ] Write tests for parsing a minimal 4-key KLE JSON into KeyMatrix
    - [ ] Write tests for parsing key sizes (1u, 1.25u, 1.5u, 2u, 6.25u)
    - [ ] Write tests for parsing key rotation angles
    - [ ] Write tests for error handling on malformed KLE JSON
    - [ ] Implement `parse_kle_json()` function mapping KLE format to `KeyMatrix`
    - [ ] Write tests for a full 60% layout KLE JSON
    - [ ] Verify all tests pass

- [ ] Task: Implement component abstraction registry (`kbd_engine/registry.py`)
    - [ ] Write tests for default footprint resolution (MX switch, SOD-123 diode, 0805 capacitor)
    - [ ] Write tests for per-key component type overrides
    - [ ] Write tests for loading custom registry from JSON configuration
    - [ ] Write tests for `RegistryError` on unknown component types
    - [ ] Implement `FootprintRegistry` class with built-in defaults and JSON extension
    - [ ] Create default registry JSON (`kbd_engine/data/default_registry.json`)
    - [ ] Verify all tests pass

- [ ] Task: Conductor - User Manual Verification 'Phase 2: KLE Parser & Component Registry' (Protocol in workflow.md)

## Phase 3: Grid Placement Engine

- [ ] Task: Implement grid placement engine (`kbd_engine/placer.py`)
    - [ ] Write tests for switch placement with default 19.05mm pitch on a 4-key row
    - [ ] Write tests for diode placement with configurable Y-offset below each switch
    - [ ] Write tests for capacitor placement adjacent to switches
    - [ ] Write tests for staggered row offsets (standard QWERTY stagger pattern)
    - [ ] Write tests for ortholinear grid placement (zero stagger)
    - [ ] Implement `GridPlacer` class with `place(key_matrix, registry) → PlacementResult`
    - [ ] Verify placement completes in <5 seconds for 60-key layout (NFR-01)
    - [ ] Verify all tests pass

- [ ] Task: Integrate placement with pcbnew adapter
    - [ ] Write tests for `apply_placement()` writing PlacementResult to a board via adapter
    - [ ] Write tests for dry-run mode returning preview without modifying board
    - [ ] Implement `apply_placement(result, adapter, dry_run=False)` function
    - [ ] Verify all tests pass with mocked pcbnew

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
