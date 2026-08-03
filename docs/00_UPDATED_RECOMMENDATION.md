# Updated recommendation

**Decision as of 2026-08-03:** use Cursor + Python `build123d` + pinned local `build123d-mcp` as the primary AI-first CAD workflow. Use a manufacturing engineer's native sheet-metal CAD workflow only for DFM, bend finalization, and production release.

## Why this is the simplest viable option

- The editable design source remains ordinary Python and configuration files in Git.
- Cursor can change parameters and geometry without the user learning a conventional CAD UI first.
- `build123d-mcp` gives the agent a visual and geometric feedback loop rather than blind code generation.
- STEP, DXF, SVG, STL, renders, measurements, and engineering-drawing workflows are available without writing a custom MCP server first.
- A manufacturer or constructor can open the neutral STEP handoff in SolidWorks, FreeCAD, Inventor, or another professional CAD system.

## Precise boundary of the recommendation

This stack is recommended for:

- requirements capture;
- equipment envelopes and service zones;
- layout variants;
- parametric parts and assemblies;
- collision and clearance checks;
- repeatable STEP export;
- visual review;
- preliminary drawings, BOM, and RFQ packages.

It is **not by itself** proof of:

- structural strength;
- tip resistance under transport or operation;
- electrical or fire safety;
- correct sheet-metal bend allowance for a specific press and tooling;
- manufacturability at a specific factory;
- compliance with an unnamed standard;
- production readiness.

## Source-of-truth hierarchy

1. `src/` Python + approved configuration are the editable design source of truth.
2. Validated STEP is the neutral geometric handoff.
3. PDF drawings and requirements carry tolerances, materials, finish, critical dimensions, and assembly intent.
4. DXF is a manufacturing derivative, not the design source.
5. Renders are approval aids only.

Do not allow `build123d-mcp` and an external CAD skill to create independent competing versions of the same model. External CAD Skills may guide validation, viewing, and handoff, but all geometry changes must return to the same Python generator.

## Version policy

- Python: `3.12.x` for the initial Windows-native implementation.
- `build123d`: `0.11.1` in `pyproject.toml`.
- `build123d-mcp`: `0.3.81` in `.cursor/mcp.json`.
- Do not use `@latest` in the working repository.
- Update only on a dedicated branch after the smoke model, tests, and a reference STEP comparison pass.

## Physical design recommendation

Do not lock the stand into a monocoque sheet-metal, welded-frame, aluminium-profile, or plywood architecture before the equipment set, operating mode, loads, transport constraints, and manufacturer capabilities are known.

For a one-off prototype, a hybrid architecture may be easier to revise, but that is an engineering hypothesis to compare during Phase 2—not a predetermined construction.

## Final professional handoff

For bent sheet-metal parts, hand the manufacturer the formed STEP model and controlled PDF drawing first. Ask the selected production technologist to confirm material, thickness, minimum inside radius, tooling constraints, bend deduction/K-factor practice, hole-to-bend rules, and responsibility for flat-pattern generation. Release cutting DXF only after that response is recorded.

