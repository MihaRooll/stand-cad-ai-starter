"""Fail-closed loader and validation for config/parameters.yaml.

YAML loading, schema validation, and the bulk of ``validate_parameters`` have no CAD
dependency and stay fast. The exception is ``computed_handle_mount_y_mm`` (and therefore
the ``PARAM-017`` handle-Y check that calls it): it lazily imports and builds the full
transport CAD assembly to compute an indicative loaded centre-of-mass — see that
property's docstring for why.

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
CASE_DEPTH_TARGET_MM = 420  # Owner 2026-08-05 override (D-045); supersedes TZ 550 mm target
REQUIRED_UPPER_SETBACK_MM = 0  # D-033 — tiers aligned; supersedes 130 mm (D-029) and TZ 150 mm
MIN_LOWER_QUICK_ACCESS_EXTENSION_MM = 130  # D-033 — minimum tier-1 quick-access forward slide
HORIZONTAL_ORGANIZER_CLEAR_MIN_MM = (610, 330, 100)  # width, depth, stack height (4×25 mm)
HORIZONTAL_SHELF_COUNT = 4  # Owner 2026-08-04 verified default

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
    "stacking",
    "joints",
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
        """Upper tray datum: lower_z + tier_clearance_min + slide + profile + tray."""
        lower_z = float(self.value("plotter.lower_z"))
        tier_min = float(self.value("plotter.tier_clearance_min_mm"))
        slide_h = float(self.value("trays.slide_rail_height_mm"))
        profile = float(self.value("materials.frame_profile_size_mm"))
        return lower_z + tier_min + slide_h + profile + self.tray_panel_thickness_mm

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

    def plotter_height_mm(self, index: int) -> float:
        """Per-slot body height — slot 1 Cameo 4 (170 mm), slot 2 Cameo 5 (124 mm).

        Tier design envelopes still use ``tier_envelope_height_mm`` (governing Cameo 4 height)
        so either machine can occupy either slot; only the actual EQUIP-PLOTTERn solid uses this.
        """
        if index == 1:
            return float(self.value("plotter_cameo4.height_mm"))
        if index == 2:
            return float(self.value("plotter_cameo5.height_mm"))
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
        """Side panel vertical centre from foot top to case height (D-030 legacy reference)."""
        foot_h = float(self.value("materials.foot_height_mm"))
        height = float(self.value("case.height"))
        return (foot_h + height) / 2

    @property
    def computed_geometric_depth_centre_y_mm(self) -> float:
        """Geometric case depth centre from front face (Y=0); legacy D-050 reference."""
        return float(self.value("case.depth")) / 2.0

    @property
    def computed_handle_mount_y_mm(self) -> float:
        """Handle mount Y — indicative loaded-case CoM Y for level carry (D-051).

        Recomputed from live transport mass model; stored ``hardware.handle_mount_y_mm``
        must track within ``tolerance.part_assembly_feature_mm`` (see
        ``test_handle_mount_y_at_loaded_com``). Not derived live at build time because
        the through-cutout removes material and would create a circular dependency if
        the handle position fed back into the same assembly's mass centroid.
        """
        from stand_cad.geometry.analysis import indicative_loaded_case_com_y_mm

        return indicative_loaded_case_com_y_mm(self)

    @property
    def computed_handle_mount_z_mm(self) -> float:
        """Handle mount Z — lowest sightline-feasible band at depth-centred Y.

        ``upper_z + slide_rail_height_mm + 2 mm`` clears tier-2 tray cladding and
        ``PANEL-IN-MID-001`` in the through-ray grid. Z=218–220 mm clears both plotter
        finger envelopes but fails ``test_handle_cutout_sightline_clear``.
        """
        upper_z = float(self.value("plotter.upper_z"))
        slide_h = float(self.value("trays.slide_rail_height_mm"))
        return upper_z + slide_h + 2.0

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
        ph = self.plotter_height_mm(index)
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


def _required(
    params: Parameters,
    path: str,
    issues: list[ValidationIssue],
    *,
    code: str = "PARAM-000",
) -> Any:
    try:
        return params.value(path)
    except KeyError:
        issues.append(ValidationIssue("ERROR", code, f"{path}: required leaf is missing"))
        return None


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

    shelf_count = _required(
        params, "film_storage_horizontal.shelf_count", issues, code="PARAM-002"
    )
    if shelf_count is not None and (
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

    clear_width = _required(
        params, "film_storage_horizontal.clear_width", issues, code="PARAM-005"
    )
    clear_depth = _required(
        params, "film_storage_horizontal.clear_depth", issues, code="PARAM-005"
    )
    stack_h: float | None = None
    if shelf_count is not None:
        try:
            stack_h = params.horizontal_shelf_stack_height_mm
        except KeyError as exc:
            issues.append(
                ValidationIssue(
                    "ERROR",
                    "PARAM-000",
                    f"{exc.args[0]}: required leaf is missing",
                )
            )
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
    if stack_h is not None and stack_h < min_stack_h:
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

    case_width = _required(params, "case.width", issues, code="PARAM-006")
    if case_width is not None and case_width != REQUIRED_CASE_WIDTH_MM:
        issues.append(
            ValidationIssue(
                "ERROR",
                "PARAM-006",
                f"case.width ({case_width}) must be exactly {REQUIRED_CASE_WIDTH_MM} mm",
            )
        )

    case_depth = _required(params, "case.depth", issues, code="PARAM-006")
    depth_tol_raw = _required(params, "case.depth_tolerance_mm", issues, code="PARAM-006")
    if (
        case_depth is not None
        and depth_tol_raw is not None
        and isinstance(case_depth, (int, float))
        and not isinstance(case_depth, bool)
    ):
        depth_tol = float(depth_tol_raw)
        if abs(float(case_depth) - CASE_DEPTH_TARGET_MM) > depth_tol:
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

    case_height = _required(params, "case.height", issues, code="PARAM-006")
    computed_height: float | None = None
    if case_height is not None:
        try:
            computed_height = params.computed_case_height_mm
        except KeyError as exc:
            issues.append(
                ValidationIssue(
                    "ERROR",
                    "PARAM-000",
                    f"{exc.args[0]}: required leaf is missing",
                )
            )
    if case_height is not None and computed_height is not None and case_height != computed_height:
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

    upper_setback = _required(params, "plotter.upper_setback", issues, code="PARAM-007")
    if upper_setback is not None and upper_setback != REQUIRED_UPPER_SETBACK_MM:
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

    upper_y = _required(params, "plotter.upper_y", issues, code="PARAM-008")
    lower_y = _required(params, "plotter.lower_y", issues, code="PARAM-008")
    if (
        upper_setback is not None
        and upper_y is not None
        and lower_y is not None
        and upper_setback != upper_y - lower_y
    ):
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

    quick_access_ext = _required(
        params, "trays.lower_quick_access_extension_mm", issues, code="PARAM-013"
    )
    lower_extension = _required(params, "trays.lower_extension", issues, code="PARAM-014")
    if (
        quick_access_ext is not None
        and isinstance(quick_access_ext, (int, float))
        and not isinstance(quick_access_ext, bool)
        and quick_access_ext < MIN_LOWER_QUICK_ACCESS_EXTENSION_MM
    ):
        issues.append(
            ValidationIssue(
                "ERROR",
                "PARAM-013",
                (
                    f"trays.lower_quick_access_extension_mm ({quick_access_ext}) is below "
                    f"{MIN_LOWER_QUICK_ACCESS_EXTENSION_MM} mm minimum"
                ),
            )
        )
    if (
        quick_access_ext is not None
        and isinstance(quick_access_ext, (int, float))
        and not isinstance(quick_access_ext, bool)
        and lower_extension is not None
        and isinstance(lower_extension, (int, float))
        and not isinstance(lower_extension, bool)
        and quick_access_ext >= lower_extension
    ):
        issues.append(
            ValidationIssue(
                "ERROR",
                "PARAM-014",
                (
                    f"trays.lower_quick_access_extension_mm ({quick_access_ext}) must be less than "
                    f"trays.lower_extension ({lower_extension})"
                ),
            )
        )

    overhang_min_raw = _required(params, "trays.front_overhang_min_mm", issues, code="PARAM-015")
    physical_depth_raw = _required(params, "plotter.physical_depth", issues, code="PARAM-015")
    if overhang_min_raw is not None and physical_depth_raw is not None:
        overhang_min = float(overhang_min_raw)
        physical_depth = float(physical_depth_raw)
        for tier_label, ext_key, y_key in (
            ("lower", "trays.lower_extension", "plotter.lower_y"),
            ("upper", "trays.upper_extension", "plotter.upper_y"),
        ):
            extension = _required(params, ext_key, issues, code="PARAM-015")
            tier_y_raw = _required(params, y_key, issues, code="PARAM-015")
            if extension is None or tier_y_raw is None:
                continue
            tier_y = float(tier_y_raw)
            if isinstance(extension, (int, float)) and not isinstance(extension, bool):
                if tier_label == "upper" and float(extension) <= 0.0:
                    continue  # D-076 — upper tier fixed; TZ overhang check N/A at zero travel
                front_y = tier_y - float(extension)
                rear_y = front_y + physical_depth
                if rear_y > -overhang_min:
                    issues.append(
                        ValidationIssue(
                            "ERROR",
                            "PARAM-015",
                            (
                                f"{ext_key} ({extension}) leaves {tier_label}-tier plotter "
                                f"rear at Y={rear_y:.1f} mm — must be ≤ "
                                f"−{overhang_min:.0f} mm (TZ front_overhang_min_mm) "
                                f"at full service extension"
                            ),
                        )
                    )
                # PARAM-016 is dominated by PARAM-015 under sane inputs: rear_y =
                # front_y + physical_depth, so front_y > 0 always implies rear_y >
                # physical_depth > -overhang_min. Retained as a clearer front-face message
                # when both fire; it never triggers independently of PARAM-015.
                if front_y > 0.0:
                    issues.append(
                        ValidationIssue(
                            "ERROR",
                            "PARAM-016",
                            (
                                f"{ext_key} ({extension}) leaves {tier_label}-tier plotter "
                                f"front at Y={front_y:.1f} mm — must be ≤ 0 mm (clear of case "
                                f"front) at full service extension"
                            ),
                        )
                    )

    tier_min_raw = _required(params, "plotter.tier_clearance_min_mm", issues, code="PARAM-012")
    if tier_min_raw is not None:
        tier_min = float(tier_min_raw)
        try:
            tier_clearance_lower = params.tier_clearance_lower_mm
        except KeyError as exc:
            issues.append(
                ValidationIssue(
                    "ERROR",
                    "PARAM-000",
                    f"{exc.args[0]}: required leaf is missing",
                )
            )
        else:
            if tier_clearance_lower < tier_min:
                issues.append(
                    ValidationIssue(
                        "ERROR",
                        "PARAM-012",
                        (
                            f"lower tier clearance ({tier_clearance_lower} mm) is below "
                            f"{tier_min} mm minimum"
                        ),
                    )
                )
        try:
            tier_clearance_upper = params.tier_clearance_upper_mm
        except KeyError as exc:
            issues.append(
                ValidationIssue(
                    "ERROR",
                    "PARAM-000",
                    f"{exc.args[0]}: required leaf is missing",
                )
            )
        else:
            if tier_clearance_upper < tier_min:
                issues.append(
                    ValidationIssue(
                        "ERROR",
                        "PARAM-012",
                        (
                            f"upper tier clearance ({tier_clearance_upper} mm) is below "
                            f"{tier_min} mm minimum"
                        ),
                    )
                )

    divider_thickness = _required(
        params, "film_storage_horizontal.divider_thickness", issues, code="PARAM-010"
    )
    materials_divider = _required(
        params, "materials.divider_thickness_mm", issues, code="PARAM-010"
    )
    if (
        divider_thickness is not None
        and materials_divider is not None
        and divider_thickness != materials_divider
    ):
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

    try:
        slot_height = params.value("media_path.slot_height_target")
        clear_height_min = params.value("media_path.clear_height_min")
    except KeyError:
        pass
    else:
        if (
            isinstance(slot_height, (int, float))
            and not isinstance(slot_height, bool)
            and isinstance(clear_height_min, (int, float))
            and not isinstance(clear_height_min, bool)
            and float(slot_height) < float(clear_height_min)
        ):
            issues.append(
                ValidationIssue(
                    "ERROR",
                    "PARAM-018",
                    (
                        f"media_path.slot_height_target ({slot_height}) must be ≥ "
                        f"media_path.clear_height_min ({clear_height_min})"
                    ),
                )
            )

    max_load = _required(
        params, "film_storage_horizontal.max_load_kg", issues, code="PARAM-011"
    )
    marked_limit = _required(params, "mass_targets.film_marked_limit_kg", issues, code="PARAM-011")
    if max_load is not None and marked_limit is not None and max_load != marked_limit:
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

    try:
        handle_y = params.value("hardware.handle_mount_y_mm")
    except KeyError:
        pass
    else:
        try:
            computed_handle_y = params.computed_handle_mount_y_mm
            com_y_tol_raw = _required(
                params, "tolerance.part_assembly_feature_mm", issues, code="PARAM-000"
            )
        except KeyError as exc:
            issues.append(
                ValidationIssue(
                    "ERROR",
                    "PARAM-000",
                    f"{exc.args[0]}: required leaf is missing",
                )
            )
        else:
            if com_y_tol_raw is not None and (
                isinstance(handle_y, (int, float))
                and not isinstance(handle_y, bool)
                and abs(float(handle_y) - computed_handle_y) > float(com_y_tol_raw)
            ):
                issues.append(
                    ValidationIssue(
                        "ERROR",
                        "PARAM-017",
                        (
                            f"hardware.handle_mount_y_mm ({handle_y}) must track indicative "
                            f"loaded-case CoM Y ({computed_handle_y:.2f} mm) within "
                            f"{float(com_y_tol_raw)} mm"
                        ),
                    )
                )

    try:
        handle_z = params.value("hardware.handle_mount_z_mm")
    except KeyError:
        pass
    else:
        try:
            computed_handle_z = params.computed_handle_mount_z_mm
        except KeyError as exc:
            issues.append(
                ValidationIssue(
                    "ERROR",
                    "PARAM-000",
                    f"{exc.args[0]}: required leaf is missing",
                )
            )
        else:
            if (
                isinstance(handle_z, (int, float))
                and not isinstance(handle_z, bool)
                and float(handle_z) != computed_handle_z
            ):
                issues.append(
                    ValidationIssue(
                        "ERROR",
                        "PARAM-017",
                        (
                            f"hardware.handle_mount_z_mm ({handle_z}) must equal "
                            f"upper_z + slide_rail_height_mm + 2 ({computed_handle_z} mm)"
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
