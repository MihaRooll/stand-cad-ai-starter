# PLT-007 — Owner priority override: horizontal film storage, tier/setback/height reconfiguration

Status: DRAFT for implementer. Tier: T2 (set by Main; do not reclassify). Sole writer: `implementer`
(Composer 2.5). Review: `adversarial-reviewer` (mandatory). Verification: `verifier` (Grok). Cap: 3
internal review/verify cycles, third cycle closes blockers only.

Pre-change checkpoint: commit `69b1261` ("Fidelity cycle 4 (rev5): frame cladding, R10 bullnose,
top-member ID"), parent `0b235fb`. The superseded vertical-storage design (10 cells, 59.2 mm cell
width, 6..12 divider range, front retainer) is fully recoverable at that SHA — cite it in
`state/DECISION_LOG.md` instead of leaving a parallel dead code path, unless you find a clean way to
keep both behind a parameter with real test coverage for both. Prefer removal-with-record over a
half-tested branch; either is acceptable, but silence is not.

## Order of authority for this cycle

Per `AGENTS.md`, this is an explicit current owner instruction (received 2026-08-04 11:56) and it
outranks the TZ (`ИИ советы/Cursor_Opus5_TZ_Light_Plotter_Tower.md`) wherever they conflict. Every TZ
line touched below must be recorded in `state/REQUIREMENTS_TRACEABILITY.csv` as superseded/changed by
this owner decision, dated 2026-08-04, not silently reinterpreted.

## 1. Horizontal film storage (replaces vertical cells)

- Sheets are 330 x 500 mm, now lying flat with the **500 mm edge across the case width** (so the
  stack depth direction is what used to be "width", and shelves stack in Z instead of dividers
  spreading in X).
- **4 shelves, thin dividers, each compartment 25 mm clear height.** Total film compartment stack
  height ≈ 100-120 mm (4 × 25 mm clear + shelf/divider material thickness — compute exactly, do not
  round to a guess).
- Add a new parameter block (name it clearly, e.g. `film_storage_horizontal:`) with every leaf tagged
  `verified` (owner-stated, 2026-08-04) or `derived` (formula in `src/stand_cad/parameters.py`). At
  minimum: shelf/compartment count, clear height per compartment, sheet orientation, divider/shelf
  material thickness (reuse `materials.divider_thickness_mm` if applicable, don't invent a new
  thickness without provenance).
- Decide and record whether the legacy vertical block stays behind a parameter or is removed with a
  `state/DECISION_LOG.md` entry citing commit `69b1261` as the recovery point. Whichever you choose,
  `src/stand_cad/geometry/dividers.py`, `organizer.py`, and `assembly.py` must not silently keep
  computing the old 59.2 mm cell width / 9-divider layout as live geometry.
- Media path clearances (`media_path.*`) still apply — re-verify front/rear pass-through openings
  exist and clear at the new shelf geometry (item 6 below).

## 2. Tier height minimum 170 mm

- The owner owns a Cameo 4 (170 mm tall) and a Cameo 5 (130 mm tall per his message; note the
  existing `plotter.physical_height` leaf says 124 mm from TZ section 3 — reconcile this discrepancy
  explicitly in a comment/decision-log note rather than silently picking one; if unsure which is
  correct, treat 170 mm as the binding tier-clearance driver either way, since Cameo 4 is now the
  larger machine to clear).
- Every plotter tier (both tiers, since it's undecided whether they hold one of each machine or two
  Cameo 5s — see section 5) must clear **170 mm minimum**, not the ~124-132 mm the current model
  assumes (`plotter.physical_height` / `plotter.design_height`).
- Add a `verified` leaf, e.g. `plotter.tier_clearance_min_mm: 170`, note citing the owner's
  2026-08-04 message and both machine heights. Recompute `plotter.lower_z` / `plotter.upper_z` (or
  whatever Z datums currently encode tier spacing in `src/stand_cad/geometry/datums.py` and
  `frame.py`) so each tier's actual clear height (tray top to the underside of the structure above)
  is ≥ 170 mm. Show the arithmetic in a code comment or docstring, not just a changed number.

