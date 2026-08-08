# Autonomous orchestrator — living status

> **Read this first** in a new chat after `HANDOFF_PROMPT.md`. Update this file at every closed defect cycle (before commit). English only. Owner replies in Russian; do not invent production-ready / G0–G8 pass.

## Snapshot (2026-08-08)

| Field | Value |
|---|---|
| Branch | `main` |
| HEAD | pending FIX-DOC-008 land — D-100 |
| Upstream | `origin/main` synced (ordinary push OK) |
| Next in flight | Live uncapped MATING_PAIRS (SOFT↔TRAY etc.); owner blockers: §F/§M/§N/§A |
| Live `CONCEPT_REVISION` | **15** (`src/stand_cad/geometry/export.py`) |
| Envelope | **650 × 420 × 540 mm** (D-089 full +11 mm stack; was 529 pre-D-089) |
| Owner-confirmed product | D-075 posts restored; D-076 upper fixed (`upper_extension=0`), lower 250 mm + door/tray choreography |
| Gates | **No G0–G8 passed** — all CONCEPT / REFERENCE_ONLY / PRELIMINARY |
| Mode | Autonomously fixing highest-impact **software/honesty** defects until owner says **СТОП** |
| Verify at land | Full **green** — `setup_windows.ps1` exit 0 (433 passed, 1 xfailed); ruff clean (FIX-HONESTY-001) |
| Commit policy | Mega-land authorized 2026-08-08. Keep excluding `ИИ советы/`, secrets, `.pytest_cache/`. `output/` gitignored. |

## Last closed defect

### FIX-DOC-008-csv-pytest-count — traceability pytest-count honesty (D-100) — **closed**

| | |
|---|---|
| Problem | `state/REQUIREMENTS_TRACEABILITY.csv` SWE-001/SWE-003 still advertised **345 pytest** as current after D-099 Full (**433 passed, 1 xfailed**) |
| Root cause | Stale hardcoded count in CSV evidence column |
| Fix | Durable wording: pytest suite green on Full/`uv run pytest`; count drifts — do not treat as physical proof; SWE-003 weak-oracle note preserved |
| Measured | N/A — documentation honesty only |
| Residual P2 | Unchanged — live uncapped `MATING_PAIRS`; owner blockers §F/§M/§N/§A |
| Key paths | `state/REQUIREMENTS_TRACEABILITY.csv`; `state/DECISION_LOG.md` D-100 |
| Verify | Verifier pass; `uv run ruff check .` exit 0 (state-only Quick) |
| Explicitly NOT done | Gate pass; geometry/collision changes; pinned numeric count |

**Anti-false-conclusion:** green pytest count ≠ physical clearance or manufacturability proof.

### FIX-HONESTY-001-dead-collision-allowlists — prune zombie allowlists (D-099) — **closed cycle 1**

| | |
|---|---|
| Problem | `collision.py` still advertised INTERLOCK/MAINS/EDGEGUARD/REARSUPPORT/AIRPATH/SVC-INSERT on mating/penetrating/share_face allowlists after D-046/D-067/D-071 removed those solids |
| Root cause | Honesty debt — allowlist entries not pruned when parts stopped emitting |
| Fix | Remove dead `RAW_MATING_PAIRS` / `PENETRATING_JOINT_PATTERNS` rows; delete `REAR_BOTTOM_SERVICE_CLUSTER` + cluster branches; drop INTERLOCK share_face / open-front / staggered markers; stub `intentional_block_pair` → False. Regression pin `test_collision_allowlists_exclude_absent_part_prefixes` |
| Measured | N/A — honesty prune only; no live pairs for absent prefixes |
| Residual P2 | SOFT↔TRAY, shelf/org, media on uncapped `MATING_PAIRS`; `kinematics.py` INTERLOCK groups unchanged |
| Key paths | `collision.py`; `tests/test_geometry.py`; `docs/14` §10a/§11; `state/DECISION_LOG.md` D-099 |
| Verify | Adversarial accept; Quick 433 passed; Full `setup_windows.ps1` exit 0 |
| Explicitly NOT done | Gate pass; §F/§M/§N/§A closure; Path A geometry; INTERLOCK/MAINS restore |

**Anti-false-conclusion:** pruning zombie allowlists ≠ physical clearance proof for residual live P2.

### FIX-COLL-013-cross-tier-share-face-bypass — cross-tier TRAY/SLIDE↔rail share_face exclude (D-098) — **closed cycle 1**

