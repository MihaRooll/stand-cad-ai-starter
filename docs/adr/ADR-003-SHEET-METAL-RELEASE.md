# ADR-003: Sheet-metal release boundary

- Status: Accepted
- Date: 2026-08-03

## Decision

Do not treat AI-generated flat patterns as production-approved. Release DXF for bent sheet-metal parts only after the target manufacturer confirms material, thickness, bend radii, tooling constraints, allowance method, and flat-pattern ownership.

## Consequences

- Preliminary DXF must be marked `REFERENCE_ONLY`.
- Formed STEP and controlled PDF drawings precede production DXF.
- The DFM response is stored under the released revision.

