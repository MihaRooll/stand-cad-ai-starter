# Cycle 1 — factual and recommendation audit

Date: 2026-08-03

## Questions tested

1. Does the proposed MCP explicitly support Cursor?
2. Does the tool provide a render/measure/validate/export feedback loop?
3. Are current versions identifiable and pinnable?
4. Are STEP/DXF/PDF relevant to the target manufacturing conversation?
5. Did the original answer overstate manufacturing readiness?
6. Is a custom plugin required now?

## Findings

- `build123d-mcp` explicitly documents Cursor setup and the local stdio subprocess model.
- It exposes persistent CAD sessions, render, measurement, inspection, validation, import/export, and drawing workflows.
- Current reviewed versions are `build123d 0.11.1` and `build123d-mcp 0.3.81`.
- Moscow/Russian production examples accept STEP, DXF, PDF, and specifications, but individual factory rules differ.
- The original answer correctly selected the stack but conflated transferable files with production readiness.
- A custom MCP would duplicate existing capability and add maintenance risk. Project-specific behavior belongs first in repository rules, validators, and export scripts.

## Corrections applied

- Added a source-of-truth hierarchy.
- Added explicit version pinning and an update policy.
- Added manufacturer DFM and sheet-metal release gates.
- Added Windows-native setup as the default.
- Reframed vendor links as capability evidence, not recommendations.

## Cycle result

PASS for architectural direction. Production-readiness language required and received major correction.

