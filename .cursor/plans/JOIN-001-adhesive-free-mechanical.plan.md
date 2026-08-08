# JOIN-001 — Adhesive-free joining + documentation accuracy

```yaml
contract_id: JOIN-001-adhesive-free-mechanical
tier: T2
cycle: 2
terminal: done
sol_approved: null
goal: >
  Owner 2026-08-06: no adhesive/glue anywhere; every joint purely mechanical
  (screws/bolts/brackets/rivnuts), matching D-060 no-weld constraint. Close §P
  with a decided M4 shelf-support method and real screw count/pattern. Fact-check
  HANDOFF_PROMPT.md / PROJECT_STATE.md top / README status against live
  parameters.yaml + fresh Quick verify. Do not re-run full PROD-001 campaign.
acceptance_criteria:
  - id: AC-1
    text: >
      hardware.panel_adhesive_backup removed; no adhesive/bond primary method
      remains in joints.*; JT-PANEL-OUTER-FRAME and JT-SHELF-SUPPORT-SKIN are
      mechanical-only with decided wording (provenance verified or derived, not
      "proposed OPEN §P").
  - id: AC-2
    text: >
      JT-SHELF-SUPPORT-SKIN has real M4 size/count/pattern sized from
      SHELF-SUPPORT-* geometry (17 mm cavity span × film clear_depth ≈330 mm);
      docs/10 §P CLOSED with those numbers; D-065 (or next free ID) logged.
  - id: AC-3
    text: >
      docs/15, docs/12, docs/04 MEC-009, REQUIREMENTS_TRACEABILITY MEC-009,
      ASSUMPTIONS A-016 (and any shelf-adhesive rows) have zero adhesive primary
      language; FOOT-* and PANEL-CLAD-FRONT-BASE-001 get a decided mechanical
      method or an explicit flagged exception with reasoning.
  - id: AC-4
    text: >
      HANDOFF_PROMPT.md, PROJECT_STATE.md top summary, README status section
      match live config (650×420×529, CONCEPT_REVISION=13, STACK-CAP-*,
      weld-free+adhesive-free catalogue, open list §F/§N trays+film/§M/§A —
      §P closed; plotter tie-down note per owner).
  - id: AC-5
    text: >
      uv run ruff check . exit 0; uv run pytest -q only sanctioned failure
      test_lid_envelope_no_intersection_in_service_states; regenerate.py exit 0.
owned_files:
  - config/parameters.yaml
  - src/stand_cad/geometry/dividers.py
  - src/stand_cad/geometry/hardware.py
  - scripts/generate_drawings.py
  - docs/10_USER_INPUT_REQUIRED.md
  - docs/12_PRODUCTION_RFQ_TEMPLATE.md
  - docs/15_ASSEMBLY_INSTRUCTIONS.md
  - docs/04_REQUIREMENTS_CHECKLIST.md
  - state/REQUIREMENTS_TRACEABILITY.csv
  - state/ASSUMPTIONS.md
  - state/DECISION_LOG.md
  - state/PROJECT_STATE.md
  - state/DEFERRED_VERIFICATION.md
  - HANDOFF_PROMPT.md
  - README.md
  - tests/ (only if joint-registry / REL-027 oracles need sync)
forbidden:
  - Mark any G0–G8 passed or production-ready
  - Invent equipment/load/torque as verified fact (torque stays to_measure)
  - Silently close §F, §M, §A, or open parts of §N (tray/film retention)
  - Re-run full PROD-001 campaign scope
  - Parallel writers / reviewer edits
verify_commands:
  - uv run ruff check .
  - uv run pytest -q
  - uv run python scripts/regenerate.py
steps:
  - id: S-1
    action: Plan artifact (this file)
    owner: operational-orchestrator
  - id: S-2
    action: Implement adhesive-free catalogue + §P close + doc fact-check sync
    owner: implementer
  - id: S-3
    action: Adversarial review — shelf-support mechanical joint + doc number re-derive
    owner: adversarial-reviewer
  - id: S-4
    action: Verifier Quick (ruff + full pytest + regenerate)
    owner: verifier
  - id: S-5
    action: Rework cycles ≤3 if reviewer/verifier rework (cycle 3 blocker-only)
    owner: operational-orchestrator
```

