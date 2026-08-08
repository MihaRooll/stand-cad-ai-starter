# Plan: PLT-005 — dev-loop automation (Part A) + fidelity cycle 3 (Part B)

Tier: **T2** (Main's explicit ruling). Mandatory `adversarial-reviewer`, **no** `principal-arbiter`.
Sole writer: `implementer` (composer-2.5-fast), sequenced through Part A then Part B so there is never
a concurrent writer. Review/verify on `cursor-grok-4.5-high-fast`. Cap 3 internal review/verify
cycles; cycle 3 is blocker-only; an open blocker after cycle 3 is `BLOCKED`, reported honestly.

Baseline (Main-confirmed, do not regress): `uv 0.11.8` responds; `uv run pytest` passes 121 tests;
`uv run ruff check .` clean.

## 0. Orchestrator-established facts for Part B (established by direct diagnostic, re-verify by render — do not re-derive from scratch)

All five findings were independently reproduced from the **current, unmodified** `rev3` source and
renders (not guesswork). Evidence below is the starting point for the implementer; the adversarial
reviewer must re-check by looking at the regenerated PNGs, per the stage contract.

### Finding 1 (handle) — root cause is real, not "no boolean cut"

The handle cutout in `PANEL-OUT-LEFT/RIGHT-001` **is** a genuine boolean through-cut
(`_subtract_rounded_through_x` in `panels.py`) — this has been true for two cycles running. It fails
to read as an opening for two compounding reasons, both confirmed by direct measurement:

1. **Sightline hits equipment, not open air.** Current fallback mount position: `y_center =
   depth*0.25 = 137.5 mm`, `mount_z = upper_z + physical_height/2 = 190 + 62 = 252 mm`. Cutout
   footprint: Y `82.5–192.5`, Z `234.5–269.5`. `EQUIP-PLOTTER2-001` physical body occupies Y
   `170–346`, Z `190–314` (from `plotter_physical_bounds(2)`). The two rectangles overlap on Y
   `170–192.5` × Z `234.5–269.5` — part of the cut looks straight into the red plotter body
   (`equipment_reference` material, RGB `(220,90,90)`), which is exactly the "red" half of the
   "small red-and-white patch" the owner and Main both saw in `transport_left.png` /
   `transport_right.png`.
2. **Even the open portion is invisible against near-white.** `render_validation_views.py`'s PNG
   background is pure white `(255,255,255)`; `cast_opal_pmma_3mm` (the side-panel material) renders
   at `(245,245,250)`. Where the cutout genuinely reveals open background (Y `82.5–170`, no
   equipment there), the pixel colour is white-on-near-white — technically a real hole, but
   imperceptible. This is the same problem the codebase already solved once for
   `base_plate_closeup.png` via `BASE_PLATE_CLOSEUP_BACKGROUND_RGB = (150,150,150)` — that pattern
   was never applied to the side views.

**Fix must do both:** reposition the cutout (Y and/or Z, formula stays `derived`/documented
provisional, same discipline as `feed_plane_z_provisional_mm`) so the full footprint is clear of
`EQUIP-PLOTTER1-001` / `EQUIP-PLOTTER2-001` / `ENV-PLOTTER*` / any frame/organizer part —
**verify this programmatically** (a helper that checks the cutout's swept volume against every
registered part's bounding box, not eyeballing); **and** use a contrasting (non-white) background
for `transport_left.png` / `transport_right.png` so a genuine open cut is visually legible, mirroring
the existing `base_plate_closeup` pattern. Do not just say "handle present" — the strengthened test
(AC-B1) and the reviewer's own look at the PNG are what count.

### Finding 2 (organizer) — no regression occurred; long-standing render-angle defect

Direct comparison: `output/validation/rev1/views/organizer_loaded_iso.png`,
`rev2/views/organizer_loaded_iso.png`, and `rev3/views/organizer_loaded_iso.png` are pixel-identical
in composition (same solid mass, same sawtooth) — **this defect predates rev3 and was never
introduced by cycle 2.** State this plainly; do not report a code regression that did not happen.

Root cause, confirmed by isolating parts and re-rendering: `FILM-BODY-*` boxes are `cell_w`(59.2 mm,
X) × `film_depth`(500 mm, Y) × `film_design_height`(320 mm, Z). Their large X-facing broadside
(Y×Z ≈ 160,000 mm²) is ~8× the area of their Y-facing front strip (X×Z ≈ 19,000 mm²) — the face that
actually reads as a "colour band" like the reference photo. The current iso camera direction
`(-1,-1,1)` gives X and Y equal weight, and because adjacent cells are offset by only 61.2 mm in X
while each broadside spans 500 mm in Y, cell 0's broadside occludes ~88% of every other cell's
broadside on screen — leaving only thin diagonal slivers (the "sawtooth"). Isolating
`FILM-BODY-*`+`DIVIDER-*` and re-rendering with a front-dominant direction such as `(0,-1,0.15)`
(tested) shows all 10 distinct colour bands with visible divider lines cleanly, proving the
**geometry is already correct** — this is a camera-angle-only defect in
`render_validation_views.py`, not a source regression.

**Separately found while diagnosing (real defect, fix while in this file):**
`build_film_body_parts` in `assembly.py` computes `x0 = org_x + divider_t + i*(cell_w+divider_t)`
for `i` in `range(cells)` (10), implicitly assuming a divider sits immediately left of every film
index. That holds for `i=0..8` (dividers exist at `_divider_x_positions()[0..8]`), but there is no
`DIVIDER-009` (`divider_count = cells-1 = 9`, indices 0–8 only) — so `FILM-BODY-009`'s right edge
lands at `632.0 mm`, 2 mm past `film_storage.x + film_storage.clear_width` (`630 mm`), intruding into
`PANEL-OUT-RIGHT-001`'s inner wall zone. Fix the formula so film 0 sits flush against the left
boundary (no divider before it, mirroring how divider-000 sits flush at the boundary today) or
however you choose to resolve the asymmetry — the constraint is that all 10 films must fit inside
`[org_x, org_x+clear_width]` with a divider between every adjacent pair, no overshoot.

**Fix:** change the camera direction used for `organizer_loaded_iso.png` and `organizer_closeup.png`
(only those two — do not change the shared `transport_iso`/front/rear/left/right/top directions used
by every other target) to a front-dominant angle that keeps the 10 bands and divider lines legible,
plus the film-body X-formula fix above.

### Finding 3 (feet) — invisible because the shell already sits on the floor

`FOOT-001..004` (hardware.py) are genuinely built (Z `0..foot_h≈9`), but `PANEL-OUT-LEFT/RIGHT-001`
(`panels.py::_build_side_slab_with_handle`) and `PANEL-OUT-REAR-001`
(`panels.py::_build_rear_panel`) both start at `z_min=0.0` — i.e. the outer shell itself touches the
table at Z=0, at the same level as the feet, so there is no visible lift and the feet sit recessed
inside/behind the shell in every view. Contrast with `FRAME-RAIL-BASE-*` (`z_base=foot_h`) and
`PANEL-IN-BOTTOM-001` (`bottom_z=foot_h+thickness`, starts at `foot_h`) — those two already do this
correctly. `case.height` (690, fixed) is the **overall envelope Z 0→690 including the feet**
(`datums.case_envelope.z` does not change); only the outer-shell parts' own `z_min` needs to move
from `0` to `foot_h`, and the overall silhouette stays 690 mm tall in `case_envelope` terms since the
feet fill exactly the gap. This is a genuinely reversible fix that does not move any fixed dimension.

**Fix:** raise `PANEL-OUT-LEFT/RIGHT-001` and `PANEL-OUT-REAR-001` (and any other outer-shell part
still starting at `z=0`) to start at `z=foot_h` instead of `0`, so the Z `0..foot_h` slice contains
only the four feet — they will then read as visible round pads under a lifted case in every side/
front/iso view, matching the reference photo, with no change to `case.height`/`case_envelope`.

### Finding 4 (side-slab shape language) — hollow "picture frame" shell, R25 unreachable on a 20 mm slab

Two compounding issues, both measured directly:

1. `_extrude_side_slab` builds a **hollow shell**: outer rectangle (`side_clear`=20 mm in X ×
   `depth` in Y) minus an inset-by-`wall_mm`(3 mm) inner rectangle, leaving a thin 3 mm "picture
   frame" wall with an open interior and open top/bottom — this is why the render reads as "a flat
   sheet with a frame edge" rather than a sculpted mass, and why the `FRAME-RAIL`/equipment "L-shaped
   grey element" is visible through the panel in `transport_left.png` (it is inside the hollow
   cavity, seen through the handle cut).
2. The requested front-corner fillet radius (`case.corner_radius = 25 mm`, fixed/verified) is
   **silently clamped** in `_extrude_side_slab` to `min(front_corner_radius, width/2 - 0.1, depth/2 -
   0.1)` — with `width = side_clear = 20 mm` (itself derived from the fixed `case.width`/
   `case.internal_width`), the true ceiling is `9.9 mm`, not `25 mm`. **This is a hard geometric
   limit, not a code choice**: a rectangle whose short side is 20 mm cannot take a corner fillet
   larger than 10 mm without the arc self-intersecting. Matching the reference's large, dominant
   radius exactly is therefore geometrically impossible without widening `side_clear`, which is
   derived from fixed TZ dimensions — **do not widen it**; state this ceiling plainly as a divergence
   from the reference rather than forcing a larger radius by some other trick.

**Fix (bounded by the above):** make the side slab **solid** (drop the inset-inner-rectangle
subtraction so the full 20 mm × height volume is one solid block, still with the front-corner fillet
at the maximum geometrically valid radius, currently ≈9.9 mm) so it reads as a chunky, sculpted mass
instead of a thin frame edge; keep attempting the top-front edge fillet with the existing
try/except-with-fallback discipline. Report the R25-vs-≈9.9mm ceiling explicitly as a stated,
justified divergence — do not claim full reference match on radius.

### Finding 5 (ventilation invisible) — real cuts, same near-white contrast problem as Finding 1

`base_plate_closeup.png` (dedicated grey `(150,150,150)` background) already shows the 5 bottom vent
slots clearly as distinct grey bars — proof the bottom cuts are real. `transport_rear.png` uses the
default white background, and the rear vent band (`hardware.vent_band_z_mm=45`, near the feet) is
barely a pale streak against the near-white `PANEL-OUT-REAR-001` — same invisibility mechanism as
Finding 1, not a missing cut.

**Fix:** apply the same contrasting-background technique to `transport_rear.png` (or add a dedicated
rear vent close-up render analogous to `base_plate_closeup.png`) so the existing rear cuts are
legible. TZ line 290 already specifies bottom+rear; the reference photo shows a fine slot pattern low
on the *side* — implement per the TZ (bottom+rear, unchanged) and record the side-vs-TZ divergence
explicitly in the handoff/decision log; do not silently follow the picture over the TZ.

## Task Contract

```yaml
contract_id: PLT-005-fidelity-cycle3-and-automation
tier: T2
goal: >
  Part A: give the owner a doctor script that diagnoses the environment (including the specific
  WSL chdir failure signature) and a live-reload viewer loop so iteration does not require manual
  restarts. Part B: fix the five rev3 fidelity findings at their measured root causes (not
  cosmetic patches) without moving any fixed TZ dimension, and produce a new revision's full
  evidence pack.
acceptance_criteria:
  # --- Part A ---
  - id: AC-A1
    text: >
      scripts/doctor.py exists, runs as `uv run python scripts/doctor.py`, and checks + reports
      pass/fail with a plain-English remedy for each: uv resolves and its version; Python is
      3.12; repo root is reachable from the current shell; `uv run pytest --collect-only`
      succeeds; concept artifacts exist in output/concept/; viewer/vendor/three@0.170.0 files
      exist with plausible (non-zero, non-trivially-small) sizes; port 8000 is free or already
      serving our viewer (distinguish the two cases in the report). If the WSL failure signature
      `chdir(/mnt/c/...) failed` is detected (check whatever surfaces it — shell env, a probe
      command's stderr, etc.; document exactly what is probed), print the exact remedy: run
      `wsl --shutdown` in PowerShell, then restart the Cursor window.
  - id: AC-A2
    text: >
      scripts/serve_viewer.py gains a `--watch` mode that polls output/concept/ modification
      times and exposes them on a small HTTP endpoint (document the endpoint path and payload
      shape). viewer/index.html polls that endpoint every ~2s and, when the newest model's
      mtime/manifest changes, reloads the model in place while preserving: camera position +
      OrbitControls target (no re-fit-to-bbox on a live-reload), the visibility tree state
      (per-part-id checkbox state carried across reload, matched by part_id — parts absent in
      the new manifest are dropped gracefully, new parts default visible), and the three
      section-plane positions/enabled state. Manual model-switching via the dropdown still does
      a full fit-to-view (unchanged behaviour) — only the automatic watch-triggered reload
      preserves camera/visibility/clipping.
  - id: AC-A3
    text: >
      scripts/regenerate.py exists, runs as `uv run python scripts/regenerate.py`, regenerates
      the model + all views for the current live source (calling the existing generator/render
      entry points — do not duplicate their logic), and prints the resulting revision number and
      every artifact path written. A running --watch viewer picks up the result automatically
      (no additional owner action).
  - id: AC-A4
    text: viewer/README.md documents --watch, the new endpoint, scripts/doctor.py, and scripts/regenerate.py.
  # --- Part B ---
  - id: AC-B1
    text: >
      Finding 1 (handle) fixed at the root cause per section 0: cutout repositioned so its full
      footprint (grip length/depth from hardware.handle_grip_length_mm/handle_grip_depth_mm,
      unchanged) is programmatically verified clear of every other registered part's bounding
      box (not just EQUIP-PLOTTER*) at the render-relevant depth; contrasting background applied
      to transport_left.png/transport_right.png (or an equivalent legibility fix) so the open cut
      is visually obvious. New/strengthened test (grid-sampled across the full cutout footprint,
      not just the centre point already covered by test_handle_cutout_dimensions) asserts no
      other part occupies the swept volume. Reviewer confirms by looking at the regenerated PNGs.
  - id: AC-B2
    text: >
      Finding 2 (organizer) addressed: state plainly in the handoff that rev1→rev2→rev3 showed no
      regression (cite the pixel-identical comparison). Fix the FILM-BODY-009 overshoot formula
      bug. Change only the organizer_loaded_iso.png / organizer_closeup.png camera direction to a
      front-dominant angle (do not change the shared transport_iso/front/rear/left/right/top
      directions). Regenerated organizer_loaded_iso.png and organizer_closeup.png must show 10
      visually distinct colour bands with visible 2 mm divider lines between them, confirmed by
      the reviewer looking at the PNGs.
  - id: AC-B3
    text: >
      Finding 3 (feet) fixed: PANEL-OUT-LEFT/RIGHT/REAR-001 (and any other outer-shell part still
      starting at z=0) raised to z_min=materials.foot_height_mm; case_envelope/case.height stays
      690 mm unchanged. Four feet visibly read as round pads lifting the case off the table plane
      in transport_front.png, transport_left.png/right.png, and transport_iso.png.
  - id: AC-B4
    text: >
      Finding 4 (side-slab shape) addressed within the stated ceiling: side slabs rebuilt as
      solid volumes (no hollow interior) with the front-corner fillet at the maximum
      geometrically valid radius (verify and state the actual value achieved, expected ≈9.9 mm,
      not 25 mm) plus best-effort top-front edge fillet (existing try/except discipline). The
      R25-vs-achieved-radius gap is stated explicitly as a bounded divergence in the handoff and
      in docs/10_USER_INPUT_REQUIRED.md if it materially affects sign-off — not silently dropped.
      Side panels remain single connected solids (len(solid.solids()) == 1).
  - id: AC-B5
    text: >
      Finding 5 (ventilation) addressed: rear vent cuts confirmed real via a probe test (grid
      sample through the cut, analogous to the bottom-vent proof already in place) and made
      visually legible in a regenerated rear render (contrasting background or dedicated
      close-up, implementer's choice — state which). The bottom-vs-rear-vs-reference's-side
      divergence from TZ line 290 is stated explicitly, not silently resolved by following the
      picture.
  - id: AC-B6
    text: >
      Every new numeric value has a provenance tag (verified/derived/to_measure) in
      config/parameters.yaml with a note citing its TZ line or derivation formula; no literal
      dimension is added directly in geometry/render Python. No fixed TZ dimension in the
      "Constraints" section of the stage contract moves. If any reference-driven change would
      require moving one, stop and report it in docs/10_USER_INPUT_REQUIRED.md instead of doing it.
  - id: AC-B7
    text: >
      All 121 existing tests keep passing (or are deliberately, individually updated with a
      stated reason if a fixed geometric assumption they encode changed — e.g. the film-body
      formula fix — never bulk-loosened to force green). Every new opening (handle,
      repositioned/added vent probes) gets a new test proving it is a real boolean cut that does
      not break clearance/collision checks or the overall 650x550x690 bounding box.
  - id: AC-B8
    text: >
      A new revision (rev4) is generated: full 10 PNG + 5 SVG view set + organizer_closeup.png +
      base_plate_closeup.png under output/validation/rev4/views/, and
      output/concept/*_rev4.*(step/stl/glb/manifest). rev1/rev2/rev3 under output/validation/ and
      output/concept/ are left untouched. viewer/index.html and any hardcoded rev3 references in
      scripts/export.py's DEFAULT_STEP_NAME etc. are updated to rev4 consistently.
  - id: AC-B9
    text: >
      state/REQUIREMENTS_TRACEABILITY.csv, state/PROJECT_STATE.md, state/ASSUMPTIONS.md,
      state/DECISION_LOG.md updated: new rev4 entry, the Finding 2 "no regression, render-angle
      defect" conclusion recorded as a decision-log row (correcting any prior rev2-vs-rev3
      regression claim), and the Finding 4 R25-ceiling divergence recorded.
  - id: AC-B10
    text: uv run pytest exits 0; uv run ruff check . exits 0; full setup_windows.ps1 exits 0.
owned_files:
  - scripts/doctor.py
  - scripts/serve_viewer.py
  - scripts/regenerate.py
  - scripts/generate_model.py
  - scripts/render_validation_views.py
  - scripts/generate_mass_report.py
  - viewer/index.html
  - viewer/README.md
  - src/stand_cad/geometry/panels.py
  - src/stand_cad/geometry/hardware.py
  - src/stand_cad/geometry/assembly.py
  - src/stand_cad/geometry/dividers.py
  - src/stand_cad/geometry/collision.py
  - src/stand_cad/geometry/export.py
  - src/stand_cad/geometry/frame.py
  - config/parameters.yaml
  - tests/test_geometry.py
  - tests/test_kinematics.py
  - tests/test_parameters.py
  - state/REQUIREMENTS_TRACEABILITY.csv
  - state/PROJECT_STATE.md
  - state/ASSUMPTIONS.md
  - state/DECISION_LOG.md
  - docs/10_USER_INPUT_REQUIRED.md
  - output/validation/rev4/**
  - output/concept/*_rev4.*
verify_commands:
  - uv run pytest
  - uv run ruff check .
  - powershell -ExecutionPolicy Bypass -File .\scripts\setup_windows.ps1
forbidden:
  - No change to any fixed TZ dimension: 650x550x690 overall envelope, case.internal_width (610),
    plotter physical/design envelopes and coordinates, the 150 mm setback, organizer 610x510x325
    clear volume, cell formula, tray extensions, feed-plane provisional values.
  - No new invented numeric parameter without a provenance tag and cited TZ line or formula.
  - No PDF or DXF generation. No gate marked passed; no PROTOTYPE_RELEASED/SERIES_RELEASED
    anywhere. No git push (local commits are fine if asked).
  - Do not touch output/validation/rev1|rev2|rev3/** or output/concept/*_rev1.*|*_rev2.*|*_rev3.* —
    they remain reproducible "before" evidence.
  - Do not silently retune any assumed input (e.g. materials.tray_panel_youngs_modulus_mpa) to
    force a test or report to pass.
  - Do not widen case.internal_width/side_clear to chase the reference's R25 corner — report the
    ceiling instead (Finding 4).
```

## Review focus for the mandatory adversarial pass

Look at the regenerated PNGs, not just the diff:
(a) do `transport_left.png`/`transport_right.png` now show a legible open handle cutout (contrasting
background, clear of equipment)?
(b) do `organizer_loaded_iso.png`/`organizer_closeup.png` show 10 distinct colour bands with visible
divider lines?
(c) do the four feet visibly lift the case off the table plane in front/left/right/iso?
(d) do the side slabs read as solid sculpted volumes rather than a thin frame, and is the R25-vs-
achieved-radius divergence stated rather than hidden?
(e) is a rear-vent grille pattern now legible in some render?
(f) does the live-reload viewer genuinely preserve camera/visibility/clipping across an automatic
watch-triggered reload (not just on first load)?
(g) does `scripts/doctor.py` detect the exact WSL signature and print the exact remedy?
(h) was any fixed TZ dimension moved, or any assumed input silently retuned?
(i) is every new numeric value provenance-tagged?

## Verification commands

- `uv run pytest`
- `uv run ruff check .`
- `powershell -ExecutionPolicy Bypass -File .\scripts\setup_windows.ps1`

All three must exit 0 for `verdict: pass`.
