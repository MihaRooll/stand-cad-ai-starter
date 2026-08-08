# PROD-001 — Weld-free joining + FAST ITERATION exit / RFQ campaign

```yaml
contract_id: PROD-001-weldfree-rfq-campaign
tier: T3
cycle: 1
sol_approved: true
principal_status: APPROVED_BY_MAIN_OVERRIDE
principal_attempts: 2
campaign_status: COMPLETE
campaign_close: >
  2026-08-06: S-1…S-14 executed. Passes 1–5 adversarial closed (pass 5 APPROVED).
  Verifier Full verdict pass; blockers_open=0. No G0–G8 passed. Owner §F/§N/§M/§A/§P OPEN.
principal_note: >
  Main override 2026-08-06: S-0 treated approved without third principal attempt.
  Gap1 (5 thematic passes vs MAX_REVIEW_CYCLES=3 rework depth) and Gap2 (AC-4 -k
  lid exclusion + Full exit 0 precedent from D-057) ratified. Proceed S-1…S-14.
goal: >
  Exit FAST ITERATION MODE (D-060): specify weld-free bolt/screw joining for every
  structural joint, write assembly sequence, discharge deferred verification, run 5
  independent thematic adversarial review PASSES, finalize CONCEPT/PRELIMINARY RFQ
  package for Moscow DFM. Never mark production-ready or pass G0–G8 (Human Gate).
acceptance_criteria:
  - id: AC-1
    text: >
      Named joint types in config/parameters.yaml (hardware.fastener_* / joints registry)
      with fastener type, nominal size, qty/joint, PART_ID pair; torque/exact length
      marked to_measure where unsourced; aluminium_angle_15x15x1.5 buildability rationale recorded.
  - id: AC-2
    text: >
      docs/15_ASSEMBLY_INSTRUCTIONS.md ordered sequence with real PART_IDs; each step
      buildability-checked (no impossible reach-through); sequencing DFM issues fixed or flagged.
  - id: AC-3
    text: >
      docs/12_PRODUCTION_RFQ_TEMPLATE.md joining section states decided weld-free method
      (manufacturer may counter-propose); honest open-item vs DFM-question split; all 12+ questions present.
  - id: AC-4
    text: >
      Formal verify suite exits 0: ruff clean; pytest -q excluding the Human-Gate-deferred
      lid-envelope test (see INV-LID); regenerate.py exit 0; setup_windows.ps1 exit 0.
      Separately record the still-failing lid-envelope test as Human Gate deferral §M
      (not a silent greenwash — evidence of fail retained in DEFERRED_VERIFICATION).
  - id: AC-5
    text: >
      D-058/D-059 geometry re-verified on final tree (height 529, light-strip, shelf supports,
      rear bullnose, FR notch); DEFERRED_VERIFICATION rows closed only with real evidence;
      owner-decision rows remain OPEN and in docs/10.
  - id: AC-6
    text: >
      Exactly 5 independent thematic adversarial-reviewer PASSES (distinct Diff scopes:
      req/geom, DFM, joining/assembly, drawings/RFQ, close-out). Rework per finding still
      capped at MAX_REVIEW_CYCLES=3 (cycle 3 blocker-only). These are NOT 5 rework cycles
      on one Diff — they are 5 sequential independent reviews. BLOCKED if unresolved after cap.
  - id: AC-7
    text: >
      CONCEPT_REVISION bumped; drawing package regenerated with fastener call-outs,
      REFERENCE_ONLY in DXF, fabricator questions; mass/stability/deflection refreshed including fastener mass;
      REL-027 to_measure count updated; D-061+ decision log; PROJECT_STATE D-060 block updated.
  - id: AC-8
    text: >
      Honest ready-to-send vs owner-decision-first split; package positioned on Phase 5
      pre-G5 ladder (no G5/G6 claim).
owned_files:
  - config/parameters.yaml
  - src/stand_cad/parameters.py
  - src/stand_cad/schema.py
  - src/stand_cad/geometry/hardware.py
  - src/stand_cad/geometry/services.py
  - src/stand_cad/geometry/frame.py
  - src/stand_cad/geometry/panels.py
  - src/stand_cad/geometry/trays.py
  - src/stand_cad/geometry/dividers.py
  - src/stand_cad/geometry/assembly.py
  - src/stand_cad/geometry/export.py
  - src/stand_cad/geometry/analysis.py
  - src/stand_cad/geometry/registry.py
  - src/stand_cad/geometry/part_trace.py
  - src/stand_cad/geometry/collision.py
  - scripts/generate_drawings.py
  - scripts/generate_mass_report.py
  - scripts/regenerate.py
  - scripts/doctor.py
  - tests/**
  - docs/12_PRODUCTION_RFQ_TEMPLATE.md
  - docs/15_ASSEMBLY_INSTRUCTIONS.md
  - docs/10_USER_INPUT_REQUIRED.md
  - docs/14_CAD_MODELING_CONVENTIONS.md
  - state/DECISION_LOG.md
  - state/PROJECT_STATE.md
  - state/ASSUMPTIONS.md
  - state/REQUIREMENTS_TRACEABILITY.csv
  - state/DEFERRED_VERIFICATION.md
  - HANDOFF_PROMPT.md
verify_commands:
  - uv run ruff check .
  - uv run pytest -q --tb=line -k "not test_lid_envelope_no_intersection_in_service_states"
  - uv run python scripts/regenerate.py
  - powershell -ExecutionPolicy Bypass -File .\scripts\setup_windows.ps1
human_gate_deferrals:
  - id: INV-LID
    test: tests/test_kinematics.py::test_lid_envelope_no_intersection_in_service_states
    reason: >
      Intentionally left failing (≈210600 mm³ LID-ENVELOPE-P1 vs INTERLOCK-SHUTTLE) pending
      owner lid-headroom decision §M / docs/10. Excluded from formal exit-0 verify suite;
      still executed once for evidence and kept OPEN in DEFERRED_VERIFICATION — not waived.
forbidden:
  - Mark any artifact production-ready or move G0–G8 to passed
  - Invent critical equipment/load/heat/electrical/transport/bend/torque data as verified fact
  - Silently resolve owner-only decisions (handle §F, transport §N, lid §M, §A measurements)
  - Concurrent writers; reviewer/verifier product edits
  - git commit/push unless Main/user explicitly requests
steps:
  - id: S-0
    action: Principal-arbiter pre-write approve on this plan + invariants
    owner: principal-arbiter
  - id: S-1
    action: >
      STREAM 1 — Weld-free joining design. Propose buildable method for 15×15×1.5 Al angle
      (corner brackets/gussets + M3–M4 machine screws into rivnuts/threaded inserts or
      through-bolts where access allows; no welding). Panel-to-frame: screw from inside into
      frame / bonded+mechanically backed for 3 mm opal PMMA cavity walls. Shelf supports:
      specify attachment beyond D-059 placeholder. Encode joint TYPEs in parameters.yaml +
      hardware.py registry (type, size, qty, PART_ID A↔B). Add optional lightweight bracket
      solids only if needed for mass/BOM honesty — keep CONCEPT/REFERENCE_ONLY. Write
      docs/15_ASSEMBLY_INSTRUCTIONS.md with sequenced PART_IDs; fix sequencing DFM or flag.
      Rewrite RFQ joining section. Log D-061 (next ID after D-060). Update ASSUMPTIONS +
      REQUIREMENTS_TRACEABILITY.
    owner: implementer
  - id: S-2
    action: >
      STREAM 2 — Discharge verification debt. Fix stale 544 mm / top_structure tests to 529 mm
      if geometry correct (or fix geometry if regression). Re-verify D-058/D-059 claims on
      current tree. Close DEFERRED_VERIFICATION OPEN rows only with command evidence; leave
      owner-decision rows OPEN + docs/10. Regenerate mass/stability/deflection including
      fastener mass; update REL-027 count. Run Full profile.
    owner: implementer
  - id: S-3
    action: >
      STREAM 4 (drawings) — Bump CONCEPT_REVISION; regenerate drawing package with joining
      call-outs, REFERENCE_ONLY in every DXF, fabricator Qs from RFQ; complete RFQ template
      honestly (open owner blockers listed separately from DFM questions).
    owner: implementer
  - id: S-4
    action: "Adversarial cycle 1 — Requirements/geometry/parameters/physics vs TRACEABILITY + TZ"
    owner: adversarial-reviewer
  - id: S-5
    action: "Implementer fix cycle for S-4 blockers (max 3 cycles per issue)"
    owner: implementer
  - id: S-6
    action: "Adversarial cycle 2 — DFM/ergonomics/thermal/electrical/transport/tooling"
    owner: adversarial-reviewer
  - id: S-7
    action: "Implementer fix cycle for S-6 blockers"
    owner: implementer
  - id: S-8
    action: "Adversarial cycle 3 — Stream 1 joining design + assembly-sequence buildability"
    owner: adversarial-reviewer
  - id: S-9
    action: "Implementer fix cycle for S-8 blockers"
    owner: implementer
  - id: S-10
    action: "Adversarial cycle 4 — Drawing package + manufacturer-readiness"
    owner: adversarial-reviewer
  - id: S-11
    action: "Implementer fix cycle for S-10 blockers"
    owner: implementer
  - id: S-12
    action: "Adversarial cycle 5 — Final consolidated close-out with fresh evidence"
    owner: adversarial-reviewer
  - id: S-13
    action: "Verifier Full profile + AC map; independent of implementer claims"
    owner: verifier
  - id: S-14
    action: "Update PROJECT_STATE D-060 block; compact handoff to Main"
    owner: operational-orchestrator
```

