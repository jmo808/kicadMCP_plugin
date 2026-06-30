# Implementation Plan: Automated Trace Routing Pipeline with Multi-Router Dispatch

## Phase 1: Routing Foundation & Data Models [checkpoint: f43ee64]

- [x] Task: Define routing data models (`kbd_engine/routing_models.py`) (e972594)
    - [x] Write tests for `RoutingRequest` dataclass (board geometry, netlist, constraints, router selection)
    - [x] Write tests for `RoutingResult` dataclass (trace paths, via locations, unrouted nets, diagnostics)
    - [x] Write tests for `NetClass` dataclass (name, track width, clearance, via diameter)
    - [x] Write tests for `TraceSegment` and `Via` dataclasses (start/end points, layer, width)
    - [x] Implement all routing data models with type hints and frozen dataclasses
    - [x] Verify all tests pass

- [x] Task: Define Router protocol and dispatch interface (`kbd_engine/router.py`) (12a7a43)
    - [x] Write tests for `Router` ABC with `route(request) → RoutingResult` contract
    - [x] Write tests for `RouterDispatch` selecting router by name (`rust_astar`, `quilter`, `freerouting`)
    - [x] Write tests for error handling when unknown router name is requested
    - [x] Write tests for structured error responses with unrouted nets and constraint violations
    - [x] Implement `Router` ABC and `RouterDispatch` class
    - [x] Verify all tests pass

- [x] Task: Implement IPC-2152 track width calculator (`kbd_engine/ipc2152.py`) (988b3fb)
    - [x] Write tests for track width calculation at 0.1A, 0.5A, 1A, and 3A with 1oz copper
    - [x] Write tests for different copper weights (0.5oz, 1oz, 2oz)
    - [x] Write tests for configurable temperature rise (10°C, 20°C)
    - [x] Write tests for edge cases (zero current, negative values raise errors)
    - [x] Implement IPC-2152 calculation functions
    - [x] Verify all tests pass

- [x] Task: Implement net class assignment engine (`kbd_engine/net_classes.py`) (f4e4c15)
    - [x] Write tests for default net class definitions (MatrixRow, MatrixCol, Power, USB, Signal)
    - [x] Write tests for assigning net classes to nets based on net name patterns
    - [x] Write tests for loading custom net class definitions from JSON
    - [x] Write tests for applying net classes to KiCad board via pcbnew adapter
    - [x] Implement `NetClassManager` with default definitions and JSON extension
    - [x] Create default net class config (`kbd_engine/data/default_net_classes.json`)
    - [x] Verify all tests pass

- [x] Task: Conductor - User Manual Verification 'Phase 1: Routing Foundation & Data Models' (Protocol in workflow.md) (f43ee64)

## Phase 2: Rust A* Routing Engine [checkpoint: 6ef490e]

- [x] Task: Scaffold Rust A* routing crate (`kbd_router/`) (7841ba6)
    - [x] Initialize Rust workspace with `cargo init --lib kbd_router`
    - [x] Add dependencies: `serde`, `serde_json`, `pyo3` (optional feature)
    - [x] Define Rust data structures mirroring Python routing models (Grid, Net, Obstacle, RouteResult)
    - [x] Write Rust unit tests for data structure serialization/deserialization
    - [x] Verify `cargo test` passes

- [x] Task: Implement A* pathfinding core in Rust (`kbd_router/src/astar.rs`) (9a34b9b)
    - [x] Write Rust tests for A* routing a single 2-point net on an empty grid
    - [x] Write Rust tests for routing around rectangular obstacles
    - [x] Write Rust tests for multi-net routing with net ordering
    - [x] Write Rust tests for via insertion at layer transitions (F.Cu ↔ B.Cu)
    - [x] Write Rust tests for routing failure (no valid path) returning diagnostics
    - [x] Implement grid-based A* with obstacle avoidance, layer transitions, and via insertion
    - [x] Verify all Rust tests pass

- [x] Task: Build PyO3 FFI binding (`kbd_router/src/python.rs`) (902f19e)
    - [x] Configure PyO3 in `Cargo.toml` with `pyo3/extension-module` feature
    - [x] Write Python tests calling Rust router via PyO3 for a simple 4-net routing
    - [x] Implement PyO3 module exposing `route_board(request_json: str) → str` function
    - [x] Write Python tests verifying identical output to Rust-native tests
    - [x] Build wheel with `maturin develop` and verify import in Python
    - [x] Verify all tests pass

- [x] Task: Build subprocess + JSON I/O CLI (`kbd_router/src/bin/cli.rs`) (df68fa9)
    - [x] Write Rust integration test for CLI reading JSON from stdin and writing result to stdout
    - [x] Write Python tests calling CLI subprocess and parsing JSON output
    - [x] Implement `kbd-router-cli` binary with JSON stdin/stdout interface
    - [x] Write Python tests verifying identical output between PyO3 and subprocess modes
    - [x] Verify all tests pass

- [x] Task: Build REST API wrapper (`kbd_router/src/bin/server.rs`) (24499b0)
    - [x] Add `axum` or `actix-web` dependency for HTTP server
    - [x] Write Rust integration test for POST `/route` endpoint
    - [x] Write Python tests calling REST API and verifying JSON response matches PyO3 output
    - [x] Implement lightweight HTTP server with `/route` POST endpoint
    - [x] Verify all tests pass

