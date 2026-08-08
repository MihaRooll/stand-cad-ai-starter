```yaml
contract_id: FIX-COLL-008-post-panel-penetrating-ceiling
tier: T2
cycle: 1
decision_id: D-093
requirement: SWE-003
sol_approved: null
status: cycle_1_closed_pending_Main_Full_land
live_max_mm3: 18652.9
ceiling_mm3: 25000.0
adversarial: accept
verifier_quick: pass
steps:
  - id: S-0
    action: Re-measure live transport FRAME-POST- ↔ PANEL-IN- inter_vol; lock ceiling 25000 if max≈18653
    owner: operational-orchestrator
    status: done
  - id: S-1
    action: Add POST_PANEL_PENETRATING_MAX_BEARING_MM3=25000 + POST_PANEL_PENETRATING_PATTERNS; gate in is_penetrating_structural_joint after ORG/MID branches
    owner: implementer
    status: done
  - id: S-2
    action: Exclude POST patterns from PANEL-IN-/FRAME- share_face (add to ORG exclude; do not replace ORG)
    owner: implementer
    status: done
  - id: S-3
    action: Mirror D-092 tests — live mate, volumetric burial, coplanar share_face burial; keep ORG/MID/OPEN_FRONT untouched
    owner: implementer
    status: done
  - id: S-4
    action: docs/14 + D-093 + state; note TRAY-rail residual P2; no G-pass
    owner: implementer
    status: done
  - id: S-5
    action: Targeted pytest/ruff; adversarial review; Quick verifier
    owner: adversarial-reviewer|verifier
    status: done
```

## Design (mirror D-092 cycle 2)

### Problem
`("FRAME-POST-", "PANEL-IN-")` is in `PENETRATING_JOINT_PATTERNS` with no volume ceiling — any `inter_vol > thr` mates. Coplanar burial still hits unconditional `PANEL-IN-`/`FRAME-` `_share_face_if_prefix` (only ORG-REAR excluded).

### GO
1. `POST_PANEL_PENETRATING_MAX_BEARING_MM3 = 25000.0` (live max ~18652.9 + margin).
2. `POST_PANEL_PENETRATING_PATTERNS = {("FRAME-POST-", "PANEL-IN-")}`.
3. In `is_penetrating_structural_joint`: elif branch like ORG/MID — reject when `inter_vol > ceiling + thr`.
4. In `is_mating` PANEL-IN-/FRAME- share_face: exclude if matches ORG **or** POST patterns (union; keep ORG).
5. Tests mirror `test_org_rear_*` three cases for a representative POST↔PANEL-IN pair (pick the live max pair).
6. Docs/state: D-093; residual TRAY-rail↔PANEL ~10k P2; ORG/MID/OPEN_FRONT constants unchanged.

### NO-GO
- Global penetrating ceiling
- Change ORG_REAR / MID_UPPER / OPEN_FRONT constants
- Geometry Path A
- Commit/push / G-pass claim
