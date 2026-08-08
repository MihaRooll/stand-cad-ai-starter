# DOC-001 — Bring documentation into agreement with rev6 product reality

Status: DRAFT for implementer. Tier: T2 (set by Main; do not reclassify). Sole writer:
`implementer` (composer-2.5-fast). Review + verify: `cursor-grok-4.5-high-fast`
(`adversarial-reviewer` mandatory, then `verifier`). Cap: 3 review/verify cycles, third cycle
closes blockers only.

Pre-change checkpoint: `44a743a` (HEAD at contract start). No geometry, config, or source-of-truth
numeric change is authorized in this stage — this is a documentation-only correction pass. If any
finding below looks like it requires a geometry/config change to become true, do not make that
change; instead record it as an open item in `docs/10_USER_INPUT_REQUIRED.md` or `state/ASSUMPTIONS.md`
and say so in the handoff.

## Ground truth already confirmed by the orchestrator (do not re-derive)

- Product: light desktop tower for two Silhouette cutting plotters + horizontal film storage.
  Not the mobile floor stand the original template docs describe.
- `config/parameters.yaml`, `state/PROJECT_STATE.md`, `state/DECISION_LOG.md`,
  `state/ASSUMPTIONS.md`, and `state/REQUIREMENTS_TRACEABILITY.csv` are **already** substantially
  updated for rev6/PLT-007 by the previous implementer cycle. Do not rewrite what is already
  correct — this pass fixes the *remaining* stale statements identified below, plus a few
  narrower staleness items inside those same files that the horizontal-reconfig cycle missed.
- Vertical film storage (10 cells, 59.2 mm width, 6..12 divider range) was **removed**, not kept
  as a parallel/alternate configuration. `src/stand_cad/geometry/dividers.py:1-3` states this
  plainly ("Vertical comb-rail / finger-notch dividers removed; recovery at commit 69b1261.").
  Confirmed by `git log`: commit `69b1261` is the pre-removal recovery point. Every doc statement
  about vertical storage must say "removed, recoverable at commit `69b1261`", not "superseded" in
  a way that implies it still runs, and not silently deleted from history.
- Governing machine: Silhouette Cameo 4, 570 × 195 × 170 mm, 4.7 kg
  (`config/parameters.yaml:36-38,60`, source
  `https://www.silhouette101.com/wp-content/uploads/2020/01/cameo-4-spec-sheet.pdf`). Slot 2:
  Cameo 5, 566 × 176 × 124 mm, 5.1-5.2 kg (`config/parameters.yaml:63-66`, sources
  `https://www.silhouetteeurope.eu/en/silhouette-cameo-5-matte-black` and
  `https://silhouetteamerica.freshdesk.com/support/solutions/articles/35000208584-cameo-machine-measurements`).
- Tier clear height ≥170 mm (`config/parameters.yaml:42`); tier 2 setback 130 mm
  (`config/parameters.yaml:48`, supersedes 150 mm).
- Overall width 650 mm, clear width 610 mm, wall 20 mm, R10 bullnose as a recorded deviation from
  TZ's R20-R30 (`config/parameters.yaml:22,25,27-28`; D-025/D-027 in `state/DECISION_LOG.md`).
- Closed case is storage/transport only: manufacturer needs ~356 mm free material travel front AND
  rear, 907 mm working length vs 550 mm case depth (`config/parameters.yaml:164`; D-028).
- New service port cutout on the right side panel, dimensions `to_measure`, connector undecided
  (`config/parameters.yaml:171-174`).
- Handles centred on the side panel by owner instruction, superseding CoM placement (D-030;
  `config/parameters.yaml:170`).
- Tooling that exists and is under-documented at the top level: `viewer/` (three.js, vendored,
  already has its own thorough `viewer/README.md`), `scripts/serve_viewer.py`, `scripts/doctor.py`,
  `scripts/regenerate.py`, `scripts/generate_model.py`, `scripts/render_validation_views.py`,
  `scripts/generate_mass_report.py`.

## Pass 1 inventory (path:line → what is false/stale → required disposition)

Fix every item below in Pass 2. Do not delete any historical decision; superseded content gets an
explicit "superseded YYYY-MM-DD, see successor" note, not a silent rewrite.

### A. Top-level mission/product framing

1. `README.md:1` — title "AI-first CAD project for a mobile equipment stand". Rewrite to name the
   actual product (light desktop tower for two cutting plotters), keep the "AI-first CAD project"
   framing which is still true of the workflow itself.
2. `README.md:5` — "designing a real mobile stand or enclosure... not a finished stand design".
   Update to the desktop-tower framing; keep the "not yet a finished/released design" caveat
   (still true — G0 unconfirmed, `to_measure` leaves remain).
