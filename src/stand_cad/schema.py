"""Fail-closed validation for project and equipment inputs.

This module deliberately has no CAD dependency so input/release gates can be tested quickly.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ValidationIssue:
    severity: str
    code: str
    message: str


def _positive(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and value > 0


# Once config/parameters.yaml exists, stand_cad.parameters.validate_release_readiness is the
# authoritative combined production gate, not validate_documents alone.


def validate_documents(
    project_doc: dict[str, Any],
    equipment_doc: dict[str, Any],
    *,
    allow_demo: bool = False,
) -> list[ValidationIssue]:
    """Validate inputs and enforce production release gates.

    Returns all issues so an autonomous agent can fix independent problems in one pass.
    """

    issues: list[ValidationIssue] = []
    project = project_doc.get("project", {})
    constraints = project_doc.get("constraints", {})
    workflow = project_doc.get("workflow", {})
    manufacturing = project_doc.get("manufacturing", {})
    production = bool(project.get("production_release", False))
    project_mode = project.get("mode")
    release_kind = str(project.get("release_kind", "none")).lower()

    if project_doc.get("schema_version") != 1:
        issues.append(ValidationIssue("ERROR", "CFG-001", "Unsupported project schema_version"))
    if equipment_doc.get("schema_version") != 1:
        issues.append(ValidationIssue("ERROR", "CFG-002", "Unsupported equipment schema_version"))
    if project_mode == "demo" and not allow_demo:
        issues.append(ValidationIssue("ERROR", "CFG-003", "Demo config requires --allow-demo"))
    if not production and release_kind != "none":
        issues.append(
            ValidationIssue(
                "ERROR",
                "REL-023",
                "Non-production configuration must use release_kind=none",
            )
        )
    if production and project_mode != "production":
        issues.append(
            ValidationIssue(
                "ERROR",
                "REL-001",
                "production_release requires project.mode=production",
            )
        )
    if production and project.get("units") != "mm":
        issues.append(ValidationIssue("ERROR", "REL-012", "Production units must be mm"))
    if production and str(project.get("revision", "")).upper() in {"", "DRAFT", "TBD"}:
        issues.append(ValidationIssue("ERROR", "REL-013", "A controlled revision is required"))
    if production and not str(project.get("id", "")).strip():
        issues.append(ValidationIssue("ERROR", "REL-024", "A project id is required"))
    if production and release_kind not in {"prototype", "series"}:
        issues.append(
            ValidationIssue("ERROR", "REL-014", "release_kind must be prototype or series")
        )
    if release_kind == "series" and not str(
        project.get("prototype_inspection_record_id", "")
    ).strip():
        issues.append(
            ValidationIssue(
                "ERROR",
                "REL-015",
                "Series release requires a prototype inspection record",
            )
        )

    enabled = [item for item in equipment_doc.get("equipment", []) if item.get("enabled")]
    if not enabled:
        issues.append(
            ValidationIssue(
                "ERROR",
                "EQP-000",
                "At least one equipment item must be enabled",
            )
        )

    ids: set[str] = set()
    for index, item in enumerate(enabled):
        item_id = str(item.get("id", "")).strip()
        prefix = item_id or f"equipment[{index}]"
        if not item_id:
            issues.append(ValidationIssue("ERROR", "EQP-001", f"{prefix}: id is required"))
        elif item_id in ids:
            issues.append(ValidationIssue("ERROR", "EQP-002", f"{prefix}: duplicate id"))
        ids.add(item_id)

        for field in ("width_mm", "depth_mm", "height_mm", "mass_kg"):
            if not _positive(item.get(field)):
                issues.append(
                    ValidationIssue("ERROR", "EQP-003", f"{prefix}: {field} must be positive")
                )
        if not _positive(item.get("quantity")):
            issues.append(
                ValidationIssue("ERROR", "EQP-004", f"{prefix}: quantity must be positive")
            )
        if production and not item.get("verified", False):
            issues.append(
                ValidationIssue("ERROR", "REL-002", f"{prefix}: enabled equipment is unverified")
            )
        if production and not str(item.get("source_reference", "")).strip():
            issues.append(
                ValidationIssue("ERROR", "REL-003", f"{prefix}: source_reference is required")
            )
        if production and "TBD" in str(item.get("model", "")).upper():
            issues.append(
                ValidationIssue("ERROR", "REL-004", f"{prefix}: exact model is unresolved")
            )
        if production and str(item.get("manufacturer", "")).strip().upper() in {"", "TBD"}:
            issues.append(
                ValidationIssue("ERROR", "REL-025", f"{prefix}: manufacturer is unresolved")
            )
        if production and str(item.get("transport_orientation", "")).strip().upper() in {
            "",
            "TBD",
        }:
            issues.append(
                ValidationIssue(
                    "ERROR",
                    "REL-026",
                    f"{prefix}: transport orientation is unresolved",
                )
            )
        if production and str(item.get("source_type", "")).upper() in {
            "",
            "TBD",
            "SYNTHETIC_DEMO",
        }:
            issues.append(
                ValidationIssue("ERROR", "REL-016", f"{prefix}: source_type is not releasable")
            )
        for field, code, label in (
            ("envelopes_verified", "REL-017", "operating/service envelopes"),
            ("support_verified", "REL-018", "support conditions"),
            ("transport_verified", "REL-019", "transport conditions"),
        ):
            if production and not item.get(field, False):
                issues.append(
                    ValidationIssue("ERROR", code, f"{prefix}: {label} are unverified")
                )
        if production and item.get("powered", False):
            if not _positive(item.get("power_w")):
                issues.append(
                    ValidationIssue("ERROR", "REL-020", f"{prefix}: power_w must be positive")
                )
            if not item.get("electrical_verified", False):
                issues.append(
                    ValidationIssue("ERROR", "REL-021", f"{prefix}: electrical data unverified")
                )
        if production and item.get("heat_source", False) and not item.get(
            "thermal_verified", False
        ):
            issues.append(
                ValidationIssue("ERROR", "REL-022", f"{prefix}: thermal data unverified")
            )

    if production:
        for field in (
            "max_outer_width_mm",
            "max_outer_depth_mm",
            "max_outer_height_mm",
            "max_total_mass_kg",
        ):
            if not _positive(constraints.get(field)):
                issues.append(
                    ValidationIssue("ERROR", "REL-005", f"constraints.{field} must be positive")
                )
        if not constraints.get("constraints_verified", False):
            issues.append(
                ValidationIssue("ERROR", "REL-006", "External constraints are unverified")
            )
        if not workflow.get("workflow_verified", False):
            issues.append(ValidationIssue("ERROR", "REL-007", "Operating workflow is unverified"))
        if not str(manufacturing.get("target_manufacturer", "")).strip() or str(
            manufacturing.get("target_manufacturer", "")
        ).upper() == "TBD":
            issues.append(ValidationIssue("ERROR", "REL-008", "Target manufacturer is unresolved"))
        if not str(manufacturing.get("dfm_record_id", "")).strip():
            issues.append(ValidationIssue("ERROR", "REL-009", "Manufacturer DFM record is missing"))
        if manufacturing.get("uses_bent_sheet_metal", False):
            if not manufacturing.get("bend_data_confirmed", False):
                issues.append(ValidationIssue("ERROR", "REL-010", "Bend data is unconfirmed"))
            if str(manufacturing.get("flat_pattern_owner", "")).upper() in {"", "TBD"}:
                issues.append(
                    ValidationIssue("ERROR", "REL-011", "Flat-pattern owner is unresolved")
                )

    return issues
