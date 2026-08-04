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

## D. Side-slab front-corner rounding (TZ section 8 / A-013)

**Open (PLT-005 rev4):** outer side slabs are **solid** 20 mm × (690−foot_h) mm volumes with **2D front-corner fillets only**. Achieved radius is **≈9.9 mm** (`min(case.corner_radius, side_clear/2−0.1, depth/2−0.1)` with default TZ datums) — **not** the full R25 case corner. Matching the reference photo's large dominant radius requires widening `side_clear` (derived from fixed 650×610 envelope) — **out of scope** until TZ dimensions change or human accepts the divergence (D-019). Top-front 3D edge fillet remains best-effort via `_try_top_front_edge_fillet`. Curved side-profile massing and RGBW glow remain deferred.

## E. Handle mount coordinates (PLT-005)

Provisional derived values `hardware.handle_mount_y_mm` (**100 mm**) and `hardware.handle_mount_z_mm` (**214 mm**) position the TZ:304 grip cutout (110×35 mm) in the front plotter-bay gap: Y band **[45, 155]**, Z band **[196.5, 231.5]**. Full case-width through-ray grid testing against all 81 transport parts reports zero encroachment (rework F-1). **VERIFY ON REAL MACHINE** before production release.

## F. Rear vent render evidence (PLT-005 rework F-3)

TZ line 290 bottom+rear layout unchanged. Primary transport rear view may still show near-white inner panel through slots; **`output/validation/rev4/views/rear_vent_closeup.png`** (outer rear only, grey backdrop) is the legibility evidence for rear vent grille sign-off.
