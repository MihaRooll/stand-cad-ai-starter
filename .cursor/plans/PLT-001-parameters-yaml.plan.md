# Plan: PLT parameters.yaml, loader, validation, traceability, docs realignment

Tier: T2 (physical-quantity change per `.cursor/rules/21-orchestration-overlay.mdc` tier floors; no
geometry/STEP/DXF/PDF export in this stage, so not T3). Adversarial review is mandatory at T2 in this
repository. Owner: `operational-orchestrator` (this plan) -> `implementer` (sole writer) -> `adversarial-reviewer`
-> `verifier`.

Source of truth for all values below: `ИИ советы/Cursor_Opus5_TZ_Light_Plotter_Tower.md` ("TZ"). Do not invent
any number not present in the TZ. Every leaf in `config/parameters.yaml` must carry a `provenance` marker,
exactly one of `verified` / `derived` / `to_measure`.

## Deliverable 1 — `config/parameters.yaml`

Create this exact file (2-space indent, LF line endings). Each leaf is a mapping `{value, provenance, note}`.
`note` cites the TZ section supporting the value. Two quantities are intentionally **not** stored as leaves —
`film_storage.cell_width_mm` and `film_storage.divider_count` — because they must be computed from `cells`,
`case.internal_width`, and `divider_thickness` at load time (see Deliverable 2); storing them here would be a
hardcoded derived value.

