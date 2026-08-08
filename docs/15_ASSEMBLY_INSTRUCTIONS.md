# Assembly instructions — Light Plotter Tower (CONCEPT / REFERENCE_ONLY)

**Revision:** CONCEPT rev15 (FIX-WAVE-004, **D-075…D-076**; supersedes FIX-WAVE-003 **D-066…D-074**)  
**Status:** PRELIMINARY — not for production release. Owner-decision blockers remain in `docs/10_USER_INPUT_REQUIRED.md` (§F handle, §N transport retention, §M lid headroom, §A measurements). **§P shelf attachment CLOSED (D-065). §Q door/strut CLOSED (D-076). §R posts CLOSED (D-075).** Confirm D-076 upper-fixed assumption (A-D076).

## Before you start

- Frame member: **15×15×1.5 mm aluminium angle** — too thin for reliable hand welding; owner forbids welding (D-060).
- **D-075:** corner posts (`FRAME-POST-FL/FR/RL/RR-001`) **restored** — primary vertical load path at corners. **JT-FRAME-CORNER** = post↔rail (supplementary rail↔rail brackets may also apply at same nodes). **JT-STACK-CAP-POST** = cap↔post tops + supplementary top-ring/panel bearing. Prototype FEA/load test still deferred — see `docs/08` R-016.
- **D-076:** upper tray **fixed** (`trays.upper_extension`=0, Main best-guess pending owner confirmation); upper service = open `DOOR-UPPER-001`. Lower door drops horizontal; tray slides over settled door.
- **D-069/D-071:** cosmetic BASE/ORG/POST front cladding and six rear service placeholder volumes (`MAINS-INLET-001`, adapters, `CTRL-RGBW-001`, `AIRPATH-001`, etc.) are **not** modeled — do not procure or install parts that have no STEP counterpart.
- Primary joining: **20×20×2 mm aluminium corner brackets** + **M4×12 pan-head** machine screws into **M4 rivnuts** (or through-bolt + nyloc where both faces are accessible). Exact grip length and install torque: **to_measure** (`hardware.fastener_m4_*`).
- Inner panels: **M3×10** from cavity side (`JT-PANEL-INNER-FRAME`). Torque **to_measure**.
- Joint catalogue: `config/parameters.yaml` → `joints.*` and `src/stand_cad/geometry/hardware.py`.

### Rivnut / insert install order (mandatory for cavity access)

1. **Perimeter rails (loose):** set **M4 rivnuts** in **FRAME-RAIL-{BASE,ORG,TOP}-*** angle faces and **FRAME-POST-*** corner posts at corner nodes **before** corner brackets close the ring (D-075 posts restored).
2. **Corner brackets:** attach brackets with **JT-FRAME-CORNER** / **JT-TRAY-RAIL-FRAME** only **after** rivnuts are set in the mating angle legs.
3. **Side slabs (loose prep):** on **PANEL-OUT-LEFT-001** and **PANEL-OUT-RIGHT-001** **before** final installation, pre-set **M4 rivnuts** in each **SHELF-SUPPORT-*** cleat and matching pilot/countersink locations in the 3 mm opal skin per **JT-SHELF-SUPPORT-SKIN** (D-065: 3×M4 front/mid/rear along Y, ~150 mm pitch).
4. **Cavity closure:** install **PANEL-OUT-LEFT/RIGHT-001** only after all reachable cavity-side **JT-PANEL-INNER-FRAME** / **JT-PANEL-OUTER-FRAME** / **JT-TRAY-SLIDE-FRAME** fasteners along rear/bottom/left are accessible; then torque **JT-SHELF-SUPPORT-SKIN** M4 screws from the still-open cavity face.

## Tools and consumables (indicative)

| Item | Nominal | Notes |
|---|---|---|
| Corner bracket | 20×20×2 mm Al L-gusset | Stamped/cut; manufacturer may substitute equivalent stock |
| Rivnut / threaded insert | M4 (frame), M3 where noted | Set before attaching brackets or closing cavity |
| Machine screws | M4×12 pan-head, M3×10 pan-head | Lengths to_measure after stack-up trial |
| Drawer slides | Full-extension pair + centre rail | Not selected; mount per datasheet (`JT-TRAY-SLIDE-FRAME`) |

## Assembly sequence

Build on a flat surface. **Do not** install **JT-SHELF-SUPPORT-SKIN** until **PANEL-OUT-LEFT/RIGHT-001** exist (installed or loose with prep complete).

### Step 1 — Feet and base ring

1. Place **FOOT-001…FOOT-004** at case corners — silicone isolation pad only; retain each foot with **1×M4 pan-head** through foot centre into **M4 rivnut** in **FRAME-RAIL-BASE-*** angle leg at that corner (D-075: foot→base-rail; post leg provides supplementary vertical path).
2. Set **M4 rivnuts** in base-rail angle faces at corner bracket nodes.
3. Join base perimeter rails at corners using **JT-FRAME-CORNER** (D-063: **1×M4 per bracket leg**, qty/joint=2):
   - **FRAME-RAIL-BASE-FRONT-001**
   - **FRAME-RAIL-BASE-REAR-001**
   - **FRAME-RAIL-BASE-LEFT-001**
   - **FRAME-RAIL-BASE-RIGHT-001**

