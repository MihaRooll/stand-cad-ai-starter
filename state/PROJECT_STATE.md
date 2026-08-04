# Project state

- Project: Light desktop tower for two Silhouette Cameo 5 plotters plus vertical film organizer, 650 × 550 × 690 mm (see ADR-005 and `ИИ советы/Cursor_Opus5_TZ_Light_Plotter_Tower.md`)
- Current phase: Phase 0 — repository and toolchain baseline
- Current gate: G0
- Status: Native Windows toolchain verified; G0 exit-criteria evidence collected
- Last updated: 2026-08-04 (PLT-005 rev4)

## PLT-005 fidelity cycle 3 + dev loop (2026-08-04)

- **Phase:** dev-loop automation (Part A) + fidelity cycle 3 → **rev4** evidence pack (CONCEPT / REFERENCE_ONLY)
- **Part A delivered:** `scripts/doctor.py`, `scripts/regenerate.py`, `scripts/serve_viewer.py --watch` + `GET /viewer/reload-status`, viewer live reload (preserves camera/visibility/clipping on auto reload)
- **Part B delivered:** handle reposition + grey side-view backgrounds; organizer front-dominant camera + FILM-BODY-009 formula fix; outer shell raised to `foot_height_mm`; solid side slabs; rear vent legibility via grey `transport_rear.png` background + grid probe test
- **Evidence:** 12 PNG + 5 SVG in `output/validation/rev4/views/`; STEP/STL/GLB/manifest `*_rev4.*`; `rev1/`–`rev3/` untouched
- **Achieved side-slab corner fillet:** **≈9.9 mm** (R25 clamped by 20 mm side-clear band — see D-019, `docs/10_USER_INPUT_REQUIRED.md` §D)
- **Tests:** 124 pytest passing; ruff clean; `scripts/setup_windows.ps1` exit 0
- **Next:** adversarial review of rev4 PNGs + live-reload behaviour; human G0 verdict unchanged

## PLT-004 fidelity cycle 2 (2026-08-04)

- **Phase:** shell restructuring + handle visibility fix (`output/validation/rev3/`, CONCEPT / REFERENCE_ONLY)
- **Delivered:** full-height side slabs (20 mm × 690 mm, 2D front-corner fillets, single solid each); open front (no `PANEL-OUT-FRONT-001`); open organizer top (no `TOP-STRUCTURE-001`); removed `PANEL-OUT-CORNER-*`; handle cutout repositioned (Y=`depth×0.25`, Z=`upper_z+physical_height/2` provisional); bottom vent through-cuts on `PANEL-IN-BOTTOM-001` under `AIRPATH-001`; organizer close-up render
- **Removed parts:** `PANEL-OUT-FRONT-001`, `TOP-STRUCTURE-001`, `PANEL-OUT-CORNER-FL/FR/RL/RR-001` (4)
- **Evidence:** 12 PNG + 5 SVG in `output/validation/rev3/views/` (incl. `organizer_closeup.png`, `base_plate_closeup.png`); STEP/STL/GLB/manifest `*_rev3.*`; `rev1/` and `rev2/` untouched
- **Mass:** indicative structural **7.849 kg** (3 mm PMMA side-slab shells; single-face shell estimate); deflection 3.953 mm (unchanged; ceiling NOT met)
- **Tests:** 121 pytest passing; ruff clean; `scripts/setup_windows.ps1` exit 0
- **Next:** adversarial review of rev3 PNGs; human G0 verdict unchanged

## PLT-003 concept validation (2026-08-03, updated 2026-08-04)

- **Phase:** concept validation evidence pack (`output/validation/rev1/`, CONCEPT / REFERENCE_ONLY)
- **Delivered:** quarter-cylinder corner shells (`PANEL-OUT-CORNER-FL/FR/RL/RR-001`); organizer top perimeter frame + front opening above retainer; divider finger cutouts; all-cell film bodies; cylindrical feet; rear vent slots; TOP-STRUCTURE sketch R25 footprint; corner junction skin continuity fix (cycle 3)
- **Evidence:** 10 PNG + 5 SVG in `output/validation/rev1/views/`; STEP/STL/GLB/manifest `*_rev1.*` in `output/concept/`; viewer `index.html` → rev1 manifest
- **Mass:** empty-case indicative 9.573 kg; regenerate via `scripts/generate_mass_report.py`
- **Tests:** 117 pytest passing; ruff clean; `scripts/setup_windows.ps1` exit 0
- **Render path:** `uv run python scripts/render_validation_views.py` writes to `output/validation/rev1/views/` and `output/concept/*_rev1.*`
- **Open:** vent slot dimensions provisional (`to_measure`); corner top-edge fillet best-effort; adversarial sign-off pending
- **Next:** final sign-off on PLT-003 evidence pack; then Gate G0 human verdict

