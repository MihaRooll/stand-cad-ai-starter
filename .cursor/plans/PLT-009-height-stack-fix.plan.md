# PLT-009 — Correct height-stack formula for tier-2 under-tray hardware clearance (`docs/10_USER_INPUT_REQUIRED.md` §H)

Status: DRAFT for implementer. Tier: **T2** (set by Main; do not reclassify — physical dimension
change, weak oracle). Sole writer: `implementer` (Composer `composer-2.5-fast`). Review:
`adversarial-reviewer` (**mandatory**, Grok) — independently recompute intersection volumes at
every listed position, do not trust implementer numbers. Verification: `verifier` (Grok). Cap: 3
review/verify cycles, third cycle closes blockers only. No `principal-arbiter` at T2.

Pre-change checkpoint: commit `d3e4247` ("QA sweep cycle 2: notch front-left post for film-shelf
withdrawal, quantify F-5"). 285 pytest passing. `CONCEPT_REVISION = 8` currently on disk; this
cycle creates **rev9**.

## 0. Problem (root-caused already — do not re-litigate, just fix)

`config/parameters.yaml` `plotter.upper_z` formula only reserves the tray panel's own thickness
(`tray_panel_thickness_mm`, 11 mm) between tier-1's clear zone and tier-2's tray, but omits the
mounting hardware stack that actually sits **below** `TRAY-UPPER-001`: `trays.slide_rail_height_mm`
(12 mm, `to_measure`) + `materials.frame_profile_size_mm` (15 mm, `verified`) = 27 mm. Root cause and
full quantified evidence: `docs/10_USER_INPUT_REQUIRED.md` §H (43,875 mm³ at rest down to 0 mm³ only
at 196 mm of tray-1 travel). `case.height` is **not** an owner-fixed dimension (only `case.width`=650,
`case.internal_width`=610, and `case.side_slab_bullnose_radius_mm` are locked) — growing it is the
correct, conservative, non-destructive resolution. Do **not** attempt to find thinner slide hardware
to make the number work instead; `trays.slide_rail_height_mm` stays `to_measure` and must not be
silently retuned.

## 1. The fix — `config/parameters.yaml` formula corrections

Change `plotter.upper_z` to reserve the **full** under-tray stack, then propagate the same +27 mm
through every downstream leaf that stacks on top of it. Verified by exploration — this is the
**complete** dependency chain in `config/parameters.yaml` (do not assume this list is exhaustive;
re-`grep` for `upper_z`, `film_storage_horizontal.z`, `top_structure`, `case.height` before you
finish to confirm no other leaf note references the old numbers):

| Leaf | Old | New | Formula (write into the YAML `note:`) |
|---|---|---|---|
| `plotter.upper_z` | 211 | **238** | `lower_z + tier_clearance_min_mm + slide_rail_height_mm + frame_profile_size_mm + tray_panel_thickness_mm = 30 + 170 + 12 + 15 + 11` |
| `film_storage_horizontal.z` | 396 | **423** | `upper_z + tier_clearance_min_mm + frame_profile_size_mm = 238 + 170 + 15` (formula itself unchanged, matches `Parameters.computed_organizer_z_mm`) |
| `top_structure.z_min_mm` | 502 | **529** | `film_storage_horizontal.z + shelf_stack_height_mm = 423 + 106` (formula unchanged) |
| `top_structure.z_max_mm` | 517 | **544** | `z_min_mm + height_mm = case.height` (formula unchanged) |
| `case.height` | 517 | **544** | `film_storage_horizontal.z + shelf_stack_height_mm + top_structure.height_mm = 423 + 106 + 15` (formula unchanged; matches `Parameters.computed_case_height_mm`) |
| `hardware.handle_mount_z_mm` | 263 | **276.5** | `(foot_height_mm + case.height) / 2 = (9 + 544) / 2` — update the note's CoM commentary too (see §3) |

Also update `src/stand_cad/parameters.py`:

- `Parameters.computed_upper_z_mm` (lines ~142-147) — add `trays.slide_rail_height_mm` and
  `materials.frame_profile_size_mm` to the sum, matching the corrected YAML formula. This property
  currently is **not** wired into `validate_parameters()` (no `PARAM-0xx` check calls it) — confirm
  that with a `grep` before you finish, and if you find it genuinely unused for validation, leave it
  that way (do not invent a new validator check unless you find one already expects it); just make
  sure the property's own arithmetic is correct and add/keep a unit test asserting
  `params.computed_upper_z_mm == pytest.approx(float(params.value("plotter.upper_z")))` (extend
  `tests/test_parameters.py`, near the existing `test_computed_case_height_matches_yaml`).
- Do **not** touch `interlock_shuttle_travel_mm`, `tier_clearance_lower_mm`,
  `tier_clearance_upper_mm`, `computed_organizer_z_mm`, or `computed_case_height_mm` bodies — their
  formulas are already correct and will pick up the new `upper_z`/`case.height` automatically on
  next read. Confirm (don't assume) that `tier_clearance_lower_mm` grows from 170 to 197 mm and
  `tier_clearance_upper_mm` stays ≥170 mm after the edit — both must stay `>=
  plotter.tier_clearance_min_mm` (existing `PARAM-012` check in `validate_parameters`).

No literal Z coordinate may appear in `src/stand_cad/geometry/*.py` — everything already reads
`plotter.upper_z`, `case.height`, `top_structure.z_min_mm`/`z_max_mm`, `film_storage_horizontal.z`
from `Parameters`/`Datums`, so no geometry source code changes are expected beyond the
`computed_upper_z_mm` property above. If you find a hardcoded literal duplicating one of these
values while doing this work, fix it in place and say so in your report — do not leave it.

## 2. Required re-verification (zero intersection, all quantified)

### 2.1 Tier-2 under-tray hardware vs `EQUIP-PLOTTER1-001` — the defect itself

Add a new regression test (new function in `tests/test_geometry.py` or `tests/test_kinematics.py`,
your call — follow the existing `apply_tray_extension` pattern already used for tray-1 kinematics in
`src/stand_cad/geometry/kinematics.py`). For **every** pair in:

```
EQUIP-PLOTTER1-001  vs  FRAME-RAIL-TRAY-UPPER-L-001
EQUIP-PLOTTER1-001  vs  FRAME-RAIL-TRAY-UPPER-R-001
EQUIP-PLOTTER1-001  vs  FRAME-RAIL-TRAY-UPPER-C-001
EQUIP-PLOTTER1-001  vs  SLIDE-UPPER-LEFT-001
EQUIP-PLOTTER1-001  vs  SLIDE-UPPER-RIGHT-001
EQUIP-PLOTTER1-001  vs  SLIDE-UPPER-CENTER-001
EQUIP-PLOTTER1-001  vs  INTERLOCK-TAB-UPPER-001
```

at **every** tray-1 position in `{0, 65, 130, 180, 250}` mm (`apply_tray_extension(transport.parts,
lower_extension_mm=dy, upper_extension_mm=0.0)` moves `EQUIP-PLOTTER1-001`'s `LOWER_KINEMATIC_GROUP`
by `-dy` in Y; the `FRAME-RAIL-TRAY-UPPER-*`/`SLIDE-UPPER-*`/`INTERLOCK-TAB-UPPER-001` targets are
fixed, not in either kinematic group), assert `intersection_volume(...) == pytest.approx(0.0, abs=1e-3)`
and **also** print/record the actual Z-gap (`minimum_clearance(...)`, or compute
`bounding_box_bounds` min/max directly) in a way the adversarial reviewer and Main's Final Report can
cite — a bare pass/fail is not enough, Main's report needs a real clearance number at each position.
Do the exploratory arithmetic first (before writing the test) so you know what to expect: with the
corrected `upper_z`, the Z-band of `FRAME-RAIL-TRAY-UPPER-*`/`SLIDE-UPPER-*` no longer overlaps
`EQUIP-PLOTTER1-001`'s fixed Z=[30,200] band **at all**, regardless of Y position — if your
measurement shows the clearance changing with `dy`, that means the Z-bands still overlap and the fix
is wrong; stop and re-derive, don't paper over it with a wider tolerance.

### 2.2 Everything QA-cycle-2 already fixed — confirm it still holds, do not assume

- Film-shelf front-withdrawal vs `FRAME-POST-FL-001` (D-037): existing test
  `tests/test_geometry.py::test_film_body_front_withdrawal_clears_front_left_post` is fully
  parametric off `datums.organizer_clear_volume` — rerun it, it should still pass with the shifted Z
  band; confirm in your report, don't just assume green pytest is enough (per repo rule: a passing
  test is not evidence of physical correctness by itself, but it IS the required regression gate
  here — run it and read the actual numbers, don't just trust exit 0).
- Interlock (`INTERLOCK-SHUTTLE-001`/`INTERLOCK-TAB-{LOWER,UPPER}-001`) — rerun
  `tests/test_kinematics.py::test_interlock_shuttle_neutral_no_tray_interference`,
  `test_interlock_blocks_upper_tray_extension`, `test_interlock_blocks_lower_tray_extension`.
- Cable pass-through (D-036) — rerun `tests/test_geometry.py::test_cable_passthrough_through_cut`;
  it does not depend on `upper_z`/`case.height` but confirm, don't assume.
- Handle cutout (D-030) — `tests/test_geometry.py::test_handle_mount_z_side_panel_centred` **will**
  need its literal `263.0` updated to `276.5` (see §1 table) — this is an intentional, expected test
  update, not a regression; also check `test_handle_cutout_sightline_clear` (D-022) still passes
  with the shifted handle Z band [45+... actually recompute the exact Y/Z band from the new
  `handle_mount_z_mm`, do not carry forward the old `[245.5, 280.5]` Z band cited in
  `docs/10_USER_INPUT_REQUIRED.md` §E verbatim — recompute it from the new 276.5 mm centre and report
  the new band].

### 2.3 Light-strip near-miss (`docs/10_USER_INPUT_REQUIRED.md` §I) — investigate, fix only if trivial

Both `LIGHT-STRIP-001` (`src/stand_cad/geometry/services.py`, reads `top_structure.z_min_mm`) and
`FRAME-POST-RR-001` (`src/stand_cad/geometry/frame.py::build_frame_posts`, top at
`datums.top_structure.z.min_mm`) derive their shared Z-boundary from the same leaf, so this fix
shifts both by the same +27 mm and — verify this, don't assume — should leave the existing
`minimum_clearance(LIGHT-STRIP-001, FRAME-POST-RR-001)` **unchanged** at exactly 0.5 mm (measured
pre-fix baseline; recompute post-fix and confirm it's still 0.5 mm, not something else). If it is
still ≈0.5 mm: the overlap in the XY footprint is real — `FRAME-POST-RR-001` is an L-shaped post
(`leg_h` at X∈[610,650]×Y∈[535,550], `leg_v` at X∈[635,650]×Y∈[510,550]) and `LIGHT-STRIP-001`'s
current footprint (X∈[25,625], Y∈[532.5,544.5]) overlaps `leg_h`'s footprint in X∈[610,625]×Y∈[535,
544.5] — a genuine ~15×9.5 mm planform overlap, only cleared vertically by the 0.5 mm Z gap. Check
honestly whether a **1-2 mm** nudge (e.g. shifting the light strip's Y anchor in
`services.py` — it is currently pinned at `depth - gap - ls_w - outer_t`; find the actual gap/outer_t
values in context and see whether tightening or loosening that offset by 1-2 mm removes the XY
overlap or meaningfully grows the Z margin) gives real margin **without moving anything else**
(no other part reads `LIGHT-STRIP-001`'s position). If clearing the overlap fully requires more than
a millimetre or two (e.g. shortening `services.light_strip_length_mm`, which is a `to_measure`
provisional hardware dimension, not a free layout choice) — leave it exactly as documented in §I and
say so explicitly in your report; do not silently retune a `to_measure` hardware leaf to manufacture
margin.

## 3. Mass / stability / deflection — recompute, do not assume

Run `scripts/generate_mass_report.py` (writes `mass_report.csv`, calls `write_stability_report`,
`write_deflection_report` — see `write_all_reports()`) against the corrected parameters, into
`output/validation/rev9/`.

- **Deflection:** span (`plotter.physical_width`=570) and load (`trays.design_load_kg`=10 kg) are
  unchanged by this fix — `indicative_tray_deflection_mm()` should still read ≈0.228 mm. Confirm the
  number in the regenerated `deflection_report.md`, state it explicitly in your report; do not assume
  it is untouched just because the formula doesn't reference `upper_z`.
- **Mass:** side slabs / outer-rear panel / other full-height panels span `case.height`, so their
  area — and mass — **will** measurably increase with the +27 mm height (this is not merely
  "repositioned parts" for those specific panels; report the actual delta between rev8's last
  `mass_report.csv` and the new one, do not just assert "negligible"). Confirm the structural total
  stays inside `mass_targets.empty_case_target_min/max_kg` (9-11 kg) and the 12 kg ceiling with the
  real number.
- **Centre of mass:** `write_mass_report()`'s CoM figures (`com_empty`, `com_plot`, `com_ext`) will
  shift up in Z roughly proportional to the height increase (case got taller, same mass distribution
  shape) — report the new z-values from the regenerated `mass_report.csv` header comments (`# CoM ...`
  lines) and update the `hardware.handle_mount_z_mm` note's CoM commentary in
  `config/parameters.yaml` (currently cites `≈216.0 mm` loaded / `≈224.7 mm` empty from rev6/D-030) to
  the new figures — cite the new revision, not rev6.
- **Stability:** `stability_report.md` tip factors depend on mass and extension arms, not directly on
  `case.height` — confirm they stay ≥ `stability.tip_factor_min` (1.5) with the regenerated report;
  do not assume unaffected.

## 4. Tests

- Add the new zero-intersection regression test(s) from §2.1 (7 pairs × 5 positions = 35 assertions
  minimum; parametrize, don't hand-write 35 near-duplicate test functions).
- Update `tests/test_parameters.py::test_computed_case_height_matches_yaml` — literal `517.0` →
  `544.0` (both the `computed_case_height_mm` and `case.height` assertions).
- Add the `computed_upper_z_mm` consistency test from §1.
- Update `tests/test_geometry.py::test_handle_mount_z_side_panel_centred` — literal `263.0` → `276.5`.
- Search for any other literal reference to `211`, `396`, `502`, `517`, `263` tied to **real**
  `load_parameters(PARAMETERS_PATH)` fixtures (not the synthetic fixture doc in
  `test_parameters.py::_valid_doc`, which is self-consistent and independent of the real config — do
  **not** touch `_valid_doc()`) before declaring done — `grep` for these literals across `tests/`
  yourself, don't rely solely on this list.
- All 285 pre-existing tests must keep passing (accounting for the two intentional literal updates
  above) — do not delete or weaken coverage to make room.

## 5. Regeneration (rev9)

- Bump `CONCEPT_REVISION` in `src/stand_cad/geometry/export.py` from `8` to `9`.
- Run `uv run python scripts/regenerate.py` (drives STEP/STL/GLB/manifest + full view set into
  `output/validation/rev9/views/` per the existing pipeline — confirm which script(s) actually own
  this path, do not hand-roll a new one).
- Run `uv run python scripts/generate_mass_report.py` for `mass_report.csv` /
  `stability_report.md` / `deflection_report.md` under `output/validation/rev9/`.
- Keep `CONCEPT`/`REFERENCE_ONLY` markings in filenames; no PDF, no production DXF, no gate
  transitions, no push.

## 6. Documentation and state updates

- `docs/10_USER_INPUT_REQUIRED.md` §H: mark **RESOLVED** (not left as an open owner decision — Main
  is closing it under the standing autonomy grant, since growing height is the conservative,
  non-destructive option and touches no owner-fixed dimension). State: the new formula, `upper_z`=238,
  `case.height`=544, and the confirmed zero-intersection evidence at all 5 tray-1 positions from
  §2.1 (cite actual clearance numbers, not just "resolved"). Keep the original problem narrative as
  honest history — do not delete it, append the resolution.
- `docs/10_USER_INPUT_REQUIRED.md` §I: update with the post-fix `minimum_clearance` measurement
  (confirm still 0.5 mm or state the new number) and whether a reposition was applied (§2.3).
- `state/DECISION_LOG.md`: new entry, e.g. `D-038`, dated **2026-08-04**, attributed to **Main**
  under the owner's standing autonomy grant for this session — cite the corrected formula, the old
  vs new `upper_z`/`case.height`, the F-5 evidence this closes, and cross-reference D-030 (handle Z
  formula unchanged, computed value updated 263→276.5) and D-034 (this supersedes/closes the F-5
  follow-up recorded there).
- `state/PROJECT_STATE.md`: record the new phase/revision (rev9), close out F-5, note the light-strip
  §I outcome, new test count.
- `state/REQUIREMENTS_TRACEABILITY.csv`: update the `PLT-019` row (handle Z — new computed value,
  new evidence path) and add/update a row for the F-5 tier-2 clearance fix if one does not already
  exist (check first; PLT-021 is the tray-1 quick-access row, not F-5 — do not overwrite it).
- Everything on disk stays in English per repository convention.

## Verification (all must pass, exit 0)

- `uv run pytest`
- `uv run ruff check .`
- `powershell -ExecutionPolicy Bypass -File .\scripts\setup_windows.ps1`
- Mandatory `adversarial-reviewer`: independently recompute the intersection volumes at every pair ×
  position in §2.1 (do not trust the implementer's numbers — re-run the actual `intersection_volume`
  calls yourself against the regenerated geometry); check §2.2 fixes still hold with real numbers;
  check the light-strip §2.3 decision is honestly justified either way; check no `to_measure` leaf
  was silently retuned; check mass/CoM/deflection figures were actually regenerated, not hand-typed.

Local commit expected at the end of a clean cycle; no push.
