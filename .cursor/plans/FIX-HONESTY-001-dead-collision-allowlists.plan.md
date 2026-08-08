# FIX-HONESTY-001 — dead collision allowlists prune

```yaml
contract_id: FIX-HONESTY-001-dead-collision-allowlists
tier: T2
decision_id: D-099
req: SWE-003
cycle: 1
sol_approved: null
steps:
  - id: S-1
    action: Inventory dead vs live allowlist surfaces in collision.py (C1 confirm)
    owner: operational-orchestrator
  - id: S-2
    action: Prune dead INTERLOCK/MAINS/EDGEGUARD/REARSUPPORT/AIRPATH/ADAPTER/SVC-INSERT entries; keep live mates
    owner: implementer
  - id: S-3
    action: Add honesty regression pin — absent prefixes absent from MATING_PAIRS / key frozensets
    owner: implementer
  - id: S-4
    action: Sync docs/14 residual P2 + DECISION_LOG D-099 + PROJECT_STATE + AUTONOMOUS_STATUS
    owner: implementer
  - id: S-5
    action: Mandatory adversarial review (SWE-003 honesty; no restore; live mates intact)
    owner: adversarial-reviewer
  - id: S-6
    action: Quick verify — uv run pytest; uv run ruff check .
    owner: verifier
```

## Goal

Remove zombie collision allowlist / share_face / penetrating / kinematic markers for parts **not emitted** so residual P2 docs stop advertising INTERLOCK/MAINS as live uncapped classes. Honesty cleanup only — **not** a volume ceiling, **not** Path A, **not** geometry restore.

## Absent parts (authority)

| Prefix / ID | Removal decision | Evidence |
|---|---|---|
| `INTERLOCK-*` | Not emitted | D-067; `build_interlock_parts()` → `[]` |
| `MAINS-INLET-*` | Not emitted | D-071; `assert "MAINS-INLET-001" not in transport.parts` |
| `AIRPATH-*` | Not emitted | D-071 |
| `ADAPTER-P1-*` / adapters | Not emitted | D-071 |
| `EDGEGUARD-*` | Not emitted | D-046 |
| `REARSUPPORT-*` | Not emitted | D-046 |
| `SVC-INSERT-*` | Not emitted | D-046 |

Live service parts remain: `COVER-SVC-001`, `MEDIA-SUPPORT-L*`, cable/light/channel, panels, frame, trays, slides, vib, equip, softstop, shelves/org, doors.

## Inventory — prune surfaces (`collision.py`)

### Remove from `RAW_MATING_PAIRS` / derived `MATING_PAIRS`

- `("EQUIP-PLOTTER1-001", "INTERLOCK-SHUTTLE-001")`
- `("EQUIP-PLOTTER2-001", "INTERLOCK-SHUTTLE-001")`
- `("INTERLOCK-TAB-LOWER-001", "INTERLOCK-SHUTTLE-001")`
- `("INTERLOCK-TAB-UPPER-001", "INTERLOCK-SHUTTLE-001")`
- `("MAINS-INLET-001", "PANEL-IN-REAR-001")`
- `("MAINS-INLET-001", "PANEL-OUT-REAR-001")`
- `("MAINS-INLET-001", "PANEL-IN-BOTTOM-001")`

**Keep** all other rows (SOFT↔SKIP, tray/slide/equip/vib/shelf/media/cover/cable/light, etc.).

### `PENETRATING_JOINT_PATTERNS`

- Remove `("FRAME-RAIL-BASE-REAR-", "MAINS-INLET-")`
- Remove `("INTERLOCK-TAB-", "PANEL-IN-")`
- Keep live capped classes (POST, ORG-REAR, TRAY-rail, MID-UPPER, COVER-SVC↔POST, open-front).

### `REAR_BOTTOM_SERVICE_CLUSTER`

