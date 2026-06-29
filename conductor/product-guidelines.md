# Product Guidelines: KiCad Keyboard Automation Engine

## Documentation Tone

**Style: Approachable Expert**

All user-facing documentation, error messages, and inline help should be:
- **Clear and professional** — Use precise technical language without unnecessary jargon.
- **Accessible to hobbyists** — Don't assume deep PCB design expertise. Explain domain-specific concepts (e.g., DRC, net classes, IPC standards) on first use.
- **Example-driven** — Pair explanations with concrete examples showing real keyboard layouts and component configurations.
- **Direct** — Prefer active voice. Get to the point. "This places the diode 2.54mm below the switch" over "The diode placement algorithm will calculate an offset."

## UX Design Principles

### 1. Fail-Fast with Clear Diagnostics
- Halt immediately on errors. Never silently skip a failed placement or routing step.
- Error messages must be **actionable**: reference specific component references (e.g., `SW_K23`), coordinates (in mm), net names, and the exact constraint violated.
- Example: `PlacementError: SW_K23 at (45.72, 38.10)mm overlaps D_K23 footprint courtyard by 0.15mm. Increase row_pitch or reduce diode_offset_y.`

### 2. Dry-Run / Preview Mode
- Every destructive operation (placement, routing, board modification) must support a `dry_run=True` parameter.
- In dry-run mode, return a structured preview (component positions, trace paths, clearance checks) without modifying the `.kicad_pcb` file.
- MCP tool endpoints must expose dry-run as a first-class parameter.

### 3. Progressive Disclosure
- **Sensible defaults** that work out-of-the-box for common layouts (60% QWERTY, Corne split).
- **Optional deep configuration** for power users: per-key component overrides, custom footprint mappings, routing constraint tuning.
- Configuration layering: global defaults → layout-level overrides → per-key overrides.

## Naming & Branding Convention

**Style: Concise and Idiomatic Python**

- **Modules:** `snake_case` — `kbd_engine`, `placer`, `router`, `kle_parser`, `mcp_server`
- **Classes:** `PascalCase` — `GridPlacer`, `MatrixRouter`, `FootprintRegistry`, `KleLayout`
- **Functions/Methods:** `snake_case` — `place_switches()`, `route_column_nets()`, `parse_kle_json()`
- **Constants:** `UPPER_SNAKE_CASE` — `DEFAULT_KEY_PITCH_MM`, `MX_SWITCH_FOOTPRINT`
- **No abbreviations** except universally understood ones: `mm`, `pcb`, `drc`, `mcp`, `kle`
- **Internal module prefix:** Use `_` prefix for private/internal modules and functions.

## Code Documentation Standard

### Google Python Style Guide (Baseline)
- All public modules, classes, and functions require **Google-style docstrings**.
- **Type hints everywhere** — all function signatures, return types, and class attributes.
- Strict linting with `ruff` or `flake8` + `mypy` for type checking.

### Hardware-Aware Documentation (Extension)
Every function that touches physical coordinates or board geometry **must** document:
- **Units:** Always millimeters (mm). State explicitly: `"All coordinates in mm."`
- **Coordinate system:** KiCad origin (top-left, Y-axis increases downward).
- **DRC implications:** Note any clearance, track width, or courtyard constraints that the function assumes or enforces.

Example:
```python
def place_diode(switch_pos: tuple[float, float], offset_y: float = 2.54) -> tuple[float, float]:
    """Calculate diode placement position relative to its parent switch.

    All coordinates in mm, using KiCad's coordinate system
    (origin top-left, Y increases downward).

    Args:
        switch_pos: (x, y) position of the parent switch center, in mm.
        offset_y: Vertical offset from switch center to diode center, in mm.
            Must be >= 1.27mm to satisfy courtyard clearance for SOD-123.

    Returns:
        (x, y) position for the diode center, in mm.

    DRC Notes:
        Assumes minimum 0.25mm courtyard clearance between switch and diode
        footprints per IPC-7351B.
    """
```

### Inline Comments
- Use inline comments **only where non-obvious** — complex coordinate math, bitwise matrix operations, KiCad API quirks.
- Never comment obvious code. `# increment counter` on `i += 1` is forbidden.

## Error Handling Standards
- Use custom exception hierarchy rooted in `KbdEngineError`.
- All exceptions must carry structured context: component ref, position, violated constraint.
- Never catch and silence exceptions in library code. Let errors propagate to the MCP server layer for proper diagnostics.

## Versioning
- Follow Semantic Versioning (SemVer): `MAJOR.MINOR.PATCH`.
- KiCad API compatibility breaks are MAJOR version bumps.