3. `README.md` — missing a "day-to-day loop" section. Add one covering: regenerate
   (`uv run python scripts/regenerate.py`), serve the viewer with live reload
   (`uv run python scripts/serve_viewer.py --watch`, then open
   `http://127.0.0.1:8000/viewer/index.html`), and run the doctor when something misbehaves
   (`uv run python scripts/doctor.py`). Link to `viewer/README.md` for full detail — do not
   duplicate its content, `viewer/README.md` is already accurate and thorough.
4. `AGENTS.md:7` — Mission line: "parametric, inspectable, prototype-ready mobile equipment
   stand/enclosure". Update the product noun; keep every other word of the mission sentence
   (autonomy/DFM-boundary framing is still correct and this file is a binding governance contract
   — change only the stale noun phrase, nothing about roles/authority/process).
5. `OPUS_5_START_PROMPT.md:7` — "real mobile equipment stand/enclosure". Same fix as AGENTS.md:7.
   This file is a copy-paste start block; keep it internally consistent with AGENTS.md's wording.
6. `pyproject.toml:8` — `description = "AI-first parametric CAD workflow for a mobile equipment
   stand"`. Update the product noun phrase only. This is metadata, not geometry — safe to touch in
   this documentation-only stage.
7. `START_HERE_RU.md` — spot-check only (Russian owner-facing quick start). Its product framing is
   already generic ("стойки/корпуса", not "mobile"), so no false statement was found. Leave as is
   unless you find a specific false claim while implementing; if you do, fix it and note it in the
   handoff. Do not do a wholesale rewrite of this file.

### B. Scope/requirements/plan docs assuming the floor-stand template

8. `docs/02_SCOPE_AND_ASSUMPTIONS.md:5` — Goal: "real mobile stand or enclosure that houses
   selected on-site printing equipment". Update to the desktop-tower/two-plotter framing.
9. `docs/02_SCOPE_AND_ASSUMPTIONS.md:7-15` — candidate equipment list (Bulros heat press, Epson
   printer, DNP/DS-RX1HS photo printer, generic "Silhouette Cameo plotter", laptop, iPad...) is
   the pre-TZ candidate inventory. It is now superseded by the TZ's fixed equipment set (two
   Silhouette Cameo plotters: Cameo 4 governing + Cameo 5 slot 2; no heat press, no photo printer,
   no laptop/iPad enclosed — PLT-013 tests exactly this). Mark this list as the **superseded
   pre-TZ candidate inventory** (dated, cite D-011 as successor decision and the TZ document as
   the fixed equipment source) — do not delete it, frame it as history that explains why the
   later fixed list exists.
10. `docs/04_REQUIREMENTS_CHECKLIST.md:31` — `MEC-003`: casters requirement. The current design has
    no casters (stationary desktop tower with feet, per `materials.foot_height_*` and
    `hardware.foot_diameter_mm`). Do not delete the requirement ID (checklist file header says "Add
    rows rather than renumbering"). Instead annotate it not-applicable to the current
    configuration with the reason (desktop tower, not mobile floor stand) and cite the successor
    concern (feet load path, `MEC-001`/`MEC-004`, `stability.tip_factor_min`) so a reader is not
    left thinking caster verification is a live open requirement.
11. `docs/05_IMPLEMENTATION_PLAN.md:78` — Phase 3 work item: "...panel interfaces, doors, caster
    interfaces, and restraint locations". No doors or casters exist in the actual design (open
    front/organizer top, trays with slide extension instead of doors; feet instead of casters).
    Reconcile the phase content to name what actually exists (tier trays, shelf dividers, side
    panels, handle) **without weakening the gate** — i.e. do not remove the underlying engineering
    concern (stable interfaces, restraint), just stop naming parts that were never built and were
    never going to be built for this product.
12. `docs/05_IMPLEMENTATION_PLAN.md:98,100` — Phase 4 work items: "...handles, casters, latches...",
    "caster capacity, tipping cases". Same fix: drop caster-specific items, keep tipping-case
    evaluation (still a real, live concern — `stability.tip_factor_min`,
    `output/validation/rev6/stability_report.md`), keep handle/latch language only where the
    product actually has an analogous part (handle: yes: `hardware.handle_*`; latch: check whether
    any latch-equivalent exists in `src/stand_cad/geometry/`before keeping the word — if none
    exists, drop it here too and say so).
13. `docs/07_VALIDATION_AND_ACCEPTANCE.md:31` — "required service/door/removal paths clear". No
    doors exist; the analogous real requirement is tray/shelf service access and the organizer's
    open top/front. Reword to match what is actually built, without weakening the acceptance
    criterion itself.