```yaml
# config/parameters.yaml
#
# Single dimensional source of truth for the Light Plotter Tower, per
# "ИИ советы/Cursor_Opus5_TZ_Light_Plotter_Tower.md" ("TZ"), section 12.
# This supersedes the earlier "mobile floor stand" framing (see docs/adr/ADR-005-*).
#
# Every leaf is a mapping {value, provenance, note}. provenance is exactly one of:
#   verified   - manufacturer documentation or the owner's fixed decision recorded in the TZ.
#   derived    - computed from verified values; the formula lives in src/stand_cad/parameters.py
#                docstrings/comments, never re-hardcoded here.
#   to_measure - must be measured on the real machine/material before production release.
# src/stand_cad/parameters.py fails closed if a leaf lacks a valid provenance marker.
#
# film_storage.cell_width_mm and film_storage.divider_count are NOT stored here: they are
# derived from case.internal_width, film_storage.cells, and film_storage.divider_thickness at
# load time (Parameters.cell_width_mm / Parameters.divider_count) so changing `cells` (valid
# range 6-12, TZ line 108) never leaves a stale hardcoded width or count behind.

schema_version: 1
units: mm

case:
  width: {value: 650, provenance: verified, note: "TZ section 4 — overall envelope"}
  depth: {value: 550, provenance: verified, note: "TZ section 4 — overall envelope"}
  height: {value: 690, provenance: verified, note: "TZ section 4 — overall envelope"}
  internal_width: {value: 610, provenance: verified, note: "TZ section 4 — plotter niche / organizer clear width"}
  corner_radius: {value: 25, provenance: verified, note: "TZ section 12 default within the R20-R30 visual range of TZ section 8"}

# EXTENSION beyond the TZ section 12 base block; source: TZ section 15.
tolerance:
  assembly_mm: {value: 1, provenance: verified, note: "TZ section 15 — overall assembly tolerance"}
  part_cnc_laser_mm: {value: 0.3, provenance: verified, note: "TZ section 15 — CNC/laser part tolerance unless stated otherwise"}
  part_assembly_feature_mm: {value: 0.5, provenance: verified, note: "TZ section 15 — assembly-feature tolerance unless stated otherwise"}

plotter:
  physical_width: {value: 566, provenance: verified, note: "TZ section 3 — Silhouette Cameo 5 manufacturer dimension"}
  physical_depth: {value: 176, provenance: verified, note: "TZ section 3"}
  physical_height: {value: 124, provenance: verified, note: "TZ section 3"}
  design_width: {value: 580, provenance: verified, note: "TZ section 4/5 — protective design envelope"}
  design_depth: {value: 200, provenance: verified, note: "TZ section 4/5"}
  design_height: {value: 132, provenance: verified, note: "TZ section 4/5"}
  design_mass_kg: {value: 5.2, provenance: verified, note: "TZ section 3 — conservative mass; 5.05 kg is reference-only"}
  x: {value: 42, provenance: verified, note: "TZ section 5 — coordinate table"}
  lower_y: {value: 20, provenance: verified, note: "TZ section 5"}
  lower_z: {value: 30, provenance: verified, note: "TZ section 5"}
  upper_y: {value: 170, provenance: verified, note: "TZ section 5"}
  upper_z: {value: 190, provenance: verified, note: "TZ section 5"}
  upper_setback: {value: 150, provenance: verified, note: "TZ section 2/5 — plotter 2 set back exactly 150 mm; must equal upper_y - lower_y"}
  feed_plane_z_from_base: {value: "TO_MEASURE", provenance: to_measure, note: "TZ section 7 and section 16 item 1 — must not be guessed"}

# EXTENSION beyond the TZ section 12 base block; source: TZ section 7.
trays:
  lower_extension: {value: 250, provenance: verified, note: "TZ section 7 — minimum full extension, lower tray"}
  upper_extension: {value: 400, provenance: verified, note: "TZ section 7 — minimum full extension, upper tray"}
  rated_load_kg: {value: 15, provenance: verified, note: "TZ section 7 — minimum slide rating per pair"}
  rated_load_preferred_kg: {value: 20, provenance: verified, note: "TZ section 7 — preferred slide rating per pair"}
  design_load_kg: {value: 10, provenance: verified, note: "TZ section 7 — design load per tray"}
  front_overhang_min_mm: {value: 40, provenance: verified, note: "TZ section 7 — minimum protrusion past the front face in service position"}
  deflection_max_mm: {value: 1.5, provenance: verified, note: "TZ section 7 and 17 — max deflection under design_load_kg"}

film_storage:
  x: {value: 20, provenance: verified, note: "TZ section 5"}
  y: {value: 20, provenance: verified, note: "TZ section 5"}
  z: {value: 350, provenance: verified, note: "TZ section 5"}
  clear_width: {value: 610, provenance: verified, note: "TZ section 4/6 — organizer clear width"}
  clear_depth: {value: 510, provenance: verified, note: "TZ section 4/6 — target cell depth; TZ section 6 minimum is 505"}
  clear_depth_min: {value: 505, provenance: verified, note: "TZ section 6 — minimum usable cell depth"}
  clear_height: {value: 325, provenance: verified, note: "TZ section 4/6"}
  film_design_height: {value: 320, provenance: verified, note: "TZ section 2/6 — design vertical envelope of one sheet"}
  film_depth: {value: 500, provenance: verified, note: "TZ section 2/6 — nominal sheet depth"}
  cells: {value: 10, provenance: verified, note: "TZ section 4 — nominal default cell count; valid range 6-12 per TZ line 108"}
  divider_thickness: {value: 2, provenance: verified, note: "TZ section 4/6/8"}
  divider_height_min: {value: 300, provenance: verified, note: "TZ section 6"}
  divider_height_max: {value: 315, provenance: verified, note: "TZ section 6"}
  divider_depth: {value: 505, provenance: verified, note: "TZ section 6"}
  front_retainer_height_min: {value: 40, provenance: verified, note: "TZ section 6"}
  front_retainer_height_max: {value: 50, provenance: verified, note: "TZ section 6"}
  finger_cutout_radius_min: {value: 25, provenance: verified, note: "TZ section 6"}
  finger_cutout_radius_max: {value: 35, provenance: verified, note: "TZ section 6"}
  floor_design_load_kg: {value: 15, provenance: verified, note: "TZ section 6 — uniform design load on the organizer floor"}
  max_load_kg: {value: 10, provenance: verified, note: "TZ section 6/11 — marked operating limit"}
  min_stack_width_mm: {value: "TO_MEASURE", provenance: to_measure, note: "TZ section 16 item 7 — real film thickness/stiffness not yet measured"}

# EXTENSION beyond the TZ section 12 base block; source: TZ section 7.
media_path:
  clear_width: {value: 330, provenance: verified, note: "TZ section 7 — minimum clear width"}
  clear_height_min: {value: 12, provenance: verified, note: "TZ section 7 — minimum clear slot height"}
  slot_height_target: {value: 18, provenance: verified, note: "TZ section 7 — target slot height with soft brush"}
  primary_length: {value: 500, provenance: verified, note: "TZ section 7 (matches film_storage.film_depth)"}
  long_mat_length: {value: 610, provenance: verified, note: "TZ section 7"}
  test_body_primary:
    height: {value: 320, provenance: verified, note: "TZ section 7 — primary test sheet 320x500x3"}
    depth: {value: 500, provenance: verified, note: "TZ section 7"}
    thickness: {value: 3, provenance: verified, note: "TZ section 7"}
  test_body_long:
    height: {value: 305, provenance: verified, note: "TZ section 7 — long mat/material 305x610x3"}
    depth: {value: 610, provenance: verified, note: "TZ section 7"}
    thickness: {value: 3, provenance: verified, note: "TZ section 7"}

# EXTENSION beyond the TZ section 12 base block; source: TZ section 8.
materials:
  frame_profile_size_mm: {value: 15, provenance: verified, note: "TZ section 8 — aluminium profile/angle 15x15x1.5"}
  frame_wall_thickness_mm: {value: 1.5, provenance: verified, note: "TZ section 8"}
  outer_panel_thickness_mm: {value: 3, provenance: verified, note: "TZ section 8 — cast opal white PMMA"}
  impact_panel_thickness_min_mm: {value: 3, provenance: verified, note: "TZ section 8 — impact-loaded inner panels"}
  impact_panel_thickness_max_mm: {value: 4, provenance: verified, note: "TZ section 8"}
  tray_panel_thickness_min_mm: {value: 10, provenance: verified, note: "TZ section 8 — tray sandwich/aluminium honeycomb panel"}
  tray_panel_thickness_max_mm: {value: 12, provenance: verified, note: "TZ section 8"}
  organizer_floor_thickness_min_mm: {value: 10, provenance: verified, note: "TZ section 8"}
  organizer_floor_thickness_max_mm: {value: 12, provenance: verified, note: "TZ section 8"}
  divider_thickness_mm: {value: 2, provenance: verified, note: "TZ section 8 (matches film_storage.divider_thickness)"}
  foot_height_min_mm: {value: 8, provenance: verified, note: "TZ section 8"}
  foot_height_max_mm: {value: 10, provenance: verified, note: "TZ section 8"}
  actual_sheet_thickness_mm: {value: "TO_MEASURE", provenance: to_measure, note: "TZ section 16 item 8 — measure after purchase, before cutting joints"}

lighting:
  voltage_v: {value: 24, provenance: verified, note: "TZ section 9"}
  max_power_w: {value: 40, provenance: verified, note: "TZ section 9 — maximum electrical power of the lighting"}

# EXTENSION beyond the TZ section 12 base block; source: TZ section 10.
thermal:
  adapter_bay_max_temp_c: {value: 40, provenance: verified, note: "TZ section 10 — after 2 h at 25 C ambient"}
  film_bay_max_temp_rise_k: {value: 10, provenance: verified, note: "TZ section 10"}
  ambient_test_temp_c: {value: 25, provenance: verified, note: "TZ section 10"}
  test_duration_hours: {value: 2, provenance: verified, note: "TZ section 10"}

# EXTENSION beyond the TZ section 12 base block; source: TZ section 7/17.
stability:
  tip_factor_min: {value: 1.5, provenance: verified, note: "TZ section 7 and 17 — minimum tip-over safety factor"}

mass_targets:
  empty_case_max_kg: {value: 12, provenance: verified, note: "TZ section 8 and 17 — hard ceiling"}
  empty_case_target_min_kg: {value: 9, provenance: verified, note: "TZ section 8 — target range"}
  empty_case_target_max_kg: {value: 11, provenance: verified, note: "TZ section 8 — target range"}
  case_with_plotters_no_film_min_kg: {value: 20, provenance: verified, note: "TZ section 8 — approximate"}
  case_with_plotters_no_film_max_kg: {value: 23, provenance: verified, note: "TZ section 8 — approximate"}
  operating_total_max_kg: {value: 33, provenance: verified, note: "TZ section 8 — maximum operating mass with film"}
  film_marked_limit_kg: {value: 10, provenance: verified, note: "TZ section 11 (matches film_storage.max_load_kg)"}
```

