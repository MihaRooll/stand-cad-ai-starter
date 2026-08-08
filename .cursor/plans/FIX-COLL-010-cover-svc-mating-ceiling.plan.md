# Plan — FIX-COLL-010-cover-svc-mating-ceiling

```yaml
contract_id: FIX-COLL-010-cover-svc-mating-ceiling
tier: T2
cycle: 1
sol_approved: null
requirement: SWE-003
decision_id: D-095
steps:
  - id: S-1
    action: >
      Add COVER_SVC_PANEL_MAX_BEARING_MM3=10000.0; is_cover_svc_panel_pair /
      is_cover_svc_panel_bearing mirroring equip/vib seating. Gate MATING_PAIRS
      COVER↔PANEL (BOTTOM/OUT-REAR) with volume check — no fall-through True.
    owner: implementer
  - id: S-2
    action: >
      Volume-gate COVER-SVC-/PANEL- share_face path (or replace helper) so
      COVER↔PANEL-IN-REAR coplanar burial cannot bypass (~7901 live still mates).
      Do not gate COVER↔POST / COVER↔BASE-REAR this cycle (residual P2).
    owner: implementer
  - id: S-3
    action: >
      Tests — live COVER↔BOTTOM/OUT-REAR mate; synthetic volumetric burial ≫ceiling
      not mating; coplanar share_face COVER↔PANEL-IN-REAR burial ≫ceiling not mating.
      Re-measure live volumes before locking constant if drift.
    owner: implementer
  - id: S-4
    action: docs/14 + D-095; state AUTONOMOUS_STATUS + PROJECT_STATE; no G-pass.
    owner: implementer
  - id: S-5
    action: adversarial-reviewer mandatory; verifier Quick.
    owner: adversarial-reviewer|verifier
invariants:
  - No global mating ceiling; do not touch equip/vib/tray/post/org gates.
  - COVER↔POST ~123 and COVER↔BASE-REAR share_face ~7350 remain residual P2.
  - Bare python forbidden; use uv run.
verify_commands:
  - uv run pytest tests/test_geometry.py -q --tb=line -k "cover or mating or burial or seating or vib or tray_rail or post_panel"
  - uv run ruff check src/stand_cad/geometry/collision.py tests/test_geometry.py
  - Quick — uv run pytest && uv run ruff check .
```
