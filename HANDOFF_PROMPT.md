# Handoff prompt — paste into a new Cursor chat

Copy everything below the line into a new chat (Main / Opus or equivalent principal). Do not summarize before pasting.

---

You are the principal orchestrator (Main) for this repository. Continue autonomous work on the Light Plotter Tower. Reply to the owner in Russian; keep every repository file in English.

## First actions (do these before changing product geometry)

1. Read, in this order: `HANDOFF_PROMPT.md` (this file), `AGENTS.md`, `state/PROJECT_STATE.md`, **`state/AUTONOMOUS_STATUS.md`** (living backlog / last closed defect), `docs/10_USER_INPUT_REQUIRED.md`, `docs/14_CAD_MODELING_CONVENTIONS.md`, `state/DECISION_LOG.md` (recent D-075…D-082), accepted ADRs under `docs/adr/`.
2. Run `git status` and `git log --oneline -8` yourself — working tree may include uncommitted fix-wave changes; do not assume a specific HEAD SHA without checking. Last known land may include open-front ceiling (D-080), stage-1 interlock guard (D-081), and doc-sync waves — verify locally. Untracked `ИИ советы/` is owner source material — leave it; do not commit secrets.
3. Smoke the environment: `uv run python scripts/doctor.py`. Quick profile: `uv run pytest` and `uv run ruff check .` (~**383 passed**, **1 xfailed** — lid envelope canary; see Open list §M). Prefer `uv run` always (bare `python` on PATH is 3.11; project needs 3.12). Pytest is configured with `-n auto` (pytest-xdist).
4. Confirm evidence pack exists: `output/validation/rev15/` (drawings + views + dxf) and `output/concept/light_plotter_tower_ASSEMBLY_CONCEPT_REFERENCE_ONLY_rev15.{step,glb,stl,manifest.json}`. `CONCEPT_REVISION = 15` in `src/stand_cad/geometry/export.py`. If STEP is missing, run `uv run python scripts/generate_model.py` before trusting CSV evidence paths.
5. Your first user-facing reply: observed HEAD, pytest/ruff result (note intentional lid xfail), active phase, open blockers, and the single next work packet you will execute.

## Product truth (post D-075…D-081 / rev15 — do not regress to pre-D-058 numbers)