## Deliverable 2 — `src/stand_cad/parameters.py` (new module)

No CAD dependency, matching `schema.py`. Reuse `ValidationIssue` from `schema.py`. Add `pyyaml` with
`uv add pyyaml` before writing this module (authorised lockfile change).

Required public surface:

- `Parameter` frozen dataclass: `path: str`, `value: Any`, `provenance: str`, `note: str = ""`.
- `PROVENANCE_VALUES = {"verified", "derived", "to_measure"}`.
- `Parameters` class wrapping the raw loaded dict:
  - Walks a fixed tuple of top-level groups (`case`, `tolerance`, `plotter`, `trays`, `film_storage`,
    `media_path`, `materials`, `lighting`, `thermal`, `stability`, `mass_targets`) — **not** `schema_version`/
    `units`, which are config metadata, not physical parameters — recursively collecting every leaf
    (a dict containing both `value` and `provenance` keys) into a dotted-path map, e.g. `"case.width"`,
    `"media_path.test_body_primary.height"`.
  - A node that is a dict but does NOT have both `value` and `provenance` keys must still surface as a
    malformed leaf (empty/invalid provenance) rather than being silently skipped, so `validate_parameters`
    can flag it via `PARAM-001`.
  - `.leaves() -> list[Parameter]`, `.get(path) -> Parameter` (raise `KeyError` with the path on miss),
    `.value(path) -> Any` convenience wrapper.
  - `cell_width_mm` property: `(case.internal_width - (film_storage.cells - 1) * film_storage.divider_thickness) / film_storage.cells`. Must yield `59.2` for the default config.
  - `divider_count` property: `int(film_storage.cells) - 1`. Must yield `9` for the default config.
