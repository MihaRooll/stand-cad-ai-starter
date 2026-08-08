# ADR-005: TZ stack and layout mapping

- Status: Accepted
- Date: 2026-08-03

## Decision

The Light Plotter Tower technical specification (`ИИ советы/Cursor_Opus5_TZ_Light_Plotter_Tower.md`, "TZ") supersedes the earlier mobile-floor-stand framing. The TZ section 13 prefers FreeCAD with TechDraw but explicitly permits a CadQuery-family B-Rep alternative with STEP/DXF/PDF export. The TZ section 14 proposes a `plotter_tower/` file tree.

**Decision 1 — master model stays build123d (not FreeCAD).** The CadQuery-family alternative the TZ permits shares the same OCCT kernel. `build123d==0.11.1` is already pinned in `pyproject.toml`, mandated by ADR-001 and ADR-002, and `build123d-mcp` is connected in-session. Switching now would discard a working toolchain for no geometric benefit.

**Decision 2 — repository layout wins over the TZ section 14 tree.** Do not create `plotter_tower/`. Generators stay under `src/stand_cad/`, scripts under `scripts/`, and generated artifacts under `output/` (git-ignored per ADR-002). Deliverable names from the TZ map to this repository as follows:

| TZ section 14 path | Repository equivalent |
|---|---|
| `README.md` / `STATUS.md` | `README.md` / `state/PROJECT_STATE.md` |
| `parameters.yaml` | `config/parameters.yaml` |
| `measurements_to_verify.md` | `docs/10_USER_INPUT_REQUIRED.md` |
| `BOM.csv` / `mass_report.csv` | BOM as **BOM-001** sheet inside `output/validation/<revision>/drawings/*.pdf` via `scripts/generate_drawings.py` (no standalone `BOM.csv`); `output/validation/<revision>/mass_report.csv` (+ `stability_report.md`, `deflection_report.md`) via `scripts/generate_mass_report.py` |
| `generate_model.py` | `scripts/generate_model.py` (CONCEPT STEP/STL/GLB export via `generate_concept_model()` → `output/concept/`) |
| `cad/*.FCStd` / `cad/*.step` | `output/concept/` (STEP/STL/GLB/manifest; no `.FCStd`) |
| `drawings/*.pdf` | `output/validation/<revision>/drawings/` via `scripts/generate_drawings.py` |
| `dxf/**` | `output/validation/<revision>/dxf/` (flat-panel `*_REFERENCE_ONLY_rev<revision>.dxf`; no TZ subfolder split) via `scripts/generate_drawings.py` |
| `renders/*.png` and `checks/*.md` | `output/validation/<revision>/views/` (PNG via `scripts/render_validation_views.py`); reports at `output/validation/<revision>/` per `AGENTS.md` CAD workflow |

## Rationale

The owner supplied a complete, dimensioned TZ that fixes product scope, envelope, and layout. The existing repository already has a validated build123d toolchain, MCP connectivity, and a source-of-truth policy (ADR-002). Adopting the TZ requirements without abandoning the working stack or duplicating directory structure minimizes rework while preserving traceability.

## Consequences

- No `.FCStd` file will ever exist in this repository; STEP is the neutral geometric handoff.
- Every future geometry stage resolves dimensions from `config/parameters.yaml` and `src/stand_cad/parameters.py` — never by hand-duplicating a TZ number in generator code.
- The `output/` tree gains the `cad/`, `drawings/`, `dxf/`, and `checks/` subfolder convention for revisioned artifacts.
