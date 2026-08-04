# Project state

- Project: Light desktop tower for two Silhouette plotters plus horizontal film storage, **650 × 550 × 544 mm** (derived height; see ADR-005 and `ИИ советы/Cursor_Opus5_TZ_Light_Plotter_Tower.md`)
- Current phase: D-040 render-evidence tie-break fix → **rev11** evidence pack (CONCEPT / REFERENCE_ONLY)
- Current gate: G0 (human verdict unconfirmed)
- Status: F-5 closed (D-038); PLT-010 stability closed (D-039, upper 1.596 / lower 3.563, both ≥1.5 floor); render Z-buffer tie-break fixed (D-040, adversarial-reviewer cycle 1 PASS) — cladding now correctly visible in evidence PNGs, zero change to mass/stability/deflection numbers
- Last updated: 2026-08-04 (D-040; render tie-break fix; `CONCEPT_REVISION` 10→11; rev11)

## PLT-009 height-stack fix (2026-08-04, D-038)

- **Fix:** `plotter.upper_z` formula now reserves full tier-2 under-tray stack (slide 12 mm + frame profile 15 mm + tray panel 11 mm) — was missing 27 mm. Propagated +27 mm through `film_storage_horizontal.z`, `top_structure`, `case.height`, `handle_mount_z_mm`.
- **Values:** `upper_z` 211→**238**; `case.height` 517→**544**; `handle_mount_z_mm` 263→**276.5**; `tier_clearance_lower_mm` 170→197
- **F-5 closed:** zero `intersection_volume` at all 7 tier-2 under-tray parts × 5 tray-1 positions; Z-gap constant across travel (rails 11 mm, slides 26 mm, interlock tab 15 mm)
- **Light-strip §I:** `minimum_clearance(LIGHT-STRIP-001, FRAME-POST-RR-001)` still **0.5 mm** (common +27 mm shift); no reposition — XY overlap requires `to_measure` length change
- **Tests:** 321 pytest passing (285 baseline + 35 F-5 regression + 1 computed_upper_z); ruff clean
- **Baseline commit:** `d3e4247`
- **Next:** adversarial-reviewer on F-5 evidence; verifier Full profile

## QA sweep cycle 2 (2026-08-04)

- **Scope:** scripted `intersection_volume` audit across **8 configuration states** — `transport`, `organizer_loaded`, `panels_hidden`, `operating`, `operating_with_test_bodies`, tier-1 tray at `lower_extension`=0 / `lower_quick_access_extension_mm` (130) / `lower_extension` (250), tier-2 tray at `upper_extension`=0 / 400
- **Fix delivered:** film-shelf front-withdrawal path collided with `FRAME-POST-FL-001` `leg_h` (≈74.23 mm³ at every withdrawal offset dy=20–340 mm) and `PANEL-CLAD-FRONT-POST-FL-001` (300–900 mm³). Real clearance notch cut in `frame.py` (X=`film_storage_horizontal.x`→`corner_radius+frame_profile_size_mm`, Y=0→profile, Z=organizer clear-volume band only); mirrors `_tray1_clearance_notch_x_z` pattern. Regression: `tests/test_geometry.py::test_film_body_front_withdrawal_clears_front_left_post` (4 shelves × 36 withdrawal steps)
- **F-5 (supersedes qualitative note below):** ~~open~~ **RESOLVED by D-038 (PLT-009)** — see PLT-009 section above. Historical quantification retained in `docs/10_USER_INPUT_REQUIRED.md` §H.
- **Light-strip near-miss:** `LIGHT-STRIP-001` vs `FRAME-POST-RR-001` exactly **0.5 mm** clearance in transport (zero margin vs `tolerance.part_assembly_feature_mm`). Flagged in `docs/10_USER_INPUT_REQUIRED.md` §I; no geometry change
- **Tests:** 285 pytest passing (141 baseline + 144 new parametrized cases in `test_film_body_front_withdrawal_clears_front_left_post`); ruff clean
- **Baseline commit:** `9e38f98`
- **Next:** adversarial-reviewer on film-post notch; verifier Quick profile

## PLT-007 cable pass-through (D-036, 2026-08-04)

- **Change:** Owner override of TZ section 10 certified rear mains inlet → plain **30 mm** grommeted cable pass-through at rear panel centre (X=325, Z=160.5); `SVC-CABLE-PASSTHROUGH-001` annular grommet (26 mm clear bore, 1 mm TZ:472 R1 chamfer on the bore rim); `MAINS-INLET-001` placeholder unchanged (deferred, not deleted)
- **Delivered:** real boolean cut through both `PANEL-OUT-REAR-001` and `PANEL-IN-REAR-001` (cycle-1 adversarial review found the first pass only cut the outer skin and used a solid, bore-less grommet — both fixed); `hardware.cable_passthrough_diameter_mm`, `services.cable_passthrough_grommet_wall_mm` (`to_measure`), `services.cable_passthrough_edge_break_radius_mm` (`verified`, TZ:472 R1); `CONCEPT_REVISION`=8; `cable_passthrough_closeup.png` evidence
- **Evidence target:** `output/validation/rev8/views/`; STEP/manifest `*_rev8.*`
- **Tests:** 141 pytest passing; ruff clean; `scripts/setup_windows.ps1` exit 0
- **Review:** adversarial-reviewer APPROVED on cycle 2 (cycle 1 REWORK: F-1 solid-plug grommet, F-2 inner panel not cut, F-3 stale REL-027 count — all closed)
- **Next:** local commit (no push); human G0 verdict unchanged

