# Plan: PLT-003 concept visual validation + engineering analysis records

Tier: **T2** per Main's explicit ruling for this stage (concept artifacts under `output/` marked
`CONCEPT`/`REFERENCE_ONLY`; mandatory `adversarial-reviewer`, no `principal-arbiter`, no escalation to T3
in this stage). Chain: **Plan (this file) -> Implementer (sole writer, single work packet) -> mandatory
Adversarial review -> Verifier**. Cap 3 review/verify cycles; cycle 3 is blocker-only; an open blocker
after cycle 3 is `BLOCKED`, reported honestly to Main — never silently `done`.

Source of truth: `ИИ советы/Cursor_Opus5_TZ_Light_Plotter_Tower.md` ("TZ"). Existing geometry:
`src/stand_cad/geometry/*`, `config/parameters.yaml`, `src/stand_cad/parameters.py`. Existing 88 tests
must keep passing unless a specific, documented, honest correction requires an update (see section 3).

## Task Contract

```yaml
contract_id: PLT-003-concept-validation
tier: T2
goal: >
  Produce real visual-validation evidence (renders + honest divergence report) and proper
  engineering-analysis records (mass/CoM, stability, deflection, thermal/electrical layout-only)
  for the CONCEPT/REFERENCE_ONLY rev1 model, with traceability updated only where evidence is
  proportionate to the claim.
acceptance_criteria:
  - id: AC-1
    text: >
      output/validation/rev1/views/ contains named PNG renders for closed-transport ortho
      front/rear/left/right/top + isometric, service-plotter-1 isometric, service-plotter-2
      isometric (tray extended), organizer-loaded-with-film isometric, and a panels-hidden
      isometric exposing frame/trays/adapters/cable channels — all referenced by relative path
      from validation_report.md.
  - id: AC-2
    text: >
      validation_report.md lists every observed comparison point from the owner's reference image
      against TZ section 8 lines 227-235. Points that diverge are tagged fixed|reported (reported
      ones citing the exact TZ line that would be violated by copying the reference, or stating
      plainly that no TZ line applies but the fix is out of bounded scope). Points that already
      match the reference may be tagged match — a third, non-divergent category — and need no
      fix-or-report citation. (Clarified 2026-08-03 after verifier cycle 2: the original wording
      only anticipated divergences; rows 7-10 in rev1 correctly use match for non-divergent
      observations.)
  - id: AC-3
    text: >
      output/validation/rev1/mass_report.csv has one row per structural part with part_id,
      material, volume_mm3, density_kg_m3, density_source, mass_kg; empty-case total reconciles
      with mass_targets.empty_case_max_kg/target band with a one-line dominance statement.
  - id: AC-4
    text: >
      output/validation/rev1/stability_report.md states pivot edge, included masses/arms, load
      case, and the resulting factor, reproducible from stated inputs by hand.
  - id: AC-5
    text: >
      output/validation/rev1/deflection_report.md states beam model, span, support conditions,
      section, E source, load case, and result; if span was previously wrong (physical_depth
      instead of the rail-to-rail span) it is corrected and the consequence stated honestly even
      if the corrected number exceeds trays.deflection_max_mm.
  - id: AC-6
    text: >
      output/validation/rev1/collision_report.md (promoted from prose in validation_report.md)
      and export_validation.md exist as their own named files per TZ section 14.
  - id: AC-7
    text: >
      No new to_measure/assumed numeric input is invented; every such input added or reused this
      stage gets or reuses an A-0xx id in state/ASSUMPTIONS.md.
  - id: AC-8
    text: >
      state/REQUIREMENTS_TRACEABILITY.csv rows move off OPEN/IN_PROGRESS toward evidenced status
      only for requirements with evidence produced this stage; indicative/assumption-dependent
      rows say so explicitly in the notes column rather than reading as fully satisfied.
  - id: AC-9
    text: uv run pytest exits 0; uv run ruff check . exits 0; full setup_windows.ps1 exits 0.
owned_files:
  - output/validation/rev1/**
  - state/REQUIREMENTS_TRACEABILITY.csv
  - state/PROJECT_STATE.md
  - state/ASSUMPTIONS.md
  - docs/10_USER_INPUT_REQUIRED.md
  - src/stand_cad/geometry/analysis.py
  - src/stand_cad/geometry/panels.py
  - src/stand_cad/geometry/frame.py
  - src/stand_cad/geometry/hardware.py
  - config/parameters.yaml
  - tests/test_geometry.py
verify_commands:
  - uv run pytest
  - uv run ruff check .
  - powershell -ExecutionPolicy Bypass -File .\scripts\setup_windows.ps1
forbidden:
  - No PDF or DXF generation this stage.
  - No gate marked passed; no PROTOTYPE_RELEASED/SERIES_RELEASED anywhere.
  - No invented material density or sandwich-panel stiffness — source it or mark it assumed with
    an A-0xx id.
  - No change to a fixed TZ dimension (650x550x690 envelope, plotter physical/design envelopes,
    150 mm setback, organizer 610x510x325 clear volume, cell formula, tray extensions) to chase
    reference-image likeness.
  - No git push.
```

