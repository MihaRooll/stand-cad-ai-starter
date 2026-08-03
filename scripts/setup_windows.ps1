$ErrorActionPreference = "Stop"

if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    throw "uv is not installed or is not on PATH. Install it from https://docs.astral.sh/uv/getting-started/installation/ and open a new PowerShell window."
}

uv sync --extra dev
uv run python scripts/validate_inputs.py --project config/project.example.toml --equipment config/equipment.example.toml --allow-demo
uv run python scripts/smoke_model.py
uv run pytest
uv run ruff check .

Write-Host "Baseline complete. Restart Cursor and verify build123d-mcp in Settings > MCP."

