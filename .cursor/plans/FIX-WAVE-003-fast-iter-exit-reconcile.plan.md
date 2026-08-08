# FIX-WAVE-003 — Fast-iteration exit reconcile (post D-065 visual wave)

```yaml
contract_id: FIX-WAVE-003-fast-iter-exit-reconcile
tier: T2
cycle: 2
# cycle-2 CLOSED: adversarial APPROVED; verifier pass (370 passed / 1 xfailed / Full 0)
# residual owner OPEN: docs/10 §Q door clearance, §R post-less, §M lid; R-016/R-017
goal: >
  Owner approved exit from the second fast-iteration / no-tests visual-design
  wave after D-065 ("Готово, можно запускать все что надо для тестов и
  проверок" — D-043-class exit, same pattern as D-060). Reconcile code,
  tests, collision/joint tables, decision log, risks, and evidence so Quick
  + Full pass cleanly (sole permitted failure remains
  test_lid_envelope_no_intersection_in_service_states if still sanctioned)
  without restoring owner-removed visual parts and without silently deciding
  structural/electrical blockers.
acceptance_criteria:
  - id: AC-1
    text: >
      Confirmed parameters unchanged from owner reverts: case.depth=420,
      trays.lower_extension=250, trays.upper_extension=250,
      media_path.slot_height_target=10, media_path.clear_height_min=10;
      apply_tray_extension still translates LOWER/UPPER_KINEMATIC_GROUP by
      dy=-extension_mm (not a no-op); build_interlock_parts returns [].
  - id: AC-2
    text: >
      Owner-removed parts stay removed (FRAME-POST-*, INTERLOCK-*, six
      service volumes, PANEL-CLAD-FRONT-BASE/ORG); obsolete tests/oracles
      updated or removed; real dependencies (joint schedule JT-FRAME-CORNER /
      JT-STACK-CAP-POST, orphan PANEL-CLAD-FRONT-POST-*, collision allowlists,
      part_trace) fixed or risk-flagged — not silently deleted assertions that
      masked nonsense mass/stability.
  - id: AC-3
    text: >
      New doors.py wired correctly: transport both closed; service_plotter_1
      lower open; service_plotter_2 upper open; tray1_quick_access sets
      door_state lower=open (no tray-through-closed-door); DOOR-* collision
      mating / clearance policy documented in code+tests; open-door vs 250 mm
      tray path either clears with measured evidence or is escalated to
      docs/10 + risk register (no silent pass).
  - id: AC-4
    text: >
      Evidence honesty: generate_mass_report.py / analysis.py still use
      unfiltered build_transport_assembly; export/render use
      build_transport_display_assembly; regression test locks the separation;
      case_only filter documented (DOOR-* currently excluded — confirm intent).
  - id: AC-5
    text: >
      Decision log D-066+ records items 1–9 from the contract (and any other
      undocumented change found); PROJECT_STATE, REQUIREMENTS_TRACEABILITY,
      DEFERRED_VERIFICATION, docs/10, docs/08 updated for corner-post load
      path + service-volume display removal + door clearance + interlock ops.
  - id: AC-6
    text: >
      CONCEPT_REVISION bumped if geometry-affecting fixes land; 
      scripts/regenerate.py succeeds; Quick (pytest+ruff) green except
      sanctioned lid failure; Full setup_windows.ps1 exit 0; adversarial
      APPROVED (or rework closed within 3 cycles). No G0–G8 pass claimed.
owned_files:
  - src/stand_cad/geometry/assembly.py
  - src/stand_cad/geometry/frame.py
  - src/stand_cad/geometry/kinematics.py
  - src/stand_cad/geometry/doors.py
  - src/stand_cad/geometry/services.py
  - src/stand_cad/geometry/collision.py
  - src/stand_cad/geometry/hardware.py
  - src/stand_cad/geometry/part_trace.py
  - src/stand_cad/geometry/analysis.py
  - src/stand_cad/geometry/export.py
  - config/parameters.yaml
  - scripts/generate_mass_report.py
  - scripts/generate_drawings.py
  - scripts/render_validation_views.py
  - scripts/_stage1_metrics.py
  - tests/test_geometry.py
  - tests/test_kinematics.py
  - tests/test_drawings.py
  - tests/conftest.py
  - state/DECISION_LOG.md
  - state/PROJECT_STATE.md
  - state/REQUIREMENTS_TRACEABILITY.csv
  - state/DEFERRED_VERIFICATION.md
  - state/ASSUMPTIONS.md
  - docs/10_USER_INPUT_REQUIRED.md
  - docs/08_RISK_REGISTER.md
  - docs/15_ASSEMBLY_INSTRUCTIONS.md
  - docs/14_CAD_MODELING_CONVENTIONS.md
  - HANDOFF_PROMPT.md
forbidden:
  - Do not restore FRAME-POST-*, INTERLOCK-*, MAINS-INLET/ADAPTER/CTRL/AIRPATH
    solids, or PANEL-CLAD-FRONT-BASE/ORG against owner visual decisions
  - Do not silence test_lid_envelope without owner decision (sanctioned open)
  - Do not invent structural adequacy of post-less corners — escalate to docs/10
  - Do not invent electrical/thermal budget to replace removed service volumes
  - Do not mark any G0–G8 gate passed or production-ready
  - Do not use bare python; never call scripts/verify-harness.ps1
  - No commit/push unless Main requests
sol_approved: null
steps:
  - id: S-0
    action: >
      Explore confirmed: params 420/250/250/10; posts/interlock/services
      return []; mass path unfiltered; doors untested with clearance risks;
      JT-FRAME-CORNER/JT-STACK-CAP-POST still count post mates; orphan
      PANEL-CLAD-FRONT-POST-* still emitted. Quick failure inventory captured
      before implementer write.
    owner: operational-orchestrator
  - id: S-1
    action: >
      Fix product debt tied to removals (not just tests): (a) joint schedule —
      JT-FRAME-CORNER / JT-STACK-CAP-POST instance counts and FOOT→post
      rivnut story must not invent mates to missing FRAME-POST-*; retarget to
      remaining hosts (rails/panels/caps) or zero/disable with documented
      owner-risk caveat; (b) drop or retarget orphan
      PANEL-CLAD-FRONT-POST-{FL,FR} if posts stay gone; (c) collision.py stale
      allowlists for posts/interlock/service cluster; (d) part_trace registry;
      (e) dead density keys in analysis if unused. Prefer minimal honest
      schedule over fake BOM counts.
    owner: implementer
  - id: S-2
    action: >
      Doors correctness: wire tray1_quick_access door_state lower=open;
      add DOOR-* collision mating / intentional-contact rules where
      plane-touch is legitimate; MEASURE open door + struts vs tray/slides/
      equip at 250 mm and closed door vs extended tray — if collisions are
      real, either fix strut/pivot geometry (bounded) or escalate to docs/10
      and skip asserting clearance (do not fake-green). Add focused tests for
      presence/state/bbox and display vs mass filter honesty.
    owner: implementer
  - id: S-3
    action: >
      Update/remove obsolete tests expecting FRAME-POST-*, INTERLOCK-*,
      MAINS-INLET-001, BASE/ORG cladding, film-notch-through-post, stack
      L-notch vs post probes — rewrite stack/foot tests against STACK-CAP +
      remaining structure; keep mass/stability assertions that iterate all
      parts (they should still be meaningful). Preserve sanctioned lid
      failure.
    owner: implementer
  - id: S-4
    action: >
      Decision log D-066 (exit fast-iter round-2), D-067 (interlock remove),
      D-068 (tray cladding widen), D-069 (BASE/ORG clad remove), D-070
      (corner posts remove + structural caveat), D-071 (service volume
      display remove + electrical/thermal still required), D-072 (display/
      case_only filters), D-073 (piano-hinge doors), D-074 (confirm depth/
      extension/media reverts). Update PROJECT_STATE, TRACEABILITY,
      DEFERRED_VERIFICATION, docs/08, docs/10, docs/15 as needed.
    owner: implementer
  - id: S-5
    action: >
      Bump CONCEPT_REVISION 13→14 if any geometry-affecting fix; run
      uv run python scripts/regenerate.py; Quick then Full.
    owner: implementer
  - id: S-6
    action: Mandatory adversarial-reviewer on structural/joint/door/test honesty.
    owner: adversarial-reviewer
  - id: S-7
    action: Independent verifier Quick+Full; cycle 2+ only on blockers.
    owner: verifier
```

