"""Validate project/equipment TOML before any geometry generation."""

from __future__ import annotations

import argparse
import sys
import tomllib
from pathlib import Path

from stand_cad.schema import validate_documents


def load_toml(path: Path) -> dict:
    with path.open("rb") as handle:
        return tomllib.load(handle)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--equipment", type=Path, required=True)
    parser.add_argument("--allow-demo", action="store_true")
    args = parser.parse_args()

    issues = validate_documents(
        load_toml(args.project),
        load_toml(args.equipment),
        allow_demo=args.allow_demo,
    )
    for issue in issues:
        print(f"{issue.severity} {issue.code}: {issue.message}")

    errors = [issue for issue in issues if issue.severity == "ERROR"]
    if errors:
        print(f"Validation failed with {len(errors)} error(s).")
        return 1
    print("Validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