- [x] Task: Implement Python adapter for Rust A* router (`kbd_engine/routers/rust_astar.py`) (daf0b25)
    - [x] Write tests for PyO3 mode routing a 60-key matrix
    - [x] Write tests for subprocess fallback when PyO3 import fails
    - [x] Write tests for REST mode routing via HTTP client
    - [x] Write tests for mode auto-detection (PyO3 → subprocess → REST)
    - [x] Implement `RustAstarRouter(Router)` with configurable integration mode
    - [x] Verify all tests pass
    - [x] Verify 60-key matrix routes in <10 seconds via PyO3 (NFR-01) (be89c39)

- [x] Task: Conductor - User Manual Verification 'Phase 2: Rust A* Routing Engine' (Protocol in workflow.md) (6ef490e)

## Phase 3: External Router Integrations

- [ ] Task: Implement FreeRouting integration (`kbd_engine/routers/freerouting.py`)
    - [ ] Write tests for DSN export from placed board (Specctra Design format)
    - [ ] Write tests for FreeRouting subprocess invocation with timeout handling
    - [ ] Write tests for SES import parsing routed traces back to internal model
    - [ ] Write tests for error handling (FreeRouting not installed, routing timeout, partial routing)
    - [ ] Implement `FreeRoutingRouter(Router)` with DSN export → subprocess → SES import pipeline
    - [ ] Create DSN/SES serializer/deserializer utilities
    - [ ] Verify all tests pass

- [ ] Task: Implement Quilter API integration (`kbd_engine/routers/quilter.py`)
    - [ ] Write tests for Quilter API authentication flow
    - [ ] Write tests for board geometry and constraint serialization to Quilter format
    - [ ] Write tests for routing result deserialization from Quilter response
    - [ ] Write tests for error handling (auth failure, rate limiting, timeout, partial routing)
    - [ ] Implement `QuilterRouter(Router)` with REST client, auth, and result mapping
    - [ ] Verify all tests pass with mocked HTTP responses

- [ ] Task: Conductor - User Manual Verification 'Phase 3: External Router Integrations' (Protocol in workflow.md)

## Phase 4: Via Insertion & Board Writing

- [ ] Task: Implement via insertion engine (`kbd_engine/via_inserter.py`)
    - [ ] Write tests for via insertion at layer transition points in routing result
    - [ ] Write tests for configurable via parameters (drill diameter, annular ring, via type)
    - [ ] Write tests for via DRC compliance (clearance to pads, tracks, board edge)
    - [ ] Write tests for via count minimization (merge nearby transition points)
    - [ ] Implement `ViaInserter` class processing RoutingResult and inserting optimal vias
    - [ ] Verify all tests pass

- [ ] Task: Integrate routing results with pcbnew adapter
    - [ ] Write tests for `apply_routing()` writing TraceSegments and Vias to board via adapter
    - [ ] Write tests for dry-run mode returning preview without modifying board
    - [ ] Write tests for applying net classes to board before routing
    - [ ] Implement `apply_routing(result, adapter, dry_run=False)` function
    - [ ] Implement `apply_net_classes(net_class_manager, adapter)` function
    - [ ] Verify all tests pass with mocked pcbnew

- [ ] Task: Conductor - User Manual Verification 'Phase 4: Via Insertion & Board Writing' (Protocol in workflow.md)

## Phase 5: MCP Endpoints & End-to-End Integration

- [ ] Task: Implement MCP routing tool endpoints
    - [ ] Write tests for `route` endpoint (placed board + router selection → routed board)
    - [ ] Write tests for `route` endpoint with `dry_run=True` returning JSON preview
    - [ ] Write tests for `route_preview` endpoint returning trace paths and via locations
    - [ ] Write tests for `get_routers` endpoint listing available backends and status
    - [ ] Write tests for `set_net_classes` endpoint configuring net class rules
    - [ ] Write tests for error responses on routing failures (structured JSON with diagnostics)
    - [ ] Implement all MCP routing endpoints in `kbd_engine/mcp_server.py`
    - [ ] Verify all tests pass

- [ ] Task: End-to-end integration tests
    - [ ] Write integration test: KLE JSON → parse → place → route (Rust A*) → DRC validate
    - [ ] Write integration test: MCP `route` with each backend (Rust A*, FreeRouting mock, Quilter mock)
    - [ ] Write integration test: MCP `route` with `dry_run=True` returns valid preview JSON
    - [ ] Write integration test: Full pipeline with net class assignment and via insertion
    - [ ] Write integration test: Routing failure returns actionable error with unrouted net details
    - [ ] Run `pytest --cov=kbd_engine --cov-report=html` and verify >80% coverage
    - [ ] Run `ruff check kbd_engine/ tests/` and verify zero errors
    - [ ] Run `mypy kbd_engine/` and verify zero errors
    - [ ] Run `cargo test` on `kbd_router/` and verify all Rust tests pass

- [ ] Task: Conductor - User Manual Verification 'Phase 5: MCP Endpoints & End-to-End Integration' (Protocol in workflow.md)
