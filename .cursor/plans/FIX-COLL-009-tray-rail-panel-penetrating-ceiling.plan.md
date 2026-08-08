```yaml
contract_id: FIX-COLL-009-tray-rail-panel-penetrating-ceiling
tier: T2
cycle: 1
decision_id: D-094
requirement: SWE-003
sol_approved: null
status: cycle_1_closed_pending_Main_Full_land
live_max_mm3: 10237.5
ceiling_mm3: 15000.0
adversarial: accept
verifier_quick: pass
steps:
  - id: S-0
    action: Re-measure live transport FRAME-RAIL-TRAY- ↔ PANEL-IN- inter_vol; lock ceiling 15000 if max≈10237.5 else adjust
    owner: implementer
    status: done
  - id: S-1
    action: Add TRAY_RAIL_PANEL_PENETRATING_MAX_BEARING_MM3=15000 + TRAY_RAIL_PANEL_PENETRATING_PATTERNS; gate after POST branch
    owner: implementer
    status: done
  - id: S-2
    action: Exclude TRAY patterns from PANEL-IN-/FRAME- share_face (union ORG∪POST∪TRAY; keep ORG/POST)
    owner: implementer
    status: done
  - id: S-3
    action: Mirror D-093 tests — live mate, volumetric burial, coplanar share_face burial; keep ORG/MID/POST/OPEN_FRONT untouched
    owner: implementer
    status: done
  - id: S-4
    action: docs/14 + D-094 + state; note residual INTERLOCK/MAINS/COVER/SOFT P2; no G-pass
    owner: implementer
    status: done
  - id: S-5
    action: Targeted pytest/ruff; adversarial review; Quick verifier
    owner: adversarial-reviewer|verifier
    status: done
```

## Design (mirror D-093) — closed cycle 1

### Problem
`("FRAME-RAIL-TRAY-", "PANEL-IN-")` uncapped penetrating + share_face ORG∪POST-only exclude.

### Done
1. Live max **10237.5** mm³ (`FRAME-RAIL-TRAY-LOWER-L/R-001` ↔ `PANEL-IN-BOTTOM-001`).
2. `TRAY_RAIL_PANEL_PENETRATING_MAX_BEARING_MM3 = 15000.0`.
3. Patterns + gate after POST; share_face exclude ORG∪POST∪TRAY.
4. Three regression tests; docs/14 + D-094; residual INTERLOCK/MAINS/COVER/SOFT noted.
5. Adversarial **accept**; Quick **pass** (419 passed, 1 xfailed + ruff 0).

### NO-GO (held)
- Global penetrating ceiling; ORG/MID/POST/OPEN_FRONT constant edits; Path A; commit; G-pass.
