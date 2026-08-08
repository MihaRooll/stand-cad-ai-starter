```yaml
contract_id: FIX-DOC-001-rfq-rev15
tier: T2
cycle: 2
sol_approved: null
orchestration_result: >
  IMPLEMENT done; adversarial cycle1 rework (F-1 blocker fastener 167→162,
  F-2 STACK-CAP ~0.118); cycle2 closed F-3 REL-027=55, F-4 §N plotter waived;
  adversarial approve; verifier Quick pass. No commit.
goal: >
  Sync manufacturer-facing docs/12 and README current-status from stale rev13
  advertising to live CONCEPT_REVISION=15 using rev15 evidence paths/numbers.
  Keep owner blockers OPEN. No production/G-pass claims. No geometry/config edits.
acceptance_criteria:
  - AC-1: docs/12 subject + Attached package → CONCEPT rev15 / *_rev15.* paths
  - AC-2: mass/tip table from rev15 (structural ~9.590, all-parts ~13.383,
          tip lower ~3.785, tip upper N/A D-076); §F/§M/§N/§A remain OPEN
  - AC-3: README current-status advertises rev15 / CONCEPT_REVISION=15
  - AC-4: regression test pins advertising docs to CONCEPT_REVISION; no false-fail
          on HANDOFF "Already closed" historical CONCEPT_REVISION=13 lines
  - AC-5: AUTONOMOUS_STATUS + DECISION_LOG D-079 (or next); no gates passed
steps:
  - id: S-1
    action: >
      Update docs/12_PRODUCTION_RFQ_TEMPLATE.md: subject + Attached package
      paths to rev15 (STEP under output/concept/*_rev15.step; drawings/dxf/mass/
      stability under output/validation/rev15/). Refresh indicative mass/tip rows
      from mass_report.csv + stability_report.md only. Tip upper = N/A (D-076/D-077),
      not 3.348. Keep §F/§M/§N/§A OPEN. Honesty edit for MAINS-INLET-001: D-071
      removed display solid — must not imply placeholder solid is in the package;
      deferred certified path (D-036), not procured. Do not blind-replace historical
      narrative elsewhere. Leave fastener/bracket/deflection rows only if still
      matching live headers or clearly still indicative; do not invent new counts.
    owner: implementer
  - id: S-2
    action: >
      Update README.md current-status line to rev15 / CONCEPT_REVISION=15;
      keep open blockers and no G0–G8 language.
    owner: implementer
  - id: S-3
    action: >
      Add tests/test_concept_revision_docs.py: import CONCEPT_REVISION from
      export.py; fully scan README.md + docs/12 for advertising pins (no stale
      rev{N-1} / CONCEPT_REVISION={N-1} in those files' live advertising sections).
      For HANDOFF_PROMPT.md: either exclude entirely OR scan only Product truth /
      Immediate mission / startup checklist zones — never whole-file (historical
      "Already closed" may retain CAPITAL CONCEPT_REVISION=13). Prefer full scan
      of README + docs/12.
    owner: implementer
  - id: S-4
    action: >
      State: AUTONOMOUS_STATUS.md close/move backlog item #2; DECISION_LOG D-079
      (next free id after D-078); PROJECT_STATE.md brief forward pointer. Do not
      mark any G0–G8 passed. Optional minimal HANDOFF mission/evidence pointer
      only if required so AC-4 scoped zones pass — no full HANDOFF rewrite.
    owner: implementer
  - id: S-5
    action: Targeted then Quick verify per contract; no commit/push.
    owner: implementer
  - id: S-6
    action: Mandatory adversarial-reviewer on docs honesty + test false-fail risk.
    owner: adversarial-reviewer
  - id: S-7
    action: Independent verifier Quick profile (pytest + ruff).
    owner: verifier
evidence_pins:
  - path: src/stand_cad/geometry/export.py
    note: CONCEPT_REVISION = 15
  - path: output/validation/rev15/mass_report.csv
    note: structural 9.590 kg; all-parts 13.383 kg; fasteners 0.174 kg / 158
  - path: output/validation/rev15/stability_report.md
    note: tip lower 3.785; tip upper N/A (D-076)
  - path: output/concept/light_plotter_tower_ASSEMBLY_CONCEPT_REFERENCE_ONLY_rev15.step
    note: live CONCEPT STEP
forbidden:
  - No geometry/config/CONCEPT_REVISION changes
  - No closing §F/§M/§N/§A; no invented measurements; no G-pass claims
  - No commit/push; no ИИ советы/
  - No full HANDOFF rewrite beyond optional mission/evidence pointer
owned_files:
  - docs/12_PRODUCTION_RFQ_TEMPLATE.md
  - README.md
  - tests/test_concept_revision_docs.py
  - state/AUTONOMOUS_STATUS.md
  - state/DECISION_LOG.md
  - state/PROJECT_STATE.md
  - .cursor/plans/FIX-DOC-001-rfq-rev15.plan.md
verify_commands:
  - uv run pytest tests/test_concept_revision_docs.py -q --tb=short
  - uv run ruff check tests/test_concept_revision_docs.py
  - uv run pytest -q --tb=line
  - uv run ruff check .
```
