#!/usr/bin/env python3
"""Environment doctor — pass/fail checks with plain-English remedies."""

from __future__ import annotations

import importlib.metadata
import os
import re
import shutil
import socket
import subprocess
import urllib.error
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
CONCEPT_DIR = REPO_ROOT / "output" / "concept"
PYPROJECT = REPO_ROOT / "pyproject.toml"
VENDOR_DIR = REPO_ROOT / "viewer" / "vendor" / "three@0.170.0"
VIEWER_PORT = 8000
VIEWER_HOST = "127.0.0.1"
WSL_CHDIR_SIGNATURE = "chdir(/mnt/c/"
MIN_VENDOR_BYTES = 10_000


class CheckResult:
    def __init__(self, name: str, passed: bool, detail: str, remedy: str = "") -> None:
        self.name = name
        self.passed = passed
        self.detail = detail
        self.remedy = remedy


def _run(cmd: list[str], *, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=str(cwd or REPO_ROOT),
        capture_output=True,
        text=True,
        check=False,
    )


def check_uv() -> CheckResult:
    uv = shutil.which("uv")
    if not uv:
        return CheckResult(
            "uv",
            False,
            "uv not found on PATH",
            "Install uv from https://docs.astral.sh/uv/ and ensure it is on PATH, "
            "then reopen the terminal.",
        )
    proc = _run([uv, "--version"])
    if proc.returncode != 0:
        return CheckResult(
            "uv",
            False,
            proc.stderr.strip() or "uv --version failed",
            "Reinstall uv or repair the installation; then run `uv --version` manually.",
        )
    return CheckResult("uv", True, proc.stdout.strip())


def check_python() -> CheckResult:
    py_snippet = (
        "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
    )
    proc = _run(["uv", "run", "python", "-c", py_snippet])
    if proc.returncode != 0:
        return CheckResult(
            "python",
            False,
            proc.stderr.strip() or "uv run python failed",
            "Run `uv sync` in the repository root to install the pinned Python 3.12 environment.",
        )
    version = proc.stdout.strip()
    if version != "3.12":
        return CheckResult(
            "python",
            False,
            f"Project Python is {version}, expected 3.12",
            "Run `uv sync` in the repository root; "
            "never use bare `python` (PATH may resolve to 3.11).",
        )
    return CheckResult("python", True, f"Python {version} via uv")


def check_repo_root() -> CheckResult:
    markers = [
        REPO_ROOT / "pyproject.toml",
        REPO_ROOT / "AGENTS.md",
        REPO_ROOT / "config" / "parameters.yaml",
    ]
    missing = [str(p.relative_to(REPO_ROOT)) for p in markers if not p.is_file()]
    if missing:
        return CheckResult(
            "repo root",
            False,
            f"Missing markers: {', '.join(missing)} (cwd={Path.cwd()})",
            f"Change directory to the repository root ({REPO_ROOT}) "
            "before running project commands.",
        )
    try:
        test_file = REPO_ROOT / "config" / "parameters.yaml"
        test_file.read_text(encoding="utf-8", errors="strict")[:1]
    except OSError as exc:
        return CheckResult(
            "repo root",
            False,
            f"Cannot read repository files: {exc}",
            "Ensure the working directory is the repository root and the drive is accessible.",
        )
    return CheckResult("repo root", True, f"Reachable at {REPO_ROOT}")


def check_pytest_collect() -> CheckResult:
    proc = _run(["uv", "run", "pytest", "--collect-only", "-q"])
    if proc.returncode != 0:
        tail = (proc.stderr or proc.stdout).strip().splitlines()[-3:]
        return CheckResult(
            "pytest collect",
            False,
            "\n".join(tail) or "pytest --collect-only failed",
            "Run `uv sync`, then `uv run pytest --collect-only` "
            "and fix import or dependency errors.",
        )
    lines = [ln for ln in proc.stdout.splitlines() if "test" in ln.lower()]
    summary = lines[-1] if lines else "collection succeeded"
    return CheckResult("pytest collect", True, summary)


def _pinned_build123d_version() -> str:
    text = PYPROJECT.read_text(encoding="utf-8")
    match = re.search(r'"build123d==([^"]+)"', text)
    if not match:
        raise RuntimeError("build123d pin not found in pyproject.toml")
    return match.group(1)


