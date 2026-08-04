# PLT-008 — Tray deflection real fix (TZ line 184, PLT-011)

Status: DRAFT for implementer. Tier: T2 (set by Main; do not reclassify). Sole writer: `implementer`
(Composer 2.5-fast). Review: `adversarial-reviewer` (mandatory, Grok). Verification: `verifier`
(Grok). Cap: 3 internal review/verify cycles, third cycle closes blockers only. No
`principal-arbiter` at T2.

Pre-change checkpoint: commit `4531393` ("Align plotter tiers to same front Y and add tray-1
quick-access slide (D-032/D-033)"). rev7 concept revision (`export.py::CONCEPT_REVISION = 7`);
`output/validation/rev7/` does not exist yet on disk — this cycle creates it.

## 0. Problem (do not re-litigate, just fix)

`indicative_tray_deflection_mm()` (`src/stand_cad/geometry/analysis.py:200-213`) models the tray
platform as a **single simply-supported span** of `plotter.physical_width` = 570 mm (rail-to-rail
across X, Cameo 4 governing), UDL from `trays.design_load_kg` = 10 kg distributed over
`plotter.physical_depth` = 195 mm, panel thickness = `tray_panel_thickness_mm` (midpoint of
10–12 mm range = 11 mm), `E` = `materials.tray_panel_youngs_modulus_mpa` = 3000 MPa
(**provenance `to_measure`, no datasheet** — this is the only unsourced input in the model).

Formula: `δ = 5·P·L³ / (384·E·I)`, `I = width_mm·t³/12`. At current inputs this evaluates to
**3.644 mm** against the TZ line 184 / `trays.deflection_max_mm` ceiling of **1.5 mm** — carried
forward from `output/validation/rev6/deflection_report.md`. Real structural failure, not a units
bug.

## 1. Chosen fix — third (centre) slide rail, mid-span support

Rejected alternatives and why:

- **Thicker panel (15–18 mm):** would need δ ∝ 1/t³ → t ≈ 14.8 mm to clear the ceiling at the
  current assumed E, which is **outside** the TZ-verified `tray_panel_thickness_min/max_mm`
  (10–12 mm, TZ section 8 line 221) range. That is a TZ deviation requiring the same
  Main+owner process as the R10 bullnose precedent (D-025) — do not take it silently. Not chosen
  because a no-deviation fix exists (below).
- **Stiffening rib bonded to the panel:** TZ line 221 itself says the platform is "сэндвич- или
  алюминиевая сотовая панель 10–12 мм **с локальными усилителями**" (10–12 mm sandwich/aluminium
  honeycomb panel **with local reinforcements**) — textually anticipated — but modelling a
  composite rib+panel section honestly requires a **second** unsourced stiffness assumption (rib
  bond/section EI) on top of the panel E that is already `to_measure`. Rejected here in favour of
  a fix that adds zero new unsourced material assumptions.
- **Aluminium sheet w/ formed edges instead of sandwich core:** bigger construction change, more
  new assumptions (formed-edge section modulus), not warranted when a support-condition fix closes
  the gap with margin.
- **Chosen: mid-span support.** Add a third slide rail at tray centre-X, same Z-band as the
  existing `SLIDE-*-LEFT/RIGHT-001`, spanning the same Y range. This changes the **support
  condition** only — same panel (10–12 mm, unchanged), same assumed E (still `to_measure`, not
  quietly "improved") — and is explicitly one of the four options Main authorised to evaluate.
  Zero new `to_measure`/`derived` parameter leaves required: reuse `trays.slide_rail_width_mm`,
  `trays.slide_rail_height_mm`, `materials.frame_profile_size_mm` (all already used by the
  existing left/right slide + frame-rail geometry in `trays.py`).

### Beam re-derivation (show the work in the deflection report, not just the number)

Adding a support at tray centre-X bisects the 570 mm rail-to-rail span into two ~285 mm half-spans.
The physically correct model is a statically-indeterminate 2-span continuous beam under UDL; this
codebase's convention (see existing `indicative_*` functions) is an explicit, honest **hand-check**,
not FEA, so use the standard **conservative simplification**: model each half-span as an
**independent simply-supported beam**, carrying its own tributary half of the total load, and
**ignore the elastic-continuity benefit** the real continuous beam would have at the shared centre
support. This is conservative, not optimistic: published two-equal-span continuous-beam-under-UDL
coefficients (`δ_max ≈ 0.0054·w·ℓ⁴/EI`) are ~2.4× **smaller** than the independent-half-span
coefficient (`5/384 ≈ 0.01302·w·ℓ⁴/EI`) used here, because the true continuous beam has moment
continuity at the centre support that this simplification discards. State this explicitly in the
report/docstring — do not present it as the exact continuous-beam solution.

