"""Viewer model index and default-selection helpers (FIX-VIEW-001)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from stand_cad.viewer_models import (
    DEFAULT_ASSEMBLY_STATE,
    build_models_index,
    manifest_assembly_state,
    manifest_label,
    model_sort_key,
    pick_default_model,
    pick_newest_concept_pair,
)


def _write_manifest(
    concept_dir: Path,
    *,
    stem: str,
    revision: int,
    assembly_state: str | None = None,
    label: str | None = None,
) -> tuple[Path, Path]:
    glb_name = f"{stem}.glb"
    manifest_path = concept_dir / f"{stem}.manifest.json"
    glb_path = concept_dir / glb_name
    payload: dict[str, object] = {
        "revision": revision,
        "glb_file": glb_name,
        "part_count": 1,
        "bbox_size_mm": [650.0, 420.0, 540.0],
    }
    if assembly_state is not None:
        payload["assembly_state"] = assembly_state
    if label is not None:
        payload["label"] = label
    manifest_path.write_text(json.dumps(payload), encoding="utf-8")
    glb_path.write_bytes(b"glb")
    return manifest_path, glb_path


@pytest.mark.parametrize(
    ("manifest_name", "payload", "expected"),
    [
        (
            "light_plotter_tower_ASSEMBLY_CONCEPT_REFERENCE_ONLY_rev15.manifest.json",
            {},
            "transport",
        ),
        (
            "light_plotter_tower_SERVICE_PLOTTER_1_CONCEPT_REFERENCE_ONLY_rev15.manifest.json",
            {},
            "service_plotter_1",
        ),
        (
            "custom.manifest.json",
            {"assembly_state": "service_plotter_2"},
            "service_plotter_2",
        ),
    ],
)
def test_manifest_assembly_state(manifest_name: str, payload: dict, expected: str) -> None:
    assert manifest_assembly_state(payload, manifest_name) == expected


def test_manifest_label_prefers_explicit() -> None:
    payload = {"label": "custom label", "assembly_state": "transport"}
    assert manifest_label(payload, "any.manifest.json") == "custom label"


def test_model_sort_key_prefers_transport_at_same_revision() -> None:
    transport = {
        "revision": 15,
        "assembly_state": "transport",
        "manifest_file": "a.manifest.json",
    }
    service = {
        "revision": 15,
        "assembly_state": "service_plotter_2",
        "manifest_file": "z.manifest.json",
    }
    assert model_sort_key(transport) < model_sort_key(service)


def test_pick_default_model_prefers_transport_over_service_at_rev15() -> None:
    service_p2_manifest = (
        "light_plotter_tower_SERVICE_PLOTTER_2_CONCEPT_REFERENCE_ONLY_rev15.manifest.json"
    )
    transport_manifest = (
        "light_plotter_tower_ASSEMBLY_CONCEPT_REFERENCE_ONLY_rev15.manifest.json"
    )
    service_p1_manifest = (
        "light_plotter_tower_SERVICE_PLOTTER_1_CONCEPT_REFERENCE_ONLY_rev15.manifest.json"
    )
    models = [
        {
            "revision": 15,
            "assembly_state": "service_plotter_2",
            "manifest_file": service_p2_manifest,
            "manifest_url": f"/output/concept/{service_p2_manifest}",
        },
        {
            "revision": 15,
            "assembly_state": "transport",
            "manifest_file": transport_manifest,
            "manifest_url": f"/output/concept/{transport_manifest}",
        },
        {
            "revision": 15,
            "assembly_state": "service_plotter_1",
            "manifest_file": service_p1_manifest,
            "manifest_url": f"/output/concept/{service_p1_manifest}",
        },
    ]
    default = pick_default_model(models)
    assert default is not None
    assert default["assembly_state"] == DEFAULT_ASSEMBLY_STATE


def test_pick_newest_concept_pair_prefers_transport_at_same_revision(tmp_path: Path) -> None:
    transport_manifest, transport_glb = _write_manifest(
        tmp_path,
        stem="light_plotter_tower_ASSEMBLY_CONCEPT_REFERENCE_ONLY_rev15",
        revision=15,
        assembly_state="transport",
    )
    service_manifest, service_glb = _write_manifest(
        tmp_path,
        stem="light_plotter_tower_SERVICE_PLOTTER_2_CONCEPT_REFERENCE_ONLY_rev15",
        revision=15,
        assembly_state="service_plotter_2",
    )
    candidates = [
        (service_manifest, {"assembly_state": "service_plotter_2"}, service_glb),
        (transport_manifest, {"assembly_state": "transport"}, transport_glb),
    ]
    manifest_path, glb_path, revision = pick_newest_concept_pair(candidates)
    assert revision == 15
    assert manifest_path == transport_manifest
    assert glb_path == transport_glb


def test_build_models_index_default_is_transport(tmp_path: Path) -> None:
    _write_manifest(
        tmp_path,
        stem="light_plotter_tower_SERVICE_PLOTTER_1_CONCEPT_REFERENCE_ONLY_rev15",
        revision=15,
        assembly_state="service_plotter_1",
        label="service P1 (lower door open)",
    )
    _write_manifest(
        tmp_path,
        stem="light_plotter_tower_ASSEMBLY_CONCEPT_REFERENCE_ONLY_rev15",
        revision=15,
        assembly_state="transport",
        label="transport (doors closed)",
    )
    index = build_models_index(tmp_path)
    assert len(index["models"]) == 2
    default_url = index["default_manifest_url"]
    assert default_url is not None
    assert default_url.endswith("ASSEMBLY_CONCEPT_REFERENCE_ONLY_rev15.manifest.json")
    labels = {item["label"] for item in index["models"]}
    assert "service P1 (lower door open)" in labels
