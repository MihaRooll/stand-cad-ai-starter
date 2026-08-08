# Consolidated user input required

The Light Plotter Tower technical specification (`ИИ советы/Cursor_Opus5_TZ_Light_Plotter_Tower.md`) is the authoritative requirement source (D-011). At adoption it settled equipment selection (two Silhouette Cameo plotters), operating scenario, appearance, and an initial layout and overall-dimension baseline. Owner instruction on 2026-08-04 during PLT-007 later overrode parts of that baseline: the governing machine is now Silhouette Cameo 4, tier setback and overall height differ from the TZ figures, and the film organizer layout changed — see `state/DECISION_LOG.md` D-025, D-027, D-028, D-029, D-032, and D-033 and the `DEVIATED`/`IN_PROGRESS` rows PLT-001/002/003/004/006/018/019/020/021 in `state/REQUIREMENTS_TRACEABILITY.csv`. The current model follows those post-TZ decisions, not the original TZ numbers verbatim. Only the items below remain unresolved.

## A. Physical measurements on real equipment (TZ section 16)

**Cameo 4 governing dimensions CLOSED (2026-08-04):** width 570 mm, depth 195 mm, height 170 mm, mass 4.7 kg — Silhouette Cameo 4 spec sheet. Cameo 5 slot-2 mass 5.2 kg confirmed. Service-port **connector type** remains open (`hardware.service_port_*` cutout is provisional `to_measure`).

Before releasing production files, measure on two real plotters:

1. Feed-plane height above the machine's lower support plane — unblocks `plotter.feed_plane_z_from_base`.
2. Rear material exit coordinates.
3. Cameo 4 (tier 1 / slot 1): open-lid hinge axis, swing radius, fully-open lid height, and opening direction — unblocks `plotter.lid_open_envelope_height_mm` and any future hinge model for `LID-ENVELOPE-P1-001`.
4. Cameo 5 (tier 2 / slot 2): open-lid hinge axis, swing radius, fully-open lid height, and opening direction — same leaves for `LID-ENVELOPE-P2-001`.
5. Power and USB connector coordinates.
6. OEM power adapter dimensions and minimum cable bend radius.
7. Plotter foot positions and drill-free fixing points.
8. Real thickness and stiffness of the films actually used — unblocks `film_storage_horizontal.min_stack_height_mm`.
9. Actual thickness of all purchased sheet materials — unblocks `materials.actual_sheet_thickness_mm`.

After measuring, update `config/parameters.yaml`, regenerate the model, repeat collision checks, and only then remove `VERIFY ON REAL MACHINE` markings from production drawings (TZ section 16 closing paragraph).

## B. Manufacturing authorization

Manufacturer DFM authorization remains open and is not addressed by the TZ. Before Gate G5 the owner must authorize which vendors may receive the RFQ package and approve the selected prototype quotation, per ADR-003 and `docs/05_IMPLEMENTATION_PLAN.md`.

## C. Tray deflection under design load (PLT-011 / TZ line 184) — indicative model only (D-035, 2026-08-04)

**Status:** Two-rail single-span indicative model (`output/validation/rev6/deflection_report.md`) yielded **3.644 mm**
mid-span deflection under the 10 kg design load with rail-to-rail span 570 mm (`plotter.physical_width`,
Cameo 4 governing) and load distributed along 195 mm (`plotter.physical_depth`) with unsourced sandwich
panel stiffness `materials.tray_panel_youngs_modulus_mpa` (3000 MPa, `to_measure`) — this **exceeded** the
1.5 mm TZ ceiling. **Fix (D-035):** added a third centre slide rail plus a fixed frame rail at each tray
level (`SLIDE-{LOWER,UPPER}-CENTER-001`, `FRAME-RAIL-TRAY-{LOWER,UPPER}-C-001`), bisecting the 570 mm span
into two ≈285 mm half-spans. Conservative half-span model (P/2 on L/2, ignoring elastic continuity at the
centre support) gives **≈0.228 mm** mid-span deflection — the **indicative model meets the 1.5 mm ceiling**
under the current unsourced E assumption (~6.6× margin). Panel thickness (10–12 mm) and E remain `to_measure`;
**NOT closed pending physical measurement** — the ceiling fails only if measured E falls below **≈456 MPa**
(3000 × 0.228/1.5). See `output/validation/rev11/deflection_report.md`,
`state/REQUIREMENTS_TRACEABILITY.csv` PLT-011 (`IN_PROGRESS` — indicative model only, not FEA), and
assumption **A-012**.

