"""Fail-closed loader and validation for config/parameters.yaml.

This module deliberately has no CAD dependency so parameter gates can be tested quickly.
Derived quantities (cell_width_mm, divider_count) are computed on access from verified
leaves — never stored as hardcoded YAML values.
"""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from .schema import ValidationIssue, validate_documents

PROVENANCE_VALUES = frozenset({"verified", "derived", "to_measure"})

# Acceptance-criteria thresholds from the TZ (not config values — see config/parameters.yaml).
CELL_WIDTH_ABSOLUTE_FLOOR_MM = 25  # TZ section 6 — minimum usable cell width
REQUIRED_CASE_ENVELOPE_MM = (650, 550, 690)  # TZ section 4
ORGANIZER_CLEAR_MIN_MM = (610, 510, 325)  # TZ section 4/6, width/depth/height
REQUIRED_UPPER_SETBACK_MM = 150  # TZ section 2/5
FILM_HEADROOM_MIN_MM = 5  # TZ line 153

PARAMETER_GROUPS = (
    "case",
    "tolerance",
    "plotter",
    "trays",
    "film_storage",
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
    def cell_width_mm(self) -> float:
        """Derived cell width: (internal_width - (cells-1)*divider_thickness) / cells."""
        internal_width = float(self.value("case.internal_width"))
        cells = int(self.value("film_storage.cells"))
        divider_thickness = float(self.value("film_storage.divider_thickness"))
        return (internal_width - (cells - 1) * divider_thickness) / cells

    @property
    def divider_count(self) -> int:
        """Derived divider count: cells - 1."""
        return int(self.value("film_storage.cells")) - 1

    @property
    def envelope_offset_x_mm(self) -> float:
        """X offset centering physical plotter in design envelope."""
        return (
            float(self.value("plotter.design_width")) - float(self.value("plotter.physical_width"))
        ) / 2

    @property
    def envelope_offset_y_mm(self) -> float:
        """Y offset centering physical plotter in design envelope."""
        return (
            float(self.value("plotter.design_depth")) - float(self.value("plotter.physical_depth"))
        ) / 2

    @property
    def envelope_offset_z_mm(self) -> float:
        """Z offset centering physical plotter in design envelope."""
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
        oz = self.envelope_offset_z_mm
        px = float(self.value("plotter.x"))
        py = float(self.value(f"plotter.{prefix}_y"))
        pz = float(self.value(f"plotter.{prefix}_z"))
        dw = float(self.value("plotter.design_width"))
        dd = float(self.value("plotter.design_depth"))
        dh = float(self.value("plotter.design_height"))
        return (
            (px - ox, px - ox + dw),
            (py - oy, py - oy + dd),
            (pz - oz, pz - oz + dh),
        )

    def plotter_physical_bounds(self, index: int) -> tuple[tuple[float, float], ...]:
        """Return ((x_min, x_max), (y_min, y_max), (z_min, z_max)) for plotter 1 or 2 body."""
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
        """Vertical clearance between plotter 1 and 2 design envelopes (Parameters-derived)."""
        env1 = self.plotter_envelope_bounds(1)
        env2 = self.plotter_envelope_bounds(2)
        return env2[2][0] - env1[2][1]

    @property
    def tray_panel_thickness_mm(self) -> float:
        """Midpoint of tray sandwich panel thickness range for concept geometry."""
        t_min = float(self.value("materials.tray_panel_thickness_min_mm"))
        t_max = float(self.value("materials.tray_panel_thickness_max_mm"))
        return (t_min + t_max) / 2

    @property
    def interlock_tab_engagement_mm(self) -> float:
        """Tab protrusion derived from assembly-feature tolerance."""
        return 6 * float(self.value("tolerance.part_assembly_feature_mm"))

    @property
    def interlock_shuttle_travel_mm(self) -> float:
        """Vertical shuttle travel between neutral and block positions."""
        lower_slide_z = float(self.value("plotter.lower_z")) - self.tray_panel_thickness_mm
        upper_slide_z = float(self.value("plotter.upper_z")) - self.tray_panel_thickness_mm
        slide_h = float(self.value("trays.slide_rail_height_mm"))
        return (upper_slide_z - lower_slide_z - slide_h) / 2

    @property
    def interlock_shuttle_channel_width_mm(self) -> float:
        """Compact captive-channel width for INTERLOCK-SHUTTLE-001."""
        return 4 * self.interlock_tab_engagement_mm

    @property
    def org_insert_thickness_mm(self) -> float:
        """HDPE insert thickness; uses documented provisional when leaf is TO_MEASURE."""
        val = self.value("materials.org_insert_thickness_mm")
        if isinstance(val, (int, float)) and not isinstance(val, bool):
            return float(val)
        return float(self.value("materials.org_insert_provisional_mm"))

    @property
    def comb_slot_clearance_mm(self) -> float:
        """Slot clearance derived from assembly-feature tolerance."""
        return float(self.value("tolerance.part_assembly_feature_mm"))

    @property
    def divider_height_mm(self) -> float:
        """Midpoint of divider height range for concept geometry."""
        h_min = float(self.value("film_storage.divider_height_min"))
        h_max = float(self.value("film_storage.divider_height_max"))
        return (h_min + h_max) / 2

    @property
    def front_retainer_height_mm(self) -> float:
        """Midpoint of front retainer height range."""
        h_min = float(self.value("film_storage.front_retainer_height_min"))
        h_max = float(self.value("film_storage.front_retainer_height_max"))
        return (h_min + h_max) / 2

    @property
    def finger_cutout_radius_mm(self) -> float:
        """Midpoint of divider finger-cutout radius range for concept geometry."""
        r_min = float(self.value("film_storage.finger_cutout_radius_min"))
        r_max = float(self.value("film_storage.finger_cutout_radius_max"))
        return (r_min + r_max) / 2

    @property
    def film_headroom_mm(self) -> float:
        """Vertical clearance above design film height inside organizer."""
        return float(self.value("film_storage.clear_height")) - float(
            self.value("film_storage.film_design_height")
        )


def with_cells(params: Parameters, cells: int) -> Parameters:
    """Return a Parameters copy with film_storage.cells overridden."""
    raw = deepcopy(params._raw)
    section = raw.setdefault("film_storage", {})
    leaf = section.get("cells", {})
    section["cells"] = {
        "value": cells,
        "provenance": leaf.get("provenance", "verified"),
        "note": leaf.get("note", ""),
    }
    return Parameters(raw)


def load_parameters(path: str | Path) -> Parameters:
    """Load parameters from a UTF-8 YAML file."""
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
    """Validate parameters fail-closed; collect all issues in one pass."""
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

    cells = params.value("film_storage.cells")
    if not isinstance(cells, int) or isinstance(cells, bool) or not 6 <= cells <= 12:
        issues.append(
            ValidationIssue(
                "ERROR",
                "PARAM-002",
                "film_storage.cells must be an integer in [6, 12]",
            )
        )

    cell_width = params.cell_width_mm
    if cell_width < CELL_WIDTH_ABSOLUTE_FLOOR_MM:
        issues.append(
            ValidationIssue(
                "ERROR",
                "PARAM-003",
                (
                    f"cell_width_mm ({cell_width}) is below the "
                    f"{CELL_WIDTH_ABSOLUTE_FLOOR_MM} mm absolute floor"
                ),
            )
        )

    min_stack = params.value("film_storage.min_stack_width_mm")
    if isinstance(min_stack, (int, float)) and not isinstance(min_stack, bool):
        if cell_width < float(min_stack):
            issues.append(
                ValidationIssue(
                    "ERROR",
                    "PARAM-004",
                    (
                        f"cell_width_mm ({cell_width}) is below "
                        f"film_storage.min_stack_width_mm ({min_stack})"
                    ),
                )
            )

    clear_width = params.value("film_storage.clear_width")
    clear_depth = params.value("film_storage.clear_depth")
    clear_height = params.value("film_storage.clear_height")
    min_clear_width, min_clear_depth, min_clear_height = ORGANIZER_CLEAR_MIN_MM
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
                    f"film_storage.clear_width ({clear_width}) is below "
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
                    f"film_storage.clear_depth ({clear_depth}) is below "
                    f"{min_clear_depth} mm minimum"
                ),
            )
        )
    if (
        isinstance(clear_height, (int, float))
        and not isinstance(clear_height, bool)
        and clear_height < min_clear_height
    ):
        issues.append(
            ValidationIssue(
                "ERROR",
                "PARAM-005",
                (
                    f"film_storage.clear_height ({clear_height}) is below "
                    f"{min_clear_height} mm minimum"
                ),
            )
        )

    envelope = (
        params.value("case.width"),
        params.value("case.depth"),
        params.value("case.height"),
    )
    if envelope != REQUIRED_CASE_ENVELOPE_MM:
        issues.append(
            ValidationIssue(
                "ERROR",
                "PARAM-006",
                (
                    f"case envelope {envelope} must be exactly "
                    f"{REQUIRED_CASE_ENVELOPE_MM}"
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

    film_design_height = params.value("film_storage.film_design_height")
    headroom = clear_height - film_design_height
    if headroom < FILM_HEADROOM_MIN_MM:
        issues.append(
            ValidationIssue(
                "ERROR",
                "PARAM-009",
                (
                    f"film headroom ({headroom} mm) is below "
                    f"{FILM_HEADROOM_MIN_MM} mm minimum"
                ),
            )
        )

    divider_thickness = params.value("film_storage.divider_thickness")
    materials_divider = params.value("materials.divider_thickness_mm")
    if divider_thickness != materials_divider:
        issues.append(
            ValidationIssue(
                "ERROR",
                "PARAM-010",
                (
                    f"film_storage.divider_thickness ({divider_thickness}) must equal "
                    f"materials.divider_thickness_mm ({materials_divider})"
                ),
            )
        )

    max_load = params.value("film_storage.max_load_kg")
    marked_limit = params.value("mass_targets.film_marked_limit_kg")
    if max_load != marked_limit:
        issues.append(
            ValidationIssue(
                "ERROR",
                "PARAM-011",
                (
                    f"film_storage.max_load_kg ({max_load}) must equal "
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
    """Combined production gate: project/equipment docs plus parameter validation."""
    production_release = bool(project_doc.get("project", {}).get("production_release", False))
    issues = validate_documents(project_doc, equipment_doc, allow_demo=allow_demo)
    issues += validate_parameters(params, production_release=production_release)
    return issues
