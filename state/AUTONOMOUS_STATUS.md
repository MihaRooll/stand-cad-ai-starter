# Autonomous orchestrator — living status

> **Read this first** in a new chat after `HANDOFF_PROMPT.md`. Update this file at every closed defect cycle (before commit). English only. Owner replies in Russian; do not invent production-ready / G0–G8 pass.

## Snapshot (2026-08-08)

| Field | Value |
|---|---|
| Branch | `main` |
| HEAD | pending FIX-DOC-004 commit — ASSUMPTIONS rev15 sync (D-085) |
| Upstream | `origin/main` synced (ordinary push OK) |
| Next in flight | Owner blockers: §F handle, §M lid headroom, §N retention, §A measurements |
| Prior base | `65d6fe3` (D-041) |
| Live `CONCEPT_REVISION` | **15** (`src/stand_cad/geometry/export.py`) |
| Envelope | **650 × 420 × 529 mm** |
| Owner-confirmed product | D-075 posts restored; D-076 upper fixed (`upper_extension=0`), lower 250 mm + door/tray choreography |
| Gates | **No G0–G8 passed** — all CONCEPT / REFERENCE_ONLY / PRELIMINARY |
| Mode | Autonomously fixing highest-impact **software/honesty** defects until owner says **СТОП** |
| Verify at land | Quick verify **green** — full pytest exit 0 (393 passed, 1 xfailed), ruff clean (FIX-COLL-002 cycle 2) |
| Commit policy | Mega-land authorized 2026-08-08. Keep excluding `ИИ советы/`, secrets, `.pytest_cache/`. `output/` gitignored. |

## Last closed defect

### FIX-DOC-004-assumptions-rev15 — ASSUMPTIONS rev15 evidence sync (D-085)

| | |
|---|---|
| Problem | A-013/A-017 validation actions still cited rev13 evidence; A-014 still claimed bottom vents under modeled `AIRPATH-001` after D-071 removal |
| Root cause | Assumption register not refreshed after FIX-WAVE-004 / rev15 evidence and D-071 service-volume removal |
| Fix | A-013 → `output/validation/rev15/views/transport_*` (rev13 historical); A-017 → rev15 stability report + upper N/A (D-076/D-077); A-014 → panel through-cuts only, no current AIRPATH solid |
| Key paths | `state/ASSUMPTIONS.md`, `state/DECISION_LOG.md`, `state/AUTONOMOUS_STATUS.md` |
| Verify | `uv run ruff check state/ASSUMPTIONS.md` — exit 0 |
| Explicitly NOT done | Gate pass; §F/§M/§N/§A closure; geometry/config changes |

### FIX-COLL-002-door-mid-clearance — DOOR-LOWER ↔ PANEL-IN-MID burial (D-084)

| | |
|---|---|
| Problem | Live transport DOOR-LOWER ↔ PANEL-IN-MID-001 **5985 mm³** burial; `is_door_mate` unconditional True for MID/SOFTSTOP |
| Root cause | MID front Y at shadow gap (2.5 mm) protruded 12.5 mm ahead of closed door plane (15 mm); no volume ceiling on MID/SOFTSTOP mates |
| Fix | Path A: retract MID front Y to `datums.plotter1_physical.y.min_mm` (15.0 mm); cap MID/SOFTSTOP with `DOOR_FRONT_PLANE_MAX_BEARING_MM3 + threshold`; synthetic burial tests |
| Measured | Before **5985 mm³** → after **0 mm³** (plane touch); SOFTSTOP live vol=0 (predicate honesty) |
| Key paths | `collision.py`; `panels.py::_build_inner_mid_panel`; `tests/test_geometry.py` (mid/softstop door_mate tests); `docs/14` §9/§10 |
| Verify | Quick exit 0 — `-k "door_mate or open_front or mid or handle_mount"` + kinematics collision + full pytest + ruff |
| Explicitly NOT done | Gate pass; production-verified clearance claims |

### FIX-DOC-003-docs10-csv-rev15 — docs/10 + CSV rev15 sync (D-083)