### Step 2 — Lower tray ring and slides

4. Set rivnuts at lower tray ring nodes on base rails as needed.
5. Build lower tray frame rails using **JT-TRAY-RAIL-FRAME** (same D-063 bracket schedule; **not** JT-FRAME-CORNER):
   - **FRAME-RAIL-TRAY-LOWER-L-001**
   - **FRAME-RAIL-TRAY-LOWER-C-001**
   - **FRAME-RAIL-TRAY-LOWER-R-001**
6. Mount **SLIDE-LOWER-LEFT-001**, **SLIDE-LOWER-CENTER-001**, **SLIDE-LOWER-RIGHT-001** to tray rails (**JT-TRAY-SLIDE-FRAME** — hole pattern to_measure until slide part number chosen).
7. Assemble **TRAY-LOWER-001** onto slides; add **VIBMOUNT-P1-001…004**, **SOFTSTOP-LOWER-001**.
8. Install **PANEL-CLAD-FRONT-TRAY-LOWER-L-001**, **PANEL-CLAD-FRONT-TRAY-LOWER-C-001**, **PANEL-CLAD-FRONT-TRAY-LOWER-R-001** (sole remaining front cladding family — widened to tray-bottom Z per D-068).

### Step 3 — Tier-1 service volume (inner panels before outer skins)

9. **PANEL-IN-BOTTOM-001** — vent slots at rear/bottom service zone; screw to base ring (**JT-PANEL-INNER-FRAME**).
10. **PANEL-IN-MID-001** — inner mid panel; screws from cavity before side slabs close (**JT-PANEL-INNER-FRAME**). *Known concept intersection with upper tray rails — see OPEN-001.*
11. **MEDIA-SUPPORT-L1-001**, **MEDIA-SUPPORT-L2-001** — glide surfaces; **M3×10** into frame/tray-rail rivnuts (mechanical only).
12. **COVER-SVC-001** — rear/bottom service cover.

### Step 4 — Organizer ring (before film stack)

13. **FRAME-RAIL-ORG-FRONT-001**, **FRAME-RAIL-ORG-REAR-001**, **FRAME-RAIL-ORG-LEFT-001**, **FRAME-RAIL-ORG-RIGHT-001** at organizer floor Z using **JT-FRAME-CORNER** — **must precede** **ORG-FLOOR-001** so the film stack bears on a closed ring.
14. Install **DOOR-UPPER-001** (closed transport default) on piano hinge at tier-2 opening — hinge hardware **to_measure** (not modeled as separate solids).

### Step 5 — Organizer floor and film shelves

15. **ORG-FLOOR-001**, **ORG-INSERT-001**.
16. **SHELF-000**, **SHELF-001**, **SHELF-002** horizontal dividers (bear on **ORG-INSERT-001**; side cleats installed in Step 10).

### Step 6 — Upper tray ring

17. Build upper tray frame rails using **JT-TRAY-RAIL-FRAME**:
    - **FRAME-RAIL-TRAY-UPPER-L-001**
    - **FRAME-RAIL-TRAY-UPPER-C-001**
    - **FRAME-RAIL-TRAY-UPPER-R-001**
18. Mount **SLIDE-UPPER-LEFT-001**, **SLIDE-UPPER-CENTER-001**, **SLIDE-UPPER-RIGHT-001** (**JT-TRAY-SLIDE-FRAME**); assemble **TRAY-UPPER-001**; add **VIBMOUNT-P2-001…004**, **SOFTSTOP-UPPER-001**.
19. **PANEL-CLAD-FRONT-TRAY-UPPER-L-001**, **PANEL-CLAD-FRONT-TRAY-UPPER-C-001**, **PANEL-CLAD-FRONT-TRAY-UPPER-R-001**.

### Step 7 — Top ring

20. **FRAME-RAIL-TOP-LEFT-001**, **FRAME-RAIL-TOP-RIGHT-001**, **FRAME-RAIL-TOP-REAR-001** (no top-front rail or post cladding per D-044/D-070) using **JT-FRAME-CORNER**.
21. Install **DOOR-LOWER-001** at tier-1 opening (closed transport default).

### Step 7b — Stacking caps (optional second-unit interface)

22. After top ring is closed, install **STACK-CAP-FL/FR/RL/RR-001** at corner nodes using **JT-STACK-CAP-POST** (D-075 post-primary): **2×M4** per cap into **M4 rivnuts** in **FRAME-POST-*** tops and/or **FRAME-RAIL-TOP-*** / **PANEL-OUT-{LEFT,RIGHT,REAR}-001** bearing faces at the corner. Caps provide continuous Al bearing under a stacked unit's **FOOT-*** and a shallow registration recess **Ø = foot_diameter + foot_recess_clearance_mm**.
23. **Stacking usage:** align a second identical unit so its four feet seat in the recesses. **Owner waives stacked tip-over risk** — this interface addresses sliding and crushing/bearing only; do **not** rely on caps for overturn resistance without an explicit owner stability decision.

