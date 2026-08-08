#!/usr/bin/env python3
"""Serve the repository root for the static GLB viewer."""

from __future__ import annotations

import argparse
import errno
import json
import re
import socketserver
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler
from pathlib import Path

HOST = "127.0.0.1"
PORT = 8000
MAX_PORT_CANDIDATES = 20
REPO_ROOT = Path(__file__).resolve().parents[1]
CONCEPT_DIR = REPO_ROOT / "output" / "concept"
MODELS_JSON_PATH = "/viewer/models.json"
RELOAD_STATUS_PATH = "/viewer/reload-status"
REV_PATTERN = re.compile(r"_rev(\d+)\.manifest\.json$", re.IGNORECASE)

# Shared watch state (updated by background poller when --watch is active).
_watch_lock = threading.Lock()
_watch_state: dict = {
    "revision": None,
    "manifest_file": None,
    "glb_file": None,
    "manifest_mtime_ns": None,
    "glb_mtime_ns": None,
    "concept_dir_mtime_ns": None,
}


def ensure_three_vendor() -> None:
    """Download pinned three.js modules if viewer/vendor is incomplete."""
    vendor_marker = (
        REPO_ROOT
        / "viewer"
        / "vendor"
        / "three@0.170.0"
        / "build"
        / "three.module.js"
    )
    if vendor_marker.is_file() and vendor_marker.stat().st_size > 0:
        return
    fetch_script = REPO_ROOT / "viewer" / "vendor" / "fetch_three.py"
    if not fetch_script.is_file():
        raise SystemExit(f"Missing vendor fetch script: {fetch_script}")
    print("Vendored three.js incomplete — downloading three@0.170.0 …")
    subprocess.run(
        [sys.executable, str(fetch_script)],
        cwd=str(REPO_ROOT),
        check=True,
    )


def _revision_from_name(name: str) -> int:
    match = REV_PATTERN.search(name)
    return int(match.group(1)) if match else -1


def _newest_concept_pair() -> tuple[Path | None, Path | None, int]:
    """Return (manifest_path, glb_path, revision) for the newest concept revision."""
    best_rev = -1
    best_manifest: Path | None = None
    best_glb: Path | None = None
    if not CONCEPT_DIR.is_dir():
        return None, None, -1
    for manifest_path in CONCEPT_DIR.glob("*.manifest.json"):
        rev = _revision_from_name(manifest_path.name)
        try:
            payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        glb_name = payload.get("glb_file") or manifest_path.name.replace(
            ".manifest.json", ".glb"
        )
        glb_path = CONCEPT_DIR / glb_name
        if not glb_path.is_file():
            continue
        if rev >= best_rev:
            best_rev = rev
            best_manifest = manifest_path
            best_glb = glb_path
    return best_manifest, best_glb, best_rev


def _concept_dir_mtime_ns() -> int:
    if not CONCEPT_DIR.is_dir():
        return 0
    latest = 0
    for path in CONCEPT_DIR.iterdir():
        if path.is_file():
            latest = max(latest, path.stat().st_mtime_ns)
    return latest


def snapshot_reload_status() -> dict:
    """Build reload-status payload from current output/concept/ mtimes."""
    manifest_path, glb_path, revision = _newest_concept_pair()
    if manifest_path is None or glb_path is None:
        return {
            "revision": None,
            "manifest_file": None,
            "glb_file": None,
            "manifest_mtime_ns": None,
            "glb_mtime_ns": None,
            "concept_dir_mtime_ns": _concept_dir_mtime_ns(),
        }
    return {
        "revision": revision,
        "manifest_file": manifest_path.name,
        "glb_file": glb_path.name,
        "manifest_mtime_ns": manifest_path.stat().st_mtime_ns,
        "glb_mtime_ns": glb_path.stat().st_mtime_ns,
        "concept_dir_mtime_ns": _concept_dir_mtime_ns(),
    }


def _refresh_watch_state() -> dict:
    status = snapshot_reload_status()
    with _watch_lock:
        _watch_state.update(status)
    return status


def _watch_poll_loop(interval: float) -> None:
    while True:
        _refresh_watch_state()
        time.sleep(interval)


def build_models_index() -> dict:
    models: list[dict] = []
    if CONCEPT_DIR.is_dir():
        for manifest_path in sorted(CONCEPT_DIR.glob("*.manifest.json")):
            try:
                payload = json.loads(manifest_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            glb_name = payload.get("glb_file") or manifest_path.name.replace(
                ".manifest.json", ".glb"
            )
            glb_path = CONCEPT_DIR / glb_name
            if not glb_path.is_file():
                continue
            models.append(
                {
                    "revision": _revision_from_name(manifest_path.name),
                    "manifest_file": manifest_path.name,
                    "manifest_url": f"/output/concept/{manifest_path.name}",
                    "glb_file": glb_name,
                    "glb_url": f"/output/concept/{glb_name}",
                    "part_count": payload.get("part_count"),
                    "bbox_size_mm": payload.get("bbox_size_mm"),
                }
            )
    models.sort(key=lambda item: (item["revision"], item["manifest_file"]), reverse=True)
    return {"models": models, "default_manifest_url": models[0]["manifest_url"] if models else None}


class RepositoryHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(REPO_ROOT), **kwargs)

    def do_GET(self) -> None:  # noqa: N802
        route = self.path.split("?", 1)[0]
        if route == MODELS_JSON_PATH:
            body = json.dumps(build_models_index(), indent=2).encode("utf-8")
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)
            return
        if route == RELOAD_STATUS_PATH:
            with _watch_lock:
                payload = dict(_watch_state)
            if payload.get("manifest_file") is None:
                payload = snapshot_reload_status()
            body = json.dumps(payload, indent=2).encode("utf-8")
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)
            return
        super().do_GET()


