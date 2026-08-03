# Project state

- Project: Mobile equipment stand/enclosure
- Current phase: Phase 0 — repository and toolchain baseline
- Current gate: G0
- Status: Native Windows toolchain verified; G0 exit-criteria evidence collected
- Last updated: 2026-08-03

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

### Equipment / user input

- Exact equipment selection for this stand.
- Verified equipment envelopes and masses.
- Operating/transport constraints.
- Budget, deadline, and final external-size constraints.

These equipment/user-input blockers block G1 and real geometry, not Phase 0 software implementation.

## Next decision

After G0 gate verdict (Human Gate), complete the consolidated input packet in `docs/10_USER_INPUT_REQUIRED.md` and start equipment envelopes only for verified selected models.