- Current: `{COVER-SVC-001, MAINS-INLET-001, AIRPATH-001, ADAPTER-P1-001}`
- After prune of absent IDs only `COVER-SVC-001` remains → cluster-pair branch never fires.
- **Prefer:** delete frozenset + cluster share_face branch (`is_mating` ~1113) + cluster short-circuit inside `is_service_volume_mount` (~351). COVER-SVC already has dedicated panel/base/post gates (D-095/D-096).

### `is_mating()` share_face / INTERLOCK blocks

- Remove entire `INTERLOCK-` channel block (~1062–1078)
- Remove dead prefix branches: `REARSUPPORT-*`, `EDGEGUARD-*`, `SVC-INSERT-*` (and REARSUPPORT↔EDGEGUARD), `MAINS-INLET-`↔`PANEL-`
- **Keep** live: `SVC-INSERT` removal means drop that branch; keep `MEDIA-SUPPORT` mates via `MATING_PAIRS` / other live paths; keep COVER-SVC gated paths; keep PANEL/FRAME/ORG/TRAY/SLIDE share_face that still match live IDs

### Open-front / staggered markers

- Remove `"INTERLOCK-TAB-LOWER-"` / `"INTERLOCK-TAB-UPPER-"` from `is_open_front_kinematic_contact` stack_prefixes
- Remove same from `is_staggered_tier_y_overlap` lower/upper markers
- Live stack markers unchanged

### `intentional_block_pair`

- Dead-only (shuttle absent). Prefer: body → `return False` with brief D-067 comment; drop unused `LOWER_KINEMATIC_GROUP` / `UPPER_KINEMATIC_GROUP` imports if no other use in this file. Keep call site in clearance sweep (harmless no-op) OR inline `False` — prefer keep stub function for API stability.

### Out of scope (do not expand)

- `kinematics.py` still lists `INTERLOCK-TAB-*` in kinematic groups and retains builder stubs — **not** owned; do not restore; optional follow-up honesty if Main opens a separate contract
- `MEDIA_SWEEP_SKIP_PREFIXES` listing absent prefixes is skip-list hygiene, not a mating allowlist — leave unless false advertising of live contact
- No Path A geometry; no G-pass; no §F/§M/§N/§A

## Tests (AC-3)

Add focused honesty pin in `tests/test_geometry.py`, e.g. `test_collision_allowlists_exclude_absent_part_prefixes`:

- Import `MATING_PAIRS`, `RAW_MATING_PAIRS` (or flatten), `PENETRATING_JOINT_PATTERNS`, and any remaining frozensets that previously held absent IDs
- Assert no pair/member contains prefixes: `INTERLOCK-`, `MAINS-INLET`, `EDGEGUARD-`, `REARSUPPORT-`, `AIRPATH-`, `SVC-INSERT-` (and `ADAPTER-P1` if still referenced)
- Do **not** require deleting historical comments in docs/tests that describe past removal

## Docs / state (AC-4)

- `docs/14` §10a residual uncapped penetrating: **remove** INTERLOCK-TAB↔PANEL-IN and FRAME-RAIL-BASE-REAR↔MAINS claims
- `docs/14` §11 residual uncapped MATING/share_face: drop INTERLOCK / mains from residual list; keep honest live P2 (SOFT↔TRAY, shelf/org, media as applicable)
- §11 kinematic prose: stop implying INTERLOCK face helpers as current mate path if removed
- `state/DECISION_LOG.md` → **D-099** Accepted
- `state/PROJECT_STATE.md` + `state/AUTONOMOUS_STATUS.md` — closed cycle note; next = owner blockers / residual live P2
- Optional `docs/10`: trim only if it falsely claims current uncapped **live** INTERLOCK/MAINS pairs — do not rewrite owner blockers

## Anti-false-conclusion

Pruning zombies ≠ physical clearance proof. Residual live uncapped P2 (e.g. SOFT↔TRAY) remains real honesty debt.

## Forbidden

Commit/push; restore solids; broad mating refactor; bare `python`; L2 spawn; `_v_*.txt`

## Verify

```
uv run pytest
uv run ruff check .
```

Main runs Full before land.
