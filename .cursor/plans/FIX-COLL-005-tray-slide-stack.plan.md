```yaml
contract_id: FIX-COLL-005-tray-slide-stack
tier: T2
cycle: 1
requirement: SWE-003
decision_id: D-089
sol_approved: null
goal: Path A Z-stack — slide fully below tray; tight TRAY↔SLIDE bearing ceiling; no permanent ~1e5 allowlist
steps:
  - id: S-1
    action: Fix _slide_bounds — use tray_bounds[2] (true tray bottom) as slide top; slide Z = [z_tray_bottom - rail_h, z_tray_bottom]; rename unpack vars
    owner: implementer
  - id: S-2
    action: Fix _tray_frame_rail_bounds same Z anchor so rail stays under slide (z_base = z_tray_bottom - rail_h - profile); measure rail∩slide after move
    owner: implementer
  - id: S-3
    action: Update doors.py _open_door_settle_dz_mm — slide_bottom_z = datum_z - tray_thickness - slide_h (not datum_z - slide_h)
    owner: implementer
  - id: S-4
    action: Add is_tray_slide_bearing + TRAY_SLIDE_MAX_BEARING_MM3≈500; gate TRAY↔SLIDE in is_mating MATING_PAIRS branch (mirror EQUIP seating)
    owner: implementer
  - id: S-5
    action: Height-stack / CoM — if under-tray stack grows by tray_thickness, retune upper_z/case.height/handle per D-038/D-084 patterns; only if tests require
    owner: implementer
  - id: S-6
    action: Tests — failing-first synthetic burial; invert/remove test_tray_slide_mating_pair_stays_uncapped; live transport+service_p1 inter_vol≪96525; door settle/rail clearance
    owner: implementer
  - id: S-7
    action: docs/14 §11 tray↔slide pattern; D-089 + AUTONOMOUS_STATUS + PROJECT_STATE; no G-pass
    owner: implementer
  - id: S-8
    action: Targeted verify then adversarial-reviewer then Quick verifier
    owner: operational-orchestrator
acceptance_criteria:
  - AC-1: live TRAY↔SLIDE inter_vol ≪96525 (≈0/skin; residual ≤~500+thr)
  - AC-2: synthetic deep burial ⇒ not is_mating / in violations
  - AC-3: failing-first tests; uncapped test removed/inverted
  - AC-4: door settle + rail coupled; no new false collision reds; docs/14 if new pattern
  - AC-5: D-089 + status; adversarial accept; Quick green; tip/mass/handle note
  - AC-6: NOT G-pass; NOT permanent ceiling ≥96525 as sole fix
forbidden:
  - commit/push
  - permanent sole ceiling ≥96525 without Path A
  - invent slide notches
  - close §F/§M/§N/§A or G-pass
  - bare python
```

## Root cause (confirmed)

`_tray_bounds` returns `(…, z0=tray_bottom, …, z1=tray_top)`. `_slide_bounds` and `_tray_frame_rail_bounds` unpack `tray_bounds[5]` as `z_tray_bottom` — that is the **tray top**. Slide occupies `[tray_top − rail_h, tray_top]`, burying through full tray thickness (~11 mm) → live L/R ~96525 mm³. `is_mating` returns unconditional True for non-seating `MATING_PAIRS`, so burial silent-greens.

## Preferred path

Geometry first (Path A), then `TRAY_SLIDE_MAX_BEARING_MM3≈500` like D-086/D-087. Interim ~110k ceiling alone is NO-GO unless geometry blocked.

## Coupling notes

- Door settle currently assumes slide bottom at `datum_z − slide_h` (as if slide top = tray top). After Path A: slide bottom = `datum_z − tray_thickness − slide_h`.
- Frame rails already intended under slides; wrong Z anchor places them relative to tray top — fix together.
- Moving stack down by `tray_panel_thickness_mm` may hit tier-1 / tip / handle CoM — retune only with measured evidence.
