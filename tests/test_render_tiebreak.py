"""Regression tests for validation-view rasterizer depth tie-breaking."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import numpy as np

from stand_cad.geometry.assembly import AssemblyState
from stand_cad.geometry.primitives import box_from_bounds
from stand_cad.geometry.registry import PartRecord

REPO_ROOT = Path(__file__).resolve().parents[1]
_RENDER_MODULE_PATH = REPO_ROOT / "scripts" / "render_validation_views.py"


def _load_render_module():
    module_name = "render_validation_views"
    spec = importlib.util.spec_from_file_location(module_name, _RENDER_MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {_RENDER_MODULE_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


_COINCIDENT_BOUNDS = (0.0, 0.0, 0.0, 100.0, 100.0, 10.0)


def _coincident_clad_struct_parts() -> tuple[PartRecord, PartRecord]:
    structural = PartRecord(
        part_id="STRUCT-001",
        material="aluminium_angle_15x15x1.5",
        solid=box_from_bounds(*_COINCIDENT_BOUNDS),
    )
    cladding = PartRecord(
        part_id="CLAD-001",
        material="cast_opal_pmma_3mm",
        solid=box_from_bounds(*_COINCIDENT_BOUNDS),
    )
    return structural, cladding


def _assert_cladding_wins_coplanar_tiebreak(render, state: AssemblyState) -> None:
    view = render.ViewSpec(direction=(0.0, -1.0, 0.0))
    image = render._render_assembly_rgb(state, view, width=256, height=256)

    clad_rgb = np.array(render.MATERIAL_RGB["cast_opal_pmma_3mm"], dtype=np.uint8)
    struct_rgb = np.array(render.MATERIAL_RGB["aluminium_angle_15x15x1.5"], dtype=np.uint8)
    background = np.array([255, 255, 255], dtype=np.uint8)

    non_background = np.any(image != background, axis=2)
    assert np.any(non_background), "expected rendered geometry pixels"
    rendered = image[non_background]
    assert np.all(rendered == clad_rgb), "cladding material must win coplanar depth ties"
    assert not np.any(np.all(rendered == struct_rgb, axis=1)), (
        "structural material must not dominate overlapping region"
    )


def test_coplanar_cladding_wins_material_priority_tiebreak():
    """Structural part drawn first must not hide flush cladding at equal depth."""
    render = _load_render_module()
    structural, cladding = _coincident_clad_struct_parts()
    state = AssemblyState(
        name="coplanar_clad_tiebreak",
        parts={
            structural.part_id: structural,
            cladding.part_id: cladding,
        },
    )
    _assert_cladding_wins_coplanar_tiebreak(render, state)


def test_coplanar_cladding_wins_material_priority_tiebreak_reverse_insertion_order():
    """Structural part drawn second must not overwrite higher-priority cladding."""
    render = _load_render_module()
    structural, cladding = _coincident_clad_struct_parts()
    state = AssemblyState(
        name="coplanar_clad_tiebreak_reverse",
        parts={
            cladding.part_id: cladding,
            structural.part_id: structural,
        },
    )
    _assert_cladding_wins_coplanar_tiebreak(render, state)