| | |
|---|---|
| Problem | Uncapped `TRAY-`/`SLIDE-` ↔ `FRAME-RAIL-TRAY` `_share_face_if_prefix` in `is_mating()` returned True before staggered check — cross-tier synthetic burial with share_face silent-green (~**1222650 mm³** TRAY, ~**105300 mm³** SLIDE) |
| Root cause | Share_face short-circuit at `collision.py` ~1055–1058 ran before `is_staggered_tier_y_overlap()` (~1121); D-097 staggered gate never reached for cross-tier share_face contacts |
| Fix | `_is_cross_tier_tray_slide_rail_pair()`; skip uncapped share_face when cross-tier; reuse `STAGGERED_TIER_MAX_BEARING_MM3=500.0` (D-097). Two new regression tests; staggered plane-touch retained via D-097 |
| Measured | Live transport/service cross-tier TRAY/SLIDE↔opposite rail share_face max **0 mm³**; same-tier SLIDE↔rail `MATING_PAIRS` vol≈0 |
| Residual P2 | Closed dead allowlists in D-099; other uncapped `MATING_PAIRS`/share_face |
| Key paths | `collision.py`; `tests/test_geometry.py`; `docs/14` §11; `state/DECISION_LOG.md` D-098 |
| Verify | Adversarial accept; Quick 432 passed; Full `setup_windows.ps1` exit 0 |
| Explicitly NOT done | Gate pass; §F/§M/§N/§A closure; Path A geometry; INTERLOCK/MAINS restore |

**Anti-false-conclusion:** share_face exclude + staggered 500 mm³ hygiene ≠ prototype Z clearance proof.

### FIX-COLL-012-staggered-tier-volume-gate — staggered-tier Y-overlap volume gate (D-097) — **closed cycle 1**

| | |
|---|---|
| Problem | `is_staggered_tier_y_overlap()` returned True on cross-tier Y-overlap alone — no `intersection_volume` ceiling; historical burial `EQUIP-PLOTTER1` ↔ `FRAME-RAIL-TRAY-UPPER` ~**43875 mm³** silent-green |
| Root cause | Y-overlap-only heuristic in `is_staggered_tier_y_overlap()` wired via `is_mating()` ~1114 — same class as D-086/D-080/D-087 volume gates |
| Fix | `STAGGERED_TIER_MAX_BEARING_MM3=500.0`; gate after Y-overlap check; marker lists and `is_mating` call site unchanged. Two regression tests |
| Measured | Live transport/service max **0 mm³** (149/38/149 cross-tier marker pairs with y_overlap > threshold) |
| Residual P2 | F-1: TRAY/SLIDE↔cross-tier `FRAME-RAIL-TRAY` uncapped share_face before staggered; dead INTERLOCK/MAINS allowlists; other uncapped `MATING_PAIRS` |
| Key paths | `collision.py`; `tests/test_geometry.py`; `docs/14` §11; `state/DECISION_LOG.md` D-097 |
| Verify | Adversarial accept; Quick 430 passed; Full `setup_windows.ps1` exit 0 |
| Explicitly NOT done | Gate pass; §F/§M/§N/§A closure; Path A geometry; INTERLOCK/MAINS restore |

**Anti-false-conclusion:** 500 mm³ ceiling is hygiene gate — live 0 mm³ does not prove physical Z clearance at prototype (kinematics canary separate).

### FIX-COLL-011-cover-svc-frame-ceiling — COVER-SVC↔FRAME BASE/POST volume gates (D-096) — **closed cycle 1**

| | |
|---|---|
| Problem | `COVER-SVC-001` ↔ `FRAME-RAIL-BASE-REAR-001` (~7350 mm³) and ↔ `FRAME-POST-RL/RR-001` (~123 mm³) uncapped on share_face; POST pairs also uncapped in `PENETRATING_JOINT_PATTERNS` — deep burial silent-green |
| Root cause | `is_mating()` returned unconditional True for `COVER-SVC-`/`FRAME-RAIL-BASE` and `FRAME-POST-R` share_face; `is_penetrating_structural_joint()` had no ceiling for COVER↔POST patterns |
| Fix | `COVER_SVC_FRAME_BASE_MAX_BEARING_MM3=10000.0`; `COVER_SVC_FRAME_POST_MAX_BEARING_MM3=500.0`; helpers + share_face gates; `COVER_SVC_FRAME_POST_PENETRATING_PATTERNS` gated in penetrating path. Five regression tests |
| Measured | Live transport: BASE-REAR **7350.0 mm³**; POST RL/RR **122.9474 mm³** each |
| Residual P2 | INTERLOCK-TAB↔PANEL-IN; BASE-REAR↔MAINS-INLET; other uncapped `MATING_PAIRS` |
| Key paths | `collision.py`; `tests/test_geometry.py`; `docs/14` §11; `state/DECISION_LOG.md` D-096 |
| Verify | Adversarial accept; Quick 428 passed; Full `setup_windows.ps1` exit 0 |
| Explicitly NOT done | Gate pass; §F/§M/§N/§A closure; global ceiling |

**Anti-false-conclusion:** 10000/500 mm³ ceilings are measured hygiene gates — live overlap is design intent, not proof of physical clearance at prototype.

### FIX-COLL-010-cover-svc-mating-ceiling — COVER-SVC↔PANEL volume gate (D-095) — **closed cycle 1**