Effective span `ℓ = span_mm / 2`, effective load per half-span `P' = load_n / 2` (UDL intensity
`w = P/L` is unchanged; each half-span of length `L/2` carries `w·(L/2) = P/2`):

```
δ_new = 5·(P/2)·(L/2)³ / (384·E·I) = δ_old / 16
```

At current inputs: `δ_new = 3.644 / 16 ≈ 0.228 mm` — comfortably under the 1.5 mm ceiling (~6.6×
margin), with the true continuous-beam value (not used as the reported figure) even lower.

**E-sensitivity, state honestly:** since `δ ∝ 1/E`, the fix tolerates the assumed E being wrong by
a wide margin: `E` would need to be measured at **below ≈ 460 MPa** (3000 × 0.228/1.5) — roughly a
6.5× drop from the assumed 3000 MPa — before this construction would fail the ceiling again. Record
this margin in the amended ASM entry so a future measurement has a concrete pass/fail threshold
instead of a vague "still assumed" flag.

## 2. Geometry changes (`src/stand_cad/geometry/trays.py`, `kinematics.py`, `collision.py`)

- `trays.py`: generalise `_slide_bounds`/`_tray_frame_rail_bounds` (or add sibling helpers) to
  support `side="center"` — centre-X window of width `trays.slide_rail_width_mm` computed from
  tray bounds midpoint (`cx = (x0+x1)/2`, same pattern as `_soft_stop_bounds`), same Z-band as the
  left/right slide (so the tray rests level on all three rails) and the matching fixed frame rail
  below it (same Z-band as `_tray_frame_rail_bounds`, centred at `cx`). New parts, one pair per
  tray level: `SLIDE-{LOWER,UPPER}-CENTER-001` (material `full_extension_slide_hardware`,
  `verify_on_real_machine=True`, same as existing side slides) and
  `FRAME-RAIL-TRAY-{LOWER,UPPER}-C-001` (material `aluminium_angle_15x15x1.5`, fixed, **not** in
  the kinematic group — matches how `FRAME-RAIL-TRAY-*-L/R-001` are fixed today).
- `kinematics.py`: add `SLIDE-LOWER-CENTER-001` to `LOWER_KINEMATIC_GROUP` and
  `SLIDE-UPPER-CENTER-001` to `UPPER_KINEMATIC_GROUP` (moves with tray on extension, same as the
  side slides) — do **not** add the new frame rails to either kinematic group.
- `slides_fully_extended_solids()` already collects everything whose `part_id` starts with
  `"SLIDE-"`, so the new centre slide is automatically included in the full-extension interlock
  check — verify this, don't assume it.
- Confirm the new centre rail's X-window does not fall inside the interlock shuttle's X-window
  (`plotter_x1 - rail_w` to `plotter_x1`, right edge) — it should not, since centre-X is far from
  the right edge, but verify with the actual computed numbers, not just visual inspection.
- Confirm the new centre rail's Z-band (below the tray, at slide height) does not intersect the
  media-feed-path Z-band (`plotter_z + physical_height/2`-ish, well above the tray top) — different
  Z bands entirely; verify with `intersection_volume`/existing collision helpers, not just
  narrative.
- `collision.py`: `RAW_MATING_PAIRS`, `is_penetrating_structural_joint`'s
  `_share_face_if_prefix(..., "TRAY-", "FRAME-RAIL-TRAY")` /
  `_share_face_if_prefix(..., "SLIDE-", "FRAME-RAIL-TRAY")`, and
  `is_staggered_tier_y_overlap`'s `lower_markers`/`upper_markers` are prefix-based
  (`"SLIDE-LOWER-"`, `"FRAME-RAIL-TRAY-LOWER-"`, etc.) so the new parts should already be covered —
  **verify this by running the full suite**, do not assume; add explicit `RAW_MATING_PAIRS` entries
  only if the generic prefix checks do not already cover the new intentional touches (tray↔centre
  slide, centre slide↔centre frame rail, plotter↔centre slide).

## 3. Analysis / report changes (`analysis.py`, `generate_mass_report.py`)