## Joining design intent (proposed — implementer refines with geometry ground truth)

### Frame profile constraint

- Member: `aluminium_angle_15x15x1.5` — 15×15 mm leg, 1.5 mm wall.
- Too thin for clean hand welding; owner forbids welding (D-060).
- **Proposed method:** stamped/cut aluminium corner brackets (nominal **20×20×2 mm** L-gusset or equivalent stock) at each rail-to-post node; **M4×12** pan-head machine screws into **M4 rivnuts** (or equivalent threaded inserts) set in the angle legs where wall access allows; where both faces are accessible, **M4 through-bolt + nyloc nut**. Quantity baseline: **2 fasteners per rail end** into bracket, **2 bracket-to-post**. Exact length/torque = `to_measure`.

### Joint type catalogue (minimum)

| Joint type ID | Connects (examples) | Method |
|---|---|---|
| `JT-FRAME-CORNER` | `FRAME-POST-*` ↔ `FRAME-RAIL-*` (base/org/top/tray rings) | Corner bracket + M4 |
| `JT-PANEL-OUTER-FRAME` | `PANEL-OUT-*` ↔ frame posts/rails | Screw from cavity/inside into frame; PMMA not load-bearing primary path; optional adhesive backup `to_measure` |
| `JT-PANEL-INNER-FRAME` | `PANEL-IN-*` ↔ frame | M3/M4 into frame / clips |
| `JT-TRAY-SLIDE-FRAME` | `SLIDE-*` / tray rails ↔ `FRAME-RAIL-TRAY-*` | M4 machine screws per slide manufacturer pattern (`to_measure` pitch) |
| `JT-SHELF-SUPPORT-SKIN` | `SHELF-SUPPORT-*` ↔ `PANEL-OUT-{LEFT,RIGHT}` | Bonded + mechanical backup (rivnut from cavity) — supersedes D-059 placeholder ambiguity |
| `JT-HANDLE-HARDWARE` | Handle hardware ↔ side slab | **OWNER OPEN (§F)** — document provisional through-cut only; no invented bolt-on spec as decided |

