# ADR-002: Geometry source of truth

- Status: Accepted
- Date: 2026-08-03

## Decision

Python generators and approved configuration own geometry. STEP is the neutral geometric handoff. DXF, PDF, STL, GLB, and renders are derived artifacts.

## Consequences

- Generated files are never edited as the normal change path.
- Any manufacturer correction that changes geometry must be returned to the Python source or recorded as an explicit vendor-owned native-CAD divergence.
- Two agents may not independently regenerate the same released part from different sources.

