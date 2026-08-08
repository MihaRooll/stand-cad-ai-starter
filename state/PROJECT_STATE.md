# Project state

> **Living status:** `state/AUTONOMOUS_STATUS.md` — last closed defect, backlog, anti-false-conclusion notes. Prefer it over mid-file historical narrative for “what next.”
>
> **FIX-COLL-010 / D-095 (2026-08-08, cycle 1 pending review):** COVER-SVC↔PANEL ceiling **10000 mm³** (live max **7901.25 mm³** BOTTOM/IN-REAR, **1048.99 mm³** OUT-REAR); `MATING_PAIRS` + share_face paths volume-gated. Residual COVER↔POST/BASE-REAR, INTERLOCK/MAINS/SOFT P2. **No** G0–G8 pass.
>
> **FIX-COLL-009 / D-094 (2026-08-08, cycle 1 closed):** TRAY-rail↔PANEL-IN penetrating ceiling **15000 mm³** (live max **10237.5 mm³**); TRAY excluded from `PANEL-IN-`/`FRAME-` share_face bypass (union with ORG∪POST); volumetric + coplanar burial regressions. ORG/MID/POST/OPEN_FRONT unchanged. Residual INTERLOCK/MAINS/COVER/SOFT P2. **No** G0–G8 pass.
>
> **FIX-COLL-008 / D-093 (2026-08-08, cycle 1 closed):** POST↔PANEL-IN penetrating ceiling **25000 mm³** (live max **18652.9 mm³**); POST excluded from `PANEL-IN-`/`FRAME-` share_face bypass (union with ORG); volumetric + coplanar burial regressions. ORG/MID/OPEN_FRONT unchanged. **No** G0–G8 pass.
>
> **FIX-COLL-007 / D-092 (2026-08-08, cycle 2 closed):** Per-class penetrating ceilings ORG-REAR + MID↔UPPER (**35000 mm³**); ORG-REAR excluded from `PANEL-IN-`/`FRAME-` share_face bypass; coplanar-face burial regression. Adversarial cycle 2 **accept**; Quick **413 passed**, 1 xfailed + ruff 0. Residual penetrating P2 noted. **No** G0–G8 pass.
>
> **FIX-COLL-006 / D-091 (2026-08-08):** Volume-gate eight VIBMOUNT-P* ↔ EQUIP-PLOTTER* pairs on `MATING_PAIRS` via `VIB_EQUIP_MAX_BEARING_MM3=2500.0` (live exactly **2000 mm³** pad embed; hygiene ceiling, not beyond-pad burial fix). Other uncapped `MATING_PAIRS` remain residual P2. Quick 408 passed, 1 xfailed + ruff 0. **No** G0–G8 pass.
>
> **FIX-DOC-007 / D-090 (2026-08-08):** README + docs/12 + HANDOFF + CSV sole-current advertising synced post D-089 — envelope **540 mm**, mass **9.651/13.445 kg**, tip lower **3.828**; HANDOFF no longer claims PLT-012 PASSING. §F/§M/§N/§A remain OPEN. **No** G0–G8 pass.
>
> **FIX-COLL-005 / D-089 (2026-08-08, cycle 2):** Path A slide below tray; `TRAY_SLIDE_MAX_BEARING_MM3=500.0`; live max **0 mm³**. Open-door BASE-FRONT/BOTTOM clearance notches (removed 26k allowlist). Full +11 mm stack → **540 mm** envelope. **No** G0–G8 pass.
>
> **FIX-DOC-005 / D-088 (2026-08-08):** `docs/12_PRODUCTION_RFQ_TEMPLATE.md` §F/§M owner-blocker rows synced to sole-current — tier-2 intrusion ≈1,515,402 mm³ at Y=180.6; §M transport headroom 27/50 mm vs 80 mm (not 210,600 mm³ lid/shuttle). Regression pin in `tests/test_concept_revision_docs.py`. §F/§M/§N/§A remain OPEN. **No** G0–G8 pass.
>
> **FIX-COLL-004 / D-087 (2026-08-08):** Volume-gate eight EQUIP-PLOTTER* ↔ TRAY-* / SLIDE-* seating pairs on `MATING_PAIRS` via `EQUIP_SEATING_MAX_BEARING_MM3=500.0` (live max **0 mm³**). Other `MATING_PAIRS` uncapped — residual P2. **No** G0–G8 pass.
>
> **FIX-COLL-003 / D-086 (2026-08-08):** Deleted blanket kinematic-group `is_mating` exemption; residual eight SLIDE↔VIBMOUNT plane-touch pairs gated by `SLIDE_VIBMOUNT_MAX_BEARING_MM3=500.0` (live max **0 mm³**). EQUIP↔SOFTSTOP not on `MATING_PAIRS`; live clr=0.5 mm. **No** G0–G8 pass.
>
> **FIX-COLL-002 / D-084 (2026-08-08):** Path A retracts `PANEL-IN-MID-001` front Y to closed-door plane (15.0 mm); caps `is_door_mate` MID/SOFTSTOP with `DOOR_FRONT_PLANE_MAX_BEARING_MM3`. Live DOOR-LOWER↔MID **5985 → 0 mm³**; handle Y **179.8 → 180.6 mm** (F-4 doc sync). **No** G0–G8 pass.
>
> **FIX-DOC-003 / D-083 (2026-08-08):** `docs/10_USER_INPUT_REQUIRED.md` §E/§F/§H intrusion + MAINS-INLET wording and `state/REQUIREMENTS_TRACEABILITY.csv` current-evidence pointers synced to rev15 / Y=179.8 / REL-027=55. §F/§M/§N/§A remain OPEN. **No** G0–G8 pass.
>
> **FIX-DOC-002 / D-082 (2026-08-08):** `HANDOFF_PROMPT.md` product-truth / startup / Immediate mission refreshed to rev15 + D-075…D-081 live numbers; test pins current zones only. **No** G0–G8 pass.
>
> **FIX-COLL-001-open-front-ceiling / D-080 (2026-08-08):** `OPEN_FRONT_MAX_BEARING_MM3=750.0` gates `is_open_front_kinematic_contact` and four front clad/rail penetrating patterns (live max **540 mm³**). P2 door MID/SOFTSTOP backlog **closed in FIX-COLL-002 (D-084)**. **No** G0–G8 pass.
>
> **FIX-MASS-001 / D-078 (2026-08-08):** Mass-report header lists excluded categories from live transport only; no longer claims removed `MAINS-INLET` / `INTERLOCK` / `EDGEGUARD` are physically present. PLT-012 / G4 **not** passed.
>
> **FIX-TIP-001 / D-077 (2026-08-08):** Upper tip-factor at `upper_extension=0` is **N/A** (`applicable=False`); report no longer prints `inf (minimum 1.5)`. Lower@250 indicative factor remains finite (~3.828 post D-089). PLT-010 / G4 **not** passed.
>
> **FIX-WAVE-004 (2026-08-07):** Corner posts restored (D-075); upper tray fixed / lower door-tray choreography (D-076, **owner-confirmed 2026-08-07** — "Да, все верно"). **`CONCEPT_REVISION`=15**. Door↔slide clearance resolved at sampled lower extensions 0/130/180/250 mm. **No G0–G8 gate passed.**
>
> **FIX-WAVE-002 / D-057 closed (2026-08-06):** All 8 unexpected D-056 pytest regressions are closed. Adversarial-reviewer cycle 2 on the collision-exemption predicate (**Y-gate** `collision.py:316-328`, solid-fill **≈428×10³ mm³** oracle) → **APPROVED**. Full profile (2026-08-06): `uv run ruff check .` clean; `uv run pytest -q --tb=line` → **365 passed, 1 failed** (sole permitted failure: `test_lid_envelope_no_intersection_in_service_states`, **210 600 mm³** lid/shuttle overlap); `powershell -ExecutionPolicy Bypass -File .\scripts\setup_windows.ps1` exit **0**. Rev12 evidence current via `scripts/regenerate.py`. Optional non-blocking nit: F-3 rail `max_bearing` full-panel Z scope. Full suite wall time **~8 min** (performance item, non-blocking).

