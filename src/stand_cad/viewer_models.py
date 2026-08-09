"""Pure helpers for the GLB viewer model index (FIX-VIEW-001)."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

REV_PATTERN = re.compile(r"_rev(\d+)\.manifest\.json$", re.IGNORECASE)
DEFAULT_ASSEMBLY_STATE = "transport"

DEFAULT_VIEWER_LABELS: dict[str, str] = {
    "transport": "transport (doors closed)",
    "service_plotter_1": "service P1 (lower door open)",
    "service_plotter_2": "service P2 (upper door open)",
}


def revision_from_name(name: str) -> int:
    match = REV_PATTERN.search(name)
    return int(match.group(1)) if match else -1


def manifest_assembly_state(payload: dict[str, Any], manifest_name: str) -> str:
    """Resolve assembly_state from manifest JSON or filename stem."""
    explicit = payload.get("assembly_state")
    if isinstance(explicit, str) and explicit:
        return explicit
    upper = manifest_name.upper()
    if "SERVICE_PLOTTER_1" in upper:
        return "service_plotter_1"
    if "SERVICE_PLOTTER_2" in upper:
        return "service_plotter_2"
    return DEFAULT_ASSEMBLY_STATE


def manifest_label(payload: dict[str, Any], manifest_name: str) -> str:
    """Human label for viewer dropdown."""
    explicit = payload.get("label")
    if isinstance(explicit, str) and explicit:
        return explicit
    return DEFAULT_VIEWER_LABELS.get(
        manifest_assembly_state(payload, manifest_name),
        manifest_assembly_state(payload, manifest_name),
    )


def model_sort_key(model: dict[str, Any]) -> tuple[int, int, str]:
    """Sort newest revision first; transport before service at the same revision."""
    revision = int(model.get("revision", -1))
    state = model.get("assembly_state", DEFAULT_ASSEMBLY_STATE)
    state_rank = 0 if state == DEFAULT_ASSEMBLY_STATE else 1
    return (-revision, state_rank, str(model.get("manifest_file", "")))


def pick_default_model(models: list[dict[str, Any]]) -> dict[str, Any] | None:
    """Default viewer model: transport at the highest available revision."""
    if not models:
        return None
    return min(models, key=model_sort_key)


def pick_newest_concept_pair(
    candidates: list[tuple[Path, dict[str, Any], Path]],
) -> tuple[Path | None, Path | None, int]:
    """Pick transport GLB/manifest at the highest revision when multiple exist."""
    if not candidates:
        return None, None, -1
    best_rev = -1
    best_state_rank = 999
    best_manifest: Path | None = None
    best_glb: Path | None = None
    for manifest_path, payload, glb_path in candidates:
        rev = revision_from_name(manifest_path.name)
        state = manifest_assembly_state(payload, manifest_path.name)
        state_rank = 0 if state == DEFAULT_ASSEMBLY_STATE else 1
        if rev > best_rev or (rev == best_rev and state_rank < best_state_rank):
            best_rev = rev
            best_state_rank = state_rank
            best_manifest = manifest_path
            best_glb = glb_path
    return best_manifest, best_glb, best_rev


def build_models_index(concept_dir: Path) -> dict[str, Any]:
    """Build viewer models.json payload from a concept output directory."""
    models: list[dict[str, Any]] = []
    if concept_dir.is_dir():
        for manifest_path in sorted(concept_dir.glob("*.manifest.json")):
            try:
                payload = json.loads(manifest_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            glb_name = payload.get("glb_file") or manifest_path.name.replace(
                ".manifest.json", ".glb"
            )
            glb_path = concept_dir / glb_name
            if not glb_path.is_file():
                continue
            models.append(
                {
                    "revision": revision_from_name(manifest_path.name),
                    "assembly_state": manifest_assembly_state(payload, manifest_path.name),
                    "label": manifest_label(payload, manifest_path.name),
                    "manifest_file": manifest_path.name,
                    "manifest_url": f"/output/concept/{manifest_path.name}",
                    "glb_file": glb_name,
                    "glb_url": f"/output/concept/{glb_name}",
                    "part_count": payload.get("part_count"),
                    "bbox_size_mm": payload.get("bbox_size_mm"),
                }
            )
    models.sort(key=model_sort_key)
    default_model = pick_default_model(models)
    return {
        "models": models,
        "default_manifest_url": default_model["manifest_url"] if default_model else None,
    }