### Assembly sequence principles

1. Feet → base ring rails + posts → vertical growth (org ring → tray rails → top three-sided ring).
2. Install tray slides/rails before closing outer skins that block access.
3. Inner panels / media supports before outer skins where screw access is from inside.
4. Outer side slabs last (or with temporary access openings) so cavity rivnuts remain reachable.
5. Equipment/film are transport-load items — retention still owner-open (§N); instructions note "install after structure, restrain per owner decision".

## Owner-decision blockers (must stay in docs/10 — do not invent)

- §F handle concept
- §N transport retention
- §M lid-open headroom
- §A real-equipment measurements still open
- Shelf-support attachment may be *proposed* as JT-SHELF-SUPPORT-SKIN but flag if owner must ratify adhesive vs bracket

## Gate positioning (honest)

- This campaign advances **Phase 5 — Preliminary manufacturing package / RFQ** work products.
- **Does not** claim Gate G5 (manufacturer selected) or G6 (prototype released).
- Human must still authorize vendor send (docs/10 §B) and later G5/G6.

## Review policy

- **Clarification for MAX_REVIEW_CYCLES=3 vs owner “5 reviews” mandate:**
  - `MAX_REVIEW_CYCLES=3` = rework loop depth on findings for a *single* Diff/issue (implement→review→fix; cycle 3 blocker-only).
  - Owner asked for **5 independent thematic review PASSES** = five sequential `adversarial-reviewer` invocations with **distinct Diff scopes** (requirements, DFM, joining, drawings, close-out). Each pass may itself open a ≤3-cycle rework loop.
  - This is compliant: we do not run 5 rework cycles on one Diff.
- Exhausted rework cap on a finding → BLOCKED in handoff (never silent done).
- Principal max 2 attempts.
