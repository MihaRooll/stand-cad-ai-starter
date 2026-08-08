"""Indicative mass and analytical helpers — NOT authoritative for Gate G4."""

from __future__ import annotations

from dataclasses import dataclass

from stand_cad.geometry.primitives import bounding_box_bounds, bounding_box_size
from stand_cad.geometry.registry import PartRecord
from stand_cad.parameters import Parameters

EXCLUDED_MASS_MATERIALS = frozenset(
    {
        "equipment_reference",
        "reference_envelope",
        "service_volume",
    }
)

MATERIAL_DENSITY_PATHS = {
    "aluminium_angle_15x15x1.5": "materials.aluminium_density_kg_m3",
    "cast_opal_pmma_3mm": "materials.pmma_density_kg_m3",
    "white_composite_3_4mm": "materials.white_composite_density_kg_m3",
    "sandwich_panel_10_12mm": "materials.sandwich_panel_density_kg_m3",
    "transparent_petg_2mm": "materials.petg_density_kg_m3",
    "hdpe_insert_thin": "materials.hdpe_density_kg_m3",
    "silicone_foot": "materials.silicone_density_kg_m3",
    "integrated_side_handle": "materials.white_composite_density_kg_m3",
    "full_extension_slide_hardware": "materials.aluminium_density_kg_m3",
    "elastomer_soft_stop": "materials.silicone_density_kg_m3",
    "elastomer_vibration_mount": "materials.silicone_density_kg_m3",
    "interlock_shuttle_hardware": "materials.aluminium_density_kg_m3",
    "interlock_tab_hardware": "materials.aluminium_density_kg_m3",
    "soft_trim_brush": "materials.silicone_density_kg_m3",
    "hardware_mains_inlet": "materials.aluminium_density_kg_m3",
    "aluminium_stack_cap": "materials.aluminium_density_kg_m3",
}

SHELL_THICKNESS_PATHS = {
    "cast_opal_pmma_3mm": "materials.outer_panel_thickness_mm",
    "white_composite_3_4mm": "materials.inner_panel_thickness_mm",
    "sandwich_panel_10_12mm": "materials.organizer_floor_thickness_mm",
    "transparent_petg_2mm": "materials.divider_thickness_mm",
    "hdpe_insert_thin": "materials.org_insert_thickness_mm",
    "full_extension_slide_hardware": "trays.slide_rail_height_mm",
    "elastomer_soft_stop": "trays.soft_stop_size_mm",
    "elastomer_vibration_mount": "trays.vibration_mount_height_mm",
}


def _panel_shell_volume_mm3(sx: float, sy: float, sz: float, thickness_mm: float) -> float:
    """Single-face shell volume: largest face area × material thickness."""
    dims = sorted([sx, sy, sz])
    return dims[1] * dims[2] * thickness_mm


def _frame_member_volume_mm3(sx: float, sy: float, sz: float, params: Parameters) -> float:
    """Approximate equal-leg angle volume: section area × member length."""
    profile = float(params.value("materials.frame_profile_size_mm"))
    wall = float(params.value("materials.frame_wall_thickness_mm"))
    section = (2 * profile - wall) * wall
    length = max(sx, sy, sz)
    return section * length


def part_volume_mm3(record: PartRecord, params: Parameters) -> float:
    """Indicative solid/shell volume for one part — same policy as part_mass_kg."""
    if record.material in EXCLUDED_MASS_MATERIALS:
        return 0.0
    if record.material not in MATERIAL_DENSITY_PATHS:
        return 0.0
    sx, sy, sz = bounding_box_size(record.solid)
    dims = sorted([sx, sy, sz])
    if record.material == "aluminium_angle_15x15x1.5":
        return _frame_member_volume_mm3(sx, sy, sz, params)
    if record.material == "transparent_petg_2mm":
        return dims[1] * dims[2] * dims[0] / 2
    if record.material in SHELL_THICKNESS_PATHS:
        thickness_path = SHELL_THICKNESS_PATHS[record.material]
        raw_t = params.value(thickness_path)
        thickness = float(raw_t) if isinstance(raw_t, (int, float)) else dims[0]
        return _panel_shell_volume_mm3(sx, sy, sz, thickness)
    if dims[0] / dims[2] < 0.08:
        return dims[1] * dims[2] * dims[0] / 2
    return float(record.solid.volume)


