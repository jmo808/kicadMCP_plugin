# Specification: Component Abstraction Layer and Footprint Registry

## Overview

This track establishes the Component Abstraction Layer and Footprint Registry, which serve as the bridge between logical keyboard components (e.g., "Switch", "Diode", "MCU") and physical KiCad footprint models on the PCB. It ensures that the placement and routing pipelines are decoupled from hardcoded footprint names, supporting mixed-type (hybrid) builds and custom libraries.

The registry is configured via JSON, strictly validates footprint existence before placement (Fail Fast), and prioritizes a bundled custom `.pretty` footprint library while falling back to standard KiCad libraries.

## Functional Requirements

### FR-01: JSON Footprint Registry
- Implement a `FootprintRegistry` class that loads mappings from a `registry.json` file.
- The JSON schema must map logical component types to KiCad footprint references (e.g., `"switch_mx_hotswap": "kbd_custom:SW_Cherry_MX_1.00u_HotSwap"`).
- Support defining default footprints for base component classes (e.g., default diode, default switch).

### FR-02: Custom Bundled `.pretty` Library
- Create a bundled `kbd_custom.pretty` KiCad footprint library distributed with the plugin.
- The registry must prioritize resolving footprints from this custom library.
- If a requested footprint is not in the custom library, gracefully fallback to standard KiCad libraries (e.g., `Button_Switch_Keyboard`, `Diode_SMD`).

### FR-03: Strict Pre-validation (Fail Fast)
- Implement a pre-flight check in the placement pipeline that interrogates the KiCad `pcbnew` footprint table.
- Before any components are placed, verify that every required footprint (base defaults + all overrides) exists and is accessible.
- If a footprint is missing, abort the operation immediately and return a structured error detailing the missing footprint and the logical keys requesting it.

### FR-04: Hybrid Component Overrides
- Support per-key footprint overrides to allow mixed-type builds (e.g., a board that is 90% SMD diodes but requires PTH diodes on the thumb cluster due to space constraints).
- **Embedded Properties:** Parse custom footprint override properties directly from KLE JSON metadata or Custom Layout JSON.
- **Explicit Override Map:** Accept a dictionary in the MCP placement request mapping specific key IDs (e.g., `Row0_Col3`) to logical footprint types (e.g., `diode_pth`).
- Resolution priority: Explicit Override Map > Embedded Property > Global Default.

### FR-05: Component Instantiation Abstraction
- Provide a factory pattern (`ComponentFactory`) that uses the registry to instantiate `pcbnew` Footprint objects.
- Ensure correct pad numbering/naming is abstracted (e.g., mapping logical "pin 1" to the footprint's specific pad designation).
- Support rotation and reference designator assignment (`SW1`, `D1`, etc.) during instantiation.

## Non-Functional Requirements

| ID | Requirement | Metric |
|---|---|---|
| NFR-01 | **Fail-Fast Reliability** | Pre-validation must catch 100% of missing footprint errors before modifying the `.kicad_pcb` file. |
| NFR-02 | **Performance** | Registry loading and footprint pre-validation must complete in < 500ms. |
| NFR-03 | **Testability** | The registry and validation logic must be testable using mocked `pcbnew` library tables without requiring a full KiCad installation. |

## Acceptance Criteria

- [ ] `registry.json` is successfully parsed into the internal registry model.
- [ ] Footprint resolution correctly prioritizes the bundled `kbd_custom.pretty` library over KiCad defaults.
- [ ] Strict pre-validation correctly identifies an intentionally missing footprint and aborts execution.
- [ ] Pre-validation succeeds when all footprints are available.
- [ ] Per-key overrides via KLE JSON metadata are correctly resolved during placement.
- [ ] Per-key overrides via explicit mapping in the request are correctly resolved and take precedence.
- [ ] `ComponentFactory` successfully instantiates valid `pcbnew.Footprint` objects with correctly assigned reference designators.
- [ ] Test suite for the registry and abstraction layer achieves >80% coverage.

## Out of Scope

- Designing 3D models (`.step`/`.wrl`) for the custom footprints (only the 2D PCB footprints are required).
- Generating entirely procedural/parametric footprints in code (we are using static `.kicad_mod` files).
