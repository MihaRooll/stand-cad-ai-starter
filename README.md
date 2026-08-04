# AI-first CAD project for a light desktop plotter tower

Русская инструкция для владельца проекта: [`START_HERE_RU.md`](START_HERE_RU.md).

This repository is a production-oriented starter for designing a light desktop tower for two Silhouette cutting plotters plus horizontal film storage, with an AI agent in Cursor. It is intentionally **not** a finished or released design: critical dimensions, loads, operating clearances, materials, and the target manufacturer's bend data are not yet known.

The chosen workflow is:

1. Cursor and Opus 5 orchestrate the project.
2. Parametric source is written in Python with `build123d`.
3. `build123d-mcp` supplies interactive CAD tools: incremental modeling, renders, measurements, validation, and interchange exports.
4. STEP is the main neutral handoff format; PDF drawings and BOM communicate design intent.
5. Sheet-metal flat patterns and production DXF are released only after DFM review with the selected manufacturer.
6. The first physical item is a prototype. Series production requires inspection, corrections, and a new approved revision.

## Day-to-day loop

After the first setup:

1. Regenerate concept and validation artifacts: `uv run python scripts/regenerate.py`
2. Serve the three.js viewer with live reload: `uv run python scripts/serve_viewer.py --watch`, then open `http://127.0.0.1:8000/viewer/index.html`
3. When something misbehaves, run the environment doctor: `uv run python scripts/doctor.py`

See [`viewer/README.md`](viewer/README.md) for viewer controls, manifest paths, and troubleshooting.

## Start here

Read these files in order:

1. [`START_HERE_RU.md`](START_HERE_RU.md)
2. [`OPUS_5_START_PROMPT.md`](OPUS_5_START_PROMPT.md)
3. [`AGENTS.md`](AGENTS.md)
4. [`docs/00_UPDATED_RECOMMENDATION.md`](docs/00_UPDATED_RECOMMENDATION.md)
5. [`docs/02_SCOPE_AND_ASSUMPTIONS.md`](docs/02_SCOPE_AND_ASSUMPTIONS.md)
6. [`docs/05_IMPLEMENTATION_PLAN.md`](docs/05_IMPLEMENTATION_PLAN.md)
7. [`docs/10_USER_INPUT_REQUIRED.md`](docs/10_USER_INPUT_REQUIRED.md)

## First local setup on Windows 11

Use native Windows Python tooling for the first implementation. Do not mix a Windows Cursor process, WSL paths, and Windows GUI rendering in one CAD session.

Install `uv` from its official installer if it is not already installed:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Open a new PowerShell window, then run:

```powershell
uv sync --extra dev
uv run python scripts/validate_inputs.py --project config/project.example.toml --equipment config/equipment.example.toml --allow-demo
uv run python scripts/smoke_model.py
uv run pytest
```

The project-level MCP configuration is already included in `.cursor/mcp.json`. Restart Cursor after opening the repository and verify that `build123d-mcp` is green in Cursor settings.

## Non-negotiable release rule

No file may be labelled `FOR_PRODUCTION`, `RELEASED`, or equivalent while any fit-critical input is unknown, any enabled equipment envelope is unverified, or the manufacturer-specific DFM gate is incomplete. A visually correct render is never manufacturing approval.

## Expected final production package

```text
release/REV_A/
├── 00_MANIFEST.csv
├── 01_REQUIREMENTS.pdf
├── 02_ASSEMBLY_STEP/
├── 03_PART_STEP/
├── 04_DRAWINGS_PDF/
├── 05_CUTTING_DXF/
├── 06_BOM/
├── 07_RENDERS/
├── 08_VALIDATION/
└── 09_VENDOR_DFM/
```

The exact contents and approval rules are defined in `docs/06_MANUFACTURING_HANDOFF.md`.
