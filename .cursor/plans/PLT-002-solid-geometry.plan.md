# Plan: PLT-002 parametric solid geometry (no drawings)

Tier: **T2**, per Main's binding ruling recorded below (Main's tier ruling supersedes the tier-floor
default in `.cursor/rules/21-orchestration-overlay.mdc` for exports that are git-ignored under
`output/`, carry `CONCEPT`/`REFERENCE_ONLY` in the filename, and are blocked from release by
`validate_release_readiness()`/`REL-027`). Chain for this stage: **Plan (this file, revision 3) ->
Implementer (sole writer, 3 sequential Work Packets per section 12; no `principal-arbiter`, per Main's
explicit instruction) -> mandatory Adversarial review -> Verifier**. Cap 3 review/verify cycles; cycle 3
is blocker-only; an open finding after cycle 3 is `BLOCKED`, reported honestly.

**Revision 3 changelog (Main's rulings, this turn) — implementer must action these as part of Packet 1:**

- **Ruling 1 (tier):** record the exact T2/T3 boundary above in `state/DECISION_LOG.md`, and reflect the
  qualified rule in `.cursor/rules/21-orchestration-overlay.mdc` (the T3 floor for STEP/PDF/DXF applies
  in full the moment an artifact is produced for a manufacturer's eyes — RFQ STEP, quotation PDF, any
  DXF, or anything without the CONCEPT/REFERENCE_ONLY marking).
- **Ruling 2 (test exhaustiveness, authorised):** update
  `tests/test_parameters.py::test_production_release_blocks_on_to_measure_parameters` to assert the
  full, explicit set of intentional `to_measure` paths (existing 3 plus every new one added by this
  plan) — an explicit fixed set, not a dynamically derived one, so the test still fails loudly if an
  *unintended* `to_measure` leaf appears later. This is not weakening: coverage stays exhaustive over
  the whole file.
- **Ruling 3 (`FRAME-001` decomposition, authorised):** split the single merged `FRAME-001` into
  individually coded members (see revised section 2). Genuinely identical members (e.g., 4 corner
  posts) get one base part-ID with a documented quantity, but each instance is still its own solid at
  its own position for collision purposes — never one merged body standing in for four.
- **Ruling 4 (interlock fidelity, clarified):** discrete-state kinematics is acceptable for this concept
  stage. Model `INTERLOCK-SHUTTLE-001` and both tabs as real solids at real `Parameters`-derived
  dimensions and prove non-interference/interference by boolean intersection at the modelled discrete
  states (transport, service-1, service-2) — never by prose or a numeric comparison alone. A continuous
  swept-envelope proof over the full travel range is explicitly deferred to detailed design; record that
  deferral as a new row in `state/ASSUMPTIONS.md` (next free ID after `A-010`, i.e. `A-011`) so it is not
  forgotten.
- **Ruling 5 (collision allowlist, numeric):** replace the vague `disjoint`/`touching`/`contained`
  wording with an explicit **mating-pairs list** (declared by exact part-ID pair — e.g.
  `FOOT-*`<->floor plane, `DIVIDER-###`<->`ORG-COMB-RAIL-001` slot, `TRAY-*`<->`SLIDE-*`, panel<->frame
  shared faces) where zero-distance contact is expected and allowed. For **every other pair**, require a
  minimum clearance and fail below it; default floor is `0.5` mm (`tolerance.part_assembly_feature_mm`,
  which already equals `0.5` in `config/parameters.yaml` — reuse it, do not add a second literal `0.5`)
  unless a more specific TZ-derived value applies to that pair. Zero-distance contact between two
  non-mating parts is a hard failure, not a rounding tolerance. State the threshold used in the
  validation report.
- **Ruling 6 (scope, confirmed):** do not narrow the stage to `verified`-only parameters; model
  everything the TZ requires or implies, adding `to_measure` leaves with clearly marked provisional
  values for geometry wherever the TZ is silent on a real dimension (slide hardware, vibration feet,
  adapter bodies, etc.), each traceable and tagged so the drawing stage can find every
  `VERIFY ON REAL MACHINE` candidate programmatically.

**Revision 2 changelog (superseded detail retained for traceability; responding to principal-arbiter
verdict, agent `f29c2368-eabe-4f35-a20c-63c506356bcd`, before Main's tier ruling removed the T3
requirement for this concept export):** explicit physical part IDs replace wildcards; envelope-
intersection arithmetic confirmed (no 3D intersection, 28 mm Z clearance) and turned into a required
non-trivial test; divider retention mechanism made concrete (comb rail + slot engagement); interlock
mechanism selected (captive vertical shuttle + two tray tabs, three positions) instead of an unspecified
generic body; tray-travel arithmetic corrected (translation-based, not additive); test list expanded to
TZ section 17 items previously missing; collision checking now uses an explicit per-pair, per-state
allowlist (further sharpened to a numeric clearance rule by Ruling 5 above); new parameters added for
every implementer-selected dimension with explicit provenance; work split into 3 sequential Work
Packets to the same sole-writer implementer.

Source of truth: `ИИ советы/Cursor_Opus5_TZ_Light_Plotter_Tower.md` ("TZ"), sections 5, 6, 7, 8, 10, 11,
13, 17. Dimensional source of truth: `config/parameters.yaml` via `src/stand_cad/parameters.py`. **No
literal dimensional number may appear in geometry code.** Every part position/size resolves through
`Parameters` (including derived quantities computed in Python, never re-hardcoded in YAML or in
geometry files). An implementer-selected dimension that is a free design choice within a TZ-stated
range (e.g., an exact vibration-mount diameter within "thin") must still get its own `Parameters` leaf
with an honest provenance — `derived` if computed from other verified values, `to_measure` if it is a
placeholder pending real measurement/selection, and never `verified` unless the TZ or a manufacturer
source states that exact number.

## 0. New parameters to add to `config/parameters.yaml`

All new leaves use `{value, provenance, note}`. Do not change any existing leaf's *value* (the other 39
existing tests must keep passing unmodified after every YAML edit — re-run `uv run pytest` after each
edit). The one authorised exception is
`tests/test_parameters.py::test_production_release_blocks_on_to_measure_parameters` (Ruling 2): update
its expected path set to the full, explicit list of intentional `to_measure` leaves once all of section
0's new `to_measure` leaves exist, keeping the assertion an explicit fixed set (so an unintended future
`to_measure` leaf still fails it) rather than a dynamically derived one.