| | |
|---|---|
| Problem | `COVER-SVC-001` ↔ `PANEL-IN-BOTTOM-001` / `PANEL-OUT-REAR-001` on `MATING_PAIRS` uncapped — deep burial silent-green; `COVER-SVC-001` ↔ `PANEL-IN-REAR-001` via uncapped `COVER-SVC-`/`PANEL-` share_face (~7901 mm³, not on `MATING_PAIRS`) |
| Root cause | `is_mating()` MATING_PAIRS branch returned unconditional True; share_face bypass had no volume ceiling |
| Fix | `COVER_SVC_PANEL_MAX_BEARING_MM3=10000.0` with `is_cover_svc_panel_pair()` / `is_cover_svc_panel_bearing()`; gate MATING_PAIRS branch + share_face path. Four regression tests |
| Measured | Live transport: BOTTOM **7901.25 mm³**; OUT-REAR **1048.99 mm³**; IN-REAR **7901.25 mm³** |
| Residual P2 | INTERLOCK-TAB↔PANEL-IN; BASE-REAR↔MAINS-INLET; other uncapped `MATING_PAIRS` |
| Key paths | `collision.py`; `tests/test_geometry.py`; `docs/14` §11; `state/DECISION_LOG.md` D-095 |
| Verify | Adversarial accept; Quick 423 passed; Full `setup_windows.ps1` exit 0 |
| Explicitly NOT done | Gate pass; §F/§M/§N/§A closure; COVER↔POST/BASE-REAR caps; global ceiling |

**Anti-false-conclusion:** 10000 mm³ ceiling is measured hygiene gate — live 7901.25 mm³ overlap is design intent, not proof of physical clearance at prototype.

### FIX-COLL-009-tray-rail-panel-penetrating-ceiling — TRAY-rail↔PANEL-IN volume gate (D-094) — **closed cycle 1**

| | |
|---|---|
| Problem | `FRAME-RAIL-TRAY-` ↔ `PANEL-IN-` in `PENETRATING_JOINT_PATTERNS` with no volume ceiling — deep burial silent-green; coplanar share_face bypass (ORG∪POST-only exclude from D-092/D-093) |
| Root cause | `is_penetrating_structural_joint()` gated ORG/MID/POST/open-front only; `PANEL-IN-`/`FRAME-` `_share_face_if_prefix` returned True for TRAY-rail↔PANEL-IN before penetrating check |
| Fix | `TRAY_RAIL_PANEL_PENETRATING_MAX_BEARING_MM3=15000.0` with `TRAY_RAIL_PANEL_PENETRATING_PATTERNS={("FRAME-RAIL-TRAY-", "PANEL-IN-")}`; gate after POST. Exclude TRAY from share_face bypass (union with ORG∪POST). Three regression tests mirror D-093 |
| Measured | Live transport: `FRAME-RAIL-TRAY-LOWER-L/R-001` ↔ `PANEL-IN-BOTTOM-001` **10237.5 mm³** each; ORG/MID/POST/open-front unchanged |
| Residual P2 | INTERLOCK-TAB↔PANEL-IN; BASE-REAR↔MAINS-INLET; COVER-SVC↔POST ~**123 mm³**; uncapped `MATING_PAIRS` |
| Key paths | `collision.py`; `tests/test_geometry.py`; `docs/14` §10a; `state/DECISION_LOG.md` D-094 |
| Verify | Adversarial accept; Quick 419 passed; Full `setup_windows.ps1` exit 0 |
| Explicitly NOT done | Gate pass; §F/§M/§N/§A closure; global penetrating ceiling; Path A geometry |

**Anti-false-conclusion:** 15000 mm³ ceiling is measured hygiene gate — live 10237.5 mm³ overlap is design intent, not proof of physical clearance at prototype.

### FIX-COLL-008-post-panel-penetrating-ceiling — POST↔PANEL-IN volume gate (D-093) — **closed cycle 1**

| | |
|---|---|
| Problem | `FRAME-POST-` ↔ `PANEL-IN-` in `PENETRATING_JOINT_PATTERNS` with no volume ceiling — deep burial silent-green; coplanar share_face bypass (ORG-only exclude from D-092) |
| Root cause | `is_penetrating_structural_joint()` gated ORG/MID/open-front only; `PANEL-IN-`/`FRAME-` `_share_face_if_prefix` returned True for POST↔PANEL-IN before penetrating check |
| Fix | `POST_PANEL_PENETRATING_MAX_BEARING_MM3=25000.0` with `POST_PANEL_PENETRATING_PATTERNS={("FRAME-POST-", "PANEL-IN-")}`; gate after MID_UPPER. Exclude POST from share_face bypass (union with ORG). Three regression tests mirror D-092 |
| Measured | Live transport: `FRAME-POST-RR/RL-001` ↔ `PANEL-IN-REAR-001` **18652.9 mm³** each; ORG/MID/open-front unchanged |
| Residual P2 | INTERLOCK-TAB↔PANEL-IN; BASE-REAR↔MAINS-INLET; COVER-SVC↔POST ~**123 mm³**; uncapped `MATING_PAIRS` |
| Key paths | `collision.py`; `tests/test_geometry.py`; `docs/14` §10a; `state/DECISION_LOG.md` D-093 |
| Verify | Adversarial accept; Quick 416 passed; Full `setup_windows.ps1` exit 0 |
| Explicitly NOT done | Gate pass; §F/§M/§N/§A closure; global penetrating ceiling; Path A geometry |