- Project: Light desktop tower for two Silhouette plotters plus horizontal film storage, **650 × 420 × 540 mm** (D-089 full +11 mm stack; was 529 mm D-058; see ADR-005 and TZ)
- **Operating mode: D-060 EXIT — FAST ITERATION MODE (D-043) closed 2026-08-06.** Owner visual 3D approval recorded in D-060; PROD-001 weld-free RFQ campaign active. No G0–G8 gate passed.
- Current phase: **rev15** FIX-WAVE-004 (D-075…D-076); prior FIX-WAVE-003 reconcile (D-066…D-074)
- Current gate: G0 (human verdict unconfirmed) — **no G0–G8 gate passed**
- Status: **`CONCEPT_REVISION`=15** evidence under `output/validation/rev15/`. **`hardware.handle_mount_y_mm`=181.3 mm** (D-089; was 180.6 at D-084). **`hardware.handle_mount_z_mm`=263 mm** (D-089; was 252). Corner posts **restored** (D-075); interlock / six service volumes / BASE·ORG·POST cladding remain removed (D-067…D-071). Door/tray choreography updated (D-076, **owner-confirmed**); `trays.upper_extension`=0. Envelope **650 × 420 × 540 mm** (D-089).
- Last updated: 2026-08-08 (FIX-DOC-007 / D-090 advertising sync)
- **Tests:** `uv run pytest -q` green on implementer machine (~370+ cases, 1 skip for missing rev evidence until regenerate); Full profile pending verifier
- **Tooling/process (D-041, 2026-08-05):** `pytest-xdist` + `-n auto`; `Quick`/`Full` profile guidance; operational-orchestrator turn-ending directive; `docs/14_CAD_MODELING_CONVENTIONS.md`
- **Handoff:** paste `HANDOFF_PROMPT.md` into a new chat to continue; do not use stale mid-file “Older status” narratives from prior drafts
- **Verification debt ledger:** `state/DEFERRED_VERIFICATION.md` — side-slab mass contradiction **closed (D-055)**; lid-headroom/interlock intersection (PLT-008), transport retention, cavity-wall prototype validation remain open

## Consolidated fix wave + rev12 (D-049…D-054, 2026-08-05)