- `plotter.envelope_offset_x_mm` / `_y_mm` / `_z_mm` — `provenance: derived`. Formula in the note and in
  a `parameters.py`/`datums.py` docstring: `offset_x = (design_width - physical_width) / 2`, same
  pattern for Y (`design_depth`/`physical_depth`) and Z (`design_height`/`physical_height`). Confirmed
  numeric result with current verified values: `(7, 12, 4)` mm — never hardcode `7`/`12`/`4` in geometry
  code; expose as a `Parameters` property that recomputes from the verified leaves live, and store the
  YAML leaf only as a traceability record of that computed value.
- **Confirmed by principal-arbiter arithmetic — record as a code comment and a test, not just this
  plan:** `ENV-PLOTTER1-001 = X[35,615], Y[8,208], Z[26,158]`; `ENV-PLOTTER2-001 = X[35,615], Y[158,358],
  Z[186,318]`. X overlap 580 mm, Y overlap 50 mm, **Z clearance 28 mm** — the two envelope boxes do
  **not** intersect in 3D because Z does not overlap. This is not an assumption to re-derive by hand in
  code; write a test that measures both built envelope solids' bounding boxes, asserts zero 3D
  intersection volume, and asserts the Z clearance equals `28` mm computed from `Parameters` (via the
  offsets and body Z coordinates), not a literal `28`.
- `plotter.feed_plane_z_provisional_mm` — `provenance: to_measure`. TZ section 12 explicitly allows a
  provisional demo value distinct from `feed_plane_z_from_base`. Pick a value in `[20, 60]` mm above
  each tray's finished top surface, document the reasoning (e.g., "provisional mid-low front-feed slot
  height for a desktop cutter; not a manufacturer figure") in the note. Tag every part whose position
  derives from it with `verify_on_real_machine=True` part metadata.