## Classification notes (orchestrator)

- **Tier T2** (not T3): CONCEPT/REFERENCE_ONLY exports under `output/` remain release-blocked by REL-027; physical quantities (mass path, load-path via post removal, service volumes) trigger T2 floor + mandatory adversarial. No principal-arbiter. No gate pass.
- **Oracle:** weak for physical claims — green pytest ≠ structural adequacy of post-less corners.

## Scout findings (S-0) — disposition map

| Change | Disposition |
|---|---|
| `build_interlock_parts` → `[]` | update-test + **owner-risk** (dual-extend ops / R-002) |
| Tray front cladding spans rail+slide band | keep geometry; update bbox oracles if any |
| BASE/ORG cladding removed | update-test (D-026 partial supersession) |
| `build_frame_posts` → `[]` | update-test + **design-fix joints/STACK story** + **owner-risk** load path |
| Six service volumes removed | update-test + **owner-risk/docs** (R-005 / electrical-thermal still real; display-only removal) |
| Display / case_only filters | keep; add honesty regression test |
| `doors.py` new | design-fix wiring + collision; tests; **owner attention** if 250 mm path collides |
| depth/ext/media reverts | confirm-only (already match); decision-log row |
| Mass/CoM unfiltered | verified OK — do not break |

## Per-failure policy

