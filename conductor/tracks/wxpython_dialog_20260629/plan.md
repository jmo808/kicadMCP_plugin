# Implementation Plan: Interactive KiCad wxPython Dialog

## Phase 1: Plugin Scaffolding & State Management

- [ ] Task: Scaffold KiCad Action Plugin (`kicad_plugin/action_plugin.py`)
    - [ ] Write tests for registering the plugin with `pcbnew.ActionPlugin`
    - [ ] Write tests for mocking `pcbnew` during standalone execution
    - [ ] Implement `KbdAutomationPlugin` class
    - [ ] Verify plugin loads in KiCad via simple mock script

- [ ] Task: Implement UI State Management (`kicad_plugin/state.py`)
    - [ ] Write tests for `DialogState` dataclass (layout source, footprint config, execution state)
    - [ ] Write tests for loading/saving state to a local `config.json` file
    - [ ] Write tests for state updates triggering UI refreshes
    - [ ] Implement state management logic
    - [ ] Verify all tests pass

- [ ] Task: Conductor - User Manual Verification 'Phase 1: Plugin Scaffolding & State Management' (Protocol in workflow.md)

## Phase 2: Wizard Flow & Input Methods

- [ ] Task: Implement main Wizard shell (`kicad_plugin/ui/wizard.py`)
    - [ ] Write tests for `wx.adv.Wizard` (or custom `wx.Notebook` flow) navigation
    - [ ] Write tests for wizard page validation (cannot proceed if no layout loaded)
    - [ ] Implement main dialog frame and page orchestration
    - [ ] Verify tests pass (using mock `wx` or standalone mode)

- [ ] Task: Implement Input Page (`kicad_plugin/ui/pages/input.py`)
    - [ ] Write tests for file picker loading KLE/JSON
    - [ ] Write tests for text area parsing raw JSON
    - [ ] Write tests for "Sync from Web Editor" HTTP/WS fetch
    - [ ] Implement UI for input methods
    - [ ] Verify all tests pass

- [ ] Task: Conductor - User Manual Verification 'Phase 2: Wizard Flow & Input Methods' (Protocol in workflow.md)

## Phase 3: Configuration & Preview Canvas

- [ ] Task: Implement Configuration Page (`kicad_plugin/ui/pages/config.py`)
    - [ ] Write tests for populating global footprint dropdowns from `FootprintRegistry`
    - [ ] Write tests for saving selected global footprints to state
    - [ ] Implement UI for global footprint selection
    - [ ] Verify all tests pass

- [ ] Task: Implement `wx.GraphicsContext` Preview Canvas (`kicad_plugin/ui/canvas.py`)
    - [ ] Write tests for computing view transforms (pan/zoom)
    - [ ] Write tests for rendering keys based on `LayoutModel`
    - [ ] Write tests for hit-testing (detecting which key was clicked)
    - [ ] Write tests for rendering routing preview traces
    - [ ] Implement `PreviewCanvas` using `wx.GraphicsContext`
    - [ ] Verify all tests pass

- [ ] Task: Implement Footprint Overrides (`kicad_plugin/ui/overrides.py`)
    - [ ] Write tests for right-click context menu on canvas keys
    - [ ] Write tests for applying a specific footprint override to a single key in state
    - [ ] Implement context menu and override logic
    - [ ] Verify all tests pass

- [ ] Task: Conductor - User Manual Verification 'Phase 3: Configuration & Preview Canvas' (Protocol in workflow.md)

## Phase 4: Execution Integration

- [ ] Task: Bridge UI to Core Engine (`kicad_plugin/execution.py`)
    - [ ] Write tests for mapping UI state to `RoutingRequest` and placement requests
    - [ ] Write tests for running core engine tasks in a background `threading.Thread`
    - [ ] Write tests for using `wx.CallAfter` to safely update UI from background thread
    - [ ] Implement asynchronous execution runner
    - [ ] Verify all tests pass

- [ ] Task: Implement Execution Pages (`kicad_plugin/ui/pages/execute.py`)
    - [ ] Write tests for placement execution UI (progress bar, log output)
    - [ ] Write tests for routing execution UI (router selection, dry-run toggle, execute)
    - [ ] Write tests for error handling displays (unrouted nets dialog)
    - [ ] Implement Place and Route wizard pages
    - [ ] Verify all tests pass

- [ ] Task: Conductor - User Manual Verification 'Phase 4: Execution Integration' (Protocol in workflow.md)

## Phase 5: End-to-End Polish

- [ ] Task: Full Dialog Integration Testing
    - [ ] Write integration test: Open wizard -> Load KLE text -> Configure footprints -> Place -> Route -> Success
    - [ ] Write integration test: Verify error handling catches routing failures gracefully
    - [ ] Verify cross-platform widget layout (sizers expanding correctly)
    - [ ] Verify the dialog can be launched via `python3 -m kicad_plugin.standalone`
    - [ ] Ensure test coverage >80% for UI logic layers

- [ ] Task: Conductor - User Manual Verification 'Phase 5: End-to-End Polish' (Protocol in workflow.md)
