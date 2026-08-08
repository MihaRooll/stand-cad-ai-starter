# Plan: PLT-004 fidelity cycle 2 — shell restructuring + handle root-cause fix

Tier: **T2** (Main's explicit ruling for this stage). Mandatory `adversarial-reviewer`, **no**
`principal-arbiter`. Sole writer: `implementer` (composer-2.5-fast). Review/verify on
`cursor-grok-4.5-high-fast`. Cap 3 internal review/verify cycles; cycle 3 is blocker-only; an open
blocker after cycle 3 is `BLOCKED`, reported honestly — never silently `done`.

Source of truth: `ИИ советы/Cursor_Opus5_TZ_Light_Plotter_Tower.md` ("TZ"),
`ИИ советы/ChatGPT Image 3 авг. 2026 г., 20_58_06.png` (owner reference photo),
`config/parameters.yaml`, `src/stand_cad/geometry/*`. 117 existing tests must keep passing unless a
specific, documented, honest correction requires a change (state it).

## 0. Orchestrator-established facts (do not re-derive, but the reviewer must re-check by render)

### Finding 1 root cause (established by direct diagnostic, not guesswork)

The handle cutout in `PANEL-OUT-LEFT/RIGHT-001` **is a genuine boolean through-cut**:
- Isolated diagnostic: cutting the 110×35 mm rounded through-hole alone removes ≈11 534 mm³ from a
  single connected solid (matches `110×35×3 mm` minus rounded corners almost exactly).
- `tests/test_geometry.py::test_handle_cutout_dimensions` already probes the exact cut centre and
  passes today — the cut genuinely exists.

It does not read as an opening in `output/validation/rev2/views/transport_left.png` /
`transport_right.png` because `hardware.handle_mount_z_mm` is `TO_MEASURE`, so the concept fallback
uses `_panel_shell_height/2 ≈ 336 mm` — a Z that lands almost exactly on the
`FRAME-RAIL-ORG-LEFT/RIGHT-001` band (335–350 mm) and `ORG-FLOOR-001`/`DIVIDER-000` (350 mm+), all
positioned at nearly the same X depth as the cut (frame rail X spans 0–15 mm, inside the panel's own
0–3 mm face). Looking through the hole reveals pale interior structure, not open background, so at
1280×960 the cutout reads as a faint tonal patch, not a visible hole. Verified reproducible from the
**current, unmodified** source (re-rendered independently outside `output/` and pixel-identical to
the committed rev2 PNG — this is not a stale-cache artifact).

**Separately found while diagnosing (must not recur in the new shell):** the existing R25
corner-relief cylinder cut on the 3 mm-thin `PANEL-OUT-LEFT/RIGHT-001` severs each side panel into 3
disconnected solids (front sliver / main body / rear sliver), because the relief radius (25 mm) is
much larger than the panel's own thickness (3 mm) at the cut location. Confirmed via
`len(solid.solids())`. This must be fixed as part of section 2's rebuild (2D profile fillet, not an
oversized boolean subtraction).

### Sync anomaly conclusion

No forensic evidence of a concurrent second writer was found:
- Only 4 commits exist in this repository total; none touch `config/parameters.yaml` or
  `src/stand_cad/geometry/**` — there is no committed snapshot to diff a "revert" against.
- `git status --porcelain` and a direct filesystem search show exactly **one**
  `config/parameters.yaml` (the earlier dual listing with a backslash path was a path-separator
  rendering duplicate of the same file, not two real files).
- Full `ls --full-time` timeline across every `src/stand_cad/**` and `config/*.yaml` file shows a
  single, monotonically increasing edit sequence with no out-of-order, duplicated, or lock-file
  artifacts consistent with two writers colliding.
- **Conclusion: cannot confirm a revert occurred, and cannot rule it out either** — the absence of
  any commit/backup checkpoint after "approval" means the claim is unfalsifiable from evidence alone.
  The real process defect is the absence of checkpointing, not a proven double-writer collision.
  Recommendation (record in `state/DECISION_LOG.md`): commit after every approved milestone so future
  revert questions are answerable from `git diff` instead of memory.

## Task Contract