**Anti-false-conclusion:** 25000 mm³ ceiling is measured hygiene gate — live 18652.9 mm³ overlap is design intent, not proof of physical clearance at prototype.

### FIX-COLL-007-penetrating-joint-ceiling — per-class penetrating volume gates (D-092) — **closed cycle 2**

| | |
|---|---|
| Problem | Largest uncapped non–open-front `PENETRATING_JOINT_PATTERNS` allowed deep burial silent-green — no volume ceiling unlike D-080 open-front; cycle 1 left ORG-REAR coplanar share_face bypass |
| Root cause | `is_penetrating_structural_joint()` gated only open-front patterns (cycle 1); `PANEL-IN-`/`FRAME-` `_share_face_if_prefix` returned True before penetrating check for ORG-REAR (cycle 2 F-1) |
| Fix | **Cycle 1:** `ORG_REAR_PENETRATING_MAX_BEARING_MM3=35000.0` and `MID_UPPER_PENETRATING_MAX_BEARING_MM3=35000.0` with pattern frozensets; gate in `is_penetrating_structural_joint()`. **Cycle 2:** exclude ORG-REAR from `PANEL-IN-`/`FRAME-` `_share_face_if_prefix` bypass in `is_mating()`; coplanar-face burial regression |
| Measured | Live transport: ORG-REAR **31500 mm³**; SLIDE-UPPER ↔ MID **30712.5 mm³**; open-front live max **540 mm³** unchanged |
| Residual P2 | POST↔PANEL-IN max **18652.9 mm³** (closed D-093); INTERLOCK-TAB↔PANEL-IN; BASE-REAR↔MAINS-INLET; COVER-SVC↔POST ~**123 mm³**; uncapped `MATING_PAIRS` (SOFT↔TRAY, …) |
| Key paths | `collision.py`; `tests/test_geometry.py`; `docs/14` §10a; `state/DECISION_LOG.md` D-092 |
| Verify | Adversarial cycle 2 **accept**; Quick 413 passed; Full `setup_windows.ps1` exit 0 |
| Explicitly NOT done | Gate pass; §F/§M/§N/§A closure; global penetrating ceiling; Path A geometry |

**Anti-false-conclusion:** 35000 mm³ ceilings are measured hygiene gates — live volumes are below ceiling by design overlap, not proof of physical clearance at prototype.

### FIX-COLL-006-vib-equip-bearing-ceiling — VIB↔EQUIP pad volume gate (D-091)

| | |
|---|---|
| Problem | Eight `VIBMOUNT-P*` ↔ `EQUIP-PLOTTER*` pairs on `MATING_PAIRS` returned unconditional True — D-087 residual P2 hygiene gap |
| Root cause | `pair_key in MATING_PAIRS: return True` with no volume ceiling on VIB↔EQUIP subset |
| Fix | Add `is_vib_equip_bearing()` for eight tier-correct pairs (`VIB_EQUIP_MAX_BEARING_MM3=2500.0`; live exactly **2000 mm³** full pad embed) |
| Measured | Live transport: all eight pairs **2000.000 mm³**; no beyond-pad live burial (FALSE_ALARM C1) |
| Residual P2 | SOFT↔TRAY, INTERLOCK, shelf/org, media, mains, … on `MATING_PAIRS` remain uncapped |
| Key paths | `collision.py`; `tests/test_geometry.py`; `docs/14` §11 |
| Verify | Adversarial accept; Quick 408 passed; Full `setup_windows.ps1` exit 0 |
| Explicitly NOT done | Gate pass; §F/§M/§N/§A closure; beyond-pad burial claim |

**Anti-false-conclusion:** Do **not** treat the 2500 mm³ ceiling as evidence of live deep burial — live was exactly pad volume (2000 mm³). Fix is hygiene gate only.

### FIX-DOC-007-post-d089-advertising — sole-current envelope/mass/tip sync (D-090) — **closed cycle 1**

| | |
|---|---|
| Problem | README + docs/12 still advertised envelope H **529 mm** and stale mass/tip; HANDOFF Open list claimed **PLT-012 PASSING**; CSV PRD-006/PLT-001 cited 529 + old kg |
| Fix | Sync README, docs/12, HANDOFF current zones, CSV PRD-006/PLT-001/PLT-012/PLT-022 to live rev15 figures; regression tests pin advertising to live `case.height` / mass / tip |
| Live figures | Envelope **650×420×540 mm**; structural **9.651 kg**; all-parts **13.445 kg**; lower tip **3.828** |
| Key paths | `README.md`; `docs/12_PRODUCTION_RFQ_TEMPLATE.md`; `HANDOFF_PROMPT.md`; `state/REQUIREMENTS_TRACEABILITY.csv`; `tests/test_concept_revision_docs.py` |
| Verify | Adversarial accept; Quick 406 passed + ruff 0; A-017 tip → 3.828 (FIX-DOC-007b) |
| Explicitly NOT done | G-pass; PLT-012 PASSING; §F/§M/§N/§A closure |