- **D-049 — tray travel restored to 250 mm both tiers:** `trays.lower_extension`/`upper_extension` 200→**250**; `lower_quick_access_extension_mm`=130 unchanged. At 250 mm with Cameo 4 depth 195 mm and `plotter.lower_y`=15 mm, plotter rear face Y=**−40 mm** (TZ `front_overhang_min_mm`=40 satisfied). **Indicative tip factors at `case.depth`=420 mm:** upper **2.339**, lower **2.650** (split-mass model D-039). **Supersedes D-048** (200 mm interim and its ~3.480/~3.943 figures).
- **D-050 — superseded by D-051 (Y choice):** geometric depth-centre handle Y=210 mm / Z=252 mm; service-port/cable aft-shift experiment — do not treat as current.
- **D-051 — handle at loaded-case balance point (historical snapshot; superseded by D-074/D-084):** `hardware.handle_mount_y_mm`=**185.9 mm** (D-063 retune; supersedes D-055 **187.6 mm** snapshot; **current live Y=180.6 mm per D-084**, was 179.8 mm at D-074); `handle_mount_z_mm`=**252 mm** unchanged. Service port Y=**275** / cable Y=**320** (D-047 pairing). Port aft margin **≈34.1 mm** (historical at Y=185.9); cable nearest edge **≈79.1 mm** aft of grip (historical). **OPEN:** tier-2 finger intrusion **≈1,515,402 mm³** at current balance point Y=180.6 (was **≈1,529,766 mm³** at D-074 Y=179.8; **≈1,389,717 mm³** at historical Y=185.9) — handle concept deferred (`docs/10_USER_INPUT_REQUIRED.md` §E/§F).
- **D-052 — PRELIMINARY drawing package rev12:** `CONCEPT_REVISION` 11→**12**; `scripts/generate_drawings.py` → PDF + REFERENCE_ONLY DXF + programmatic `to_measure` traceability; evidence under `output/validation/rev12/`.
- **D-053 — evidence-integrity fixes:** REL-027 count **42** (was 44 baseline; −2 when D-046 removed `services.edgeguard_depth_mm`/`rearsupport_depth_mm`); manifest readback checks; `doctor.py` rev12 artifact checks; SVG edge-skip warnings; mass-report text sync to D-046 media path.
- **D-054 — consolidated adversarial-review fix wave:** traceability honesty (PLT-010 `IN_PROGRESS`, D-048↔D-049 supersession link, D-028 partial supersession by D-046), docs honesty (`docs/10`, `docs/08`, `docs/12`), decision-log/ADR-005 corrections, **cable-grommet lining fix** (only 3 mm of 20 mm bore was lined — now full annular grommet), render-view `cable_passthrough_closeup` target fix, test strengthening including **intentionally-failing** `tests/test_kinematics.py::test_lid_envelope_no_intersection_in_service_states` (LID-ENVELOPE-P1-001 vs INTERLOCK-SHUTTLE-001 **≈210,600 mm³** — left failing pending owner decision on lid headroom §M). No new physical design decisions.

## Owner edit batch 2026-08-05 (D-044…D-048) — **partially superseded by D-049…D-054**

> **Forward pointer:** D-049 restores 250 mm tray travel and supersedes D-048 figures; D-051 supersedes handle coordinates cited here; D-052 bumps `CONCEPT_REVISION` to 12; D-054 corrects documentation/tooling only. Retain this section as historical record — do not treat D-048 tip factors or 200 mm travel as current.

- **D-044 — top-front rail removed:** `FRAME-RAIL-TOP-FRONT-001` and `PANEL-CLAD-FRONT-TOP-001` deleted; TOP-LEFT/TOP-RIGHT/TOP-REAR still close the ring on three sides. Top perimeter ring resistance to front-top splay **unverified** — deferred in `state/DEFERRED_VERIFICATION.md`.
- **D-045 — depth shrink:** `case.depth` 550→**420 mm**; envelope **650 × 420 × 544 mm**; closed-state tier-2 rear clearance 340→**210 mm** (420−210 at aligned tiers). Mass roll-up at shallower depth: structural **~6.048 kg** / all-parts **~8.476 kg** (post-D-045 regenerate; **supersedes** pre-D-045 rev11 figures 7.054 / 9.292 kg).
- **D-046 — rear media exit widened:** **450 × 10 mm** through-cuts through **both** `PANEL-OUT-REAR-001` and `PANEL-IN-REAR-001` at L1/L2; `media_path.clear_width` 330→450, `slot_height_target` 18→10, `clear_height_min` 12→10 (owner override of TZ 12 mm floor). Removed `SVC-INSERT-L{1,2}-001` / `EDGEGUARD-L{1,2}-001` / `REARSUPPORT-L{1,2}-001`; replaced by flat `MEDIA-SUPPORT-L{1,2}-001` glide surfaces plotter rear edge → inner rear wall. Physical film-glide validation still open.
- **D-047 — cable pass-through relocated:** `SVC-CABLE-PASSTHROUGH-001` (Ø30 mm, 26 mm clear bore, R1 edge break — dimensions unchanged from D-036) moved from rear panel (was X=325) to **`PANEL-OUT-RIGHT-001` at Y=320 / Z=120**, adjacent to USB service port (Y=275). Rear wall kept clean for film feed.
- **D-048 — tray travel capped at 200 mm both tiers (SUPERSEDED by D-049):** `trays.lower_extension` 250→200, `trays.upper_extension` 400→200; `lower_quick_access_extension_mm`=130 unchanged. **Historical indicative** tip factors at `case.depth`=420 mm: upper **~3.480**, lower **~3.943** (split-mass model D-039). **Current (D-049):** 250 mm extension; upper **2.339**, lower **2.650**. D-048 status in decision log: **Superseded**.
- **Evidence / verification:** geometry + targeted tests updated; full pytest/adversarial/render/mass-stability re-campaign deferred per D-043. All exports remain **CONCEPT / REFERENCE_ONLY**; no gate G0–G8 passed.

## FAST ITERATION MODE (D-043) — **superseded; exited D-060 (2026-08-06)**

> **Historical record only.** D-043 deferred Quick/Full verification until owner visual 3D approval. **Exit recorded in D-060 (2026-08-06).** Do not cite FAST ITERATION as active.

- **Recorded policy (D-043):** rapid geometry/appearance iteration in live viewer; defer exhaustive pytest/adversarial campaigns until owner approval
- **Exit (D-060):** owner visual 3D approval **recorded satisfied 2026-08-06** — FAST ITERATION MODE closed; PROD-001 weld-free RFQ campaign is the active frame
- **Pre-D-060 practice:** rev12 drawing package (D-052) and fix waves (D-053/D-054) ran verification before formal D-060 exit — moot after D-060; debt tracked in `state/DEFERRED_VERIFICATION.md`
- **Invariants (unchanged):** no production-ready label; no G0–G8 pass without Human Gate; all exports remain CONCEPT/REFERENCE_ONLY/PRELIMINARY