## PLT-007 horizontal reconfig + Cameo 4 governing envelope (2026-08-04)

- **Envelope (at rev7, pre-D-038):** 650 × 550 × 517 mm; **610 mm clear width** (20 mm side wall, **R10** bullnose — D-027 rejects 620/630 widening). **Superseded 2026-08-04 by D-038:** `case.height` grew to **544 mm** (+27 mm height-stack fix) — see **PLT-009 height-stack fix** section above; 610 mm clear width and R10 bullnose unaffected.
- **Governing machine:** Silhouette Cameo 4 — 570 × 195 × 170 mm, 4.7 kg (`plotter_cameo4`); design envelope 584 × 219 × 178 mm; slot 2 mass 5.2 kg (Cameo 5)
- **Film storage:** 4 horizontal shelves, 25 mm compartment height, 500 mm sheet edge across width
- **Tier layout:** tiers aligned, setback removed (D-033); `lower_y`=`upper_y`=15; tier 1 has a documented 130 mm quick-access forward slide (`trays.lower_quick_access_extension_mm`) in addition to its 250 mm full-service extension; tier clear height ≥170 mm each
- **Storage clearances (closed trays):** plotter 1 front **15 mm**; plotter 2 rear **340 mm** to case back (recomputed after D-033 alignment; was 210 mm at the old 130 mm setback)
- **Operational clearance (structural — settled):** manufacturer pass-through **907 mm** (356+195+356) **exceeds** case depth 550 mm → **closed niche is storage/transport only** (D-028). Active cutting requires material through front **and** rear openings (330 mm slots at L1/L2 feed planes) and/or tray extension plus **external rear supports** (`services.rearsupport_*`). Tests: `test_pass_through_depth_exceeds_case_envelope`, `test_operating_state_front_rear_pass_through_open`.
- **Delivered:** service-port cutout (provisional); handle Z=263 (side-panel centre) — **superseded 2026-08-04 by D-038: recomputed to 276.5 mm** on the taller 544 mm case, formula unchanged; frame cladding; grey backgrounds; `CONCEPT_REVISION`=7; `service_port_closeup.png` evidence
- **Evidence target:** `output/validation/rev7/views/`; STEP/manifest `*_rev7.*`
- **Viewer:** `uv run python scripts/serve_viewer.py --watch` → `http://127.0.0.1:8000/viewer/index.html` (see `viewer/README.md`)
- **Tests:** 132 pytest passing; ruff/setup not re-run this cycle
- **Pre-change SHA:** `69b1261`
- **Next:** adversarial-reviewer on rev7; verifier Full profile
- **Known non-blocking follow-ups from D-033 adversarial review (2026-08-04, not required for this cycle):** F-3 `tests/test_kinematics.py::test_tray1_quick_access_distinct_from_full_extension` is YAML-only (no geometry measurement) — could be strengthened later. **F-5 closed by D-038/PLT-009** — zero `intersection_volume` at all 7 tier-2 under-tray parts × 5 tray-1 positions (35 regression cases); see **PLT-009 height-stack fix** section above and `docs/10_USER_INPUT_REQUIRED.md` §H (RESOLVED). F-6 `is_open_front_kinematic_contact()` docstring should mention the tray-1 base-front notch now modeled in `frame.py`.

## PLT-006 fidelity cycle 4 (2026-08-04)