## 1. Part A — visual validation (render, compare, fix-or-report)

Use `build123d-mcp` against the live parametric build (do not rely on the exported STEP alone —
rebuild each state in-session so hidden-panel and loaded-organizer views are possible).

Required renders under `output/validation/rev1/views/` (implementer picks filenames, references
them all from `validation_report.md`):

1. Transport state: orthographic front, rear, left, right, top, plus one isometric.
2. `service_plotter_1` isometric (lower tray extended).
3. `service_plotter_2` isometric (upper tray extended).
4. Organizer loaded with representative film bodies (vertical sheets + dividers visible) —
   compose a state that adds sheet-like test bodies per cell (reuse the `320x500` film envelope
   geometry already used for `PLT-005`, replicated across a few cells) if no such state exists yet.
5. One isometric with `PANEL-OUT-*` (and `TOP-STRUCTURE-001` if it occludes) suppressed, showing
   frame, trays, adapters, cable-channel service volumes.

Compare against `ИИ советы/ChatGPT Image 3 авг. 2026 г., 20_58_06.png` and TZ section 8 lines
227-235 (white body, R20-R30 soft radii, minimal visible joints/screws, 2-3 mm shadow gaps, no
sharp front edges, rear/underside service covers, two side handles near CoM).

Known candidate divergences to evaluate (not exhaustive — look honestly at the renders):

- **Corner radius.** `config/parameters.yaml` `case.corner_radius` (25 mm) is not consumed by any
  geometry builder (`rg corner_radius src` returns only the YAML leaf) — panels/frame are sharp
  boxes. Applying true R20-R30 fillets across the outer shell (4 separate box panels, not one
  shelled solid) is a real modeling task, not a one-line tweak. Attempt it **only** if it can be
  done as a bounded, low-risk edit (e.g. filleting the 4 vertical outer corners after a boolean
  union of the 4 `PANEL-OUT-*` boxes into one shell, re-split or kept as one part, with the
  assembly bounding box unchanged) and it does not require restructuring collision/mass code
  beyond `analysis.py`'s existing shell-volume approximation. If it is not bounded/low-risk within
  this stage, do **not** attempt it — report it as an open cosmetic finding (not a TZ-dimension
  conflict; TZ explicitly permits R20-R30 and the case envelope is unaffected either way) with a
  proposed follow-up geometry packet.
- **Open-shelf vs enclosed front.** The reference image shows an open-shelf unit with plotters and
  film fully visible from the front. TZ section 2 lines 170-172 requires plotters to stay inside a
  closed case with locked platforms during normal cutting, and TZ section 8 requires an opal-PMMA
  glowing shell, not an open shelf. Do **not** open up the front panel to match the reference —
  report this as an expected, TZ-mandated divergence (cite TZ:170-172) rather than a defect.
