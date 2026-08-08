# CAD modeling conventions

Mechanical, evidence-based rules from real defects found and fixed in this repository. Not generic CAD advice — every rule cites the file/line or decision that motivated it. Read this before re-deriving a fix that already has a documented precedent.

## 1. Cladding must share the covered rail's X/Z span (thin 3 mm front face)

Cosmetic opal cladding (`PANEL-CLAD-FRONT-*`, D-026) is a **3 mm-thick front-face strip** flush-mounted on the visible side of each covered rail/post, not a full-profile-depth block. It must reuse the **same X span and Z span** as the structural member it covers:

- Perimeter BASE/ORG rails: same `[inset, width-inset]` X and `z_base`/`z_top` as `_perimeter_rail()` (`frame.py`), with **Y depth = `materials.outer_panel_thickness_mm` (3 mm)** at the open front (Y=0).
- Tray-rail cladding: same X/Z bounds from `_tray_frame_rail_bounds()` (`trays.py`), with **Y from rail `y0` to `y0 + outer_panel_thickness_mm`**.
- Post cladding: same X/Z post cover spans as before, **Y depth 3 mm** at the front face.

Do not revert to a 15 mm profile-depth block — that contradicted D-026 "thin opal cosmetic covers" and overstated mass. Render tie-break (§2) still applies where the 3 mm strip overlaps the rail front face in Y.

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

## 7. Side-slab cavity bearing joints: X overlap, not full confinement

Corner posts (`FRAME-POST-FL/FR/RL/RR-001`) span the **20 mm wall pocket plus an inward leg (~40 mm X)** after the D-055 cavity-wall rebuild. `is_side_slab_frame_cavity_joint()` (`collision.py`) must classify **zero-clearance bearing** on the 3 mm opal skin as legitimate mating, but reject solid-acrylic burial (~428×10³ mm³ synthetic at a corner post — far above `max_bearing`≈56×10³; the old ~50–85×10³ band overlapped `max_bearing` and was not a reliable rejection oracle).

The X-band gate tests **overlap with the pocket band** `[0, side_clear]` (left) or `[width − side_clear, width]` (right), **not** confinement of the entire frame bbox inside `side_clear`. For `FRAME-POST-*`, a **Y-band gate** also requires overlap with the front return `[0, side_clear]` or rear return `[depth − side_clear, depth]` so mid-wall skin burial cannot exempt on X overlap alone. Measured transport (2026-08-06): `FRAME-POST-FL-001` X=(0, 40), Y=(0, 40), `inter_vol`≈47 830 mm³, `max_bearing`≈56 175 mm³, clearance 0.000 mm — all four post↔side-slab pairs pass `test_numeric_collision_clearance` at 0.000 mm clearance; volumes above `_max_legitimate_skin_bearing_volume_mm3` and mid-wall posts still reject.

## 8. Assembly cache must return copied solids, not shared OCCT children

`_STATIC_PARTS_CACHE` / `_STATE_CACHE` (`assembly.py`) store canonical `PartRecord` solids for performance. Every cache hit must return **`_copy_parts()`** — shallow `PartRecord` copies with `copy(solid)` per part (same pattern as `translate_solid()` in `primitives.py`). Without this, two successive `AssemblyState.compound()` calls share OCCT topology: the first compound's bbox collapses to `(3, 3, 12)` mm (= `INTERLOCK-TAB` size) while the second reads `(650, 420, 544)` mm — `test_idempotent_rebuild_matching_metrics` fails even though the builder is deterministic.

## 9. Drop-front doors — closed-plane mating and strut routing (D-073 / D-076)

`DOOR-LOWER/UPPER-001` sit on the tray front plane (Y = datum.y.min). Zero clearance vs trays, slides, plotters, tray cladding, org-front rail, and tier divider is **expected closed-front contact** — classify via `collision.py::is_door_mate`, not as a defect. **`PANEL-IN-MID-001`** front Y is retracted to the closed-door / tray front plane (`datums.plotter1_physical.y.min_mm`, FIX-COLL-002 Path A) — the inner divider must not protrude ahead of the door slab. Door ↔ mid and door ↔ softstop mates use the same **`DOOR_FRONT_PLANE_MAX_BEARING_MM3`** (500 mm³) closed-posture ceiling as tray/slide front mates; open horizontal doors require `inter_vol <= threshold` only. Media-path front sweeps must **exclude `DOOR-*`** (intentional closed barrier) while keeping rear-channel checks honest.

