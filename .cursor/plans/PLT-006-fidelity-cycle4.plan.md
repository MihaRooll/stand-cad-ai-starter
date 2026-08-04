# Plan: PLT-006 — fidelity cycle 4 (frame concealment, slab radius arithmetic, CoM-based handle, top-edge review)

Tier: **T2** (Main's explicit ruling, same as PLT-005). Mandatory `adversarial-reviewer`, **no**
`principal-arbiter`. Sole writer: `implementer` (composer-2.5-fast), same agent that closed
PLT-005 rework cycle 1 — resume it, do not start a second writer. Review/verify on
`cursor-grok-4.5-high-fast`. Cap 3 internal review/verify cycles; cycle 3 is blocker-only.

Baseline (Main-confirmed after PLT-005 rework cycle 1, do not regress): `uv run pytest` passes 127
tests; `uv run ruff check .` clean; `setup_windows.ps1` exits 0; rev4 renders regenerated with
grey backgrounds, visible handle void, visible dark feet, `rear_vent_closeup.png`, and
`organizer_closeup.png` restored to 10 bands. This cycle's commit (separate from PLT-005's) covers
this cycle's own delta only — do not re-describe PLT-005 work in the cycle-4 commit message.

## 0. Orchestrator-established facts (established by direct computation on the live source —
re-verify by render/test, do not re-derive from scratch)

### Owner decision, 2026-08-04 (final — supersedes "Main's ruling" below as the authoritative record)

Main presented the owner with the three options implied by the arithmetic. The owner's decision:

- **Accepts R10 with the overall width held at 650 mm.**
- **Explicitly rejected** shrinking the clear width to ~570 mm (the branch that would reach R20 at
  650 mm overall): 570 mm is narrower than the 580 mm protective plotter envelope
  (`plotter.design_width`) and would leave only ~2 mm per side clearance where TZ line 89 requires
  22 mm.
- **Declined** growing the overall width to 690 mm (to reach R20 while keeping 610 mm clear) and
  declined a cosmetic overhang/non-structural visual radius trick.