14. `docs/07_VALIDATION_AND_ACCEPTANCE.md:43` — "caster static/dynamic capacity and mounting load
    distribution" under Mechanical acceptance. No casters exist. Replace with the actual
    load-bearing item for this product (foot/vibration-mount load distribution,
    `hardware.foot_diameter_mm`, `materials.foot_height_*`) so the acceptance criterion still
    covers a real load path, just the correct one.
15. `docs/08_RISK_REGISTER.md:7` — `R-003`: "Under-rated casters or mounting". Do not delete the
    risk row (this is a register, keep IDs stable like the requirements checklist). Annotate: the
    caster half of this risk is not applicable to the current stationary desktop-tower
    configuration; the "mounting" half remains live (foot/vibration-mount load path,
    `hardware.foot_diameter_mm`). State this explicitly rather than leaving "casters" reading as a
    live open risk on a product that will never have casters.
16. `docs/12_PRODUCTION_RFQ_TEMPLATE.md:3,7` — Subject and project summary: "mobile equipment stand
    prototype", "mobile equipment stand/enclosure for event operation and transport". This is a
    template an RFQ would actually be drafted from — update the product description to the light
    desktop tower for two cutting plotters (still used for event transport/operation per the TZ's
    own "мероприятия" framing — do not drop the "event transport" concept, it is TZ-confirmed, only
    fix "mobile equipment stand" → the actual product name/description).
17. `docs/12_PRODUCTION_RFQ_TEMPLATE.md:29` — Question 7: "...casters, welds, and fasteners
    feasible and accessible?" Drop "casters" (none exist), keep the rest of the question — it is a
    generic per-hardware-class DFM question and every other item in it is real
    (inserts/hinges/latches — recheck latches per finding 12 — /handles/welds/fasteners).

### C. `state/ASSUMPTIONS.md` — stale statuses and one broken parameter-path reference

18. `state/ASSUMPTIONS.md` row `A-001` — "Windows 11 native is available", status `Open`. This has
    been repeatedly confirmed true across every rev1-rev6 cycle (`scripts/setup_windows.ps1` exit 0
    each time per `state/PROJECT_STATE.md`). Close it, citing the repeated successful runs.
19. `state/ASSUMPTIONS.md` row `A-003` — "The stand is intended for event transport and operation",
    status `Open`, "Validation action: User confirms workflow". This predates the TZ. The TZ
    (`ИИ советы/Cursor_Opus5_TZ_Light_Plotter_Tower.md:13,23`) explicitly answers this ("лёгкого
    настольного корпуса **для мероприятий**", "пригодным для перевозки на мероприятия") and D-011
    adopted the TZ as authoritative. Close this assumption, citing the TZ lines and D-011.
20. `state/ASSUMPTIONS.md` row `A-004` — "Existing yellow/black and orange/grey concepts are
    appearance references only", status `Open`. This predates the TZ, which fixes the appearance
    (white modern exterior, opal PMMA, RGBW backlight — TZ lines ~21, 219, 227-256) and which is
    already implemented (`PANEL-CLAD-FRONT-*`, D-026; `LIGHT-STRIP-001`, PLT-014). Close it, citing
    the TZ lines and the implementing decisions.
21. `state/ASSUMPTIONS.md` row `A-008` — text says "until measured on a real Cameo 5" and "Measure
    on two real units per TZ section 16 item 1". The governing machine is now Cameo 4, not Cameo 5
    (PLT-007). Update the wording to name both machines (Cameo 4 governing, Cameo 5 slot 2) so a
    reader does not think only the Cameo 5 needs this measurement.
22. `state/ASSUMPTIONS.md` row `A-009` — references `film_storage.min_stack_width_mm`. That leaf no
    longer exists; the horizontal-storage parameter is `film_storage_horizontal.min_stack_height_mm`
    (`config/parameters.yaml:95`). This is a broken/stale path reference, not just wording — fix
    the exact leaf name and re-check the impact statement still makes sense for horizontal shelves
    (stack height per shelf, not cell width).
23. `state/ASSUMPTIONS.md` row `A-012` — "uses rail-to-rail span `plotter.physical_width` (566
    mm)". Since Cameo 4 (570 mm) now governs `plotter.physical_width`
    (`config/parameters.yaml:36`), the span basis is 570 mm, not 566 mm — verify the exact current
    value against `src/stand_cad/geometry/analysis.py::indicative_tray_deflection_mm` (reads
    `plotter.physical_width` for span, `plotter.physical_depth` for load-distribution width) and
    against the actual number in `output/validation/rev6/deflection_report.md`, then correct the
    text. Also check `state/REQUIREMENTS_TRACEABILITY.csv` row `PLT-011`'s notes column, which
    currently says "Cameo 4 depth 195 mm span" — reconcile which dimension is actually the
    span in the code (`physical_width`) vs the load-distribution width (`physical_depth`) and make
    both A-012 and the PLT-011 notes state the same, correct, code-verified numbers. Also update
    `docs/10_USER_INPUT_REQUIRED.md` section C, which currently repeats the stale "span 566 mm".

