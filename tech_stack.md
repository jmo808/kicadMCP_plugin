# Technical Stack & Environment Rules

## Runtime & System Frameworks
* **Primary Environment:** Python 3.11+ running inside the native KiCad 9.0+ `pcbnew` Python shell.
* **Key Interoperability Interface:** Model Context Protocol (MCP) server spec via `mixelpixx/KiCAD-MCP-Server` and `Seeed-Studio/kicad-mcp-server`.
* **Routing Core Engine:** High-performance Rust-accelerated $A^*$ pathfinding engine or Quilter API integrations.
* **Standard Schematics Specification:** S-expression based `.kicad_sch` and `.kicad_pcb` formats.

## Guardrails & Engineering Standards
* **IPC Standard Adherence:** Automatically calculate track widths and spacing constraints using strict IPC-2152 current capacity matrices.
* **DRC Rigor:** Code generated must compile under rigid Design Rule Checks (DRC) natively without short-circuits or isolated unrouted nets.
* **Code Integrity:** All Python scripts interfacing with `pcbnew` must use absolute coordinates and clean vector structures to avoid overlapping footprints.