- `plotter.lid_open_envelope_height_mm` (or similar) — `provenance: to_measure`. TZ section 16 item 3
  states the real open-lid envelope and hinge position must be measured; add a provisional swept-volume
  height above `physical_height` for the demo lid-open envelope, tagged `verify_on_real_machine=True`.
- `trays.slide_rail_width_mm`, `trays.slide_rail_height_mm` — `provenance: to_measure` (dimensions of a
  full-extension slide pair are a bought-hardware selection, not yet chosen); use placeholder values
  for concept geometry.
- `trays.soft_stop_size_mm`, `trays.vibration_mount_diameter_mm`, `trays.vibration_mount_height_mm` —
  `provenance: to_measure` (free design choices pending hardware selection).
- `film_storage.comb_slot_depth_mm`, `film_storage.comb_slot_clearance_mm` — `provenance: derived`
  (`comb_slot_clearance_mm` derived from `tolerance.part_assembly_feature_mm`); `comb_slot_depth_mm` may
  be `to_measure`/a documented provisional choice.
- `hardware.handle_grip_length_mm` (>=110), `hardware.handle_grip_depth_mm` (>=35) — `provenance:
  verified` (TZ:304 states the minimum directly) or `derived` if the implementer adds margin.
- `interlock.shuttle_travel_mm`, `interlock.tab_engagement_mm` — `provenance: to_measure`/`derived` as
  appropriate; support the mechanism in section 7.
- `materials.*_density_kg_m3` for PMMA, PETG/PC, aluminium, sandwich-panel-equivalent — `provenance:
  verified` citing generic datasheet ranges (e.g., PMMA ~1180, PETG ~1270, 5052 aluminium ~2680 kg/m3),
  or `to_measure` if no defensible generic figure exists. Label all resulting mass numbers **indicative**,
  never a G4 engineering result.
- `materials.tray_panel_youngs_modulus_mpa` (or equivalent stiffness parameter) — `provenance:
  to_measure` unless a specific sandwich-panel datasheet is cited; used only for an indicative analytical
  deflection estimate (section 9, item 8), explicitly not a substitute for the G4 engineering review.
- `stability.foot_footprint_margin_mm` or similar if needed for the tip-over calculation base — derive
  from `case.width`/`case.depth` and foot positions rather than inventing a new literal.

## 1. Module architecture

Package `src/stand_cad/geometry/`: `datums.py` (named datums from `Parameters` only), per-subsystem part
builder modules (`frame.py`, `panels.py`, `trays.py`, `organizer.py`, `dividers.py`, `kinematics.py`,
`services.py`), `assembly.py` (composes the four TZ section 13 states), `export.py` (STEP export with
CONCEPT/REFERENCE_ONLY naming). Entry point: `scripts/generate_model.py`, idempotent.

## 2. Part list, IDs, and material tags (explicit — no wildcards; TZ section 13 one-body-one-code)

