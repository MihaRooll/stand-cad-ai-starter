# Autonomous orchestrator — living status

> **Read this first** in a new chat after `HANDOFF_PROMPT.md`. Update this file at every closed defect cycle (before commit). English only. Owner replies in Russian; do not invent production-ready / G0–G8 pass.

## Snapshot (2026-08-08)

| Field | Value |
|---|---|
| Branch | `main` |
| HEAD | `d816e5a` (status snapshot); mega-land `b4da1d7` — *Land rev15 + FIX-TIP-001* |
| Upstream | `origin/main` synced (ordinary push OK) |
| Next in flight | Collision allowlist burial — backlog #1 confirmation |
| Prior base | `65d6fe3` (D-041) |
| Live `CONCEPT_REVISION` | **15** (`src/stand_cad/geometry/export.py`) |
| Envelope | **650 × 420 × 529 mm** |
| Owner-confirmed product | D-075 posts restored; D-076 upper fixed (`upper_extension=0`), lower 250 mm + door/tray choreography |
| Gates | **No G0–G8 passed** — all CONCEPT / REFERENCE_ONLY / PRELIMINARY |
| Mode | Autonomously fixing highest-impact **software/honesty** defects until owner says **СТОП** |
| Verify at land | Full `setup_windows.ps1` exit 0 — **383 passed, 1 xfailed**, ruff clean |
| Commit policy | Mega-land authorized 2026-08-08. Keep excluding `ИИ советы/`, secrets, `.pytest_cache/`. `output/` gitignored. |

## Last closed defect

### FIX-MASS-001 — mass-report header honesty (D-078)

| | |
|---|---|
| Problem | `generate_mass_report.py` header claimed `MAINS-INLET-001` / `INTERLOCK-*` / `EDGEGUARD-*` "physically present" after D-046/D-067/D-071 removed them from transport |
| Root cause | Static header text not updated when parts were removed from `build_transport_assembly()` |
| Fix | `_present_other_excluded_category_labels()` builds header from live `transport.parts`; only `SLIDE-*`, `VIBMOUNT-*`, `etc.` listed |
| Key paths | `scripts/generate_mass_report.py`, `tests/test_geometry.py::test_mass_report_header_honest_excluded_categories`, `output/validation/rev15/mass_report.csv` + RFQ copy |
| Verify | `uv run pytest -k mass_report` + ruff on touched py — exit 0 |
| Explicitly NOT done | Gate G4 / PLT-012 PASSING; mass-formula / geometry changes |

**Anti-false-conclusion:** Do **not** treat indicative mass totals as G4 sign-off. Do **not** re-add removed categories to transport without owner decision.

## Open defect backlog (impact order)

1. **Collision allowlist burial** — `is_open_front_kinematic_contact` / `is_door_mate` can skip deep interpenetration (`collision.py`). T2+; weak oracle. Confirm before fix.
2. **Stale rev13 advertising** — `docs/12` (P0 RFQ paths), README current-status, HANDOFF product-truth still say rev13 while live is 15. Refresh numbers from rev15 evidence; keep §F/§M/§N/§A OPEN. Test must not false-fail on historical `Already closed` lines.
3. **`scripts/_stage1_metrics.py` KeyError** on removed `INTERLOCK-SHUTTLE-001` (if still unguarded after tip metrics edit).
4. **Traceability CSV / ASSUMPTIONS** evidence paths still pointing at rev13 for several PLT/SWE rows.
5. Owner blockers unchanged: §F handle, §M lid headroom, §N retention, §A measurements.

## Where we are / next action

1. Land verified working tree (mega-commit + ordinary push) per owner approval.
2. Refresh `HANDOFF_PROMPT.md` product-truth pointers to rev15 / D-077 / D-078.
3. Pick backlog **#1** (highest remaining impact), run confirmation (reproduce → counter → root → test → safety), then T2 plan/implement/adversarial/verify; commit only that cycle's paths when isolatable.
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
