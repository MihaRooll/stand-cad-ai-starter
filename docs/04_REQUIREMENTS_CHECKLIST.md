# Requirements checklist

Requirement IDs are stable. Add rows rather than renumbering existing items.

## Product definition

- `PRD-001`: selected equipment set and quantity are explicit.
- `PRD-002`: operating workflow is described step by step.
- `PRD-003`: transport workflow is described step by step.
- `PRD-004`: target user height/reach and service ergonomics are defined.
- `PRD-005`: external appearance references and finish expectations are recorded.
- `PRD-006`: maximum allowed external dimensions and mass are verified.

## Equipment facts

- `EQP-001`: exact manufacturer/model/revision is recorded.
- `EQP-002`: verified body dimensions and orientation are recorded.
- `EQP-003`: verified operating and transport mass are recorded.
- `EQP-004`: feet/contact points and support-plane requirements are recorded.
- `EQP-005`: moving parts and full movement envelopes are recorded.
- `EQP-006`: loading/consumable replacement zones are recorded.
- `EQP-007`: ventilation intake/exhaust and thermal restrictions are recorded.
- `EQP-008`: power, data, connector positions, plug protrusion, and cable bend zones are recorded.
- `EQP-009`: maintenance/removal path is recorded.
- `EQP-010`: transport orientation, levelling, shock, ink/liquid, and restraint requirements are recorded.

## Mechanical

- `MEC-001`: load path from every device to floor is explicit.
- `MEC-002`: shelves/supports have rated loads and deflection acceptance.
- `MEC-003`: casters have verified type, diameter, brake arrangement, mounting, and capacity with engineering margin.
- `MEC-004`: worst-case centre of mass and tipping cases are evaluated in operating and transport modes.
- `MEC-005`: dynamic transport cases and thresholds/ramps are considered.
- `MEC-006`: doors, drawers, extensions, and presses cannot create uncontrolled tipping.
- `MEC-007`: restraint, latch, hinge, and handle loads are defined.
- `MEC-008`: sharp edges, pinch/shear points, and hot-contact zones are mitigated.
- `MEC-009`: fasteners, inserts, welds, adhesives, and serviceability are specified.

## Thermal/electrical

- `THE-001`: heat sources and temperatures/duty cycle are recorded.
- `THE-002`: ventilation design is based on evidence or conservative analysis and test.
- `THE-003`: hot equipment is separated from heat-sensitive devices and combustibles.
- `ELE-001`: total and peak electrical load are recorded.
- `ELE-002`: power distribution, protective devices, earthing, strain relief, and cable routing receive qualified review.
- `ELE-003`: external cable entry/exit and trip-risk controls are defined.

## Manufacturing

- `MFG-001`: material and thickness are specified per part.
- `MFG-002`: finish, colour, texture, masking, and cosmetic class are specified.
- `MFG-003`: tolerances and critical-to-function dimensions are explicit.
- `MFG-004`: minimum hole-edge/bend distances and tool access are reviewed.
- `MFG-005`: weld distortion, access, grinding, and cosmetic requirements are reviewed.
- `MFG-006`: bought-in hardware uses orderable part identifiers.
- `MFG-007`: target manufacturer DFM response is archived.
- `MFG-008`: sheet-metal flat-pattern ownership and bend parameters are confirmed.
- `MFG-009`: prototype inspection plan and measurement tools are defined.

## Software and evidence

- `SWE-001`: one canonical Python generator exists per released part/assembly.
- `SWE-002`: configuration validates before CAD generation.
- `SWE-003`: generated solids, dimensions, count, placement, and clearances are tested.
- `SWE-004`: reference STEP regression detects dependency-caused geometry drift.
- `SWE-005`: every output carries project/part/revision/status identifiers.
- `SWE-006`: manifest hashes and traceability exist for a release.
- `SWE-007`: front/right/top/isometric views are reviewed for every release candidate.