def part_mass_kg(record: PartRecord, params: Parameters) -> float:
    """Indicative mass — uses shell/frame approximations, not solid-box FEA mass."""
    density_path = MATERIAL_DENSITY_PATHS.get(record.material)
    if density_path is None:
        return 0.0
    density = float(params.value(density_path))
    volume_mm3 = part_volume_mm3(record, params)
    return volume_mm3 / 1e9 * density


def density_source_for_material(material: str) -> str:
    """Return the parameters.yaml path used for a material density lookup."""
    return MATERIAL_DENSITY_PATHS.get(material, "")


@dataclass(frozen=True)
class MassReportRow:
    """One row of the indicative mass table."""

    part_id: str
    material: str
    volume_mm3: float
    density_kg_m3: float
    density_source: str
    mass_kg: float


def mass_report_rows(parts: dict[str, PartRecord], params: Parameters) -> list[MassReportRow]:
    """Per-part indicative mass rows for transport-state structural parts."""
    rows: list[MassReportRow] = []
    for part_id in sorted(parts):
        record = parts[part_id]
        if record.verify_on_real_machine:
            continue
        density_path = density_source_for_material(record.material)
        if not density_path:
            continue
        volume = part_volume_mm3(record, params)
        density = float(params.value(density_path))
        rows.append(
            MassReportRow(
                part_id=part_id,
                material=record.material,
                volume_mm3=volume,
                density_kg_m3=density,
                density_source=density_path,
                mass_kg=volume / 1e9 * density,
            )
        )
    return rows


def _solid_centroid_mm(record: PartRecord) -> tuple[float, float, float]:
    bounds = bounding_box_bounds(record.solid)
    return (
        (bounds[0][0] + bounds[0][1]) / 2,
        (bounds[1][0] + bounds[1][1]) / 2,
        (bounds[2][0] + bounds[2][1]) / 2,
    )


def weighted_centre_of_mass_mm(
    masses: list[tuple[tuple[float, float, float], float]],
) -> tuple[float, float, float]:
    """Mass-weighted centroid from (xyz, mass_kg) samples."""
    total = sum(m for _, m in masses)
    if total <= 0:
        return (0.0, 0.0, 0.0)
    x = sum(x * m for (x, _, _), m in masses) / total
    y = sum(y * m for (_, y, _), m in masses) / total
    z = sum(z * m for (_, _, z), m in masses) / total
    return (x, y, z)


def loaded_case_centre_of_mass_mm(
    parts: dict[str, PartRecord], params: Parameters
) -> tuple[float, float, float]:
    """Indicative loaded-case CoM from structural mass + both plotters (transport state)."""
    return weighted_centre_of_mass_mm(
        structural_mass_samples(parts, params) + plotter_mass_samples(parts, params)
    )


def indicative_loaded_case_com_y_mm(params: Parameters) -> float:
    """Recompute indicative loaded-case CoM Y from live transport assembly geometry."""
    from stand_cad.geometry.assembly import build_transport_assembly

    state = build_transport_assembly(params)
    return loaded_case_centre_of_mass_mm(state.parts, params)[1]


