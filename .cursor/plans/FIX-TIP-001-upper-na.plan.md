# FIX-TIP-001 — Upper zero-travel tip factor N/A

```yaml
contract_id: FIX-TIP-001-upper-na
tier: T2
cycle: 3
sol_approved: null
goal: >
  After D-076 (trays.upper_extension=0), stop treating upper tip_factor=inf as a
  tip_factor_min compliance pass. Mark zero-travel tip case N/A in report/API;
  keep lower@250mm finite tip assert meaningful. Do NOT invent tip numbers;
  do NOT pass Gate G4 / PLT-010.
acceptance_criteria:
  - AC-1: StabilityReportInputs exposes applicable=False or status=N/A when
    trays.{level}_extension<=0; tip_factor_min comparison must not treat
    non-finite factor as pass.
  - AC-2: test asserts finite lower factor >= tip_factor_min at 250mm AND
    upper zero-travel is N/A / not tip-applicable (fails today on vacuous inf>=min).
  - AC-3: write_stability_report does not print "Tip factor: inf (minimum …)"
    for upper@0; prints N/A / not applicable (D-076) instead.
  - AC-4: Lower tip math unchanged; tip_factor_min unchanged; upper_extension=0;
    no G4/PLT-010 PASSING; no production-ready labels.
  - AC-5: Regenerate output/validation/rev{CONCEPT_REVISION}/stability_report.md
    (and RFQ copy if workflow copies it) to match AC-3.
owned_files:
  - src/stand_cad/geometry/analysis.py
  - scripts/generate_mass_report.py
  - tests/test_geometry.py
  - scripts/_stage1_metrics.py
  - state/PROJECT_STATE.md
  - state/DECISION_LOG.md
  - state/REQUIREMENTS_TRACEABILITY.csv
  - .cursor/plans/FIX-TIP-001-upper-na.plan.md
forbidden:
  - Do not change trays.upper_extension or invent synthetic upper tip factor
  - Do not mark G4 / PLT-010 PASSING or production-ready
  - Do not expand into collision allowlist, docs/12 full rev sync, mass-header
  - Do not commit/push
steps:
  - id: S-1
    action: >
      Failing-first: rewrite test_indicative_tip_factor_non_authoritative (or
      successor) so lower@full extension asserts math.isfinite(factor) and
      factor >= tip_factor_min; upper with extension<=0 asserts tip not
      applicable (report.applicable is False / status N/A) and does NOT use
      inf >= tip_factor_min as a pass. Keep PLT-010 non-authoritative wording.
    owner: implementer
  - id: S-2
    action: >
      Mirror PARAM-015 upper@0 skip (parameters.py ~646-647): in
      stability_report_inputs, when extension_mm <= 0 set applicable=False
      (or status="N/A") citing D-076; keep computed arms/moments for audit but
      exclude from tip_factor_min compliance. Prefer bool applicable + optional
      status str. Do not invent a finite substitute factor.
    owner: implementer
  - id: S-3
    action: >
      indicative_tip_factor: document that float('inf') at zero travel is
      arithmetic-only, not a compliance pass; callers must use
      stability_report_inputs().applicable (or equivalent) before comparing to
      tip_factor_min. Optionally raise or return a sentinel only if all call
      sites updated — prefer keeping float return + applicable gate on report.
    owner: implementer
  - id: S-4
    action: >
      write_stability_report _tier_section: if not applicable, print Tip factor
      N/A / not applicable (D-076 zero travel) — never "Tip factor: inf
      (minimum …)". Legacy factor line: either N/A or clearly non-compliance.
      _stage1_metrics.py: print N/A for non-applicable tier.
    owner: implementer
  - id: S-5
    action: >
      Regenerate stability_report.md via existing generate_mass_report /
      write_stability_report entrypoint into
      output/validation/rev{CONCEPT_REVISION}/; if RFQ package workflow copies
      that file, refresh the copy the same way the script already does — do not
      invent a parallel RFQ path. Confirm upper section shows N/A.
    owner: implementer
  - id: S-6
    action: >
      State: DECISION_LOG D-077 (or next id) records honesty fix — zero-travel
      tip N/A, not pass; PROJECT_STATE notes FIX-TIP-001; PLT-010 row stays
      IN_PROGRESS / not PASSING; update evidence path to current rev report.
      tip_factor_min and upper_extension unchanged.
    owner: implementer
  - id: S-7
    action: >
      Targeted verify: pytest -k "tip_factor or stability_split"; ruff on
      touched py files; then Quick (pytest -q + ruff check .).
    owner: implementer
  - id: S-8
    action: Mandatory adversarial review; fix blockers only.
    owner: adversarial-reviewer
  - id: S-9
    action: Grok verifier Quick profile after green targeted.
    owner: verifier
```

## Design notes (binding for implementer)

### Root cause (confirmed — do not re-litigate)

- D-076 sets `trays.upper_extension=0`.
- Split-mass model yields `overturn_arm < 0` → `overturn_moment <= 0` → `factor = inf`.
- `test_indicative_tip_factor_non_authoritative` does `factor >= tip_factor_min` → vacuous True.
- Published `stability_report.md` prints `Tip factor: inf (minimum 1.5)` implying compliance.

### Pattern to mirror

`parameters.py` PARAM-015 (~646–647): `if tier_label == "upper" and float(extension) <= 0.0: continue` — TZ overhang N/A at zero travel. Tip check should use the same `extension <= 0` applicability gate (prefer generic `extension_mm <= 0` for either tier so lower@0 would also be N/A if ever configured that way).

### API sketch (minimal)

```python
@dataclass
class StabilityReportInputs:
    ...
    applicable: bool  # False when extension_mm <= 0 (D-076 / zero-travel)
    # factor may still be inf for audit; MUST NOT be compared to tip_factor_min when not applicable
```

Report text when `not applicable`:

- `Tip factor: N/A — not applicable (D-076; zero travel / no overhang tip case)`
- Do **not** print minimum beside inf.

### Out of scope

- Collision allowlist, docs/12 RFQ full sync, mass-header MAINS/INTERLOCK
- Changing `trays.upper_extension`, inventing finite upper tip, Gate G4 / PLT-010 PASSING
- Commit/push (Main owns git)

## Residual risks (pre-implement)

- Broader PLT-010 cases (lean / dual-tray) still fail TZ floor — honesty fix only.
- Call sites outside owned files that compare `indicative_tip_factor(...) >= min` without `applicable` may still vacuous-pass if any exist; implementer should grep and fix only owned call sites (`_stage1_metrics.py`, tests, report writer).
