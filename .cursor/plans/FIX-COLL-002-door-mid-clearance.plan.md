# FIX-COLL-002 — door mid clearance (T2)

```yaml
contract_id: FIX-COLL-002-door-mid-clearance
cycle: 2
tier: T2
sol_approved: null
steps:
  - id: S-1
    action: Cap is_door_mate PANEL-IN-MID + SOFTSTOP* with DOOR_FRONT_PLANE_MAX_BEARING_MM3 (reject silent-green burial)
    owner: implementer
    status: done_cycle_1
  - id: S-2
    action: Path A geometry — retract PANEL-IN-MID front Y to closed-door inner face (tray front plane)
    owner: implementer
    status: done_cycle_1
  - id: S-6
    action: "F-1 blocker: retune hardware.handle_mount_y_mm to new loaded CoM Y after Path A (D-074 pattern); sync docs/10 §E if cited"
    owner: implementer
  - id: S-7
    action: "F-2 should-fix: AUTONOMOUS_STATUS verify snapshot must not claim 383 passed while Quick red"
    owner: implementer
  - id: S-8
    action: "F-3 nit (optional): open-posture synthetic MID/SOFTSTOP burial rejection test"
    owner: implementer
  - id: S-9
    action: Adversarial re-review then Quick verify (full pytest + ruff)
    owner: adversarial-reviewer|verifier
```

## Cycle-1 measured after (Path A landed)

| Pair | Before | After |
|---|---:|---:|
| DOOR-LOWER ↔ PANEL-IN-MID | 5985.0 | **0.0** (clr=0 plane touch) |
| MID Y front | 2.5 | **15.0** |

Adversarial cycle-1 verdict: **rework** (F-1 CoM/PARAM-017 blocker; F-2 status honesty; F-3 open-burial coverage nit).

## Measured baseline (transport, HEAD ce88037+)

| Pair | inter_vol mm³ | clr | notes |
|---|---:|---:|---|
| DOOR-LOWER-001 ↔ PANEL-IN-MID-001 | **5985.0** | 0 | overlap dX=570, dY=3, dZ=3.5 |
| DOOR-LOWER ↔ SOFTSTOP-* | 0 | ~190 | no contact; still needs volume predicate |
| DOOR-UPPER ↔ PANEL-IN-MID | 0 | — | must not regress |

Bboxes: DOOR-LOWER Y(12,15) Z(19,227); MID Y(2.5,417.5) Z(217.25,220.75).  
`is_door_mate` currently `return True` for MID and SOFTSTOP (silent-green). Ceiling `DOOR_FRONT_PLANE_MAX_BEARING_MM3 + thr` = **500.5**.

## Trim strategy choice

| Option | Change | Sim after | Correctness |
|---|---|---|---|
| **A (chosen)** | Retract MID `y0` 2.5 → **15.0** (door/tray front = closed-door inner face); ΔY=**12.5 mm** | vol=0, clr=0 (plane touch) | Inner divider no longer occupies door slab / protrudes past front plane |
| B | Shorten lower door `z_top` 227 → 217.25 (mid underside); ΔZ=**9.75 mm** | vol=0 | Aligns with doors.py comment “divider underside”, but leaves MID protruding Y∈[2.5,12] ahead of closed door |
| A+B | both | vol=0 | unnecessary if A alone clears |

**Decision:** Path **A only** — smallest *correct* single fix (B is shorter linearly but leaves incorrect mid protrusion through the door plane). Do **not** raise MID mate ceiling near 5985.

Implementation sketch (`panels.py::_build_inner_mid_panel`): set front Y from tray/door front plane (`datums.plotter1_physical.y.min_mm` / closed-door `y1`), not `gap`. Keep rear at `depth - gap`.

## Collision predicate (AC-1)

Same pattern as other closed front mates:

- `PANEL-IN-MID-001`: `inter_vol <= DOOR_FRONT_PLANE_MAX_BEARING_MM3 + threshold` when closed; open-door → `<= threshold` (match tray/slide front-mate posture split).
- `SOFTSTOP-*`: same ceiling (live vol=0; predicate honesty).
- Synthetic burial test must reject MID (and SOFTSTOP if practical) deep inter_vol.

## Expected after

- Live DOOR-LOWER ↔ MID: inter_vol **0** (or skin-only ≪ 500.5); `check_collision_pairs` transport/service green. **Implemented (D-084):** measured **5985 → 0 mm³**.
- Softstop predicate capped; live still vol=0.
- Upper door unchanged.
- D-084 records measured before/after; docs/14 closes P2 backlog note; no G0–G8 pass; no invented clearances beyond measured trim.

## Forbidden

- Ceiling ≈5985 greenwash
- Production-verified clearance claims
- Commit/push; touch `ИИ советы/`

## Cycle-2 closeout

| Finding | Severity | Status |
|---|---|---|
| F-1 CoM/PARAM-017 handle retune | blocker | closed (`handle_mount_y_mm=180.6`) |
| F-2 AUTONOMOUS_STATUS honesty | should-fix | closed |
| F-3 open-posture burial tests | nit | closed |
| F-4 sole-current HANDOFF/CSV/PROJECT_STATE Y=179.8 lag | should-fix | closed (180.6 / ≈1,515,402) |

Verifier Quick: pass (393 passed, 1 xfailed; live MID inter_vol=0; ceiling=500).