def handle_finger_intrusion_volume_mm3(
    *,
    handle_mount_y_mm: float,
    handle_mount_z_mm: float,
    grip_length_mm: float,
    grip_depth_mm: float,
    plotter_y_bounds: tuple[float, float],
    plotter_z_bounds: tuple[float, float],
    plotter_x_span_mm: float,
) -> float:
    """Axis-aligned finger-reach volume overlapping a plotter bay (Y/Z band × plotter X span).

    Models fingers passing through the side through-cutout into the interior — not the
    20 mm side-slab solid alone. Used for carry-ergonomics reporting (D-050/D-051).
    """
    y0 = handle_mount_y_mm - grip_length_mm / 2
    y1 = handle_mount_y_mm + grip_length_mm / 2
    z0 = handle_mount_z_mm - grip_depth_mm / 2
    z1 = handle_mount_z_mm + grip_depth_mm / 2
    overlap_y0 = max(y0, plotter_y_bounds[0])
    overlap_y1 = min(y1, plotter_y_bounds[1])
    overlap_z0 = max(z0, plotter_z_bounds[0])
    overlap_z1 = min(z1, plotter_z_bounds[1])
    if overlap_y1 <= overlap_y0 or overlap_z1 <= overlap_z0:
        return 0.0
    return (overlap_y1 - overlap_y0) * (overlap_z1 - overlap_z0) * plotter_x_span_mm


def structural_mass_samples(
    parts: dict[str, PartRecord], params: Parameters
) -> list[tuple[tuple[float, float, float], float]]:
    """Centroid/mass samples for structural parts included in empty-case mass."""
    samples: list[tuple[tuple[float, float, float], float]] = []
    for record in parts.values():
        if record.verify_on_real_machine:
            continue
        mass = part_mass_kg(record, params)
        if mass <= 0:
            continue
        samples.append((_solid_centroid_mm(record), mass))
    return samples


def plotter_mass_samples(
    parts: dict[str, PartRecord], params: Parameters, *, lower_extension_mm: float = 0.0
) -> list[tuple[tuple[float, float, float], float]]:
    """Point-mass samples for both plotters; slot 1 = Cameo 4, slot 2 = Cameo 5."""
    samples: list[tuple[tuple[float, float, float], float]] = []
    for index, part_id, extension in (
        (1, "EQUIP-PLOTTER1-001", lower_extension_mm),
        (2, "EQUIP-PLOTTER2-001", 0.0),
    ):
        record = parts[part_id]
        cx, cy, cz = _solid_centroid_mm(record)
        samples.append(((cx, cy + extension / 2, cz), params.plotter_mass_kg(index)))
    return samples


def empty_case_mass_kg(parts: dict[str, PartRecord], params: Parameters) -> float:
    """Indicative empty-case structural mass (excludes equipment/envelopes/service volumes)."""
    total = 0.0
    for record in parts.values():
        if record.verify_on_real_machine:
            continue
        total += part_mass_kg(record, params)
    return total


def indicative_joining_hardware_mass_kg(params: Parameters) -> float:
    """Indicative bought-in M3/M4 fasteners + corner brackets (D-061) — not modeled as solids."""
    from stand_cad.geometry.hardware import indicative_bracket_mass_kg, indicative_fastener_mass_kg

    return indicative_fastener_mass_kg(params) + indicative_bracket_mass_kg(params)


def empty_case_mass_for_stability_kg(
    parts: dict[str, PartRecord], params: Parameters
) -> float:
    """Empty-case mass for tip-over model — geometric structural + indicative joining hardware."""
    return empty_case_mass_kg(parts, params) + indicative_joining_hardware_mass_kg(params)


def indicative_tray_deflection_single_span_mm(params: Parameters) -> float:
    """Legacy single-span model (two rails only) — retained for before/after reporting."""
    load_n = float(params.value("trays.design_load_kg")) * 9.80665
    span_mm = float(params.value("plotter.physical_width"))
    thickness_mm = params.tray_panel_thickness_mm
    e_mpa = float(params.value("materials.tray_panel_youngs_modulus_mpa"))
    width_mm = float(params.value("plotter.physical_depth"))
    i_mm4 = width_mm * thickness_mm**3 / 12
    return 5 * load_n * span_mm**3 / (384 * e_mpa * i_mm4)