### D. Cross-check before writing (do this, not optional)

- For every numeric claim you correct, verify it against the current `config/parameters.yaml`
  value or the current test/report file it cites — do not just swap 566→570 by pattern-matching
  the finding text; confirm against `src/stand_cad/geometry/analysis.py` and the actual
  `output/validation/rev6/deflection_report.md` number.
- Re-check finding 12's "latches" claim against `src/stand_cad/geometry/` before keeping or
  dropping the word.
- `state/REQUIREMENTS_TRACEABILITY.csv` PLT-001..020 rows already look substantially correct for
  rev6 (verified by the orchestrator read). Do not rewrite rows that are already accurate. Only
  touch rows connected to a finding above (PLT-011 notes per finding 23) or where you find, during
  implementation, a row claiming a requirement is satisfied without matching evidence — if you
  find one, treat it as a new finding, fix it, and report it as such (do not silently skip past
  it or silently "fix" it without recording that you found it).
- If, while fixing any of the above, you discover the row/table needs a **new** requirement row
  because the horizontal reconfiguration created a requirement with no existing ID (the contract
  from Main specifically flags this possibility) — add it with the next free `PLT-0NN` ID, proper
  source citation, and status. Do not silently skip this if you find a gap; report what you added.

## Pass 2 — correction rules (binding)

- Never delete history. A superseded decision/assumption/requirement gets marked superseded with
  its date and successor citation, not erased or silently rewritten as if it was always this way.
- Keep every requirement ID and risk ID stable (`MEC-003`, `R-003`, etc.) — annotate
  not-applicable-to-current-configuration, do not renumber or delete.
- `docs/10_USER_INPUT_REQUIRED.md` must, after your edits, list exactly what is still genuinely
  open: the outstanding physical measurements (section A's numbered list), the USB connector type
  and its panel cutout, the tray-deflection engineering miss (section C), and anything else you
  find truly unresolved while implementing findings 1-23. Do not add anything the owner has
  already answered (Cameo 4 dimensions, governing machine, tier setback, handle placement, R10
  bullnose deviation — all already closed in this file, leave those sections as-is unless you find
  a specific new falsehood in them).
- `state/PROJECT_STATE.md` must, after your edits, let a stranger understand in one read: what the
  product is, the current revision (rev6), what/where the artifacts are
  (`output/concept/`, `output/validation/rev6/`), what passes (126 pytest, ruff clean,
  `setup_windows.ps1` exit 0 — re-verify these counts against your own Pass 2/3 command runs and
  correct the number in this file if the count changed), what is open, and the next step. It is
  already close to this bar — add a one-line pointer to `viewer/README.md` for how to look at the
  model, and correct anything you find stale while cross-checking it against your other edits (for
  example, if any A-0xx/PLT-0xx ID it references changes status in this pass).
- No geometry changes. No PDF or production DXF. No gate marked passed. Nothing production-ready.
  No `git push`; local commits expected.

## Pass 3 — verify against this inventory, then adversarial review

Re-walk findings 1-23 item by item and confirm each is resolved (quote the corrected line back in
your own verification note). Then the mandatory `adversarial-reviewer` must specifically hunt for:

- a surviving false statement anywhere touched by this pass (or anywhere in the files listed in
  Main's Pass 1 scope: `README.md`, `AGENTS.md`, `OPUS_5_START_PROMPT.md`, everything under
  `docs/`, all ADRs, everything under `state/`);
- a requirement marked satisfied (`DEVIATED`/`IN_PROGRESS`/closed assumption) without a matching
  evidence citation that actually exists at the cited path;
- a gate (`G0`-`G8`) implied as passed anywhere — none may be;
- any place a `to_measure`/`TO_MEASURE` value is described as if it were verified/measured.

Fix and re-verify. Cap 3 cycles total for this whole DOC-001 task, not per finding. Third cycle
closes blockers only.

## Verification commands (must all exit 0)

```powershell
uv run pytest
uv run ruff check .
powershell -ExecutionPolicy Bypass -File .\scripts\setup_windows.ps1
```

Expect `uv run pytest` to report 126 tests passing (no test file is touched in this stage — if the
count differs, that is itself a finding to report, not to silently paper over).

## Forbidden (restated from Main's contract)

No geometry changes. No PDF or production DXF. No gate marked passed, nothing production-ready. No
`git push`; local commits expected.

## Report to Main (450 words max, per Main's contract)

The pass 1 inventory size, the files corrected, the specific false statements that were most
misleading, the traceability changes, what remains genuinely open, the commit SHA, command exit
codes, and reviewer findings.