```yaml
contract_id: PLT-004-fidelity-cycle2
tier: T2
goal: >
  Fix the handle visibility defect at its root cause, restructure the outer shell from a
  six-sided box with cutouts into two full-height rounded side slabs + open shelves + open
  top + closed rear panel per the owner's reference, close the Finding 4 bottom-ventilation
  deferral, confirm divider plate visibility, recompute mass/stability/deflection against the
  restructured geometry, and keep the viewer/tests/traceability consistent — all without moving
  any fixed TZ dimension.
acceptance_criteria:
  - id: AC-1
    text: >
      Root cause of Finding 1 is fixed, not just documented: after the rebuild, regenerated
      transport_left.png AND transport_right.png visibly show open daylight/background through
      each handle cutout (not a same-tone interior patch) — confirmed by the reviewer looking at
      the actual PNGs, plus a strengthened test that probes a grid across the full cutout
      footprint through the slab thickness and asserts no other registered part occupies that
      swept volume (not just the single centre point already covered by
      test_handle_cutout_dimensions).
  - id: AC-2
    text: >
      Side panels are rebuilt as full-height (Z 0 to case.height) slabs spanning the full
      (case.width - case.internal_width)/2 side clearance in X, each a single connected solid
      (len(solid.solids()) == 1), with a pronounced fillet/round on the front vertical edge and
      an attempted round on the top-front edge (graceful fallback on build123d fillet failure,
      same try/except discipline as the existing _try_top_edge_fillet). PANEL-OUT-CORNER-FL/FR/
      RL/RR-001 are removed as redundant once the slab itself provides the rounded corner, or
      their removal is explicitly justified if kept for the rear corners only.
  - id: AC-3
    text: >
      PANEL-OUT-FRONT-001 is removed entirely — both plotter shelf zones are fully open with no
      framing panel anywhere in that zone. RETAINER-001 / organizer front opening logic in
      dividers.py is confirmed unaffected (it does not depend on PANEL-OUT-FRONT-001).
  - id: AC-4
    text: >
      TOP-STRUCTURE-001 is removed as a visible lid surface (or reduced to a fully hidden
      internal tie that never appears as a rim/sheet in any render) — the organizer top reads as
      genuinely open in transport_top.png, transport_iso.png, and organizer_loaded_iso.png.
      organizer_clear_volume (610x510x325) is unchanged.
  - id: AC-5
    text: >
      PANEL-OUT-REAR-001 keeps its existing role unchanged (closed, two feed slots, rear vent
      slots) plus new bottom vent slots are added as real through-cuts on PANEL-IN-BOTTOM-001
      (the exposed base plate between the feet), closing the bottom half of assumption A-014 /
      decision D-016. No new to_measure numeric leaf is invented for slot shape — reuse the
      existing hardware.vent_slot_count/width/height/pitch leaves; only positioning is new and
      must be derived from existing datums (documented in the fix).
  - id: AC-6
    text: >
      Divider count/spacing is confirmed correct (state the formula and resulting count plainly)
      and a new higher-resolution close-up render of the organizer bay is added so a human can
      count the 2 mm divider plates by eye.
  - id: AC-7
    text: >
      output/validation/rev1/ and output/validation/rev2/ are left untouched on disk. A new
      output/validation/rev3/views/ (full 10 PNG + 5 SVG set plus the new organizer close-up) and
      output/concept/*_rev3.* (STEP/STL/GLB/manifest) exist, generated from the live rebuilt
      source via scripts/render_validation_views.py (local uv run path — no build123d-mcp).
  - id: AC-8
    text: >
      mass_report.csv, stability_report.md, deflection_report.md under
      output/validation/rev3/ are recomputed against the restructured geometry (not copied from
      rev1/rev2). Deflection keeps the already-corrected rail-to-rail beam model; if the honest
      result still exceeds trays.deflection_max_mm (1.5 mm), report it plainly — do not retune
      materials.tray_panel_youngs_modulus_mpa or any other input to force a pass.
  - id: AC-9
    text: >
      viewer/index.html points at the rev3 manifest; the part-visibility tree still groups
      correctly (verify against surviving part-id prefixes); viewer/README.md is updated if any
      prefix used by the "Outer panels off" toggle changed or disappeared (e.g. TOP-STRUCTURE-,
      PANEL-OUT-CORNER-).
  - id: AC-10
    text: >
      collision.py's part-id allowlists and assembly.py's _HIDDEN_OUTER_SHELL_PREFIXES /
      build_transport_shell_top_view_assembly are updated for every removed/renamed part id — no
      dangling references to parts that no longer exist.
  - id: AC-11
    text: >
      state/REQUIREMENTS_TRACEABILITY.csv, state/PROJECT_STATE.md, state/ASSUMPTIONS.md, and
      state/DECISION_LOG.md are updated: A-014 bottom-ventilation half closed, D-016 updated, new
      rev3 entry in PROJECT_STATE, and the sync-anomaly conclusion from section 0 recorded as a
      new decision-log row.
  - id: AC-12
    text: uv run pytest exits 0; uv run ruff check . exits 0; full setup_windows.ps1 exits 0.
owned_files:
  - src/stand_cad/geometry/panels.py
  - src/stand_cad/geometry/frame.py
  - src/stand_cad/geometry/hardware.py
  - src/stand_cad/geometry/services.py
  - src/stand_cad/geometry/assembly.py
  - src/stand_cad/geometry/collision.py
  - src/stand_cad/geometry/analysis.py
  - src/stand_cad/geometry/export.py
  - src/stand_cad/geometry/primitives.py
  - scripts/render_validation_views.py
  - scripts/generate_mass_report.py
  - scripts/generate_model.py
  - tests/test_geometry.py
  - tests/test_kinematics.py
  - viewer/index.html
  - viewer/README.md
  - state/REQUIREMENTS_TRACEABILITY.csv
  - state/PROJECT_STATE.md
  - state/ASSUMPTIONS.md
  - state/DECISION_LOG.md
  - docs/10_USER_INPUT_REQUIRED.md
  - output/validation/rev3/**
  - output/concept/*_rev3.*
verify_commands:
  - uv run pytest
  - uv run ruff check .
  - powershell -ExecutionPolicy Bypass -File .\scripts\setup_windows.ps1
forbidden:
  - No change to any fixed TZ dimension: 650x550x690 overall envelope, case.internal_width (610),
    plotter physical/design envelopes and coordinates, the 150 mm setback, organizer 610x510x325
    clear volume, cell formula, tray extensions, feed-plane provisional values.
  - No new invented numeric parameter. Any new leaf must be `derived` from existing fixed data
    (formula stated) or reuse an existing `to_measure` leaf with a stated rationale for reuse.
  - No PDF or DXF generation. No gate marked passed; no PROTOTYPE_RELEASED/SERIES_RELEASED
    anywhere. No git push.
  - Do not touch output/validation/rev1/** or output/validation/rev2/** — they remain reproducible
    "before" evidence for this cycle's findings.
  - Do not silently retune materials.tray_panel_youngs_modulus_mpa or any other assumed input to
    make deflection pass.
```