| Part ID | Description | Material / thickness | Source |
|---|---|---|---|
| `FRAME-POST-FL-001`, `FRAME-POST-FR-001`, `FRAME-POST-RL-001`, `FRAME-POST-RR-001` | 4 corner vertical posts (Ruling 3 — no merged frame) | Aluminium angle/profile 15x15x1.5 mm | TZ:218 |
| `FRAME-RAIL-BASE-FRONT-001`, `FRAME-RAIL-BASE-REAR-001`, `FRAME-RAIL-BASE-LEFT-001`, `FRAME-RAIL-BASE-RIGHT-001` | 4 base perimeter rails | Aluminium angle/profile 15x15x1.5 mm | TZ:218 |
| `FRAME-RAIL-TOP-FRONT-001`, `FRAME-RAIL-TOP-REAR-001`, `FRAME-RAIL-TOP-LEFT-001`, `FRAME-RAIL-TOP-RIGHT-001` | 4 top perimeter rails (support `TOP-STRUCTURE-001`) | Aluminium angle/profile 15x15x1.5 mm | TZ:218 |
| `FRAME-RAIL-ORG-FRONT-001`, `FRAME-RAIL-ORG-REAR-001`, `FRAME-RAIL-ORG-LEFT-001`, `FRAME-RAIL-ORG-RIGHT-001` | 4 rails at Z=350 supporting `ORG-FLOOR-001` | Aluminium angle/profile 15x15x1.5 mm | TZ:218 |
| `FRAME-RAIL-TRAY-LOWER-001`, `FRAME-RAIL-TRAY-UPPER-001` | Rail pairs carrying each tray's `SLIDE-*` mounts (2 members each; index `-L`/`-R`) | Aluminium angle/profile 15x15x1.5 mm | TZ:218 |
| `PANEL-OUT-FRONT-001`, `PANEL-OUT-REAR-001`, `PANEL-OUT-LEFT-001`, `PANEL-OUT-RIGHT-001` | Outer opal PMMA shell walls | Cast opal PMMA 3 mm, R20-R30 corners, 2-3 mm shadow gaps | TZ:219,230,232 |
| `TOP-STRUCTURE-001` | Top structure/lid | Z 675-690, full 650x550 footprint | TZ section 5 |
| `PANEL-IN-BOTTOM-001` | Inner structural base panel | White composite 3-4 mm | TZ:220 |
| `PANEL-IN-REAR-001` | Inner rear service panel (carries `SVC-INSERT-*`, `MAINS-INLET-001`) | White composite 3-4 mm | TZ:220,204 |
| `PANEL-IN-MID-001` | Inner partition between plotter 1 and plotter 2 zones | White composite 3-4 mm | TZ:220 |
| `TRAY-LOWER-001`, `TRAY-UPPER-001` | Tray platforms | Sandwich/honeycomb 10-12 mm | TZ:221 |
| `SLIDE-LOWER-LEFT-001`, `SLIDE-LOWER-RIGHT-001`, `SLIDE-UPPER-LEFT-001`, `SLIDE-UPPER-RIGHT-001` | Full-extension slide pairs (simplified rail volumes) | Hardware, `to_measure` cross-section | TZ:181-182 |
| `SOFTSTOP-LOWER-001`, `SOFTSTOP-UPPER-001` | Soft stops per tray | Elastomer, `to_measure` size | TZ:185 |
| `VIBMOUNT-P1-001..004`, `VIBMOUNT-P2-001..004` | 4 vibration mounts per plotter (8 total) | Elastomer, `to_measure` size | TZ:185 |
| `ORG-FLOOR-001` | Organizer floor | Sandwich panel 10-12 mm | TZ:222 |
| `ORG-INSERT-001` | Replaceable low-friction floor insert | Thin HDPE-class insert | TZ:160 |
| `ORG-COMB-RAIL-001` | Bottom comb rail carrying divider retention slots | Same panel family as `ORG-FLOOR-001` or a bonded strip | TZ:156 |
| `DIVIDER-###` (parametric, count = `cells - 1`) | Film dividers | Transparent PETG/PC 2 mm, height 300-315, depth 505, finger cutouts R25-R35 | TZ:223,159 |
| `RETAINER-001` | Removable front retainer | 40-50 mm tall | TZ:158 |
| `FOOT-001..004` | Non-slip feet | >=30 mm dia, 8-10 mm tall | TZ:224,300 |
| `HANDLE-001`, `HANDLE-002` | Side handles | >=110x35 mm grip, near computed CoM | TZ:235,304 |
| `SVC-INSERT-L1-001`, `SVC-INSERT-L2-001` | Replaceable feed-slot service insert per level | Own small part; `verify_on_real_machine=True` | TZ:204 |
| `EDGEGUARD-L1-001`, `EDGEGUARD-L2-001` | Brush/radius edge guard at each media-path opening | Soft trim, `to_measure` profile | TZ:200 |
| `REARSUPPORT-L1-001`, `REARSUPPORT-L2-001` | Removable/foldable rear support for long material, per level | `to_measure` geometry | TZ:199 |
| `COVER-SVC-001` | Rear/bottom service cover | White composite | TZ:234 |
| `MAINS-INLET-001` | Single rear mains inlet w/ strain relief | Hardware volume | TZ:283 |
| `LIGHT-STRIP-001` | Simplified RGBW COB strip + aluminium heat-sink volume | `service_volume` | TZ:253 |
| `ADAPTER-LIGHT-001` | Lighting power supply simplified volume | `service_volume` | TZ:402 |
| `CTRL-RGBW-001` | RGBW controller simplified volume | `service_volume` | TZ:402 |
| `ADAPTER-P1-001`, `ADAPTER-P2-001` | Plotter power adapter simplified volumes, vented side pockets | `service_volume` | TZ:289,402 |
| `CABLE-CH-001` | Cable channel simplified volume(s) | `service_volume` | TZ:402 |
| `AIRPATH-001` | Air path simplified volume(s) | `service_volume` | TZ:402 |
| `ENV-PLOTTER1-001`, `ENV-PLOTTER2-001` | Protective design envelopes (reference, not manufactured) | `reference_envelope` | TZ:143 |
| `EQUIP-PLOTTER1-001`, `EQUIP-PLOTTER2-001` | Physical plotter body placeholders | `equipment_reference` | TZ section 3/5 |
| `LID-ENVELOPE-P1-001`, `LID-ENVELOPE-P2-001` | Provisional open-lid swept volumes | `reference_envelope`, `verify_on_real_machine=True` | TZ:16 item 3 |
| `INTERLOCK-SHUTTLE-001` | Captive vertical shuttle, 3 positions (neutral / blocks-upper / blocks-lower) | Hardware volume | TZ:186 |
| `INTERLOCK-TAB-LOWER-001`, `INTERLOCK-TAB-UPPER-001` | Tray-mounted tabs that drive the shuttle | Hardware volume | TZ:186 |