## PLT-009 height-stack fix (2026-08-04, D-038)

- **Fix:** `plotter.upper_z` formula now reserves full tier-2 under-tray stack (slide 12 mm + frame profile 15 mm + tray panel 11 mm) — was missing 27 mm. Propagated +27 mm through `film_storage_horizontal.z`, `top_structure`, `case.height`, `handle_mount_z_mm`.
- **Values:** `upper_z` 211→**238**; `case.height` 517→**544**; `handle_mount_z_mm` 263→**276.5**; `tier_clearance_lower_mm` 170→197
- **F-5 closed:** zero `intersection_volume` at all 7 tier-2 under-tray parts × 5 tray-1 positions; Z-gap constant across travel (rails 11 mm, slides 26 mm, interlock tab 15 mm)
- **Light-strip §I:** `minimum_clearance(LIGHT-STRIP-001, FRAME-POST-RR-001)` still **0.5 mm** (common +27 mm shift); no reposition — XY overlap requires `to_measure` length change
- **Tests:** 321 pytest passing (285 baseline + 35 F-5 regression + 1 computed_upper_z); ruff clean
- **Baseline commit:** `d3e4247`
- **Next:** adversarial-reviewer on F-5 evidence; verifier Full profile

## QA sweep cycle 2 (2026-08-04)

- **Scope:** scripted `intersection_volume` audit across **8 configuration states** — `transport`, `organizer_loaded`, `panels_hidden`, `operating`, `operating_with_test_bodies`, tier-1 tray at `lower_extension`=0 / `lower_quick_access_extension_mm` (130) / `lower_extension` (250), tier-2 tray at `upper_extension`=0 / 400
- **Fix delivered:** film-shelf front-withdrawal path collided with `FRAME-POST-FL-001` `leg_h` (≈74.23 mm³ at every withdrawal offset dy=20–340 mm) and `PANEL-CLAD-FRONT-POST-FL-001` (300–900 mm³). Real clearance notch cut in `frame.py` (X=`film_storage_horizontal.x`→`corner_radius+frame_profile_size_mm`, Y=0→profile, Z=organizer clear-volume band only); mirrors `_tray1_clearance_notch_x_z` pattern. Regression: `tests/test_geometry.py::test_film_body_front_withdrawal_clears_front_left_post` (4 shelves × 36 withdrawal steps)
- **F-5 (supersedes qualitative note below):** ~~open~~ **RESOLVED by D-038 (PLT-009)** — see PLT-009 section above. Historical quantification retained in `docs/10_USER_INPUT_REQUIRED.md` §H.
- **Light-strip near-miss:** `LIGHT-STRIP-001` vs `FRAME-POST-RR-001` exactly **0.5 mm** clearance in transport (zero margin vs `tolerance.part_assembly_feature_mm`). Flagged in `docs/10_USER_INPUT_REQUIRED.md` §I; no geometry change
- **Tests:** 285 pytest passing (141 baseline + 144 new parametrized cases in `test_film_body_front_withdrawal_clears_front_left_post`); ruff clean
- **Baseline commit:** `9e38f98`
- **Next:** adversarial-reviewer on film-post notch; verifier Quick profile

## PLT-007 cable pass-through (D-036, 2026-08-04; **superseded mount by D-047, 2026-08-05**)

- **Change (historical D-036):** Owner override of TZ section 10 certified rear mains inlet → plain **30 mm** grommeted cable pass-through; `SVC-CABLE-PASSTHROUGH-001` annular grommet (26 mm clear bore, 1 mm TZ:472 R1 chamfer on the bore rim); `MAINS-INLET-001` placeholder unchanged (deferred, not deleted)
- **Mount (superseded):** ~~rear panel centre (X=325, Z=160.5)~~ → **D-047:** `PANEL-OUT-RIGHT-001` at **Y=320 / Z=120**, next to USB service port (Y=275); rear-panel round cut removed
- **Delivered:** real boolean cut through both `PANEL-OUT-REAR-001` and `PANEL-IN-REAR-001` (cycle-1 adversarial review found the first pass only cut the outer skin and used a solid, bore-less grommet — both fixed); `hardware.cable_passthrough_diameter_mm`, `services.cable_passthrough_grommet_wall_mm` (`to_measure`), `services.cable_passthrough_edge_break_radius_mm` (`verified`, TZ:472 R1); `CONCEPT_REVISION`=8; `cable_passthrough_closeup.png` evidence
- **Evidence target:** `output/validation/rev8/views/`; STEP/manifest `*_rev8.*`
- **Tests:** 141 pytest passing; ruff clean; `scripts/setup_windows.ps1` exit 0
- **Review:** adversarial-reviewer APPROVED on cycle 2 (cycle 1 REWORK: F-1 solid-plug grommet, F-2 inner panel not cut, F-3 stale REL-027 count — all closed)
- **Next:** local commit (no push); human G0 verdict unchanged

## PLT-007 horizontal reconfig + Cameo 4 governing envelope (2026-08-04; **partially superseded D-045/D-046/D-048, 2026-08-05**)

