# Prototype manufacturing RFQ template

Subject: DFM and quotation request — light desktop plotter tower prototype — `light_plotter_tower` / **CONCEPT rev15** (`REFERENCE_ONLY`)

## Project summary

We need one functional prototype of a light desktop tower for two Silhouette cutting plotters plus horizontal film storage, for event operation and transport. The attached package is marked **`PRELIMINARY` / `CONCEPT` / `NOT FOR PRODUCTION` / `REFERENCE_ONLY`** and is submitted for DFM and quotation only.

**Overall envelope (derived):** **650 × 420 × 529 mm** (W × D × H).  
**Frame:** 15×15×1.5 mm aluminium angle — **no welding** (owner requirement D-060).  
**Joining (concept level, D-061/D-063/D-064):** 20×20×2 mm aluminium corner brackets + M4/M3 pan-head machine screws into rivnuts. Frame corners: **2×M4 per node** (1 per bracket leg — dual M4 per 15 mm angle leg rejected for edge distance). **Stacking (D-064):** four **STACK-CAP-*** parts + **JT-STACK-CAP-POST** (2×M4 per cap into post tops). Full joint schedule: `config/parameters.yaml` `joints.*`, drawing sheet **JOIN-001**, assembly sequence **`docs/15_ASSEMBLY_INSTRUCTIONS.md`**. Manufacturer may counter-propose equivalent brackets, insert brands, and screw lengths after DFM — we expect written rationale.

Expected processes may include cutting, bending, profile/tube fabrication, **mechanical fastening only (no welded frame)**, inserts, grinding, powder coating, and final assembly.

## Owner responsibilities and known gaps (read before quoting)

These items are **not** resolved in the attached STEP/PDF package. Do not infer completed design from geometry presence alone.

### Owner-decision blockers (must be resolved by owner before production release — not DFM alone)

| ID | Topic | Status |
|---|---|---|
| §F | Handle concept — through-cut grip only; tier-2 finger intrusion ≈1,502,834 mm³ (≈1.50×10⁶) at Y=181.3 / Z=263 | **OPEN** |
| §N | Transport retention — tray/film unrestrained; plotter tie-down waived (owner 2026-08-06) | **OPEN** |
| §M | Lid-open headroom — transport clear gaps tier 1 27 mm / tier 2 50 mm vs 80 mm provisional lid envelope | **OPEN** |
| §A | Real-equipment measurements (feed plane, lid envelope, sheet thickness, …) | **OPEN** |

### DFM / manufacturer-quotation questions (we invite your written response)

1. **Joining counter-proposals:** For each joint type in **JOIN-001**, confirm feasibility or propose alternatives (bracket stock, rivnut vs rivet, through-bolt access).
2. **Grip lengths / torques:** Nominal M4×12 and M3×10 called out; all install torques and final grip lengths marked **`to_measure`** until prototype stack-up — quote allowance for trial assembly.
3. **Panel-to-frame:** 3 mm opal PMMA cavity walls are **not** primary structural load path; confirm screw pitch (~150 mm). **Adhesive-free** — M4 pan-head into frame rivnuts only (D-065).
4. **Slide mounting:** `JT-TRAY-SLIDE-FRAME` — hole pattern **`to_measure`** until slide part number selected (`trays.slide_rail_*`).
5. Which proposed construction/material/thickness changes do you recommend and why?
6. Which processes and machines would you use?
7. Minimum inside bend radii, flange lengths, hole-to-bend distances, tool clearances?
8. Flat patterns from formed STEP vs customer DXF — who owns bend deduction/K-factor?
9. Economically held tolerances vs drawing changes required?
10. Inserts, hinges, **non-welded** fasteners — accessibility from cavity with side slabs installed last?
11. Powder-coat preparation, masking, colour/texture, minimum batch constraints?
12. Ambiguous or impossible-to-inspect details in the package?
13. First-article inspection scope and measurement report format?
14. Quote engineering/NRE, prototype, optional corrected second prototype, delivery, lead times **separately**.
15. Identify every intended deviation before manufacture.

### Settled concept facts (do not re-open without owner approval)

