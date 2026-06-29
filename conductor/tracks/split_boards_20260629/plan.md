# Implementation Plan: Split Ergonomic Board Support

## Phase 1: Split Geometry Model & Data Structures

- [ ] Task: Define split layout data models (`kbd_engine/split_models.py`)
    - [ ] Write tests for `HalfLayout` dataclass (origin, rotation, key matrix, thumb cluster config)
    - [ ] Write tests for `SplitLayout` dataclass containing left and right `HalfLayout` instances
    - [ ] Write tests for `ThumbClusterConfig` dataclass (style, key count, arc radius, fan angle, offset)
    - [ ] Write tests for `StaggerProfile` dataclass (per-column Y-offset array)
    - [ ] Implement all split data models with type hints and frozen dataclasses
    - [ ] Verify all tests pass

- [ ] Task: Implement symmetric mirroring engine (`kbd_engine/mirror.py`)
    - [ ] Write tests for mirroring a 5-column half across a vertical axis
    - [ ] Write tests for mirroring key rotations (angles negate across mirror axis)
    - [ ] Write tests for mirroring thumb cluster positions
    - [ ] Write tests for configurable mirror axis (vertical, horizontal)
    - [ ] Write tests for round-trip: mirror(mirror(half)) == original half
    - [ ] Implement `mirror_half(half: HalfLayout, axis: str) → HalfLayout`
    - [ ] Verify all tests pass

- [ ] Task: Implement columnar stagger engine (`kbd_engine/stagger.py`)
    - [ ] Write tests for Sofle stagger profile (pinky dropped ~6mm, index raised)
    - [ ] Write tests for Corne stagger profile (moderate 3-row columnar offsets)
    - [ ] Write tests for Dactyl Manuform stagger profile (curvature-derived offsets)
    - [ ] Write tests for custom stagger profile loading from JSON
    - [ ] Write tests for applying stagger offsets to a column of key positions
    - [ ] Implement `StaggerEngine` with built-in profiles and JSON extension
    - [ ] Create default stagger profiles (`kbd_engine/data/stagger_profiles.json`)
    - [ ] Verify all tests pass

- [ ] Task: Conductor - User Manual Verification 'Phase 1: Split Geometry Model & Data Structures' (Protocol in workflow.md)

## Phase 2: Thumb Cluster & Dactyl Projection

- [ ] Task: Implement thumb cluster placement (`kbd_engine/thumb_cluster.py`)
    - [ ] Write tests for arc layout: 3 keys along a 30mm radius arc
    - [ ] Write tests for linear row: 3 keys in a straight horizontal line
    - [ ] Write tests for fan layout: 4 keys fanned at 15° increments from a pivot
    - [ ] Write tests for configurable key count (2–6 keys) across all styles
    - [ ] Write tests for thumb cluster positioning relative to main matrix corner
    - [ ] Write tests for mirrored thumb cluster (left vs right half)
    - [ ] Implement `ThumbClusterPlacer` with arc, linear, and fan algorithms
    - [ ] Verify all tests pass

- [ ] Task: Implement Dactyl Manuform flat projection (`kbd_engine/dactyl_projection.py`)
    - [ ] Write tests for flat projection of a single column well with 15° curvature
    - [ ] Write tests for flat projection with row tenting angle (10°, 20°, 30°)
    - [ ] Write tests for variable curvature across columns (pinky vs index)
    - [ ] Write tests for projection preserving inter-key spacing in projected coordinates
    - [ ] Write tests for known Dactyl Manuform configurations producing expected XY positions
    - [ ] Implement projection math with documented coordinate system and DRC notes
    - [ ] Verify all tests pass

- [ ] Task: Conductor - User Manual Verification 'Phase 2: Thumb Cluster & Dactyl Projection' (Protocol in workflow.md)

## Phase 3: Split-Aware Placement Engine

- [ ] Task: Extend grid placer for split layouts (`kbd_engine/placer.py`)
    - [ ] Write tests for placing a Corne layout (21 keys per half, 42 total)
    - [ ] Write tests for placing a Sofle layout (30 keys per half, 60 total)
    - [ ] Write tests for symmetric mirroring producing correct mirrored positions
    - [ ] Write tests for independent half placement with different key counts
    - [ ] Write tests for diode and capacitor placement on both halves
    - [ ] Implement split-aware placement in `GridPlacer.place()` dispatching to `SplitPlacer`
    - [ ] Verify placement completes in <10 seconds for 70-key split layout (NFR-01)
    - [ ] Verify all tests pass

