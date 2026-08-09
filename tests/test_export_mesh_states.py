"""GLB/manifest export for transport + service viewer states (FIX-VIEW-001)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from build123d import Box, Compound

from stand_cad.geometry.assembly import (
    build_service_plotter_1_assembly,
    build_transport_display_assembly,
)
from stand_cad.geometry.collision import _door_is_open_horizontal
from stand_cad.geometry.export import (
    CONCEPT_REVISION,
    VIEWER_MESH_STATE_LABELS,
    build_labeled_assembly_compound,
    export_transport_mesh_bundle,
    viewer_mesh_state_stem,
    write_glb_manifest,
)
from stand_cad.geometry.registry import PartRecord


def test_viewer_mesh_state_stems_include_rev_suffix() -> None:
    assert viewer_mesh_state_stem("transport") == (
        f"light_plotter_tower_ASSEMBLY_CONCEPT_REFERENCE_ONLY_rev{CONCEPT_REVISION}"
    )
    assert viewer_mesh_state_stem("service_plotter_1") == (
        f"light_plotter_tower_SERVICE_PLOTTER_1_CONCEPT_REFERENCE_ONLY_rev{CONCEPT_REVISION}"
    )
    assert viewer_mesh_state_stem("service_plotter_2") == (
        f"light_plotter_tower_SERVICE_PLOTTER_2_CONCEPT_REFERENCE_ONLY_rev{CONCEPT_REVISION}"
    )


def test_write_glb_manifest_includes_assembly_state_and_label(tmp_path: Path) -> None:
    compound = Compound(children=[Box(10, 10, 10)])
    records = [
        PartRecord(part_id="PART-001", material="sandwich_panel_10_12mm", solid=Box(10, 10, 10))
    ]
    manifest_path = tmp_path / "demo.manifest.json"
    write_glb_manifest(
        manifest_path,
        glb_filename="demo.glb",
        compound=compound,
        records=records,
        assembly_state="service_plotter_1",
        label=VIEWER_MESH_STATE_LABELS["service_plotter_1"],
    )
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert payload["assembly_state"] == "service_plotter_1"
    assert payload["label"] == "service P1 (lower door open)"
    assert payload["glb_file"] == "demo.glb"


def test_build_labeled_assembly_compound_labels_solids(params) -> None:
    state = build_transport_display_assembly(params)
    _state, compound, records = build_labeled_assembly_compound(state)
    assert len(records) == len(state.parts)
    assert len(compound.children) == len(state.parts)


def test_export_transport_mesh_bundle_forwards_include_stl(
    params,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Regression: wrapper must pass include_stl, not export_stl (F-1)."""
    captured: dict[str, object] = {}

    def fake_export(*_args, **kwargs):
        captured.update(kwargs)
        return {
            "stl": tmp_path / "demo.stl",
            "glb": tmp_path / "demo.glb",
            "manifest": tmp_path / "demo.manifest.json",
        }

    monkeypatch.setattr(
        "stand_cad.geometry.export.export_assembly_mesh_bundle",
        fake_export,
    )
    export_transport_mesh_bundle(params, tmp_path, stem="demo")
    assert captured.get("include_stl") is True
    assert "export_stl" not in captured


def test_service_plotter_1_lower_door_open_vs_transport_closed(params) -> None:
    """Service P1 exports with lower door horizontal-open orientation."""
    threshold = float(params.value("tolerance.part_assembly_feature_mm"))
    transport = build_transport_display_assembly(params)
    service = build_service_plotter_1_assembly(params)
    lower_closed = transport.parts["DOOR-LOWER-001"].solid
    lower_open = service.parts["DOOR-LOWER-001"].solid
    assert not _door_is_open_horizontal(lower_closed, threshold=threshold)
    assert _door_is_open_horizontal(lower_open, threshold=threshold)
