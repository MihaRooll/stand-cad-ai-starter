```yaml
contract_id: FIX-COLL-011-cover-svc-frame-ceiling
cycle: 1
tier: T2
requirement: SWE-003
decision_id: D-096
sol_approved: null
status: cycle_1_closed_pending_main
measured_live_mm3:
  COVER-SVC-001_FRAME-RAIL-BASE-REAR-001: 7350.0
  COVER-SVC-001_FRAME-POST-RL-001: 122.9474
  COVER-SVC-001_FRAME-POST-RR-001: 122.9474
ceilings_mm3:
  COVER_SVC_FRAME_BASE_MAX_BEARING_MM3: 10000.0
  COVER_SVC_FRAME_POST_MAX_BEARING_MM3: 500.0
adversarial: accept
verifier_quick: pass
steps:
  - id: S-1
    action: >
      Re-measure live transport intersection_volume for COVER-SVC-001 ↔
      FRAME-RAIL-BASE* (expect ~7350 mm³) and COVER-SVC-001 ↔ FRAME-POST-R*
      (expect ~123 mm³ share_face and/or penetrating). Lock ceilings after measure;
      do not overload COVER_SVC_PANEL_MAX_BEARING_MM3.
    owner: implementer
  - id: S-2
    action: >
      Add COVER_SVC_FRAME_BASE_MAX_BEARING_MM3=10000.0 and separate
      COVER_SVC_FRAME_POST_MAX_BEARING_MM3 (prefer tighter ~500 if live ≪10000
      after re-measure; 10000 also acceptable if it rejects burial). Helpers
      is_cover_svc_frame_base_* / is_cover_svc_frame_post_* mirroring D-095
      panel pattern. Replace uncapped share_face at collision.py ~1030–1032
      with volume-gated bearing returns. Gate uncapped PENETRATING_JOINT_PATTERNS
      COVER-SVC-001↔FRAME-POST-RL/RR in is_penetrating_structural_joint.
    owner: implementer
  - id: S-3
    action: >
      Regression tests — live mate passes for BASE and POST; synthetic burial
      ≫ ceiling rejects mating for both classes (share_face and penetrating
      paths as applicable). COVER_SVC_PANEL_* unchanged.
    owner: implementer
  - id: S-4
    action: >
      docs/14 §11 note for COVER↔FRAME BASE/POST ceilings; D-096 in
      DECISION_LOG; PROJECT_STATE + AUTONOMOUS_STATUS. No G-pass claim.
    owner: implementer
  - id: S-5
    action: >
      Targeted verify — pytest -k cover/burial/mating/base/post_panel + ruff
      on owned paths. Then adversarial-reviewer + Quick verifier.
    owner: implementer
  - id: S-6
    action: Mandatory adversarial review of cycle-1 diff vs AC-1..AC-5.
    owner: adversarial-reviewer
  - id: S-7
    action: Quick verify — uv run pytest + uv run ruff check .
    owner: verifier
invariants:
  - COVER_SVC_PANEL_MAX_BEARING_MM3 and its gates unchanged
  - No Path A geometry edits
  - No G0–G8 pass
  - No commit/push
  - Bare python forbidden — uv run only
acceptance_criteria:
  - AC-1: COVER↔FRAME-RAIL-BASE volume-gated; live ~7350 still mates
  - AC-2: COVER↔FRAME-POST-R* volume-gated (share_face and/or penetrating); live ~123 still mates
  - AC-3: Synthetic burial ≫ ceilings ⇒ not mating (both classes)
  - AC-4: COVER_SVC_PANEL_* unchanged; other pen/mating gates untouched
  - AC-5: docs/14 + D-096; adversarial accept; Quick green; no G-pass
```