- **Envelope (current):** **650 × 420 × 540 mm** (D-089 +11 mm over D-058 **529 mm**; D-045 depth shrink from 550 mm); **610 mm clear width** (20 mm side wall, **R10** bullnose — D-027 rejects 620/630 widening). Historical D-058 height **529 mm** superseded by D-089 **540 mm**.
- **Governing machine:** Silhouette Cameo 4 — 570 × 195 × 170 mm, 4.7 kg (`plotter_cameo4`); design envelope 584 × 219 × 178 mm; slot 2 mass 5.2 kg (Cameo 5)
- **Film storage:** 4 horizontal shelves, 25 mm compartment height, 500 mm sheet edge across width
- **Tier layout:** tiers aligned, setback removed (D-033); `lower_y`=`upper_y`=15; tier 1 has 130 mm quick-access forward slide (`trays.lower_quick_access_extension_mm`) plus **250 mm** full-service extension on both tiers (D-049; **supersedes** D-048 interim 200 mm and TZ 400 mm upper); tier clear height ≥170 mm each
- **Storage clearances (closed trays):** plotter 1 front **15 mm**; plotter 2 rear **210 mm** to case back at `case.depth`=420 mm (**supersedes** 340 mm at 550 mm depth / D-033 alignment)
- **Operational clearance (structural — settled):** manufacturer pass-through **907 mm** (356+195+356) **exceeds** case depth **420 mm** → **closed niche is storage/transport only** (D-028). Active cutting requires material through front **and** rear openings (**450 × 10 mm** slots at L1/L2 through both rear panels — D-046; **supersedes** 330 × 18 mm outer-only / `REARSUPPORT-*`) and/or tray extension plus **`MEDIA-SUPPORT-L{1,2}-001`** glide surfaces (D-046; **supersedes** external `REARSUPPORT-*`). Tests: `test_pass_through_depth_exceeds_case_envelope`, `test_operating_state_front_rear_pass_through_open`, `test_rear_media_channel_clear_of_obstructions`.
- **Delivered:** service-port cutout (provisional); handle Z=263 (side-panel centre) — **superseded 2026-08-04 by D-038: recomputed to 276.5 mm** on the taller 544 mm case, formula unchanged; frame cladding; grey backgrounds; `CONCEPT_REVISION`=7; `service_port_closeup.png` evidence
- **Evidence target:** `output/validation/rev7/views/`; STEP/manifest `*_rev7.*`
- **Viewer:** `uv run python scripts/serve_viewer.py --watch` → `http://127.0.0.1:8000/viewer/index.html` (see `viewer/README.md`)
- **Tests:** 132 pytest passing; ruff/setup not re-run this cycle
- **Pre-change SHA:** `69b1261`
- **Next:** adversarial-reviewer on rev7; verifier Full profile
- **Known non-blocking follow-ups from D-033 adversarial review (2026-08-04, not required for this cycle):** F-3 `tests/test_kinematics.py::test_tray1_quick_access_distinct_from_full_extension` is YAML-only (no geometry measurement) — could be strengthened later. **F-5 closed by D-038/PLT-009** — zero `intersection_volume` at all 7 tier-2 under-tray parts × 5 tray-1 positions (35 regression cases); see **PLT-009 height-stack fix** section above and `docs/10_USER_INPUT_REQUIRED.md` §H (RESOLVED). F-6 `is_open_front_kinematic_contact()` docstring should mention the tray-1 base-front notch now modeled in `frame.py`.

## PLT-006 fidelity cycle 4 (2026-08-04)

- **Phase:** fidelity cycle 4 → **rev5** evidence pack (CONCEPT / REFERENCE_ONLY)
- **Delivered:** opal `PANEL-CLAD-FRONT-{BASE,ORG,TOP}-001` over centre front rails; R10 side-slab bullnose (exterior front vertical + top edge); mass report paths sync to `CONCEPT_REVISION`; `evidence_light_strip_only.png` / `evidence_retainer_only.png` identity renders; handle Z note cites CoM z≈217.3 mm (unchanged Y=100/Z=214) — **rev5-era figures; superseded by D-038 height-stack fix (handle Z now 276.5 mm) and current `output/validation/rev11/mass_report.csv` (CoM empty case z=236.4 mm; case + 2 plotters z=229.3 mm). D-040 (2026-08-04) also found this cladding's pre-rev11 PNG renders had a Z-buffer tie-break defect that hid it behind the rail it covers — the geometry above was always correct, only the render tool's visual evidence was wrong; see rev11 evidence.**
- **Evidence:** 14 PNG + 5 SVG in `output/validation/rev5/views/`; STEP/STL/GLB/manifest `*_rev5.*`; `rev4/` untouched
- **DEVIATED:** PLT-018 / TZ line 230 R20–R30 → R10 bullnose (D-025)
- **Tests:** 130 pytest passing; ruff clean; `scripts/setup_windows.ps1` exit 0
- **Next:** adversarial review of rev5 PNGs; human G0 verdict unchanged

## PLT-005 fidelity cycle 3 + dev loop (2026-08-04)

- **Phase:** dev-loop automation (Part A) + fidelity cycle 3 → **rev4** evidence pack (CONCEPT / REFERENCE_ONLY)
- **Part A delivered:** `scripts/doctor.py`, `scripts/regenerate.py`, `scripts/serve_viewer.py --watch` + `GET /viewer/reload-status`, viewer live reload (preserves camera/visibility/clipping on auto reload)
- **Part B delivered:** handle reposition + grey side-view backgrounds; organizer front-dominant camera + FILM-BODY-009 formula fix; outer shell raised to `foot_height_mm`; solid side slabs; rear vent legibility via grey `transport_rear.png` background + grid probe test
- **Evidence:** 12 PNG + 5 SVG in `output/validation/rev4/views/`; STEP/STL/GLB/manifest `*_rev4.*`; `rev1/`–`rev3/` untouched
- **Achieved side-slab corner fillet:** **≈9.9 mm** (R25 clamped by 20 mm side-clear band — see D-019, `docs/10_USER_INPUT_REQUIRED.md` §D)
- **Tests:** 124 pytest passing; ruff clean; `scripts/setup_windows.ps1` exit 0
- **Next:** adversarial review of rev4 PNGs + live-reload behaviour; human G0 verdict unchanged

