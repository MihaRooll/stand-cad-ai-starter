# Assumption register

An assumption is not a fact. Give every assumption an owner, validation action, and expiry gate.

| ID | Assumption | Impact if wrong | Validation action | Must resolve by | Status |
|---|---|---|---|---|---|
| A-001 | Windows 11 native is available for Cursor/CAD tooling | Setup changes | Verify in Phase 0 | G0 | Open |
| A-002 | At least one selected Moscow-region manufacturer can accept formed STEP + PDF for DFM | Handoff redesign | RFQ capability check | G5 | Open |
| A-003 | The stand is intended for event transport and operation | Requirements change | User confirms workflow | G1 | Open |
| A-004 | Existing yellow/black and orange/grey concepts are appearance references only | Visual direction changes | User selects direction | G2 | Open |
| A-005 | Imported `.cursor/` orchestration harness will be committed to version control | Harness lost on clone or not shared with collaborators | User confirms commit or documents exclusion | Phase 0 close | Open |
| A-006 | MCP session connectivity will be restored so the mandated build/measure/render workflow can be used | Geometry work would stall or be tempted onto a second, prohibited geometry pipeline | User enables `build123d-mcp` for this project and reloads MCP configuration in Cursor; confirm session tool search returns build123d-mcp tools | G0 | Closed |
| A-007 | MCP tool catalog is observable in-session (38 tools, `serverStatus: ready`) but no repository rule, test, or workflow content yet depends on build123d-mcp tool semantics because none has been exercised beyond listing | Premature rules or tests would encode unverified tool behaviour | Exercise MCP tools in-session before authoring MCP-dependent rules or tests | G0 | Open |
