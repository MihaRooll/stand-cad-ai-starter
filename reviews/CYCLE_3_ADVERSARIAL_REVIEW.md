# Cycle 3 — adversarial release review

Date: 2026-08-03

## Review question

Could a capable autonomous agent misread this starter, produce plausible files, and accidentally claim that a real hot/heavy/mobile stand is ready for manufacture?

## Adversarial findings and resolutions

### 1. Starter completeness could be mistaken for hardware readiness

**Risk:** a polished repository looks like a finished design.

**Resolution:** top-level Russian/English notices distinguish the software starter from real geometry. Gate G1 explicitly blocks fit-dependent modeling and Gate G6 blocks prototype fabrication.

### 2. An MCP persistent session could become an invisible second source

**Risk:** geometry looks correct in-session but cannot be reproduced after restart.

**Resolution:** the saved Python generator plus approved config is the only source of truth. Every accepted experiment must be persisted and regenerated outside the session.

### 3. A second CAD agent/tool could silently diverge

**Risk:** two plausible STEP files with no authoritative lineage.

**Resolution:** one geometry pipeline and one production writer at a time. Optional viewers/skills may inspect or advise, but geometry changes return to canonical source.

### 4. Sheet-metal rules were initially unconditional

**Risk:** projects based on profiles, welded tube, machined panels, or plywood would be blocked by irrelevant bend data; alternatively, bent parts could bypass factory calibration.

**Resolution:** bend-data and flat-pattern-owner gates apply only when `uses_bent_sheet_metal=true`. DFM is still required for every production release.

### 5. Neutral STEP may be mistaken for native editable sheet metal

**Risk:** downstream constructor expects feature history or reliable automatic unfolding.

**Resolution:** handoff documentation states the feature-history limitation and requires explicit ownership of any vendor-native rebuilt derivative.

### 6. Candidate model names could be treated as verified equipment

**Risk:** internet data for a similar revision is used for fit-critical geometry.

**Resolution:** production validation requires exact model, manufacturer, provenance, verification flags, operating/service/support/transport evidence, and transport orientation. Synthetic demo inputs cannot be released.

### 7. Release labels could be inconsistent with configuration

**Risk:** a non-production config claims `prototype` or a series package lacks a prototype record.

**Resolution:** fail-closed rules enforce `release_kind=none` outside production, controlled project ID/revision for production, and a prototype-inspection record for series.

### 8. Version drift could make geometry non-reproducible

**Risk:** an unpinned dependency changes modeling/export behavior.

**Resolution:** Python 3.12, `build123d 0.11.1`, and `build123d-mcp 0.3.81` are pinned. Upgrades require a dedicated branch, tests, smoke model, and geometry comparison.

### 9. Generated binary history could become untraceable

**Risk:** Git repository grows uncontrollably or a release cannot be tied to source.

**Resolution:** routine generated output is ignored. Controlled release manifests must retain checksums, revision, source/config paths, generator commit, approval, and date. Git LFS or external binary storage must be decided before real review/release packages are added.

### 10. Valid geometry could conceal mechanical, thermal, or electrical danger

**Risk:** CAD checks pass while the stand tips, overloads a shelf/caster, overheats, damages cables, or exposes unsafe power distribution.

**Resolution:** separate engineering and physical evidence gates cover load path, deflection, tipping, dynamic transport, thermal test, cable/earthing review, pinch/hot zones, and prototype inspection. Competent-person review is required where risk warrants it.

### 11. Vendor website evidence could be read as a recommendation

**Risk:** the user selects a supplier without price/quality/reputation comparison.

**Resolution:** source notes label vendor pages as capability/file-format evidence only. Vendor selection requires an authorized RFQ and comparison.

### 12. Repository data could be syntactically present but structurally broken

**Risk:** malformed traceability CSV, stale setup commands, or generated junk defeats agent resumption.

**Resolution:** traceability CSV was normalized and receives a rectangular-schema test. Lint, pytest, input validation, smoke STEP, package manifest, and ZIP integrity checks are mandatory before archive handoff.

## Residual risks deliberately not hidden

- Real equipment and site evidence is still absent.
- The Windows-native Cursor/MCP path must be re-run on the user's machine; Linux container checks do not prove Windows rendering/launch behavior.
- No target manufacturer has reviewed the design because there is no design or authorization to contact one.
- No structural, stability, thermal, electrical, or transport claim has yet been made or verified.
- Upstream MCP is a third-party dependency and should be re-reviewed before future upgrades or remote/HTTP use.

## Cycle result

PASS for release of the **software/specification starter archive** after all final checks pass. BLOCKED for real stand geometry at Gate G1 and BLOCKED for fabrication at Gate G6.