## D. Side-slab front-corner rounding (TZ section 8 line 230 / D-025) — **CLOSED**

With fixed `case.width`=650 mm and `case.internal_width`=610 mm, `side_clear`=(650−610)/2=**20 mm exactly**. A full bullnose on a 20 mm-thick side slab cannot exceed **R10** (= `side_clear`/2) before the edge becomes a full round. TZ line 230 asks for **R20–R30**, which cannot hold simultaneously with the TZ's own 610 mm clear-width floor once 650 mm overall width is fixed — an **internal conflict inside the TZ**.

**Implemented (rev5):** R10 full bullnose on the **exterior front vertical** edges of both side slabs, **continued along the top-front horizontal edge** (`case.side_slab_bullnose_radius_mm`=10, achieved ≈9.9 mm after width/2−0.1 clamp). Recorded as **DEVIATED** in `state/REQUIREMENTS_TRACEABILITY.csv` row **PLT-018** (D-025).

**Owner decision (2026-08-04):** accepts **option 1 — R10 bullnose at the current 650×610 envelope** (matches rev5 geometry; no dimensional change). **Declined option 2** (grow overall width to 690 mm). **Rejected option 3** (shrink clear width to ~570 mm): that envelope is narrower than the 584 mm protective plotter design width (`plotter.design_width`, `config/parameters.yaml:39`) and would leave only ~2 mm clearance per side where TZ line 89 requires 22 mm. Owner also declined a cosmetic/non-structural overhang workaround.

Curved side-profile massing beyond the bullnose and RGBW photometric glow remain deferred.

## E. Handle mount coordinates and tier-2 intrusion (PLT-007 / D-051)

**Current placement (D-074, 2026-08-07):** `hardware.handle_mount_y_mm` = **179.8 mm** (loaded-case balance-point CoM Y — live recomputation within `tolerance.part_assembly_feature_mm`; retune after FIX-WAVE-003 mass removals; supersedes D-063 **185.9 mm**); `hardware.handle_mount_z_mm` = **252 mm** (unchanged). TZ:304 grip cutout (110×35 mm) on the right side slab (`PANEL-OUT-RIGHT-001`): grip band **Y ≈ [124.8, 234.8] mm**, **Z ≈ [234.5, 269.5] mm**.

**Tier-2 finger intrusion (OPEN blocker):** at Y=185.9 / Z=252 the through-cutout grip volume intersects the tier-2 plotter bay (`EQUIP-PLOTTER2-001`, Cameo 5 **124 mm** body) by **≈1,389,717 mm³** (`handle_finger_intrusion_volume_mm3`, `tests/test_geometry.py::test_handle_tier2_finger_intrusion_at_balance_point`). Tier-1 plotter finger intrusion is **0 mm³**. Service-port aft margin **≈34.1 mm** (port Y=275); cable entry (Y=320, Ø30) nearest edge **≈79.1 mm** aft of grip band.

**Superseded history (do not treat as current):**

| Decision era | Y (mm) | Z (mm) | Grip band Y | Grip band Z | Notes |
|---|---|---|---|---|---|
| D-022 / D-030 | 100 | 276.5 (after D-038) | [45, 155] | [259.0, 294.0] | Side-panel-centred Z; claimed zero encroachment — **false after D-051 balance-point move** |
| D-050 (superseded Y) | 210 | 252 | [155, 265] | [234.5, 269.5] | Geometric depth centre; tier-2 intrusion **987,525 mm³** at Y=210 — superseded by D-051 |

**VERIFY ON REAL MACHINE** before any production release claim on carry ergonomics or final handle concept.

## F. Handle concept choice (D-051) — **OPEN**

D-051 records that the owner **deferred** a handle-concept decision. None of the following is yet chosen; the balance-point through-cutout in §E remains modelled only as an interim carry experiment:

1. **External bolt-on handle** — hardware mounted outside the side slab, avoiding a through-cut into the plotter bay.
2. **Blind pocket in the side slab** — recessed grip without a through-hole into the interior volume.
3. **Low aft cutout behind the plotters** — grip opening in the rear/aft zone, clear of tier-2 finger reach.

Until one option is chosen and modelled, the §E through-cutout intersecting the tier-2 bay by **≈1.39×10⁶ mm³** blocks a production-ready side-panel release. Tracked in `state/DEFERRED_VERIFICATION.md` (D-050/D-051 row).

## G. Rear vent render evidence (PLT-005 rework F-3)

TZ line 290 bottom+rear layout unchanged. Primary transport rear view may still show near-white inner panel through slots; **`output/validation/rev4/views/rear_vent_closeup.png`** (outer rear only, grey backdrop) is the legibility evidence for rear vent grille sign-off.

## H. Cable pass-through opening size (D-036 defer certified inlet; D-047 right-side relocation; D-051 cable Y revert)

Owner simplified TZ section 10's certified rear mains inlet (with retention/strain relief, feeding an internal certified distributor) to a plain grommeted cable pass-through hole for the prototype: he will route a household extension cord/power strip through the hole and plug the plotters and lighting into it himself inside the case. **`SVC-CABLE-PASSTHROUGH-001`** is on **`PANEL-OUT-RIGHT-001`** at **Y=320 mm / Z=120 mm** (D-047; cable Y reverted from D-050's brief Y=330 experiment per D-051), **45 mm aft** of the USB service port at **Y=275 / Z=120**. Two provisional leaves remain open (`to_measure`, A-015): `hardware.cable_passthrough_diameter_mm` (30 mm) and `services.cable_passthrough_grommet_wall_mm` (2 mm → 26 mm clear bore) — chosen in a generous 25–35 mm range for a common plug/cable end, **not measured against the actual cord at the current right-side mount location**. The grommet edge-break radius (`services.cable_passthrough_edge_break_radius_mm`, 1 mm) is settled at TZ:472's own verified R1 value and does not need further measurement.

**To close this item:** measure the outer diameter of the actual extension-cord plug/cable end the owner intends to route through the **right-side** opening, then update `config/parameters.yaml` and regenerate before production DXF release. The certified-inlet path (TZ section 10) remains deferred, not deleted — `MAINS-INLET-001` stays modeled as a placeholder service volume if a future revision reinstates it (D-036).

## I. Tier-2 under-tray hardware vs plotter 1 envelope (F-5) — **RESOLVED (D-038, 2026-08-04)**

**Status:** Closed by Main under the owner's standing autonomy grant (PLT-009). **Option 1 applied:** grew `case.height` by **+27 mm** via corrected `plotter.upper_z` formula — `lower_z + tier_clearance_min_mm + slide_rail_height_mm + frame_profile_size_mm + tray_panel_thickness_mm` = 30 + 170 + 12 + 15 + 11 → `upper_z`=**238**, `case.height`=**544**. Zero `intersection_volume` at all 7 tier-2 under-tray parts × 5 tray-1 positions (35 cases); regression `tests/test_kinematics.py::test_plotter1_clear_of_tier2_under_tray_hardware`; evidence pack `output/validation/rev9/`.

### Problem history (QA sweep cycle 2 quantification, pre-fix)

Scripted `intersection_volume` measurement (build123d) had confirmed a real volumetric overlap between `EQUIP-PLOTTER1-001` (Cameo 4 body, Z=[30, 200]) and tier-2 under-tray mounting hardware. At rest (`lower_extension_mm`=0) the overlap was full; as tier-1 tray travel increased, overlap **decreased roughly linearly** because `EQUIP-PLOTTER1-001` is in `LOWER_KINEMATIC_GROUP` and moves forward with the tray, reducing its Y-overlap with the fixed `FRAME-RAIL-TRAY-UPPER-*` rails. For `EQUIP-PLOTTER1-001` vs `FRAME-RAIL-TRAY-UPPER-L-001` as `lower_extension_mm` increased: dy=0 → 43,875.0 mm³; dy=130 (`trays.lower_quick_access_extension_mm`) → still overlapping ≈14,625.0 mm³; dy=180 → 3,375.0 mm³; dy=194 → 225.0 mm³; dy=196 → 0.0 mm³ (clearance ≈1.0 mm); dy=250 (full `trays.lower_extension` service) → 0.0 mm³ (clearance ≈55.0 mm). **Quick-access (130 mm) had substantial real overlap** — the interference was present at quick-access, not only at rest.