### FIX-COLL-005-tray-slide-stack — Path A + door-base notch (D-089) — **closed cycle 2**

| | |
|---|---|
| Problem | Cycle 1 `DOOR_BASE_RAIL_MAX_BEARING_MM3=26000` silent-greened ~25650 mm³ open-door burial; TRAY↔SLIDE ~96525 mm³ pre-Path A |
| Fix | Path A slide on `tray_bounds[2]`; `TRAY_SLIDE_MAX_BEARING_MM3=500`; `_base_front_clearance_notch_x_z` + defensive bottom pocket; **26k removed**; full +11 mm stack (`lower_z` 41, `upper_z` 249, `case.height` 540, `handle_mount_z` 263) |
| Measured | Live TRAY↔SLIDE **0 mm³**; open-door ∩ BASE/BOTTOM **0 mm³**; open-door ↔ bottom **1.5 mm** air gap; loaded CoM Y **≈181.31 mm** → `handle_mount_y_mm` **181.3** (cycle 3) |
| Key paths | `trays.py`; `frame.py`; `panels.py`; `doors.py`; `collision.py`; `config/parameters.yaml`; `tests/`; `docs/14` §9/§11 |
| Verify | Adversarial cycle 2 **accept**; cycle 3 Quick **green**; F-1 sole-current doc sync (§F **OPEN**) |
| Explicitly NOT done | G-pass; §F/§M/§N/§A closure |
| HANDOFF | Current zones synced to 540 / Y=181.3 / Z=263 / intrusion ≈1,502,833.5 (FIX-DOC-006) |

### FIX-COLL-005-tray-slide-stack — Path A Z-stack (D-089) — cycle 1 (superseded by cycle 2)

| | |
|---|---|
| Problem | TRAY↔SLIDE live ~96525 mm³ burial; `is_mating` uncapped on `MATING_PAIRS` |
| Fix | Path A slide under tray; `TRAY_SLIDE_MAX_BEARING_MM3=500`; interim 26k door allowlist (**removed in cycle 2**) |
| Measured | Live TRAY↔SLIDE **0 mm³** transport + service_p1 (was ~96525 L/R) |
| Key paths | `trays.py`; `doors.py`; `collision.py`; `config/parameters.yaml`; `tests/`; `docs/14` §11 |
| Superseded | Cycle 2 — full +11 mm stack + door-base notch geometry; no deferral |

### FIX-DOC-005-rfq-fm-advertising — docs/12 §F/§M owner-blocker sync (D-088)

| | |
|---|---|
| Problem | `docs/12` §F advertised stale tier-2 intrusion ~1.39×10⁶ mm³; §M cited removed 210,600 mm³ lid/shuttle overlap (D-067) |
| Root cause | RFQ owner-blocker table not refreshed after D-084 handle Y retune and D-067 INTERLOCK removal |
| Fix | §F → ≈1,515,402 mm³ (≈1.52×10⁶) at Y=180.6; §M → transport headroom tier 1 **27 mm** / tier 2 **50 mm** vs **80 mm** provisional envelope; regression pin `test_rfq_owner_blocker_table_pins_live_blockers` |
| Key paths | `docs/12_PRODUCTION_RFQ_TEMPLATE.md`; `tests/test_concept_revision_docs.py`; `state/REQUIREMENTS_TRACEABILITY.csv` (PLT-008/PLT-019) |
| Verify | Adversarial accept; Quick ~400 passed + ruff 0; targeted docs pin tests pass |
| Explicitly NOT done | Gate pass; §F/§M/§N/§A closure; geometry/config changes |

**Anti-false-conclusion:** Do **not** treat updated RFQ blocker wording as resolved handle or lid headroom. All four owner blockers remain **OPEN**.

### FIX-COLL-004-mating-pairs-seating-ceiling — EQUIP seating volume gate (D-087)

| | |
|---|---|
| Problem | `is_mating()` returned unconditional True for all `MATING_PAIRS` — synthetic EQUIP↔TRAY deep burial (~1.22×10⁶ mm³) silent-green |
| Root cause | `pair_key in MATING_PAIRS: return True` with no volume ceiling on seating subset |
| Fix | Add `is_equip_seating_bearing()` for eight EQUIP-PLOTTER* ↔ TRAY-* / SLIDE-* pairs (`EQUIP_SEATING_MAX_BEARING_MM3=500.0`; live max **0 mm³**) |
| Measured | Live transport seating inter_vol **0 mm³** across four spot-checked pairs; synthetic burial > ceiling rejected |
| Residual P2 | SOFT↔TRAY, INTERLOCK, shelf/org, media, mains, … on `MATING_PAIRS` remain uncapped |
| Key paths | `collision.py`; `tests/test_geometry.py` (EQUIP↔TRAY/SLIDE burial + live transport spot-check); `docs/14` §11 |
| Verify | Adversarial accept; Quick 399 passed + ruff 0; Full `setup_windows.ps1` exit 0 |
| Explicitly NOT done | Gate pass; global MATING_PAIRS ceiling; uncapped P2 classes |

