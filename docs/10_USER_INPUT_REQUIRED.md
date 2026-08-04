# Consolidated user input required

The Light Plotter Tower technical specification (`ИИ советы/Cursor_Opus5_TZ_Light_Plotter_Tower.md`) is the authoritative requirement source (D-011). At adoption it settled equipment selection (two Silhouette Cameo plotters), operating scenario, appearance, and an initial layout and overall-dimension baseline. Owner instruction on 2026-08-04 during PLT-007 later overrode parts of that baseline: the governing machine is now Silhouette Cameo 4, tier setback and overall height differ from the TZ figures, and the film organizer layout changed — see `state/DECISION_LOG.md` D-025, D-027, D-028, D-029, D-032, and D-033 and the `DEVIATED`/`IN_PROGRESS` rows PLT-001/002/003/004/006/018/019/020/021 in `state/REQUIREMENTS_TRACEABILITY.csv`. The current model follows those post-TZ decisions, not the original TZ numbers verbatim. Only the items below remain unresolved.

## A. Physical measurements on real equipment (TZ section 16)

**Cameo 4 governing dimensions CLOSED (2026-08-04):** width 570 mm, depth 195 mm, height 170 mm, mass 4.7 kg — Silhouette Cameo 4 spec sheet. Cameo 5 slot-2 mass 5.2 kg confirmed. Service-port **connector type** remains open (`hardware.service_port_*` cutout is provisional `to_measure`).

Before releasing production files, measure on two real plotters:

1. Feed-plane height above the machine's lower support plane — unblocks `plotter.feed_plane_z_from_base`.
2. Rear material exit coordinates.
3. Real open-lid envelope and hinge position.
4. Power and USB connector coordinates.
5. OEM power adapter dimensions and minimum cable bend radius.
6. Plotter foot positions and drill-free fixing points.
7. Real thickness and stiffness of the films actually used — unblocks `film_storage_horizontal.min_stack_height_mm`.
8. Actual thickness of all purchased sheet materials — unblocks `materials.actual_sheet_thickness_mm`.

After measuring, update `config/parameters.yaml`, regenerate the model, repeat collision checks, and only then remove `VERIFY ON REAL MACHINE` markings from production drawings (TZ section 16 closing paragraph).

## B. Manufacturing authorization

Manufacturer DFM authorization remains open and is not addressed by the TZ. Before Gate G5 the owner must authorize which vendors may receive the RFQ package and approve the selected prototype quotation, per ADR-003 and `docs/05_IMPLEMENTATION_PLAN.md`.

## C. Tray deflection under design load (PLT-011 / TZ line 184)

Concept-stage corrected beam model (`output/validation/rev6/deflection_report.md`) yields **3.644 mm**
mid-span deflection under the 10 kg design load with rail-to-rail span 570 mm (`plotter.physical_width`,
Cameo 4 governing) and load distributed along 195 mm (`plotter.physical_depth`) with unsourced sandwich
panel stiffness `materials.tray_panel_youngs_modulus_mpa` (3000 MPa, `to_measure`). This exceeds the
1.5 mm TZ ceiling. Resolving the miss requires measured panel stiffness, tray structural redesign, or
slide/support review — not silent parameter retuning. See assumption **A-012**.

## D. Side-slab front-corner rounding (TZ section 8 line 230 / D-025) — **CLOSED**

With fixed `case.width`=650 mm and `case.internal_width`=610 mm, `side_clear`=(650−610)/2=**20 mm exactly**. A full bullnose on a 20 mm-thick side slab cannot exceed **R10** (= `side_clear`/2) before the edge becomes a full round. TZ line 230 asks for **R20–R30**, which cannot hold simultaneously with the TZ's own 610 mm clear-width floor once 650 mm overall width is fixed — an **internal conflict inside the TZ**.

**Implemented (rev5):** R10 full bullnose on the **exterior front vertical** edges of both side slabs, **continued along the top-front horizontal edge** (`case.side_slab_bullnose_radius_mm`=10, achieved ≈9.9 mm after width/2−0.1 clamp). Recorded as **DEVIATED** in `state/REQUIREMENTS_TRACEABILITY.csv` row **PLT-018** (D-025).

**Owner decision (2026-08-04):** accepts **option 1 — R10 bullnose at the current 650×610 envelope** (matches rev5 geometry; no dimensional change). **Declined option 2** (grow overall width to 690 mm). **Rejected option 3** (shrink clear width to ~570 mm): that envelope is narrower than the 580 mm protective plotter design width (`plotter.design_width`) and would leave only ~2 mm clearance per side where TZ line 89 requires 22 mm. Owner also declined a cosmetic/non-structural overhang workaround.

Curved side-profile massing beyond the bullnose and RGBW photometric glow remain deferred.

## E. Handle mount coordinates (PLT-007 / D-030)

Provisional derived values `hardware.handle_mount_y_mm` (**100 mm**) and `hardware.handle_mount_z_mm` (**263 mm**) position the TZ:304 grip cutout (110×35 mm) in the front plotter-bay gap: Y band **[45, 155]**, Z band **[245.5, 280.5]**. Handle Z is centred on the side panel, **not** at the indicative loaded-case centre of mass (CoM z≈216 mm → **+47 mm** offset above CoM per D-030). Full case-width through-ray grid testing against all transport parts reports zero encroachment (rework F-1). **VERIFY ON REAL MACHINE** before production release.

## F. Rear vent render evidence (PLT-005 rework F-3)

TZ line 290 bottom+rear layout unchanged. Primary transport rear view may still show near-white inner panel through slots; **`output/validation/rev4/views/rear_vent_closeup.png`** (outer rear only, grey backdrop) is the legibility evidence for rear vent grille sign-off.

