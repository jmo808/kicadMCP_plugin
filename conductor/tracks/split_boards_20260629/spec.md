# Specification: Split Ergonomic Board Support (Dactyl Manuform, Sofle, Lily58)

## Overview

This track extends the placement and routing engines to support split ergonomic keyboard layouts. It introduces a dual-half geometry model with independent coordinate systems, adds thumb cluster placement algorithms, supports three major split form factors (Sofle/Lily58, Corne, Dactyl Manuform), and handles split-specific components (TRRS jacks, USB-C connectors) with automated interconnect routing.

The output model supports both separate per-half PCB files (the production standard for split boards) and a single panelized board with break-away tabs.

## Functional Requirements

### FR-01: Split Board Geometry Model
- Introduce a `SplitLayout` model that contains two `HalfLayout` instances (left and right).
- Each `HalfLayout` has its own independent coordinate origin, rotation, and key matrix.
- **Symmetric mirroring mode:** Define one half and auto-generate the mirrored counterpart. Mirror axis is configurable (default: vertical).
- **Independent mode:** Each half defined separately with its own key count, stagger pattern, and thumb cluster configuration.
- Both modes must produce identical data structures downstream (the placer and router see two `HalfLayout` objects regardless of how they were defined).

### FR-02: Thumb Cluster Placement
- Dedicated thumb cluster placement algorithm supporting:
  - **Arc layout:** Keys arranged along a curved arc (Dactyl Manuform style).
  - **Linear row:** Keys in a straight horizontal row (Corne style).
  - **Fan layout:** Keys fanned outward from a pivot point (Sofle/Lily58 style).
- Configurable parameters: key count (2–6 keys), arc radius, fan angle, offset from main matrix.
- Thumb cluster position is relative to the bottom-right (left half) or bottom-left (right half) of the main column matrix.

### FR-03: Columnar Stagger Engine
- Extend the grid placer to support per-column vertical stagger offsets (columnar stagger).
- Pre-built stagger profiles for common layouts:
  - **Sofle/Lily58:** Aggressive columnar stagger with pinky column dropped ~6mm.
  - **Corne:** Moderate columnar stagger, compact 3-row format.
  - **Dactyl Manuform:** Variable curvature-derived offsets (flat projection of 3D column wells).
- Custom stagger profiles definable via JSON (per-column Y-offset array).

### FR-04: Dactyl Manuform Flat Projection
- Accept Dactyl Manuform configuration parameters (column curvature, row tenting angle, key well depth).
- Compute flat PCB projection coordinates from 3D curved geometry.
- Generate placement positions that, when assembled into a curved case, align with the Dactyl Manuform key wells.
- Document the projection math with units (mm) and coordinate system assumptions.

### FR-05: Split-Specific Component Placement
- **TRRS/TRS jack:** Auto-place 3.5mm audio jack footprint on both halves for half-to-half serial communication. Configurable position (default: top-right of left half, top-left of right half).
- **USB-C connector:** Auto-place USB-C receptacle on the master half (configurable: left or right). Position defaults to top-center of the designated master half.
- Add TRRS and USB-C footprints to the `FootprintRegistry` with default library references.

### FR-06: Interconnect Net Routing
- Automatically create I2C/serial communication nets between the TRRS jack pads and the MCU.
- Net names follow convention: `SPLIT_SDA`, `SPLIT_SCL`, `SPLIT_VCC`, `SPLIT_GND` for I2C; `SPLIT_TX`, `SPLIT_RX` for serial.
- Route interconnect traces through the routing pipeline (respects net classes and DRC).
- Interconnect nets assigned to a dedicated `Interconnect` net class with appropriate clearance and width.

### FR-07: Dual PCB Output
- **Separate PCBs mode:** Generate independent `.kicad_pcb` files for left and right halves. Each file is a complete, standalone board.
- **Panelized mode:** Generate a single `.kicad_pcb` file containing both halves with:
  - Configurable gap between halves (default: 2mm).
  - V-score or mouse-bite break-away line between halves.
  - Panel outline (Edge.Cuts) encompassing both halves.
- Output mode selectable via MCP tool parameter (`output="separate"` | `"panel"`).

### FR-08: KLE JSON Split Layout Parsing
- Extend the KLE parser to detect and handle split layout KLE JSON files.
- Split detection heuristic: gap >2u between key groups along the X-axis.
- Map left/right key groups to `HalfLayout` instances.
- Support explicit split markers in KLE metadata (if present).

### FR-09: MCP Tool Endpoint Extensions
- Extend existing `place` and `route` MCP endpoints with split-aware parameters:
  - `layout_type`: `"single"` | `"split_symmetric"` | `"split_independent"`
  - `output_mode`: `"separate"` | `"panel"`
  - `master_half`: `"left"` | `"right"`
- New endpoint: **`configure_split`** — Set split-specific parameters (thumb cluster style, stagger profile, interconnect components).
- All split endpoints support `dry_run` mode.

## Non-Functional Requirements

| ID | Requirement | Metric |
|---|---|---|
| NFR-01 | **Performance** | Split board placement (both halves) must complete in <10 seconds for a 70-key layout. |
| NFR-02 | **Testability** | All split geometry math testable without KiCad (pure coordinate calculations). |
| NFR-03 | **Backward Compatibility** | Existing single-board workflows must be unaffected. Split features are opt-in. |
| NFR-04 | **DRC Compliance** | Both halves (separate or panelized) must pass KiCad DRC independently. |

## Acceptance Criteria

- [ ] Symmetric mirroring produces correct left/right halves from a single-half definition.
- [ ] Independent mode accepts two separate half definitions with different key counts.
- [ ] Sofle-style layout places 30 keys per half with correct columnar stagger and 4-key thumb fan.
- [ ] Corne-style layout places 21 keys per half (3x6 + 3 thumb) with moderate stagger.
- [ ] Dactyl Manuform flat projection produces valid PCB coordinates from 3D curvature parameters.
- [ ] TRRS jack and USB-C connector are auto-placed at correct positions on each half.
- [ ] Interconnect traces (I2C) route correctly between TRRS jack and MCU pads.
- [ ] Separate PCB output generates two valid, independent `.kicad_pcb` files.
- [ ] Panelized output generates a single board with break-away line and correct panel outline.
- [ ] KLE parser correctly splits a Corne/Sofle KLE JSON into left and right halves.
- [ ] All MCP split endpoints return valid structured JSON with dry-run support.
- [ ] Test suite achieves >80% coverage for all split-related modules.

## Out of Scope

- Wireless split support (Bluetooth/ZMK firmware integration).
- 3D case generation or enclosure design.
- RGB LED per-key placement and routing.
- More than 2-half splits (unibody splits like Kyria are treated as single boards with stagger).