- Visible joints/screws, shadow-gap evenness, handle placement/shape, sharp front edges elsewhere
  (e.g. `TOP-STRUCTURE-001`, `PANEL-IN-*` edges visible through the opal shell) — judge case by
  case; fix only if it is a small coordinate/parameter change with no risk to the 88 passing tests,
  otherwise report.

For every divergence: state fixed-or-reported, and for reported ones, name the exact TZ line that
a reference-matching change would violate (or, for non-dimensional cosmetic gaps like the fillets,
say plainly that no TZ line is violated but the fix is out of bounded scope for this stage).

## 2. Part B — engineering analysis records

All under `output/validation/rev1/`. Every number states its method, inputs, assumptions, and
limits per TZ section 13 line 401. Reuse `state/ASSUMPTIONS.md` A-0xx ids for every to_measure
input; add new ids only for genuinely new assumptions (next free id after `A-011`).

1. **`mass_report.csv`** — columns `part_id,material,volume_mm3,density_kg_m3,density_source,
   mass_kg`. Derive volume/density using the existing `part_mass_kg`/`MATERIAL_DENSITY_PATHS`
   logic in `src/stand_cad/geometry/analysis.py` (reuse, do not duplicate the shell-approximation
   policy elsewhere) for every non-excluded structural part across the transport-state build. Add
   an assembly-rollup section (or a second small table) by material family. In
   `validation_report.md` (or a short header in the CSV's companion prose), report the empty-case
   total against the 12 kg ceiling and 9-11 kg target band, and name what actually dominates the
   mass (inspect the rolled-up totals — do not guess). Add centre-of-mass computation (volume-
   weighted centroid, or component-centroid weighted by `part_mass_kg`) for three configurations:
   empty case, case + two plotters (add `EQUIP-PLOTTER1/2-001` mass at `plotter.design_mass_kg`
   each even though equipment is excluded from the structural shell total), and one plotter fully
   extended (translate that plotter's CoM contribution by its tray's extension). Record method and
   result in `mass_report.csv`'s header/notes or a short section of `validation_report.md`.
2. **`stability_report.md`** — TZ lines 187/508: factor >= 1.5, one tray fully extended, organizer
   empty, second plotter installed. State explicitly: pivot edge (front or rear foot line —
   whichever the extended tray tips toward), which moments are included (restoring: total weight
   times horizontal arm to the pivot edge; overturning: extended assembly weight times arm from
   its CoM to the pivot edge), and what is excluded (aerodynamic/dynamic loads, friction). Show the
   arithmetic from `indicative_tip_factor()` in `analysis.py` (or a corrected version of it) with
   actual numbers substituted, not just the returned float.
3. **`deflection_report.md`** — TZ line 184: <=1.5 mm under 10 kg. Re-derive
   `indicative_tray_deflection_mm()`: the current span (`plotter.physical_depth`, 176 mm) is
   almost certainly the wrong axis — the tray is carried by two full-extension slide rails running
   front-to-back (Y) at the left/right (X) edges of the niche, so the panel spans **across X**
   (rail-to-rail, on the order of `plotter.physical_width`/`case.internal_width`, ~566-610 mm)
   under a load distributed over **Y** (~`plotter.physical_depth`, 176 mm). Correct the beam model
   accordingly (state the corrected span/width assignment explicitly), keep `E =
   materials.tray_panel_youngs_modulus_mpa` (already `to_measure`/unsourced — restate that
   plainly, cite its existing note, do not invent a better number), and report the honest result
   even if it now exceeds `trays.deflection_max_mm`. If the corrected code path is applied in
   `analysis.py`, do not leave `tests/test_geometry.py::test_indicative_tray_deflection_non_authoritative`
   silently green on a false premise: either convert it to an `xfail` with a reason string citing
   this finding and `deflection_report.md`, or change its assertion to check the method (e.g.
   monotonic/positive/finite) rather than a ceiling it cannot honestly pass under the current
   unsourced `E`. Whatever is chosen, `uv run pytest` must still exit 0, and the choice and its
   reasoning go in the report and in `docs/10_USER_INPUT_REQUIRED.md` (this is a load-path/fit
   result, not a documentation nit — flag it per `AGENTS.md` autonomy rules). Do not paper over a
   ceiling miss by quietly tuning `E` upward with no source.
4. **Thermal/electrical** — do not compute. In `validation_report.md` (or a short
   `thermal_electrical_layout.md` section within it), record: separated mains/low-voltage channel
   parts already modeled (`CABLE-CH-001`, `MAINS-INLET-001`), vented adapter pocket parts outside
   the media path (`ADAPTER-P1/2-001`, `ADAPTER-LIGHT-001`), single mains inlet count (reuse the
   existing registry check), and TZ section 10 line 291's two limits (40 C adapter bay after 2 h at
   25 C ambient; <=10 K rise in film bay) explicitly as **prototype tests to run**, not computed
   results. Cite TZ:293 (layout only, qualified electrician required).