### FIX-COLL-003-kinematic-group-mates — delete blanket group `is_mating` (D-086)

| | |
|---|---|
| Problem | `is_mating()` returned True for any same kinematic-group pair with no `intersection_volume` ceiling — silent-green deep burial |
| Root cause | Blanket loop at `collision.py` 663–665 overrode `check_collision_pairs` clearance gate |
| Fix | Delete blanket; add `is_slide_vibmount_bearing()` for eight residual SLIDE↔VIBMOUNT plane-touch pairs (`SLIDE_VIBMOUNT_MAX_BEARING_MM3=500.0`; live max **0 mm³**) |
| Measured | Residual same-group non-MATING contacts: 8 SLIDE↔VIBMOUNT @ 0 mm³; EQUIP↔SOFTSTOP live clr=0.5 mm (not mated) |
| Key paths | `collision.py`; `tests/test_geometry.py` (EQUIP↔SOFTSTOP + SLIDE↔VIBMOUNT burial tests); `docs/14` §11 |
| Verify | Adversarial accept; Quick 395 passed + ruff 0; Full `setup_windows.ps1` exit 0 |
| Explicitly NOT done | Gate pass; MATING_PAIRS P2 expansion; TAB removal from kinematics groups |

### FIX-DOC-004-assumptions-rev15 — ASSUMPTIONS rev15 evidence sync (D-085)

| | |
|---|---|
| Problem | A-013/A-017 validation actions still cited rev13 evidence; A-014 still claimed bottom vents under modeled `AIRPATH-001` after D-071 removal |
| Root cause | Assumption register not refreshed after FIX-WAVE-004 / rev15 evidence and D-071 service-volume removal |
| Fix | A-013 → `output/validation/rev15/views/transport_*` (rev13 historical); A-017 → rev15 stability report + upper N/A (D-076/D-077); A-014 → panel through-cuts only, no current AIRPATH solid |
| Key paths | `state/ASSUMPTIONS.md`, `state/DECISION_LOG.md`, `state/AUTONOMOUS_STATUS.md` |
| Verify | `uv run ruff check state/ASSUMPTIONS.md` — exit 0 |
| Explicitly NOT done | Gate pass; §F/§M/§N/§A closure; geometry/config changes |

### FIX-COLL-002-door-mid-clearance — DOOR-LOWER ↔ PANEL-IN-MID burial (D-084)

| | |
|---|---|
| Problem | Live transport DOOR-LOWER ↔ PANEL-IN-MID-001 **5985 mm³** burial; `is_door_mate` unconditional True for MID/SOFTSTOP |
| Root cause | MID front Y at shadow gap (2.5 mm) protruded 12.5 mm ahead of closed door plane (15 mm); no volume ceiling on MID/SOFTSTOP mates |
| Fix | Path A: retract MID front Y to `datums.plotter1_physical.y.min_mm` (15.0 mm); cap MID/SOFTSTOP with `DOOR_FRONT_PLANE_MAX_BEARING_MM3 + threshold`; synthetic burial tests |
| Measured | Before **5985 mm³** → after **0 mm³** (plane touch); SOFTSTOP live vol=0 (predicate honesty) |
| Key paths | `collision.py`; `panels.py::_build_inner_mid_panel`; `tests/test_geometry.py` (mid/softstop door_mate tests); `docs/14` §9/§10 |
| Verify | Quick exit 0 — `-k "door_mate or open_front or mid or handle_mount"` + kinematics collision + full pytest + ruff |
| Explicitly NOT done | Gate pass; production-verified clearance claims |

### FIX-DOC-003-docs10-csv-rev15 — docs/10 + CSV rev15 sync (D-083)

| | |
|---|---|
| Problem | `docs/10_USER_INPUT_REQUIRED.md` §E/§F still cited stale Y=185.9 / ≈1.39×10⁶ mm³ as sole current; §H claimed MAINS-INLET placeholder solid retained; CSV rows still pointed at rev13 / 53-leaf REL-027 / 8.806 kg as current |
| Root cause | Documentation not refreshed after FIX-WAVE-004 / D-074 handle retune and D-071 service-volume removal |
| Fix | §E → Y=179.8 / ≈1,529,766 mm³ + margins 40.2/85.2; §F → ≈1.53×10⁶; §H → deferred/not modeled (D-036/D-071); CSV SWE/PLT/MFG/PRD/ELE rows → rev15 paths, CONCEPT_REVISION=15, REL-027=55, current mass 9.590/13.383 kg |
| Key paths | `docs/10_USER_INPUT_REQUIRED.md`, `state/REQUIREMENTS_TRACEABILITY.csv`, `state/DECISION_LOG.md`, `state/PROJECT_STATE.md` |
| Verify | Adversarial cycle-1 **approve** (findings=[]); Quick exit 0 — `uv run pytest tests/test_geometry.py -k handle_tier2_finger --tb=short -q`, `uv run pytest tests/test_concept_revision_docs.py`, full `uv run pytest`, `uv run ruff check .` |
| Explicitly NOT done | Gate pass; §F/§M/§N/§A closure; geometry/config changes |

