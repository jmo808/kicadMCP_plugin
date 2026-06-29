# Implementation Plan: Web-based Keyboard Layout Editor with Live PCB Preview

## Phase 1: Python WebSocket Bridge

- [ ] Task: Scaffold the WebSocket Bridge (`kbd_engine/server/bridge.py`)
    - [ ] Add `fastapi` and `uvicorn` (or `websockets`) dependencies to the project if not present
    - [ ] Write tests for WebSocket connection lifecycle (connect, heartbeat, disconnect)
    - [ ] Write tests for parsing incoming JSON messages into structured commands
    - [ ] Write tests for dispatching commands to the underlying placement/routing engines
    - [ ] Implement `BridgeServer` with WebSocket endpoint
    - [ ] Verify all tests pass

- [ ] Task: Define communication protocol and schemas
    - [ ] Write tests for serializing `SplitLayout` and custom matrix JSON to bridge format
    - [ ] Write tests for serializing placement results (X, Y, rotation, footprint) to JSON
    - [ ] Write tests for serializing routing results (traces, layer, width, vias) to JSON
    - [ ] Implement Pydantic models (or TypedDicts) for all incoming/outgoing messages
    - [ ] Verify all tests pass

- [ ] Task: Conductor - User Manual Verification 'Phase 1: Python WebSocket Bridge' (Protocol in workflow.md)

## Phase 2: React + Vite Frontend Scaffolding

- [ ] Task: Initialize Vite project (`web_editor/`)
    - [ ] Run `npm create vite@latest web_editor -- --template react-ts`
    - [ ] Install dependencies: `three`, `@react-three/fiber`, `@react-three/drei`, `zustand`
    - [ ] Install UI library (e.g., `lucide-react`, Tailwind or Radix UI)
    - [ ] Setup ESLint, Prettier, and Vitest for frontend testing
    - [ ] Verify `npm run test` and `npm run build` pass

- [ ] Task: Implement WebSocket client and State Management
    - [ ] Write unit tests for Zustand store (layout state, connection status, selection state)
    - [ ] Write tests for WebSocket service reconnection logic
    - [ ] Write tests for dispatching received bridge messages to the Zustand store
    - [ ] Implement `useLayoutStore` and `WebSocketProvider`
    - [ ] Verify all frontend tests pass

- [ ] Task: Conductor - User Manual Verification 'Phase 2: React + Vite Frontend Scaffolding' (Protocol in workflow.md)

## Phase 3: Layout Editor UI (Code + Visual)

- [ ] Task: Implement JSON Code Editor pane
    - [ ] Install Monaco Editor (`@monaco-editor/react`)
    - [ ] Write tests for editor debouncing and syncing to global state
    - [ ] Write tests for JSON schema validation and error highlighting
    - [ ] Implement `JsonEditor` component with side-by-side sync
    - [ ] Verify all tests pass

- [ ] Task: Implement Interactive 2D Visual Builder
    - [ ] Write tests for rendering 2D grid based on layout state
    - [ ] Write tests for drag-and-drop key placement (updating global state)
    - [ ] Write tests for key selection, rotation, and property editing pane
    - [ ] Implement `VisualBuilder` using HTML5 Canvas or SVG
    - [ ] Ensure bidirectional sync: Visual builder changes update JSON, JSON changes update Visual builder
    - [ ] Verify all tests pass

- [ ] Task: Conductor - User Manual Verification 'Phase 3: Layout Editor UI (Code + Visual)' (Protocol in workflow.md)

## Phase 4: Three.js Live 3D Preview

- [ ] Task: Scaffold 3D Preview Canvas
    - [ ] Write tests for React-Three-Fiber Canvas initialization
    - [ ] Write tests for camera controls (OrbitControls) and lighting
    - [ ] Implement `PreviewCanvas` base component
    - [ ] Verify all tests pass

- [ ] Task: Render PCB Geometry and Components
    - [ ] Write tests for rendering board outline polygon based on layout bounds
    - [ ] Write tests for rendering simple 3D keycaps and switches at provided coordinates
    - [ ] Write tests for rendering 3D routing traces (lines/tubes) on F.Cu and B.Cu layers
    - [ ] Write tests for toggling layer visibility (hide keycaps, isolate F.Cu)
    - [ ] Implement geometry generation from the backend WebSocket messages
    - [ ] Verify all tests pass

- [ ] Task: Conductor - User Manual Verification 'Phase 4: Three.js Live 3D Preview' (Protocol in workflow.md)

## Phase 5: Integration & Generation Endpoints

- [ ] Task: End-to-End Workflow Integration
    - [ ] Write integration test: Frontend sends layout -> Bridge places -> Bridge sends geometry -> Frontend renders
    - [ ] Write integration test: Requesting route preview -> Bridge routes (dry-run) -> Frontend renders traces
    - [ ] Implement the "Generate KiCad PCB" button triggering the final export command
    - [ ] Write integration test: "Generate" command successfully writes `.kicad_pcb` via Bridge
    - [ ] Add split-board configuration UI (mirroring toggle, thumb cluster params)
    - [ ] Verify all tests pass

- [ ] Task: Final Polish and Coverage
    - [ ] Verify frontend test coverage meets guidelines
    - [ ] Verify Python bridge test coverage is >80%
    - [ ] Verify UI responsiveness and performance with a large (100+ key) layout
    - [ ] Verify zero linter/type errors across both Python and TypeScript codebases

- [ ] Task: Conductor - User Manual Verification 'Phase 5: Integration & Generation Endpoints' (Protocol in workflow.md)
