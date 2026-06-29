# Specification: Integration Tests and CI/CD Deployment Pipeline

## Overview

This track establishes the continuous integration and continuous deployment (CI/CD) foundation for the KiCad Keyboard Automation Engine. It utilizes GitHub Actions to ensure code quality on every pull request by running linters, unit tests, and full End-to-End (E2E) integration tests inside a KiCad Docker container.

For releases, the pipeline automates the packaging of the plugin into a distributable ZIP file and generates the necessary metadata for publication to the KiCad Plugin and Content Manager (PCM).

## Functional Requirements

### FR-01: GitHub Actions CI Pipeline
- Create a `.github/workflows/ci.yml` workflow triggered on `push` to `main` and all `pull_request` events.
- **Frontend Job:** Run `npm run lint` and `npm run test` for the React/Vite Web Editor.
- **Backend Job (Python):** Run `ruff check`, `mypy`, and `pytest` for the Python core engine and MCP server.

### FR-02: Full E2E KiCad Docker Testing
- Implement a dedicated E2E testing job in the CI workflow.
- Spin up a Docker container pre-installed with KiCad 9 (e.g., using `kicad/kicad:9.0` image or a custom `Dockerfile`).
- Execute integration tests that require a real `pcbnew` Python environment (e.g., verifying placement coordinates, running headless routing, executing DRC).
- Store integration test artifacts (generated `.kicad_pcb` files, DRC reports) as GitHub Actions artifacts for manual inspection on failure.

### FR-03: Release Packaging (ZIP & PCM)
- Create a `.github/workflows/release.yml` workflow triggered when a new Git tag (e.g., `v1.0.0`) is pushed.
- **ZIP Artifact:** Package the `kicad_plugin/`, `kbd_engine/`, and the built `web_editor/dist/` into a single release `.zip` file. Upload this ZIP as a GitHub Release asset.
- **PCM Metadata:** Generate a `metadata.json` file conforming to the KiCad PCM specification. Include this in the release artifacts so users can easily add the plugin to their KiCad installation via the manager.

### FR-04: Test Data Fixtures
- Create a `tests/fixtures/` directory containing known-good inputs:
  - Sample KLE JSON files (e.g., a simple 4-key macropad, a 60% board, a split ergo).
  - Sample Custom JSON matrix definition files.
  - Expected output `.kicad_pcb` footprints/coordinates to assert against during E2E testing.

## Non-Functional Requirements

| ID | Requirement | Metric |
|---|---|---|
| NFR-01 | **CI Speed** | The standard CI job (linting + unit tests) must complete in < 2 minutes. The E2E Docker job must complete in < 5 minutes. |
| NFR-02 | **Reproducibility** | The E2E tests must be runnable locally by developers using a provided `docker-compose.yml` or standard `pytest` command. |
| NFR-03 | **Coverage Enforcement** | The CI pipeline must enforce a minimum 80% test coverage threshold for both Python and TypeScript, failing the build if coverage drops. |

## Acceptance Criteria

- [ ] `.github/workflows/ci.yml` is implemented and successfully runs linters and unit tests.
- [ ] `.github/workflows/release.yml` successfully creates a GitHub Release with attached `.zip` and `metadata.json` on tag push.
- [ ] E2E integration tests execute successfully inside a KiCad Docker container in CI.
- [ ] CI pipeline fails correctly when test coverage drops below 80%.
- [ ] A developer can run the E2E integration tests locally without modifying their host KiCad installation.

## Out of Scope

- Hosting a custom PCM repository web server (we only generate the necessary metadata JSON/ZIP files).
- Automated deployment of the Web Editor to Vercel/Netlify (it is intended to be run locally alongside KiCad).