def check_build123d_pin() -> CheckResult:
    try:
        pinned = _pinned_build123d_version()
    except RuntimeError as exc:
        return CheckResult(
            "build123d pin",
            False,
            str(exc),
            "Restore the build123d pin in pyproject.toml.",
        )
    try:
        installed = importlib.metadata.version("build123d")
    except importlib.metadata.PackageNotFoundError:
        return CheckResult(
            "build123d pin",
            False,
            "build123d is not installed in the uv environment",
            "Run `uv sync` in the repository root.",
        )
    if installed != pinned:
        return CheckResult(
            "build123d pin",
            False,
            f"Installed build123d {installed}, expected pinned {pinned}",
            "Run `uv sync` to install the pinned build123d version.",
        )
    return CheckResult("build123d pin", True, f"build123d {installed} matches pin")


def check_concept_artifacts() -> CheckResult:
    from stand_cad.geometry.export import CONCEPT_REVISION, DEFAULT_STEP_NAME

    stem = f"light_plotter_tower_ASSEMBLY_CONCEPT_REFERENCE_ONLY_rev{CONCEPT_REVISION}"
    manifest = CONCEPT_DIR / f"{stem}.manifest.json"
    glb = CONCEPT_DIR / f"{stem}.glb"
    stl = CONCEPT_DIR / f"{stem}.stl"
    step = CONCEPT_DIR / DEFAULT_STEP_NAME
    if not CONCEPT_DIR.is_dir():
        return CheckResult(
            "concept artifacts",
            False,
            f"{CONCEPT_DIR} does not exist",
            "Run `uv run python scripts/regenerate.py` to generate "
            "concept STEP/STL/GLB/manifest files.",
        )
    missing = [
        path.name
        for path in (manifest, glb, stl, step)
        if not path.is_file()
    ]
    if missing:
        return CheckResult(
            "concept artifacts",
            False,
            f"Missing rev{CONCEPT_REVISION} artifacts: {', '.join(missing)}",
            "Run `uv run python scripts/regenerate.py` to export the current revision bundle.",
        )
    return CheckResult(
        "concept artifacts",
        True,
        f"rev{CONCEPT_REVISION} STEP/STL/GLB/manifest present under output/concept/",
    )


def check_three_vendor() -> CheckResult:
    required = [
        VENDOR_DIR / "build" / "three.module.js",
        VENDOR_DIR / "examples" / "jsm" / "loaders" / "GLTFLoader.js",
        VENDOR_DIR / "examples" / "jsm" / "controls" / "OrbitControls.js",
        VENDOR_DIR / "examples" / "jsm" / "utils" / "BufferGeometryUtils.js",
    ]
    missing = [str(p.relative_to(REPO_ROOT)) for p in required if not p.is_file()]
    tiny = [
        str(p.relative_to(REPO_ROOT))
        for p in required
        if p.is_file() and p.stat().st_size < MIN_VENDOR_BYTES
    ]
    if missing:
        return CheckResult(
            "three.js vendor",
            False,
            f"Missing: {', '.join(missing)}",
            "Run `uv run python viewer/vendor/fetch_three.py` or start `scripts/serve_viewer.py` "
            "(auto-downloads on first launch).",
        )
    if tiny:
        return CheckResult(
            "three.js vendor",
            False,
            f"Suspiciously small files (<{MIN_VENDOR_BYTES} B): {', '.join(tiny)}",
            "Delete viewer/vendor/three@0.170.0/ and run "
            "`uv run python viewer/vendor/fetch_three.py`.",
        )
    sizes = ", ".join(f"{p.name}={p.stat().st_size // 1024}KB" for p in required)
    return CheckResult("three.js vendor", True, sizes)


def _port_in_use(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.5)
        return sock.connect_ex((host, port)) == 0


def _is_our_viewer(base: str) -> bool:
    try:
        with urllib.request.urlopen(f"{base}/viewer/models.json", timeout=2) as resp:
            return resp.status == 200 and b'"models"' in resp.read(4096)
    except (urllib.error.URLError, OSError, TimeoutError):
        return False


