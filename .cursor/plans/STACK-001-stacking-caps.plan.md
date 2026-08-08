# STACK-001 — Stacking interface caps (T2)

```yaml
contract_id: STACK-001
tier: T2
cycle: 2
sol_approved: null
status: ready_for_main_handoff
goal: >-
  Weld-free load-bearing stacking caps at four top corners so a second identical
  unit can rest without sliding; owner waives stacked tip-over risk; crushing/bearing
  must still be sanity-checked with real geometry numbers.
adversarial_verdict: approve  # cycle-2 rework verification; F-1..F-5 closed
verifier_verdict: pass  # Quick: ruff 0; pytest 376 passed / 1 sanctioned lid failure
```

## Process note (breadth vs rework — read first)

**Independent review passes for breadth** and **`MAX_REVIEW_CYCLES`-bounded rework depth per finding** are different, non-conflicting controls:

| Control | Meaning | Cap |
|---|---|---|
| Breadth passes | How many independent `adversarial-reviewer` looks at the stacking feature (or adjacent honesty) Main/orchestrator schedules for coverage | Contract-driven; this campaign requires **≥1** pass on the stacking interface |
| Rework depth | How many implementer→reviewer fix loops may chase the **same** finding set before `BLOCKED` | `MAX_REVIEW_CYCLES=3`; cycle 3 is **blocker-only** |

Scheduling more than one breadth pass does **not** reset or violate the rework cap. A single finding cannot be reworked past cycle 3 without human decision. Do **not** reject this plan for stating both.

Owner tip-over waiver applies **only** to stacked tip-over/lateral overturn of two stacked units — **not** to crushing/bearing failure of posts/caps.

## Pre-flight geometry (orchestrator-measured 2026-08-06)

Main's L-notch claim is directionally correct; foot-anchor detail corrected:

| Fact | Value | Source |
|---|---|---|
| `hardware.foot_diameter_mm` | 30 | `config/parameters.yaml` |
| Foot centres (`build_feet`) | FL `(15,15)`, FR `(635,15)`, RL `(15,405)`, RR `(635,405)` | inset = `diameter/2`, **not** `case.corner_radius` |
| `case.corner_radius` / post `inset` | 25 mm | used by `_corner_post_solid` L extent (`inset+profile`=40) |
| `materials.frame_profile_size_mm` | 15 | L leg thickness |
| `FRAME-POST-FL-001` bbox | XY `[0,40]×[0,40]`, Z `[9,529]` | built geometry |
| FL L solid | `leg_h`: X`[0,40]` Y`[0,15]`; `leg_v`: X`[0,15]` Y`[0,40]` | `frame.py::_corner_post_solid` |
| Point `(25,25)` in L solid? | **False** | arithmetic + confirmed |
| Foot disk over hollow (X>15∧Y>15) | **~22%** of sampled disk points | 69/317 grid samples |
| Lateral registration today | **None** | no boss/recess/lip |

So a stacked `FOOT-*` lands partly on Al angle edge and partly on open L-notch / thin outer skin — not a reliable bearing interface.

## Indicative stacked compressive load (hand-calc; not FEA)

Using D-062 numbers (empty structural **8.806 kg**; all-parts indicative **12.860 kg** including equipment):

- Upper-unit weight on lower: **≈12.86 kg** → **≈126 N** total (g=9.81).
- Per corner if equal share: **≈3.215 kg ≈ 31.5 N**.
- Angle section (D-063 formula): `(2×profile−wall)×wall = (30−1.5)×1.5 = **42.75 mm²**`.
- Mean compressive stress in angle: **31.5 / 42.75 ≈ 0.74 MPa**.
- Allowable aluminium compressive/bearing stress: **`to_measure`** (no certified alloy sourced) — even a conservative 20–40 MPa concept floor leaves large margin; flag if implementer finds a thinner bearing path (plate-to-angle contact area) that concentrates load.

## Design intent (implementer must realise + prove with geometry queries)

### Parts
- `STACK-CAP-{FL,FR,RL,RR}-001` — four aluminium stacking caps (IDs consistent with `FRAME-POST-*` corners).
- Optional: keep fasteners as catalogue mass via new joint type (no need for separate screw solids unless existing bracket pattern already does).

### Geometry (per corner, mirror to FR/RL/RR)
1. **Bearing plate** on case top (`z` from `case.height` upward by `stack_cap_thickness_mm`, new param under `hardware.*` or `stacking.*`):
   - XY footprint at least the post L envelope (**40×40 mm** at FL) **and** the full stacked-foot disk (**Ø30** centred on foot centre) so the L-notch is **solid-bridged**.
   - Prefer a filled square / plate (not another open L) so bearing under the foot is continuous aluminium.
2. **Lateral registration**: shallow cylindrical recess (or raised lip) sized to `hardware.foot_diameter_mm` with small clearance leaf (`stacking.foot_recess_clearance_mm`, concept `to_measure`, e.g. 0.5–1.0 mm diametral). Depth shallow (e.g. 2–3 mm) so feet seat positively without deep pockets that trap dirt. Recess centre = stacked foot centre = same XY as `FOOT-*` on the upper unit when cases are aligned.
3. **Fastening (weld-free, D-061 catalogue style)**:
   - New joint `JT-STACK-CAP-POST`: `STACK-CAP-*` ↔ `FRAME-POST-*`.
   - Method: M4 pan-head into M4 rivnuts in post top / top-rail legs (reuse `hardware.fastener_m4_*`); qty_per_joint ≥2 (two screws per cap into the two L legs — buildable edge distance on 15 mm leg: **one** fastener per leg, same D-063 lesson).
   - Do **not** invent a parallel fastener system.

