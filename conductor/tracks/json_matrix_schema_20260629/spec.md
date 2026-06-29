# Specification: Custom JSON Matrix Definition Parser and Schema

## Overview

This track defines and implements a robust, custom JSON schema tailored specifically for keyboard layout generation. While KLE JSON is widely used, it lacks native concepts for electrical routing (rows/cols) and advanced ergonomics (curves, arcs). This custom schema fills that gap, serving as the native data format for the core engine.

The schema is built and validated using Pydantic, supports advanced ergonomic geometry, handles hybrid electrical matrix assignments, and supports full bidirectional serialization.

## Functional Requirements

### FR-01: Pydantic Schema Definition
- Implement the core JSON schema using Pydantic v2 data models (`BaseModel`).
- The schema must strictly type all layout properties (X/Y coordinates, rotation, dimensions, component overrides).
- Support export of the schema as an OpenAPI/JSON Schema standard document for consumption by the Web Editor.

### FR-02: Advanced Geometry Support
- Extend the basic X/Y/Rotation coordinate system to support advanced geometries common in split/ergo boards:
  - **Arcs:** Define key placements along a calculated radius.
  - **Bezier Curves:** Define thumb clusters along a curve.
  - **Clusters/Groups:** Group keys logically so they can be rotated and translated as a single unit (e.g., rotating an entire thumb cluster by 15 degrees).

### FR-03: Hybrid Matrix Auto-Calculation
- The schema must support explicit `matrix_row` and `matrix_col` integers for every key.
- Implement a heuristic auto-calculation pass: if a key omits explicit row/col assignments, the engine calculates them based on the physical X/Y grid position relative to other keys.
- Allow users to define a custom matrix mapping strategy in the schema root (e.g., "strict grid", "staggered column fallback").

### FR-04: Full Bidirectional Serialization
- Provide a `parse_json()` method to securely ingest and validate layout files into the engine's internal `LayoutModel`.
- Provide a `to_json()` method to serialize the engine's internal `LayoutModel` back out to the custom JSON format.
- Ensure that parsing and re-serializing a file results in structurally equivalent output (idempotency).

### FR-05: Validation and Error Reporting
- Pydantic validation must gracefully handle invalid data types, missing required fields, and out-of-bounds geometry.
- Return structured error messages (line numbers, field names) that the Web Editor or MCP server can display to the user.

## Non-Functional Requirements

| ID | Requirement | Metric |
|---|---|---|
| NFR-01 | **Validation Speed** | Pydantic validation of a 120-key layout must complete in < 50ms. |
| NFR-02 | **Extensibility** | The Pydantic models must use `extra="allow"` (or explicit extension fields) to allow third-party plugins to embed custom data without failing validation. |
| NFR-03 | **Type Safety** | The module must achieve 100% strict type checking passing under `mypy`. |

## Acceptance Criteria

- [ ] Pydantic models are fully defined for Keys, Clusters, and the Root Layout.
- [ ] A valid JSON file parses successfully into the Python objects.
- [ ] An invalid JSON file raises a clear, structured `ValidationError`.
- [ ] Advanced geometry (e.g., an arc of keys) correctly calculates the final absolute X/Y/Rotation for the placement engine.
- [ ] Keys missing explicit row/col assignments have them correctly auto-calculated based on spatial heuristics.
- [ ] A parsed layout can be serialized back to JSON without data loss.
- [ ] The JSON Schema export function successfully generates a valid `.schema.json` file for frontend consumption.

## Out of Scope

- Writing a parser for QMK `info.json` or ZMK `.keymap` files (this schema is exclusively for the physical PCB layout, not firmware configuration).
