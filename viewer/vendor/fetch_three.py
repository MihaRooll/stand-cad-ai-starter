#!/usr/bin/env python3
"""Download pinned three.js 0.170.0 modules into viewer/vendor/ (offline viewer)."""

from __future__ import annotations

import urllib.request
from pathlib import Path

VERSION = "0.170.0"
BASE = f"https://unpkg.com/three@{VERSION}"

FILES = [
    "build/three.module.js",
    "examples/jsm/loaders/GLTFLoader.js",
    "examples/jsm/controls/OrbitControls.js",
    "examples/jsm/utils/BufferGeometryUtils.js",
]

VENDOR_ROOT = Path(__file__).resolve().parent / f"three@{VERSION}"


def fetch_all() -> list[tuple[str, int]]:
    results: list[tuple[str, int]] = []
    for rel in FILES:
        url = f"{BASE}/{rel}"
        dest = VENDOR_ROOT / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        try:
            with urllib.request.urlopen(url, timeout=120) as resp:
                data = resp.read()
        except OSError as exc:
            raise SystemExit(f"FAILED {url}: {exc}") from exc
        dest.write_bytes(data)
        results.append((str(dest.relative_to(VENDOR_ROOT.parent.parent)), len(data)))
        print(f"OK {len(data):>10} bytes  {dest}")
    return results


if __name__ == "__main__":
    fetch_all()