**Open-door settle (D-076 / D-089):** after 90° hinge swing, door translates down so top face ≤ `slide_bottom_z − tolerance.assembly_mm` where `slide_bottom_z = datum_z − tray_panel_thickness_mm − slide_rail_height_mm` (Path A). **`FRAME-RAIL-BASE-FRONT-001`** carries a clearance notch through the settled door Z band (`frame.py::_base_front_clearance_notch_x_z`); at the current +11 mm stack, live open-door ∩ rail **0 mm³**. **`PANEL-IN-BOTTOM-001`** front pocket (`panels.py::_open_door_bottom_panel_notch_bounds`) is **defensive** — primary clearance at current stack is the measured **≈1.5 mm** air gap (slide-bottom / height-stack reserve), not volumetric subtraction. Open posture mates use **`inter_vol <= threshold` only** (no volume allowlist).

**Open-door struts (`DOOR-STRUT-*`):** route along **corner-post outer faces** at settled door Z — outside tray X-span. Struts **always emitted** when door is open. Strut ↔ post/panel attachment capped at **`DOOR_STRUT_MAX_BEARING_MM3`** (350 mm³); TRAY/SLIDE/EQUIP kinematic targets require vol≈0 (`test_lower_open_door_kinematic_clearance_sweep`). Open horizontal doors detected via **`_door_is_open_horizontal()`** — closed-plane 500 mm³ ceiling applies to **closed posture only**.

## 10. Open-front kinematic contact — intersection-volume ceiling (D-080)

Front perimeter structure (`PANEL-CLAD-FRONT-*`, `FRAME-RAIL-BASE-FRONT-*`, `FRAME-RAIL-ORG-FRONT-*`) legitimately touches the travelling tray/slide/plotter stack at the open front opening — zero clearance with small skin/plane bearing is expected. **`is_open_front_kinematic_contact()`** and the four front clad/rail **`PENETRATING_JOINT_PATTERNS`** (clad/rail ↔ `TRAY-LOWER-*` / `SLIDE-LOWER-*`) exempt only when `intersection_volume <= OPEN_FRONT_MAX_BEARING_MM3 + threshold` (**750 mm³** ceiling; live max **540 mm³** measured 2026-08-08 across transport / service_p1 / tray1_qa). Deep volumetric burial (~1e6 mm³ synthetic) must **not** silent-green. Door ↔ `PANEL-IN-MID-001` / `SOFTSTOP-*` closed-posture mates follow the same volume-ceiling pattern via **`is_door_mate`** and **`DOOR_FRONT_PLANE_MAX_BEARING_MM3`** (D-084; live DOOR-LOWER ↔ MID **5985 → 0 mm³** after Path A trim).

## 10a. Non–open-front penetrating joints — per-class volume ceilings (D-092)

Largest uncapped non–open-front **`PENETRATING_JOINT_PATTERNS`** pairs are gated by class-specific ceilings in **`is_penetrating_structural_joint()`** — same predicate shape as §10 open-front (reject when `intersection_volume > class_ceiling + threshold`; no global penetrating default). Live maxes measured in **transport** posture (2026-08-08). **`PANEL-IN-`/`FRAME-` `_share_face_if_prefix`** does **not** bypass ORG-REAR or POST↔PANEL-IN — pairs matching `ORG_REAR_PENETRATING_PATTERNS` or `POST_PANEL_PENETRATING_PATTERNS` defer to the capped penetrating predicate (D-092 cycle 2; D-093).

| Pattern class | Constant | Ceiling (mm³) | Live max (2026-08-08 transport) |
|---|---|---|---|
| `FRAME-RAIL-ORG-` ↔ `PANEL-IN-REAR-` | `ORG_REAR_PENETRATING_MAX_BEARING_MM3` | **35000** | **31500** (`FRAME-RAIL-ORG-REAR-001` ↔ `PANEL-IN-REAR-001`) |
| `SLIDE-UPPER-` / `TRAY-UPPER-001` / `SOFTSTOP-UPPER-001` ↔ `PANEL-IN-MID-001` | `MID_UPPER_PENETRATING_MAX_BEARING_MM3` | **35000** | **30712.5** (`SLIDE-UPPER-*` ↔ MID; TRAY/SOFTSTOP ↔ MID same family, live vol≈0) |
| `FRAME-POST-` ↔ `PANEL-IN-` | `POST_PANEL_PENETRATING_MAX_BEARING_MM3` | **25000** | **18652.9** (`FRAME-POST-RR/RL-001` ↔ `PANEL-IN-REAR-001`) |