- **Phase:** fidelity cycle 4 → **rev5** evidence pack (CONCEPT / REFERENCE_ONLY)
- **Delivered:** opal `PANEL-CLAD-FRONT-{BASE,ORG,TOP}-001` over centre front rails; R10 side-slab bullnose (exterior front vertical + top edge); mass report paths sync to `CONCEPT_REVISION`; `evidence_light_strip_only.png` / `evidence_retainer_only.png` identity renders; handle Z note cites CoM z≈217.3 mm (unchanged Y=100/Z=214) — **rev5-era figures; superseded by D-038 height-stack fix (handle Z now 276.5 mm) and current `output/validation/rev11/mass_report.csv` (CoM empty case z=236.4 mm; case + 2 plotters z=229.3 mm). D-040 (2026-08-04) also found this cladding's pre-rev11 PNG renders had a Z-buffer tie-break defect that hid it behind the rail it covers — the geometry above was always correct, only the render tool's visual evidence was wrong; see rev11 evidence.**
- **Evidence:** 14 PNG + 5 SVG in `output/validation/rev5/views/`; STEP/STL/GLB/manifest `*_rev5.*`; `rev4/` untouched
- **DEVIATED:** PLT-018 / TZ line 230 R20–R30 → R10 bullnose (D-025)
- **Tests:** 130 pytest passing; ruff clean; `scripts/setup_windows.ps1` exit 0
- **Next:** adversarial review of rev5 PNGs; human G0 verdict unchanged

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
- **Mass (rev3 figure):** indicative structural **7.849 kg** (3 mm PMMA side-slab shells; single-face shell estimate); deflection 3.953 mm (unchanged; ceiling NOT met) — **superseded: deflection fixed to ≈0.228 mm by D-035's three-rail centre support (ceiling now met); current rev11 structural mass 7.054 kg per `output/validation/rev11/mass_report.csv`**
- **Tests:** 121 pytest passing; ruff clean; `scripts/setup_windows.ps1` exit 0
- **Next:** adversarial review of rev3 PNGs; human G0 verdict unchanged

## PLT-003 concept validation (2026-08-03, updated 2026-08-04)

- **Phase:** concept validation evidence pack (`output/validation/rev1/`, CONCEPT / REFERENCE_ONLY)
- **Delivered:** quarter-cylinder corner shells (`PANEL-OUT-CORNER-FL/FR/RL/RR-001`); organizer top perimeter frame + front opening above retainer; divider finger cutouts; all-cell film bodies; cylindrical feet; rear vent slots; TOP-STRUCTURE sketch R25 footprint; corner junction skin continuity fix (cycle 3)
- **Evidence:** 10 PNG + 5 SVG in `output/validation/rev1/views/`; STEP/STL/GLB/manifest `*_rev1.*` in `output/concept/`; viewer `index.html` → rev1 manifest
- **Mass (rev1 figure):** empty-case indicative 9.573 kg; regenerate via `scripts/generate_mass_report.py` — **superseded: current rev11 structural total 7.054 kg (excl. `verify_on_real_machine` parts) / all-parts total 9.292 kg per `output/validation/rev11/mass_report.csv`**
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

### Verification-tooling fix — render Z-buffer tie-break (D-040, rev11)

- `scripts/render_validation_views.py`'s PNG rasterizer had a Z-buffer tie-break defect: coplanar cladding-over-rail pairs (`PANEL-CLAD-FRONT-{BASE,ORG,TOP,TRAY-*}-001` vs their rails) always resolved to the structural rail winning, because the strict `z > depth` comparison let whichever part was inserted first (always the rail) win every coincident-depth pixel. This meant "frame concealed" render evidence since fidelity cycle 4 (rev5) never actually showed the cladding — the geometry was always correct, the tool's PNG output was not. Fixed with a material-priority epsilon tie-break (`MATERIAL_RENDER_PRIORITY`, `DEPTH_EPSILON_MM=1e-6`); regression test `tests/test_render_tiebreak.py` covers both insertion orders. Independently confirmed by adversarial review: `rev10`→`rev11` pixel histograms show an exact aluminium↔cladding swap (e.g. transport_iso.png ∓30064 px) on all four checked views, zero change to mass/stability/deflection numbers. `SLIDE-*` hardware remains visible (unchanged, known non-blocking follow-up — separate owner decision, not fixed in this cycle). See D-040.

### Stability — indicative PLT-010 closed in rev10, reconfirmed rev11 (D-039/D-040)

- Upper tray fully extended (400 mm) with both plotters installed: corrected tip-over factor **1.596** (meets TZ line 508 floor of **1.5**). Lower tray: **3.563**. Legacy mass-cancelling model had upper at **1.300** — a modelling flaw, not a geometry limitation. No ballast added. See `output/validation/rev11/stability_report.md` (identical numeric content to rev10, differing only in the revision-tag title line, per D-040's independent re-check), `state/REQUIREMENTS_TRACEABILITY.csv` PLT-010 (`PASSING`), and `docs/10_USER_INPUT_REQUIRED.md` section J. Still **not authoritative for Gate G4** — needs qualified engineering review.

### Measurements and manufacturing

- Eight physical measurements on real plotters (Cameo 4 governing + Cameo 5 slot 2) and purchased sheet materials — see `docs/10_USER_INPUT_REQUIRED.md` section A.
- Manufacturer DFM authorization — see `docs/10_USER_INPUT_REQUIRED.md` section B and Gate G5 in `docs/05_IMPLEMENTATION_PLAN.md`.

These blockers do not prevent parameter-layer work but block production geometry release and Gate G5/G6.

## Next decision

After G0 gate verdict (Human Gate), complete the consolidated input packet in `docs/10_USER_INPUT_REQUIRED.md` and start equipment envelopes only for verified selected models.
