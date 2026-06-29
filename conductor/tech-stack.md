# Tech Stack: KiCad Keyboard Automation Engine

## Programming Languages

| Language | Version | Role |
|---|---|---|
| **Python** | 3.11+ | Core engine, MCP server, KiCad plugin, KLE parser |
| **Rust** | stable (latest) | High-performance A* routing engine |
| **TypeScript** | 5.x+ | Web-based layout editor / GUI frontend |

## Core Frameworks & APIs

| Framework | Purpose |
|---|---|
| **pcbnew** (KiCad Python API) | Native board manipulation — footprint placement, net assignment, track creation, DRC invocation |
| **FastMCP** | Python MCP server framework for exposing keyboard automation as tool endpoints |
| **wxPython** | KiCad's built-in GUI framework for interactive dialogs and preview panels |

## External Routing Engines

| Engine | Type | Integration Method |
|---|---|---|
| **Rust A* pathfinder** | Custom deterministic router | FFI via PyO3 or subprocess with JSON I/O |
| **Quilter API** | Cloud-based constraint autorouter | REST API calls |
| **FreeRouting** | Open-source autorouter | DSN export → FreeRouting → SES import file exchange |

## Development & Testing Tools

| Tool | Purpose |
|---|---|
| **pytest** | Unit and integration testing with fixtures |
| **ruff** | Fast linter and formatter (replaces flake8/black/isort) |
| **mypy** | Static type checking for all Python type hints |

## Runtime Environment

- **Primary runtime:** KiCad 9.0+ embedded Python 3.11+ shell (`pcbnew` scripting console)
- **MCP server runtime:** Standalone Python process (can run outside KiCad for headless/CI use)
- **Board file format:** KiCad S-expression `.kicad_pcb` and `.kicad_sch`

## Engineering Standards

- **IPC-2152 adherence:** Track widths and spacing calculated per current capacity matrices.
- **DRC compliance:** All generated boards must pass KiCad native DRC with zero errors.
- **Coordinate system:** All positions in millimeters (mm), KiCad origin (top-left, Y-down).