## Product pivot (2026-08-03)

The Light Plotter Tower TZ (`ИИ советы/Cursor_Opus5_TZ_Light_Plotter_Tower.md`) supersedes the earlier mobile-floor-stand framing (ADR-005, D-011). The parameter layer now exists: `config/parameters.yaml` and `src/stand_cad/parameters.py`. No geometry has been generated yet. TZ section 3 supplies G1 equipment data for the Silhouette Cameo 5 (physical envelope, mass, quantity = 2); G1 itself remains an unconfirmed Human Gate.

## Git baseline

- Repository initialized with remote `origin` = `https://github.com/MihaRooll/stand-cad-ai-starter.git` (fetch and push). Upstream branch: `origin/main`.
- Commits (oldest first):
  - `910a23a` — Initial commit: add README
  - `a1f2c97` — Initial AI-first CAD project specification
  - `c07dbf4` (`c07dbf40235ffb258bc5881d3d71d7ac194a7d62`) — Adopt orchestration harness and record MCP connectivity resolution (15 files: `.cursor/agents/`, `.cursor/skills/autonomous-task/`, rules `20`/`21`/`30`, four `state/**` files)
- Annotated tag `baseline` on `a1f2c97`, message `Baseline: initial AI-first CAD project specification`.
- `c07dbf4` is local-only and unpushed (`git log origin/main..HEAD` lists it; not pushed to remote).

## G0 status (evidence only)

G0 exit-criteria evidence is partially complete on native Windows; gate verdict is a Human Gate and remains unconfirmed.

Satisfied: locked dependency sync (53 packages), input validator with `--allow-demo`, smoke STEP bounds 100 × 60 × 20 mm (`output/smoke/calibration_block_REFERENCE_ONLY.step`, 15460 bytes), `uv run pytest` (9 passed), `uv run ruff check .` (clean), pinned MCP session connectivity — `build123d-mcp@0.3.81` connected in-session with 38 tools exposed and `serverStatus: ready` (see MCP server record; satisfies evidence collection for `docs/05_IMPLEMENTATION_PLAN.md:26`).

Evidence collected is not a gate verdict: G0 remains an unconfirmed Human Gate.

## Environment and versions

- `requires-python`: `>=3.12,<3.13` (`pyproject.toml:9`)
- `build123d==0.11.1` (`pyproject.toml:11`)
- Locked dependency sync: 53 packages resolved (`uv.lock`)
- Command rule: all project commands run via `uv run`; bare `python` on this machine resolves to 3.11

## MCP server record