| | |
|---|---|
| Problem | `docs/10_USER_INPUT_REQUIRED.md` §E/§F still cited stale Y=185.9 / ≈1.39×10⁶ mm³ as sole current; §H claimed MAINS-INLET placeholder solid retained; CSV rows still pointed at rev13 / 53-leaf REL-027 / 8.806 kg as current |
| Root cause | Documentation not refreshed after FIX-WAVE-004 / D-074 handle retune and D-071 service-volume removal |
| Fix | §E → Y=179.8 / ≈1,529,766 mm³ + margins 40.2/85.2; §F → ≈1.53×10⁶; §H → deferred/not modeled (D-036/D-071); CSV SWE/PLT/MFG/PRD/ELE rows → rev15 paths, CONCEPT_REVISION=15, REL-027=55, current mass 9.590/13.383 kg |
| Key paths | `docs/10_USER_INPUT_REQUIRED.md`, `state/REQUIREMENTS_TRACEABILITY.csv`, `state/DECISION_LOG.md`, `state/PROJECT_STATE.md` |
| Verify | Adversarial cycle-1 **approve** (findings=[]); Quick exit 0 — `uv run pytest tests/test_geometry.py -k handle_tier2_finger --tb=short -q`, `uv run pytest tests/test_concept_revision_docs.py`, full `uv run pytest`, `uv run ruff check .` |
| Explicitly NOT done | Gate pass; §F/§M/§N/§A closure; geometry/config changes |

### FIX-DOC-002-handoff-rev15 — HANDOFF product-truth sync (D-082)

| | |
|---|---|
| Problem | `HANDOFF_PROMPT.md` startup checklist, Product truth table, and Immediate mission still cited rev13 paths/numbers while live `CONCEPT_REVISION`=15 |
| Root cause | Documentation not refreshed after FIX-WAVE-004 / rev15 evidence and D-075…D-081 fix waves |
| Fix | Rewrite current zones to rev15 + D-075…D-081 truths; rephrase historical closed-list `CONCEPT_REVISION` lines; test scans current zones only. **Cycle 2:** drop stale 210600 lid/shuttle; tier-2 headroom 50 mm; §F intrusion ≈1,529,766 mm³; Open list in test scan. **Cycle 3:** PROJECT_STATE `## Current blockers` aligned (F-7 handle/headroom/transport/tip honesty) |
| Key paths | `HANDOFF_PROMPT.md`, `tests/test_concept_revision_docs.py` |
| Verify | Adversarial cycle-3 **approve**; Quick exit 0 — `uv run pytest tests/test_concept_revision_docs.py`, full `uv run pytest`, `uv run ruff check .` |
| Explicitly NOT done | Gate pass; §F/§M/§N/§A closure; geometry/config changes |

### FIX-TOOL-001-stage1-interlock-guard — `_stage1_metrics.py` KeyError (D-067)

| | |
|---|---|
| Problem | `scripts/_stage1_metrics.py` crashed on `parts["INTERLOCK-SHUTTLE-001"]` after D-067 removed interlock hardware |
| Root cause | Lid/shuttle intersection metrics assumed interlock always emitted |
| Fix | `.get()` guard; print `N/A (absent / D-067)` for P1/P2 lid vs shuttle when absent; volume print unchanged when present |
| Key paths | `scripts/_stage1_metrics.py` |
| Verify | `uv run python scripts/_stage1_metrics.py` + `uv run ruff check scripts/_stage1_metrics.py` — exit 0 |
| Explicitly NOT done | Interlock geometry restore; gate pass |

### FIX-COLL-001-open-front-ceiling — intersection-volume ceiling (D-080)

| | |
|---|---|
| Problem | `is_open_front_kinematic_contact` / front penetrating patterns exempted any clearance `< thr`, allowing deep burial to silent-green |
| Root cause | No intersection-volume upper bound on open-front skin bearing (unlike door F-1 / cavity-joint ceilings) |
| Fix | `OPEN_FRONT_MAX_BEARING_MM3=750.0` (live max **540 mm³**); gate open-front + four front clad/rail penetrating patterns; synthetic burial tests (open_front + penetrating) |
| Key paths | `collision.py`; `tests/test_geometry.py::test_open_front_kinematic_contact_rejects_volumetric_burial`; `tests/test_geometry.py::test_open_front_penetrating_rejects_volumetric_burial`; `docs/14` §10 |
| Verify | Targeted pytest `-k "open_front or door_mate or cavity_joint or collision"` + kinematics collision — pending adversarial/Quick |
| Explicitly NOT done | Gate pass; P2 door `PANEL-IN-MID` / `SOFTSTOP-*` unconditional True cap — **closed in FIX-COLL-002 (D-084)** |