- `load_parameters(path) -> Parameters`: read UTF-8, `yaml.safe_load`, raise `ValueError` if the top-level
  document is not a mapping.
- `validate_parameters(params: Parameters, *, production_release: bool = False) -> list[ValidationIssue]`,
  fail-closed, all issues collected in one pass, using these stable codes (new `PARAM-` family plus one
  `REL-027` continuing the existing `REL-` family from `schema.py`):
  - `PARAM-001` — any leaf whose `provenance` is not in `PROVENANCE_VALUES` (missing, empty, or a value
    outside the three markers).
  - `PARAM-002` — `film_storage.cells` is not an int in `[6, 12]`.
  - `PARAM-003` — `cell_width_mm` is below the 25 mm absolute floor.
  - `PARAM-004` — `cell_width_mm` is below `film_storage.min_stack_width_mm` **only when that leaf's value
    is numeric** (skip the check while it is still the `"TO_MEASURE"` sentinel — do not invent a number to
    compare against).
  - `PARAM-005` — any of `film_storage.clear_width < 610`, `clear_depth < 510`, `clear_height < 325`
    (organizer clear volume smaller than required; equality passes).
  - `PARAM-006` — `(case.width, case.depth, case.height) != (650, 550, 690)` (envelope must match exactly,
    not just be no-smaller).
  - `PARAM-007` — `plotter.upper_setback != 150`.
  - `PARAM-008` — `plotter.upper_setback != plotter.upper_y - plotter.lower_y` (internal consistency between
    the three coordinate fields; defends against future edits silently drifting the fixed 150 mm offset).
  - `PARAM-009` — `film_storage.clear_height - film_storage.film_design_height < 5` (insufficient headroom,
    TZ line 153; exactly 5 mm passes).
  - `REL-027` — only when `production_release=True`: one issue per leaf whose `provenance == "to_measure"`
    (reuses the `schema.py` `REL-` family and its fail-closed philosophy; since no geometry exists yet in
    this stage there is no per-artifact consumption graph to scope this to, so it conservatively covers the
    whole parameter set — note this as a follow-up narrowing item once geometry consumes specific leaves).
- Update `src/stand_cad/__init__.py` to also export `Parameter`, `Parameters`, `load_parameters`,
  `validate_parameters`.

## Deliverable 2b — `pyproject.toml`

Run `uv add pyyaml` (adds `pyyaml` to `[project] dependencies` and updates `uv.lock`). Do not hand-edit the
lockfile.

## Deliverable 2c — tests: `tests/test_parameters.py` (new file)

Cover every rule above in both directions. Suggested structure — a `_valid_doc()` builder returning a
minimal-but-complete nested dict (plain Python dicts, not loaded from YAML) covering `case`, `plotter`,
`film_storage` groups with passing values, then per-test `deepcopy` + mutate one leaf:

- `test_repository_parameters_yaml_loads_and_validates_clean` — `load_parameters("config/parameters.yaml")`,
  `validate_parameters(params)` (production_release=False) has zero ERROR issues.
- `test_default_cell_width_matches_expected` — `cell_width_mm == pytest.approx(59.2)`.
- `test_default_divider_count_matches_expected` — `divider_count == 9`.
- `test_missing_provenance_marker_fails` / `test_invalid_provenance_value_fails` — both produce `PARAM-001`.
- `test_cells_below_range_fails` (5), `test_cells_above_range_fails` (13), `test_cells_at_range_boundaries_pass`
  (6 and 12) — `PARAM-002`.
- `test_cell_width_below_absolute_floor_fails` (force `cells`/`divider_thickness`/`internal_width` so
  `cell_width_mm < 25`) — `PARAM-003`.
- `test_cell_width_below_required_film_stack_fails` (numeric `min_stack_width_mm` above the computed
  `cell_width_mm`) and `test_cell_width_stack_check_skipped_while_to_measure` (sentinel value, no `PARAM-004`)
  — `PARAM-004`.
- `test_organizer_clear_volume_below_minimum_fails` (one test per dimension) and
  `test_organizer_clear_volume_at_minimum_passes` (exactly 610x510x325) — `PARAM-005`.
