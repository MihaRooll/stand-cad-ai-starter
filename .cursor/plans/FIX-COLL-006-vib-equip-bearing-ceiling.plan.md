# FIX-COLL-006-vib-equip-bearing-ceiling — Plan (T2)

**tier:** T2  
**contract_id:** FIX-COLL-006-vib-equip-bearing-ceiling  
**requirement:** SWE-003  
**decision_id:** D-091  
**HEAD base:** `5f53991`

## Goal

Close silent-green burial via uncapped VIB↔EQUIP `MATING_PAIRS` with a **pad-scale** bearing ceiling. Document as hygiene / D-087 residual-P2 closeout — **not** as a live beyond-pad burial fix.

## Live evidence (re-measured this session)

Transport assembly, eight `VIBMOUNT-P*` ↔ `EQUIP-PLOTTER*` pairs on `MATING_PAIRS`:

| Result | Value |
|---|---|
| pair count | 8 |
| every `inter_vol` | **2000.000 mm³** |
| vib pad size | 20×20×5 mm → 2000 mm³ full embed |
| beyond-pad live burial | **FALSE_ALARM** (C1) |

Ceiling seed: `VIB_EQUIP_MAX_BEARING_MM3 = 2500.0` (= 2000 + 500 margin).  
**NO-GO:** raise plotter on vib_h; ceiling from tray∩slide ~1e5 era.

## Design

Mirror `is_equip_seating_bearing` / `is_slide_vibmount_bearing`:

1. Constant `VIB_EQUIP_MAX_BEARING_MM3 = 2500.0` next to other bearing ceilings in `collision.py`.
2. `is_vib_equip_bearing_pair(a, b)` — tier-correct prefixes:
   - `VIBMOUNT-P1-` ↔ `EQUIP-PLOTTER1-`
   - `VIBMOUNT-P2-` ↔ `EQUIP-PLOTTER2-`
3. `is_vib_equip_bearing(a, b, parts, threshold)` — clearance ≥ threshold → False; else `inter_vol <= VIB_EQUIP_MAX_BEARING_MM3 + threshold`.
4. In `is_mating`, when `pair_key in MATING_PAIRS` and vib↔equip pair: require parts/threshold and call helper (same pattern as equip seating / tray↔slide). Do **not** leave uncapped `return True` for these pairs.
5. Update EQUIP_SEATING / docs comments that listed VIB↔EQUIP as uncapped residual P2.

## Tests (`tests/test_geometry.py`)

- Live exempt: all eight (or representative) live pairs `is_mating` True; `inter_vol <= 2500 + threshold` (expect ~2000).
- Burial reject: synthetic oversized vib / deep bury with `inter_vol ≫ 2500` → `not is_vib_equip_bearing` and `not is_mating`.

## Docs / state

- `docs/14_CAD_MODELING_CONVENTIONS.md` §11 pattern note: live exactly pad volume; hygiene ceiling 2500; no beyond-pad claim.
- `state/DECISION_LOG.md` D-091: honesty — live was exactly pad volume; fix is hygiene gate.
- `state/AUTONOMOUS_STATUS.md`, `state/PROJECT_STATE.md`: contract closed; no G-pass; no §F/§M/§N/§A close.

## Owned paths

- `src/stand_cad/geometry/collision.py`
- `tests/test_geometry.py`
- `docs/14_CAD_MODELING_CONVENTIONS.md`
- `state/DECISION_LOG.md`, `state/AUTONOMOUS_STATUS.md`, `state/PROJECT_STATE.md`

## Forbidden

- Commit/push; geometry Path A (raise plotter / vib height / envelope); ceiling ≥ tray∩slide volumes; claiming live deep burial; bare `python`.

## Verify (implementer targeted)

```
uv run pytest tests/test_geometry.py -q --tb=line -k "vib or equip or mating or burial or seating or tray_slide"
uv run ruff check src/stand_cad/geometry/collision.py tests/test_geometry.py
```

Verifier Quick: `uv run pytest` + `uv run ruff check .`

## Acceptance

| ID | Criterion |
|---|---|
| AC-1 | VIB↔EQUIP volume-gated; live 2000 mates |
| AC-2 | Synthetic ≫ ceiling ⇒ not mating |
| AC-3 | Tests + docs/14 pattern |
| AC-4 | D-091 honesty (pad volume / hygiene) |
| AC-5 | adversarial accept; Quick green; no G-pass |

## Cycle 1 outcome (orchestrator)

- Live re-measure: max/min/unique **2000.0** mm³ (8/8) — ceiling **2500** locked.
- Implementer: done. Adversarial: **accept** (findings=[]). Verifier Quick: **pass** (pytest 408/1 xfailed, ruff 0).
- State Verify row synced. Terminal → Main handoff. No commit.