def check_port_8000() -> CheckResult:
    base = f"http://{VIEWER_HOST}:{VIEWER_PORT}"
    if not _port_in_use(VIEWER_HOST, VIEWER_PORT):
        return CheckResult(
            "port 8000",
            True,
            "Port 8000 is free — ready for `uv run python scripts/serve_viewer.py --watch`",
        )
    if _is_our_viewer(base):
        return CheckResult(
            "port 8000",
            True,
            f"Port 8000 already serves this repository's viewer ({base}/viewer/index.html)",
        )
    return CheckResult(
        "port 8000",
        False,
        f"Port {VIEWER_PORT} is in use by another process (not our /viewer/models.json)",
        f"Stop the other service on port {VIEWER_PORT}, or run the viewer on a different port "
        "(not yet supported — free port 8000 first).",
    )


def check_wsl_chdir() -> CheckResult:
    """Probe for the WSL chdir(/mnt/c/...) failure signature.

    Probes (in order):
    1. ``os.getcwd()`` — if the cwd string contains the signature substring, fail immediately.
    2. ``Path.cwd().resolve()`` on the repository root — OSError message checked for the signature.
    3. ``os.chdir(REPO_ROOT)`` then restore prior cwd — OSError message checked for the signature.
    4. Subprocess ``uv run python -c "import os; os.chdir(r'...')"`` — combined stdout/stderr
       checked for the signature (mirrors shell-level chdir failures seen in mixed WSL sessions).
    """
    cwd = os.getcwd()
    if WSL_CHDIR_SIGNATURE in cwd:
        return CheckResult(
            "WSL chdir",
            False,
            f"Current cwd contains WSL failure signature: {cwd}",
            "Run `wsl --shutdown` in PowerShell, then restart the Cursor window.",
        )

    try:
        resolved = REPO_ROOT.resolve()
        _ = resolved.exists()
    except OSError as exc:
        if WSL_CHDIR_SIGNATURE in str(exc):
            return CheckResult(
                "WSL chdir",
                False,
                str(exc),
                "Run `wsl --shutdown` in PowerShell, then restart the Cursor window.",
            )

    prior = cwd
    try:
        os.chdir(REPO_ROOT)
        os.chdir(prior)
    except OSError as exc:
        if WSL_CHDIR_SIGNATURE in str(exc):
            return CheckResult(
                "WSL chdir",
                False,
                str(exc),
                "Run `wsl --shutdown` in PowerShell, then restart the Cursor window.",
            )

    proc = _run(
        [
            "uv",
            "run",
            "python",
            "-c",
            f"import os; os.chdir(r'{REPO_ROOT}'); print('ok')",
        ],
    )
    combined = (proc.stdout or "") + (proc.stderr or "")
    if WSL_CHDIR_SIGNATURE in combined:
        return CheckResult(
            "WSL chdir",
            False,
            combined.strip(),
            "Run `wsl --shutdown` in PowerShell, then restart the Cursor window.",
        )
    if proc.returncode != 0:
        return CheckResult(
            "WSL chdir",
            False,
            combined.strip() or "subprocess chdir probe failed",
            "Fix the underlying path or shell issue; if this is a WSL/Cursor mount glitch, "
            "run `wsl --shutdown` in PowerShell, then restart the Cursor window.",
        )

    return CheckResult("WSL chdir", True, "No chdir(/mnt/c/...) failure signature detected")


def run_all_checks() -> list[CheckResult]:
    return [
        check_uv(),
        check_python(),
        check_repo_root(),
        check_pytest_collect(),
        check_build123d_pin(),
        check_concept_artifacts(),
        check_three_vendor(),
        check_port_8000(),
        check_wsl_chdir(),
    ]


def main() -> None:
    print(f"Environment doctor — {REPO_ROOT}\n")
    results = run_all_checks()
    failed = 0
    for result in results:
        status = "PASS" if result.passed else "FAIL"
        print(f"[{status}] {result.name}: {result.detail}")
        if not result.passed:
            failed += 1
            print(f"         Remedy: {result.remedy}")
    print()
    if failed:
        print(f"{failed} check(s) failed.")
        raise SystemExit(1)
    print("All checks passed.")
    raise SystemExit(0)


if __name__ == "__main__":
    main()
