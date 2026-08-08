# FIX-WAVE-001 — consolidated adversarial-review fix wave

- Orchestrator: operational-orchestrator (L1), tier T2 (physical-quantity floor: Stream D grommet
  lining fix + PLT-010 status honesty change), mandatory adversarial review before verifier close-out.
- Scope: everything ten independent adversarial reviews found that is still open AND fixable without
  an owner decision. Excludes the DO-NOT-FIX list (joining design, ORG-FLOOR-001 clearance, PANEL-IN-MID
  rail intersection, MEDIA-SUPPORT unsupported span, frame-as-solid-prism, side-slab mass contradiction,
  transport retention hardware, handle concept, lid headroom, thermal, electrical) — those are recorded
  only, in `state/DEFERRED_VERIFICATION.md` and `docs/10_USER_INPUT_REQUIRED.md`.
- Sole writer: Composer `implementer`, sequential dispatch per stream (no parallel writers).
- Streams (disjoint file sets, run sequentially by this orchestrator):
  - A: `state/REQUIREMENTS_TRACEABILITY.csv` only.
  - B: `docs/10_USER_INPUT_REQUIRED.md`, `docs/08_RISK_REGISTER.md`, `docs/12_PRODUCTION_RFQ_TEMPLATE.md`.
  - C: `state/DECISION_LOG.md`, `docs/adr/ADR-005-TZ-STACK-AND-LAYOUT.md`.
  - D: `src/stand_cad/geometry/services.py`, `scripts/render_validation_views.py`,
    `config/parameters.yaml`, `src/stand_cad/parameters.py`.
  - E: `tests/**` only.
  - F (last, after A–E land): `state/PROJECT_STATE.md`, `HANDOFF_PROMPT.md`.
- Verification: Quick (`uv run pytest` + `uv run ruff check .`) between streams touching code;
  Full (`powershell -ExecutionPolicy Bypass -File .\scripts\setup_windows.ps1`) plus
  `uv run python scripts/regenerate.py` at the end. Note: bare `powershell` (no `.exe`) is not on
  PATH in this bash shell — use `powershell.exe`.
- Stream E's extended `test_lid_envelope_no_intersection_in_service_states` (INTERLOCK-SHUTTLE-001
  coverage) is EXPECTED to fail — do not weaken it; report the measured intersection volume.
- Grounding already established by the orchestrator before dispatch (so implementer does not need to
  re-derive):
  - `state/REQUIREMENTS_TRACEABILITY.csv` PLT-021 row is missing its `status` field (9 fields instead
    of 10) — every field after `source` is shifted one column left.
  - Real test names: `tests/test_geometry.py::test_handle_mount_y_at_loaded_com`,
    `test_handle_mount_z_lowest_sightline_feasible` (handle); `tests/test_kinematics.py::
    test_tray_extension_rear_face_clearance` (tray extension/front-rear clearance, supersedes both the
    stale D-048 and PLT-020 citations).
  - `src/stand_cad/geometry/services.py:120,138` — cable grommet uses
    `materials.outer_panel_thickness_mm` (3 mm) for both its length and its X placement
    (`width - cp_outer_t`), so it only lines X∈[647,650] instead of the full 20 mm
    `_side_clearance_mm(params)` bore span X∈[630,650] cut by `panels.py::_subtract_cable_passthrough_x`.
  - `scripts/render_validation_views.py:432-441` `build_cable_passthrough_closeup_assembly` still
    filters `PANEL-OUT-REAR-001`; must filter `PANEL-OUT-RIGHT-001` and the render/background/view
    grouping (lines ~480-683) should move with it to the side-view convention (direction (1,0,0),
    `SIDE_VIEW_BACKGROUND_RGB`) instead of the rear-view grouping.
  - `EDGEGUARD_MATERIAL` (`services.py:13`) is NOT fully dead — it is the literal material string
    (`"soft_trim_brush"`) still assigned to the cable-passthrough grommet (`services.py:141`); only the
    *name* is stale (an edge-guard part that no longer exists). `REARSUPPORT_MATERIAL` (`services.py:14`)
    is genuinely unused. Rename the grommet's constant to something accurate (e.g. `GROMMET_MATERIAL`),
    keep the string value `"soft_trim_brush"` (feeds `analysis.py::MATERIAL_DENSITY_PATHS`, unrelated to
    this fix), delete `REARSUPPORT_MATERIAL`, and correct the module docstring.
  - `config/parameters.yaml:100-101` — the `slot_height_target` note claims it is "BELOW
    media_path.clear_height_min" but both are 10 — false; `clear_height_min`'s own note already
    correctly says there is no code validator enforcing it. Fix the misstatement and decide: add a real
    `PARAM-0xx` check in `validate_parameters`, or state explicitly (accurately) that it is unenforced.
  - `src/stand_cad/parameters.py:612-653` — `PARAM-016` (front_y > 0) is mathematically always a subset
    of `PARAM-015` (rear_y > -overhang_min) whenever `overhang_min_mm >= 0` and `physical_depth > 0`
    (rear_y = front_y + physical_depth, so front_y > 0 ⇒ rear_y > physical_depth > -overhang_min) — true
    for any physically sane parameter set, not just current values. Document this honestly.
  - `src/stand_cad/parameters.py:1-8` module docstring claims "no CAD dependency"; `computed_handle_mount_y_mm`
    (line ~248) lazily imports `stand_cad.geometry.analysis.indicative_loaded_case_com_y_mm`, which
    itself lazily imports `stand_cad.geometry.assembly.build_transport_assembly` and builds full CAD —
    so `validate_parameters`'s PARAM-017 handle-Y check is NOT CAD-free. Docstring is wrong; fix it.
  - `interlock.shuttle_travel_mm` YAML leaf (75) vs `Parameters.interlock_shuttle_travel_mm` property
    (recomputes ~98 after D-038); geometry reads the property, not the leaf — leaf is dead.
  - `state/DECISION_LOG.md` D-048's test citation `test_tray_extension_plotter_front_clears_case` does
    not exist; correct citation is `tests/test_kinematics.py::test_tray_extension_rear_face_clearance`
    (same test D-049 already cites).
  - `docs/adr/ADR-005-TZ-STACK-AND-LAYOUT.md` deliverable table: `output/<revision>/BOM.csv` →
    `output/validation/<revision>/`; `generate_model.py` "future" → exists at `scripts/generate_model.py`
    (plus `scripts/generate_drawings.py` for PDF/DXF/BOM per D-052).
  - `docs/12_PRODUCTION_RFQ_TEMPLATE.md` currently has no statement that electrical is unengineered,
    no joining-design statement, no flat-pattern/bend-data ownership statement, and no plain-language
    warning that `MAINS-INLET-001` is a deferred placeholder, not a designed inlet.
  - `state/PROJECT_STATE.md` and `HANDOFF_PROMPT.md` are both stuck at the D-048 era (rev11, 200 mm
    travel, tip factors ~3.480/~3.943, handle Y=100, PARAM-015 deviation) — must be brought current
    through D-053/rev12 in Stream F, last.