- `test_overall_envelope_mismatch_fails` and `test_overall_envelope_match_passes` — `PARAM-006`.
- `test_plotter_setback_not_150_fails` and `test_plotter_setback_150_passes` — `PARAM-007`.
- `test_plotter_setback_inconsistent_with_coordinates_fails` — `PARAM-008`.
- `test_film_headroom_below_5mm_fails` and `test_film_headroom_exactly_5mm_passes` — `PARAM-009`.
- `test_production_release_blocks_on_to_measure_parameters` — using the real repository config (which has
  exactly three `to_measure` leaves: `plotter.feed_plane_z_from_base`, `film_storage.min_stack_width_mm`,
  `materials.actual_sheet_thickness_mm`), `validate_parameters(params, production_release=True)` yields
  exactly 3 `REL-027` issues, one per those paths.
- `test_production_release_passes_with_no_to_measure_parameters` — an all-`verified`/`derived` doc produces
  zero `REL-027` issues under `production_release=True`.

All 9 pre-existing tests in `tests/test_schema.py` must keep passing unmodified.

## Deliverable 3 — `state/REQUIREMENTS_TRACEABILITY.csv`

Append 17 new rows, `PLT-001`..`PLT-017`, one per TZ section 17 acceptance-criterion bullet (lines 499-515,
in order). Do not delete or reorder existing rows. Keep the file rectangular (exactly 10 fields per row,
quote any field containing a comma) — `tests/test_schema.py::test_traceability_csv_is_rectangular_and_has_expected_columns`
enforces this. All 17 rows: `status=OPEN` (nothing is satisfied yet — no geometry exists), `revision=DRAFT`,
`owner=IMPLEMENTER`, `source` cites the exact TZ file path and line number.

| id | summary (English) | source line | design_element | verification (intended) |
|---|---|---|---|---|
| PLT-001 | Overall case envelope is 650 x 550 x 690 mm | TZ:499 | `config/parameters.yaml` (`case.width/depth/height`) | CAD bounding-box measurement; parameter target enforced now by `PARAM-006` |
| PLT-002 | Both plotters have physical envelope 566 x 176 x 124 mm | TZ:500 | `config/parameters.yaml` (`plotter.physical_*`) | CAD bounding-box measurement against `plotter.physical_*` |
| PLT-003 | Plotter 2 is set back exactly 150 mm from plotter 1 | TZ:501 | `config/parameters.yaml` (`plotter.upper_setback`) | Parameter validation now (`PARAM-007`/`PARAM-008`); CAD placement measurement pending |
| PLT-004 | Internal film organizer clear volume is at least 610 x 510 x 325 mm | TZ:502 | `config/parameters.yaml` (`film_storage.clear_*`) | Parameter validation now (`PARAM-005`); CAD measurement pending |
| PLT-005 | The 320 x 500 mm vertical film test envelope stands vertically and does not intersect the case | TZ:503 | "" | CAD collision check against the film test envelope |
| PLT-006 | Default configuration creates 10 vertical cells about 59.2 mm wide | TZ:504 | `config/parameters.yaml` (`film_storage.cells`); `src/stand_cad/parameters.py` (`Parameters.cell_width_mm`) | Unit test asserts derived `cell_width_mm` for `cells=10` (`tests/test_parameters.py`) |
| PLT-007 | Both material test bodies pass through both levels without collisions | TZ:505 | "" | CAD collision check in multiple Y positions |
| PLT-008 | Each plotter's lid fully opens in the service position | TZ:506 | "" | CAD collision/clearance check in service state |
| PLT-009 | Both trays cannot be fully extended at the same time (mechanical interlock) | TZ:507 | "" | CAD mechanism/interference check |
| PLT-010 | Tip-over stability factor is at least 1.5 | TZ:508 | `config/parameters.yaml` (`stability.tip_factor_min`) | Stability calculation with worst-case extended tray |
| PLT-011 | Each tray's deflection under the 10 kg design load is at most 1.5 mm | TZ:509 | `config/parameters.yaml` (`trays.design_load_kg`, `trays.deflection_max_mm`) | Analytical deflection check or FEA |
| PLT-012 | Calculated empty-case mass is at most 12 kg | TZ:510 | `config/parameters.yaml` (`mass_targets.empty_case_max_kg`) | CAD mass computation from material densities |
| PLT-013 | Case has one external mains inlet and contains no laptop or router | TZ:511 | "" | Design/BOM review |
| PLT-014 | Lighting is uniform white-case RGBW illumination, not a display | TZ:512 | `config/parameters.yaml` (`lighting.*`) | Visual/photometric review of light sample panel |
| PLT-015 | FCStd/STEP/DXF/PDF/BOM files and check reports are produced (see ADR-005 mapping: STEP/DXF/PDF/BOM/reports under `output/`) | TZ:513 | "" | Export validation (`inspect_drawing`, STEP/DXF read-back) |
| PLT-016 | Model rebuilds from the parameter file without manual geometry edits | TZ:514 | `config/parameters.yaml`; `src/stand_cad/parameters.py` | Regenerate from `config/parameters.yaml` and diff output |
| PLT-017 | All unmeasured real-world dimensions are explicitly marked, never invented | TZ:515 | `config/parameters.yaml` (`to_measure` leaves); `src/stand_cad/parameters.py` (`PARAM-001`, `REL-027`) | Unit tests assert provenance markers and production-release blocking (`tests/test_parameters.py`) |