## 3. Tier 2 setback → 130 mm

- `plotter.upper_setback` changes from 150 to 130. This value is enforced by a hardcoded validator
  constant `REQUIRED_UPPER_SETBACK_MM` in `src/stand_cad/parameters.py` (currently 150) — update the
  constant, not just the YAML leaf, or the two will conflict and the loader will fail closed.
  `PARAM-008` also requires `upper_setback == upper_y - lower_y`; adjust `plotter.upper_y` (currently
  170) and/or `plotter.lower_y` (currently 20, TZ-verified coordinate) consistently — keep
  `lower_y` at 20 unless you find a reason it must move, and update `upper_y` to 150 so the
  identity holds (`150 - 20 = 130`). Update the note to record the owner override and the superseded
  TZ section 5 coordinate.
- Update `tests/test_geometry.py:96` (`measured_setback == pytest.approx(150.0)`) and every
  150/149-based assertion in `tests/test_parameters.py` (`test_plotter_setback_not_150_fails`,
  `test_plotter_setback_150_passes`, and the `_leaf(150)` fixtures) to the new 130 mm value. Keep the
  tests — do not delete coverage, retarget it.

## 4. Overall height — computed, not carried forward

- `case.height` is currently a hardcoded `verified` 690 mm leaf, and `REQUIRED_CASE_ENVELOPE_MM` in
  `src/stand_cad/parameters.py` hard-fails (`PARAM-006`) unless `(width, depth, height) == (650, 550,
  690)` exactly. That validator must change: `case.height` is no longer an independent fixed input,
  it is the **sum** of the base/foot structure, tier 1 clearance (≥170 mm), inter-tier structure, tier
  2 clearance (≥170 mm), the film-shelf stack (~100-120 mm from section 1), and the top structure
  (`top_structure.z_min_mm`/`z_max_mm`, currently a 15 mm band). Compute it from those parameters —
  change `case.height`'s provenance to `derived` with the formula in the note and in
  `src/stand_cad/parameters.py`, and change the width/depth/height check so width still hard-fails at
  exactly 650 while height is verified as *consistent with the tier/shelf stack sum* instead of
  compared to a hardcoded 690.
- Report the resulting number in your handoff with the full arithmetic chain.

## 5. Depth — 550 mm target with tolerance

- The owner states 550 mm depth measured from the tier where plotter 1 (the bottom tier) sits, and
  explicitly allows small changes if the geometry justifies them. `case.depth` currently participates
  in the same hardcoded `REQUIRED_CASE_ENVELOPE_MM` exact-match tuple as height — loosen that check
  for depth specifically (e.g. an explicit tolerance band, cite the owner's allowance and a numeric
  tolerance you choose and justify, `derived`/`verified` as appropriate) while keeping `case.width`
  exact at 650 (never stated as flexible).
  Compute what the geometry actually needs (organizer/shelf clear depth + panel thicknesses + plotter
  design_depth + any structure) and report the actual required depth next to the 550 mm target. Only
  change the stored value if the arithmetic does not close within your stated tolerance, and say so
  explicitly rather than quietly rounding.

## 6. Media pass-through, re-verified

- Keep the existing front/rear media pass-through openings per tier (`media_path.*`). Re-verify at
  the new tier Z-positions (section 2/3) and new shelf geometry (section 1) that clearances still
  hold — add/adjust a geometry test analogous to the existing media-path clearance tests if the
  current ones assume the old tier Z values.

## 7. Handles — centred, overriding centre-of-mass

