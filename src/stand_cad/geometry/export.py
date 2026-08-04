"""STEP and mesh export helpers for CONCEPT/REFERENCE_ONLY artifacts."""

from __future__ import annotations

import json
from copy import copy
from pathlib import Path
from typing import Any

from build123d import Compound, export_gltf, export_step, export_stl, import_step

from stand_cad.geometry.assembly import (
    AssemblyState,
    build_operating_with_test_bodies_assembly,
    build_service_plotter_1_assembly,
    build_service_plotter_2_assembly,
    build_transport_assembly,
)
from stand_cad.geometry.primitives import bounding_box_bounds, bounding_box_size
from stand_cad.geometry.registry import PartRecord
from stand_cad.parameters import Parameters, load_parameters

CONCEPT_REVISION = 7
DEFAULT_STEP_NAME = (
    f"light_plotter_tower_ASSEMBLY_CONCEPT_REFERENCE_ONLY_rev{CONCEPT_REVISION}.step"
)


def build_all_states(params: Parameters) -> dict[str, AssemblyState]:
    """Build all four TZ section 13 assembly states."""
    return {
        "transport": build_transport_assembly(params),
        "service_plotter_1": build_service_plotter_1_assembly(params),
        "service_plotter_2": build_service_plotter_2_assembly(params),
        "operating_with_test_bodies": build_operating_with_test_bodies_assembly(params),
    }


def transport_compound(params: Parameters):
    """Transport-state compound for export."""
    return build_transport_assembly(params).compound()


def build_labeled_transport_compound(
    params: Parameters,
) -> tuple[AssemblyState, Compound, list[PartRecord]]:
    """Transport assembly with part_id labels on each solid for GLB export.

    build123d export_gltf propagates Shape.label to glTF node and mesh names,
    so the viewer can map meshes by name rather than fragile child order.
    """
    state = build_transport_assembly(params)
    records = list(state.parts.values())
    labeled_solids = []
    for record in records:
        solid = copy(record.solid)
        solid.label = record.part_id
        labeled_solids.append(solid)
    return state, Compound(children=labeled_solids), records


def write_glb_manifest(
    manifest_path: Path,
    *,
    glb_filename: str,
    compound: Compound,
    records: list[PartRecord],
    generated_from: str = "scripts/render_validation_views.py",
) -> None:
    """Write co-located manifest JSON for the interactive GLB viewer."""
    (x_bounds, y_bounds, z_bounds) = bounding_box_bounds(compound)
    size = bounding_box_size(compound)
    manifest: dict[str, Any] = {
        "generated_from": generated_from,
        "glb_file": glb_filename,
        "part_count": len(records),
        "bbox_min_mm": [x_bounds[0], y_bounds[0], z_bounds[0]],
        "bbox_max_mm": [x_bounds[1], y_bounds[1], z_bounds[1]],
        "bbox_size_mm": list(size),
        "parts": [
            {"index": index, "part_id": record.part_id, "material": record.material}
            for index, record in enumerate(records)
        ],
    }
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def export_transport_mesh_bundle(
    params: Parameters,
    output_dir: Path | str,
    *,
    stem: str,
    generated_from: str = "scripts/render_validation_views.py",
) -> dict[str, Path]:
    """Export transport STL, labeled GLB, and viewer manifest."""
    target_dir = Path(output_dir)
    target_dir.mkdir(parents=True, exist_ok=True)
    _state, labeled_compound, records = build_labeled_transport_compound(params)
    stl_path = target_dir / f"{stem}.stl"
    glb_path = target_dir / f"{stem}.glb"
    manifest_path = target_dir / f"{stem}.manifest.json"
    export_stl(labeled_compound, stl_path)
    export_gltf(labeled_compound, glb_path, binary=True)
    write_glb_manifest(
        manifest_path,
        glb_filename=glb_path.name,
        compound=labeled_compound,
        records=records,
        generated_from=generated_from,
    )
    return {"stl": stl_path, "glb": glb_path, "manifest": manifest_path}


def export_transport_step(params: Parameters, output_path: Path | str) -> Path:
    """Export transport assembly STEP."""
    target = Path(output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    export_step(transport_compound(params), target)
    return target


def measure_compound(compound) -> dict[str, tuple[float, float, float] | int | float]:
    """Return volume and bounding box metrics."""
    solids = getattr(compound, "solids", lambda: [])()
    return {
        "solid_count": len(solids),
        "volume_mm3": float(compound.volume),
        "bbox_size_mm": bounding_box_size(compound),
        "bbox_bounds_mm": bounding_box_bounds(compound),
    }


def read_back_step_metrics(
    step_path: Path | str,
) -> dict[str, tuple[float, float, float] | int | float]:
    """Import STEP and return metrics."""
    imported = import_step(str(step_path))
    return measure_compound(imported)


def generate_concept_model(
    parameters_path: Path | str = Path("config/parameters.yaml"),
    *,
    output_dir: Path | str = Path("output/concept"),
    step_name: str = DEFAULT_STEP_NAME,
) -> dict[str, object]:
    """Build all states, export transport STEP, return validation metrics."""
    params = load_parameters(parameters_path)
    states = build_all_states(params)
    step_path = Path(output_dir) / step_name
    export_transport_step(params, step_path)
    live_metrics = measure_compound(states["transport"].compound())
    readback_metrics = read_back_step_metrics(step_path)
    return {
        "parameters_path": str(parameters_path),
        "step_path": str(step_path),
        "part_count": len(states["transport"].parts),
        "live_metrics": live_metrics,
        "readback_metrics": readback_metrics,
        "states": list(states.keys()),
    }