5. **`collision_report.md` / `export_validation.md`** — split the existing prose out of
   `validation_report.md` into these two named files (TZ section 14 naming); keep
   `validation_report.md` as the top-level index that links to all five reports and the `views/`
   renders.

## 3. Part C — traceability

Update `state/REQUIREMENTS_TRACEABILITY.csv`:

- `SWE-007` (view review): now has real evidence — cite the `views/` renders.
- `PLT-010` (tip factor): cite `stability_report.md`; keep noting non-authoritative-for-G4 unless
  the report itself demotes/confirms.
- `PLT-011` (deflection): cite `deflection_report.md`; if the corrected analysis exceeds the
  ceiling under the current unsourced `E`, the row must say so plainly (e.g. status stays
  `IN_PROGRESS` with a note that the ceiling is not met under present assumptions), never marked
  as satisfied.
- `PLT-012` (mass): cite `mass_report.csv`; note dominance finding.
- `PLT-015` (deliverables): cite the newly split report files.
- Any other PLT/SWE row with new evidence this stage — update `evidence`/`notes`, never flip a row
  to a stronger status than the evidence supports.

Update `state/PROJECT_STATE.md` (new dated entry) and `state/ASSUMPTIONS.md` (new A-0xx rows for
any new to_measure input, e.g. the corrected deflection span's own confidence, if applicable).

## 4. Review focus for the mandatory adversarial pass

Hunt specifically for: (a) a number presented as computed that is actually assumed without an
A-0xx citation; (b) a render whose filename/caption claims a state (e.g. "service_plotter_2") that
the image does not actually show (wrong tray extended, wrong panels visible/hidden); (c) any PLT/
SWE row moved off OPEN/IN_PROGRESS with evidence disproportionate to the claim; (d) whether the
deflection ceiling miss (if any) was honestly surfaced rather than hidden by a quietly retuned
input or a test weakened without explanation; (e) whether any geometry edit this stage (fillets,
etc.) silently changed a fixed TZ dimension or broke a previously-passing assertion without
disclosure.

## 4a. Addendum (Main's priority change, 2026-08-03 23:13) — open shell, local render, MCP config

**Ruling override:** the earlier framing that an open front conflicts with TZ:170-172 was wrong.
TZ:170-172 constrains tray/machine *position* (retracted, locked) during normal operation, not the
presence of a solid front panel. The reference image's open front is consistent with the TZ. The
open front at both plotter levels is now **required geometry**, not a reported-only divergence.

**MCP is confirmed unusable, not just flaky:** Main independently reproduced `import_cad_file`
timeout (120s x2), `health_check` failure x2, and a trivial `Box(100,60,20)` `execute()` timeout —
matching the operational-orchestrator's own two `health_check` failures earlier this stage. Per the
package's own `--help` text, a worker that fails even a trivial call matches the documented
"Worker process failed to start" case, for which the package itself recommends `--in-process`.
Stop routing renders through `build123d-mcp`; the local `uv run` path is the project's real render
path going forward.

**Required geometry changes (bounded, must not change the fixed TZ envelope/coordinate table or
break existing collision/bounding-box tests):**

- Front openings at both plotter niches (`PANEL-OUT-FRONT-001` gets boolean cutouts, or is split
  into stiles/header + two clear openings) sized to each niche's design envelope, leaving the
  organizer level's front panel/retainer as-is (organizer front opening is explicitly out of scope
  for this addendum — TZ's 40-50mm `RETAINER-001` already governs that zone).
- Two rear media feed slots (one per level) as real boolean openings in `PANEL-OUT-REAR-001` at
  each level's feed-plane zone, sized to `media_path.clear_width`/`slot_height_target` (or the
  existing `SVC-INSERT-*` footprint) — not just a conceptual placeholder volume.
