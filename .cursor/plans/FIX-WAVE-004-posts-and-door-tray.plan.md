# FIX-WAVE-004 — Corner posts restore + lower door/tray choreography

```yaml
contract_id: FIX-WAVE-004-posts-and-door-tray
tier: T2
cycle: 2
status: complete
sol_approved: null
review_verdict_cycle_1: rework
review_verdict_cycle_2: approve  # after docs F-8..F-10
verifier_verdict: pass
blocker_findings_closed: [F-1, F-2]
major_findings_closed: [F-3, F-4, F-5]
minor_findings_closed: [F-6, F-7]
docs_findings_closed: [F-8, F-9, F-10]
goal: >
  Restore consistency after owner D-075 corner-post return; apply upper_extension=0
  (Main best-guess); redesign lower open-door + strut geometry so lower tray can
  travel 0–250 mm over the locked horizontal door without volumetric collision.
acceptance_criteria:
  - id: AC-1
    text: transport emits FRAME-POST-FL/FR/RL/RR-001; D-070 "posts absent" tests inverted
  - id: AC-2
    text: JT-FRAME-CORNER / JT-STACK-CAP-POST notes retargeted to post-primary mating (rail nodes may remain supplementary)
  - id: AC-3
    text: trays.upper_extension=0; trays.lower_extension stays 250; provenance notes D-076
  - id: AC-4
    text: lower open door + struts clear tray/slides/plotter at sampled extensions 0,130,180,250 mm (vol≈0)
  - id: AC-5
    text: if AC-4 intractable, §Q stays OPEN with precise conflict + 2–3 redesign options (no fake-green)
  - id: AC-6
    text: docs/10 §R CLOSED; D-075/D-076 in DECISION_LOG; state/PROJECT_STATE + TRACEABILITY updated
  - id: AC-7
    text: CONCEPT_REVISION bumped ≥15; scripts/regenerate.py succeeds
  - id: AC-8
    text: Quick (pytest+ruff) green after implement; Full profile green before done
owned_files:
  - src/stand_cad/geometry/doors.py
  - src/stand_cad/geometry/assembly.py
  - src/stand_cad/geometry/export.py
  - src/stand_cad/geometry/collision.py
  - src/stand_cad/geometry/kinematics.py
  - src/stand_cad/geometry/frame.py
  - config/parameters.yaml
  - tests/test_geometry.py
  - tests/test_kinematics.py
  - tests/test_parameters.py
  - docs/10_USER_INPUT_REQUIRED.md
  - docs/14_CAD_MODELING_CONVENTIONS.md
  - docs/15_ASSEMBLY_INSTRUCTIONS.md
  - docs/08_RISK_REGISTER.md
  - state/DECISION_LOG.md
  - state/PROJECT_STATE.md
  - state/REQUIREMENTS_TRACEABILITY.csv
  - state/ASSUMPTIONS.md
verify_commands:
  - uv run ruff check .
  - uv run pytest -q
  - powershell -ExecutionPolicy Bypass -File .\scripts\setup_windows.ps1
forbidden:
  - Mark any G0–G8 gate passed
  - Label artifacts production-ready
  - Fake-green door/tray collisions via mating exemptions or strut omission alone
  - Bare python / scripts/verify-harness.ps1
  - Invent equipment/load/heat/electrical data
steps:
  - id: S-1
    action: Plan written (this artifact)
    owner: operational-orchestrator
  - id: S-2
    action: Implement posts consistency + door/tray geometry + docs/state + regenerate
    owner: implementer
  - id: S-3
    action: Mandatory adversarial review of product diffs
    owner: adversarial-reviewer
  - id: S-4
    action: Fix rework from review (cycles ≤3; cycle 3 blocker-only)
    owner: implementer
  - id: S-5
    action: Independent Quick+Full verification
    owner: verifier
```

## Engineering intent

### A. Corner posts (D-075) — consistency only

Main already restored `build_frame_posts()`. Implementer must:

1. Invert/remove `test_corner_posts_not_emitted` → assert four `FRAME-POST-*` present.
2. Update foot/post mate docs/tests that still say "posts removed D-070".
3. **Joint metadata judgement (orchestrator):** restore **post-primary** language for `JT-FRAME-CORNER` (`FRAME-POST-*` ↔ `FRAME-RAIL-*`) and `JT-STACK-CAP-POST` (`STACK-CAP-*` ↔ post tops / top-ring). Keep rail-to-rail / panel bearing as **supplementary** valid mating at the same corners now that both posts and rails exist — do not delete rail patterns if schedule counts depend on them; document dual scheme in notes. Update `JT-TRAY-RAIL-FRAME` / `JT-PANEL-OUTER-FRAME` notes that still say posts removed.
4. Close `docs/10` §R; update `docs/08` R-016 / `docs/15` post-removal language; add D-075 decision row.

### B. Upper fixed / lower door choreography (D-076)

**Assumption (Main best-guess — flag in ASSUMPTIONS + final report):**

- `trays.upper_extension` → **0**. Upper access = open `DOOR-UPPER-001` only; tray/plotter stationary.
- `trays.lower_extension` stays **250**. Lower door drops to horizontal and locks; tray slides out over/across it.

**Geometry problem (measured):** open `DOOR-LOWER-001` buries into `SLIDE-LOWER-*` (~5–7×10³ mm³); struts clash with plotter (~7.4×10³ mm³) — current omit-when-extended is insufficient.

**Preferred CONCEPT fix (simplest that reads correctly):**

1. **Door resting plane:** ensure open-door top face Z ≤ tray underside Z − assembly clearance (slides must also clear — check slide bottom Z across travel). Prefer adjusting open-door Z (hinge offset / post-open settle) over changing tray stack unless unavoidable.
2. **Struts:** keep struts in open states; relocate pivots/attachments outside tray X-span (corner-post side faces) and/or route under the open door so the strut cylinder never intersects tray/slide/plotter solids at extensions **0, 130, 180, 250 mm**. Remove the `include_door_struts = extension<=0` omission once clear; if struts still collide after honest attempts, document remaining conflict — do not re-omit as a "pass".
3. **Tests:** invert `test_open_door_extended_tray_collision_not_exempt` for lower service/quick-access to expect **zero** door↔slide volumetric violations once fixed. Update `service_plotter_2` expectations for `upper_extension=0` (door open, no upper travel). Sample-sweep test for lower door clearance at 0/130/180/250.
4. Update `docs/14` §9 (strut omission policy obsolete if fixed); §Q close only if AC-4 met across samples, else keep OPEN with options.
5. Bump `CONCEPT_REVISION` 14→15; run `uv run python scripts/regenerate.py` (via `uv run`).

### C. If intractable

Do not fake green. Keep §Q OPEN with: part IDs, intersection volumes, extension values, and 2–3 concrete redesign options (e.g. hinge axis raise, telescoping/folding door, side-mounted struts outside footprint, different slide Z pack).

## Review / verify

- Adversarial review mandatory (overlay).
- Verifier runs Quick then Full; no product edits.
- Max 3 review/fix cycles; cycle 3 blocker-only.
