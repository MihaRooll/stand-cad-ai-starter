```yaml
contract_id: FIX-MASS-001-header-honesty
tier: T2
cycle: 1
sol_approved: null
goal: >
  Stop mass_report header from claiming MAINS-INLET-001 / INTERLOCK-* / EDGEGUARD-*
  are physically present when absent from transport after D-046/D-067/D-071.
acceptance_criteria:
  - AC-1: header must not claim those IDs present when absent from transport.parts
  - AC-2: failing-first pytest via write_mass_report (or equivalent)
  - AC-3: regen output/validation/rev15/mass_report.csv; copy RFQ if present
  - AC-4: no geometry/config/mass-formula changes; no G4/PLT-012 PASSING; no invented masses
  - AC-5: AUTONOMOUS_STATUS backlog #2 closed; DECISION_LOG D-078; PLT-012 stays IN_PROGRESS if touched
owned_files:
  - scripts/generate_mass_report.py
  - tests/test_geometry.py
  - state/AUTONOMOUS_STATUS.md
  - state/DECISION_LOG.md
  - state/PROJECT_STATE.md
  - state/REQUIREMENTS_TRACEABILITY.csv
  - .cursor/plans/FIX-MASS-001-header-honesty.plan.md
  - output/validation/rev15/mass_report.csv
  - output/RFQ_PACKAGE_rev15/mass_report.csv
forbidden:
  - mass formulas, densities, part emission, geometry/config
  - marking gates passed / production-ready
  - docs/12 full rev sync, collision allowlist
  - commit/push; ИИ советы/
steps:
  - id: S-1
    action: >
      Add failing-first pytest that builds header text via write_mass_report
      (temp path or StringIO-equivalent path under tmp) and asserts regenerated
      header does NOT claim MAINS-INLET / INTERLOCK / EDGEGUARD are physically
      present when those prefixes are absent from build_transport_assembly parts.
      Prefer asserting against live transport.parts presence rather than only
      static string bans if cheap. Must fail on current lie at
      scripts/generate_mass_report.py:89-91.
    owner: implementer
  - id: S-2
    action: >
      Fix header wording only in generate_mass_report.py. Keep honest wording
      for categories that remain in transport (e.g. SLIDE-*, VIBMOUNT-*). Do not
      invent mass numbers. Preferred: list only still-present excluded categories
      (static honest text is OK if matched to current transport); do not claim
      absent categories are physically present. No changes to mass_report_rows,
      part_mass_kg, densities, or assembly emission.
    owner: implementer
  - id: S-3
    action: >
      Regenerate via write_mass_report only into
      output/validation/rev15/mass_report.csv; if
      output/RFQ_PACKAGE_rev15/mass_report.csv exists, copy the same file there.
      Do not run full regenerate.py / stability / deflection unless required.
    owner: implementer
  - id: S-4
    action: >
      Close AUTONOMOUS_STATUS backlog item #2; add DECISION_LOG D-078 (next free
      after D-077); brief PROJECT_STATE note if needed; if PLT-012 CSV row is
      touched for honesty, status must remain or become IN_PROGRESS (do not
      newly mark PASSING). No gate PASS.
    owner: implementer
  - id: S-5
    action: Mandatory adversarial-reviewer on header honesty + AC scope.
    owner: adversarial-reviewer
  - id: S-6
    action: >
      Quick verify — pytest -k mass_report; ruff on touched py; full pytest -q;
      ruff check .
    owner: verifier
evidence:
  - path: scripts/generate_mass_report.py
    lines: 89-91
    excerpt: 'Other excluded categories (SLIDE-*, MAINS-INLET-001, INTERLOCK-*, EDGEGUARD-*, VIBMOUNT-*, etc.) are physically present'
  - decisions: D-046 EDGEGUARD removed; D-067 INTERLOCK removed; D-071 MAINS-INLET removed
  - still_present: SLIDE=6 VIBMOUNT=8 in transport
verify_commands:
  - uv run pytest -k "mass_report" --tb=short -q
  - uv run ruff check scripts/generate_mass_report.py tests/test_geometry.py
  - uv run pytest -q --tb=line
  - uv run ruff check .
```
