# Consolidated user input required

The Light Plotter Tower technical specification (`ИИ советы/Cursor_Opus5_TZ_Light_Plotter_Tower.md`) answered most prior open questions: equipment selection (two Silhouette Cameo 5 plotters), operating scenario, appearance, layout, and overall dimensions. Only the items below remain unresolved.

## A. Physical measurements on real equipment (TZ section 16)

Before releasing production files, measure on two real Cameo 5 units:

1. Feed-plane height above the machine's lower support plane — unblocks `plotter.feed_plane_z_from_base`.
2. Rear material exit coordinates.
3. Real open-lid envelope and hinge position.
4. Power and USB connector coordinates.
5. OEM power adapter dimensions and minimum cable bend radius.
6. Plotter foot positions and drill-free fixing points.
7. Real thickness and stiffness of the films actually used — unblocks `film_storage.min_stack_width_mm`.
8. Actual thickness of all purchased sheet materials — unblocks `materials.actual_sheet_thickness_mm`.

After measuring, update `config/parameters.yaml`, regenerate the model, repeat collision checks, and only then remove `VERIFY ON REAL MACHINE` markings from production drawings (TZ section 16 closing paragraph).

## B. Manufacturing authorization

Manufacturer DFM authorization remains open and is not addressed by the TZ. Before Gate G5 the owner must authorize which vendors may receive the RFQ package and approve the selected prototype quotation, per ADR-003 and `docs/05_IMPLEMENTATION_PLAN.md`.

## C. Tray deflection under design load (PLT-011 / TZ line 184)

Concept-stage corrected beam model (`output/validation/rev3/deflection_report.md`) yields **3.953 mm**
mid-span deflection under the 10 kg design load with rail-to-rail span 566 mm and unsourced sandwich
panel stiffness `materials.tray_panel_youngs_modulus_mpa` (3000 MPa, `to_measure`). This exceeds the
1.5 mm TZ ceiling. Resolving the miss requires measured panel stiffness, tray structural redesign, or
slide/support review — not silent parameter retuning. See assumption **A-012**.

## D. Side-slab front-corner rounding (TZ section 8 line 230 / D-025) — **CLOSED**

With fixed `case.width`=650 mm and `case.internal_width`=610 mm, `side_clear`=(650−610)/2=**20 mm exactly**. A full bullnose on a 20 mm-thick side slab cannot exceed **R10** (= `side_clear`/2) before the edge becomes a full round. TZ line 230 asks for **R20–R30**, which cannot hold simultaneously with the TZ's own 610 mm clear-width floor once 650 mm overall width is fixed — an **internal conflict inside the TZ**.

**Implemented (rev5):** R10 full bullnose on the **exterior front vertical** edges of both side slabs, **continued along the top-front horizontal edge** (`case.side_slab_bullnose_radius_mm`=10, achieved ≈9.9 mm after width/2−0.1 clamp). Recorded as **DEVIATED** in `state/REQUIREMENTS_TRACEABILITY.csv` row **PLT-018** (D-025).

**Owner decision (2026-08-04):** accepts **option 1 — R10 bullnose at the current 650×610 envelope** (matches rev5 geometry; no dimensional change). **Declined option 2** (grow overall width to 690 mm). **Rejected option 3** (shrink clear width to ~570 mm): that envelope is narrower than the 580 mm protective plotter design width (`plotter.design_width`) and would leave only ~2 mm clearance per side where TZ line 89 requires 22 mm. Owner also declined a cosmetic/non-structural overhang workaround.

Curved side-profile massing beyond the bullnose and RGBW photometric glow remain deferred.

## E. Handle mount coordinates (PLT-005)

Provisional derived values `hardware.handle_mount_y_mm` (**100 mm**) and `hardware.handle_mount_z_mm` (**214 mm**) position the TZ:304 grip cutout (110×35 mm) in the front plotter-bay gap: Y band **[45, 155]**, Z band **[196.5, 231.5]**. Full case-width through-ray grid testing against all 81 transport parts reports zero encroachment (rework F-1). **VERIFY ON REAL MACHINE** before production release.

## F. Rear vent render evidence (PLT-005 rework F-3)

TZ line 290 bottom+rear layout unchanged. Primary transport rear view may still show near-white inner panel through slots; **`output/validation/rev4/views/rear_vent_closeup.png`** (outer rear only, grey backdrop) is the legibility evidence for rear vent grille sign-off.
