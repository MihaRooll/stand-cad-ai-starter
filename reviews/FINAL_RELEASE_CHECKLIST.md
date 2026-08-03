# Final starter-archive release checklist

This checklist releases only the repository starter. It does not approve a stand, enclosure, prototype order, or production file.

## Scope and governance

- [x] Previous recommendation reviewed and corrected.
- [x] Updated Russian recommendation and start guide included.
- [x] One canonical geometry source and one-writer policy defined.
- [x] Demo, review, prototype, and series states separated.
- [x] Gates G0–G8 define maturity and stop conditions.
- [x] Opus 5 receives a self-contained startup contract.

## Manufacturing boundary

- [x] STEP/PDF/DXF are not described as manufacturing approval.
- [x] Bent-sheet DXF is gated by target-manufacturer DFM and bend responsibility.
- [x] STEP feature-history limitation is documented.
- [x] Mechanical, stability, transport, thermal, electrical, and physical checks are distinct.
- [x] Prototype precedes series release.

## Input/release safety

- [x] Production validator fails closed on unverified enabled equipment.
- [x] Exact project/model/manufacturer/provenance/transport state is required.
- [x] Powered and heat-source items require corresponding verified data.
- [x] Series release requires a prototype inspection record.
- [x] Sheet-metal bend gates are process-conditional.

## Reproducibility and package verification

- [x] Locked dependency synchronization succeeds in the Linux verification container.
- [x] Input validator passes the explicit demo configuration.
- [x] Ruff static checks pass.
- [x] Pytest passes: 9 tests.
- [x] Reference-only smoke STEP has expected 100 × 60 × 20 mm bounds.
- [x] Pinned MCP executable reports version 0.3.81.
- [x] Checksum manifest verifies before packaging.
- [x] ZIP integrity verifies and excludes environments/caches/generated CAD.

## Known blockers carried forward

- [x] Real geometry remains blocked until exact equipment/site/workflow inputs pass G1.
- [x] Prototype release remains blocked until engineering and manufacturer DFM gates pass.
- [x] Series release remains blocked until prototype inspection and corrective revision pass.

Final disposition: PASS for the starter archive. Native Windows G0 and all hardware gates remain open as documented.