**Explicit exclusion (simplified-hardware policy):** M4 fasteners, threaded inserts, and individual
screws (TZ:225) are out of scope as discrete solids at this concept stage; state this exclusion in the
Final Report rather than omitting it silently. Left/right slide and vibration-mount pairs, and every
identical frame member (posts, base rails, top rails, organizer rails), are modeled as distinct
individual solids at their own positions (Ruling 3) — never one merged body standing in for several —
while sharing a common base part-ID/type for a future BOM quantity rollup (e.g. type `FRAME-POST` at
quantity 4, instances `-FL`/`-FR`/`-RL`/`-RR`).

## 3. Coordinate datums (TZ section 5, lines 122-128)

Origin at the bottom-front-left corner: X `[0, case.width]`, Y `[0, case.depth]`, Z `[0, case.height]`,
all from `Parameters`. Encode all TZ section 5 coordinate-chain rows as named datum objects. Add a
geometry-level test that measures the built solids' bounding boxes and re-derives `plotter.upper_y -
plotter.lower_y == 150` from the actual solid placements (not re-reading the parameter file), so a
datum-wiring bug is caught even when `parameters.yaml` itself is correct.

## 4. Envelope centering — verified, not assumed

Use the offsets from section 0. Build `ENV-PLOTTER1-001`/`ENV-PLOTTER2-001` at the confirmed coordinates
above. Required test: boolean intersection between the two envelope solids has zero volume, and the
measured Z clearance equals the `Parameters`-derived `28` mm (not a hardcoded literal). If any other
placed solid pair unexpectedly intersects, do not silently re-center; report it in
`docs/10_USER_INPUT_REQUIRED.md` and stop only that part's placement, continuing everything else.

## 5. Divider system — concrete retention mechanism

`ORG-COMB-RAIL-001` sits on `ORG-FLOOR-001` and carries one slot per divider position (`divider_count`
slots for the current `cells`), each slot width = `film_storage.divider_thickness +
film_storage.comb_slot_clearance_mm` (derived from `tolerance.part_assembly_feature_mm`), depth =
`film_storage.comb_slot_depth_mm`. `DIVIDER-###` engages the slot from above (open vertical withdrawal —
lift straight up, no disassembly of the case, satisfying TZ:156) and its position along X is
`film_storage.x + i * (cell_width_mm + divider_thickness)`, computed from `Parameters` for the loop
`i in range(divider_count)`, never a literal. `RETAINER-001` at the front prevents dividers/film sliding
out forward during transport. Regenerate and test for every `cells` in `6..12`: correct divider and slot
count, non-degenerate solids, and each divider's bottom engaging its slot without intersecting the rail
body (contained/touching, not clipped).