## PLT-004 fidelity cycle 2 (2026-08-04)

- **Phase:** shell restructuring + handle visibility fix (`output/validation/rev3/`, CONCEPT / REFERENCE_ONLY)
- **Delivered:** full-height side slabs (20 mm × 690 mm, 2D front-corner fillets, single solid each); open front (no `PANEL-OUT-FRONT-001`); open organizer top (no `TOP-STRUCTURE-001`); removed `PANEL-OUT-CORNER-*`; handle cutout repositioned (Y=`depth×0.25`, Z=`upper_z+physical_height/2` provisional); bottom vent through-cuts on `PANEL-IN-BOTTOM-001` under `AIRPATH-001`; organizer close-up render
- **Removed parts:** `PANEL-OUT-FRONT-001`, `TOP-STRUCTURE-001`, `PANEL-OUT-CORNER-FL/FR/RL/RR-001` (4)
- **Evidence:** 12 PNG + 5 SVG in `output/validation/rev3/views/` (incl. `organizer_closeup.png`, `base_plate_closeup.png`); STEP/STL/GLB/manifest `*_rev3.*`; `rev1/` and `rev2/` untouched
- **Mass (rev3 figure):** indicative structural **7.849 kg** (3 mm PMMA side-slab shells; single-face shell estimate); deflection 3.953 mm (unchanged; ceiling NOT met) — **superseded: deflection fixed to ≈0.228 mm by D-035's three-rail centre support (ceiling now met); current post-D-045 structural mass ~6.048 kg / all-parts ~8.476 kg (supersedes pre-D-045 rev11 figures 7.054 / 9.292 kg)**
- **Tests:** 121 pytest passing; ruff clean; `scripts/setup_windows.ps1` exit 0
- **Next:** adversarial review of rev3 PNGs; human G0 verdict unchanged

## PLT-003 concept validation (2026-08-03, updated 2026-08-04)

- **Phase:** concept validation evidence pack (`output/validation/rev1/`, CONCEPT / REFERENCE_ONLY)
- **Delivered:** quarter-cylinder corner shells (`PANEL-OUT-CORNER-FL/FR/RL/RR-001`); organizer top perimeter frame + front opening above retainer; divider finger cutouts; all-cell film bodies; cylindrical feet; rear vent slots; TOP-STRUCTURE sketch R25 footprint; corner junction skin continuity fix (cycle 3)
- **Evidence:** 10 PNG + 5 SVG in `output/validation/rev1/views/`; STEP/STL/GLB/manifest `*_rev1.*` in `output/concept/`; viewer `index.html` → rev1 manifest
- **Mass (rev1 figure):** empty-case indicative 9.573 kg; regenerate via `scripts/generate_mass_report.py` — **superseded: current post-D-045 structural total ~6.048 kg (excl. `verify_on_real_machine` parts) / all-parts total ~8.476 kg (supersedes pre-D-045 rev11 figures 7.054 / 9.292 kg)**
- **Tests:** 117 pytest passing; ruff clean; `scripts/setup_windows.ps1` exit 0
- **Render path:** `uv run python scripts/render_validation_views.py` writes to `output/validation/rev1/views/` and `output/concept/*_rev1.*`
- **Open:** vent slot dimensions provisional (`to_measure`); corner top-edge fillet best-effort; adversarial sign-off pending
- **Next:** final sign-off on PLT-003 evidence pack; then Gate G0 human verdict

## Product pivot (2026-08-03)

The Light Plotter Tower TZ (`ИИ советы/Cursor_Opus5_TZ_Light_Plotter_Tower.md`) supersedes the earlier mobile-floor-stand framing (ADR-005, D-011). The parameter layer now exists: `config/parameters.yaml` and `src/stand_cad/parameters.py`. No geometry has been generated yet. TZ section 3 supplies G1 equipment data for the Silhouette Cameo 5 (physical envelope, mass, quantity = 2); G1 itself remains an unconfirmed Human Gate.

## Git baseline

- Repository initialized with remote `origin` = `https://github.com/MihaRooll/stand-cad-ai-starter.git` (fetch and push). Upstream branch: `origin/main`.
- Commits (oldest first):
  - `910a23a` — Initial commit: add README
  - `a1f2c97` — Initial AI-first CAD project specification
  - `c07dbf4` (`c07dbf40235ffb258bc5881d3d71d7ac194a7d62`) — Adopt orchestration harness and record MCP connectivity resolution (15 files: `.cursor/agents/`, `.cursor/skills/autonomous-task/`, rules `20`/`21`/`30`, four `state/**` files)
- Annotated tag `baseline` on `a1f2c97`, message `Baseline: initial AI-first CAD project specification`.
- `c07dbf4` is local-only and unpushed (`git log origin/main..HEAD` lists it; not pushed to remote).

## G0 status (evidence only)

G0 exit-criteria evidence is partially complete on native Windows; gate verdict is a Human Gate and remains unconfirmed.

Satisfied: locked dependency sync (53 packages), input validator with `--allow-demo`, smoke STEP bounds 100 × 60 × 20 mm (`output/smoke/calibration_block_REFERENCE_ONLY.step`, 15460 bytes), `uv run pytest` (9 passed), `uv run ruff check .` (clean), pinned MCP session connectivity — `build123d-mcp@0.3.81` connected in-session with 38 tools exposed and `serverStatus: ready` (see MCP server record; satisfies evidence collection for `docs/05_IMPLEMENTATION_PLAN.md:26`).

Evidence collected is not a gate verdict: G0 remains an unconfirmed Human Gate.