1. **Electrical arrangement — NOT engineered.** Owner routes extension cord through **SVC-CABLE-PASSTHROUGH-001** (D-036). Safe in-case distribution remains owner responsibility (R-005).

2. **Flat patterns and bend data — factory-owned until DFM says otherwise.** Per ADR-003: preliminary DXF stays **`REFERENCE_ONLY`**; formed STEP and controlled PDF precede production DXF.

3. **`MAINS-INLET-001` — deferred certified inlet path** (D-036); **not modeled** in the current CONCEPT package (D-071 removed the display solid). Do not procure as a specification. Prototype electrical entry is **`SVC-CABLE-PASSTHROUGH-001`** only (owner-routed extension cord).

4. **Weld-free frame — mandatory.** Do not quote welded 15×15×1.5 mm angle joints; propose bolted brackets/gussets instead.

## Attached package (CONCEPT rev15)

| Artifact | Path / note |
|---|---|
| Formed assembly STEP | `output/concept/light_plotter_tower_ASSEMBLY_CONCEPT_REFERENCE_ONLY_rev15.step` |
| PRELIMINARY PDF drawings | `output/validation/rev15/drawings/light_plotter_tower_DRAWINGS_PRELIMINARY_CONCEPT_NOT_FOR_PRODUCTION_rev15.pdf` — sheets GA/OP/SEC/BOM/**JOIN-001**/OPEN/DET |
| REFERENCE_ONLY DXF (flat panels) | `output/validation/rev15/dxf/*_REFERENCE_ONLY_rev15.dxf` |
| Assembly instructions | `docs/15_ASSEMBLY_INSTRUCTIONS.md` |
| Indicative mass report | `output/validation/rev15/mass_report.csv` |
| Stability / deflection | `output/validation/rev15/stability_report.md`, `deflection_report.md` |
| BOM + joint schedule | PDF **BOM-001**, **JOIN-001** |

## Indicative mass figures (NOT Gate G4 — regenerate for latest)

Figures below are **indicative** from `scripts/generate_mass_report.py` at regenerate time; cavity-wall side-slab policy per D-055 (see OPEN-001).

| Metric | Typical rev15 order of magnitude |
|---|---|
| Empty structural (excl. verify_on_real_machine parts) | **9.590 kg** |
| All-parts (+ plotters in model) | **13.383 kg** |
| Bought-in fasteners (indicative, excl. structural total) | **≈0.174 kg** registry (**158** screws: **137 M4 + 21 M3** from `joints.*`) **+ 4 FOOT M4** supplementary (`hardware.py::supplementary_fastener_instances`; `base_clad_m3=0` since D-069 removed BASE cladding) → **162** total indicative |
| Corner brackets (indicative, not all modeled as solids) | **0.145 kg** (34 nodes: 22 JT-FRAME-CORNER + 12 JT-TRAY-RAIL-FRAME) |
| Stacking caps (D-064, four **STACK-CAP-***) | **~0.118 kg** indicative (4× **0.0294 kg** per `mass_report.csv` / `part_mass_kg`; 40×40×8 mm plate less Ø30.75×2.5 mm recess) |
| Stacking cap fasteners | included in registry **158** (**JT-STACK-CAP-POST**, 4 corners × qty 2) |
| Tip factor lower tier @ 250 mm ext / 420 mm depth | **3.785** (split-mass model D-039; incl. D-061 joining roll-up) |
| Tip factor upper tier | **N/A — not applicable** (D-076 zero travel / no overhang tip case; D-077 policy) |
| Tray deflection (3-rail indicative model @ 10 kg) | ~0.23 mm vs 1.5 mm ceiling |
| REL-027 `to_measure` leaf count | **55** (see `state/REQUIREMENTS_TRACEABILITY.csv` PLT-017; live validator oracle in `tests/test_parameters.py`) |

## Release boundary

Do not manufacture from this RFQ package. A separate `PROTOTYPE_RELEASED` revision with manifest will follow after DFM resolution, owner closure of §F/§N/§M/§A blockers, and written authorization (`docs/10` §B).