1. **KeyError on removed part_id in tests** → update/remove test (owner decision) **unless** the same ID is still required by joint BOM / stack bearing logic → then design-fix or escalate.
2. **Mass/stability numeric nonsense** after removal → investigate; do not delete the assertion; fix sampling or document expected mass delta.
3. **Door/tray collision** → measure first; geometry fix if small; else docs/10 blocker.
4. **JT-* counts referencing posts** → must change product source (S-1), not only tests.

## Baseline Quick inventory (pre-fix, 2026-08-07)

- Ruff: 1 error — unused `build_transport_assembly` import in `export.py:18`.
- Pytest (deselect film-post flood): **~38 unique failing bases** + film-post KeyError flood + drawings setup ERROR cascade (`DOOR-LOWER-001` missing from `part_trace`).
- Confirmed root causes (not just stale asserts):
  - `PARAM-017` / handle CoM: config Y=185.9 vs live loaded CoM Y≈179.30 after mass removals.
  - `test_numeric_collision_clearance` / media sweep: closed `DOOR-*` at 0.000 mm vs trays/slides/equip/rails/clad (need mating rules and/or door geometry fix; escalate if open+250 mm still collides).
  - Drawings: `part_trace` KeyError `DOOR-LOWER-001`.
  - Tray clad height oracle: 30.0 vs expected 18.0±0.5 (widened strip).
  - Render: `aluminium_strut_hardware` unregistered.
  - Obsolete KeyError oracles: `FRAME-POST-*`, `INTERLOCK-*`, `MAINS-INLET-001`.

## Verification commands

```text
uv run ruff check .
uv run pytest -q --tb=line
uv run python scripts/regenerate.py
powershell -ExecutionPolicy Bypass -File .\scripts\setup_windows.ps1
```

## Open owner questions to escalate (not agent-decided)

1. Post-less corners: is rails+panels+brackets-only load path acceptable for weld-free prototype, or must vertical Al corners return?
2. STACK-CAP bearing without post L envelope — accept crush path through plate/rails only?
3. Interlock removal: operating rule "never dual-extend" only, or restore mechanical inhibit later?
4. Service volumes: confirm display-only hide vs "no electrical accommodation in cabinet"?
5. Door struts vs 250 mm tray: redesign kinematics or accept cosmetic-only open state?
