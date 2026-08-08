```yaml
contract_id: FIX-DOC-002-handoff-rev15
tier: T2
cycle: 3
sol_approved: null
goal: >
  Rewrite HANDOFF_PROMPT.md current product-truth / startup evidence / mission
  from stale rev13 to live rev15 + D-075…D-081 truths. Keep historical Already
  closed rows honest. Keep §F/§M/§N/§A OPEN. Point agents to AUTONOMOUS_STATUS.md.
acceptance_criteria:
  - id: AC-1
    text: Startup checklist points to rev15 evidence pack and CONCEPT_REVISION=15
  - id: AC-2
    text: >
      Product truth matches live params — upper_extension=0, lower 250,
      handle Y from parameters (179.8), mass/tip from rev15 (upper tip N/A),
      posts restored, doors, no false MAINS/INTERLOCK present claims
  - id: AC-3
    text: Mission continue-from is rev15 not rev13; mention AUTONOMOUS_STATUS.md
  - id: AC-4
    text: >
      Historical closed-list lines rephrased (no current-zone CONCEPT_REVISION=13);
      test scans HANDOFF current zones for live revision
  - id: AC-5
    text: Update AUTONOMOUS_STATUS; D-082; Quick verify including test_concept_revision_docs.py
owned_files:
  - HANDOFF_PROMPT.md
  - tests/test_concept_revision_docs.py
  - state/AUTONOMOUS_STATUS.md
  - state/DECISION_LOG.md
  - state/PROJECT_STATE.md
  - .cursor/plans/FIX-DOC-002-handoff-rev15.plan.md
forbidden:
  - Do not close owner blockers or invent measurements
  - Do not change geometry/config
  - Do not commit/push
steps:
  - id: S-1
    action: >
      Rewrite HANDOFF First actions §4 evidence paths to rev15 + CONCEPT_REVISION=15;
      refresh Product truth header/table to D-075…D-081 live truths; rephrase
      Already-closed historical CONCEPT_REVISION=13 lines; keep §F/§M/§N/§A OPEN;
      Immediate mission → rev15 + AUTONOMOUS_STATUS.md pointer; first-actions
      read list includes state/AUTONOMOUS_STATUS.md.
    owner: implementer
  - id: S-2
    action: >
      Update tests/test_concept_revision_docs.py to pin HANDOFF current zones
      (startup / Product truth / Immediate mission) to live CONCEPT_REVISION;
      allow historical closed-list narrative without assign-form =13 as current.
    owner: implementer
  - id: S-3
    action: >
      Append D-082 to DECISION_LOG; refresh AUTONOMOUS_STATUS (close FIX-DOC-002,
      remove HANDOFF backlog item); brief PROJECT_STATE pointer update.
    owner: implementer
  - id: S-4
    action: Mandatory adversarial-reviewer on doc honesty / AC coverage.
    owner: adversarial-reviewer
  - id: S-5
    action: >
      Verifier Quick — pytest test_concept_revision_docs.py; full pytest; ruff.
    owner: verifier
  - id: S-6
    action: >
      Cycle 2 (adversarial rework F-1…F-4): remove stale 210600 lid/shuttle from
      Product truth + Open §M; tier-2 headroom 4→50 mm; §F intrusion ≈1,529,766 mm³
      at Y=179.8; dual-tray 0.924 marked historical; extend test current zones to
      include Open list + forbid 210600/lid-shuttle narrative + require 50 mm.
    owner: implementer
  - id: S-7
    action: Mandatory adversarial-reviewer re-pass on cycle-2 honesty fixes.
    owner: adversarial-reviewer
  - id: S-8
    action: >
      Cycle 3 blocker-only (F-7…F-9): align PROJECT_STATE "## Current blockers"
      with HANDOFF cycle-2 — 27/50 mm headroom, no 210600 lid/shuttle; handle
      Y=179.8 / ≈1,529,766 mm³; transport interlock absent procedure-only;
      dual-tray 0.924 historical.
    owner: implementer
  - id: S-9
    action: Mandatory adversarial-reviewer re-pass on cycle-3 blocker fixes.
    owner: adversarial-reviewer
```

## Live product-truth sources (do not invent)

| Field | Live value | Source |
|---|---|---|
| `CONCEPT_REVISION` | **15** | `export.py` / README |
| Evidence | `output/validation/rev15/`, `*_rev15.{step,glb,stl,manifest.json}` | filesystem |
| Envelope | 650 × 420 × 529 mm | PROJECT_STATE / params |
| `upper_extension` | **0** | parameters.yaml D-076 |
| `lower_extension` | **250** | parameters.yaml |
| `lower_quick_access_extension_mm` | **130** | parameters.yaml |
| `handle_mount_y_mm` | **179.8** (D-074; supersedes 185.9) | parameters.yaml / docs/10 §F |
| `handle_mount_z_mm` | **252** | unchanged |
| Grip band Y | ≈ [124.8, 234.8] mm | docs/10 §F |
| Posts | Restored `FRAME-POST-*` (D-075; supersedes D-070) | DECISION_LOG |
| Doors | `DOOR-LOWER/UPPER-001` + struts; D-076 choreography CLOSED §Q | docs/10 |
| Interlock | **Absent** (D-067) — procedure only | DECISION_LOG |
| MAINS-INLET | **Not modeled** (D-071); certified path deferred D-036; cable passthrough remains | DECISION_LOG / RFQ |
| Mass structural / all-parts | **9.590 / 13.383 kg** | rev15 mass_report / docs/12 |
| Fasteners | **162** indicative (158 registry + 4 FOOT M4; base_clad_m3=0) | docs/12 |
| Tip lower @250 | **3.785** | rev15 stability / docs/12 |
| Tip upper | **N/A** (D-076/D-077) | docs/12 |
| STACK-CAP | ~0.118 kg (4×0.0294) | FIX-DOC-001 |
| REL-027 | **55** | FIX-DOC-001 |
| Tests | Prefer live AUTONOMOUS_STATUS count (~383 passed, 1 xfailed) over stale 363/375 | AUTONOMOUS_STATUS |
| Open blockers | §F handle, §M lid headroom, §N tray/film retention (plotter tie-down waived), §A | unchanged |

## Historical closed-list rewrite pattern

Replace assign-form current claims such as `` `CONCEPT_REVISION`=13 `` with historical phrasing, e.g. “at D-062 delivery `CONCEPT_REVISION` was 13” / “rev13 PDF package (historical)”. Do not leave Product truth / First actions / Immediate mission claiming rev13 as current.

## Anti-false-conclusion

- Doc sync ≠ G0–G8 pass.
- Indicative mass/tip remain non-authoritative for G4.
- Do not restore INTERLOCK/MAINS solids via prose.