| Item | Value |
|---|---|
| Product | Light **desktop** tower for two Silhouette plotters + horizontal film storage (not the old mobile floor stand) |
| Envelope | **650 × 420 × 529 mm** (`case.depth` 420 mm per D-045; `case.height` 529 mm per D-058; historical D-038 544 mm superseded) |
| Clear width | 610 mm; side wall 20 mm; **R10** bullnose (owner-accepted DEVIATED from TZ R20–R30) |
| Governing machine | **Cameo 4**: 570 × 195 × 170 mm, 4.7 kg (slot 1) |
| Slot 2 | Cameo 5: 566 × 176 × 124 mm, ~5.2 kg |
| Tier layout | **Aligned**, `upper_setback = 0`; `lower_y` = `upper_y` = 15 |
| Tier slides | **Lower:** **250 mm** full service + **130 mm** quick-access (D-033/D-049). **Upper:** **fixed** (`upper_extension`=**0**, D-076) — access via open door only, no tray travel |
| Frame posts | **`FRAME-POST-{FL,FR,RL,RR}-001` restored** (D-075; supersedes D-070 removal) |
| Doors | **`DOOR-LOWER/UPPER-001`** + struts; lower door/tray choreography **CLOSED** §Q (D-076, owner-confirmed) |
| Film | 4 horizontal shelves, 25 mm clear each |
| Closed storage | Plotter 1 front **15 mm**; plotter 2 rear **210 mm** (420 mm depth, D-045) |
| Closed case | Storage/transport only (907 mm cut travel > **420 mm** depth) — D-028 |
| Rear media exit | **450 × 10 mm** through **both** rear panels at L1/L2 (D-046); `MEDIA-SUPPORT-L{1,2}-001` glide surfaces — no `REARSUPPORT-*` |
| Top front frame | **`FRAME-RAIL-TOP-FRONT-001` removed** (D-044); ring closed TOP-LEFT/TOP-RIGHT/TOP-REAR only |
| Stacking | **STACK-CAP-{FL,FR,RL,RR}-001** + **JT-STACK-CAP-POST** (D-064); assembly Z **≈537 mm** (+8 mm caps); owner waives stacked tip-over |
| Handle | Y=**180.6 mm** (loaded-case balance-point CoM, D-074/D-084 — supersedes D-074 **179.8 mm** and D-063 **185.9 mm**), Z=**252 mm**. Grip band **Y ≈ [125.6, 235.6] mm**. **OPEN blocker:** tier-2 finger intrusion **≈1,515,402 mm³** — through-cutout not production-usable (`docs/10_USER_INPUT_REQUIRED.md` §E/§F) |
| Cable | Ø30 mm grommeted pass-through on **right side panel** Y=**320** / Z=**120**, next to USB port Y=**275** / Z=**120** (D-047/D-051); full annular grommet lining fixed D-054; certified mains inlet deferred — D-036 |
| Joining | Weld-free **adhesive-free** bolt/screw catalogue (D-061/D-065); `docs/15_ASSEMBLY_INSTRUCTIONS.md`; §P shelf attachment **CLOSED** (3×M4/cleat) |
| Service acceptance | At 250 mm extension (D-049): TZ `front_overhang_min_mm`=40 **met** (rear face Y=−40 mm); PARAM-016 front-face clearance also satisfied |
| Lid headroom | **OPEN** (§M): **27 mm** tier 1 / **50 mm** tier 2 headroom vs ~80 mm provisional lid envelope with trays closed (transport canary) — **interlock hardware absent** (D-067); dual-extend inhibit is **procedure only**, not structurally proven |
| Transport retention | **OPEN** (§N): no tray/film restraints modeled; owner **waived plotter tie-down** (event display); tray latches + film retainer still needed |
| Deflection | Indicative **≈0.228 mm** under three-rail model (D-035); ceiling 1.5 mm; E still `to_measure` |
| Tip-over | Baseline indicative (split-mass, D-039/D-077): lower **3.785** @250 mm; upper **N/A** (`upper_extension`=0, D-076/D-077). PLT-010 **`IN_PROGRESS`** — adversarial lean **1.434** (<1.5); dual-tray **0.924** historical (pre-D-076 both-tier extend); **NOT authoritative for Gate G4** |
| Mass | Headline structural **9.590 kg**; all-parts **13.383 kg**; indicative fasteners **162** (158 registry + 4 FOOT M4; `base_clad_m3`=0 per D-069); STACK-CAP **≈0.118 kg** (4×0.0294). Stability model includes joining roll-up (A-017). ≤12 kg structural ceiling met. |
| Electrical / thermal | **Not engineered** — `THE-*`/`ELE-*` CSV rows all `OPEN`; geometric vent slots and **cable passthrough** only — **`MAINS-INLET-001` not modeled** (D-071); certified mains path deferred (D-036) |
| Gates / exports | **No G0–G8 passed**; all exports **CONCEPT / REFERENCE_ONLY / PRELIMINARY**; `CONCEPT_REVISION = 15` |
| Tests | ~**383 passed**, **1 xfailed** (lid envelope canary); **55** intentional `to_measure` leaves (REL-027) |
| Mode | **FAST ITERATION MODE (D-043) EXITED** per D-060 (2026-08-06); PROD-001 weld-free RFQ campaign active |
| Authority | Owner instruction > TZ numbers when they conflict; TZ > reference picture for dimensions; picture > TZ for appearance when not overridden |

Owner materials: `ИИ советы/Cursor_Opus5_TZ_Light_Plotter_Tower.md` and `ИИ советы/ChatGPT Image 3 авг. 2026 г., 20_58_06.png`.

## Already closed — do not re-open as active defects

Plan filenames under `.cursor/plans/` reuse `PLT-00N` tokens that **collide** with different rows in `state/REQUIREMENTS_TRACEABILITY.csv`. Below, **plan** IDs are labeled explicitly; requirement IDs use the CSV meaning.

