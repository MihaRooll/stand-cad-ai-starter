# Validation and acceptance

## Evidence levels

1. **Schema:** required fields and states are present.
2. **Deterministic geometry:** solids, part count, dimensions, placement, and clearances match expectations.
3. **Visual:** controlled views are reviewed for missing/incorrect geometry.
4. **Engineering:** load, stability, thermal, electrical, transport, and human-use risks have proportionate evidence.
5. **DFM:** target manufacturer confirms process-specific feasibility.
6. **Physical:** prototype inspection/test confirms the real item.

No lower level substitutes for a higher one.

## Software acceptance

- fresh `uv sync --extra dev` succeeds;
- config validator fails closed for production mode;
- unit tests pass;
- canonical targets regenerate without manual GUI edits;
- every exported part is a valid expected solid/compound;
- part labels/IDs and assembly placement are stable;
- reference geometry comparison detects unintended version drift;
- validation output is revisioned and reproducible.

## Geometry acceptance per revision

- expected overall bounding box;
- expected part and solid count;
- equipment body contained within support envelope;
- no unintended equipment/structure collision;
- required tray/shelf service access and organizer open-top/front removal paths clear;
- required ventilation and cable zones clear;
- transport restraints do not collide in either state;
- no zero-thickness/non-manifold/invalid result;
- front/right/top/isometric snapshots reviewed.

## Mechanical acceptance

Criteria must be quantified by the design engineer before release:

- shelf/support stress and deflection;
- fastener, insert, weld, latch, hinge, and handle capacity;
- foot/vibration-mount static load distribution (`hardware.foot_diameter_mm`, `materials.foot_height_*`);
- static tipping in worst operating configuration;
- dynamic transport cases, ramps, thresholds, and braking;
- safe deployment/stow sequence;
- sharp-edge, pinch/shear, and hot-zone controls.

## Thermal/electrical acceptance

- measured or sourced device power/heat data;
- air inlet/outlet path and recirculation review;
- heat-sensitive device separation;
- prototype thermal test points, duration, ambient condition, and pass thresholds;
- qualified review of power distribution, protective devices, earthing, connectors, strain relief, and cable rating.

## Prototype inspection

- incoming cosmetic and coating inspection;
- critical dimension report;
- equipment fit and removal test;
- full operating workflow test;
- load/roll/brake/threshold/tip tests;
- transport restraint test;
- ventilation/temperature test;
- cable and power test by qualified person;
- assembly/service time and tool list;
- defect log and disposition.

## Release acceptance

A release is rejected if any critical requirement is `TBD`, any enabled equipment input is unverified, any high risk lacks an owner/mitigation, any file/revision mapping conflicts, or DFM/prototype evidence required by the target gate is absent.

