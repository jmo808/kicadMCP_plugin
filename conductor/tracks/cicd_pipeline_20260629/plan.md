# Implementation Plan: Integration Tests and CI/CD Deployment Pipeline

## Phase 1: Local Testing Infrastructure & Fixtures

- [ ] Task: Set up test fixtures (`tests/fixtures/`)
    - [ ] Create `macropad.json` (KLE) and `macropad_expected.kicad_pcb`
    - [ ] Create `ergo_split.json` (Custom Schema) and `ergo_split_expected.kicad_pcb`
    - [ ] Create `drc_violations_board.kicad_pcb` (mock board with known errors)
    - [ ] Verify fixtures load correctly in simple test scripts

- [ ] Task: Scaffold test suite
    - [ ] Configure `pytest.ini` with integration and unit markers
    - [ ] Implement `tests/conftest.py` with reusable fixtures for mocked `pcbnew` objects
    - [ ] Verify `pytest` runs and collects tests successfully

- [ ] Task: Conductor - User Manual Verification 'Phase 1: Local Testing Infrastructure & Fixtures' (Protocol in workflow.md)

## Phase 2: Standard CI Workflows (Linting & Unit Tests)

- [ ] Task: Implement CI Workflow (`.github/workflows/ci.yml`)
    - [ ] Write GitHub Actions job for `frontend_tests`: setup Node, run `npm install`, `npm run lint`, `npm run test`
    - [ ] Write GitHub Actions job for `backend_tests`: setup Python, run `ruff check`, `mypy`, `pytest -m "not integration"`
    - [ ] Add step to enforce >80% coverage threshold using `pytest-cov`
    - [ ] Verify workflow logic (e.g., using `act` locally or mock trigger)

- [ ] Task: Conductor - User Manual Verification 'Phase 2: Standard CI Workflows (Linting & Unit Tests)' (Protocol in workflow.md)

## Phase 3: E2E KiCad Docker Integration Tests

- [ ] Task: Configure KiCad Docker Environment
    - [ ] Create `tests/Dockerfile` or configure `docker-compose.yml` pulling `kicad/kicad:9.0`
    - [ ] Write script to inject plugin code into the container's KiCad plugin directory
    - [ ] Verify container can be spun up locally and executes `kicad-cli`

- [ ] Task: Implement E2E tests (`tests/integration/`)
    - [ ] Write E2E test: `test_full_placement_pipeline` (validates output against fixture)
    - [ ] Write E2E test: `test_full_routing_pipeline` (runs headless router, validates DRC)
    - [ ] Add `e2e_tests` job to `.github/workflows/ci.yml` utilizing the Docker container
    - [ ] Configure GitHub Actions artifact upload for failed `.kicad_pcb` files
    - [ ] Verify integration tests pass locally via Docker

- [ ] Task: Conductor - User Manual Verification 'Phase 3: E2E KiCad Docker Integration Tests' (Protocol in workflow.md)

## Phase 4: Release Packaging & PCM Metadata

- [ ] Task: Implement Release Workflow (`.github/workflows/release.yml`)
    - [ ] Write script `scripts/build_release.py` to package frontend `dist/` and backend into a clean folder
    - [ ] Write script `scripts/generate_pcm.py` to auto-generate `metadata.json` for PCM based on Git tags
    - [ ] Configure GitHub Action to trigger on `refs/tags/v*`
    - [ ] Configure GitHub Action to zip the release folder and upload as a Release Asset
    - [ ] Verify build scripts run successfully locally

- [ ] Task: Conductor - User Manual Verification 'Phase 4: Release Packaging & PCM Metadata' (Protocol in workflow.md)

## Phase 5: Workflow Integration & Verification

- [ ] Task: End-to-End Pipeline Polish
    - [ ] Add branch protection rules documentation to `README.md` (require CI passing to merge)
    - [ ] Verify all existing codebase modules pass the newly established strict linting and coverage thresholds
    - [ ] Document local testing procedures for contributors in `CONTRIBUTING.md`

- [ ] Task: Conductor - User Manual Verification 'Phase 5: Workflow Integration & Verification' (Protocol in workflow.md)
