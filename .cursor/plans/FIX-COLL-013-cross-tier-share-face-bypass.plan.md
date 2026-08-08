```yaml
contract_id: FIX-COLL-013-cross-tier-share-face-bypass
cycle: 1
tier: T2
requirement: SWE-003
related: PLT-009
decision_id: D-098
sol_approved: null
status: cycle_1_closed_pending_main
adversarial: accept
verifier_quick: pass
verifier_quick_summary: "432 passed, 1 xfailed; ruff clean"
docs_rework:
  f1_project_state_residual_wording: closed
  n1_autonomous_status_test_count: closed
  n2_upper_lower_burial_pin: skipped
c1_confirm:
  helper: src/stand_cad/geometry/collision.py::_share_face_if_prefix ~326
  uncapped_call_sites: >
    is_mating() TRAY-/FRAME-RAIL-TRAY and SLIDE-/FRAME-RAIL-TRAY
    _share_face_if_prefix (~1055-1058) return True before
    is_staggered_tier_y_overlap (~1121)
  bypass_demo_transport: >
    TRAY-LOWER-001 ↔ synthetically buried FRAME-RAIL-TRAY-UPPER-L-001
    inter_vol≈1222650 mm³, aabb_share_face True, staggered False (D-097),
    is_mating True via share_face short-circuit; same for SLIDE-LOWER-LEFT
    (vol≈105300 mm³)
measured_live_mm3:
  transport_cross_tier_tray_slide_opposite_rail_share_face_max: 0.0
  service_p1_cross_tier_tray_slide_opposite_rail_share_face_max: 0.0
  service_p2_cross_tier_tray_slide_opposite_rail_share_face_max: 0.0
  transport_same_tier_slide_rail_mating_pairs_max: 0.0
  note: >
    Live cross-tier TRAY/SLIDE ↔ opposite FRAME-RAIL-TRAY currently have
    zero share_face contacts and zero intersection volume; same-tier
    SLIDE↔rail mates via MATING_PAIRS (vol≈0). Same-tier TRAY↔rail have
    ~12 mm clearance and are not mates. Ceiling 500 mm³ hygiene (reuse
    STAGGERED_TIER_MAX_BEARING_MM3) is appropriate — do not Path A.
chosen_fix: >
  Exclude cross-tier TRAY-/SLIDE- ↔ opposite-tier FRAME-RAIL-TRAY-* from
  uncapped _share_face_if_prefix short-circuit so pairs fall through to
  is_staggered_tier_y_overlap (already volume-gated at 500 mm³, D-097).
  Same-tier share_face path unchanged. No new global ceiling constant
  required if exclude is complete; document D-098 + reuse of staggered
  ceiling. Alternative acceptable: volume-gate share_face with 500 mm³
  for those prefixes — prefer exclude so staggered remains single oracle
  for cross-tier.
ceilings_mm3:
  STAGGERED_TIER_MAX_BEARING_MM3: 500.0
  reuse: true
residual_p2_out_of_scope:
  - INTERLOCK-TAB↔PANEL-IN / BASE-REAR↔MAINS uncapped MATING_PAIRS
  - Other uncapped share_face / MATING_PAIRS (SOFT↔TRAY, shelf/org, media, …)
notes: >
  No Path A geometry; no INTERLOCK/MAINS restore; no G-pass; no §F/§M/§N/§A
  closure. Main runs Full before land. Adversarial cycle 1 accept (no blockers).
  Docs rework: F-1 PROJECT_STATE residual wording + N-1 test-count nit closed.
steps:
  - id: S-1
    action: >
      Confirm C1 + re-measure live transport/service_p1/service_p2 max
      inter_vol for TRAY-/SLIDE- ↔ FRAME-RAIL-TRAY pairs that currently
      mate via share_face (not staggered). Record measured max; lock
      fix strategy (exclude cross-tier from uncapped share_face → staggered
      gate; ceiling 500 if vol≈0).
    owner: operational-orchestrator
    status: done
  - id: S-2
    action: >
      In collision.py is_mating(): for TRAY-/FRAME-RAIL-TRAY and
      SLIDE-/FRAME-RAIL-TRAY share_face branches, skip (do not return True)
      when the pair is cross-tier (LOWER tray/slide ↔ UPPER rail or
      UPPER tray/slide ↔ LOWER rail). Reuse existing tier markers /
      helper consistent with is_staggered_tier_y_overlap. Same-tier
      share_face remains uncapped. Do not touch INTERLOCK/MAINS,
      open-front, penetrating, Path A geometry, or unrelated ceilings.
    owner: implementer
    status: done
  - id: S-3
    action: >
      Regression tests in test_geometry.py: (1) synthetic cross-tier
      TRAY or SLIDE burial into opposite-tier FRAME-RAIL-TRAY with
      aabb_share_face True and inter_vol ≫ 500 ⇒ is_mating False
      (staggered also False). (2) Live same-tier SLIDE↔FRAME-RAIL-TRAY
      MATING_PAIRS still mate. (3) Live cross-tier plane-touch via
      staggered (e.g. TRAY-LOWER ↔ FRAME-RAIL-TRAY-UPPER or equip pair)
      still mates. Mirror FIX-COLL-012 burial test shape.
    owner: implementer
    status: done
  - id: S-4
    action: >
      docs/14 §11 note for cross-tier tray/slide↔rail share_face exclude
      (D-098); D-098 in DECISION_LOG; PROJECT_STATE + AUTONOMOUS_STATUS.
      Update this plan measured_live + status. No G-pass; no §F/§M/§N/§A.
    owner: implementer
    status: done
  - id: S-5
    action: Targeted verify on owned paths, then hand off for adversarial + Quick.
    owner: implementer
    status: done
  - id: S-6
    action: Mandatory adversarial review of cycle-1 diff vs AC-1..AC-6.
    owner: adversarial-reviewer
    status: done
  - id: S-6b
    action: >
      Docs rework post-adversarial: F-1 PROJECT_STATE residual wording
      (share_face F-1 only, not INTERLOCK/MAINS); N-1 AUTONOMOUS_STATUS
      test-count nit. N-2 UPPER↔LOWER burial pin optional/skipped.
    owner: implementer
    status: done
  - id: S-7
    action: Quick verify — uv run pytest + uv run ruff check .
    owner: verifier
    status: done
    verdict: pass
    summary: "432 passed, 1 xfailed; ruff All checks passed"
invariants:
  - No Path A geometry change
  - No G0–G8 pass
  - No restore INTERLOCK/MAINS/EDGEGUARD/AIRPATH solids
  - No global ceilings unrelated to this bypass
  - No commit/push
  - Bare python forbidden — uv run only
acceptance_criteria:
  - AC-1: cross-tier TRAY/SLIDE ↔ opposite FRAME-RAIL-TRAY cannot silent-green deep burial via share_face alone
  - AC-2: same-tier intentional tray↔rail / slide↔rail mates still pass (live)
  - AC-3: synthetic cross-tier burial ≫ ceiling → not mating / clearance would fire
  - AC-4: docs/14 + D-098 + PROJECT_STATE + AUTONOMOUS_STATUS + this plan
  - AC-5: adversarial accept; Quick pytest + ruff green
  - AC-6: no Path A; no G-pass; no §F/§M/§N/§A; no INTERLOCK restore
```