`notes` column for every PLT row: `"Parameter/config layer only in this stage; no geometry yet, see ADR-005"`.

## Deliverable 4 — documentation realignment

### `docs/adr/ADR-005-TZ-STACK-AND-LAYOUT.md` (new)

Status Accepted, dated 2026-08-03, formatted like the existing ADRs (`docs/adr/ADR-001-CAD-STACK.md` etc.).
Content:

- Context: the TZ (`ИИ советы/Cursor_Opus5_TZ_Light_Plotter_Tower.md`) supersedes the earlier mobile-floor-stand
  framing; TZ section 13 prefers FreeCAD+TechDraw but explicitly permits a CadQuery-family B-Rep alternative
  with STEP/DXF/PDF export; TZ section 14 proposes a `plotter_tower/` file tree.
- Decision 1: master model stays `build123d` (not FreeCAD) — same OCCT kernel as the CadQuery-family
  alternative TZ permits, already pinned in `pyproject.toml` and mandated by ADR-001/ADR-002,
  `build123d-mcp` already connected in-session; switching now discards a working toolchain for no
  geometric benefit.
- Decision 2: repository layout wins over the TZ section 14 tree — do not create `plotter_tower/`; generators
  stay under `src/stand_cad/`, scripts under `scripts/`, generated artifacts under `output/` (git-ignored,
  ADR-002). Include a mapping table, TZ section 14 path -> repository equivalent, covering: `README.md`/
  `STATUS.md` -> `README.md`/`state/PROJECT_STATE.md`; `parameters.yaml` -> `config/parameters.yaml`;
  `measurements_to_verify.md` -> `docs/10_USER_INPUT_REQUIRED.md`; `BOM.csv`/`mass_report.csv` ->
  `output/<revision>/BOM.csv` / `mass_report.csv`; `generate_model.py` -> a future `scripts/generate_model.py`;
  `cad/*.FCStd/.step` -> `output/<revision>/cad/` (STEP only, no `.FCStd`); `drawings/*.pdf` ->
  `output/<revision>/drawings/`; `dxf/**` -> `output/<revision>/dxf/**` (same acrylic/structural_panels/
  dividers/test_coupons split); `renders/*.png` and `checks/*.md` -> `output/validation/<revision>/` per
  `AGENTS.md`'s CAD workflow.
- Consequences: no `.FCStd` will ever exist; every future geometry stage resolves dimensions from
  `config/parameters.yaml` / `src/stand_cad/parameters.py`, never hand-duplicating a TZ number; `output/`
  gains the `cad/`/`drawings/`/`dxf/`/`checks/` subfolder convention.

### `docs/10_USER_INPUT_REQUIRED.md` (full rewrite)

Replace the entire file. Remove every item the TZ already answers (equipment selection, scenario, appearance,
layout, dimensions — sections A-E of the old file). Keep only:

1. A short intro noting the TZ answered most prior open questions.
2. Section "A" — the 8 physical measurements from TZ section 16, lines 482-489, verbatim-translated, each
   cross-referenced to the `to_measure` parameter it unblocks where one exists:
   1. Feed-plane height above the machine's lower support plane (`plotter.feed_plane_z_from_base`).
   2. Rear material exit coordinates.
   3. Real open-lid envelope and hinge position.
   4. Power and USB connector coordinates.
   5. OEM power adapter dimensions and minimum cable bend radius.
   6. Plotter foot positions and drill-free fixing points.
   7. Real thickness and stiffness of the films actually used (`film_storage.min_stack_width_mm`).
   8. Actual thickness of all purchased sheet materials (`materials.actual_sheet_thickness_mm`).
   Instruction line: after measuring, update `config/parameters.yaml`, regenerate, repeat collision checks,
   only then remove `VERIFY ON REAL MACHINE` markings (TZ section 16 closing paragraph).
3. A short section "B" noting manufacturer DFM authorization remains open and untouched by the TZ, per
   ADR-003 / `docs/05_IMPLEMENTATION_PLAN.md` (G5) — one or two lines, not the old file's full Section F.

