# Specification: Build Core Keyboard-to-PCB Placement Pipeline with MCP Server

## Overview

This track delivers the foundational pipeline that takes a keyboard layout definition (KLE JSON) and produces a fully placed, DRC-validated KiCad PCB — all orchestrated through an MCP server interface. It encompasses project scaffolding, input parsing, component abstraction, algorithmic placement, DRC validation, and MCP tool exposure.

## Scope

### In Scope
- Python package structure with `pcbnew` mock layer for testing
- KLE JSON parser producing internal matrix representation
- Component abstraction registry mapping logical types to KiCad footprints
- Grid placement engine for switches, diodes, and capacitors
- DRC validation gate integrated into the placement pipeline
- MCP server (FastMCP) with `place`, `preview`, and `validate_drc` endpoints
- Dry-run / preview mode for all destructive operations
- Comprehensive test suite (>80% coverage)

### Out of Scope (Future Tracks)
- Automated trace routing (Rust A*, Quilter, FreeRouting integration)
- Custom JSON matrix definition input format
- Interactive KiCad wxPython dialog
- TypeScript web-based layout editor
- Split board geometry (Dactyl, Sofle) — deferred to a layout-extensions track

## Technical Design

### Package Structure
```
kbd_engine/
├── __init__.py
├── kle_parser.py        # KLE JSON parsing → internal KeyMatrix model
├── models.py            # Core data models (Key, KeyMatrix, PlacementResult)
├── registry.py          # Component abstraction & footprint registry
├── placer.py            # Grid placement engine
├── drc.py               # DRC validation gate
├── mcp_server.py        # FastMCP server with tool endpoints
├── pcbnew_adapter.py    # Thin adapter over pcbnew API (mockable)
└── exceptions.py        # Custom exception hierarchy
tests/
├── conftest.py          # Shared fixtures (sample KLE data, mock pcbnew)
├── test_kle_parser.py
├── test_models.py
├── test_registry.py
├── test_placer.py
├── test_drc.py
├── test_mcp_server.py
└── test_pcbnew_adapter.py
```

### Data Flow
```
KLE JSON → kle_parser → KeyMatrix → placer (+ registry) → PlacementResult → pcbnew_adapter → .kicad_pcb
                                                                    ↓
                                                              drc (validate)
                                                                    ↓
                                                           MCP Server (expose)
```

### Key Design Decisions

1. **pcbnew Adapter Pattern:** All `pcbnew` API calls go through `pcbnew_adapter.py`, which provides a thin, mockable interface. This satisfies NFR-02 (testability without KiCad).

2. **Immutable Data Models:** `Key`, `KeyMatrix`, and `PlacementResult` are dataclasses (frozen where practical) to ensure predictable state.

3. **Registry-Driven Footprints:** The `FootprintRegistry` loads from a JSON configuration file, with built-in defaults for common components (MX switches, SOD-123 diodes, etc.).

4. **DRC as a Gate:** DRC validation runs as a post-placement verification step. In dry-run mode, the DRC check uses coordinate-based clearance calculations without writing to the board.

## Acceptance Criteria

- [ ] KLE JSON files from keyboard-layout-editor.com parse correctly for 60%, 65%, and TKL layouts.
- [ ] Placement engine generates correct X/Y positions for a 60-key layout in <5 seconds.
- [ ] Component registry resolves MX switch and SOD-123 diode footprints with per-key overrides.
- [ ] DRC validation gate catches clearance violations and reports actionable errors.
- [ ] MCP server exposes `place`, `preview`, and `validate_drc` endpoints with dry-run support.
- [ ] All MCP endpoints return structured JSON responses.
- [ ] Test suite achieves >80% coverage with mocked pcbnew.
- [ ] All code passes `ruff` linting and `mypy` type checking.