### Step 8 — Services before rear closure

24. **LIGHT-STRIP-001** — mount under **FRAME-RAIL-TOP-REAR-001** bottom face (Z≈506–514 mm); route wiring before **PANEL-OUT-REAR-001** closes.
25. **SVC-CABLE-PASSTHROUGH-001** grommet lands on **PANEL-OUT-RIGHT-001** (Y=320, Z=120) — install before right slab if grommet is press-fit. Owner-routed extension cord only — no modeled mains inlet or adapter placeholders (D-071).

### Step 9 — Rear and inner rear panels

26. **PANEL-IN-REAR-001** — rear media channels 450×10 mm; **JT-PANEL-INNER-FRAME**.
27. **PANEL-OUT-REAR-001** — outer rear skin; **JT-PANEL-OUTER-FRAME** from cavity.

### Step 10 — Side slab prep and installation

28. **Prep (loose panels):** on **PANEL-OUT-LEFT-001** and **PANEL-OUT-RIGHT-001**, set **JT-SHELF-SUPPORT-SKIN** rivnuts in cleats and skin pilot/countersink locations (D-065: 3×M4 per cleat, front/mid/rear along Y).
29. **PANEL-OUT-LEFT-001** — left cavity wall; **JT-PANEL-OUTER-FRAME** M4 screws from cavity into frame rivnuts (~150 mm pitch).
30. **PANEL-OUT-RIGHT-001** — right slab carries:
    - USB service port cutout (provisional 16×8 mm, to_measure)
    - Cable passthrough Ø30 mm (to_measure)
    - Handle **through-cut only** (**JT-HANDLE-HARDWARE** — §F OPEN; no bolt-on handle decided)
    Install right slab only after all cavity-side M4/M3 fasteners along left/rear/bottom are torqued.

### Step 11 — Shelf supports (after side skins exist)

31. **SHELF-SUPPORT-L-000…002**, **SHELF-SUPPORT-R-000…002** — **JT-SHELF-SUPPORT-SKIN** (D-065): **15×15×1.5 mm L-angle** bolted to inner face of **PANEL-OUT-LEFT/RIGHT-001** with **3×M4×12 pan-head** into **M4 rivnuts** in the **vertical leg** (front/mid/rear along Y, ~150 mm pitch); torque from cavity. Horizontal leg bears **SHELF-*** at shelf bottom — no adhesive.

### Step 12 — Equipment and operating check (transport load)

32. Place **EQUIP-PLOTTER1-001**, **EQUIP-PLOTTER2-001** on trays (reference bodies; real machines differ). **No transport retention modeled** for trays or film — owner waived plotter tie-down for event-display use (§N); specify tray/film restraints before shipping.
33. Load film sheets into organizer compartments after structure is stable. **No front retainer modeled** (§N).
34. **Dual-tray extension:** procedure-only — no interlock hardware in current CONCEPT (D-067); operator must not extend both trays simultaneously unless a future mechanical inhibit is added.

## Reach-through / DFM checks

| Check | Result |
|---|---|
| Rivnuts set in rails before corner brackets | **Required** — Step 1 § rivnut order |
| Tray rails use **JT-TRAY-RAIL-FRAME** (JOIN-001 / yaml) | **OK** — Steps 2/6; distinct from perimeter **JT-FRAME-CORNER** |
| **FRAME-RAIL-ORG-*** before **ORG-FLOOR-001** / **SHELF-*** | **OK** — Step 4 before Step 5 |
| Tray slides mounted before outer side slabs | **OK** — Steps 2/6 before Step 10 |
| Inner panels before **PANEL-OUT-LEFT/RIGHT** | **OK** — Steps 3/9 before Step 10 |
| **JT-SHELF-SUPPORT-SKIN** only after **PANEL-OUT-*** exist | **OK** — Step 11 after Step 10 (prep rivnuts on loose panels in Step 10) |
| Rivnuts on frame accessible from cavity | **OK** if side slabs last |
| **LIGHT-STRIP-001** service access with rear panel off | **OK** — Step 8 before Step 9 |
| Handle hardware without §F decision | **FLAG** — through-cut only; do not procure bolt-on handle |
| Shelf **JT-SHELF-SUPPORT-SKIN** (D-065) | **OK** — mechanical 3×M4/cleat; §P closed |
| Corner posts (**§R**, D-075) | **OK** — `FRAME-POST-*` restored; prototype FEA/load test still deferred (R-016) |
| Open-door + extended tray (**§Q**, D-076) | **OK** — struts present; door settle + post-face routing; vol≈0 vs tray/slide/plotter at 0/130/180/250 mm |

## Related documents

- Joining parameters: `config/parameters.yaml` (`hardware.fastener_*`, `joints.*`)
- RFQ template: `docs/12_PRODUCTION_RFQ_TEMPLATE.md`
- Open owner items: `docs/10_USER_INPUT_REQUIRED.md`