### `state/PROJECT_STATE.md`

- Change the `Project:` line to reflect the new product: light desktop tower for two Silhouette Cameo 5 plus
  vertical film organizer, 650 x 550 x 690 mm (cite ADR-005 and the TZ file).
- Add a new `## Product pivot (2026-08-03)` section summarizing: TZ supersedes the old framing; `config/parameters.yaml`
  and `src/stand_cad/parameters.py` now exist as the parameter layer; no geometry yet; G1 equipment data is
  now supplied for the Cameo 5 by TZ section 3 (record this explicitly), though G1 itself is still an
  unconfirmed Human Gate.
- Trim `## Current blockers` — remove items TZ answers (exact equipment model, quantity is now 2x Cameo 5,
  general scenario); keep/rephrase to point at the rewritten `docs/10_USER_INPUT_REQUIRED.md` (8 measurements
  + manufacturer DFM authorization).
- Do not mark any gate passed.

### `state/DECISION_LOG.md`

Append rows (next IDs D-011.. continuing the existing table), each with Date 2026-08-03:

- D-011: Adopt the Light Plotter Tower TZ as the authoritative requirement source, superseding the mobile
  floor stand framing. Reason: owner supplied a complete, dimensioned TZ. Evidence:
  `ИИ советы/Cursor_Opus5_TZ_Light_Plotter_Tower.md`; ADR-005. Status: Accepted.
- D-012: Keep `build123d` as master model instead of switching to FreeCAD. Reason: TZ section 13 permits the
  CadQuery-family alternative; `build123d` already pinned and working in-session. Evidence: ADR-001, ADR-005.
  Status: Accepted.
- D-013: Keep the existing repository layout instead of the TZ section 14 `plotter_tower/` tree. Reason:
  ADR-002 already governs source-of-truth location; TZ deliverable names mapped in ADR-005. Evidence:
  ADR-002, ADR-005. Status: Accepted.
- D-014: Adopt `config/parameters.yaml` as the single dimensional source of truth per TZ section 12. Reason:
  prevents hand-duplicated dimensions across future geometry code. Evidence: `config/parameters.yaml`,
  `src/stand_cad/parameters.py`. Status: Accepted.

### `state/ASSUMPTIONS.md`

Append rows (next IDs A-008..):

- A-008: `plotter.feed_plane_z_from_base` (and any future visualisation-only provisional value) remains
  `TO_MEASURE` until measured on a real Cameo 5. Impact if wrong: production media-path drawings/DXF would be
  wrong. Validation action: measure on two real units per TZ section 16 item 1. Must resolve by: before
  production DXF release (G6). Status: Open.
- A-009: `film_storage.min_stack_width_mm` remains `TO_MEASURE` until real film thickness/stiffness is
  measured. Impact if wrong: organizer cell width could be undersized or oversized for the actual film stock.
  Validation action: measure per TZ section 16 item 7. Must resolve by: before production DXF release (G6).
  Status: Open.
- A-010: `materials.actual_sheet_thickness_mm` remains `TO_MEASURE` until sheet materials are purchased and
  measured. Impact if wrong: fitted-slot joints built to nominal thickness could bind or rattle. Validation
  action: measure after purchase per TZ section 16 item 8; TZ section 15 requires joints built from measured,
  not nominal, thickness. Must resolve by: before cutting joints / production DXF release (G6). Status: Open.

## Verification commands (must all exit 0 before reporting)

```bash
uv add pyyaml
uv run pytest
uv run ruff check .
```

## Adversarial review checklist (hunt specifically for)

1. Any numeric dimension duplicated outside `config/parameters.yaml` (e.g. re-typed into a docstring, a
   test's expected value that isn't independently justified, or a doc that repeats a number instead of
   citing the parameter path).
2. Any leaf in `config/parameters.yaml` missing a `provenance` key or using a marker outside the three
   allowed values.
3. Any derived value (`cell_width_mm`, `divider_count`) hardcoded as a YAML leaf instead of computed.
4. Any code path where a `to_measure` value could reach a "production-ready" claim without tripping
   `REL-027` — check that `validate_parameters(..., production_release=True)` is actually exercised by a
   test using the real repository config, not only a synthetic doc.

Fix findings, then re-run the verification commands. Cap 3 cycles; an open finding after cycle 3 is BLOCKED,
not done.

## Forbidden in this stage

No geometry code, no STEP/DXF/PDF output, no gate marked passed, no invented dimension, no `git push`.

## Cycle 1 adversarial review fixes (mandatory before verification)

The adversarial reviewer returned `rework` after cycle 1. Apply these fixes to
`src/stand_cad/parameters.py`, `src/stand_cad/schema.py`, and `src/stand_cad/__init__.py`:

