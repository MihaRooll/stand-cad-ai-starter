# FIX-COLL-001 — open-front intersection-volume ceiling

```yaml
contract_id: FIX-COLL-001-open-front-ceiling
tier: T2
cycle: 1
sol_approved: null
steps:
  - id: S-1
    action: Measure live transport/service/tray1_qa open_front + front penetrating inter_vol; record calibration
    owner: operational-orchestrator
  - id: S-2
    action: Add OPEN_FRONT_MAX_BEARING_MM3; gate is_open_front_kinematic_contact; upper-bound front clad/rail PENETRATING patterns
    owner: implementer
  - id: S-3
    action: Failing-first synthetic burial test FRAME-RAIL-BASE-FRONT ↔ EQUIP-PLOTTER1; assert not is_mating
    owner: implementer
  - id: S-4
    action: Docs § open-front ceiling; D-080; AUTONOMOUS_STATUS backlog #1; SWE-003 note; P2 door SOFTSTOP/MID backlog
    owner: implementer
  - id: S-5
    action: Mandatory adversarial-reviewer then Quick verifier
    owner: adversarial-reviewer|verifier
```

## Calibration (measured 2026-08-08, HEAD f144938+)

`tolerance.part_assembly_feature_mm` = **0.5**. Assemblies: `build_transport_assembly`, `build_service_plotter_1_assembly`, `build_tray1_quick_access_assembly`.

### Live open-front pairs (clearance < thr)

| Mode | Max `inter_vol` (mm³) | Dominant pairs |
|---|---|---|
| transport | **540.000** | `PANEL-CLAD-FRONT-TRAY-*-*` ↔ `SLIDE-*-*` (also 495 ↔ `TRAY-*`; rail/equip plane contacts 0) |
| service_p1 | **540.000** | upper clad ↔ slide/tray only (lower stack extended away) |
| tray1_qa | **540.000** | same band as transport |

Legitimate skin/plane bearing band: **0 … 540 mm³**. Synthetic burial target from C1: **~1e6 mm³**.

### Front penetrating patterns (AC-3)

Patterns that can exempt before `is_open_front_kinematic_contact` runs:

- `PANEL-CLAD-FRONT-` ↔ `TRAY-LOWER-` / `SLIDE-LOWER-` — live max **540** (same band)
- `FRAME-RAIL-BASE-FRONT-` ↔ `TRAY-LOWER-` / `SLIDE-LOWER-` — live **0** (plane; current code requires `inter_vol > threshold`, so these already fall through to open_front)

Other penetrating pairs reach **~31 500 mm³** (`FRAME-RAIL-ORG-REAR` ↔ `PANEL-IN-REAR`) — **do not** apply a global penetrating ceiling.

### Test-pair isolation (AC-2)

Live `FRAME-RAIL-BASE-FRONT-001` ↔ `EQUIP-PLOTTER1-001`: clearance **6.0 mm**, `inter_vol` **0**, `of=False`, `pen=False`. Synthetic burial of this pair hits **only** `is_open_front_kinematic_contact` (EQUIP not in front penetrating patterns).

### P2 door SOFTSTOP / PANEL-IN-MID (AC-5)

No clearance < thr door↔SOFTSTOP / door↔PANEL-IN-MID contacts in transport / service_p1 / tray1_qa — **no measured evidence** for a live ceiling. Leave as explicit backlog; do not invent a cap this cycle.

## Chosen constant

`OPEN_FRONT_MAX_BEARING_MM3 = 750.0`

- Floor: live max **540** + thr **0.5**
- Headroom: ~39% above max live skin contact (same honesty pattern as `DOOR_FRONT_PLANE_MAX_BEARING_MM3=500` with modest margin; far below ~1e6 burial)
- Reuse for front clad/rail penetrating upper bound only

## Implementation sketch

1. `collision.py`: define `OPEN_FRONT_MAX_BEARING_MM3 = 750.0` near door constants.
2. `is_open_front_kinematic_contact`: on clearance < thr, compute `inter_vol`; return `inter_vol <= OPEN_FRONT_MAX_BEARING_MM3 + threshold` (keeps 0…540; rejects burial).
3. `is_penetrating_structural_joint`: when matched pattern is one of the four front clad/rail↔tray/slide patterns and `inter_vol > OPEN_FRONT_MAX_BEARING_MM3 + threshold`, do **not** return True (continue). Other patterns unchanged.
4. Test `test_open_front_kinematic_contact_rejects_volumetric_burial`: mirror `test_door_mate_rejects_volumetric_burial` — bury rail into plotter bbox (+Y or equivalent); assert `inter_vol > ceiling`, `not is_open_front_kinematic_contact`, `not is_mating`.
5. Optional tight unit assert: live transport clad↔slide still `is_open_front_kinematic_contact` True with `inter_vol <= ceiling` (may already be covered by `check_collision_pairs` green).
6. `docs/14` short § after door section: open-front ceiling + measured 540 → 750.
7. State: D-080, close/narrow backlog #1, SWE-003 note; **no G-pass**.

## Forbidden

- Invent clearance gaps in geometry
- Raise ceiling to keep suite green without measurement
- Cap non-front penetrating patterns globally
- Claim physical clearances / gates passed
- Commit/push; touch `ИИ советы/`

## Verify (implementer targeted; verifier Quick)

```
uv run pytest tests/test_geometry.py -k "open_front or door_mate or cavity_joint or collision" --tb=short -q
uv run pytest tests/test_kinematics.py -k "collision" --tb=short -q
uv run ruff check src/stand_cad/geometry/collision.py tests/test_geometry.py
uv run pytest -q --tb=line
uv run ruff check .
```
