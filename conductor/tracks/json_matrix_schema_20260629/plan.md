# Implementation Plan: Custom JSON Matrix Definition Parser and Schema

## Phase 1: Pydantic Schema Definition

- [ ] Task: Define base Pydantic models (`kbd_engine/schema/models.py`)
    - [ ] Write tests for valid and invalid basic JSON layouts
    - [ ] Write tests ensuring strict typing for coordinates (float), rotations (float), and dimensions
    - [ ] Implement `KeyModel`, `ClusterModel`, and `LayoutModel` using Pydantic `BaseModel`
    - [ ] Implement `extra="allow"` configuration for third-party extensions
    - [ ] Verify all tests pass

- [ ] Task: Conductor - User Manual Verification 'Phase 1: Pydantic Schema Definition' (Protocol in workflow.md)

## Phase 2: Advanced Geometry & Cluster Resolution

- [ ] Task: Implement Geometry Resolver (`kbd_engine/schema/geometry.py`)
    - [ ] Write tests for resolving nested cluster absolute coordinates
    - [ ] Write tests for resolving arc-based positioning (polar to cartesian conversion)
    - [ ] Write tests for resolving bezier curve positioning for thumb clusters
    - [ ] Implement geometry traversal to flatten all keys into an absolute X/Y/Rot coordinate space
    - [ ] Verify all tests pass

- [ ] Task: Conductor - User Manual Verification 'Phase 2: Advanced Geometry & Cluster Resolution' (Protocol in workflow.md)

## Phase 3: Hybrid Matrix Auto-Calculation Heuristics

- [ ] Task: Implement Matrix Calculator (`kbd_engine/schema/matrix.py`)
    - [ ] Write tests for layouts with explicit row/col assignments (pass-through)
    - [ ] Write tests for basic ortholinear grid heuristic calculation (based on bounding boxes)
    - [ ] Write tests for staggered column heuristic calculation
    - [ ] Implement the `calculate_missing_matrix_pins()` logic, updating the flattened key models
    - [ ] Verify all tests pass

- [ ] Task: Conductor - User Manual Verification 'Phase 3: Hybrid Matrix Auto-Calculation Heuristics' (Protocol in workflow.md)

## Phase 4: Full Bidirectional Serialization & Export

- [ ] Task: Implement Serialization Methods (`kbd_engine/schema/serializer.py`)
    - [ ] Write tests validating that `LayoutModel.model_validate_json()` parses successfully
    - [ ] Write tests validating that `LayoutModel.model_dump_json()` matches the original structural input (idempotency)
    - [ ] Implement the bidirectional serialization wrappers if needed for engine edge cases
    - [ ] Implement the JSON Schema Generator endpoint (`generate_schema.py`) to export the OpenAPI definition
    - [ ] Verify all tests pass

- [ ] Task: Conductor - User Manual Verification 'Phase 4: Full Bidirectional Serialization & Export' (Protocol in workflow.md)

## Phase 5: Integration & Validation Polish

- [ ] Task: End-to-End Pipeline Integration
    - [ ] Write integration test: Parse complex layout -> Resolve Geometry -> Calculate Matrix -> Dump to JSON
    - [ ] Integrate the Pydantic parser into the core `placement_pipeline` (replacing or running alongside KLE parser)
    - [ ] Ensure validation errors are gracefully caught and returned in the MCP Server/Bridge Server
    - [ ] Verify 100% type safety with `mypy` across the `schema` module
    - [ ] Verify >80% test coverage

- [ ] Task: Conductor - User Manual Verification 'Phase 5: Integration & Validation Polish' (Protocol in workflow.md)
