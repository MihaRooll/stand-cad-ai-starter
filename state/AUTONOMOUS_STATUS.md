# Autonomous orchestrator — living status

> **Read this first** in a new chat after `HANDOFF_PROMPT.md`. Update this file at every closed defect cycle (before commit). English only. Owner replies in Russian; do not invent production-ready / G0–G8 pass.

## Snapshot (2026-08-08)

| Field | Value |
|---|---|
| Branch | `main` |
| HEAD | `5eb2375`+ working tree — FIX-DOC-001-rfq-rev15 in progress |
| Upstream | `origin/main` synced (ordinary push OK) |
| Next in flight | Door PANEL-IN-MID / SOFTSTOP unconditional True (P2 honesty backlog) |
| Prior base | `65d6fe3` (D-041) |
| Live `CONCEPT_REVISION` | **15** (`src/stand_cad/geometry/export.py`) |
| Envelope | **650 × 420 × 529 mm** |
| Owner-confirmed product | D-075 posts restored; D-076 upper fixed (`upper_extension=0`), lower 250 mm + door/tray choreography |
| Gates | **No G0–G8 passed** — all CONCEPT / REFERENCE_ONLY / PRELIMINARY |
| Mode | Autonomously fixing highest-impact **software/honesty** defects until owner says **СТОП** |
| Verify at land | Full `setup_windows.ps1` exit 0 — **383 passed, 1 xfailed**, ruff clean |
| Commit policy | Mega-land authorized 2026-08-08. Keep excluding `ИИ советы/`, secrets, `.pytest_cache/`. `output/` gitignored. |

## Last closed defect

### FIX-COLL-001-open-front-ceiling — intersection-volume ceiling (D-080)

| | |
|---|---|
| Problem | `is_open_front_kinematic_contact` / front penetrating patterns exempted any clearance `< thr`, allowing deep burial to silent-green |
| Root cause | No intersection-volume upper bound on open-front skin bearing (unlike door F-1 / cavity-joint ceilings) |
| Fix | `OPEN_FRONT_MAX_BEARING_MM3=750.0` (live max **540 mm³**); gate open-front + four front clad/rail penetrating patterns; synthetic burial tests (open_front + penetrating) |
| Key paths | `collision.py`; `tests/test_geometry.py::test_open_front_kinematic_contact_rejects_volumetric_burial`; `tests/test_geometry.py::test_open_front_penetrating_rejects_volumetric_burial`; `docs/14` §10 |
| Verify | Targeted pytest `-k "open_front or door_mate or cavity_joint or collision"` + kinematics collision — pending adversarial/Quick |
| Explicitly NOT done | Gate pass; P2 door `PANEL-IN-MID` / `SOFTSTOP-*` unconditional True cap (no measured contacts) |

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

1. **Door PANEL-IN-MID / SOFTSTOP unconditional True** — `is_door_mate` returns True without volume ceiling; no clearance `< thr` contacts measured in transport / service_p1 / tray1_qa. T2+; do not invent cap without evidence.
2. **`scripts/_stage1_metrics.py` KeyError** on removed `INTERLOCK-SHUTTLE-001` (if still unguarded after tip metrics edit).
3. **Traceability CSV / ASSUMPTIONS** evidence paths still pointing at rev13 for several PLT/SWE rows.
4. **HANDOFF product-truth** still cites rev13 in Product truth header — refresh in a follow-up packet (test excludes historical closed lists).
5. Owner blockers unchanged: §F handle, §M lid headroom, §N retention, §A measurements.

## Where we are / next action

1. Land verified working tree (mega-commit + ordinary push) per owner approval.
2. Pick backlog **#1** (highest remaining impact), run confirmation (reproduce → counter → root → test → safety), then T2 plan/implement/adversarial/verify; commit only that cycle's paths when isolatable.
3. Refresh `HANDOFF_PROMPT.md` product-truth pointers to rev15 / D-077 / D-078 / D-079 in a follow-up packet.
4. Prefer Quick mid-cycle; Full before stage-final commits.

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