def indicative_tray_deflection_mm(params: Parameters) -> float:
    """Indicative tray mid-span deflection under three-rail support — NOT G4 FEA.

    Tray slides run front-to-back (Y) at left, right, and centre (X), bisecting
    the rail-to-rail span (~plotter.physical_width) into two half-spans. Load is
    distributed along Y (~plotter.physical_depth).

    Conservative hand-check simplification (not FEA, not exact continuous-beam):
    each half-span is modelled as an **independent** simply-supported beam carrying
    half the total UDL (P/2 on span L/2), ignoring elastic continuity at the centre
    support. A true two-equal-span continuous beam under UDL would give ~2.4× lower
    peak deflection; this model is therefore conservative, not optimistic.
    """
    load_n = float(params.value("trays.design_load_kg")) * 9.80665
    span_mm = float(params.value("plotter.physical_width"))
    half_span_mm = span_mm / 2
    half_load_n = load_n / 2
    thickness_mm = params.tray_panel_thickness_mm
    e_mpa = float(params.value("materials.tray_panel_youngs_modulus_mpa"))
    width_mm = float(params.value("plotter.physical_depth"))
    i_mm4 = width_mm * thickness_mm**3 / 12
    return 5 * half_load_n * half_span_mm**3 / (384 * e_mpa * i_mm4)


@dataclass(frozen=True)
class StabilityReportInputs:
    """Explicit inputs for hand-checking indicative_tip_factor()."""

    pivot_edge: str
    extended_level: str
    extension_mm: float
    structural_mass_kg: float
    plotter_mass_kg: float
    plotter_count: int
    foot_inset_mm: float
    pivot_y_mm: float
    case_depth_mm: float
    moving_mass_kg: float
    moving_cog_y_rest_mm: float
    moving_cog_y_extended_mm: float
    stationary_mass_kg: float
    stationary_cog_y_mm: float
    restore_arm_mm: float
    overturn_arm_mm: float
    total_mass_kg: float
    restore_moment_n_mm: float
    overturn_moment_n_mm: float
    factor: float
    legacy_factor: float
    applicable: bool


def _extended_tier_ids(extended_level: str) -> tuple[str, str, str, int]:
    if extended_level == "lower":
        return "TRAY-LOWER-001", "EQUIP-PLOTTER1-001", "EQUIP-PLOTTER2-001", 2
    if extended_level == "upper":
        return "TRAY-UPPER-001", "EQUIP-PLOTTER2-001", "EQUIP-PLOTTER1-001", 1
    raise ValueError(f"unknown extended_level: {extended_level}")


def _legacy_tip_factor(params: Parameters, *, extended_level: str) -> float:
    """Pre-D-039 model retained for before/after reporting only."""
    foot_inset = float(params.value("hardware.foot_diameter_mm")) / 2
    depth = float(params.value("case.depth"))
    support_y = depth / 2
    ext_key = "trays.lower_extension" if extended_level == "lower" else "trays.upper_extension"
    extension = float(params.value(ext_key))
    empty_mass = float(params.value("mass_targets.empty_case_target_max_kg"))
    plotter_mass = params.plotter_mass_kg(1) + params.plotter_mass_kg(2)
    total_mass = empty_mass + plotter_mass
    overturn_arm = extension / 2
    restore_arm = support_y - foot_inset
    g = 9.80665
    restore_moment = total_mass * g * restore_arm
    overturn_moment = total_mass * g * overturn_arm
    return restore_moment / overturn_moment if overturn_moment > 0 else float("inf")