## Environment and versions

- `requires-python`: `>=3.12,<3.13` (`pyproject.toml:9`)
- `build123d==0.11.1` (`pyproject.toml:11`)
- Locked dependency sync: 53 packages resolved (`uv.lock`)
- Command rule: all project commands run via `uv run`; bare `python` on this machine resolves to 3.11

## MCP server record

- Pinned package: `build123d-mcp@0.3.81` (`.cursor/mcp.json:10`; schema-correct: top-level `mcpServers`, server key `build123d-mcp`, `command: "uv"`, `args: ["tool","run","--python","3.12","build123d-mcp@0.3.81"]`; no `env`, `cwd`, `transport`, `type`, or `disabled` keys).
- Package-level (native Windows): `uv` resolves to `C:\Users\katko\.local\bin\uv.exe`; `uv tool run --python 3.12 build123d-mcp@0.3.81 --help` exits 0 and advertises `--transport {stdio,http}` with default `stdio`. Confirms the package resolves and runs natively. This is separate from session connectivity below.
- Session connectivity timeline:
  - **Pre-enable (historical, before 2026-08-03 ~19:48):** registered but client never started — Cursor registered `build123d-mcp` but did not spawn or connect an MCP client (zero tools exposed). Evidence: `workbench.mcp.files.log` shows `createClient` only for the `context7` plugin server, never for build123d; `workbench.mcp.oauth.log` repeats `project-0-stand-cad-ai-starter-build123d-mcp none -> disconnected`; `Mcp FileSystem Writer.log` lines 6–14 show build123d receives only a `server_status` lease while context7 receives `snapshot_store`, then `lease returned 2 tools across 1 clients`; no spawn / ENOENT / `uv` error line for build123d in those pre-enable logs. Resolution required user action (enable toggle and Reload Window), not a repository code change.
  - **Resolution (2026-08-03):** user enabled the server via Cursor Settings → MCP → `build123d-mcp` → enable toggle → Reload Window. Post-enable log `C:\Users\katko\AppData\Roaming\Cursor\logs\20260803T185957\mcp-server-project-0-stand-cad-ai-starter-build123d-mcp.log` (1051 bytes): line 1, 2026-08-03 19:48:13.414, `connecting stdio for "build123d-mcp" (project-0-stand-cad-ai-starter-build123d-mcp)`; line 3, `MCP stdio spawn policy decision: sandboxed=false, sandboxReason=controls_disabled`; line 4, 2026-08-03 19:48:14.585, `Successfully connected to stdio server`; lines 6–11, three `[error] Processing request of type ListToolsRequest / ListPromptsRequest / ListResourcesRequest` entries followed by `undefined`. **Interpretation (not fact):** these are the MCP SDK's own stderr request-logging relayed by Cursor under an error label; they coincided with a successful connection and a successful tool listing, so they are not evidence of failure.
  - **Current session catalog (2026-08-03, post-enable):** server id `project-0-stand-cad-ai-starter-build123d-mcp`, `serverStatus: ready`, 38 tools exposed to the agent session (previously zero).
