"""Regression tests for validation-view rasterizer depth tie-breaking."""

from __future__ import annotations

import importlib.util
import sys
from collections.abc import Callable
from pathlib import Path

import numpy as np

from stand_cad.geometry.assembly import (
    AssemblyState,
    build_operating_with_test_bodies_assembly,
    build_organizer_loaded_assembly,
    build_panels_hidden_assembly,
    build_service_plotter_1_assembly,
    build_service_plotter_2_assembly,
    build_transport_assembly,
    build_tray1_quick_access_assembly,
)
from stand_cad.geometry.primitives import box_from_bounds
from stand_cad.geometry.registry import PartRecord
from stand_cad.parameters import Parameters, load_parameters

REPO_ROOT = Path(__file__).resolve().parents[1]
_RENDER_MODULE_PATH = REPO_ROOT / "scripts" / "render_validation_views.py"
_PARAMETERS_PATH = REPO_ROOT / "config" / "parameters.yaml"

# Approach (b): structural / reference materials intentionally default to render priority 0.
# Cladding keys must appear in MATERIAL_RENDER_PRIORITY with priority 1 (D-040).
# Follow-up: register every key explicitly in scripts/render_validation_views.py.
KNOWN_PRIORITY_ZERO_MATERIALS: frozenset[str] = frozenset({
    "aluminium_angle_15x15x1.5",  # frame rails and tray structure
    "sandwich_panel_10_12mm",  # tray and organizer floor panels
    "hdpe_insert_thin",  # organizer inserts
    "full_extension_slide_hardware",  # slide rails
    "elastomer_soft_stop",  # rear soft stops
    "elastomer_vibration_mount",  # plotter vibration mounts
    "interlock_shuttle_hardware",  # tray interlock shuttle
    "interlock_tab_hardware",  # tray interlock tabs
    "silicone_foot",  # transport feet
    "aluminium_stack_cap",  # STACK-001 corner stacking caps (D-064)
    "soft_trim_brush",  # cable grommet trim (GROMMET_MATERIAL)
    "hardware_mains_inlet",  # mains inlet placeholder
    "service_volume",  # service-zone collision volumes
    "equipment_reference",  # plotter body placeholders
    "reference_envelope",  # design envelopes and lid envelopes
    "film_sheet_reference",  # organizer film bodies
    "media_path_test_body",  # operating-state media-path probes
})

_ASSEMBLY_BUILDERS: tuple[tuple[str, Callable[[Parameters], AssemblyState]], ...] = (
    ("transport", build_transport_assembly),
    ("organizer_loaded", build_organizer_loaded_assembly),
    ("operating_with_test_bodies", build_operating_with_test_bodies_assembly),
    ("service_plotter_1", build_service_plotter_1_assembly),
    ("service_plotter_2", build_service_plotter_2_assembly),
    ("tray1_quick_access", build_tray1_quick_access_assembly),
    ("panels_hidden", build_panels_hidden_assembly),
)


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


def test_all_assembly_materials_registered_or_documented_priority_zero():
    """Every assembly material must be in MATERIAL_RENDER_PRIORITY or KNOWN_PRIORITY_ZERO."""
    render = _load_render_module()
    params = load_parameters(_PARAMETERS_PATH)
    materials: set[str] = set()
    for _name, builder in _ASSEMBLY_BUILDERS:
        for record in builder(params).parts.values():
            materials.add(record.material)

    registered = set(render.MATERIAL_RENDER_PRIORITY)
    allowed = registered | KNOWN_PRIORITY_ZERO_MATERIALS
    unknown = sorted(materials - allowed)
    assert unknown == [], (
        "materials missing from MATERIAL_RENDER_PRIORITY and KNOWN_PRIORITY_ZERO_MATERIALS: "
        + ", ".join(unknown)
    )
    missing_from_dict = sorted(materials - registered)
    assert missing_from_dict, "expected some priority-0 materials not yet in dict"
    assert missing_from_dict == sorted(KNOWN_PRIORITY_ZERO_MATERIALS & materials), (
        "KNOWN_PRIORITY_ZERO_MATERIALS must match materials absent from "
        "MATERIAL_RENDER_PRIORITY; follow-up should add explicit priority-0 keys to "
        "scripts/render_validation_views.py"
    )