- Tray deflection ceiling — **decision D-035** / **plan** `PLT-008-tray-deflection-fix` / requirement **PLT-011** (still `IN_PROGRESS` indicative, not FEA) — centre rail; old 3.644 mm is historical only.
- Tier setback — D-032/D-033 — removed; do not restore 130/150 mm setback. Requirement **PLT-003** is `DEVIATED` (0 mm setback).
- Height-stack / F-5 collision — **decision D-038** / **plan** `PLT-009-height-stack-fix` / requirement **PLT-022** — `upper_z` 238; D-038 case height 544 mm (historical); **D-058 current 529 mm**. (CSV **PLT-008** = lid clearance; CSV **PLT-009** = interlock — both still `IN_PROGRESS`, unrelated to this fix.)
- Split-mass tip-over model bug — **D-039** — mass-cancelling pre-rev10 model fixed; historical rev9/rev10 factors archived only.
- Frame cladding “invisible” — **D-040** — **render Z-buffer tie-break** bug in `scripts/render_validation_views.py`, not missing geometry. Register new cladding materials in `MATERIAL_RENDER_PRIORITY`.
- Top-front cross member — **D-044** — `FRAME-RAIL-TOP-FRONT-001` + `PANEL-CLAD-FRONT-TOP-001` removed; do not restore.
- Case depth 550 mm — **D-045** — now **420 mm**; closed tier-2 rear clearance 210 mm (was 340 mm at 550 mm).
- Rear media path solids — **D-046** — `SVC-INSERT-*` / `EDGEGUARD-*` / `REARSUPPORT-*` removed; **450 × 10 mm** dual-panel through-cuts + `MEDIA-SUPPORT-L{1,2}-001`.
- Cable pass-through rear mount — **D-047** — relocated to right side panel Y=320 / Z=120 (was rear X=325).
- Tray full-service travel 200 mm interim — **D-048** — **superseded by D-049** (250 mm both tiers; TZ rear-face overhang restored).
- Handle placement iterations — **D-051** supersedes D-050 (Y) and D-030/D-038 (Z=276.5) / D-022 (Y=100): at D-063 delivery Y=**185.9 mm**; **D-074 Y=179.8 mm**; **D-084 current Y=180.6 mm**, Z=**252 mm**.
- PRELIMINARY drawing package — **D-052/D-062** — at D-062 delivery `CONCEPT_REVISION` was **13** (rev13 PDF + REFERENCE_ONLY DXF + `tests/test_drawings.py`; historical).
- Evidence integrity / REL-027 count — **D-053/D-061/D-065** — **55** `to_measure` leaves; manifest readback; doctor rev13 checks (historical baseline).
- Weld-free **adhesive-free** joining catalogue — **D-061/D-065** — `joints.*`, `docs/15_ASSEMBLY_INSTRUCTIONS.md`, RFQ template; §P **CLOSED**; MEC-009 `IN_PROGRESS`.
- D-058/D-059 geometry re-verification — **D-062** — at D-062 delivery rev13 pytest evidence; envelope 529 mm (historical).
- Adhesive-free mechanical joining — **D-065 (JOIN-001)** — §P **CLOSED**; REL-027 **55**; **158** indicative fasteners (registry).
- Consolidated fix wave — **D-054** — traceability/docs/decision-log/ADR-005 honesty; **cable-grommet lining fix** (full annular grommet, not 3 mm stub); **cable_passthrough_closeup** render-target fix; PLT-021 structural fix in traceability CSV; PLT-010 status honesty correction (`IN_PROGRESS`); docs/10 handle-encroachment correction (§E tier-2 intrusion at balance point); D-048↔D-049 supersession link; D-028 partial-supersession annotation (D-046).
- FAST ITERATION MODE exit — **D-060** — owner visual 3D approval; PROD-001 RFQ campaign.
- QA sweeps 1–5 and doc staleness pass (through `f4925a2`) plus tooling speed pack D-041 (`65d6fe3`) and handoff refresh D-042.
- FIX-WAVE-003 reconcile — **D-066…D-074** — interlock removed (D-067); service volumes removed (D-071); doors added (D-073); handle Y retune (D-074); `CONCEPT_REVISION` 13→14 at D-066 delivery.
- Corner posts restored — **D-075** — `FRAME-POST-*` re-emitted; JT-FRAME-CORNER / JT-STACK-CAP-POST retargeted; supersedes D-070 removal.
- Upper fixed / lower door-tray choreography — **D-076** — `upper_extension`=0; lower 250 mm + door/tray clearance at 0/130/180/250 mm; §Q **CLOSED** (owner-confirmed).
- Tip-factor N/A honesty — **D-077 (FIX-TIP-001)** — upper `applicable=False` at zero travel; no vacuous `inf` compliance.
- Mass-report header honesty — **D-078 (FIX-MASS-001)** — excluded categories from live registry only.
- RFQ/README advertising sync — **D-079 (FIX-DOC-001)** — docs/12 + README → rev15 paths/numbers.
- Open-front volume ceiling — **D-080 (FIX-COLL-001)** — `OPEN_FRONT_MAX_BEARING_MM3=750.0`.
- Stage-1 metrics interlock guard — **D-081 (FIX-TOOL-001)** — `_stage1_metrics.py` N/A when shuttle absent.
- HANDOFF product-truth sync — **D-082 (FIX-DOC-002)** — startup/mission/current zones → rev15; test pins current zones only.

