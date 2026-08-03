# ADR-004: Agent autonomy and blockers

- Status: Accepted
- Date: 2026-08-03

## Decision

Opus 5 proceeds autonomously on all reversible, non-safety-critical work. It consolidates fit-critical questions into `docs/10_USER_INPUT_REQUIRED.md`, uses explicit non-production placeholders where useful, and continues all independent work.

It must stop the affected release path when a missing fact changes fit, load, stability, heat, electrical safety, transport safety, or manufacturing outcome.

## Consequences

- The project does not stall because one input is missing.
- Missing inputs cannot be silently converted into assumptions.
- No production label is permitted while a blocker remains open.