**At rest (closed/transport) — pre-fix volumes:**

| Pair | Intersection volume (mm³) | Notes |
|---|---|---|
| `EQUIP-PLOTTER1-001` vs `FRAME-RAIL-TRAY-UPPER-L-001` | 43,875 | 100% of rail volume (Z=[184, 199]) |
| `EQUIP-PLOTTER1-001` vs `FRAME-RAIL-TRAY-UPPER-R-001` | 43,875 | same |
| `EQUIP-PLOTTER1-001` vs `FRAME-RAIL-TRAY-UPPER-C-001` | 42,637.5 | same |
| `EQUIP-PLOTTER1-001` vs `SLIDE-UPPER-LEFT-001` | 8,775 | 1 mm-deep sliver |
| `EQUIP-PLOTTER1-001` vs `SLIDE-UPPER-RIGHT-001` | 8,775 | same |
| `EQUIP-PLOTTER1-001` vs `SLIDE-UPPER-CENTER-001` | 8,527.5 | same |
| `EQUIP-PLOTTER1-001` vs `INTERLOCK-TAB-UPPER-001` | 108 | constant |

**Root cause (pre-fix):** tier-2 under-tray mounting hardware (slide 12 mm + rail profile 15 mm = **27 mm** stack below `TRAY-UPPER-001`'s bottom face) needed clearance below the tray, but `plotter.upper_z`'s derived formula (`lower_z + tier_clearance_min_mm + tray_panel_thickness_mm`) only reserved the tray's own 11 mm panel thickness below the mounting surface. `EQUIP-PLOTTER1-001`'s top (Z=200) exactly met `TRAY-UPPER-001`'s bottom (Z=200) with **zero gap**. Pre-fix collision sweeps passed only via the Y-overlap-only `is_staggered_tier_y_overlap()` heuristic in `src/stand_cad/geometry/collision.py`, which did **not** check `intersection_volume`.

**Closure (D-038):** Main resolved this under the owner's standing autonomy grant — **option 1** (grow `case.height` by +27 mm via extended `upper_z` formula) applied; **option 2** (select shallower slide/rail hardware) not taken. `trays.slide_rail_height_mm` remains `to_measure` and was not retuned. QA sweep cycle 2 had quantified the defect but applied no geometric fix; PLT-009 corrected the formula and closed F-5.

### Post-fix evidence (rev9)

| Leaf | Old | New |
|---|---|---|
| `plotter.upper_z` | 211 | **238** |
| `case.height` | 517 | **544** |
| `hardware.handle_mount_z_mm` | 263 | **276.5** (formula unchanged; recomputed from taller case — **superseded to 252 mm by D-050/D-051**) |

**Confirmed zero-intersection evidence** (`intersection_volume` == 0 at all tray-1 positions {0, 65, 130, 180, 250} mm):

| Hardware part | Z-gap (mm) | Constant across dy? |
|---|---|---|
| `FRAME-RAIL-TRAY-UPPER-{L,R,C}-001` | 11.0 | yes |
| `SLIDE-UPPER-{LEFT,RIGHT,CENTER}-001` | 26.0 | yes |
| `INTERLOCK-TAB-UPPER-001` | 15.0 | yes |

Regression: `tests/test_kinematics.py::test_plotter1_clear_of_tier2_under_tray_hardware` (7 parts × 5 positions = 35 cases). Evidence pack: `output/validation/rev9/`.

## J. Light-strip service-volume near-miss (2026-08-05 re-verified at `case.depth`=420 mm)

`LIGHT-STRIP-001` (provisional `service_volume` reference body, `verify_on_real_machine`) sits exactly **0.5 mm** from `FRAME-POST-RR-001` in the closed/transport state — exactly at, not below, the `tolerance.part_assembly_feature_mm` floor (0.5 mm). Re-measured **2026-08-05** after the D-045 depth shrink (`case.depth` 550→420 mm): `minimum_clearance(LIGHT-STRIP-001, FRAME-POST-RR-001)` remains **0.5 mm** (unchanged — both bodies share the same `top_structure.z_min_mm` anchor). All tests pass with **zero margin**. Flag only; no geometry change in this cycle. Owner should confirm whether 0.5 mm is acceptable for the real light-strip mounting path or whether the strip position should move before production release.

A 1–2 mm Y-anchor nudge in `services.py` would not remove the genuine XY planform overlap (X∈[610,625]×Y∈[535,544.5] between strip footprint and post `leg_h` at current depth); clearing it fully would require shortening `services.light_strip_length_mm` (a `to_measure` hardware leaf) — not applied. **No reposition applied.**

## K. Upper-tray tip-over stability factor below the TZ floor (PLT-010 / TZ line 508) — indicative pass only (D-039, rev10)

`output/validation/rev10/stability_report.md` (D-039 split stationary/moving mass model):

| Case | Legacy factor (rev9) | Corrected factor (rev10) | TZ floor (line 508) | Indicative model |
|---|---|---|---|---|
| Lower tray fully extended (250 mm), both plotters installed | **2.080** | **3.563** | 1.5 | Meets floor under unmeasured mass assumptions |
| Upper tray fully extended (400 mm), both plotters installed | **1.300** | **1.596** | 1.5 | Meets floor under unmeasured mass assumptions |

**Root cause (D-039):** the pre-rev10 model applied identical `total_mass` to both restore and overturn moments, so mass cancelled algebraically; only extension ratio mattered (400/250=1.6 explained the 1.300 vs 2.080 split). The corrected model credits only the extended tier's tray panel + plotter as moving mass and the real computed structural mass plus the other plotter as stationary mass. Both tiers pivot at the front foot line (Y=15.0 mm, `hardware.foot_diameter_mm`/2 foot inset — not Y=0), consistent with `output/validation/rev11/stability_report.md`. No ballast was required.

**Status:** tracked as `IN_PROGRESS` in `state/REQUIREMENTS_TRACEABILITY.csv` PLT-010 under the indicative model only — an independent adversarial review found the same model gives 1.434 under a 20 N lean on an already-extended tray and 0.924 with both trays extended simultaneously, both below the 1.5 floor, so `PASSING` no longer reads honestly (fix wave D-054). **NOT closed pending physical measurement and qualified review** — Gate G4 needs FEA, dynamic transport loads, and real measured masses, not an agent-computed static model. Historical rev10 factors at `case.depth`=550 mm; **current** datums use `case.depth`=420 mm — see §L for D-049 figures.

## L. Upper-tray tip-over after D-045 depth reduction — indicative pass only (D-049, still not Gate G4)

D-039/D-040 closed this concern at `case.depth`=550 mm (upper tier factor 1.596, meets the 1.5 floor in `stability.tip_factor_min`). D-045 (2026-08-05) reduced `case.depth` to 420 mm per owner instruction (within the owner's stated 350–450 mm range) to match the film organizer's rear boundary. This shrank the tipping base and re-opened the concern:

| Case | Factor at case.depth=550 (rev11, D-039) | Factor at case.depth=420 (D-045, before D-048) | TZ floor (line 508) | Indicative model at 420 mm (D-049) |
|---|---|---|---|---|
| Lower tray fully extended (250 mm), both plotters installed | 3.563 | 2.650 | 1.5 | **2.650** — meets floor |
| Upper tray fully extended (250 mm after D-049; was 400 mm in TZ), both plotters installed | 1.596 | 1.179 | 1.5 | **2.339** — meets floor |

**Why it was opened:** this was a real, deliberately-failing pytest gate (`tests/test_geometry.py::test_indicative_tip_factor_non_authoritative`) — the test was NOT weakened or skipped so the regression stayed visible until the owner ruled.

**Options presented to the owner (2026-08-05):**
1. Accept reduced upper-tier margin for prototype/CONCEPT only, with ballast, reduced upper-tray extension, or reduced upper-tray load as follow-up before production.
2. Choose a depth nearer 450 mm to recover tipping-base margin if footprint tolerates it.
3. Accept 420 mm depth and formally waive the 1.5 floor for prototype stage in writing.
4. **Limit tray full-service extension** — owner first chose **200 mm on both tiers** (D-048) because large pull-out seemed unnecessary; upper-tier indicative factor **~3.48** at 420 mm depth, comfortably above 1.5, but TZ `front_overhang_min_mm`=40 rear-face criterion was **not met** (rear at Y=+10 mm).

**Resolution (D-049 supersedes D-048's 200 mm figure):** after seeing both options with numbers, owner restored **250 mm full-service extension on both tiers** to recover TZ front-overhang compliance (rear face Y=−40 mm). **Current indicative factors at `case.depth`=420 mm:** upper **2.339**, lower **2.650** (both ≥1.5) under the narrow baseline case (single tier extended, at rest). `tests/test_geometry.py::test_indicative_tip_factor_non_authoritative` passes. **PLT-010 tracked as `IN_PROGRESS`, not `PASSING`** (fix wave D-054 honesty correction) — a broader independent review of the same model shows a 20 N lean on an extended tray falls to 1.434 and both trays extended simultaneously falls to 0.924, both below the 1.5 floor, so the baseline-only pass does not represent closure. **NOT closed pending physical measurement and qualified engineering review** (FEA, dynamic transport loads, measured masses) before any production release claim.

## M. Open-lid headroom vs fixed structure (PLT-008) — **OPEN**

Provisional open-lid envelopes `LID-ENVELOPE-P1-001` / `LID-ENVELOPE-P2-001` (`src/stand_cad/geometry/trays.py::_lid_envelope_bounds`) extend **80 mm** above each plotter physical top (`plotter.lid_open_envelope_height_mm`, `to_measure`). Hinge axis, swing radius, and opening direction are **not modelled** — see §A items 3–4.

**Transport / trays closed — vertical gap to next fixed member above each plotter** (measured 2026-08-05 on transport assembly with lid envelopes included; tier-2 plotter Z_max updated **D-055** to per-slot Cameo 5 height 124 mm):

| Tier | Plotter Z_max (mm) | Next fixed structure | Structure Z_min (mm) | Clear gap (mm) | Provisional lid top Z (mm) | Shortfall vs 80 mm lid (mm) |
|---|---|---|---|---|---|---|
| 1 (Cameo 4) | 200.0 | `TRAY-UPPER-001` underside | 227.0 | **27** | 280.0 | **53** (27 ≪ 80) |
| 2 (Cameo 5) | 362.0 | `ORG-FLOOR-001` underside | 412.0 | **50** | 442.0 | **30** (50 ≪ 80) |

**Practical consequence:** with trays closed, neither plotter has enough headroom for the provisional 80 mm open-lid envelope — a lid cannot fully open in the closed/transport configuration. Open-door vs slide-stack collision is **closed under D-076** (`docs/10` §Q — door/strut vs tray/slide/plotter vol≈0 at sampled extensions; struts present when door open). **§M remains OPEN for lid headroom only** — not for door/tray clearance. **`tests/test_kinematics.py::test_lid_envelope_no_intersection_in_service_states`** is marked **`@pytest.mark.xfail(strict=True)`** with a transport headroom canary (tier 1 **27 mm** / tier 2 **50 mm** clear gap vs **80 mm** provisional envelope) — do **not** weaken to green pytest; remedy requires owner decision on lid envelope or headroom. Tracked in `state/DEFERRED_VERIFICATION.md` (D-054 fix-wave row) alongside PLT-008 `IN_PROGRESS`.

## N. Transport retention — trays, plotters, and film (TZ lines 158, 181, 303) — **OPEN**

**Nothing in the current transport assembly restrains the trays, the plotters, or the film** against shock, tilt, or deceleration. TZ requirements not yet met:

- TZ line 158: «Передний съёмный ограничитель высотой 40–50 мм не позволяет листам выпадать при транспортировке.»
- TZ line 181: «Направляющие полного выдвижения с фиксацией в закрытом положении.»
- TZ line 303: «Платформы и передний ограничитель плёнки блокируются на время перевозки.»

**Current model facts (verified in geometry source):**

- **Soft stops (`SOFTSTOP-LOWER-001`, `SOFTSTOP-UPPER-001`)** are members of the tray kinematic groups (`src/stand_cad/geometry/kinematics.py::LOWER_KINEMATIC_GROUP` / `UPPER_KINEMATIC_GROUP`) — they **travel with their trays** and contact **no fixed structure** in transport; they are end-of-travel bumpers on the moving tray, not transport locks (`src/stand_cad/geometry/trays.py::_soft_stop_bounds`).
- **Tray interlock (`INTERLOCK-*`) — REMOVED (D-067):** hardware not emitted; dual-extend inhibit is **operating procedure only** until interlock restored.
- **Plotters** rest on **`VIBMOUNT-P*`** elastomer pads only — no mechanical fasteners, clamps, or straps modelled (`src/stand_cad/geometry/trays.py`; no restraint hardware in `hardware.py` / `services.py`).
- **Film front retainer:** `RETAINER-001` was specified in PLT-002 for the vertical organizer (TZ line 158) but is **absent from the current horizontal-organizer geometry** (PLT-007 / D-031 horizontal replacement — no `RETAINER-*` part IDs in `src/`). The TZ's removable 40–50 mm front retainer is **not built**.

**Unrestrained mass at risk in transport:** plotters **4.7 kg + 5.2 kg** (`plotter_cameo4.mass_kg`, `plotter_cameo5.mass_kg`) plus up to **10 kg** of film (`film_storage_horizontal.max_load_kg` / `mass_targets.film_marked_limit_kg`, TZ line 305 marking limit).

**Owner must specify** transport-lock hardware for **trays and film** (tray detents/latches, removable film retainer) before Gate G4 transport testing or production release. **Owner 2026-08-06:** plotter tie-down **not required** for owner-operated event display — unrestrained plotter mass (**4.7+5.2 kg**) accepted; tray/film retention remains **OPEN**. Tracked in `state/DEFERRED_VERIFICATION.md` (D-054 fix-wave row).

## O. Side-slab mass-model contradiction (PLT-012) — **RESOLVED (D-055, Stage 1 fix wave)**

**Resolution (2026-08-05, D-055):** Side slabs rebuilt as **3 mm opal-PMMA cavity walls** over a **20 mm profile pocket** (TZ lines 218–219: cast opal PMMA 3 mm over hidden aluminium frame; line 212: monolithic appearance without thick acrylic as load-bearing material; line 547 forbids thick monolithic-acrylic structure). The prior **solid 20 mm fill** was a **rendering-legibility artifact** (PLT-004/PLT-005, A-013) — not ratified construction.

**Geometry (`panels.py::_extrude_side_slab`):** outer X face + front/rear Y **3 mm returns**; ~17 mm air cavity for light strip and frame members. Mass model unchanged policy: **`cast_opal_pmma_3mm` shell-thickness path** on bounding box (now matches physical skin intent). **`analysis.py::_panel_shell_volume_mm3` `/2` bug removed** — flat 3 mm parts (e.g. `PANEL-OUT-REAR-001`) were under-counted 2×.

**Headline masses (D-055 verified, 2026-08-05):** side-slab shell mass **≈0.395 kg each** (`PANEL-OUT-LEFT/RIGHT-001`, bbox shell estimate on cavity-wall solids). Empty structural **9.972 kg** (TZ goal band 9–11 kg; ceiling ≤12 kg). All-parts (+ both plotters) **≈19.87 kg**. Regenerate via `scripts/regenerate.py` → `output/validation/rev12/mass_report.csv` to sync evidence file timestamps. Pre-D-055 baseline: structural **≈6.048 kg** / all-parts **≈8.479 kg**.

**Owner action:** none required for mass-accounting policy — geometry now matches TZ intent. Physical validation of return-flange choice deferred (`state/DEFERRED_VERIFICATION.md` D-055 row).

## P. Shelf-support attachment method (D-059 / D-061 / D-065) — **CLOSED (2026-08-06)**

**Context:** D-059 added **SHELF-SUPPORT-L/R-{000,001,002}** cleats closing a measured **17 mm** air gap between horizontal **SHELF-*** dividers and **PANEL-OUT-LEFT/RIGHT-001**. Geometry places bearing surfaces at **0.000 mm** clearance to both shelf and panel (verified `tests/test_geometry.py::test_shelf_supports_bear_on_side_panels`).

**Decided method (D-065, owner 2026-08-06 — adhesive-free, matches D-060 no-weld):** **JT-SHELF-SUPPORT-SKIN** — **15×15×1.5 mm Al L-angle** cleat (cycle-2 geometry fix: vertical leg in cavity X-band hosts **M4 rivnuts**; horizontal leg bears shelf at **0.000 mm** clearance). Sole attachment **3×M4×12 pan-head** into rivnuts in the **vertical leg** (not a 2 mm flat plate). Pattern: **front / mid / rear along Y** over `film_storage_horizontal.clear_depth` (**330 mm**), nominal pitch **≈150 mm** (`hardware.fastener_panel_pitch_mm`). Six cleats (L/R × 3 shelves) → **18 M4** shelf-support screws in `joints.*` registry. Install from cavity before side-slab final close (`docs/15_ASSEMBLY_INSTRUCTIONS.md` Step 10–11). Hole positions and final grip length: **`to_measure`** on prototype (`verify_on_real_machine=True` on **SHELF-SUPPORT-*** parts).

**Owner action:** none — method closed. Manufacturer DFM may counter-propose equivalent rivnut brand or screw length with written rationale.

## Q. Door support struts vs extended tray (D-073 / D-076) — **CLOSED (2026-08-07)**

**Context:** Piano-hinge drop-front doors (`DOOR-LOWER/UPPER-001`) with cosmetic `DOOR-STRUT-*` when open. Pre-D-076 measured **≈6638–6885 mm³** open lower door ↔ extended `SLIDE-LOWER-*` and **≈7374 mm³** strut ↔ plotter at 250 mm extension.

**Resolution (D-076):** Open door post-settle drops top face to **Z ≤ slide_bottom − tolerance.assembly_mm** (~2 mm below tray underside) so slides travel **over** the horizontal door in Z. Struts rerouted along **corner-post outer faces** at settled door Z (outside tray X-span); struts **always emitted** when door open.

**Volumetric evidence (2026-08-07, rev15):** Sample-sweep at lower extensions **0 / 130 / 180 / 250 mm** — `DOOR-LOWER-001` and `DOOR-STRUT-LOWER-*` vs `TRAY-/SLIDE-/EQUIP-PLOTTER1-*` all **vol = 0 mm³** (`tests/test_kinematics.py::test_lower_open_door_kinematic_clearance_sweep`). Strut ↔ post/panel attachment **≈282 / ≈177 mm³** (under `DOOR_STRUT_MAX_BEARING_MM3`=350 ceiling; `tests/test_geometry.py::test_strut_mate_rejects_volumetric_burial`). Full-state collision sweeps clean: `test_open_door_service_states_collision_clear`, `test_numeric_collision_clearance[service_plotter_1|tray1_quick_access|service_plotter_2]`. Upper tier: `trays.upper_extension`=**0** — `test_upper_open_door_kinematic_clearance_sweep`.

**Owner confirmed 2026-08-07** ("Да, все верно") — D-076 upper-fixed assumption accepted as final; `state/ASSUMPTIONS.md` A-D076 closed.

## R. Post-less corner structure (D-070 / D-075) — **CLOSED (2026-08-07)**

**Resolution (D-075):** Owner restored all four `FRAME-POST-FL/FR/RL/RR-001` corner posts. **JT-FRAME-CORNER** retargeted to **post-primary** (`FRAME-POST-*` ↔ `FRAME-RAIL-*`); rail-to-rail bracket mating remains **supplementary** valid at the same nodes. **JT-STACK-CAP-POST** retargeted to post tops + supplementary top-ring/panel bearing. Transport emits four posts (`tests/test_geometry.py::test_corner_posts_emitted`). Prototype FEA/load test still deferred before series release — see **R-016**.
