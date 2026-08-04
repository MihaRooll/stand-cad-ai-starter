# Initial risk register

| ID | Risk | Consequence | Initial severity | Required mitigation/evidence |
|---|---|---|---|---|
| R-001 | Wrong equipment variant or dimensions | Does not fit / unusable access | Critical | Exact model, manual, user measurement, envelope review |
| R-002 | High centre of mass / open drawer or press motion | Tip-over and injury | Critical | Worst-case CoM, stability analysis, deployment interlocks/restraints, prototype tip tests |
| R-003 | Under-rated casters or mounting | Collapse / runaway stand | Critical | **Caster half not applicable to current stationary desktop-tower configuration (2026-08-04):** no casters; feet instead (`hardware.foot_diameter_mm`). **Mounting half remains live:** foot/vibration-mount load path, load distribution, and physical tests |
| R-004 | Heat press/printer thermal interaction | Damage, fire, poor operation | Critical | Heat data, separation, airflow design, thermal test, qualified review |
| R-005 | Improper power distribution/earthing | Shock or fire | Critical | Qualified electrical design/review and testing |
| R-006 | Incorrect bend allowance/flat pattern | Scrap or assembly mismatch | High | Target-factory DFM and flat-pattern ownership before DXF release |
| R-007 | STEP interpreted as editable native design | Untracked vendor divergence | High | Explicit native-CAD responsibility and return-to-source process |
| R-008 | AI creates visually plausible invalid geometry | Fabrication error | High | Deterministic geometry checks plus visual and DFM review |
| R-009 | MCP/dependency update changes geometry | Silent revision drift | High | Version pins, lockfile, reference STEP regression, update branch |
| R-010 | Parallel agents edit same geometry | Conflicts / divergent source | High | One-writer rule and independent non-editing review |
| R-011 | Service/cable/moving zones omitted | Device cannot operate or be removed | High | Typed envelopes and workflow simulation |
| R-012 | Transport shock, tilt, ink/liquid constraints ignored | Equipment damage/leak | High | Exact transport requirements, levelling/restraint plan, prototype transport test |
| R-013 | Cosmetic coating masks threads/interfaces | Assembly/rework | Medium | Finish masking notes and first-article inspection |
| R-014 | Vendor selected only on price | Quality/schedule/process mismatch | High | Multi-factor RFQ/DFM comparison and prototype stage |
| R-015 | Prototype treated as series-ready | Repeated defects and cost | High | Separate prototype and series release gates/revisions |

Update likelihood, owner, status, and residual risk in the live project state once facts are available.

