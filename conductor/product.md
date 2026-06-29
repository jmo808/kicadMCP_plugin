# Initial Concept

KiCad Keyboard Automation Engine — a Python plugin for KiCad 9.0+ that translates standard alphanumeric matrix layouts directly into perfectly placed, DRC-compliant, routed KiCad footprints. It targets hardware engineers and custom keyboard designers requiring low-latency layout generation without repetitive trace routing manual overhead.

Core capabilities include algorithmic grid placement for switches/diodes/capacitors, a component abstraction layer for mixed footprint types (PTH vs SMD, MX hot-swap vs soldered), and an automated trace routing pipeline interfacing with high-throughput external routers (Rust A* or Quilter).

---

# Product Guide: KiCad Keyboard Automation Engine

## Vision Statement
Eliminate the tedious, error-prone manual workflow of laying out custom mechanical keyboard PCBs. The KiCad Keyboard Automation Engine is an AI-assisted, MCP server-driven plugin that transforms a high-level keyboard layout definition into a fully placed, DRC-compliant, routed KiCad PCB — from matrix specification to finished board in minutes, not hours.

## Target Audience
- **Hardware engineers** building production-grade custom keyboards who need repeatable, constraint-correct layout generation.
- **Custom keyboard designers** in the enthusiast community who iterate rapidly on split, ortholinear, and staggered layouts without deep PCB design expertise.
- **AI-assisted design workflows** where an MCP client (such as an LLM agent) orchestrates end-to-end PCB generation programmatically.

## Interaction Model
The primary interface is an **MCP (Model Context Protocol) server** that exposes keyboard automation capabilities as tool endpoints. This enables:
- LLM agents and AI assistants to orchestrate KiCad operations programmatically.
- Programmatic integration with external toolchains and CI pipelines.
- A complementary **interactive KiCad dialog** for users who prefer a GUI-driven workflow within the KiCad environment.

## Supported Keyboard Layouts
The engine supports all major keyboard form factors at launch:
1. **Standard staggered QWERTY** — TKL, 60%, 65%, 75%, and full-size.
2. **Ortholinear / columnar stagger** — Planck, Preonic, Corne-style grid and column-stagger layouts.
3. **Split ergonomic boards** — Dactyl Manuform, Sofle, Lily58, and similar split designs with independent halves.

## Input Formats
Users can define their keyboard layout through three complementary input methods:
1. **KLE (Keyboard Layout Editor) JSON import** — Parse exports from keyboard-layout-editor.com directly, providing instant compatibility with thousands of existing community layouts.
2. **Custom JSON matrix definition** — A structured JSON schema describing rows, columns, key unit sizes, rotation angles, and per-key component type overrides.
3. **Interactive KiCad dialog** — A GUI panel within KiCad for specifying layout parameters, selecting component footprints, and previewing placement before committing.

## Core Capabilities

### 1. Algorithmic Grid Placement Engine
- Auto-compute X/Y coordinates for switches, diodes, and bypass capacitors using parametric layout metadata.
- Support key unit sizing (1u, 1.25u, 1.5u, 2u, etc.), rotation, and stagger offsets.
- Handle split board geometry with independent coordinate systems per half.

### 2. Component Abstraction Layer
- Natively handle mixed-type footprints: PTH vs. SMD diodes (e.g., 1N4148 through-hole vs. SOD-123), MX-style hot-swap sockets vs. soldered pins.
- Provide a footprint registry that maps logical component types to physical KiCad footprint libraries.
- Support per-key component type overrides for hybrid builds.

### 3. Automated Trace Routing Pipeline
- Generate row and column net traces for the switch-diode matrix.
- Programmatic interface to offload complex routing to high-throughput external engines:
  - **Rust A* pathfinding engine** for deterministic, high-performance trace routing.
  - **Quilter API** for advanced autorouting with constraint satisfaction.
- IPC-2152 compliant track width and spacing calculations.

### 4. MCP Server Interface
- Expose all automation capabilities as MCP tool endpoints.
- Support stateful session management for multi-step PCB generation workflows.
- Provide progress reporting and error diagnostics through MCP protocol.

## Design Constraints
- All generated PCBs must pass KiCad's native DRC without errors (no short circuits, no unrouted nets, no clearance violations).
- Python scripts interfacing with `pcbnew` must use absolute coordinates and clean vector math.
- The engine targets **KiCad 9.0+** and **Python 3.11+** running in KiCad's native Python environment.

## Release Scope (v1.0)
The first release is a **full pipeline** delivery:
- Algorithmic placement of all matrix components.
- Automated row/column matrix trace routing.
- External router integration (Rust A* / Quilter).
- MCP server with complete tool endpoint coverage.
- KLE JSON import as the primary input format.