- `--in-process` fallback: never applied and never needed; post-enable log line 3 shows `sandboxed=false` (`controls_disabled`).
- Explicitly undetermined: the exact enabled/disabled bit in the Cursor settings store was never read directly.
- Reported `serverInfo.version` from MCP `initialize` handshake in an **earlier session**: `1.29.0` (not re-read in this session's catalog check).
- Note: package pin (`0.3.81`) and reported server runtime (`1.29.0`) are two different numbering schemes; both are expected and neither is "the" single version.

## Completed

- Three-cycle specification review completed.
- CAD stack and version policy selected.
- Source-of-truth, DFM, autonomy, and release boundaries recorded as ADRs.
- Repository starter, validation scaffold, and implementation plan prepared.
- Linux-container baseline passed during archive preparation.
- Git initialized; baseline commit `a1f2c97` on `origin`.
- Windows-native `uv`/Python/MCP verification complete.
- Committed `uv.lock` resolves on Windows (53 packages).
- Input demo validation passed explicitly with `--allow-demo`.
- Ruff passed and pytest passed: 9 tests.
- Reference-only STEP regenerated with verified bounds 100 × 60 × 20 mm.
- Windows-observed versions and outputs recorded (see Environment and versions, MCP server record).

## Phase 0 baseline work (items 1–5) — complete

1. Initialize Git and create baseline commit.
2. Verify Windows-native `uv`/Python/MCP.
3. Verify the committed `uv.lock` resolves on Windows.
4. Run validator, smoke model, lint, and tests.
5. Record exact Windows-observed versions and outputs.

## Remaining Phase 0 work

- Author MCP modeling/drawing/repair project rules per `docs/05_IMPLEMENTATION_PLAN.md:14` — precondition now satisfied (MCP connected in-session, 38 tools listed; see D-009). Authoring is unblocked as a separate follow-up packet; not in scope for this cycle. `build123d-mcp@0.3.81 --help` lists only server options, with no rule-install command; rules must be authored in this repository.

## Current blockers

### FAST ITERATION MODE — exited (D-060)

- D-043 exit condition (owner visual 3D approval) **recorded satisfied in D-060 (2026-08-06)**. FAST ITERATION MODE is closed; PROD-001 weld-free RFQ campaign is the active operating frame. Historical D-043 policy/practice mismatch (pre-D-060) is moot — do not cite FAST ITERATION as still active.

### Handle concept — tier-2 finger intrusion (D-074/D-084; `docs/10_USER_INPUT_REQUIRED.md` §E / §F)

- Balance-point through-cutout at Y=**181.3** / Z=**263** (D-089; was 180.6/252 at D-084) intersects tier-2 plotter bay by **≈1,502,833.5 mm³** (`test_handle_tier2_finger_intrusion_at_balance_point`). Owner deferred choosing: (1) external bolt-on handle, (2) blind side pocket, (3) low aft cutout behind plotters. Blocks production-ready side-panel release.

### Open-lid headroom (PLT-008; `docs/10_USER_INPUT_REQUIRED.md` §M)

- Provisional 80 mm lid envelope: **27 mm** headroom tier 1 / **50 mm** tier 2 with trays closed (transport canary) — lid cannot fully open. **Interlock hardware absent** (D-067); dual-extend inhibit is **procedure only**, not structurally proven. `tests/test_kinematics.py::test_lid_envelope_no_intersection_in_service_states` **xfail/canary** — do not weaken; remedy is owner decision on lid envelope, headroom, or operating procedure (§M).

### Transport retention (`docs/10_USER_INPUT_REQUIRED.md` §N; R-012)

- No tray closed-position latches, plotter tie-downs, or film front retainer modeled. Soft stops travel with trays. **Interlock hardware absent** (D-067); dual-extend inhibit is **procedure only** — not a modeled retention device. Owner **waived plotter tie-down** for event display; unrestrained mass: up to **10 kg** film (R-012).

### Tip-over — PLT-010 honesty (`IN_PROGRESS`; `docs/10_USER_INPUT_REQUIRED.md` §K / §L)

- **FIX-TIP-001 / D-077 (2026-08-08):** Upper tier at `trays.upper_extension`=0 (D-076) — tip check **N/A**, not `inf >= 1.5` pass. Applicability gate: `extension > 0` **and** `overturn_moment > 0`; report/metrics distinguish zero-travel vs extended-but-non-applicable wording (cycle 3). Lower@250 mm finite indicative factor still asserted in pytest (rev15 `stability_report.md`). Independent adversarial finding unchanged: 20 N lateral lean → **1.434** (<1.5); dual-tray **0.924** historical (pre-D-076 both-tier extend). **Not authoritative for Gate G4.** CSV row PLT-010 status **`IN_PROGRESS`**.

### Mass accounting (PLT-012 — `IN_PROGRESS`; indicative only)

- **D-078 (2026-08-08):** Current indicative totals live in `output/validation/rev15/mass_report.csv` — **not authoritative for Gate G4** / PLT-012 sign-off. Historical rev13 snapshot (side-slab cavity-wall + equal-leg angle formula, D-063): empty structural **8.806 kg**; D-061/D-065 indicative fastener **≈0.174 kg** (**158** screws: **137 M4 + 21 M3**) + bracket **0.145 kg** (34 nodes); all-parts indicative **12.860 kg**. Pre-D-063 headline **9.877 kg** and rev13 figures above are **superseded** — do not cite as current or as PLT-012 pass.

### Electrical and joining design — not engineered

- `THE-*` and `ELE-*` requirement rows in traceability CSV are all **`OPEN`**. No thermal/airflow analysis or qualified electrical arrangement in repository. See R-004, R-005 in `docs/08_RISK_REGISTER.md`.

### Verification-tooling fix — render Z-buffer tie-break (D-040, rev11)

- `scripts/render_validation_views.py`'s PNG rasterizer had a Z-buffer tie-break defect: coplanar cladding-over-rail pairs (`PANEL-CLAD-FRONT-{BASE,ORG,TOP,TRAY-*}-001` vs their rails) always resolved to the structural rail winning, because the strict `z > depth` comparison let whichever part was inserted first (always the rail) win every coincident-depth pixel. This meant "frame concealed" render evidence since fidelity cycle 4 (rev5) never actually showed the cladding — the geometry was always correct, the tool's PNG output was not. Fixed with a material-priority epsilon tie-break (`MATERIAL_RENDER_PRIORITY`, `DEPTH_EPSILON_MM=1e-6`); regression test `tests/test_render_tiebreak.py` covers both insertion orders. Independently confirmed by adversarial review: `rev10`→`rev11` pixel histograms show an exact aluminium↔cladding swap (e.g. transport_iso.png ∓30064 px) on all four checked views, zero change to mass/stability/deflection numbers. `SLIDE-*` hardware remains visible (unchanged, known non-blocking follow-up — separate owner decision, not fixed in this cycle). See D-040. **Note:** D-044 removed `PANEL-CLAD-FRONT-TOP-001`; remaining cladding pairs unaffected. D-054 also fixed cable-grommet lining (full annular grommet, not 3 mm stub) and `cable_passthrough_closeup` render target.

### Top-front ring structural capacity (D-044)

- With `FRAME-RAIL-TOP-FRONT-001` removed, top perimeter closes on three sides only. Front-top side-wall splay resistance **unverified** this cycle — see `state/DEFERRED_VERIFICATION.md`.

### Measurements and manufacturing

- Eight physical measurements on real plotters (Cameo 4 governing + Cameo 5 slot 2) and purchased sheet materials — see `docs/10_USER_INPUT_REQUIRED.md` §A (**still open**, including feed-plane height and open-lid hinge data §A items 3–4).
- Manufacturer DFM authorization — see `docs/10_USER_INPUT_REQUIRED.md` §B and Gate G5 in `docs/05_IMPLEMENTATION_PLAN.md`.

These blockers do not prevent parameter-layer work but block production geometry release and Gate G5/G6.

## Next decision

1. **Owner decisions on open product blockers** — handle concept (§F), lid headroom (§M), transport retention (§N trays/film; plotter tie-down waived per owner 2026-08-06).
2. After G0 gate verdict (Human Gate), complete the consolidated input packet in `docs/10_USER_INPUT_REQUIRED.md` (§A/B `to_measure` still open) and start equipment envelopes only for verified selected models.
