# Implementation plan and gates

The plan separates software completeness, engineering maturity, prototype release, and series release. Passing an early gate never implies passing a later one.

## Phase 0 — Repository and toolchain baseline

Work:

- initialize Git and preserve this archive as the baseline commit;
- verify Windows-native Python 3.12 and `uv`;
- lock dependencies;
- verify pinned `build123d-mcp` in Cursor;
- run input validator, smoke STEP, and tests;
- install MCP modeling/drawing/repair project rules only after the server works;
- optionally install CAD Skills for inspection/viewer/handoff, without creating a second geometry pipeline.

Deliverables:

- `uv.lock`;
- successful `output/smoke/calibration_block_REFERENCE_ONLY.step`;
- environment/version record in `state/PROJECT_STATE.md`;
- baseline Git tag or commit.

### Gate G0 — Toolchain reproducible

Pass when a fresh native Windows checkout can sync, test, create a valid smoke STEP, and connect to the pinned MCP version.

## Phase 1 — Evidence-backed requirements

Work:

- choose exact devices and quantities;
- collect manuals/datasheets and user measurements;
- photograph every device from six sides with a scale/reference;
- capture body, feet, moving, loading, thermal, connector, cable, and removal envelopes;
- record operating and transport sequences;
- capture doorway, elevator, vehicle, floor, ramp, event, storage, and power constraints;
- classify each value as verified/user-measured/manufacturer-documented/assumed/TBD.

Deliverables:

- completed config;
- evidence folder/index;
- resolved `docs/10_USER_INPUT_REQUIRED.md` for selected devices;
- requirement traceability statuses.

### Gate G1 — Fit-critical inputs complete

Pass when every enabled item has exact identity, dimensions, mass, support conditions, moving/service/thermal/cable zones, and provenance. No production geometry proceeds on approximate equipment data.

## Phase 2 — Layout concepts and construction strategy

Work:

- create simplified verified equipment envelopes first;
- produce at least three materially different layouts;
- show operating and transport configurations;
- compare footprint, mass estimate, centre of mass, workflow, access, heat separation, cable routing, manufacturability, cost drivers, and revision ease;
- compare viable construction families instead of assuming one;
- select a concept through a documented decision matrix.

Deliverables:

- layout STEP/GLB or renders;
- front/right/top/isometric images for each variant;
- decision matrix and ADR for chosen concept;
- preliminary manufacturer conversation package.

### Gate G2 — Layout and architecture approved

Pass when all equipment and service zones fit in both modes, the workflow is viable, major risks are visible, and the construction choice has evidence-based rationale.

## Phase 3 — Parametric skeleton and stable interfaces

Work:

- establish global coordinate system and named datums;
- implement equipment components, frame/shell skeleton, tier trays with slide extension, horizontal film-shelf dividers, side panels, handle cutout, and restraint locations;
- use stable part IDs and parameters;
- add automated bounding-box, solid-count, placement, and clearance tests;
- produce repeatable assembly STEP and snapshots.

Deliverables:

- canonical Python generators;
- parameter schema;
- tests and validation evidence;
- preliminary BOM structure.

### Gate G3 — Parametric architecture stable

Pass when a parameter change regenerates all explicit targets, every part remains valid, assembly interfaces are deterministic, and critical geometry has regression tests.

## Phase 4 — Detailed design and engineering checks

Work:

- detail frame/shell, tier trays, horizontal film shelves, panels, service access (open front/organizer top, tray slide-out), restraints, handles, ventilation, and cable management;
- estimate mass and centre of mass from verified inputs/materials;
- evaluate load paths, shelf/tray deflection, foot/vibration-mount load distribution, tipping cases, and dynamic transport loads with an appropriately qualified method;
- evaluate heat separation/airflow and define a prototype thermal test;
- obtain qualified electrical review for power distribution and earthing;
- eliminate sharp-edge, pinch, shear, hot-contact, and service-access hazards;
- perform independent design review.

Deliverables:

- detailed assembly and parts;
- engineering calculation/test records;
- risk mitigations;
- design-review findings and resolutions.

### Gate G4 — Engineering review complete

Pass when no high-severity mechanical/thermal/electrical/transport risk remains unowned and all safety-critical claims have evidence proportionate to risk.

## Phase 5 — Preliminary manufacturing package / RFQ

Work:

- assign material, thickness, finish, process, tolerance, and quantity per part;
- generate formed STEP parts and assembly;
- generate controlled preliminary PDF drawings;
- generate BOM and bought-in hardware list;
- include visible `PRELIMINARY / NOT FOR PRODUCTION` markings;
- submit the same RFQ package to multiple capable manufacturers when authorized;
- compare DFM feedback, not only price.

Deliverables:

- `review/RFQ_REV_*/` package;
- RFQ questions and response matrix;
- selected manufacturer decision record when user authorizes selection.

### Gate G5 — Manufacturer/process selected

Pass when the selected manufacturer confirms processes, materials, tooling constraints, tolerances, bend practice, flat-pattern responsibility, insert/weld/finish feasibility, and prototype scope.

## Phase 6 — Prototype release package

Work:

- incorporate DFM changes into canonical source or explicitly document vendor-native divergence;
- regenerate and revalidate everything;
- release production DXF only where responsibility is confirmed;
- cross-check filenames, part IDs, drawing titles, quantities, revisions, and BOM;
- create manifest and approval record;
- freeze release revision.

### Gate G6 — Prototype package released

Pass when `docs/06_MANUFACTURING_HANDOFF.md` and `reviews/FINAL_RELEASE_CHECKLIST.md` pass with no TBDs affecting fabrication.

## Phase 7 — Prototype manufacture and inspection

Work after explicit user authorization:

- build one prototype;
- inspect critical dimensions and fit;
- load, roll, brake, threshold, tip, service, operating, thermal, cable, and transport tests;
- record defects, deviations, rework, usability findings, photos, and measurements;
- update risks and source.

### Gate G7 — Prototype validated

Pass when the physical item satisfies the approved inspection plan and all deviations are dispositioned.

## Phase 8 — Corrective revision and series release

Work:

- apply prototype learning to canonical source;
- repeat deterministic, visual, engineering, and DFM checks;
- publish a new revision; never overwrite the prototype release;
- obtain required approvals.

### Gate G8 — Series production release

Pass only after prototype validation, corrected revision, manufacturer confirmation, complete manifest, and explicit user authorization.