### Integration
- Build in `hardware.py` (or small dedicated helper called from `hardware.py` / `frame.py` — prefer `hardware.py` next to feet) and wire via `assembly.py::_build_static_parts`.
- Real small mass in mass model (Al density path already used for brackets/frame).
- Collision: caps must not reopen PROD-001 exemptions; re-run collision-related tests. Caps sit **above** case top — expect no transport-state penetration into existing parts; if they mate flush on post tops, add a legitimate mating exemption only if zero-clearance contact is intentional and volume-bounded (prefer small gap / documented bearing contact pattern consistent with `docs/14_CAD_MODELING_CONVENTIONS.md`).

### Docs / state
- `docs/15_ASSEMBLY_INSTRUCTIONS.md` — install caps after top ring; stacking usage note; tip-over waiver explicit.
- `docs/12_PRODUCTION_RFQ_TEMPLATE.md` / BOM — add four caps + JT-STACK-CAP-POST if BOM lists joints/parts.
- `state/DECISION_LOG.md` → **D-064** (next after D-063) with measured point-containment, hollow fraction, bearing load, mass delta.
- `state/PROJECT_STATE.md` — short product-truth stacking note.
- README only if an obvious one-line product-truth slot exists; do not force.

### Tests (minimum)
1. **Bearing:** for each corner, stacked-foot footprint disk (or proxy solid) at case-top Z has **non-zero solid intersection / containment** with the matching `STACK-CAP-*` over the former L-notch region (e.g. probe at FL `(25,25)` or outer-quad samples that were hollow on the bare post).
2. **Registration:** recess/lip geometry present; diameter/clearance vs `FOOT-*` / `hardware.foot_diameter_mm` asserted within tolerance.
3. Existing collision / weld-free joint registry tests still green (extend registry test for `JT-STACK-CAP-POST`).

### Verification
- `uv run ruff check .`
- `uv run pytest -q` — only sanctioned failure: `test_lid_envelope_no_intersection_in_service_states` (≈210 600 mm³). Any other failure = regression to fix.
- Regenerating full rev14 evidence pack is **out of scope** unless implementer needs a mass number from live assembly; decision log may cite pytest/mass helper output. Do **not** bump `CONCEPT_REVISION` unless regenerating package is required for honesty — prefer leave rev13 and note stacking caps as post-rev13 working-tree geometry pending next regenerate (or bump if assembly mass tests force it). **Judgement:** if `CONCEPT_REVISION` / evidence-age tests fail after geometry change, bump revision and regenerate only as needed to keep suite green — keep CONCEPT/REFERENCE_ONLY naming.

## Forbidden
- Re-litigate PROD-001 joining catalogue / RFQ structure beyond integrating new stacking parts.
- Mark production-ready or pass G0–G8.
- Invent certified alloy allowables as verified.
- Solve stacked tip-over / add ballast for tip resistance.
- Parallel writers; reviewer/verifier edits.

## Steps

```yaml
steps:
  - id: S-1
    action: Persist this plan (done); no further explore scouts — geometry pre-flight complete
    owner: operational-orchestrator
  - id: S-2
    action: Implement STACK-CAP-* + JT-STACK-CAP-POST + tests + docs + D-064; ruff + pytest
    owner: implementer
  - id: S-3
    action: Independent adversarial review of stacking interface (bearing + registration + weld-free + load sanity)
    owner: adversarial-reviewer
  - id: S-4
    action: Independent verifier Quick profile (ruff + full pytest); confirm sanctioned lid failure only
    owner: verifier
  - id: S-5
    action: Compact handoff to Main with design numbers, pytest counts, review verdict, D-064
    owner: operational-orchestrator
```

## Acceptance criteria

- AC-1: Four `STACK-CAP-*` parts in assembly; solid bearing under stacked foot (geometry query evidence).
- AC-2: Positive lateral registration sized to `FOOT-*` / foot diameter.
- AC-3: Weld-free `JT-STACK-CAP-POST` in `joints.*` + registry; M4 catalogue reuse.
- AC-4: Crushing/bearing hand-calc logged with real section/load numbers; alloy allowable `to_measure`.
- AC-5: Docs 15 (+12/BOM as needed) + D-064 with real numbers.
- AC-6: ruff clean; pytest green except sanctioned lid-envelope failure; ≥1 new regression test covering AC-1 and AC-2.
- AC-7: Adversarial-reviewer verdict on stacking feature (approve, or rework within ≤3 cycles).

## Owned paths (implementer)

- `config/parameters.yaml`
- `src/stand_cad/parameters.py` (if validation/leaves needed)
- `src/stand_cad/geometry/hardware.py`
- `src/stand_cad/geometry/assembly.py`
- `src/stand_cad/geometry/analysis.py` and/or `collision.py` (only if mass/collision integration requires)
- `tests/test_geometry.py` (and/or new focused test module if cleaner)
- `docs/15_ASSEMBLY_INSTRUCTIONS.md`
- `docs/12_PRODUCTION_RFQ_TEMPLATE.md` (BOM/joint only as needed)
- `state/DECISION_LOG.md`, `state/PROJECT_STATE.md`
- `README.md` (optional one-line)
- `src/stand_cad/geometry/export.py` **only if** revision bump required for evidence-age tests

## Out of scope

- Tip-over redesign / ballast / depth change for stacked stability.
- Full PROD-001 RFQ redraw unless suite forces regenerate.
- Owner blockers §F/§N/§M/§A/§P.
