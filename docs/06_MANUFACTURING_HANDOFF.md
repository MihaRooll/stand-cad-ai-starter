# Manufacturing handoff specification

## Package states

- `CONCEPT`: layout/appearance only.
- `REFERENCE_ONLY`: geometry or DXF may be incomplete or uncalibrated.
- `PRELIMINARY_NOT_FOR_PRODUCTION`: suitable for DFM/RFQ, not fabrication.
- `PROTOTYPE_RELEASED`: authorized for exactly the defined prototype quantity/revision.
- `SERIES_RELEASED`: authorized only after Gate G8.

## File naming

Use:

```text
<PROJECT>-<TYPE>-<NUMBER>-REV_<REV>-<STATUS>.<ext>
```

Examples:

```text
STAND-ASM-000-REV_A-PROTOTYPE_RELEASED.step
STAND-PRT-014-REV_A-PROTOTYPE_RELEASED.step
STAND-DRW-014-REV_A-PROTOTYPE_RELEASED.pdf
STAND-CUT-014-REV_A-PROTOTYPE_RELEASED.dxf
```

## Minimum package contents

### Assembly

- full formed assembly STEP;
- exploded/assembly drawing where needed;
- overall dimensions and mass estimate;
- centre-of-mass evidence;
- assembly sequence and critical alignment notes.

### Per manufactured part

- formed STEP;
- controlled PDF drawing;
- material and standard/grade;
- thickness or stock size;
- process and finish;
- quantity;
- general and critical tolerances;
- threads/inserts/weld symbols/finish masking as applicable;
- part ID and revision matching the BOM.

### DXF for cutting

- only after DFM and responsibility confirmation;
- 1:1 in millimetres;
- closed, non-self-intersecting contours;
- no duplicate/overlapping geometry;
- distinct layers/colours for cutting, marking, and bend reference when accepted by the target factory;
- no dimensions/title block in the cutting layer;
- one authoritative part/revision mapping;
- checked against the corresponding formed part and drawing.

### BOM

- part ID and revision;
- description;
- manufactured/bought-in classification;
- material/stock/finish;
- quantity per assembly and prototype order quantity;
- supplier/manufacturer part number for bought items;
- drawing/STEP/DXF references;
- mass when known;
- approval state.

## Manufacturer DFM record

Archive written confirmation of:

- processes and machines used;
- material/grade/thickness availability;
- preferred inside radii and bend tooling;
- bend deduction/K-factor/table responsibility;
- minimum flange and hole-to-bend limits;
- insert, weld, grinding, and finish constraints;
- achievable tolerances and cosmetic expectations;
- flat-pattern ownership;
- deviations from supplied model/drawing;
- prototype quantity, lead time, and inspection agreement.

## STEP limitation

STEP transfers precise geometry and assembly structure, but generally not the original editable feature history. If the manufacturer rebuilds a part in native sheet-metal CAD, record whether their native file becomes a vendor-owned manufacturing derivative or whether the corrected geometry is returned to and regenerated from canonical Python source.

## Release manifest

`00_MANIFEST.csv` contains filename, part ID, revision, status, byte size, checksum, generator commit, generator/config path, approver, and date. No unlisted file belongs to the release.