- Rewrite `indicative_tray_deflection_mm()` docstring + body to state the new support condition
  (three rails, half-span, conservative independent-half-span simplification) per §1. Keep the
  function pure/parametric — no literals; `span_mm`, `load_n` stay derived from
  `plotter.physical_width` / `trays.design_load_kg` as today, halved inside the function with the
  reasoning in the docstring, not a magic `/16` with no explanation.
- `write_deflection_report()`: show the full beam model — original single-span numbers **and** the
  new three-rail numbers, the conservative-simplification caveat, the E-sensitivity margin, and the
  verdict (ceiling met under the current indicative model; E remains `to_measure`). Do not delete
  the honest history of the 3.644 mm finding — carry it forward as "before".
- Re-run `write_mass_report()` / `write_stability_report()` — new parts (2× slide, 2× frame rail)
  change `empty_case_structural_kg` (frame rails only, slides are `verify_on_real_machine=True`
  and excluded from the structural total, same as today) and part counts; confirm the structural
  total stays inside `mass_targets.empty_case_target_min/max_kg` (9–11 kg) / ceiling (12 kg) with
  actual numbers, not an assumption — current baseline is 6.782 kg (rev6), so headroom is large but
  must be shown, not asserted.
- Confirm `computed_upper_z_mm`/tier clearance formulas are untouched (they are — this fix does not
  change `tray_panel_thickness_mm`), so both tiers keep their ≥170 mm clearance and the 610 mm clear
  width / 650 mm overall width / R10 bullnose stay as-is. State this explicitly in the Final Report
  rather than leaving it implied.

## 4. Tests (`tests/test_geometry.py`)

- Update `test_indicative_tray_deflection_non_authoritative` to match the new formula (halved span,
  halved load) — keep it as an exact-arithmetic check, not a rounded literal.
- Add a new test, e.g. `test_indicative_tray_deflection_meets_tz_ceiling`, that asserts
  `indicative_tray_deflection_mm(params) < trays.deflection_max_mm` with a clear failure message
  citing TZ line 184 — this is the "fails loudly if it regresses" requirement from Main.
- Add/extend a collision or kinematics test asserting the new centre slide/frame-rail parts exist,
  are captured by the kinematic-group and full-extension helpers, and do not collide unexpectedly
  (reuse the existing collision-check fixtures/patterns in `test_geometry.py`/`test_kinematics.py`).
- All 132 pre-existing tests must keep passing — do not delete or weaken coverage to make room.

## 5. State updates

- `state/ASSUMPTIONS.md`: amend `A-012` in place — new construction (three-rail support, halved
  effective span), new indicative figure (≈0.228 mm), the E-sensitivity threshold (≈460 MPa) as the
  new concrete validation criterion, status stays **Open** (E is still `to_measure` — the fix
  changes the geometry, not the material provenance).
- `state/DECISION_LOG.md`: new entry `D-035` — third centre slide rail added to both tray levels to
  fix TZ line 184 deflection ceiling; cite the rejected alternatives from §1 and the before/after
  numbers.
- `state/REQUIREMENTS_TRACEABILITY.csv`: update the `PLT-011` row — evidence path to
  `output/validation/rev7/deflection_report.md`, notes reflecting the three-rail fix and the
  indicative pass, status stays `IN_PROGRESS` (not `VERIFIED` — no FEA, no measured E).

## 6. Regeneration

- Regenerate `output/validation/rev7/` (`mass_report.csv`, `stability_report.md`,
  `deflection_report.md`, views) via the existing `scripts/generate_mass_report.py` /
  `scripts/render_validation_views.py` / `scripts/regenerate.py` pipeline — check which script(s)
  actually drive `rev{CONCEPT_REVISION}` output and use them, don't hand-roll a new path.
- Keep `CONCEPT`/`REFERENCE_ONLY` markings in filenames; no PDF, no production DXF, no gate
  transitions, no push.

## Verification (all must pass, exit 0)

- `uv run pytest`
- `uv run ruff check .`
- `powershell -ExecutionPolicy Bypass -File .\scripts\setup_windows.ps1`
- Adversarial review specifically checking: (a) the beam model/simplification is stated, not
  hidden; (b) the E source is honestly labelled `to_measure` throughout (report, ASM, traceability);
  (c) the fix did not silently regress tier height (≥170 mm ×2), mass target band (9–11 kg /
  12 kg ceiling), or the tier-1 130 mm quick-access / 250 mm full-extension slide clearance verified
  in rev6/rev7 baseline.

Local commit encouraged at the end of a clean cycle; no push.