**Anti-false-conclusion:** Green collision sweep ≠ physical clearance at prototype. Do **not** treat 750 mm³ ceiling as manufacturing sign-off.

### FIX-DOC-001-rfq-rev15 — RFQ/README advertising sync (D-079)

| | |
|---|---|
| Problem | `docs/12` and README **Current status** still advertised rev13 paths/numbers while live `CONCEPT_REVISION`=15 |
| Root cause | Documentation not refreshed after FIX-WAVE-004 / rev15 evidence generation |
| Fix | Subject + Attached package + indicative mass/tip table → rev15 evidence; MAINS-INLET honesty (D-071); regression test `tests/test_concept_revision_docs.py` |
| Key paths | `docs/12_PRODUCTION_RFQ_TEMPLATE.md`, `README.md`, `tests/test_concept_revision_docs.py` |
| Verify | `uv run pytest tests/test_concept_revision_docs.py -q` + Quick profile — exit 0 |
| Cycle 2 | F-1: fastener total **162** (drop dead D-069 base-clad M3); F-2: STACK-CAP **~0.118 kg** from rev15 CSV; F-3: REL-027 **55**; F-4: §N plotter tie-down waived |
| Explicitly NOT done | Gate pass; §F/§M/§N/§A closure; full HANDOFF rewrite |

**Anti-false-conclusion:** Do **not** treat indicative mass/tip figures as G4 sign-off. Do **not** re-open removed service-volume solids without owner decision.

## Open defect backlog (impact order)

1. Owner blockers unchanged: §F handle, §M lid headroom, §N retention, §A measurements.

## Where we are / next action

1. Land verified working tree (mega-commit + ordinary push) per owner approval.
2. Pick backlog **#1** (highest remaining impact), run confirmation (reproduce → counter → root → test → safety), then T2 plan/implement/adversarial/verify; commit only that cycle's paths when isolatable.
3. Prefer Quick mid-cycle; Full before stage-final commits.

## Protection rules (do not skip)

- Physical / tip / clearance / mass claims → **T2 min** + mandatory `adversarial-reviewer`.
- Green pytest ≠ physical correctness.
- Findings need path, lines, requirement ID, reproducible evidence.
- Never mark G0–G8 passed or production-ready.
- Never invent equipment/load/thermal/bend data.
- Always `uv run` (not bare `python`).
- Subagent DROP/WEAKEN must be weighed; Main may keep an honesty fix when publish+gate mislead even if math sentinel is intentional.

## Commands

| Profile | Command |
|---|---|
| Quick | `uv run pytest` and `uv run ruff check .` |
| Full | `powershell -ExecutionPolicy Bypass -File .\scripts\setup_windows.ps1` |
| Tip smoke | `uv run pytest tests/test_geometry.py -k "tip_factor or stability_split" --tb=short` |
| Regen reports | `uv run python scripts/generate_mass_report.py` |

## Update log

| When | Change |
|---|---|
| 2026-08-08 | Created. FIX-TIP-001 done in WT; mega-commit authorized; backlog listed. |
| 2026-08-08 | FIX-MASS-001 closed (D-078); backlog #2 removed; header honesty test added. |
| 2026-08-08 | FIX-COLL-001 closed (D-080); open-front volume ceiling 750 mm³; backlog #1 narrowed to door PANEL-IN-MID/SOFTSTOP P2. |
| 2026-08-08 | FIX-TOOL-001 closed (D-081); `_stage1_metrics.py` interlock N/A guard; backlog #2 removed. |
| 2026-08-08 | FIX-COLL-002 closed (D-084); DOOR-LOWER↔MID 5985→0 mm³; P2 MID/SOFTSTOP backlog cleared. |
| 2026-08-08 | FIX-DOC-003 closed (D-083); docs/10 §E/§F/§H + CSV current-evidence → rev15; backlog #2 (CSV rev13 pointers) removed. |
| 2026-08-08 | FIX-DOC-002 closed (D-082); HANDOFF current zones → rev15; backlog #3 (HANDOFF product-truth) removed. |
| 2026-08-08 | FIX-DOC-002 cycle 3: PROJECT_STATE Current blockers honesty (F-7/F-8/F-9). |
| 2026-08-08 | FIX-DOC-004 closed (D-085); A-013/A-017 → rev15 evidence; A-014 AIRPATH honesty (D-071). |