This is now a **recorded owner decision**, not a pending agent-side ruling awaiting input — write the
records that way: `state/DECISION_LOG.md` gets a decision entry dated **2026-08-04** with the
arithmetic (`(650-610)/2=20mm` per slab → max edge radius 10mm; R20 would require 40mm/slab, forcing
either 690mm overall or ~570mm clear) **and** the reason the 570mm branch was rejected (580mm
protective envelope vs TZ line 89's 22mm clearance requirement — 570mm leaves only ~2mm). The
`state/REQUIREMENTS_TRACEABILITY.csv` row tracing to TZ line 230 stays **DEVIATED** (R10 is not
R20-R30 — do not mark it satisfied), but its note now reads as **owner-accepted**, not
pending-owner-input. If the implementer already wrote these two records framed as "agent ruling,
pending owner" (per the original cycle-4 instructions, written before this decision arrived), amend
the wording in place rather than duplicating a second entry — one decision-log row and one
traceability note for this item, reflecting the final accepted state.

### Main's ruling (binding, supersedes the open-ended analysis below) — R10 bullnose, no principal-arbiter

Main independently confirmed the arithmetic and ruled directly (do not escalate, do not wait for the
owner):

1. **Implement a full R10 bullnose** on the front vertical edges of both side slabs, **continued along
   the top edge** where the same 20 mm-thickness limit applies. Do not shave the 650 mm overall width
   or the 610 mm clear width to buy a bigger radius.
2. **Record the conflict as a deviation, not a pass:** the row tracing to TZ line 230 (R20-R30 outer
   corner) in `state/REQUIREMENTS_TRACEABILITY.csv` must be marked **DEVIATED** (new row if none
   exists yet — check first) with the arithmetic in the notes; `state/DECISION_LOG.md` gets the same
   arithmetic; `state/ASSUMPTIONS.md` gets an entry only if a new assumption is introduced by the
   bullnose implementation itself (e.g. how the top-edge continuation is constructed).
3. **Do not raise this to `principal-arbiter`.** Main will present the owner with three options
   (accept R10 / grow overall width past 650 / shrink clear width below 610) — none of them blocks
   the rest of this cycle.

The below section's original open-ended "single-corner fillet ~19.9mm" analysis is **superseded** —
implement R10 bullnose per the ruling instead, not the ~19.9mm single-corner variant.

### Item 2 (side-slab radius) — superseded by Main's ruling above; kept for arithmetic record only

`case.width`=650 mm and `case.internal_width`=610 mm are both `provenance: verified` (TZ section 4,
fixed). `side_clear = (650-610)/2 = 20.000 mm` **exactly, with zero slack** — there is no margin to
give up anywhere in this formula; both terms are protected fixed dimensions.

`_extrude_side_slab` currently fillets **both** front-face vertices of the panel's thin cross-section
(`Rectangle(side_clear, depth)` in the XY sketch, filleting the two vertices at `Y≈0`: `(0,0)` — the
true **exterior** case corner — and `(side_clear,0)` — the **interior** corner where the panel meets
the organizer, which is not visible in the reference and does not need rounding). Filleting *both*
simultaneously requires `2R ≤ side_clear`, capping `R ≤ ~9.9 mm` (the ceiling already reported in
`docs/10_USER_INPUT_REQUIRED.md` §D from PLT-005).

**A design correction, not just a bigger number:** if only the single exterior vertex `(0,0)` (for the
left panel; `(side_clear, 0)`→ mirrored for the right panel's true exterior corner) is filleted, the
constraint relaxes to `R ≤ side_clear - ε` ≈ **19.9 mm** — the low end of TZ's own R20-R30 band,
reachable with **zero change** to `side_clear`/`internal_width`. Verify this is geometrically valid
(the fillet arc must stay tangent within the rectangle and not cross the un-filleted interior corner —
check with `build123d` before committing to it) and implement it if valid; state the achieved value.

**Anything above ≈19.9-20 mm requires widening `side_clear`, which is arithmetically impossible without
violating the fixed `case.internal_width ≥ 610 mm`:**

| Target R | Required `side_clear` (`≥2R+0.2` two-corner, or `≥R+0.1` single-corner) | Resulting `internal_width` (`650-2·side_clear`) | Shortfall vs fixed 610 mm minimum |
|---|---|---|---|
| 20 mm (single-corner) | 20.1 mm | 609.8 mm | 0.2 mm |
| 25 mm (single-corner) | 25.1 mm | 599.8 mm | **10.2 mm** |
| 30 mm (single-corner) | 30.1 mm | 589.8 mm | **20.2 mm** |

This is a genuine conflict **inside the TZ itself**: TZ section 8 line 230 (R20-R30 outer corner) and
TZ section 4 (`internal_width ≥ 610 mm`) cannot both hold simultaneously once `case.width=650 mm` is
also fixed. **Do not resolve this by quietly shrinking `internal_width` or the radius target.**
Implement the single-corner fillet (~19.9 mm, effectively meeting the R20 floor within the existing
budget) as the improvement that *is* available, and record the R25/R30-vs-610mm-internal-width
conflict in `docs/10_USER_INPUT_REQUIRED.md` as a TZ-internal conflict requiring an owner decision
(which fixed number yields), with the exact table above. This satisfies Main's "stop and report the
conflict with numbers rather than shaving the radius silently" instruction.

### Item 3 (handle Z from centre of mass) — CLOSED by Main's ruling: keep Z=214, do not move it

Main has ruled this item **dropped**, correcting the original cycle-4 request: Z=214 is within ~4 mm
of the computed CoM z=217.3 mm, which **is** what TZ line 235 asks for (centre-of-mass placement),
so the original "handle sits too low vs the reference photo" framing was wrong — the reference
picture is not the criterion here, the computed CoM is, and the current position already satisfies
it. **Do not reposition the handle.** Still do the small, low-risk parts of the original analysis:

Live mass report (`uv run python scripts/generate_mass_report.py`, current source, PLT-005 rework
cycle 1 state) gives centre of mass **z = 217.3 mm** for "case + 2 plotters" (the representative
transport-loaded condition; "lower tray extended + 2 plotters" agrees at the same z). The current
handle mount (`hardware.handle_mount_z_mm = 400` **must first be re-read from live config — PLT-005
rework cycle 1's handoff already moved it to `Y=100/Z=214`**, i.e. footprint centre Z≈214 mm) is
**already within ~3 mm of the computed CoM**. Do not move it further by eye or to chase the reference
photo's "high on the panel" look — Main's own instruction is to use the computed CoM, not the
picture. Re-run the mass report against the *current* live parameters (not the stale `rev3`-labelled
output — see the small fix below), confirm the ~3 mm agreement holds, and rewrite
`hardware.handle_mount_z_mm`'s note in `config/parameters.yaml` to cite the mass-report CoM
explicitly (formula + resulting z) as the basis, replacing the current "clear of dividers" framing
with "clear of dividers AND matches computed CoM z=XXX.X mm (± tolerance)". If re-running shows a
materially different CoM (e.g. because this cycle's frame/slab changes shift mass), use the new
number and state the delta from 214 mm.

**Small fix while in this file:** `scripts/generate_mass_report.py`'s `DEFAULT_OUTPUT`/
`DEFAULT_VALIDATION_DIR` are hardcoded to `output/validation/rev3/...` (predates the rev4 revision
bump). Point it at the live `CONCEPT_REVISION` (same pattern already used in
`render_validation_views.py`'s `DEFAULT_OUTPUT_DIR`) so the mass/stability/deflection reports land
under `output/validation/rev{CONCEPT_REVISION}/` and their in-file `# PLT-004 revN` headers match.

### Item 4 (top-front member identity) — investigate before changing; it is likely **not** the retainer

Two candidate parts render with warm colours near the top of the case:

- `RETAINER-001` (`src/stand_cad/geometry/dividers.py`) — material `transparent_petg_2mm`, RGB
  `(120,185,235)` (**blue**, same as the dividers) — positioned at the organizer's front, top ≈ the
  divider top (`z_base+front_retainer_height_mm`, roughly organizer-floor-top height, not the case's
  outer top).
- `LIGHT-STRIP-001` (`src/stand_cad/geometry/services.py`) — material `service_volume`, RGB
  `(240,190,110)` (**orange/tan** — this matches the "yellow member" Main is describing) —
  positioned at `top_z` (the case's actual structural top) and near the **rear** (`depth - gap -
  ls_w - outer_t` .. `depth - gap - outer_t`, i.e. Y close to `depth`, not Y≈0/front).

The colour match strongly suggests the visible warm bar is **`LIGHT-STRIP-001`**, not the retainer,
and it sits near the case's rear-top rather than literally "front" — the front-dominant organizer
camera and the iso camera can both make a rear-top element read as if it's at the front of the visual
top edge. **Confirm by isolating just `RETAINER-001` and just `LIGHT-STRIP-001` in a throwaway
render** (or by printing both parts' bounding boxes from `datums`/the transport registry) before
deciding what "reconsider its cross-section" means. `LIGHT-STRIP-001` and `RETAINER-001` are both
`verify_on_real_machine=True`/provisional — if the visible member is confirmed to be `LIGHT-STRIP-001`,
it is a service-volume placeholder, not the TZ line 158 retainer, and TZ line 158's 40-50 mm
removable-retainer requirement is satisfied by `RETAINER-001` regardless of what happens to
`LIGHT-STRIP-001`'s cross-section. State the confirmed identity plainly in the handoff — do not guess.

### Item 1 (frame concealment) — design task, no shortcut available; give the implementer the part
inventory, not a prescribed fix

Exposed structural parts at the open front / around the organizer, confirmed present in the transport
registry: `FRAME-POST-FL/FR/RL/RR-001` (posts, `frame.py`), `FRAME-RAIL-BASE/TOP/ORG-*`
(perimeter rails at three Z levels, `frame.py`), all material `aluminium_angle_15x15x1.5`
(RGB `(175,178,188)` — the grey seen in every render). TZ line 231 asks for minimum visible
joints/screws. The case is deliberately open at the front (media access) and open at the top
(organizer access, per PLT-004's `TOP-STRUCTURE-001` removal) — some frame visibility at those two
openings may be structurally unavoidable without adding cladding that TZ does not otherwise call for.
This is a genuine design trade-off, not a one-line fix: the implementer should choose and justify one
of (a) recess the frame further inward so panel/shelf edges naturally occlude it from the front/iso
viewing angles used in the evidence renders, (b) add a thin trim/cladding strip over the specific
exposed rail segments (new provenance-tagged part, materials already in the palette), or (c) confirm a
subset of exposure is structurally unavoidable at the open front/top and document exactly which rails
remain visible and why, rather than claiming full concealment that isn't real. Whatever is chosen,
re-render `transport_iso.png`/`transport_front.png`/`organizer_closeup.png` and confirm by direct
visual read whether the grey aluminium footprint on-screen is materially reduced versus this cycle's
starting point (a before/after description with rough screen-area or part-visibility comparison is
acceptable evidence — an exact pixel percentage is not required).

## Task Contract

```yaml
contract_id: PLT-006-fidelity-cycle4
tier: T2
goal: >
  Highest priority: conceal the visible structural frame (Item 1) — the single biggest visual gap
  vs the reference. Implement Main's binding ruling on the corner radius (R10 bullnose on front
  vertical edges AND the top edge, recorded as a DEVIATED requirement against TZ line 230, no
  principal-arbiter escalation). Item 3 (handle Z) is CLOSED/dropped by Main's ruling — keep Z=214,
  document the CoM basis, do not move it. Item 4 (top member identity) must be demonstrated by an
  isolated render, not asserted. No fixed TZ dimension moves.
acceptance_criteria:
  - id: AC-C1
    text: >
      HIGHEST PRIORITY. Item 1 (frame concealment): implementer picks and justifies one approach
      (recess / cladding / documented-unavoidable-subset) for FRAME-POST-*/FRAME-RAIL-*-* visibility
      at the open front and open top; regenerates transport_iso.png, transport_front.png,
      organizer_closeup.png; states in the handoff, with reference to the specific renders,
      whether/how much grey aluminium exposure was reduced. If a subset remains visibly exposed and
      is judged structurally unavoidable, that subset is named explicitly (part IDs) rather than
      glossed over. Give this the most implementation attention/iteration of the four items.
  - id: AC-C2
    text: >
      Item 2 (slab radius) — Main's binding ruling, not open for reinterpretation: implement a full
      R10 bullnose on the front vertical edges of both side slabs, continued along the top edge
      (same 20mm-thickness ceiling applies there too). case.width (650) and case.internal_width
      (610) are NOT changed. Add or update the traceability row tracing to TZ line 230 (R20-R30
      outer corner) in state/REQUIREMENTS_TRACEABILITY.csv with status DEVIATED and the arithmetic
      in notes: side_clear=(650-610)/2=20mm exactly (zero slack); max radius before the edge becomes
      a full bullnose is side_clear/2=10mm; TZ line 230 asks for R20-R30, which cannot hold
      simultaneously with TZ's own 610mm clear-width floor once 650mm overall is fixed. Same
      arithmetic goes into state/DECISION_LOG.md. Do NOT escalate to principal-arbiter — Main has
      ruled; do not raise it again this cycle. If the bullnose implementation itself introduces a
      new assumption (e.g. how the top-edge continuation is constructed/joined), add one
      state/ASSUMPTIONS.md entry — otherwise skip that file.
  - id: AC-C3
    text: >
      Item 3 (handle Z) — CLOSED by Main's ruling: do NOT reposition hardware.handle_mount_y_mm/
      handle_mount_z_mm (stay at Y=100/Z=214). Fix scripts/generate_mass_report.py's hardcoded
      rev3 path to use CONCEPT_REVISION (small, while-in-file fix), re-run it against live source,
      and rewrite handle_mount_z_mm's config/parameters.yaml note to cite the mass-report CoM z
      value explicitly as the basis (e.g. "matches computed CoM z=217.3mm (case+2 plotters,
      scripts/generate_mass_report.py) within ~3mm — TZ line 235") replacing the current framing.
      Confirm in the handoff that this closes/drops the "handle sits too low" framing from the
      original cycle-4 request, per Main's explicit correction.
  - id: AC-C4
    text: >
      Item 4 (top member identity) — must be demonstrated, not asserted: render (or otherwise
      geometrically confirm, e.g. isolated bounding-box printout backed by a render check) whether
      the warm-coloured member visible in organizer_loaded_iso.png/transport_iso.png is
      RETAINER-001 or LIGHT-STRIP-001. State the confirmed identity plainly with the evidence used.
      If it is LIGHT-STRIP-001 (service_volume, provisional), say so and leave RETAINER-001 (TZ
      line 158, 40-50mm removable retainer) untouched/unresolved this cycle — no cross-section
      change is required by this finding once the identity is confirmed as LIGHT-STRIP-001.
  - id: AC-C5
    text: >
      No fixed TZ dimension moves: case.width/depth/height (650x550x690), case.internal_width (610),
      plotter coordinates, the 150mm setback, organizer clear volume ≥610x510x325, media path
      clearances. Every new/changed numeric value has a provenance tag and a note citing its TZ line
      or derivation formula in config/parameters.yaml.
  - id: AC-C6
    text: >
      All 127 tests keep passing (or are deliberately, individually updated with a stated reason);
      new tests cover the R10 bullnose's achieved radius (front + top edge) and any new/changed part
      (e.g. a cladding part if added for AC-C1). uv run pytest exits 0; uv run ruff check . exits 0;
      full setup_windows.ps1 exits 0.
  - id: AC-C7
    text: >
      A new revision is generated (rev5) with the full view set (10 PNG + 5 SVG + organizer_closeup +
      base_plate_closeup + rear_vent_closeup) under output/validation/rev5/views/, and
      output/concept/*_rev5.*; rev1-rev4 untouched. state/PROJECT_STATE.md, state/DECISION_LOG.md,
      state/REQUIREMENTS_TRACEABILITY.csv, docs/10_USER_INPUT_REQUIRED.md updated (the last one gets
      the R10-vs-R20-R30 owner-decision note: accept R10 / grow overall width past 650 / shrink clear
      width below 610 — Main will present these three options to the owner).
owned_files:
  - src/stand_cad/geometry/panels.py
  - src/stand_cad/geometry/frame.py
  - src/stand_cad/geometry/services.py
  - src/stand_cad/geometry/dividers.py
  - src/stand_cad/geometry/assembly.py
  - src/stand_cad/geometry/collision.py
  - scripts/render_validation_views.py
  - scripts/generate_mass_report.py
  - config/parameters.yaml
  - tests/test_geometry.py
  - state/PROJECT_STATE.md
  - state/DECISION_LOG.md
  - state/REQUIREMENTS_TRACEABILITY.csv
  - state/ASSUMPTIONS.md
  - docs/10_USER_INPUT_REQUIRED.md
  - output/validation/rev5/**
  - output/concept/*_rev5.*
verify_commands:
  - uv run pytest
  - uv run ruff check .
  - powershell -ExecutionPolicy Bypass -File .\scripts\setup_windows.ps1
forbidden:
  - No change to case.width/depth/height/internal_width, plotter coordinates, 150mm setback,
    organizer clear volume, cell formula, tray extensions, feed-plane provisional values.
  - Do not widen side_clear/shrink internal_width to reach R20-R30 — Main ruled R10 bullnose;
    record the conflict as DEVIATED, do not silently resolve it (Item 2).
  - Do not raise Item 2 to principal-arbiter this cycle — Main has ruled directly.
  - Do not reposition hardware.handle_mount_y_mm/handle_mount_z_mm — Main closed Item 3 at Z=214.
  - Do not touch output/validation/rev1|2|3|4/** or output/concept/*_rev1..4.* — reproducible
    "before" evidence.
  - No PDF/DXF, no gate marked passed, no git push.
```

## Review focus for the mandatory adversarial pass

Look at the regenerated PNGs, not just the diff:
(a) is grey aluminium exposure at the front/top visibly reduced in `transport_iso.png`/
`transport_front.png`/`organizer_closeup.png`, or is the "unavoidable subset" honestly named? (this
is the highest-priority item — give it the most scrutiny)
(b) is the R10 bullnose actually applied to both the front vertical edges AND the top edge (check the
achieved-radius helper/test); is the TZ line 230 row in `state/REQUIREMENTS_TRACEABILITY.csv` marked
`DEVIATED` with the arithmetic, not silently marked done or silently dropped; was
`principal-arbiter` NOT invoked for this (it shouldn't have been)?
(c) is `hardware.handle_mount_y_mm`/`handle_mount_z_mm` genuinely unchanged from Y=100/Z=214, with
`config/parameters.yaml`'s note now citing the mass-report CoM number?
(d) is the warm top member's identity (RETAINER-001 vs LIGHT-STRIP-001) demonstrated by a render or
bbox check, not asserted?
(e) no fixed TZ dimension moved; every new value provenance-tagged.

## Verification commands

- `uv run pytest`
- `uv run ruff check .`
- `powershell -ExecutionPolicy Bypass -File .\scripts\setup_windows.ps1`

All three must exit 0 for `verdict: pass`.