def _fetch(url: str) -> tuple[int, int]:
    with urllib.request.urlopen(url, timeout=30) as resp:
        data = resp.read()
        return resp.status, len(data)


def _should_try_next_port(exc: OSError) -> bool:
    if exc.errno == errno.EADDRINUSE:
        return True
    winerror = getattr(exc, "winerror", None)
    return winerror in (10048, 10013)


def _bind_tcp_server(host: str, requested_port: int) -> tuple[socketserver.TCPServer, int]:
    """Bind TCPServer, trying requested_port .. requested_port+MAX_PORT_CANDIDATES-1."""
    socketserver.TCPServer.allow_reuse_address = True
    candidates = range(requested_port, requested_port + MAX_PORT_CANDIDATES)
    last_error: OSError | None = None
    for port in candidates:
        try:
            httpd = socketserver.TCPServer((host, port), RepositoryHandler)
        except OSError as exc:
            if not _should_try_next_port(exc):
                raise
            last_error = exc
            continue
        if port != requested_port:
            print(f"Port {requested_port} unavailable — using {port} instead.")
        return httpd, port
    tried = ", ".join(str(p) for p in candidates)
    detail = f" ({last_error})" if last_error else ""
    raise SystemExit(
        f"Could not bind to any port on {host} (tried: {tried}){detail}"
    )


def verify_viewer(base_url: str | None = None, *, port: int = PORT) -> int:
    ensure_three_vendor()
    base = base_url or f"http://{HOST}:{port}"
    index = build_models_index()
    if not index["models"]:
        print("VERIFY FAIL: no concept models under output/concept/")
        return 1

    newest = index["models"][0]
    urls = [
        f"{base}/viewer/index.html",
        f"{base}/viewer/vendor/three@0.170.0/build/three.module.js",
        f"{base}/viewer/vendor/three@0.170.0/examples/jsm/loaders/GLTFLoader.js",
        f"{base}/viewer/vendor/three@0.170.0/examples/jsm/controls/OrbitControls.js",
        f"{base}/viewer/vendor/three@0.170.0/examples/jsm/utils/BufferGeometryUtils.js",
        f"{base}{MODELS_JSON_PATH}",
        f"{base}{newest['manifest_url']}",
        f"{base}{newest['glb_url']}",
    ]

    print(f"Verifying viewer at {base} (newest: {newest['glb_file']})")
    for url in urls:
        try:
            status, nbytes = _fetch(url)
        except urllib.error.URLError as exc:
            print(f"VERIFY FAIL {url}: {exc}")
            return 1
        if status != 200 or nbytes <= 0:
            print(f"VERIFY FAIL {url}: HTTP {status}, {nbytes} bytes")
            return 1
        print(f"OK {nbytes:>10} bytes  {url}")
    return 0


def _run_verify_with_ephemeral_server(port: int = PORT) -> int:
    ensure_three_vendor()
    httpd, bound_port = _bind_tcp_server(HOST, port)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    time.sleep(0.3)
    try:
        return verify_viewer(f"http://{HOST}:{bound_port}")
    finally:
        httpd.shutdown()
        httpd.server_close()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Fetch-check viewer assets over HTTP, then exit.",
    )
    parser.add_argument(
        "--verify-only-running",
        action="store_true",
        help="Verify against an already-running server on the default port.",
    )
    parser.add_argument(
        "--watch",
        action="store_true",
        help=(
            "Poll output/concept/ mtimes and expose /viewer/reload-status for live reload "
            "(viewer/index.html polls every ~2s)."
        ),
    )
    parser.add_argument(
        "--watch-interval",
        type=float,
        default=1.0,
        help="Concept directory poll interval in seconds when --watch is set (default: 1.0).",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=PORT,
        help=f"TCP port to bind (default: {PORT}; tries successive ports if unavailable).",
    )
    args = parser.parse_args()

    if args.verify_only_running:
        raise SystemExit(verify_viewer(port=args.port))

    if args.verify:
        raise SystemExit(_run_verify_with_ephemeral_server(args.port))

    ensure_three_vendor()
    if args.watch:
        _refresh_watch_state()
        poll_thread = threading.Thread(
            target=_watch_poll_loop,
            args=(args.watch_interval,),
            daemon=True,
        )
        poll_thread.start()
    httpd, bound_port = _bind_tcp_server(HOST, args.port)
    url = f"http://{HOST}:{bound_port}/viewer/index.html"
    print(f"Serving repository root at {url}")
    print(f"Concept model index: http://{HOST}:{bound_port}{MODELS_JSON_PATH}")
    if args.watch:
        print(f"Live reload status: http://{HOST}:{bound_port}{RELOAD_STATUS_PATH}")
        print(f"Polling {CONCEPT_DIR} every {args.watch_interval}s")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down.")
    finally:
        httpd.server_close()


if __name__ == "__main__":
    main()
