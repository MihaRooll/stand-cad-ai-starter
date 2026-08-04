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