### FIX-DOC-002-handoff-rev15 — HANDOFF product-truth sync (D-082)

| | |
|---|---|
| Problem | `HANDOFF_PROMPT.md` startup checklist, Product truth table, and Immediate mission still cited rev13 paths/numbers while live `CONCEPT_REVISION`=15 |
| Root cause | Documentation not refreshed after FIX-WAVE-004 / rev15 evidence and D-075…D-081 fix waves |
| Fix | Rewrite current zones to rev15 + D-075…D-081 truths; rephrase historical closed-list `CONCEPT_REVISION` lines; test scans current zones only. **Cycle 2:** drop stale 210600 lid/shuttle; tier-2 headroom 50 mm; §F intrusion ≈1,529,766 mm³; Open list in test scan. **Cycle 3:** PROJECT_STATE `## Current blockers` aligned (F-7 handle/headroom/transport/tip honesty) |
| Key paths | `HANDOFF_PROMPT.md`, `tests/test_concept_revision_docs.py` |
| Verify | Adversarial cycle-3 **approve**; Quick exit 0 — `uv run pytest tests/test_concept_revision_docs.py`, full `uv run pytest`, `uv run ruff check .` |
| Explicitly NOT done | Gate pass; §F/§M/§N/§A closure; geometry/config changes |

### FIX-TOOL-001-stage1-interlock-guard — `_stage1_metrics.py` KeyError (D-067)

| | |
|---|---|
| Problem | `scripts/_stage1_metrics.py` crashed on `parts["INTERLOCK-SHUTTLE-001"]` after D-067 removed interlock hardware |
| Root cause | Lid/shuttle intersection metrics assumed interlock always emitted |
| Fix | `.get()` guard; print `N/A (absent / D-067)` for P1/P2 lid vs shuttle when absent; volume print unchanged when present |
| Key paths | `scripts/_stage1_metrics.py` |
| Verify | `uv run python scripts/_stage1_metrics.py` + `uv run ruff check scripts/_stage1_metrics.py` — exit 0 |
| Explicitly NOT done | Interlock geometry restore; gate pass |

### FIX-COLL-001-open-front-ceiling — intersection-volume ceiling (D-080)

| | |
|---|---|
| Problem | `is_open_front_kinematic_contact` / front penetrating patterns exempted any clearance `< thr`, allowing deep burial to silent-green |
| Root cause | No intersection-volume upper bound on open-front skin bearing (unlike door F-1 / cavity-joint ceilings) |
| Fix | `OPEN_FRONT_MAX_BEARING_MM3=750.0` (live max **540 mm³**); gate open-front + four front clad/rail penetrating patterns; synthetic burial tests (open_front + penetrating) |
| Key paths | `collision.py`; `tests/test_geometry.py::test_open_front_kinematic_contact_rejects_volumetric_burial`; `tests/test_geometry.py::test_open_front_penetrating_rejects_volumetric_burial`; `docs/14` §10 |
| Verify | Targeted pytest `-k "open_front or door_mate or cavity_joint or collision"` + kinematics collision — pending adversarial/Quick |
| Explicitly NOT done | Gate pass; P2 door `PANEL-IN-MID` / `SOFTSTOP-*` unconditional True cap — **closed in FIX-COLL-002 (D-084)** |

**Anti-false-conclusion:** Green collision sweep ≠ physical clearance at prototype. Do **not** treat 750 mm³ ceiling as manufacturing sign-off.

### FIX-DOC-001-rfq-rev15 — RFQ/README advertising sync (D-079)

| | |
|---|---|
| Problem | `docs/12` and README **Current status** still advertised rev13 paths/numbers while live `CONCEPT_REVISION`=15 |
| Root cause | Documentation not refreshed after FIX-WAVE-004 / rev15 evidence generation |
| Fix | Subject + Attached package + indicative mass/tip table → rev15 evidence; MAINS-INLET honesty (D-071); regression test `tests/test_concept_revision_docs.py` |
| Key paths | `docs/12_PRODUCTION_RFQ_TEMPLATE.md`, `README.md`, `tests/test_concept_revision_docs.py` |
| Verify | `uv run pytest tests/test_concept_revision_docs.py -q` + Quick profile — exit 0 |
| Cycle 2 | F-1: fastener total **162** (drop dead D-069 base-clad M3); F-2: STACK-CAP **~0.118 kg** from rev15 CSV; F-3: REL-027 **55**; F-4: §N plotter tie-down waived |
| Explicitly NOT done | Gate pass; §F/§M/§N/§A closure; full HANDOFF rewrite |

**Anti-false-conclusion:** Do **not** treat indicative mass/tip figures as G4 sign-off. Do **not** re-open removed service-volume solids without owner decision.

## Open defect backlog (impact order)

1. Owner blockers unchanged: §F handle, §M lid headroom, §N retention, §A measurements.

## Where we are / next action

1. Land verified working tree (mega-commit + ordinary push) per owner approval.
2. Pick backlog **#1** (highest remaining impact), run confirmation (reproduce → counter → root → test → safety), then T2 plan/implement/adversarial/verify; commit only that cycle's paths when isolatable.
3. Prefer Quick mid-cycle; Full before stage-final commits.

