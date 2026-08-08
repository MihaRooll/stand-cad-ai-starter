# FIX-WAVE-002 — D-056 regression close-out (T2)

```yaml
contract_id: FIX-WAVE-002-d056-regression-closeout
tier: T2
cycle: 2
goal: >
  Close the 8 unexpected D-056 pytest failures so that `uv run pytest -q`
  ends with exactly one permitted failure
  (test_lid_envelope_no_intersection_in_service_states) and ruff is clean;
  regenerate validation evidence; adversarial-review the collision-exemption fix.
acceptance_criteria:
  - id: AC-1
    text: >
      is_side_slab_frame_cavity_joint() returns True for the four
      FRAME-POST-{FL,FR,RL,RR}-001 ↔ PANEL-OUT-{LEFT,RIGHT}-001 pairs at
      0.000 mm clearance with measured inter_vol ≈47–48×10³ mm³; still rejects
      solid-acrylic burial magnitude (≥~50–85×10³ mm³ historical / far above
      _max_legitimate_skin_bearing_volume_mm3).
  - id: AC-2
    text: >
      test_numeric_collision_clearance passes for all 5 parametrizations
      (transport, service_plotter_1/2, operating_with_test_bodies, tray1_quick_access).
  - id: AC-3
    text: >
      test_idempotent_rebuild_matching_metrics passes — two successive
      build_transport_assembly() calls yield matching bbox/volume; root cause
      is shared PartRecord.solid instances across AssemblyState copies that
      break Compound bbox when both compounds exist.
  - id: AC-4
    text: >
      test_handle_tier2_finger_intrusion_at_balance_point updated to D-055
      measured values (balance ≈1,389,717 mm³; geom ≈987,525 mm³); remove
      stale assert intrusion < geom_intrusion (false after Y 165.7→187.6).
  - id: AC-5
    text: >
      After items 1–3 fixed, uv run python scripts/regenerate.py succeeds and
      test_validation_evidence_not_older_than_parameters passes.
  - id: AC-6
    text: >
      uv run pytest -q → exactly one failure (lid envelope); uv run ruff check .
      clean; Full profile setup_windows.ps1 exit 0; adversarial-reviewer
      APPROVED (or resolved rework) on collision predicate; D-057 written;
      PROJECT_STATE STOP block removed/rewritten.
owned_files:
  - src/stand_cad/geometry/collision.py
  - src/stand_cad/geometry/assembly.py
  - tests/test_geometry.py
  - state/DECISION_LOG.md
  - state/PROJECT_STATE.md
  - state/REQUIREMENTS_TRACEABILITY.csv
  - state/DEFERRED_VERIFICATION.md
  - docs/14_CAD_MODELING_CONVENTIONS.md
  - output/validation/rev12/   # via regenerate.py only
forbidden:
  - Do not touch lid/interlock geometry or silence test_lid_envelope_no_intersection_in_service_states
  - Do not blindly widen SIDE_SLAB_FRAME_MAX_INTERSECTION_MM3 / max_bearing ceilings without measured justification
  - Do not relax idempotent-rebuild tolerances without fixing shared-solid ownership
  - Do not mark any G0–G8 gate passed
  - No commit/push unless Main requests
sol_approved: null
steps:
  - id: S-1
    action: >
      Fix is_side_slab_frame_cavity_joint X-band check: require frame X
      overlap with wall pocket [0, side_clear] / [width-side_clear, width],
      not confinement of entire frame bbox inside side_clear. Measured root
      cause 2026-08-06: FRAME-POST-FL xmax=40.0 > side_clear+thr=20.5 →
      x_pass=False while z_ok=True, inter_vol=47830 < max_bearing=56175,
      clearance=0.000. Keep volume ceiling + clearance gate.
    owner: implementer
  - id: S-2
    action: >
      Fix assembly cache ownership: when serving from _STATIC_PARTS_CACHE /
      _STATE_CACHE, return PartRecords with copied solids (copy(solid) pattern
      already used by translate_solid) so two AssemblyState.compound() calls
      never share OCCT topology. Evidence: shared=True → c1 bbox (3,3,12)
      [=INTERLOCK-TAB size] vs c2 (650,420,544).
    owner: implementer
  - id: S-3
    action: >
      Update test_handle_tier2_finger_intrusion_at_balance_point expectations
      to D-055 numbers; drop stale intrusion < geom_intrusion.
    owner: implementer
  - id: S-4
    action: >
      Targeted pytest on the 8 failures + ruff; then regenerate.py once;
      then Quick full pytest -q confirming only lid failure.
    owner: implementer
  - id: S-5
    action: >
      Record D-057 (next after D-056) with measured before/after; rewrite
      PROJECT_STATE STOP block only after genuine single-failure pytest;
      update traceability/deferred if mapped.
    owner: implementer
  - id: S-6
    action: Adversarial review of collision-exemption predicate fix only.
    owner: adversarial-reviewer
  - id: S-7
    action: Verifier Quick then Full (setup_windows.ps1).
    owner: verifier
  - id: S-8
    action: >
      Cycle-2 rework from adversarial F-1/F-2: add Y-corner/return-band
      gate for FRAME-POST-* so mid-wall skin burial cannot exempt; add
      negative regression proving solid-fill / mid-wall burial rejected;
      correct comments/docs/D-057 burial band (~361×10³ solid-fill, not
      50–85×10³ overlapping max_bearing). F-3 nit optional.
    owner: implementer
    blocker_findings: [F-1, F-2]
```

## Stage close-out (2026-08-06)

- **S-6 (adversarial-reviewer, cycle 2):** **APPROVED** — F-1 Y-gate + F-2 solid-fill oracle closed; F-3 nit optional.
- **S-7 (verifier Full):** `ruff` clean; pytest **365 passed / 1 permitted failure** (lid envelope); `setup_windows.ps1` exit 0.
- **S-8 (implementer cycle-2 rework):** merged into D-057 evidence; state/docs close-out records FIX-WAVE-002 **closed**.

## Measured diagnostics (orchestrator, 2026-08-06, transport)

| Pair | frame X | inter_vol mm³ | max_bearing | clearance | rejecting branch |
|---|---|---|---|---|---|
| FL↔LEFT | (0, 40) | 47830.127 | 56175.000 | 0.000 | X: xmax>20.5 |
| RL↔LEFT | (0, 40) | 46798.188 | 56175.000 | 0.000 | X: xmax>20.5 |
| FR↔RIGHT | (610, 650) | 47830.127 | 56175.000 | 0.000 | X: xmin<629.5 |
| RR↔RIGHT | (610, 650) | 46798.188 | 56175.000 | 0.000 | X: xmin<629.5 |

Corner posts intentionally span pocket + inward leg (~40 mm). Predicate must test **overlap** with side slab X band.

Handle test failure: `assert 1389717.0 < 987525.0` — stale inequality after handle Y retune.

Idempotent failure: shared solids across Compounds → first bbox collapses to 3×3×12.

## Conventions note

`docs/14_CAD_MODELING_CONVENTIONS.md` has no prior rule for this cavity-wall bearing joint; implementer should add a short § documenting the overlap-not-confinement X check + measured volumes, and the assembly-cache solid-copy ownership rule.
