"""Fail-closed loader and validation for config/parameters.yaml.

This module deliberately has no CAD dependency so parameter gates can be tested quickly.
Derived quantities (shelf_stack_height_mm, tier clearances, case.height consistency) are
computed on access from verified leaves — never stored as stale hardcoded YAML values.

Vertical film storage removed in PLT-007; recovery point commit 69b1261.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from .schema import ValidationIssue, validate_documents

PROVENANCE_VALUES = frozenset({"verified", "derived", "to_measure"})

# Acceptance-criteria thresholds (see config/parameters.yaml notes).
REQUIRED_CASE_WIDTH_MM = 650  # TZ section 4 — not flexible per owner 2026-08-04
CASE_DEPTH_TARGET_MM = 550  # TZ section 4 target; tolerance below
CASE_DEPTH_TOLERANCE_MM = 5  # Owner 2026-08-04 allowance
REQUIRED_UPPER_SETBACK_MM = 130  # Owner 2026-08-04 (supersedes TZ 150 mm)
HORIZONTAL_ORGANIZER_CLEAR_MIN_MM = (610, 330, 100)  # width, depth, stack height (4×25 mm)
HORIZONTAL_SHELF_COUNT = 4  # Owner 2026-08-04 verified default
TIER_CLEARANCE_MIN_MM = 170  # Owner 2026-08-04; matches plotter.tier_clearance_min_mm leaf

PARAMETER_GROUPS = (
    "case",
    "tolerance",
    "plotter",
    "plotter_cameo4",
    "plotter_cameo5",
    "operational",
    "trays",
    "film_storage_horizontal",
    "media_path",
    "materials",
    "lighting",
    "thermal",
    "stability",
    "mass_targets",
    "hardware",
    "top_structure",
    "interlock",
    "services",
)


@dataclass(frozen=True)
class Parameter:
    path: str
    value: Any
    provenance: str
    note: str = ""


class Parameters:
    """Wrapper around the loaded parameter document with dotted-path leaf access."""

    def __init__(self, raw: dict[str, Any]) -> None:
        self._raw = raw
        self._leaves: dict[str, Parameter] = {}
        for group in PARAMETER_GROUPS:
            section = raw.get(group)
            if isinstance(section, dict):
                self._walk(section, group, self._leaves)

    @staticmethod
    def _walk(node: dict[str, Any], prefix: str, leaves: dict[str, Parameter]) -> None:
        for key, val in node.items():
            path = f"{prefix}.{key}"
            if not isinstance(val, dict):
                leaves[path] = Parameter(
                    path=path,
                    value=val,
                    provenance="",
                    note="",
                )
                continue
            if "value" in val and "provenance" in val:
                leaves[path] = Parameter(
                    path=path,
                    value=val["value"],
                    provenance=str(val["provenance"]),
                    note=str(val.get("note", "")),
                )
            elif any(isinstance(v, dict) for v in val.values()):
                Parameters._walk(val, path, leaves)
            else:
                provenance = val.get("provenance", "")
                leaves[path] = Parameter(
                    path=path,
                    value=val.get("value"),
                    provenance="" if provenance is None else str(provenance),
                    note=str(val.get("note", "")),
                )

    def leaves(self) -> list[Parameter]:
        return list(self._leaves.values())

    def get(self, path: str) -> Parameter:
        try:
            return self._leaves[path]
        except KeyError as exc:
            raise KeyError(path) from exc

    def value(self, path: str) -> Any:
        return self.get(path).value

    @property
    def horizontal_shelf_stack_height_mm(self) -> float:
        """Derived stack height: shelf_count × clear + (shelf_count−1) × divider_t."""
        shelves = int(self.value("film_storage_horizontal.shelf_count"))
        clear_h = float(self.value("film_storage_horizontal.compartment_clear_height_mm"))
        divider_t = float(self.value("film_storage_horizontal.divider_thickness"))
        return shelves * clear_h + (shelves - 1) * divider_t

    @property
    def horizontal_shelf_divider_count(self) -> int:
        """Horizontal shelf dividers between compartments: shelf_count − 1."""
        return int(self.value("film_storage_horizontal.shelf_count")) - 1

    @property
    def computed_case_height_mm(self) -> float:
        """Overall case height = organizer floor Z + shelf stack + top_structure.height_mm."""
        org_z = float(self.value("film_storage_horizontal.z"))
        top_h = float(self.value("top_structure.height_mm"))
        return org_z + self.horizontal_shelf_stack_height_mm + top_h

    @property
    def computed_organizer_z_mm(self) -> float:
        """Organizer floor top Z = upper_z + tier_clearance_min + frame profile."""
        upper_z = float(self.value("plotter.upper_z"))
        tier_min = float(self.value("plotter.tier_clearance_min_mm"))
        profile = float(self.value("materials.frame_profile_size_mm"))
        return upper_z + tier_min + profile

    @property
    def computed_upper_z_mm(self) -> float:
        """Upper tray datum: lower_z + tier_clearance_min + tray_panel_thickness."""
        lower_z = float(self.value("plotter.lower_z"))
        tier_min = float(self.value("plotter.tier_clearance_min_mm"))
        return lower_z + tier_min + self.tray_panel_thickness_mm

    @property
    def side_slab_thickness_mm(self) -> float:
        """Side slab thickness = (case.width − internal_width) / 2."""
        return self.side_clearance_mm

    @property
    def side_clearance_mm(self) -> float:
        """Derived side clearance: (case.width − internal_width) / 2."""
        width = float(self.value("case.width"))
        internal = float(self.value("case.internal_width"))
        return (width - internal) / 2

    @property
    def tier_envelope_height_mm(self) -> float:
        """Protective design envelope height for tier niches (Cameo 4 derived design_height)."""
        return float(self.value("plotter.design_height"))

    @property
    def tier_envelope_offset_z_mm(self) -> float:
        """Z offset centering governing physical plotter in design envelope."""
        return float(self.value("plotter.envelope_offset_z_mm"))

    def plotter_mass_kg(self, index: int) -> float:
        """Per-slot mass — slot 1 Cameo 4, slot 2 Cameo 5 (either machine either tier model)."""
        if index == 1:
            return float(self.value("plotter_cameo4.mass_kg"))
        if index == 2:
            return float(self.value("plotter_cameo5.mass_kg"))
        raise ValueError("plotter index must be 1 or 2")

    def plotter_y_front_mm(self, index: int, *, tray_extension_mm: float = 0.0) -> float:
        """Plotter front face Y after optional tray extension (negative dy = forward)."""
        prefix = "lower" if index == 1 else "upper"
        return float(self.value(f"plotter.{prefix}_y")) - tray_extension_mm

    def plotter_y_rear_mm(self, index: int, *, tray_extension_mm: float = 0.0) -> float:
        """Plotter rear face Y after optional tray extension."""
        return self.plotter_y_front_mm(index, tray_extension_mm=tray_extension_mm) + float(
            self.value("plotter.physical_depth")
        )

    def material_travel_clearance_front_mm(
        self, index: int, *, tray_extension_mm: float = 0.0
    ) -> float:
        """Clear Y from case front (Y=0) to plotter front face — cutting/service check."""
        return self.plotter_y_front_mm(index, tray_extension_mm=tray_extension_mm)

    def material_travel_clearance_rear_mm(
        self, index: int, *, tray_extension_mm: float = 0.0
    ) -> float:
        """Clear Y from plotter rear face to case rear (case.depth)."""
        depth = float(self.value("case.depth"))
        return depth - self.plotter_y_rear_mm(index, tray_extension_mm=tray_extension_mm)

    def pass_through_depth_required_mm(self) -> float:
        """Linear Y span for 356 mm front + machine + 356 mm rear pass-through."""
        required = float(self.value("operational.material_travel_clearance_mm"))
        machine_d = float(self.value("plotter.physical_depth"))
        return 2 * required + machine_d

    @property
    def tier_clearance_lower_mm(self) -> float:
        """Lower tier: tray top (lower_z) to underside of upper tray (upper_z − tray_t)."""
        lower_z = float(self.value("plotter.lower_z"))
        upper_z = float(self.value("plotter.upper_z"))
        return (upper_z - self.tray_panel_thickness_mm) - lower_z

    @property
    def tier_clearance_upper_mm(self) -> float:
        """Upper tier: tray top (upper_z) to underside of ORG frame rail (org_z − profile)."""
        upper_z = float(self.value("plotter.upper_z"))
        org_z = float(self.value("film_storage_horizontal.z"))
        profile = float(self.value("materials.frame_profile_size_mm"))
        return (org_z - profile) - upper_z

    @property
    def side_panel_centre_z_mm(self) -> float:
        """Handle mount Z — side panel vertical centre from foot top to case height."""
        foot_h = float(self.value("materials.foot_height_mm"))
        height = float(self.value("case.height"))
        return (foot_h + height) / 2

    @property
    def envelope_offset_x_mm(self) -> float:
        return (
            float(self.value("plotter.design_width")) - float(self.value("plotter.physical_width"))
        ) / 2

    @property
    def envelope_offset_y_mm(self) -> float:
        return (
            float(self.value("plotter.design_depth")) - float(self.value("plotter.physical_depth"))
        ) / 2

    @property
    def envelope_offset_z_mm(self) -> float:
        return (
            float(self.value("plotter.design_height"))
            - float(self.value("plotter.physical_height"))
        ) / 2

    def plotter_envelope_bounds(self, index: int) -> tuple[tuple[float, float], ...]:
        """Return ((x_min, x_max), (y_min, y_max), (z_min, z_max)) for plotter 1 or 2."""
        if index not in (1, 2):
            raise ValueError("plotter index must be 1 or 2")
        prefix = "lower" if index == 1 else "upper"
        ox = self.envelope_offset_x_mm
        oy = self.envelope_offset_y_mm
        oz = self.tier_envelope_offset_z_mm
        px = float(self.value("plotter.x"))
        py = float(self.value(f"plotter.{prefix}_y"))
        pz = float(self.value(f"plotter.{prefix}_z"))
        dw = float(self.value("plotter.design_width"))
        dd = float(self.value("plotter.design_depth"))
        dh = self.tier_envelope_height_mm
        return (
            (px - ox, px - ox + dw),
            (py - oy, py - oy + dd),
            (pz - oz, pz - oz + dh),
        )

    def plotter_physical_bounds(self, index: int) -> tuple[tuple[float, float], ...]:
        if index not in (1, 2):
            raise ValueError("plotter index must be 1 or 2")
        prefix = "lower" if index == 1 else "upper"
        px = float(self.value("plotter.x"))
        py = float(self.value(f"plotter.{prefix}_y"))
        pz = float(self.value(f"plotter.{prefix}_z"))
        pw = float(self.value("plotter.physical_width"))
        pd = float(self.value("plotter.physical_depth"))
        ph = float(self.value("plotter.physical_height"))
        return (
            (px, px + pw),
            (py, py + pd),
            (pz, pz + ph),
        )

    @property
    def plotter_envelope_z_clearance_mm(self) -> float:
        env1 = self.plotter_envelope_bounds(1)
        env2 = self.plotter_envelope_bounds(2)
        return env2[2][0] - env1[2][1]

    @property
    def tray_panel_thickness_mm(self) -> float:
        t_min = float(self.value("materials.tray_panel_thickness_min_mm"))
        t_max = float(self.value("materials.tray_panel_thickness_max_mm"))
        return (t_min + t_max) / 2

    @property
    def interlock_tab_engagement_mm(self) -> float:
        return 6 * float(self.value("tolerance.part_assembly_feature_mm"))

    @property
    def interlock_shuttle_travel_mm(self) -> float:
        lower_slide_z = float(self.value("plotter.lower_z")) - self.tray_panel_thickness_mm
        upper_slide_z = float(self.value("plotter.upper_z")) - self.tray_panel_thickness_mm
        slide_h = float(self.value("trays.slide_rail_height_mm"))
        return (upper_slide_z - lower_slide_z - slide_h) / 2

    @property
    def interlock_shuttle_channel_width_mm(self) -> float:
        return 4 * self.interlock_tab_engagement_mm

    @property
    def org_insert_thickness_mm(self) -> float:
        val = self.value("materials.org_insert_thickness_mm")
        if isinstance(val, (int, float)) and not isinstance(val, bool):
            return float(val)
        return float(self.value("materials.org_insert_provisional_mm"))


def with_shelf_count(params: Parameters, shelf_count: int) -> Parameters:
    """Return a Parameters copy with film_storage_horizontal.shelf_count overridden."""
    raw = deepcopy(params._raw)
    section = raw.setdefault("film_storage_horizontal", {})
    leaf = section.get("shelf_count", {})
    section["shelf_count"] = {
        "value": shelf_count,
        "provenance": leaf.get("provenance", "verified"),
        "note": leaf.get("note", ""),
    }
    return Parameters(raw)


def load_parameters(path: str | Path) -> Parameters:
    text = Path(path).read_text(encoding="utf-8")
    doc = yaml.safe_load(text)
    if not isinstance(doc, dict):
        raise ValueError("Top-level parameters document must be a mapping")
    return Parameters(doc)


def validate_parameters(
    params: Parameters,
    *,
    production_release: bool = False,
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []

    for leaf in params.leaves():
        if leaf.provenance not in PROVENANCE_VALUES:
            issues.append(
                ValidationIssue(
                    "ERROR",
                    "PARAM-001",
                    f"{leaf.path}: invalid or missing provenance marker",
                )
            )

    shelf_count = params.value("film_storage_horizontal.shelf_count")
    if (
        not isinstance(shelf_count, int)
        or isinstance(shelf_count, bool)
        or shelf_count != HORIZONTAL_SHELF_COUNT
    ):
        issues.append(
            ValidationIssue(
                "ERROR",
                "PARAM-002",
                f"film_storage_horizontal.shelf_count must be exactly {HORIZONTAL_SHELF_COUNT}",
            )
        )

    clear_width = params.value("film_storage_horizontal.clear_width")
    clear_depth = params.value("film_storage_horizontal.clear_depth")
    stack_h = params.horizontal_shelf_stack_height_mm
    min_clear_width, min_clear_depth, min_stack_h = HORIZONTAL_ORGANIZER_CLEAR_MIN_MM
    if (
        isinstance(clear_width, (int, float))
        and not isinstance(clear_width, bool)
        and clear_width < min_clear_width
    ):
        issues.append(
            ValidationIssue(
                "ERROR",
                "PARAM-005",
                (
                    f"film_storage_horizontal.clear_width ({clear_width}) is below "
                    f"{min_clear_width} mm minimum"
                ),
            )
        )
    if (
        isinstance(clear_depth, (int, float))
        and not isinstance(clear_depth, bool)
        and clear_depth < min_clear_depth
    ):
        issues.append(
            ValidationIssue(
                "ERROR",
                "PARAM-005",
                (
                    f"film_storage_horizontal.clear_depth ({clear_depth}) is below "
                    f"{min_clear_depth} mm minimum"
                ),
            )
        )
    if stack_h < min_stack_h:
        issues.append(
            ValidationIssue(
                "ERROR",
                "PARAM-005",
                (
                    f"horizontal shelf stack height ({stack_h}) is below "
                    f"{min_stack_h} mm minimum"
                ),
            )
        )

    case_width = params.value("case.width")
    if case_width != REQUIRED_CASE_WIDTH_MM:
        issues.append(
            ValidationIssue(
                "ERROR",
                "PARAM-006",
                f"case.width ({case_width}) must be exactly {REQUIRED_CASE_WIDTH_MM} mm",
            )
        )

    case_depth = params.value("case.depth")
    depth_tol = float(params.value("case.depth_tolerance_mm"))
    if (
        isinstance(case_depth, (int, float))
        and not isinstance(case_depth, bool)
        and abs(float(case_depth) - CASE_DEPTH_TARGET_MM) > depth_tol
    ):
        issues.append(
            ValidationIssue(
                "ERROR",
                "PARAM-006",
                (
                    f"case.depth ({case_depth}) must be within ±{depth_tol} mm of "
                    f"{CASE_DEPTH_TARGET_MM} mm target"
                ),
            )
        )

    case_height = params.value("case.height")
    computed_height = params.computed_case_height_mm
    if case_height != computed_height:
        issues.append(
            ValidationIssue(
                "ERROR",
                "PARAM-006",
                (
                    f"case.height ({case_height}) must equal computed stack sum "
                    f"({computed_height} mm)"
                ),
            )
        )

    upper_setback = params.value("plotter.upper_setback")
    if upper_setback != REQUIRED_UPPER_SETBACK_MM:
        issues.append(
            ValidationIssue(
                "ERROR",
                "PARAM-007",
                (
                    f"plotter.upper_setback ({upper_setback}) must be exactly "
                    f"{REQUIRED_UPPER_SETBACK_MM} mm"
                ),
            )
        )

    upper_y = params.value("plotter.upper_y")
    lower_y = params.value("plotter.lower_y")
    if upper_setback != upper_y - lower_y:
        coordinate_delta = upper_y - lower_y
        issues.append(
            ValidationIssue(
                "ERROR",
                "PARAM-008",
                (
                    f"plotter.upper_setback ({upper_setback}) must equal "
                    f"upper_y - lower_y ({coordinate_delta})"
                ),
            )
        )

    tier_min = float(params.value("plotter.tier_clearance_min_mm"))
    if params.tier_clearance_lower_mm < tier_min:
        issues.append(
            ValidationIssue(
                "ERROR",
                "PARAM-012",
                (
                    f"lower tier clearance ({params.tier_clearance_lower_mm} mm) is below "
                    f"{tier_min} mm minimum"
                ),
            )
        )
    if params.tier_clearance_upper_mm < tier_min:
        issues.append(
            ValidationIssue(
                "ERROR",
                "PARAM-012",
                (
                    f"upper tier clearance ({params.tier_clearance_upper_mm} mm) is below "
                    f"{tier_min} mm minimum"
                ),
            )
        )

    divider_thickness = params.value("film_storage_horizontal.divider_thickness")
    materials_divider = params.value("materials.divider_thickness_mm")
    if divider_thickness != materials_divider:
        issues.append(
            ValidationIssue(
                "ERROR",
                "PARAM-010",
                (
                    f"film_storage_horizontal.divider_thickness ({divider_thickness}) must equal "
                    f"materials.divider_thickness_mm ({materials_divider})"
                ),
            )
        )

    max_load = params.value("film_storage_horizontal.max_load_kg")
    marked_limit = params.value("mass_targets.film_marked_limit_kg")
    if max_load != marked_limit:
        issues.append(
            ValidationIssue(
                "ERROR",
                "PARAM-011",
                (
                    f"film_storage_horizontal.max_load_kg ({max_load}) must equal "
                    f"mass_targets.film_marked_limit_kg ({marked_limit})"
                ),
            )
        )

    if production_release:
        for leaf in params.leaves():
            if leaf.provenance == "to_measure":
                issues.append(
                    ValidationIssue(
                        "ERROR",
                        "REL-027",
                        f"{leaf.path}: to_measure parameter blocks production release",
                    )
                )

    return issues


def validate_release_readiness(
    project_doc: dict[str, Any],
    equipment_doc: dict[str, Any],
    params: Parameters,
    *,
    allow_demo: bool = False,
) -> list[ValidationIssue]:
    production_release = bool(project_doc.get("project", {}).get("production_release", False))
    issues = validate_documents(project_doc, equipment_doc, allow_demo=allow_demo)
    issues += validate_parameters(params, production_release=production_release)
    return issues
