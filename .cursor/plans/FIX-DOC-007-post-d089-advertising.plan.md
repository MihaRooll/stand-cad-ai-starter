---
contract_id: FIX-DOC-007-post-d089-advertising
tier: T2
cycle: 1
decision_id: D-090
sol_approved: null
---

# Plan — FIX-DOC-007-post-d089-advertising

## Live figures (do not invent; regenerate or read reports)

Source checked: `config/parameters.yaml` `case.height=540`; `tests/test_parameters.py` asserts 540;
`output/validation/rev15/mass_report.csv` (header): structural **9.651 kg**, all-parts **13.445 kg**;
`output/validation/rev15/stability_report.md`: lower tip factor **3.828**.

Implementer may re-run `uv run python scripts/generate_mass_report.py` and cite regenerated header numbers if they differ; otherwise pin these.

## Defect surfaces (sole-current advertising)

| Surface | Stale | Target |
|---|---|---|
| README envelope H | 529 | 540 |
| docs/12 envelope H | 529 | 540 |
| docs/12 + HANDOFF mass | 9.590 / 13.383 | 9.651 / 13.445 |
| docs/12 + HANDOFF tip lower | 3.785 | 3.828 |
| HANDOFF Open list PLT-012 | claims PASSING | CSV IN_PROGRESS — honest wording only |
| CSV PRD-006 / PLT-001 (+ mass/tip evidence if stale) | 529 / old kg | 540 + live paths/figures |

HANDOFF Product truth already has envelope 540; sync tip/mass/PLT-012 only there.

## Steps

```yaml
steps:
  - id: S-1
    action: Confirm live mass/tip via regenerate or read rev15 reports; record exact figures for D-090
    owner: implementer
  - id: S-2
    action: Update README + docs/12 envelope to 650×420×540; sync tip/mass tables to live figures
    owner: implementer
  - id: S-3
    action: Fix HANDOFF tip/mass + remove PLT-012 PASSING claim; keep §F/§M/§N/§A OPEN; no G-pass
    owner: implementer
  - id: S-4
    action: Sync CSV PRD-006/PLT-001 (and related mass/tip evidence cells) to 540 + live mass/tip
    owner: implementer
  - id: S-5
    action: Extend tests/test_concept_revision_docs.py to pin advertising docs to live case.height; forbid sole-current 529 envelope
    owner: implementer
  - id: S-6
    action: Record D-090 in DECISION_LOG; update AUTONOMOUS_STATUS + PROJECT_STATE
    owner: implementer
  - id: S-7
    action: Targeted verify then adversarial-reviewer + Quick verifier
    owner: operational-orchestrator
```

## Cycle 1 outcomes

- Implementer: complete (D-090 cites 540 / 9.651 / 13.445 / 3.828)
- Adversarial-reviewer: **accept** (findings: [])
- Verifier Quick: **pass** (406 passed, 1 xfailed; ruff clean)
- Residual out-of-scope: `state/ASSUMPTIONS.md` A-017 may still cite tip ≈3.785 (not owned)

## Acceptance map

- AC-1 → S-2
- AC-2 → S-1/S-2/S-3 + D-090 exact cites
- AC-3 → S-3
- AC-4 → S-4
- AC-5 → S-5
- AC-6 → S-6/S-7

## Forbidden

Geometry/config edits; commit/push; invent numbers; close blockers; mark G-pass or PLT-012 passed.