## 1. Architecture for the restructured shell (Finding 2)

Case datums are unchanged (`case.width=650`, `case.depth=550`, `case.height=690`,
`case.internal_width=610`, `case.corner_radius=25`). Side clearance
`side_clear = (case.width - case.internal_width)/2 = 20 mm` (derived, already computable from
existing fixed leaves).

**Side slabs (`PANEL-OUT-LEFT-001` / `PANEL-OUT-RIGHT-001`, material unchanged
`cast_opal_pmma_3mm` even though the footprint is no longer literally 3 mm thick — rename the
material constant/comment if that becomes confusing, but do not invent a new material leaf):**

- X range: `[0, side_clear]` (left) / `[width - side_clear, width]` (right).
- Y range: `[0, depth]` (open front — nothing abuts the slab at Y=0 anymore); keep whatever
  shadow-gap convention makes sense where the slab meets `PANEL-OUT-REAR-001` at Y=depth.
- Z range: `[0, case.height]` (absorbs the former `top_structure` zone; no separate lid volume).
- Build via an explicit 2D profile (not `RectangleRounded`, which rounds all four corners
  equally): a plain rectangle sketch with **vertex fillets applied only at the two front
  corners**, radius `case.corner_radius` clamped to whatever the local geometry actually
  supports (never force a radius bigger than the profile allows), extruded the full height. This
  guarantees a single connected solid by construction — no oversized boolean cylinder subtraction
  (that technique is exactly what produced the 3-solid fragmentation bug in section 0).
- After extrusion, attempt a 3D fillet on the top-front horizontal edge for the "soft slab" look,
  using the same try/except-with-fallback discipline as the existing `_try_top_edge_fillet`. If it
  fails, ship without it and say so plainly in the handoff — do not spend the review cycle budget
  fighting an OCCT fillet failure.
