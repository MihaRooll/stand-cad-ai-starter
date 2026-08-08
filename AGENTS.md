# Agent operating contract

This file is binding for every agent working in this repository.

## Mission

Develop a parametric, inspectable, prototype-ready light desktop tower for two Silhouette cutting plotters and the evidence needed for a manufacturer DFM review. Progress the project autonomously while preserving a hard boundary between design intent and production release.

## Principal roles

- **Principal orchestrator / final arbiter:** Opus 5.
- **Implementer:** the single agent currently authorized to edit product source.
- **Researcher:** gathers exact equipment/manufacturer evidence and records provenance; does not edit released geometry.
- **Reviewer:** inspects requirements, code, drawings, and geometry; does not edit product source in the review turn.
- **Verifier:** executes tests/checks and records reproducible evidence; does not silently fix failures.

Opus 5 may assign lower-cost subagents to bounded work. Keep one production writer at a time. Review findings are actionable only when they identify the requirement, file/path, evidence, consequence, and proposed correction.

## Order of authority

1. Explicit current user instruction.
2. Safety and manufacturing release gates in this repository.
3. Accepted ADRs in `docs/adr/`.
4. Approved requirements and configuration.
5. Implementation plan.
6. Agent preference.

## Source of truth

- Geometry: Python generators under `src/` plus approved config.
- Requirement state: `state/REQUIREMENTS_TRACEABILITY.csv`.
- Current progress: `state/PROJECT_STATE.md`.
- Decisions: `state/DECISION_LOG.md` and accepted ADRs.
- Assumptions: `state/ASSUMPTIONS.md`.
- Generated CAD files are outputs. Do not make untracked edits to them.

## Mandatory startup sequence

1. Read `README.md`, this file, `OPUS_5_START_PROMPT.md`, all accepted ADRs, and `state/PROJECT_STATE.md`.
2. Inspect the repository and working tree before editing.
3. Verify Windows-native `uv`, Python, tests, and the smoke STEP.
4. Verify the project MCP server is connected and reports the pinned version.
5. Update `state/PROJECT_STATE.md` with the active phase, plan, and blockers.
6. Work through `docs/05_IMPLEMENTATION_PLAN.md` in gate order.

## CAD workflow

For each meaningful geometry change:

1. Identify requirement IDs and parameters affected.
2. Edit the smallest responsible Python/config source.
3. Regenerate explicit targets only.
4. Use `build123d-mcp` incrementally: render, measure, inspect, and validate.
5. Check expected bounding boxes, part count, solids, placement, clearance, and collisions.
6. Review at least orthographic front/right/top and isometric views.
7. Store evidence under `output/validation/<revision>/`.
8. Update traceability and project state.
9. Check `docs/14_CAD_MODELING_CONVENTIONS.md` for an established pattern before re-deriving a fix — cladding bounds, render depth tie-break, and the stability moment split all have documented precedents there.
10. For a new chat continuation, start from `HANDOFF_PROMPT.md` rather than re-deriving status from old plan notes. Prefer Quick verification inside a stage; reserve Full for stage/revision close (see `.cursor/rules/21-orchestration-overlay.mdc`).

Never use `--no-sandbox` merely to make an MCP script work. Never expose MCP HTTP mode outside localhost; the reviewed server documentation states that HTTP mode has no built-in authentication.

## Autonomy rules

- Proceed without asking on reversible software architecture, naming, tests, documentation, and non-critical modeling choices.
- When data is missing, implement schemas, validators, placeholders, and independent modules, then continue.
- Consolidate blocking questions in `docs/10_USER_INPUT_REQUIRED.md`; do not repeatedly interrupt the user.
- Ask/stop only when an answer changes fit, load, stability, heat, electrical safety, transport safety, procurement, destructive action, or production outcome.
- Do not infer exact equipment dimensions from visually similar models.
- Do not mark a web dimension as verified unless exact model/revision provenance and orientation are recorded.

## Production release prohibitions

Do not label or place an artifact under a production release when any of the following is true:

- enabled equipment has unverified dimensions, mass, or service zones;
- operating and transport configurations are not both modeled;
- material/thickness/joining strategy is undecided;
- stability, load path, caster, thermal, service, or cable checks are incomplete;
- critical tolerances are absent;
- the chosen manufacturer has not completed DFM;
- sheet-metal flat-pattern responsibility and bend data are unconfirmed;
- prototype inspection is required but not complete.

`REFERENCE_ONLY`, `CONCEPT`, and `PRELIMINARY` must be obvious in filename/title block for non-released outputs.

## Definition of done

Software implementation is done only when tests, deterministic geometry checks, and visual snapshots pass. Prototype release is done only when Gate G6 in the implementation plan passes. Series release is done only after the physical prototype inspection and corrective revision pass Gate G8.

## Required handoff at every completed phase

- what changed;
- requirements satisfied;
- commands/checks executed and results;
- generated artifacts and revision;
- unresolved risks and blockers;
- next autonomous step.

