# Specification: Automated Trace Routing Pipeline with Multi-Router Dispatch

## Overview

This track delivers the automated trace routing pipeline that completes the keyboard-to-PCB generation workflow. Building on the placement pipeline (Track 1), it takes a placed board with assigned nets and generates fully routed traces — covering the switch-diode scanning matrix, power distribution rails, USB data lines, MCU connections, and all other board-level nets.

The routing pipeline supports three backend engines (Rust A* pathfinder, Quilter API, FreeRouting) with a user-selectable dispatch model. The Rust A* engine is the default and is integrated via all three methods: PyO3 FFI for in-process performance, subprocess + JSON I/O as a portable fallback, and a REST API wrapper for language-agnostic external clients.

## Functional Requirements

### FR-01: Multi-Router Dispatch Interface
- Unified `Router` protocol/ABC that all routing backends implement.
- User-selectable router via MCP `route` tool parameter (`router="rust_astar"` | `"quilter"` | `"freerouting"`).
- Default router: `rust_astar`.
- Graceful error handling: if the selected router fails, return a structured error with diagnostics (unrouted nets, violated constraints) — no silent fallback.

### FR-02: Rust A* Pathfinding Engine
- Deterministic, high-performance grid-based A* router implemented in Rust.
- **Three integration modes:**
  1. **PyO3 FFI binding (primary):** Compiled as a Python extension module (`kbd_router`) for zero-copy, in-process calls from the Python engine.
  2. **Subprocess + JSON I/O (fallback):** Standalone Rust binary (`kbd-router-cli`) exchanging routing requests/results via JSON on stdin/stdout.
  3. **REST API wrapper:** Lightweight HTTP server (`kbd-router-server`) exposing routing as a POST endpoint for language-agnostic clients.
- All three modes must produce identical routing results for the same input.

### FR-03: Quilter API Integration
- REST client interfacing with the Quilter cloud-based autorouter.
- Send board geometry, netlist, and constraint definitions.
- Receive routed trace data and map back to KiCad track objects.
- Handle API authentication, rate limiting, and timeout errors.

### FR-04: FreeRouting Integration
- Export placed board to Specctra DSN format.
- Invoke FreeRouting (Java-based) as subprocess.
- Import routed results from Specctra SES format.
- Map imported routes back to KiCad `pcbnew` track objects.

### FR-05: Full Board Routing Scope
- **Matrix nets:** Route all row and column nets connecting switches and diodes in the scanning matrix.
- **Power rails:** Route VCC and GND distribution traces with appropriate track widths for current capacity.
- **Signal traces:** Route USB data lines (D+/D−), I2C/SPI MCU communication buses, and other non-matrix signal nets.
- **Net prioritization:** Route power and signal-integrity-critical nets first, matrix nets second.

### FR-06: IPC-2152 Track Width Calculation
- Automatically compute minimum track widths based on:
  - Expected current per net (configurable per net class).
  - Copper weight/thickness (default: 1oz/35µm).
  - Maximum acceptable temperature rise (default: 10°C).
- Expose track width calculator as a standalone utility and as part of the routing pipeline.

### FR-07: Net Class Assignment
- Assign KiCad net classes with per-class design rules:
  - `MatrixRow` / `MatrixCol`: Standard clearance and width for low-current scanning traces.
  - `Power`: Wider tracks and increased clearance for VCC/GND.
  - `USB`: Differential pair constraints for D+/D−.
  - `Signal`: Default rules for general MCU I/O.
- Net class definitions configurable via JSON.

### FR-08: Automatic Via Insertion
- Insert vias when traces need to transition between front (F.Cu) and back (B.Cu) copper layers.
- Via parameters configurable: drill diameter, annular ring, via type (through-hole, blind, buried).
- Minimize via count while maintaining routability.
- All inserted vias must satisfy DRC clearance rules.

### FR-09: MCP Tool Endpoints
- **`route`:** Execute routing on a placed board with specified router and constraints. Supports `dry_run` mode.
- **`route_preview`:** Return a structured JSON preview of proposed routing (trace paths, via locations, net assignments) without modifying the board.
- **`get_routers`:** List available routing backends and their status (installed/available/configured).
- **`set_net_classes`:** Configure net class assignments and design rules.

## Non-Functional Requirements

| ID | Requirement | Metric |
|---|---|---|
| NFR-01 | **Performance** | Rust A* must route a 60-key matrix (rows + columns) in <10 seconds. |
| NFR-02 | **Testability** | All routing logic testable without KiCad or external router services (mock adapters). |
| NFR-03 | **Determinism** | Rust A* must produce identical results for identical inputs across all three integration modes. |
| NFR-04 | **DRC Compliance** | All routed boards must pass KiCad native DRC with zero errors. |
| NFR-05 | **Dry-Run Support** | All MCP routing endpoints must support dry-run mode with structured JSON previews. |

## Acceptance Criteria

- [ ] Multi-router dispatch routes a 60-key board using each of the three backends independently.
- [ ] Rust A* PyO3 binding routes a 60-key matrix in <10 seconds.
- [ ] Subprocess and REST modes produce identical routing output to PyO3 for the same input.
- [ ] FreeRouting DSN/SES round-trip produces a valid routed board.
- [ ] Quilter API integration handles authentication, routing, and result import.
- [ ] IPC-2152 track width calculator produces correct widths for 0.1A–3A range at 1oz copper.
- [ ] Net classes are assigned correctly and design rules enforced during routing.
- [ ] Vias are inserted correctly at layer transitions with DRC-compliant clearances.
- [ ] All MCP endpoints (`route`, `route_preview`, `get_routers`, `set_net_classes`) return valid structured JSON.
- [ ] Full pipeline test: KLE JSON → parse → place → route → DRC validate passes end-to-end.
- [ ] Test suite achieves >80% coverage with mocked pcbnew and router backends.

## Out of Scope

- Interactive routing visualization (future GUI track).
- Differential pair length matching beyond basic USB D+/D− constraints.
- Multi-layer routing beyond 2-layer (F.Cu + B.Cu) boards.
- Impedance-controlled routing for RF applications.