- The owner wants handles **centred on the side panel**, not at the computed centre of mass. This
  overrides the Z=214 mm placement Main and the previous cycle agreed on (mass-report CoM z≈217.6
  mm; see `hardware.handle_mount_z_mm`'s current note and `output/validation/rev5/mass_report.csv`).
- Compute the side-panel centre Z (from `materials.foot_height_mm` up to `case.height`, using the
  *new* computed `case.height` from section 4 — this value depends on section 4's output, so do this
  after height is settled) and set `hardware.handle_mount_z_mm` to that centred value, provenance
  `derived`.
- In the note: record that this is an explicit owner override of the TZ line 235 centre-of-mass
  criterion, state the new centred Z, and state the resulting **offset from the computed CoM**
  (~217.6 mm) in mm, so the consequence is visible in the record rather than lost. Also update
  `state/DECISION_LOG.md` with the override and its date, and mark the TZ line 235 traceability row
  in `state/REQUIREMENTS_TRACEABILITY.csv` accordingly (superseded-by-owner-decision, not silently
  satisfied).

## 8. Missing shelf on the right — root-cause first, before you touch anything

Orchestrator's own arithmetic on the **current vertical** organizer, for you to verify by rendering
before you delete/replace this code:

- `film_storage.cell_width_mm` (derived) = `(clear_width − (cells−1)×divider_thickness) / cells` =
  `(610 − 9×2) / 10` = **59.2 mm**.
- `_divider_x_positions` in `src/stand_cad/geometry/dividers.py` places `divider_count = cells−1 = 9`
  dividers at `org_x + i×(cell_w + divider_t)` for `i = 0..8`, i.e. the last divider starts at
  `20 + 8×61.2 = 509.6 mm`.
- Cell 9 (the rightmost, 0-indexed) therefore spans `x ∈ [511.6, 570.8]`... **recompute this in the
  render/inspection, don't trust arithmetic alone** — the point is that the rightmost cell is bounded
  on its right by the organizer's own right edge (`film_storage.x + clear_width = 630`), not by a
  tenth divider, because 10 cells only need 9 internal partitions. That is very likely by design, not
  a defect: a render close to the right edge of the case, where the last cell blends into the side
  panel/frame, would visually read as "a shelf/divider is missing" even though the geometry is
  correct.
- **Confirm this with an actual isolated render or bounding-box dump of the rightmost cell and its
  boundary before writing your conclusion** — do not just accept the orchestrator's arithmetic.
  Report which it is: real geometric gap, or edge-of-image artefact. Whatever the answer, carry the
  lesson into the new horizontal shelves: each new shelf's compartments must have a real floor and
  divider (or wall boundary) on every side, and the boundary cell must not silently rely on being
  "at the edge" without you having checked it renders correctly.

## 9. Cameo 4 — unresolved dimensions, do not invent them

- Add `plotter_cameo4.height_mm: 170` (`verified`, owner-stated 2026-08-04).
- Add `plotter_cameo4.width_mm` and `plotter_cameo4.depth_mm` as `to_measure` with a clearly marked
  **provisional** placeholder value (do not leave them blank/null — the loader needs a number to
  build geometry with, but the note must say "PROVISIONAL, not measured, do not use for fit
  confirmation"). Do **not** invent these from memory or from a visually similar model — that
  prohibition is absolute in this repository.
- Tag every part that depends on these two leaves so they are identifiable exactly like the existing
  `feed_plane_z_from_base` to-measure regime (a `verify_on_real_machine=True` flag on the
  `PartRecord`, or equivalent).
- Size the niches so the **known** Cameo 5 (566×176×124 physical, 580×200×132 design envelope) fits
  with proper clearance on both tiers. Since it is undecided whether the design must hold one Cameo 4
  + one Cameo 5 simultaneously, or two Cameo 5s (Main has asked the owner), **model both tiers
  identically at the larger of the two known envelopes** so either machine could occupy either tier;
  state explicitly in your handoff that Cameo 4 footprint fit is **not confirmed** pending the two
  measurements, and add both open numbers to `docs/10_USER_INPUT_REQUIRED.md` if they are not already
  there from a previous cycle.
- Record in `state/DECISION_LOG.md` whether you modelled for "both machines simultaneously" or
  "either machine, either tier" and why.

## Carry forward unchanged from cycle 4 (commit `69b1261`)

Frame concealment (`PANEL-CLAD-FRONT-*`), the R10 bullnose on the side slabs, the grey render
background, and the closeup render targets. Re-verify they still render correctly once the tier
heights and overall case height change — dimensions they depend on (case.height, tier Z positions)
are moving.

## Constraints (unchanged)

- Every dimension flows from `config/parameters.yaml`; a literal in geometry code is a defect worth
  reporting even if you don't have time to fix it this cycle.
- Provenance on every new/changed leaf: `verified`, `derived`, or `to_measure` — nothing else.
- No invented dimension, ever, especially not Cameo 4 width/depth.
- All existing tests keep passing (updated to new numbers where the *requirement* changed, not
  weakened); add new tests for the new horizontal shelf geometry, the new tier clearance, and the
  new setback.
- Regenerate STEP, GLB, STL, manifest, and the full view set under a new revision (rev6) so rev5
  evidence stays reproducible. `CONCEPT`/`REFERENCE_ONLY` markings preserved.
- No PDF drawings, no production DXF, no gate marked passed, no `git push`. Local commits encouraged.
- `uv run pytest` exit 0, `uv run ruff check .` exit 0, full
  `powershell -ExecutionPolicy Bypass -File .\scripts\setup_windows.ps1` exit 0.
- Update `state/PROJECT_STATE.md`, `state/DECISION_LOG.md`, `state/ASSUMPTIONS.md`, and
  `state/REQUIREMENTS_TRACEABILITY.csv`. Update `docs/10_USER_INPUT_REQUIRED.md` with the Cameo 4
  width/depth gap and the both-machines-simultaneously question if not already present.

## Verification

Mandatory `adversarial-reviewer`: must confirm by looking at the regenerated renders (not by reading
code) that the four horizontal shelves are visible and distinct, the tier heights and setback read
correctly, handles are visibly centred on the side panel, and the rightmost-shelf question has a
render-backed answer. Then `verifier` re-runs the three commands above. Cap 3 internal cycles; a
third cycle closes blockers only.

## Report to Main (450 words max)

Commit SHA for the pre-change state (`69b1261`), the new computed overall dimensions with the
arithmetic, how the four horizontal shelves are parameterised, what changed in the tests, the root
cause of the missing right shelf, the Cameo 4 exposure (what's known, what's provisional, what's
blocked pending measurement), the new revision and render paths, command exit codes, and reviewer
findings.

## Addendum, 2026-08-04 12:12 — Cameo 4 blocker closed, governing model changes

The owner supplied verified Cameo 4 dimensions mid-cycle (interrupted the implementer while section 9
was in flight): **570 x 195 x 170 mm, 4.7 kg** (Silhouette Cameo 4 spec sheet:
https://www.silhouette101.com/wp-content/uploads/2020/01/cameo-4-spec-sheet.pdf). Cameo 5 confirmed at
566 x 176 x 124 mm, use 5.2 kg conservative
(https://www.silhouetteeurope.eu/en/silhouette-cameo-5-matte-black;
https://silhouetteamerica.freshdesk.com/support/solutions/articles/35000208584-cameo-machine-measurements).
This closes the `docs/10_USER_INPUT_REQUIRED.md` Cameo 4 blocker — section 9 above's `to_measure`
placeholders become `verified`.

Consequences superseding parts of sections 1-9 above, in order of impact:

1. Cameo 4 (570 mm wide) becomes the governing equipment model, not Cameo 5 (566 mm) — the base
   equipment CAD object must be sized to 570 mm minimum.
2. Overall width stays 650 mm. Remainder after 570 mm machine = 80 mm total; choose a wall thickness
   (10 mm → 630 mm clear, 15 mm → 620 mm clear, or another justified value) and derive clear width
   from it. **This supersedes the 610 mm clear width used in the PLT-006 R10 bullnose ruling** —
   recompute the maximum edge radius (≈ wall_thickness / 2) at the new wall thickness and update
   `case.side_slab_bullnose_radius_mm`, `state/DECISION_LOG.md`, and the TZ-230 traceability row
   accordingly. Do not grow past 650 mm to buy a bigger radius.
3. Both tiers sized definitively for the Cameo 4 envelope (≥170 mm clear height, already in progress).
4. **Operational clearance is now a modelled/tested requirement**: ~356 mm free space front AND rear
   of the machine during cutting (manufacturer figure). A closed niche is storage-only; cutting needs
   the tray extended or a full front-to-rear pass-through. Model and test both states; report whether
   the final case depth can deliver 356 mm front + 356 mm rear simultaneously alongside the machine's
   own depth (195/176 mm) — with numbers, not a glossed-over assumption.
5. Mass roll-up: 4.7 kg (Cameo 4) / 5.2 kg (Cameo 5) into `scripts/generate_mass_report.py` output.
6. **New part**: service port cut-out on the right side panel (facing the front) for an external
   USB/USB-C connection into the stand. Connector undecided — model a generic panel-mount USB/USB-C
   coupler cutout, dimensions `to_measure` with an explicit PROVISIONAL note, and log the open
   decision (connector type + exact cutout) in `docs/10_USER_INPUT_REQUIRED.md`.
7. Re-derive the protective design envelope from Cameo 4 (570 x 195 x 170) using the same
   `envelope_offset_*` formula that currently produces 580 x 200 x 132 from Cameo 5 — put it in
   `config/parameters.yaml` as `derived`, and re-run every clearance/collision/media-path test
   against the new envelope.

Everything else in this plan (horizontal shelves, 130 mm setback, centred handles, frame concealment,
grey background, computed height, depth-with-tolerance, no invented dimension, cap 3 cycles total for
the whole PLT-007 task) stands unchanged. Report per the original section above, plus: the re-derived
envelope and formula, new overall dimensions with arithmetic, the chosen wall thickness and its
resulting maximum radius, and an explicit numeric verdict on the 356 mm front+rear clearance question.

## Addendum 2, 2026-08-04 12:16 — Main's two rulings (supersede part of Addendum 1)

Interrupted the implementer a second time, same agent, to fold these in before it finished.

**Ruling 1 — clear width stays 610 mm; the "widen the niche" instruction in Addendum 1 is retracted.**
Max edge radius is bounded by wall thickness: a 10 mm wall caps radius at 5 mm, a 15 mm wall caps it
at 7.5 mm — both worse than the R10 the owner already accepted on the original 20 mm wall. Widening
the niche makes the case *more* angular, not less. Cameo 4 (570 mm wide) fits inside 610 mm clear
width with 20 mm free per side, closer to the TZ-89 target of 22 mm/side than a wider niche would
give. Ruling: hold `case.internal_width` at 610 mm, `case.width` at 650 mm, the 20 mm side wall, and
the existing R10 bullnose — revert anything already changed under Addendum 1's width/radius
instruction. Record in `state/DECISION_LOG.md` that Main considered and rejected widening the niche,
with the radius-vs-wall-thickness arithmetic, so it isn't re-opened later. The Cameo-4-derived
protective envelope (depth/height consequences) from Addendum 1 stands unchanged — only width/wall
thickness/radius revert.

**Ruling 2 — operating clearance is structural, not an open question.** Cameo 4 depth 195 mm + ~356 mm
front + ~356 mm rear = 907 mm working length; a 550 mm deep case cannot contain that at any tier
position, full stop. State this plainly with numbers in `state/PROJECT_STATE.md` and the validation
report: the closed case is storage/transport only; cutting requires material to pass out through
front+rear openings or the tray to extend, with external rear supports for long material
(`services.rearsupport_*`, TZ line 199) already anticipated. Add a test asserting the front/rear
pass-throughs are genuinely open and dimensioned in the operating state. Compute and report actual
clearance in front of plotter 1 and behind plotter 2 at the 130 mm tier-2 setback and 195 mm Cameo 4
depth (governs where external rear supports sit) — the existing `plotter.lower_y`/`upper_y` were
derived for a 176 mm machine and 150 mm setback, both now changed, so do not assume they still work;
adjust with numbers if they don't.

Everything else from Addendum 1 and the base plan stands. One final revision ships all of this
together — no shipping an intermediate revision with the now-reverted wider niche. Same 3-cycle cap
for the whole PLT-007 task, not a fresh budget per addendum.
