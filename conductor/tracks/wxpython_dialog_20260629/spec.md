# Specification: Interactive KiCad wxPython Dialog

## Overview

This track delivers a native wxPython GUI dialog that runs inside KiCad's `pcbnew` environment. It provides a guided, step-by-step wizard interface for users who prefer working directly within KiCad rather than using external MCP clients or the web editor. The dialog supports layout loading, footprint configuration, visual previewing, and execution of the placement and routing pipelines.

## Functional Requirements

### FR-01: wxPython Plugin Integration
- Register the dialog as a native KiCad Action Plugin (appears in the "Tools -> External Plugins" menu).
- Build the UI using native wxPython widgets (`wx.Dialog`, `wx.Panel`, `wx.Notebook`, etc.) targeting compatibility with KiCad 9.0's embedded wxPython environment.

### FR-02: Wizard Execution Flow
- Implement a step-by-step `wx.adv.Wizard` (or custom multi-page flow) to guide the user:
  - **Step 1: Input** — Load layout definition.
  - **Step 2: Configuration** — Assign footprints (global + overrides).
  - **Step 3: Preview & Place** — Visual preview and execution of `placement_pipeline`.
  - **Step 4: Route** — Router selection and execution of `routing_pipeline`.

### FR-03: Layout Input Methods
- **File Picker:** Browse and load KLE JSON or Custom Layout JSON from disk.
- **Text Input:** A `wx.TextCtrl` multiline area to paste raw KLE JSON strings.
- **Web Editor Sync:** A "Sync from Web Editor" button that connects to the local WebSocket Bridge (Track 4) to fetch the active layout automatically.

### FR-04: Component Configuration
- **Global Defaults:** Dropdowns to select default footprints for switches, diodes, TRRS jacks, and MCUs. Dropdowns auto-populate from the `FootprintRegistry`.
- **Interactive Overrides:** In the preview canvas, users can click on individual keys to open a context menu or properties panel to override the footprint for that specific key (e.g., assigning a rotary encoder or a 2u stabilizer footprint).

### FR-05: wx.GraphicsContext Preview Canvas
- Implement a custom `wx.Panel` utilizing `wx.GraphicsContext` for high-performance, native 2D drawing of the layout.
- Render key outlines, bounding boxes, and basic component shapes.
- Implement basic interaction: pan, zoom (scroll wheel), and click-to-select (for footprint overrides).
- Render routing preview traces using the routing engine's dry-run mode.

### FR-06: Engine Execution Integration
- Bridge the wxPython UI to the core Python placement and routing engines.
- Execute placement and routing operations asynchronously (e.g., using `wx.CallAfter` or background threads) to prevent freezing the KiCad UI.
- Display progress bars and detailed status messages during heavy operations (like Rust A* routing).
- Handle engine errors gracefully, displaying human-readable dialogs with diagnostic information (e.g., "Unrouted net: MatrixRow2").

### FR-07: Configuration Persistence
- Save dialog preferences (last used input method, global footprint selections, split board settings) to a local JSON config file so settings persist across KiCad sessions.

## Non-Functional Requirements

| ID | Requirement | Metric |
|---|---|---|
| NFR-01 | **Responsiveness** | The dialog must not block the main KiCad event loop. Long-running tasks must run in background threads. |
| NFR-02 | **Cross-Platform** | The wxPython UI must render correctly on Windows, macOS, and Linux (accounting for different OS DPI scaling and widget sizing). |
| NFR-03 | **Standalone Testability** | The dialog must be runnable as a standalone Python script outside of KiCad for rapid UI testing (using mock `pcbnew` data). |

## Acceptance Criteria

- [ ] The plugin registers correctly in the KiCad menu.
- [ ] The wizard flow progresses cleanly from Input to Routing.
- [ ] KLE JSON can be loaded via file picker and text paste.
- [ ] "Sync from Web Editor" successfully fetches layout data.
- [ ] Global footprint selections populate correctly from the registry.
- [ ] Clicking a key in the `wx.GraphicsContext` canvas allows overriding its footprint.
- [ ] The 2D canvas renders the layout with pan/zoom support.
- [ ] Clicking "Place" successfully executes the placement engine and updates the `pcbnew` board.
- [ ] Clicking "Route" successfully executes the routing engine without freezing the UI.
- [ ] Dialog preferences are saved and restored across sessions.
- [ ] The UI runs outside of KiCad for development/testing using mocked dependencies.

## Out of Scope

- 3D rendering within the wxPython dialog (that is handled by the web editor).
- Interactive drag-and-drop key placement (the dialog is for configuration and execution, not creating layouts from scratch).