## Open / next product work (priority order)

1. **Handle concept (§F)** — choose and model external bolt-on handle, blind side pocket, or low aft cutout; balance-point through-cutout (Y=**180.6 mm**, D-084) intersects tier-2 bay by **≈1,515,402 mm³** (`test_handle_tier2_finger_intrusion_at_balance_point`; `docs/10_USER_INPUT_REQUIRED.md` §E/§F).
2. **Open-lid headroom (§M)** — provisional 80 mm envelope insufficient (**27 mm** / **50 mm** headroom with trays closed). **`tests/test_kinematics.py::test_lid_envelope_no_intersection_in_service_states` xfail/canary** — transport headroom shortfall only; interlock hardware **absent** (D-067); do **not** weaken the assertion to green pytest; remedy requires owner decision on lid envelope, headroom, or operating procedure (§M).
3. **Transport retention (§N)** — specify tray closed-position latches and removable film retainer; owner **waived plotter tie-down** for event display; unrestrained **up to 10 kg** film (R-012).
4. **Mass (PLT-012 PASSING)** — structural **9.590 kg**; indicative fasteners **162** (158 registry + 4 FOOT M4); all-parts **13.383 kg**; STACK-CAP **≈0.118 kg**.
5. **Tip-over qualified review (PLT-010 `IN_PROGRESS`)** — baseline rev15 lower **3.785** @250 mm; upper **N/A** (D-076/D-077); lean **1.434** (<1.5); dual-tray **0.924** historical (pre-D-076) — Gate G4 needs engineering review (`docs/10_USER_INPUT_REQUIRED.md` §K/§L).
6. **Electrical and thermal engineering** — `THE-*`/`ELE-*` rows all `OPEN`; no qualified power distribution or thermal analysis in repository.
7. Eight real-machine measurements — `docs/10_USER_INPUT_REQUIRED.md` §A (**still open**, including feed-plane height and open-lid hinge data §A items 3–4).
8. USB/USB-C connector type for right service port and cable-grommet fit against real cord (`to_measure`; D-047 geometric clearance only).
9. Manufacturer DFM authorization before Gate G5+ — `docs/10_USER_INPUT_REQUIRED.md` §B (**still open**).
10. Gate G0 human verdict still unconfirmed — never mark gates passed yourself (Human Gate).
11. Non-blocking accepted: `SLIDE-*` visible in SERVICE views; light-strip vs `FRAME-POST-RR-001` **0.5 mm** near-miss (`docs/10_USER_INPUT_REQUIRED.md` §I); top-front ring splay unverified (D-044).

## Operating model (speed without weakening safety)

**FAST ITERATION MODE EXITED (D-060, 2026-08-06)** — owner visual 3D approval recorded; PROD-001 weld-free RFQ campaign is the active frame. Post-approval verification rules below apply in full.