def stability_report_inputs(
    params: Parameters,
    parts: dict[str, PartRecord],
    *,
    extended_level: str = "lower",
) -> StabilityReportInputs:
    """Return substituted numbers for stability_report.md arithmetic."""
    foot_inset = float(params.value("hardware.foot_diameter_mm")) / 2
    depth = float(params.value("case.depth"))
    pivot_y = foot_inset
    ext_key = "trays.lower_extension" if extended_level == "lower" else "trays.upper_extension"
    extension = float(params.value(ext_key))
    tray_id, plotter_id, other_plotter_id, other_plotter_index = _extended_tier_ids(
        extended_level
    )

    tray_mass = part_mass_kg(parts[tray_id], params)
    moving_plotter_mass = params.plotter_mass_kg(1 if extended_level == "lower" else 2)
    moving_mass = tray_mass + moving_plotter_mass
    tray_cog = _solid_centroid_mm(parts[tray_id])
    plotter_cog = _solid_centroid_mm(parts[plotter_id])
    moving_cog_y_rest = (
        tray_cog[1] * tray_mass + plotter_cog[1] * moving_plotter_mass
    ) / moving_mass
    moving_cog_y_extended = moving_cog_y_rest - extension

    stationary_samples: list[tuple[tuple[float, float, float], float]] = []
    for record in parts.values():
        if record.verify_on_real_machine or record.part_id == tray_id:
            continue
        mass = part_mass_kg(record, params)
        if mass <= 0:
            continue
        stationary_samples.append((_solid_centroid_mm(record), mass))
    other_plotter_mass = params.plotter_mass_kg(other_plotter_index)
    stationary_samples.append((_solid_centroid_mm(parts[other_plotter_id]), other_plotter_mass))
    joining_mass = indicative_joining_hardware_mass_kg(params)
    if joining_mass > 0:
        struct_samples = structural_mass_samples(parts, params)
        if struct_samples:
            struct_cog = weighted_centre_of_mass_mm(struct_samples)
            stationary_samples.append((struct_cog, joining_mass))
    stationary_mass = sum(mass for _, mass in stationary_samples)
    _, stationary_cog_y, _ = weighted_centre_of_mass_mm(stationary_samples)

    restore_arm = stationary_cog_y - pivot_y
    overturn_arm = pivot_y - moving_cog_y_extended
    g = 9.80665
    restore_moment = stationary_mass * g * restore_arm
    overturn_moment = moving_mass * g * overturn_arm
    factor = restore_moment / overturn_moment if overturn_moment > 0 else float("inf")

    structural_mass = empty_case_mass_for_stability_kg(parts, params)
    plotter_mass = params.plotter_mass_kg(1) + params.plotter_mass_kg(2)
    total_mass = structural_mass + plotter_mass

    applicable = extension > 0.0 and overturn_moment > 0.0

    return StabilityReportInputs(
        pivot_edge=f"front foot line (Y={foot_inset:.1f} mm, foot inset)",
        extended_level=extended_level,
        extension_mm=extension,
        structural_mass_kg=structural_mass,
        plotter_mass_kg=plotter_mass,
        plotter_count=2,
        foot_inset_mm=foot_inset,
        pivot_y_mm=pivot_y,
        case_depth_mm=depth,
        moving_mass_kg=moving_mass,
        moving_cog_y_rest_mm=moving_cog_y_rest,
        moving_cog_y_extended_mm=moving_cog_y_extended,
        stationary_mass_kg=stationary_mass,
        stationary_cog_y_mm=stationary_cog_y,
        restore_arm_mm=restore_arm,
        overturn_arm_mm=overturn_arm,
        total_mass_kg=total_mass,
        restore_moment_n_mm=restore_moment,
        overturn_moment_n_mm=overturn_moment,
        factor=factor,
        legacy_factor=_legacy_tip_factor(params, extended_level=extended_level),
        applicable=applicable,
    )


def indicative_tip_factor(
    params: Parameters,
    parts: dict[str, PartRecord],
    *,
    extended_level: str = "lower",
) -> float:
    """Indicative tip-over factor with one tray extended — NOT G4 stability analysis.

    ``float('inf')`` when overturn moment ≤ 0 is arithmetic-only; callers must check
    ``stability_report_inputs(...).applicable`` (extension > 0 and overturn moment > 0)
    before comparing to ``stability.tip_factor_min``.
    """
    return stability_report_inputs(
        params, parts, extended_level=extended_level
    ).factor
