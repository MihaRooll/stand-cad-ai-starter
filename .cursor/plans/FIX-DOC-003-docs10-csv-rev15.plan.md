```yaml
contract_id: FIX-DOC-003-docs10-csv-rev15
tier: T2
cycle: 1
sol_approved: null
goal: >
  Sync docs/10 §E/§F/§H intrusion + MAINS-INLET wording and CSV current-evidence
  pointers from stale rev13 / Y=185.9 to live rev15 / Y=179.8 without closing
  blockers or changing geometry.
live_measurements:
  handle_mount_y_mm: 179.8
  handle_mount_z_mm: 252
  tier2_intrusion_mm3: 1529766.0
  source: tests/test_geometry.py::test_handle_tier2_finger_intrusion_at_balance_point
  rel027_to_measure_leaves: 55
  source_rel027: tests/test_parameters.py::test_production_release_blocks_on_to_measure_parameters
  mass_headline: >
    Cite current rev15 mass_report.csv structural/all-parts from D-079 /
    HANDOFF (structural 9.590 kg / all-parts 13.383 kg) where PRD-006 asserts
    currency; label 8.806 kg as historical rev13 only.
derived_current_margins:
  grip_band_y_mm: "[124.8, 234.8]"
  service_port_aft_margin_mm: 40.2  # 275 - 234.8
  cable_aft_of_grip_mm: 85.2        # 320 - 234.8 (center-to-grip-aft formula matching §E)
steps:
  - id: S-1
    action: >
      docs/10 §E — replace sole-current Y=185.9 / ≈1,389,717 mm³ claim with
      Y=179.8 / ≈1,529,766 mm³; refresh aft margins to 40.2 / 85.2; keep D-063
      185.9 / historical table as superseded history. §F — update 1.39e6 →
      ≈1.53×10⁶ (or 1,529,766). §H — MAINS-INLET not currently modeled
      (D-071 removed placeholder); certified path deferred (D-036). §F/§M/§N/§A stay OPEN.
    owner: implementer
  - id: S-2
    action: >
      REQUIREMENTS_TRACEABILITY.csv — update currency claims for SWE-002/005/007,
      MFG-008, PLT-011/013/015/017/022/023, PRD-006 (and any other *current*
      rev13 / CONCEPT_REVISION=13 / mass 8.806 / 53-leaf REL-027 pointers) to
      rev15 evidence paths, CONCEPT_REVISION=15, REL-027=55, current mass
      headline; historical notes OK if labeled historical. PLT-013: MAINS-INLET
      deferred/not modeled (D-071), not "placeholder solid retained".
    owner: implementer
  - id: S-3
    action: >
      state — D-083 in DECISION_LOG; AUTONOMOUS_STATUS last-closed + HEAD note;
      PROJECT_STATE / ASSUMPTIONS only if needed for consistency; no geometry/config.
    owner: implementer
  - id: S-4
    action: adversarial-review against AC-1..AC-5 (docs honesty, no blocker close)
    owner: adversarial-reviewer
  - id: S-5
    action: Quick verify (packet verify_commands)
    owner: verifier
acceptance_criteria:
  - AC-1
  - AC-2
  - AC-3
  - AC-4
  - AC-5
forbidden:
  - close §F/§M/§N/§A or invent measurements
  - geometry/config/CONCEPT_REVISION changes
  - commit/push
```
