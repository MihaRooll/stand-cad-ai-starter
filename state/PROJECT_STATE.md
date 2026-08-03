# Project state

- Project: Mobile equipment stand/enclosure
- Current phase: Phase 0 — repository and toolchain baseline
- Current gate: G0
- Status: Three-cycle-reviewed starter archive; repository not yet initialized by user
- Last updated: 2026-08-03

## Completed

- Three-cycle specification review completed.
- CAD stack and version policy selected.
- Source-of-truth, DFM, autonomy, and release boundaries recorded as ADRs.
- Repository starter, validation scaffold, and implementation plan prepared.
- Linux-container baseline passed during archive preparation; native Windows verification remains part of G0.
- Locked dependency sync passed with 53 resolved packages.
- Input demo validation passed explicitly with `--allow-demo`.
- Ruff passed and pytest passed: 9 tests.
- Reference-only STEP regenerated with verified bounds 100 × 60 × 20 mm.
- Pinned `build123d-mcp` executable reported version 0.3.81.

## Active work after extraction

1. Initialize Git and create baseline commit.
2. Verify Windows-native `uv`/Python/MCP.
3. Verify the committed `uv.lock` resolves on Windows.
4. Run validator, smoke model, lint, and tests.
5. Record exact Windows-observed versions and outputs.

## Current blockers

- Exact equipment selection for this stand.
- Verified equipment envelopes and masses.
- Operating/transport constraints.
- Budget, deadline, and final external-size constraints.

These block G1 and real geometry, not Phase 0 software implementation.

## Next decision

After G0, complete the consolidated input packet in `docs/10_USER_INPUT_REQUIRED.md` and start equipment envelopes only for verified selected models.