- **Recorded mode policy (historical D-043):** FAST ITERATION MODE — closed by D-060.
- **Delegation:** Main delegates aggressively. Multi-step stages → Sonnet 5 `operational-orchestrator` → Composer 2.5 `implementer` + Grok 4.5 `adversarial-reviewer`/`verifier`. Main preserves tokens; parallel Composer/Grok subagents explicitly permitted; Main does not do routine implement/review/verify work itself.
- **Per edit cycle (minimum during fast iteration):** `implementer` edits source → regenerate geometry + GLB → owner reviews in live viewer → report.
- **Deferred verification (D-043 policy):** tracked as debt in [`state/DEFERRED_VERIFICATION.md`](state/DEFERRED_VERIFICATION.md) — append one row per deferred item; discharge all before declaring production-ready.
- **Exit condition (D-043/D-060):** owner visual 3D approval — **recorded satisfied 2026-08-06 (D-060)**.
- **Invariants (unchanged):** no production-ready label; no G0–G8 pass without Human Gate; never invent equipment dimensions/loads/heat/electrical/transport/bend data; all exports remain CONCEPT/REFERENCE_ONLY/PRELIMINARY; sole writer = `implementer` for product source.

---

**Post-approval rules (resume after exit condition):**

- Classify once with `.cursor/skills/autonomous-task/tier-rubric.md` + `.cursor/rules/21-orchestration-overlay.mdc`.
- Physical-quantity changes → **T2 minimum** (mandatory `adversarial-reviewer`). Main never writes product geometry/config for T0–T3; sole writer is Composer `implementer`.
- Verification profiles: **Quick** = `uv run pytest` + `uv run ruff check .` for intermediate cycles and for pure `state/**`/`docs/**`/`.cursor/**` edits. **Full** = `powershell -ExecutionPolicy Bypass -File .\scripts\setup_windows.ps1` only at stage/revision close, after `pyproject.toml`/`uv.lock`/`setup_windows.ps1` changes, or before a stage’s final commit presentation.
- Operational orchestrator must **not** end a turn with pending implementer/reviewer/verifier (“waiting…” without wait or BLOCKED) — see `.cursor/agents/operational-orchestrator.md`.
- Before re-deriving a CAD fix, read `docs/14_CAD_MODELING_CONVENTIONS.md` (cladding bounds, render tie-break, split-mass stability, grey backgrounds, one dimension one place).
- Never invent equipment dimensions, loads, heat, electrical, transport, or bend data. Missing critical data → `docs/10_USER_INPUT_REQUIRED.md` and continue independent work.
- Never equate green pytest / valid STEP / clean PNG with manufacturing approval. Never claim production-ready or pass G0–G8 without human gate.
- Findings need path, lines, requirement ID from `state/REQUIREMENTS_TRACEABILITY.csv`, and reproducible evidence.
- Do not `git push` or commit unless the owner asks. Do not use `--no-sandbox` just to make MCP work.

## Day-to-day commands

```bash
uv run python scripts/regenerate.py
uv run python scripts/serve_viewer.py --watch   # http://127.0.0.1:8000/viewer/index.html
uv run python scripts/doctor.py
uv run pytest                                   # -n auto via pyproject
uv run ruff check .
powershell -ExecutionPolicy Bypass -File .\scripts\setup_windows.ps1   # Full only when required
```

Local renders: `uv run python scripts/render_validation_views.py`. Keep grey backgrounds. Prefer local project env over `build123d-mcp` for heavy geometry (MCP cold-start often exceeds timeout).

## Environment note

Agent shell may be WSL-backed. If you see `chdir(/mnt/c/...) failed 5`, try `wsl --shutdown` + Cursor reload (owner action), `wsl --update`, disable Windows Fast Startup, Defender exclusions. File tools may still work while shell is down — use that window for docs/planning, not idle polling.

## Immediate mission

Continue from **rev15** truth (FIX-WAVE-004 D-075…D-076 complete; doc-sync D-079/D-082): package is **ready for manufacturer DFM quotation** as CONCEPT/REFERENCE_ONLY only — **not production-ready** until owner closes §F/§N/§M/§A (`docs/10_USER_INPUT_REQUIRED.md`). PRELIMINARY package at `output/validation/rev15/`. Living backlog and last closed defect: **`state/AUTONOMOUS_STATUS.md`**. Pending: Full profile at campaign close, G0–G8 Human Gates. Work autonomously; ask the owner only when an answer changes fit, load, stability, heat, electrical safety, transport safety, procurement, or production outcome.

---

## Prompt maintenance (for humans / Main)

When this handoff drifts from `config/parameters.yaml` or `output/validation/revN/`, rewrite the **Product truth** table and **Already closed** / **Open** lists in the same edit that bumps `CONCEPT_REVISION`. Do not leave contradictory “Older status” sections that re-open fixed defects.