1. **F-1 (blocker)** — `validate_documents()` in `schema.py` has no visibility into
   `config/parameters.yaml`, so a caller that treats `validate_documents(..., production_release
   implied by project.production_release=True)` alone as "cleared for release" would never see
   `REL-027` even though 3 `to_measure` leaves exist. Add a new combined gate function
   `validate_release_readiness(project_doc, equipment_doc, params, *, allow_demo=False) ->
   list[ValidationIssue]` to `src/stand_cad/parameters.py` (it already imports from `.schema`,
   so this is the right module) that: reads `production_release = bool(project_doc.get("project",
   {}).get("production_release", False))`, calls `validate_documents(project_doc, equipment_doc,
   allow_demo=allow_demo)`, calls `validate_parameters(params, production_release=production_release)`,
   and returns the concatenation. Export it from `src/stand_cad/__init__.py`. Add a one-line
   docstring note above `validate_documents` in `schema.py` (comment only, no behavior change)
   stating that once `config/parameters.yaml` exists, `stand_cad.parameters.validate_release_readiness`
   is the authoritative combined production gate, not `validate_documents` alone. Add a test in
   `tests/test_parameters.py` proving `validate_release_readiness` surfaces `REL-027` when
   `project.production_release=True` against the real repository config, and surfaces zero errors
   for a fully clean synthetic doc (all `verified`/`derived`, no `to_measure`).
2. **F-2 (should-fix)** — Extract the magic-number acceptance thresholds in `validate_parameters`
   (`25`, `610`/`510`/`325`, `(650, 550, 690)`, `150`, `5`) into named module-level constants with
   a comment citing the TZ line/section each came from (e.g. `CELL_WIDTH_ABSOLUTE_FLOOR_MM = 25`,
   `REQUIRED_CASE_ENVELOPE_MM = (650, 550, 690)  # TZ section 4`,
   `ORGANIZER_CLEAR_MIN_MM = (610, 510, 325)  # TZ section 4/6, width/depth/height`,
   `REQUIRED_UPPER_SETBACK_MM = 150  # TZ section 2/5`, `FILM_HEADROOM_MIN_MM = 5  # TZ line 153`).
   These are acceptance-criteria thresholds from the TZ, not config values, so they are correctly
   code constants, not YAML — just make them named and cited instead of inline literals.
3. **F-3a (should-fix, docstring accuracy)** — The module docstring says derived quantities are
   "computed at load time"; they are actually lazy `@property` accessors evaluated on each access.
   Reword to something accurate, e.g. "computed on access from verified leaves ... — never stored
   as hardcoded YAML values."
4. **F-3b (should-fix, real correctness bug)** — `Parameters._walk` silently `continue`s past any
   node that is not a `dict` (a bare scalar leaf), so a malformed leaf like `case.width: 650`
   (missing the `{value, provenance}` wrapper) is dropped entirely instead of being surfaced as a
   `PARAM-001` finding, and a later `params.value(...)` call on that path raises an unhandled
   `KeyError` instead of `validate_parameters` returning a clean issue list (violates the fail-closed,
   collect-all-issues-in-one-pass contract). Fix `_walk` so any node that is not a well-formed
   `{value, provenance, ...}` mapping (including bare scalars) is still registered as a `Parameter`
   with `provenance=""` (or the malformed value's own `provenance` if partially present) so
   `PARAM-001` catches it. Add a test constructing a doc with a bare-scalar leaf and asserting
   `validate_parameters` returns a `PARAM-001` issue instead of raising.
5. **F-4 (should-fix)** — Two physical quantities are each stored as two independent `verified`
   leaves in `config/parameters.yaml` with no cross-check: `film_storage.divider_thickness` vs.
   `materials.divider_thickness_mm` (both `2`), and `film_storage.max_load_kg` vs.
   `mass_targets.film_marked_limit_kg` (both `10`). Add two new validation codes to
   `validate_parameters` — `PARAM-010` (divider thickness cross-check) and `PARAM-011` (film marked
   load-limit cross-check) — each an `ERROR` if the pair differs, following the same pattern as the
   existing `PARAM-008` upper-setback-vs-coordinates cross-check. Add both passing- and
   failing-direction tests.
6. **F-5 (nit)** — `src/stand_cad/__init__.py` module docstring still says "mobile equipment stand"
   after the TZ pivot recorded in ADR-005. Update the wording to reflect the current product
   (Light Plotter Tower) while keeping it accurate that this package is general CAD/config
   infrastructure, not product-specific code.

After applying all six fixes, re-run `uv run pytest` and `uv run ruff check .`; both must exit 0 with
every old and new test passing.