Deep synthetic burial ≫ ceiling must **not** silent-green (including coplanar AABB-face burial for ORG-REAR and POST↔PANEL-IN). **`OPEN_FRONT_MAX_BEARING_MM3`** (**750 mm³**) and §10 behavior unchanged (D-080).

**Residual uncapped penetrating classes (P2):** `FRAME-RAIL-TRAY-` ↔ `PANEL-IN-` (live max **10237.5 mm³**); `INTERLOCK-TAB-` ↔ `PANEL-IN-` (uncapped — not re-measured this cycle); `FRAME-RAIL-BASE-REAR-` ↔ `MAINS-INLET-` (uncapped — out of scope); `COVER-SVC-001` ↔ `FRAME-POST-R*` (~**123 mm³**). Cap in a follow-on cycle — do not apply a single global ~40k ceiling.

## 11. Kinematic-group mates — no blanket exemption (D-086)

**Do not** treat shared `LOWER_KINEMATIC_GROUP` / `UPPER_KINEMATIC_GROUP` membership as an unconditional `is_mating` pass — that greenwashed deep burial (e.g. synthetic TRAY↔EQUIP). Intentional same-group contacts must be on **`MATING_PAIRS`**, **`is_door_mate`**, **`is_open_front_kinematic_contact`**, INTERLOCK/face helpers, or a measured skin ceiling.

**Slide ↔ vibration mount (`is_slide_vibmount_bearing`):** eight live pairs (`SLIDE-LOWER-*` ↔ `VIBMOUNT-P1-*`, `SLIDE-UPPER-*` ↔ `VIBMOUNT-P2-*`) show plane-touch only — live max **0 mm³** (2026-08-08 transport). Exempt when `intersection_volume <= SLIDE_VIBMOUNT_MAX_BEARING_MM3 + threshold` (**500 mm³** ceiling). Deep burial must fail. **`EQUIP-PLOTTER*`** ↔ **`SOFTSTOP-*`** are **not** on `MATING_PAIRS`; live transport keeps **0.5 mm** clearance — no mate rule needed.

**Equipment seating (`is_equip_seating_bearing`):** eight live pairs (`EQUIP-PLOTTER1-*` ↔ `TRAY-LOWER-*` / `SLIDE-LOWER-*`, `EQUIP-PLOTTER2-*` ↔ `TRAY-UPPER-*` / `SLIDE-UPPER-*`) on `MATING_PAIRS` show plane-touch only — live max **0 mm³** (2026-08-08 transport). Exempt when `intersection_volume <= EQUIP_SEATING_MAX_BEARING_MM3 + threshold` (**500 mm³** ceiling). Deep burial must fail.

**Tray ↔ slide (`is_tray_slide_bearing`, D-089):** six live pairs on `MATING_PAIRS` — slide Z-stack sits **fully below** the tray platform (`_slide_bounds` anchors slide top at `tray_bounds[2]` = true tray bottom, not index `[5]` tray top). Pre-fix wrong unpack buried slide through full tray thickness (~96525 mm³ L/R, ~93802 mm³ center). Post-fix live max **0 mm³** (2026-08-08 transport / service_p1). Exempt when `intersection_volume <= TRAY_SLIDE_MAX_BEARING_MM3 + threshold` (**500 mm³** ceiling). Frame rails share the same Z anchor via `_tray_frame_rail_bounds` (`z_base = z_tray_bottom − rail_h − profile`). Door open settle uses `slide_bottom_z = datum_z − tray_panel_thickness − slide_h` (D-076 intent preserved).

**Vibration mount ↔ equipment (`is_vib_equip_bearing`, D-091):** eight live pairs (`VIBMOUNT-P1-*` ↔ `EQUIP-PLOTTER1-*`, `VIBMOUNT-P2-*` ↔ `EQUIP-PLOTTER2-*`) on `MATING_PAIRS` show full 20×20×5 mm pad embed — live **2000 mm³** exactly (2026-08-08 transport). Exempt when `intersection_volume <= VIB_EQUIP_MAX_BEARING_MM3 + threshold` (**2500 mm³** hygiene ceiling). No beyond-pad live burial claim; fix closes D-087 residual P2 for this pair class only. Deep burial must fail.

Other `MATING_PAIRS` (SOFT↔TRAY, INTERLOCK, shelf/org, media, mains, …) remain uncapped — D-087 residual P2 where applicable.