- [ ] Task: Implement split-specific component placement
    - [ ] Write tests for TRRS jack auto-placement on both halves (default positions)
    - [ ] Write tests for USB-C connector placement on master half only
    - [ ] Write tests for configurable master half (left or right)
    - [ ] Write tests for configurable TRRS/USB-C positions
    - [ ] Add TRRS and USB-C footprints to `FootprintRegistry` default mappings
    - [ ] Implement `SplitComponentPlacer` for connector auto-placement
    - [ ] Verify all tests pass

- [ ] Task: Conductor - User Manual Verification 'Phase 3: Split-Aware Placement Engine' (Protocol in workflow.md)

## Phase 4: Split KLE Parsing & Interconnect Routing

- [ ] Task: Extend KLE parser for split layouts (`kbd_engine/kle_parser.py`)
    - [ ] Write tests for detecting split layout via X-axis gap >2u between key groups
    - [ ] Write tests for mapping left key group to left `HalfLayout`
    - [ ] Write tests for mapping right key group to right `HalfLayout`
    - [ ] Write tests for explicit split markers in KLE metadata
    - [ ] Write tests for non-split KLE JSON still parsing correctly (backward compat)
    - [ ] Write tests for a full Corne KLE JSON and a full Sofle KLE JSON
    - [ ] Implement split detection and half-mapping in `parse_kle_json()`
    - [ ] Verify all tests pass

- [ ] Task: Implement interconnect net creation and routing
    - [ ] Write tests for I2C net creation (SPLIT_SDA, SPLIT_SCL, SPLIT_VCC, SPLIT_GND)
    - [ ] Write tests for serial net creation (SPLIT_TX, SPLIT_RX)
    - [ ] Write tests for net assignment to TRRS jack pads and MCU pins
    - [ ] Write tests for `Interconnect` net class with correct clearance and track width
    - [ ] Implement interconnect net factory and net class registration
    - [ ] Verify interconnect traces route through the routing pipeline without DRC errors
    - [ ] Verify all tests pass

- [ ] Task: Conductor - User Manual Verification 'Phase 4: Split KLE Parsing & Interconnect Routing' (Protocol in workflow.md)

## Phase 5: Dual PCB Output & MCP Integration

- [ ] Task: Implement dual PCB output modes
    - [ ] Write tests for separate PCB output generating two independent .kicad_pcb files
    - [ ] Write tests for each half-PCB passing DRC independently
    - [ ] Write tests for panelized output with configurable gap (2mm default)
    - [ ] Write tests for break-away line generation (V-score Edge.Cuts geometry)
    - [ ] Write tests for panel outline (Edge.Cuts) encompassing both halves
    - [ ] Implement `SplitBoardWriter` with `write_separate()` and `write_panel()` methods
    - [ ] Verify all tests pass

- [ ] Task: Extend MCP endpoints for split board support
    - [ ] Write tests for `place` endpoint with `layout_type="split_symmetric"`
    - [ ] Write tests for `place` endpoint with `layout_type="split_independent"`
    - [ ] Write tests for `route` endpoint with `output_mode="separate"` and `"panel"`
    - [ ] Write tests for `configure_split` endpoint setting thumb cluster and stagger profile
    - [ ] Write tests for `master_half` parameter on route/place endpoints
    - [ ] Write tests for backward compatibility: existing single-board calls unaffected
    - [ ] Implement all split MCP endpoint extensions
    - [ ] Verify all tests pass with dry-run support

- [ ] Task: End-to-end integration tests
    - [ ] Write integration test: Corne KLE JSON → split parse → place → route → DRC (separate output)
    - [ ] Write integration test: Sofle symmetric mirror → place → route → DRC (panelized output)
    - [ ] Write integration test: Dactyl Manuform projection → place → verify coordinate accuracy
    - [ ] Write integration test: TRRS + USB-C placement → interconnect routing → DRC
    - [ ] Run `pytest --cov=kbd_engine --cov-report=html` and verify >80% coverage
    - [ ] Run `ruff check kbd_engine/ tests/` and verify zero errors
    - [ ] Run `mypy kbd_engine/` and verify zero errors

- [ ] Task: Conductor - User Manual Verification 'Phase 5: Dual PCB Output & MCP Integration' (Protocol in workflow.md)
