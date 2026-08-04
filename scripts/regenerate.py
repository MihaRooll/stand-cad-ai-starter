#!/usr/bin/env python3
"""Regenerate concept STEP + mesh bundle and validation view evidence pack."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from stand_cad.geometry.export import CONCEPT_REVISION, DEFAULT_STEP_NAME, generate_concept_model

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PARAMETERS = REPO_ROOT / "config" / "parameters.yaml"
DEFAULT_CONCEPT_DIR = REPO_ROOT / "output" / "concept"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "output" / "validation" / f"rev{CONCEPT_REVISION}" / "views"
CONCEPT_STEM = f"light_plotter_tower_ASSEMBLY_CONCEPT_REFERENCE_ONLY_rev{CONCEPT_REVISION}"


def main() -> None:
    print(f"Regenerating revision rev{CONCEPT_REVISION} from {DEFAULT_PARAMETERS}")

    concept_result = generate_concept_model(
        parameters_path=DEFAULT_PARAMETERS,
        output_dir=DEFAULT_CONCEPT_DIR,
        step_name=DEFAULT_STEP_NAME,
    )
    print(f"STEP: {concept_result['step_path']} ({concept_result['part_count']} parts)")

    render_script = REPO_ROOT / "scripts" / "render_validation_views.py"
    proc = subprocess.run(
        [sys.executable, str(render_script)],
        cwd=str(REPO_ROOT),
        check=False,
    )
    if proc.returncode != 0:
        raise SystemExit(proc.returncode)

    # Collect written paths for handoff output.
    view_paths = sorted(DEFAULT_OUTPUT_DIR.glob("*"))
    mesh_paths = {
        "stl": DEFAULT_CONCEPT_DIR / f"{CONCEPT_STEM}.stl",
        "glb": DEFAULT_CONCEPT_DIR / f"{CONCEPT_STEM}.glb",
        "manifest": DEFAULT_CONCEPT_DIR / f"{CONCEPT_STEM}.manifest.json",
    }

    print(f"\nRevision: rev{CONCEPT_REVISION}")
    print("Artifacts written:")
    print(concept_result["step_path"])
    for path in view_paths:
        print(path)
    for label, path in mesh_paths.items():
        if path.is_file():
            print(f"{label}: {path}")


if __name__ == "__main__":
    main()
