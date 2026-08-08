# Autonomous orchestrator — living status

> **Read this first** in a new chat after `HANDOFF_PROMPT.md`. Update this file at every closed defect cycle (before commit). English only. Owner replies in Russian; do not invent production-ready / G0–G8 pass.

## Snapshot (2026-08-08)

| Field | Value |
|---|---|
| Branch | `main` |
| HEAD (mega-land) | `b4da1d7` — *Land rev15 concept tree and FIX-TIP-001 tip-factor N/A honesty.* |
| Prior base | `65d6fe3` (D-041) |
| Live `CONCEPT_REVISION` | **15** (`src/stand_cad/geometry/export.py`) |
| Envelope | **650 × 420 × 529 mm** |
| Owner-confirmed product | D-075 posts restored; D-076 upper fixed (`upper_extension=0`), lower 250 mm + door/tray choreography |
| Gates | **No G0–G8 passed** — all CONCEPT / REFERENCE_ONLY / PRELIMINARY |
| Mode | Autonomously fixing highest-impact **software/honesty** defects until owner says **СТОП** |
| Verify at land | Full `setup_windows.ps1` exit 0 — **383 passed, 1 xfailed**, ruff clean |
| Commit policy | Mega-land authorized 2026-08-08. Keep excluding `ИИ советы/`, secrets, `.pytest_cache/`. `output/` gitignored. |

## Last closed defect

### FIX-TIP-001 — upper tip-factor vacuous pass (D-077)

| | |
|---|---|
| Problem | After D-076, upper tip factor = `inf`; pytest `factor >= tip_factor_min` and report `Tip factor: inf (minimum 1.5)` were vacuous / misleading |
| Root cause | `overturn_moment <= 0 → float("inf")` is valid math; pairing with min-floor assert/publish is not |
| Fix | `StabilityReportInputs.applicable = extension > 0 and overturn_moment > 0`; report prints **N/A (D-076)** for non-applicable; lower@250 still finite (~3.785 ≥ 1.5) |
| Key paths | `src/stand_cad/geometry/analysis.py`, `scripts/generate_mass_report.py`, `tests/test_geometry.py`, `scripts/_stage1_metrics.py`, state D-077 / PLT-010 |
| Evidence | `output/validation/rev15/stability_report.md` + RFQ copy — upper N/A, lower 3.785 |
| Verify | Targeted tip tests green; Quick `pytest` + `ruff` exit 0; adversarial **approve** |
| Explicitly NOT done | Gate G4 / PLT-010 PASSING; lean/dual-tray tip closure; open-door tip physics |

**Anti-false-conclusion:** Do **not** treat `inf` as “buggy arithmetic.” Do **not** invent a finite upper tip. Do **not** claim G4 closed because lower ≥ 1.5.

## Open defect backlog (impact order)

1. **Collision allowlist burial** — `is_open_front_kinematic_contact` / `is_door_mate` can skip deep interpenetration (`collision.py`). T2+; weak oracle. Confirm before fix.
2. **Mass-report header honesty** — `generate_mass_report.py` still claims `MAINS-INLET` / `INTERLOCK-*` “physically present” after D-067/D-071. Separate from rev-sync.
3. **Stale rev13 advertising** — `docs/12` (P0 RFQ paths), README current-status, HANDOFF product-truth still say rev13 while live is 15. Refresh numbers from rev15 evidence; keep §F/§M/§N/§A OPEN. Test must not false-fail on historical `Already closed` lines.
4. **`scripts/_stage1_metrics.py` KeyError** on removed `INTERLOCK-SHUTTLE-001` (if still unguarded after tip metrics edit).
5. **Traceability CSV / ASSUMPTIONS** evidence paths still pointing at rev13 for several PLT/SWE rows.
6. Owner blockers unchanged: §F handle, §M lid headroom, §N retention, §A measurements.

## Where we are / next action

1. Land verified working tree (mega-commit + ordinary push) per owner approval.
2. Refresh this file + `HANDOFF_PROMPT.md` product-truth pointers to rev15 / D-077.
3. Pick backlog **#1 or #2** (highest remaining impact), run confirmation (reproduce → counter → root → test → safety), then T2 plan/implement/adversarial/verify; commit only that cycle’s paths when isolatable.
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
