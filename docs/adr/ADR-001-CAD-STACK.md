# ADR-001: AI-first CAD stack

- Status: Accepted
- Date: 2026-08-03

## Decision

Use Cursor, Python 3.12, `build123d==0.11.1`, and project-pinned `build123d-mcp==0.3.81` as the initial design environment.

## Rationale

The user can operate through natural-language agents in Cursor; source remains text, reviewable, parameterized, and version controlled; neutral manufacturing formats are available.

## Consequences

- A native sheet-metal CAD/technologist stage remains necessary for production flat patterns.
- Dependency upgrades require comparison against stored reference geometry.
- The initial workflow is Windows-native to reduce path and GUI-rendering variability.