## Engineering intent (shelf supports — AC-2)

Cleat geometry (`dividers.py::build_single_shelf_support`): X span **3→20 mm** (17 mm cavity), Y = `film_storage_horizontal.clear_depth` (**330 mm**), Z = divider thickness. Six cleats L/R × 3 shelves.

**Decided method (implementer must encode, not leave OPEN):**

- Sole method: **M4 pan-head into M4 rivnut** — **no adhesive**.
- **qty_per_joint = 3** per cleat (front / mid / rear along Y), nominal pitch ≈ **150 mm** (= `hardware.fastener_panel_pitch_mm`) over 330 mm clear depth — supersedes prior proposed qty=2 adhesive+backup.
- Rivnuts seat in the **aluminium cleat** (not as primary pull-out in 3 mm PMMA alone). Fastener access: cavity-side install sequence already in docs/15 (prep rivnuts before side-slab close). If exterior countersinks through opal skin are required for clamp-up, document them as flush M4 and keep cosmetic note — preferred over glue.
- If implementer judges cleat+3×M4 insufficient for peel without skin bond: add a **small Al angle bracket** leg tied **2×M4** into nearest frame member (`FRAME-RAIL-ORG-*` / post) **in addition to** or **instead of** skin screws — document real count in D-065. Do not invent allowable stress as verified; mark stack-up/`to_measure` where unknown.
- Update `hardware.py` screw totals (was 6 cleats × 2; becomes 6 × 3 = +6 M4 vs prior shelf line).
- `dividers.py` docstrings: remove "bonded" language; cite D-065 mechanical method.
- `verify_on_real_machine` may remain True for hole positions / grip length, but method is **decided**.

## Cosmetic / feet judgement calls

| Part | Decision guidance |
|---|---|
| `FOOT-*` | Prefer mechanical: Ø clearance + M3/M4 or rivet through foot into post/base rail. If only stick-on pad is sane, **flag explicit exception** with reasoning — do not silently keep adhesive language. |
| `PANEL-CLAD-FRONT-BASE-001` | Prefer flush **countersunk M3/M4 into rail rivnuts** or clip — not tape/adhesive. |
| `MEDIA-SUPPORT-*` | Screw to frame/panel per JT-PANEL-INNER or dedicated M3/M4 — no "bond or…". |
| Historical "bonded" in D-040 prose / docs/14 | Do not rewrite ancient decision-log physics metaphors; fix **active** design docs and parameter methods. docs/14 "bonded strip" may become "flush-mounted mechanical cladding strip". |

## Doc fact-check targets (AC-4)

Re-derive from `config/parameters.yaml` + live helpers, not from old decision prose:

- Envelope **650 × 420 × 529**; assembly Z with STACK-CAP ≈ **537** if still true.
- `CONCEPT_REVISION`=**13**; evidence `output/validation/rev13/`.
- Joining: weld-free **and adhesive-free**; §P **CLOSED**.
- STACK-CAP-* + JT-STACK-CAP-POST (D-064).
- Handle Y: re-read live `hardware.handle_mount_y_mm` (HANDOFF currently contradicts itself: 185.9 vs 165.7 vs D-055 187.6 — fix to live value).
- Mass / screw counts: recompute after qty change; do not copy stale 144/152 without check.
- Open list: §F, §N (tray/film; note owner — plotters specifically don't need tie-down), §M, §A. Remove §P from open.
- PROJECT_STATE top still saying §P OPEN → fix.
- README status section if present — sync same truths.

## REL-027 / tests

Removing `panel_adhesive_backup` and flipping JT-SHELF method provenance from `to_measure`→`verified`/`derived` will change REL-027 count — update oracles in `tests/test_parameters.py` / drawings JOIN-001 text if they assert counts or §P OPEN strings.

## Invariants

No G0–G8. No invented verified torque. Sole writer = implementer. Reviewer/verifier read-only.
