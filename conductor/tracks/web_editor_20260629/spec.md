# Specification: Web-based Keyboard Layout Editor with Live PCB Preview

## Overview

This track delivers a comprehensive TypeScript web-based keyboard layout editor that serves as the primary interactive frontend for the KiCad Keyboard Automation Engine. It allows users to define keyboard layouts visually or via code, and immediately see a live, interactive 3D preview of the resulting PCB geometry.

The frontend is built with React and Vite, utilizing Three.js/WebGL for high-performance 3D rendering of the keyboard matrix and PCB. It communicates with the Python core engine via a lightweight Local WebSocket Bridge, enabling real-time bidirectional communication for placement, routing previews, and DRC validation.

## Functional Requirements

### FR-01: React + Vite Frontend
- Scaffold the application using Vite and React with TypeScript.
- Implement a responsive, professional IDE-like UI (e.g., using a component library like MUI, Radix UI, or Tailwind).
- The layout should include a split pane view: Workspace (Editor/Visual Builder) on the left, and Live 3D Preview on the right.

### FR-02: Dual-Mode Layout Editing
- **JSON Code Editor:** Integrate a code editor (e.g., Monaco Editor) for writing and modifying the custom JSON matrix definition or pasting KLE JSON data.
- **Visual Drag-and-Drop Builder:** Implement an interactive 2D canvas where users can drag, drop, and rotate keycaps/switches to build the layout visually.
- **Bi-directional Sync:** Changes in the visual builder must immediately update the JSON code, and changes in the JSON code must immediately reflect in the visual builder.

### FR-03: WebGL / Three.js Live 3D Preview
- Render a 3D preview of the keyboard and the generated PCB.
- Support rendering components: keycaps, switches (MX/Choc), diodes, TRRS jacks, and USB-C connectors.
- Render PCB geometry: board outline, traces (FR-04), and vias.
- Implement camera controls: orbit, pan, zoom.
- Support layer toggling (e.g., hide keycaps to see the PCB, view only F.Cu or B.Cu traces).

### FR-04: Local WebSocket Bridge Communication
- Develop a lightweight Python HTTP/WebSocket server (the "Bridge") running alongside the MCP server.
- The Bridge will accept layout JSON from the web app, invoke the Python placement and routing engines, and return structured geometry data to the frontend.
- Implement a WebSocket client in the React app to maintain a persistent connection to the Bridge.
- Handle connection state management (connecting, connected, disconnected, reconnecting) and surface this in the UI.

### FR-05: Real-time Layout and Routing Previews
- When the layout changes (debounced), send a request to the Bridge to run the `placement_pipeline`.
- Request and render the routing preview via the Bridge using the `routing_pipeline`'s dry-run/preview mode.
- Display routing progress or errors (e.g., unrouted nets) directly in the 3D preview or a dedicated diagnostics panel.

### FR-06: Split Board Support (Integration)
- Ensure the editor natively supports the `SplitLayout` model introduced in the split board track.
- Provide UI controls for split-specific configuration (mirroring vs. independent, panelized vs. separate output, thumb cluster generation parameters).

### FR-07: Export and Generation
- Provide a clear "Generate KiCad PCB" action.
- When triggered, send a command to the Bridge to write the actual `.kicad_pcb` files to disk.
- Show success/failure notifications and link to the generated output directory.

## Non-Functional Requirements

| ID | Requirement | Metric |
|---|---|---|
| NFR-01 | **Performance (Render)** | 3D preview must maintain 60 FPS during camera manipulation on a standard laptop GPU for a 100-key board. |
| NFR-02 | **Performance (Update)** | PCB geometry updates from the backend must be reflected in the UI within 500ms of a layout change (excluding complex autorouting). |
| NFR-03 | **Modularity** | The frontend architecture must cleanly separate state management (Zustand/Redux), API communication, and rendering. |

## Acceptance Criteria

- [ ] React + Vite application starts and serves a basic shell.
- [ ] JSON Code Editor is implemented with syntax highlighting for the layout schema.
- [ ] Visual Builder allows placing, moving, and rotating at least one key unit.
- [ ] Modifying the visual layout updates the JSON, and vice versa.
- [ ] Three.js preview renders a basic board outline and keycap meshes.
- [ ] Python WebSocket Bridge starts and accepts connections from the web app.
- [ ] Sending a layout from the web app triggers placement in Python, and the resulting component coordinates are rendered in the 3D view.
- [ ] Requesting a routing preview displays traces in the 3D view.
- [ ] The "Generate KiCad PCB" button successfully writes `.kicad_pcb` files to the local disk via the Bridge.

## Out of Scope

- Hosting the application on the public internet (it is a local dev tool).
- Full schematic (`.kicad_sch`) generation or preview.
- Photorealistic raytraced rendering of the keyboard.
