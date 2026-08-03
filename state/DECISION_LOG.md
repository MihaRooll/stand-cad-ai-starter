# Decision log

Use short entries for operational decisions. Create a new ADR for durable architectural or manufacturing decisions.

| Date | ID | Decision | Reason | Evidence | Status |
|---|---|---|---|---|---|
| 2026-08-03 | D-001 | Use AI-first build123d workflow with manufacturer sheet-metal finalization | Simplest Cursor-native path with controlled manufacturing boundary | ADR-001/003 | Accepted |
| 2026-08-03 | D-002 | Start Windows-native, not mixed WSL/Windows | Reduce subprocess/path/render variability | ADR-001 | Accepted |
| 2026-08-03 | D-003 | Do not write a custom MCP in Phase 0 | Existing MCP covers build/inspect/export loop | Architecture review | Accepted |