## 6. Media path (TZ section 7)

Per-level clear path width >= `media_path.clear_width` (330), slot height >=
`media_path.clear_height_min` (12, target `slot_height_target` 18). `SVC-INSERT-L1-001`/`-L2-001` own
the feed-plane-dependent geometry (positioned from `plotter.feed_plane_z_provisional_mm`, tagged
`verify_on_real_machine=True`) so a future measurement only touches these two parts.
`EDGEGUARD-L1-001`/`-L2-001` close the slot edges. Sweep both TZ test bodies
(`media_path.test_body_primary`, `media_path.test_body_long`) through each level's path at several Y
positions (parametrized test) and assert zero contact with any part other than the intended support
surfaces (an explicit touching allowlist, see section 9).

## 7. Tray kinematics and interlock — corrected arithmetic, selected mechanism

**Corrected travel arithmetic** (principal-arbiter correction to revision 1, which had the sign wrong):
extension is a translation of the tray/plotter assembly by `-extension_mm` along Y. Resulting rear-face
Y position = `original_rear_y - extension_mm`. With minimum extensions: lower `196 - 250 = -54`; upper
`346 - 400 = -54`. Both are `14` mm past the required `Y = -40` plane (i.e., `-54 <= -40`, with a `14`
mm margin) — TZ is self-consistent. Write this as a geometry measurement test on the actual translated
solid, not a hand-computed literal: assert `rear_face_y <= -front_overhang_min_mm` (`trays.
front_overhang_min_mm`, currently `40`, sign-adjusted) after applying the modeled extension transform.

**Lid opening:** tray extension alone does not prove the lid fully opens (principal-arbiter finding).
Model `LID-ENVELOPE-P1-001`/`-P2-001` (provisional swept volumes per section 0) attached to each
plotter's service position and assert they do not intersect `PANEL-IN-MID-001`, `PANEL-OUT-*`, or the
other plotter's parts in that service state. Mark this check `verify_on_real_machine=True` since the
lid envelope itself is provisional.