## Protection rules (do not skip)

- Physical / tip / clearance / mass claims → **T2 min** + mandatory `adversarial-reviewer`.
- Green pytest ≠ physical correctness.
- Findings need path, lines, requirement ID, reproducible evidence.
- Never mark G0–G8 passed or production-ready.
- Never invent equipment/load/thermal/bend data.
- Always `uv run` (not bare `python`).
- Subagent DROP/WEAKEN must be weighed; Main may keep an honesty fix when publish+gate mislead even if math sentinel is intentional.

## Commands

| Profile | Command |
|---|---|
| Quick | `uv run pytest` and `uv run ruff check .` |
| Full | `powershell -ExecutionPolicy Bypass -File .\scripts\setup_windows.ps1` |
| Tip smoke | `uv run pytest tests/test_geometry.py -k "tip_factor or stability_split" --tb=short` |
| Regen reports | `uv run python scripts/generate_mass_report.py` |

## Update log

| When | Change |
|---|---|
| 2026-08-08 | Created. FIX-TIP-001 done in WT; mega-commit authorized; backlog listed. |
| 2026-08-08 | FIX-MASS-001 closed (D-078); backlog #2 removed; header honesty test added. |
| 2026-08-08 | FIX-COLL-001 closed (D-080); open-front volume ceiling 750 mm³; backlog #1 narrowed to door PANEL-IN-MID/SOFTSTOP P2. |
| 2026-08-08 | FIX-TOOL-001 closed (D-081); `_stage1_metrics.py` interlock N/A guard; backlog #2 removed. |
| 2026-08-08 | FIX-COLL-002 closed (D-084); DOOR-LOWER↔MID 5985→0 mm³; P2 MID/SOFTSTOP backlog cleared. |
| 2026-08-08 | FIX-DOC-003 closed (D-083); docs/10 §E/§F/§H + CSV current-evidence → rev15; backlog #2 (CSV rev13 pointers) removed. |
| 2026-08-08 | FIX-DOC-002 closed (D-082); HANDOFF current zones → rev15; backlog #3 (HANDOFF product-truth) removed. |
| 2026-08-08 | FIX-DOC-002 cycle 3: PROJECT_STATE Current blockers honesty (F-7/F-8/F-9). |
| 2026-08-08 | FIX-DOC-004 closed (D-085); A-013/A-017 → rev15 evidence; A-014 AIRPATH honesty (D-071). |
| 2026-08-08 | FIX-COLL-003 closed (D-086); kinematic-group blanket deleted; SLIDE↔VIBMOUNT ceiling 500; Full green. |
| 2026-08-08 | FIX-COLL-004 closed (D-087); EQUIP seating MATING_PAIRS volume gate 500; residual uncapped P2 noted; Full green. |
| 2026-08-08 | FIX-DOC-005 closed (D-088); docs/12 §F/§M owner blockers → sole-current intrusion/headroom; stale 1.39×10⁶ / 210600 lid/shuttle pin. |
| 2026-08-08 | FIX-COLL-005 closed (D-089); Path A tray↔slide Z-stack; live 96525→0; ceiling 500; envelope 540; handle Y=181.3; Full green. |
| 2026-08-08 | FIX-DOC-006 HANDOFF current zones → D-089 (540 / 181.3 / 263 / intrusion 1,502,833.5). |
| 2026-08-08 | FIX-DOC-007 closed (D-090); README/docs/12/HANDOFF/CSV advertising → 540 / 9.651 / 13.445 / 3.828; PLT-012 PASSING claim removed. |
| 2026-08-08 | FIX-DOC-007b closed; A-017 tip validation action → **≈3.828** (residual D-090). |
| 2026-08-08 | FIX-COLL-006 closed (D-091); VIB↔EQUIP hygiene ceiling 2500 (live pad 2000); Full green. |
| 2026-08-08 | FIX-COLL-008 closed (D-093); POST↔PANEL-IN ceiling 25000; share_face ORG∪POST; Full green. |
| 2026-08-08 | FIX-COLL-007 closed (D-092); ORG/MID ceilings 35000; share_face bypass closed; Full green. |
| 2026-08-08 | FIX-COLL-009 closed (D-094); TRAY-rail↔PANEL-IN ceiling 15000; share_face ORG∪POST∪TRAY; Full green. |
| 2026-08-08 | FIX-COLL-012 closed (D-097); staggered-tier ceiling 500 mm³; Full green. |
| 2026-08-08 | FIX-COLL-011 closed (D-096); COVER↔FRAME BASE/POST ceilings 10000/500; Full green. |
| 2026-08-08 | FIX-COLL-013 closed (D-098); cross-tier TRAY/SLIDE↔rail share_face exclude; Full green. |
| 2026-08-08 | FIX-HONESTY-001 closed (D-099); prune zombie INTERLOCK/MAINS/… allowlists; Full green. |
| 2026-08-08 | FIX-DOC-008 closed (D-100); CSV SWE-001/003 stop advertising stale 345 pytest. |