- Two handle openings (110x35mm minimum grip, TZ:304) as real through-cuts in
  `PANEL-OUT-LEFT-001`/`PANEL-OUT-RIGHT-001` at `HANDLE-*` positions, not solid box additions.
- Even 2-3mm shadow-gap reveals between all four outer panels' shared vertical edges (not just the
  existing single-axis gap on left/right).
- Real R20-R30 fillets on the visible outer shell corners — restore a `case.corner_radius` leaf
  (new provenance `verified`, TZ:230) since it is now implemented, not deferred; supersede `A-013`
  (mark its status `Closed`, cite the new fillet implementation).

**New deliverables:**

- `output/validation/rev1/views/`: same 10 PNGs as before (regenerated with the open shell), plus
  SVG orthographic line drawings (front/rear/left/right/top) via the build123d HLR path (works
  headless, no VTK dependency).
- `output/concept/`: STL and, if a glTF/GLB exporter exists in the pinned `build123d==0.11.1`
  stack, a GLB — both named with `CONCEPT`/`REFERENCE_ONLY` exactly like the STEP, e.g.
  `light_plotter_tower_ASSEMBLY_CONCEPT_REFERENCE_ONLY_rev1.stl`. Confirm both fall under the
  existing `output/` gitignore rule (check `.gitignore`, do not add a new one unless missing).
- `.cursor/mcp.json`: add `--exec-timeout` (generous, e.g. `300`) and `--in-process` to the
  `build123d-mcp` server args. Record in `state/PROJECT_STATE.md` that this requires an owner
  Cursor reload to take effect, and that the local `scripts/render_*.py` path is what the project
  actually relies on for renders regardless of whether the MCP fix helps.

**Owned files added this addendum:** `.cursor/mcp.json`, `.gitignore` (read-only check, edit only
if the rule is missing), `src/stand_cad/geometry/panels.py`, `src/stand_cad/geometry/hardware.py`,
`src/stand_cad/geometry/services.py` (rear slot geometry if it lives there instead of panels.py),
`scripts/render_validation_views.py` (extend in place — do not fork a second render script).

**Review focus addition for this addendum:** confirm every render actually shows the open-shell
state it claims (not a stale cached PNG from the closed-box version); confirm the new openings did
not silently violate a fixed TZ dimension (niche width/height, envelope, setback) and did not break
any previously-passing collision/clearance/bounding-box test; confirm STL/GLB are non-trivial
(nonzero solids, exported from the same live build, not stub files).

## 5. Verification commands

- `uv run pytest`
- `uv run ruff check .`
- `powershell -ExecutionPolicy Bypass -File .\scripts\setup_windows.ps1`

All three must exit 0 for `verdict: pass`.
