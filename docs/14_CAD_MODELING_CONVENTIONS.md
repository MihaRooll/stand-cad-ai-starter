# CAD modeling conventions

Mechanical, evidence-based rules from real defects found and fixed in this repository. Not generic CAD advice — every rule cites the file/line or decision that motivated it. Read this before re-deriving a fix that already has a documented precedent.

## 1. Cladding must share the covered rail's exact bounds

A cosmetic cladding part covering a structural frame/rail member must be built from the **same bounds-computing call** as the member it covers, not an offset strip placed in front of it. `build_frame_cladding()` (`src/stand_cad/geometry/frame.py:237`) follows this: perimeter cladding reuses the `z_base`/`z_top` and `[inset, width-inset]` X span used by `_perimeter_rail()` (`frame.py:182`); tray-rail cladding calls `box_from_bounds(*_tray_frame_rail_bounds(params, tray_b, side=side))` (`frame.py:300-301`) — the identical bounds helper the rail itself uses, from `src/stand_cad/geometry/trays.py::_tray_frame_rail_bounds`. An offset strip has zero geometric overlap with what it should conceal (D-026, D-039).

## 2. Render depth tie-break: material priority, not draw order

When cladding and its rail occupy the same plane, the rasterizer must resolve the depth tie by material priority, not insertion order. `scripts/render_validation_views.py:92-96` defines `DEPTH_EPSILON_MM = 1e-6` and `MATERIAL_RENDER_PRIORITY` (cladding materials `cast_opal_pmma_3mm`/`white_composite_3_4mm`/`transparent_petg_2mm` → priority 1, default 0). **Register any new cladding material in this dict** or it will silently lose every coplanar tie against the structural rail it covers, exactly like every render since rev5 did before D-040.

## 3. Use a grey background for QA renders

A white part on a white background is invisible. `render_validation_views.py:99-101` sets `BASE_PLATE_CLOSEUP_BACKGROUND_RGB`/`SIDE_VIEW_BACKGROUND_RGB`/`REAR_VIEW_BACKGROUND_RGB` to `(150, 150, 150)` with the comment "near-white panel on white PNG" — this cost three review cycles before being fixed. Any new render intended to check an opening, cutout, or clearance must use a non-white background.

## 4. Stability requires split moving/stationary mass, never one combined total

A tip-over factor computed as `restore_arm / overturn_arm` with the **same** combined mass in both moments cancels mass out of the ratio — a real bug (D-039), not a hypothetical one: the retired `_legacy_tip_factor()` (`src/stand_cad/geometry/analysis.py:270-285`) multiplies one `total_mass` into both `restore_moment` and `overturn_moment` (lines 283-284), so only the extension ratio ever mattered. The corrected model, `stability_report_inputs()` (`analysis.py:288`), splits `moving_mass` (extending tray + its plotter) from `stationary_mass` (everything else, including the other plotter) with each mass's own real centroid (lines 304-331). Never regress to the combined-mass form.

## 5. Never trust a claimed overlap or "now concealed" state without independent proof

Reading the generator code and assuming a fix worked is not evidence. Two real examples from this project: the tier-2/plotter-1 overlap was only proven by scripted `intersection_volume` measurement, not by inspection (`docs/10_USER_INPUT_REQUIRED.md:65-105`, D-038); and "frame concealed, confirmed by render" was wrong for every render since rev5 because the rasterizer itself misreported what it drew (D-040, `state/DECISION_LOG.md` D-040 row). Require a computed `intersection_volume` or an isolation render before accepting a clearance/visibility claim.

## 6. One dimension, one place, with a provenance tag

Every dimension in `src/stand_cad/geometry/**` must come from `config/parameters.yaml` via `Parameters.value(...)`, and every leaf carries exactly one provenance tag — `verified`, `derived`, or `to_measure` (`src/stand_cad/parameters.py:21`, `config/parameters.yaml:22-28` shows the `{value, provenance, note}` pattern). Commit `9e38f98` ("QA sweep cycle 1: wire remaining hardcoded dimensions to config/parameters.yaml") is the concrete precedent for what happens when this lapses: `src/stand_cad/parameters.py` had accumulated dead duplicate constants `CASE_DEPTH_TOLERANCE_MM` and `TIER_CLEARANCE_MIN_MM = 170` that duplicated `case.depth_tolerance_mm` and `plotter.tier_clearance_min_mm` (`config/parameters.yaml:42`) — two sources of truth for the same number is a drift risk even before they actually diverge. Never add a Python constant that duplicates a config leaf; add the leaf and read it.
