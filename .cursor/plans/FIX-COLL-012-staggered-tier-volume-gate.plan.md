```yaml
contract_id: FIX-COLL-012-staggered-tier-volume-gate
cycle: 1
tier: T2
requirement: SWE-003
related: PLT-009
decision_id: D-097
sol_approved: null
status: cycle_1_closed_pending_main
adversarial: accept
verifier_quick: pass
measured_live_mm3:
  transport_cross_tier_max: 0.0
  service_p1_cross_tier_max: 0.0
  service_p2_cross_tier_max: 0.0
  historical_burial_EQUIP-PLOTTER1_FRAME-RAIL-TRAY-UPPER: 43875
ceilings_mm3:
  STAGGERED_TIER_MAX_BEARING_MM3: 500.0
historical_burial_mm3: 43875
historical_pair: EQUIP-PLOTTER1 ↔ FRAME-RAIL-TRAY-UPPER
residual_p2:
  - F-1 should-fix: TRAY/SLIDE ↔ cross-tier FRAME-RAIL-TRAY still hit uncapped share_face before staggered gate
  - INTERLOCK-TAB↔PANEL-IN / BASE-REAR↔MAINS uncapped MATING_PAIRS (out of scope)
notes: >
  Live Z gaps clear (inter_vol≈0) via D-038/D-089; oracle still greened historical
  burial via Y-overlap-only heuristic. Locked 500 mm³ hygiene ceiling mirroring
  EQUIP_SEATING / TRAY_SLIDE / SLIDE_VIBMOUNT. Adversarial accept + Quick pass;
  Main runs Full before land.
steps:
  - id: S-1
    action: >
      Re-measure live transport (and service if staggered pairs contact) max
      intersection_volume among cross-tier pairs that currently hit
      is_staggered_tier_y_overlap (lower markers × upper markers with y_overlap
      > threshold). Record measured max; lock STAGGERED_TIER_MAX_BEARING_MM3
      (prefer 500.0 if live ≪500; raise only with measured evidence).
    owner: implementer
    status: done
  - id: S-2
    action: >
      Add STAGGERED_TIER_MAX_BEARING_MM3 near sibling bearing constants in
      collision.py. Change is_staggered_tier_y_overlap to require y_overlap >
      threshold AND intersection_volume <= ceiling + threshold. Keep marker
      lists and is_mating wiring (~1114) unchanged otherwise. Do not touch
      INTERLOCK/MAINS residual P2, open-front, penetrating, or Path A geometry.
    owner: implementer
    status: done
  - id: S-3
    action: >
      Regression tests — live staggered pairs with vol≈0 still mate / exempt;
      synthetic burial (e.g. EQUIP-PLOTTER1 into FRAME-RAIL-TRAY-UPPER-*) much
      greater than ceiling ⇒ is_staggered_tier_y_overlap False and is_mating
      False (or clearance would surface). Mirror equip_seating burial test shape.
    owner: implementer
    status: done
  - id: S-4
    action: >
      docs/14 §11 (or adjacent) note for staggered-tier volume gate; D-097 in
      DECISION_LOG; PROJECT_STATE + AUTONOMOUS_STATUS. Update this plan
      measured_live + ceilings + status. No G-pass; no §F/§M/§N/§A closure.
    owner: implementer
    status: done
  - id: S-5
    action: >
      Targeted verify on owned paths, then hand off for adversarial + Quick.
    owner: implementer
    status: done
  - id: S-6
    action: Mandatory adversarial review of cycle-1 diff vs AC-1..AC-6.
    owner: adversarial-reviewer
    status: done
    verdict: accept
  - id: S-7
    action: Quick verify — uv run pytest + uv run ruff check .
    owner: verifier
    status: done
    verdict: pass
invariants:
  - No Path A geometry change
  - No G0–G8 pass
  - No restore INTERLOCK/MAINS/EDGEGUARD/AIRPATH solids
  - No global penetrating ceiling
  - No commit/push
  - Bare python forbidden — uv run only
acceptance_criteria:
  - AC-1: staggered requires Y-overlap AND inter_vol <= ceiling + thr
  - AC-2: live transport/service staggered pairs vol≈0 still mate/exempt
  - AC-3: synthetic burial much greater than ceiling ⇒ is_mating False / clearance surfaces
  - AC-4: docs/14 + D-097 + state + this plan
  - AC-5: adversarial accept; Quick green
  - AC-6: no Path A; no G-pass; no §F/§M/§N/§A; no INTERLOCK restore
```