- Confirm `FRAME-POST-*` / left-right `FRAME-RAIL-*` X-extents stay inside the new slab's X range
  (they already are inset by `case.corner_radius`, so this should hold without code changes to
  `frame.py` — verify, don't assume).
- Remove `PANEL-OUT-CORNER-FL/FR/RL/RR-001` and `_apply_outer_corner_fillets` /
  `_build_corner_shell_solid` / `_corner_clip_box` (dead once the slab itself is the rounded
  corner for the front). Decide and document what happens to the rear case corners (keep today's
  modest rounding on `PANEL-OUT-REAR-001` alone, or extend the slab's rear corner too) — either is
  acceptable, just be explicit in the handoff about which was chosen and why.

**Handle placement fix (Finding 1):** move each handle cutout's Y position toward the front of
the slab (clear of `depth/2`) and choose a Z within an open shelf bay, so that the sightline
through the cutout, continued through the slab's new thickness plus a margin, hits nothing else in
the registry (verify this programmatically, not by eye only) and — because the front is now open —
ultimately reads as open air in the render. `hardware.handle_mount_z_mm` stays `TO_MEASURE`; only
the concept-stage *fallback formula* changes to a position that is provably clear, and the fallback
must be documented as provisional (same pattern as `feed_plane_z_provisional_mm`).

**Front panel:** delete `_build_front_panel` / `PANEL-OUT-FRONT-001` entirely. `RETAINER-001`
(dividers.py) and the organizer front-opening logic are unaffected — confirm this with the existing
`test_organizer_front_opening` (repoint or delete it if it becomes meaningless once there is no
front panel at all; state which).

**Top:** delete `build_top_structure` / `TOP-STRUCTURE-001`, or keep a fully embedded structural
tie that never surfaces in a render — implementer's engineering call, but the acceptance test is
visual: no rim/sheet visible over the organizer in `transport_top.png` / `transport_iso.png`.
Update `_HIDDEN_OUTER_SHELL_PREFIXES`, `_suppress_outer_shell`,
`build_transport_shell_top_view_assembly`, and `collision.py`'s several `TOP-STRUCTURE-001`
references accordingly.

**Base plate / Finding 4:** add real through-cut vent slots to `PANEL-IN-BOTTOM-001` reusing the
`_subtract_rear_vent_slots` technique (refactor into a small shared helper parameterized by axis
if convenient — do not duplicate the loop body verbatim). Position clear of feet, frame rails, and
existing service volumes; a sensible location is under the existing `AIRPATH-001` footprint. Close
the bottom half of A-014/D-016.

## 2. Divider confirmation (Finding 3)

State the exact formula for `divider_count` (from `parameters.py`) and the resulting count for the
default `cells=10` configuration, confirm one divider sits between every adjacent pair of film
cells, and add a close-up render (larger canvas or tighter crop on just the organizer bay) so the
count is human-verifiable by eye, not just by reading code.

## 3. Engineering recompute

Rebuild `mass_report.csv` / `stability_report.md` / `deflection_report.md` under
`output/validation/rev3/` from the restructured geometry (update `scripts/generate_mass_report.py`
for any renamed/removed part ids first). Restate the deflection beam model's span, support
conditions, and E source exactly as already corrected in `indicative_tray_deflection_mm` — this
cycle does not touch tray span or `E`, so if the result is still ≈3.95 mm and still exceeds the 1.5
mm ceiling, say so plainly in the report and in `docs/10_USER_INPUT_REQUIRED.md` section C (update
the existing entry, do not duplicate it).

## 4. Review focus for the mandatory adversarial pass

The reviewer must **look at the regenerated PNGs**, not just read the diff:
(a) does `transport_left.png` / `transport_right.png` now show a visibly open handle cutout with
daylight/background through it; (b) does `transport_iso.png` read as two rounded side slabs with
open shelves/open front/open top/closed rear, closer to the reference photo than rev2; (c) does the
organizer close-up show individually countable 2 mm dividers; (d) do the bottom vent slots exist as
real cuts (probe test + render); (e) is every part-id reference in `collision.py`/`assembly.py`
consistent with the surviving registry (no dangling ids); (f) was any fixed TZ dimension moved; (g)
was any assumed input (`tray_panel_youngs_modulus_mpa`, etc.) quietly retuned to force a pass; (h)
does the new side-slab solid remain a single connected body (no repeat of the 3-solid fragmentation
bug elsewhere).

## 5. Verification commands

- `uv run pytest`
- `uv run ruff check .`
- `powershell -ExecutionPolicy Bypass -File .\scripts\setup_windows.ps1`

All three must exit 0 for `verdict: pass`.