- Pinned package: `build123d-mcp@0.3.81` (`.cursor/mcp.json:10`; schema-correct: top-level `mcpServers`, server key `build123d-mcp`, `command: "uv"`, `args: ["tool","run","--python","3.12","build123d-mcp@0.3.81"]`; no `env`, `cwd`, `transport`, `type`, or `disabled` keys).
- Package-level (native Windows): `uv` resolves to `C:\Users\katko\.local\bin\uv.exe`; `uv tool run --python 3.12 build123d-mcp@0.3.81 --help` exits 0 and advertises `--transport {stdio,http}` with default `stdio`. Confirms the package resolves and runs natively. This is separate from session connectivity below.
- Session connectivity timeline:
  - **Pre-enable (historical, before 2026-08-03 ~19:48):** registered but client never started — Cursor registered `build123d-mcp` but did not spawn or connect an MCP client (zero tools exposed). Evidence: `workbench.mcp.files.log` shows `createClient` only for the `context7` plugin server, never for build123d; `workbench.mcp.oauth.log` repeats `project-0-stand-cad-ai-starter-build123d-mcp none -> disconnected`; `Mcp FileSystem Writer.log` lines 6–14 show build123d receives only a `server_status` lease while context7 receives `snapshot_store`, then `lease returned 2 tools across 1 clients`; no spawn / ENOENT / `uv` error line for build123d in those pre-enable logs. Resolution required user action (enable toggle and Reload Window), not a repository code change.
  - **Resolution (2026-08-03):** user enabled the server via Cursor Settings → MCP → `build123d-mcp` → enable toggle → Reload Window. Post-enable log `C:\Users\katko\AppData\Roaming\Cursor\logs\20260803T185957\mcp-server-project-0-stand-cad-ai-starter-build123d-mcp.log` (1051 bytes): line 1, 2026-08-03 19:48:13.414, `connecting stdio for "build123d-mcp" (project-0-stand-cad-ai-starter-build123d-mcp)`; line 3, `MCP stdio spawn policy decision: sandboxed=false, sandboxReason=controls_disabled`; line 4, 2026-08-03 19:48:14.585, `Successfully connected to stdio server`; lines 6–11, three `[error] Processing request of type ListToolsRequest / ListPromptsRequest / ListResourcesRequest` entries followed by `undefined`. **Interpretation (not fact):** these are the MCP SDK's own stderr request-logging relayed by Cursor under an error label; they coincided with a successful connection and a successful tool listing, so they are not evidence of failure.
  - **Current session catalog (2026-08-03, post-enable):** server id `project-0-stand-cad-ai-starter-build123d-mcp`, `serverStatus: ready`, 38 tools exposed to the agent session (previously zero).
- `--in-process` fallback: never applied and never needed; post-enable log line 3 shows `sandboxed=false` (`controls_disabled`).
- Explicitly undetermined: the exact enabled/disabled bit in the Cursor settings store was never read directly.
- Reported `serverInfo.version` from MCP `initialize` handshake in an **earlier session**: `1.29.0` (not re-read in this session's catalog check).
- Note: package pin (`0.3.81`) and reported server runtime (`1.29.0`) are two different numbering schemes; both are expected and neither is "the" single version.

## Completed

- Three-cycle specification review completed.
- CAD stack and version policy selected.
- Source-of-truth, DFM, autonomy, and release boundaries recorded as ADRs.
- Repository starter, validation scaffold, and implementation plan prepared.
- Linux-container baseline passed during archive preparation.
- Git initialized; baseline commit `a1f2c97` on `origin`.
- Windows-native `uv`/Python/MCP verification complete.
- Committed `uv.lock` resolves on Windows (53 packages).
- Input demo validation passed explicitly with `--allow-demo`.
- Ruff passed and pytest passed: 9 tests.
- Reference-only STEP regenerated with verified bounds 100 × 60 × 20 mm.
- Windows-observed versions and outputs recorded (see Environment and versions, MCP server record).

## Phase 0 baseline work (items 1–5) — complete

1. Initialize Git and create baseline commit.
2. Verify Windows-native `uv`/Python/MCP.
3. Verify the committed `uv.lock` resolves on Windows.
4. Run validator, smoke model, lint, and tests.
5. Record exact Windows-observed versions and outputs.

## Remaining Phase 0 work

- Author MCP modeling/drawing/repair project rules per `docs/05_IMPLEMENTATION_PLAN.md:14` — precondition now satisfied (MCP connected in-session, 38 tools listed; see D-009). Authoring is unblocked as a separate follow-up packet; not in scope for this cycle. `build123d-mcp@0.3.81 --help` lists only server options, with no rule-install command; rules must be authored in this repository.

## Current blockers

### Measurements and manufacturing

- Eight physical measurements on real Cameo 5 units and purchased sheet materials — see `docs/10_USER_INPUT_REQUIRED.md` section A.
- Manufacturer DFM authorization — see `docs/10_USER_INPUT_REQUIRED.md` section B and Gate G5 in `docs/05_IMPLEMENTATION_PLAN.md`.

These blockers do not prevent parameter-layer work but block production geometry release and Gate G5/G6.

## Next decision

After G0 gate verdict (Human Gate), complete the consolidated input packet in `docs/10_USER_INPUT_REQUIRED.md` and start equipment envelopes only for verified selected models.