**Interlock mechanism (selected, concrete):** one `INTERLOCK-SHUTTLE-001` captive in a vertical channel
between the two slide zones, with three explicit Z positions: neutral (both trays closed), blocks-upper
(driven up by `INTERLOCK-TAB-LOWER-001` when the lower tray extends — the shuttle occupies a slice of
the upper tray's slide path), blocks-lower (driven down by `INTERLOCK-TAB-UPPER-001` when the upper tray
extends). Required test: build the service-plotter-1 state (lower extended, shuttle at blocks-upper) and
boolean-intersect the shuttle with the upper tray's fully-extended swept volume — must be non-zero
(interference), proving the upper tray cannot reach full extension while the shuttle is in that
position. Repeat symmetrically for service-plotter-2. This is the required "not just a Python boolean
flag" mechanical evidence — discrete-state proof is sufficient for this concept stage (Ruling 4). A
continuous swept-envelope proof over the shuttle's full travel path is out of scope here; Packet 2 must
add `A-011` to `state/ASSUMPTIONS.md` recording that deferral (owner, validation action = "detailed-
design swept-volume interference simulation", resolve-by = a future detailed-design gate, status Open).

## 8. Output and STEP naming

`scripts/generate_model.py` rebuilds idempotently (run twice; assert identical measured volumes/bounds,
or byte-identical STEP if export is deterministic) and exports an assembly STEP under `output/` with a
filename containing both `CONCEPT` and `REFERENCE_ONLY`, e.g.
`output/concept/light_plotter_tower_ASSEMBLY_CONCEPT_REFERENCE_ONLY_rev1.step`. After export, read the
STEP back (build123d import or the MCP `import_cad_file` tool) and assert non-zero solids and matching
overall bounding box — required "STEP read-back" evidence (TZ master-prompt final paragraph). Validation
evidence goes under `output/validation/<revision>/`. No PDF/DXF. No gate marked passed; no
`PROTOTYPE_RELEASED`/`SERIES_RELEASED` anywhere.

## 9. Tests (add to `tests/`, keep all 40 existing tests passing and unmodified)

Every new assertion cites the `tolerance.*` group from `Parameters`, never a new hardcoded tolerance.
Each new test module opens with the comment: "A passing test is not evidence of physical correctness."

1. Overall assembly bounding box == `(650, 550, 690)` within `tolerance.assembly_mm`.
2. Each plotter physical body measures `(566, 176, 124)` at the documented coordinates.
3. Setback between plotter front faces == exactly `150`, measured from built geometry (section 3).
4. Envelope-vs-envelope: zero 3D intersection volume; measured Z clearance == derived `28` mm (section 4).
5. Organizer clear volume >= `(610, 510, 325)`.
6. Defaults `cells=10` -> `cell_width_mm ~= 59.2`, `divider_count == 9`; geometry regenerates correctly
   (right divider/slot count, non-degenerate solids, dividers seated in slots) for every `cells` in `6..12`.
7. A `320x500` mm film body stands vertically in a cell without intersecting the case, >=5 mm headroom.
8. Both media-path test bodies pass through each level at multiple Y positions without unintended contact
   (explicit allowlist of intended support-surface contact).
9. Each tray reaches its required extension; rear-point-40-mm-clear condition holds using the corrected
   translation arithmetic (section 7); lid-open envelope does not intersect surrounding parts in each
   service state (`verify_on_real_machine`-tagged check).
10. Interlock: in service-plotter-1 state, shuttle-vs-upper-extended-swept-volume intersection is
    non-zero (blocked); symmetric check for service-plotter-2; in transport state the shuttle is neutral
    and intersects neither tray's closed volume.
11. Per-pair, per-state numeric collision/clearance check (Ruling 5) across **all four** TZ section 13
    states (transport, service-1, service-2, operating-with-test-bodies): every part is a valid solid.
    Maintain an explicit **mating-pairs list** by exact part-ID pair (feet-to-floor-plane,
    divider-to-comb-slot, tray-to-slide, panel-to-frame shared faces, etc.) where zero-distance contact
    is expected; for every other pair, measure the minimum clearance and assert it is `>=
    tolerance.part_assembly_feature_mm` (`0.5` mm, reused — not a second hardcoded `0.5`) unless a more
    specific TZ-derived clearance applies to that pair, and fail if two non-mating parts touch at zero
    distance. For `contained` pairs (e.g., `EQUIP-*` inside `ENV-*`) assert the equipment volume's
    intersection with the envelope equals the equipment volume itself within tolerance (true
    containment). Record the threshold actually used for each category in the validation report.
12. Single mains inlet: exactly one `MAINS-INLET-001`; no part IDs represent a laptop, monitor, or
    router (TZ:511) — a structural registry check, not a geometry check.
13. Indicative-only analytical checks, each explicitly labeled non-authoritative for G4: tip-over
    stability factor >= `stability.tip_factor_min` for the worst-case one-tray-extended state using
    modeled foot footprint and `mass_targets`/equipment mass values; tray deflection under
    `trays.design_load_kg` <= `trays.deflection_max_mm` using the indicative stiffness parameter from
    section 0; empty-case mass <= `mass_targets.empty_case_max_kg` from modeled part volumes times
    `materials.*_density_kg_m3`. Each test/report must state in its assertion message or docstring that
    it is indicative and not a substitute for the Phase 4 / Gate G4 engineering review.
14. Idempotent rebuild: running the generator twice yields measurably identical geometry (bounding boxes
    and volumes match within a tight numerical tolerance, or byte-identical STEP).
15. STEP read-back: exported STEP re-imports with non-zero solids and matching overall bounding box.

Explicitly **out of scope** for this stage (state this in the Final Report, do not silently claim
satisfied): PDF drawings, production DXF, BOM.csv/mass_report.csv as controlled deliverables, full FEA
deflection/stability analysis, lighting photometric review, DFM. Do not mark PLT-010 through PLT-015 as
fully `DONE` in `state/REQUIREMENTS_TRACEABILITY.csv` — record indicative/partial status with a note
pointing at what remains (full G4 analysis, drawings stage, etc.).

## 10. Review focus for the mandatory adversarial pass

Hunt specifically for: (a) any literal dimensional number in geometry code that should come from
`Parameters`; (b) any part positioned from a `to_measure`/provisional value without a traceable
`verify_on_real_machine` tag; (c) a test that asserts something trivially true (loose tolerance, literal
compared to itself, or a collision check that can't fail because the allowlist marks everything
`disjoint`); (d) any interpenetration the suite would miss (states not covered, containment pairs
mislabeled as `disjoint`, or vice versa); (e) whether the interlock evidence is a real boolean
interference result or just a Python flag; (f) whether indicative analytical claims (mass, tip factor,
deflection) are clearly labeled non-authoritative everywhere they appear. Findings need path, lines, the
requirement ID from `state/REQUIREMENTS_TRACEABILITY.csv` (PLT-001..017; add new PLT IDs for
requirements introduced in this stage that have no existing row), and reproducible evidence.

## 11. Verification commands (must all exit 0, run by the `verifier` role)

- `uv run pytest` — all previous 40 tests plus new tests pass.
- `uv run ruff check .` — clean.
- `powershell -ExecutionPolicy Bypass -File .\scripts\setup_windows.ps1` — full run, exit 0.

## 12. Sequential Work Packets (same sole-writer `implementer`; no `principal-arbiter` this stage per
Main's tier ruling)

Run `uv run pytest` and `uv run ruff check .` after each packet; do not start the next packet on a red
suite.

- **Packet 0 (administrative, do first, part of Packet 1's turn) — record Main's rulings.** Add the
  exact T2/T3 boundary from Main's Ruling 1 to `state/DECISION_LOG.md` (new entry, cite this plan and
  the ruling); reflect the qualified rule in `.cursor/rules/21-orchestration-overlay.mdc` (edit the tier
  floor bullet so the next agent reads the qualified rule directly rather than re-deriving it from
  Main's chat ruling). These are governance/state files, not geometry code, and are explicitly
  authorised for the implementer to write this turn.
- **Packet 1 — static structure.** Section 0 parameters needed for static parts; `datums.py`; part
  registry/tagging convention (part ID, material, `verify_on_real_machine` flag); the decomposed
  `FRAME-POST-*`/`FRAME-RAIL-*` members, `PANEL-OUT-*`, `TOP-STRUCTURE-001`, `PANEL-IN-*`,
  `ORG-FLOOR-001`, `ORG-INSERT-001`, `FOOT-*`, `HANDLE-*`, `EQUIP-PLOTTER*`, `ENV-PLOTTER*` and the
  envelope-intersection test (item 4), overall bounding box test (item 1), plotter body test (item 2),
  setback test (item 3), organizer clear-volume test (item 5).
- **Packet 2 — trays, kinematics, interlock.** `TRAY-*`, `SLIDE-*`, `SOFTSTOP-*`, `VIBMOUNT-*`,
  `LID-ENVELOPE-*`, `INTERLOCK-SHUTTLE-001`, `INTERLOCK-TAB-*`; the four TZ section 13 states in
  `assembly.py`; tests 9, 10, and the all-state numeric collision/clearance check (test 11) for parts
  that exist by end of this packet; add `A-011` to `state/ASSUMPTIONS.md` for the swept-envelope
  deferral (Ruling 4).
- **Packet 3 — organizer detail, media path, services, export, remaining tests.** `ORG-COMB-RAIL-001`,
  `DIVIDER-###`, `RETAINER-001`, `SVC-INSERT-*`, `EDGEGUARD-*`, `REARSUPPORT-*`, `COVER-SVC-001`,
  `MAINS-INLET-001`, `LIGHT-STRIP-001`, `ADAPTER-*`, `CTRL-RGBW-001`, `CABLE-CH-001`, `AIRPATH-001`;
  `scripts/generate_model.py`; STEP export/read-back; idempotence; tests 6, 7, 8, 12, 13, 14, 15; final
  full all-state collision allowlist covering every part; `state/REQUIREMENTS_TRACEABILITY.csv` updates.

Adversarial review runs once, after Packet 3, against the fully integrated result (not after each
packet) per the overlay's cycle-cap discipline; the verifier's full command run (section 11) also runs
once, after review findings are closed.