## G. Cable pass-through opening size (owner 2026-08-04 override, D-036)

Owner simplified TZ section 10's certified rear mains inlet (with retention/strain relief, feeding an internal certified distributor) to a plain grommeted cable pass-through hole for the prototype: he will route a household extension cord/power strip through the hole and plug the plotters and lighting into it himself inside the case. Two provisional leaves remain open (`to_measure`, A-015): `hardware.cable_passthrough_diameter_mm` (30 mm) and `services.cable_passthrough_grommet_wall_mm` (2 mm → 26 mm clear bore) — chosen in a generous 25-35 mm range for a common plug/cable end, not measured against the actual cord. The grommet edge-break radius (`services.cable_passthrough_edge_break_radius_mm`, 1 mm) is settled at TZ:472's own verified R1 value and does not need further measurement.

**To close this item:** measure the outer diameter of the actual extension-cord plug/cable end the owner intends to route through the opening, then update `config/parameters.yaml` and regenerate before production DXF release. The certified-inlet path (TZ section 10) remains deferred, not deleted — `MAINS-INLET-001` stays modeled as a placeholder service volume if a future revision reinstates it.

## H. Tier-2 under-tray hardware vs plotter 1 envelope (F-5 quantified, 2026-08-04 QA sweep cycle 2)

Scripted `intersection_volume` measurement (build123d) confirms a real volumetric overlap between `EQUIP-PLOTTER1-001` (Cameo 4 body, Z=[30, 200]) and tier-2 under-tray mounting hardware. At rest (`lower_extension_mm`=0) the overlap is full; as tier-1 tray travel increases, overlap **decreases roughly linearly** because `EQUIP-PLOTTER1-001` is in `LOWER_KINEMATIC_GROUP` and moves forward with the tray, reducing its Y-overlap with the fixed `FRAME-RAIL-TRAY-UPPER-*` rails. For `EQUIP-PLOTTER1-001` vs `FRAME-RAIL-TRAY-UPPER-L-001` as `lower_extension_mm` increases: dy=0 → 43,875.0 mm³; dy=130 (`trays.lower_quick_access_extension_mm`) → still overlapping ≈14,625.0 mm³; dy=180 → 3,375.0 mm³; dy=194 → 225.0 mm³; dy=196 → 0.0 mm³ (clearance ≈1.0 mm); dy=250 (full `trays.lower_extension` service) → 0.0 mm³ (clearance ≈55.0 mm). **Quick-access (130 mm) still has substantial real overlap** — the interference is present at quick-access, not only at rest.

**At rest (closed/transport):**

| Pair | Intersection volume (mm³) | Notes |
|---|---|---|
| `EQUIP-PLOTTER1-001` vs `FRAME-RAIL-TRAY-UPPER-L-001` | 43,875 | 100% of rail volume (Z=[184, 199]) |
| `EQUIP-PLOTTER1-001` vs `FRAME-RAIL-TRAY-UPPER-R-001` | 43,875 | same |
| `EQUIP-PLOTTER1-001` vs `FRAME-RAIL-TRAY-UPPER-C-001` | 42,637.5 | same |
| `EQUIP-PLOTTER1-001` vs `SLIDE-UPPER-LEFT-001` | 8,775 | 1 mm-deep sliver |
| `EQUIP-PLOTTER1-001` vs `SLIDE-UPPER-RIGHT-001` | 8,775 | same |
| `EQUIP-PLOTTER1-001` vs `SLIDE-UPPER-CENTER-001` | 8,527.5 | same |
| `EQUIP-PLOTTER1-001` vs `INTERLOCK-TAB-UPPER-001` | 108 | constant |

**Root cause:** tier-2 under-tray mounting hardware (slide 12 mm + rail profile 15 mm = **27 mm** stack below `TRAY-UPPER-001`'s bottom face) needs clearance below the tray, but `plotter.upper_z`'s derived formula (`lower_z + tier_clearance_min_mm + tray_panel_thickness_mm`) only reserves the tray's own 11 mm panel thickness below the mounting surface. `EQUIP-PLOTTER1-001`'s top (Z=200) exactly meets `TRAY-UPPER-001`'s bottom (Z=200) with **zero gap**. Currently passed in collision sweeps only via the Y-overlap-only `is_staggered_tier_y_overlap()` heuristic in `src/stand_cad/geometry/collision.py`, which does **not** check `intersection_volume`.

**Owner decision required (pick one or equivalent):**

1. Grow `case.height` (currently **517 mm**) by ≈**+27 mm** via extending the `upper_z` / height formula, **or**
2. Select slide/rail hardware with less under-tray depth (`trays.slide_rail_height_mm` is `to_measure`, not yet selected).

Both options change fixed dimensional or hardware assumptions outside the current concept geometry authority. **No geometric fix was applied in QA sweep cycle 2** — this item remains a documented follow-up (supersedes the qualitative F-5 note in `state/PROJECT_STATE.md`).

## I. Light-strip service-volume near-miss (2026-08-04 QA sweep cycle 2)

`LIGHT-STRIP-001` (provisional `service_volume` reference body, `verify_on_real_machine`) sits exactly **0.5 mm** from `FRAME-POST-RR-001` in the closed/transport state — exactly at, not below, the `tolerance.part_assembly_feature_mm` floor (0.5 mm). All tests pass with **zero margin**. Flag only; no geometry change in this cycle. Owner should confirm whether 0.5 mm is acceptable for the real light-strip mounting path or whether the strip position should move before production release.
