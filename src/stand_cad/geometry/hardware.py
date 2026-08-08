"""Feet, handles, fasteners, and weld-free joint registry (D-061)."""

from __future__ import annotations

from dataclasses import dataclass

from build123d import Align, Box, Cylinder, Location, Part

from stand_cad.geometry.datums import Datums
from stand_cad.geometry.primitives import box_from_bounds
from stand_cad.geometry.registry import PartRecord
from stand_cad.parameters import Parameters

FOOT_MATERIAL = "silicone_foot"
BRACKET_MATERIAL = "aluminium_angle_15x15x1.5"
STACK_CAP_MATERIAL = "aluminium_stack_cap"

JOINT_TYPE_IDS = (
    "JT-FRAME-CORNER",
    "JT-TRAY-RAIL-FRAME",
    "JT-PANEL-OUTER-FRAME",
    "JT-PANEL-INNER-FRAME",
    "JT-TRAY-SLIDE-FRAME",
    "JT-SHELF-SUPPORT-SKIN",
    "JT-STACK-CAP-POST",
    "JT-HANDLE-HARDWARE",
)


@dataclass(frozen=True)
class JointTypeSpec:
    """One weld-free joint type from config/parameters.yaml joints.*."""

    joint_type_id: str
    part_a_pattern: str
    part_b_pattern: str
    method: str
    fastener_type: str
    fastener_size: str
    qty_per_joint: int
    length_leaf: str
    torque_leaf: str


def _joint_leaf(params: Parameters, joint_id: str, field: str) -> str:
    return str(params.value(f"joints.{joint_id}.{field}"))


def joint_type_registry(params: Parameters) -> list[JointTypeSpec]:
    """Load all joint type specs from parameters.yaml."""
    specs: list[JointTypeSpec] = []
    for joint_id in JOINT_TYPE_IDS:
        specs.append(
            JointTypeSpec(
                joint_type_id=_joint_leaf(params, joint_id, "joint_type_id"),
                part_a_pattern=_joint_leaf(params, joint_id, "part_a_pattern"),
                part_b_pattern=_joint_leaf(params, joint_id, "part_b_pattern"),
                method=_joint_leaf(params, joint_id, "method"),
                fastener_type=_joint_leaf(params, joint_id, "fastener_type"),
                fastener_size=_joint_leaf(params, joint_id, "fastener_size"),
                qty_per_joint=int(params.value(f"joints.{joint_id}.qty_per_joint")),
                length_leaf=_joint_leaf(params, joint_id, "length_leaf"),
                torque_leaf=_joint_leaf(params, joint_id, "torque_leaf"),
            )
        )
    return specs


def perimeter_rail_count() -> int:
    """BASE(4) + ORG(4) + TOP(3, no front per D-044)."""
    return 11


def tray_rail_count() -> int:
    """LOWER/UPPER × L/R/C."""
    return 6


def joint_instance_counts(params: Parameters) -> dict[str, int]:
    """Indicative instance counts for BOM/fastener mass — not shop-floor pick lists."""
    pitch = float(params.value("hardware.fastener_panel_pitch_mm"))
    width = float(params.value("case.width"))
    depth = float(params.value("case.depth"))
    height = float(params.value("case.height"))
    # Perimeter rail ends (BASE/ORG/TOP rings only — tray rails use JT-TRAY-RAIL-FRAME).
    perimeter_corners = perimeter_rail_count() * 2
    tray_rail_corners = tray_rail_count() * 2
    # Outer panels: left/right long edges + rear perimeter (approximate screw stations).
    side_edge = max(2, int(height / pitch) + 1)
    side_depth_edge = max(2, int(depth / pitch) + 1)
    outer_screws = 2 * (side_edge + side_depth_edge) + max(2, int(width / pitch) + 1)
    # Inner panels (3 panels, perimeter estimate).
    inner_screws = 3 * max(4, int((width + depth) / pitch))
    # Slides: 6 rails × 4 holes each (typical full-extension pair) until datasheet known.
    slide_holes = tray_rail_count() * 4
    # Shelf supports: 6 cleats (L/R × 3 shelves).
    shelf_cleats = 6
    return {
        "JT-FRAME-CORNER": perimeter_corners,
        "JT-TRAY-RAIL-FRAME": tray_rail_corners,
        "JT-PANEL-OUTER-FRAME": outer_screws,
        "JT-PANEL-INNER-FRAME": inner_screws,
        "JT-TRAY-SLIDE-FRAME": slide_holes,
        "JT-SHELF-SUPPORT-SKIN": shelf_cleats,
        "JT-STACK-CAP-POST": 4,
        "JT-HANDLE-HARDWARE": 0,
    }


def total_fastener_count(params: Parameters) -> int:
    """Total indicative screw count across joint types in ``joints.*``."""
    counts = joint_instance_counts(params)
    total = 0
    for spec in joint_type_registry(params):
        total += counts[spec.joint_type_id] * spec.qty_per_joint
    return total


def supplementary_fastener_instances(params: Parameters) -> tuple[int, int]:
    """Extra fasteners decided in docs/15 but not encoded as ``joints.*`` types."""
    foot_m4 = 4
    # PANEL-CLAD-FRONT-BASE-001 removed (D-069) — no supplementary M3 cladding line.
    base_clad_m3 = 0
    return foot_m4, base_clad_m3


def indicative_fastener_roll_up(params: Parameters) -> dict[str, int | float]:
    """Registry + supplementary FOOT/base-cladding counts for BOM honesty (D-065)."""
    m4_count = 0
    m3_count = 0
    counts = joint_instance_counts(params)
    for spec in joint_type_registry(params):
        n = counts[spec.joint_type_id] * spec.qty_per_joint
        if spec.fastener_size == "M4":
            m4_count += n
        elif spec.fastener_size == "M3":
            m3_count += n
    foot_m4, base_clad_m3 = supplementary_fastener_instances(params)
    m4_count += foot_m4
    m3_count += base_clad_m3
    mass_kg = indicative_fastener_mass_kg(params)
    foot_m4_len = float(params.value("hardware.fastener_m4_pan_head_length_mm"))
    m3_len = float(params.value("hardware.fastener_m3_pan_head_length_mm"))
    m4_d = float(params.value("hardware.fastener_m4_nominal_diameter_mm"))
    m3_d = float(params.value("hardware.fastener_m3_nominal_diameter_mm"))
    density_kg_m3 = 7850.0
    extra_vol = foot_m4 * 3.14159 * (m4_d / 2) ** 2 * foot_m4_len
    extra_vol += base_clad_m3 * 3.14159 * (m3_d / 2) ** 2 * m3_len
    mass_kg += extra_vol / 1e9 * density_kg_m3
    return {
        "m4": m4_count,
        "m3": m3_count,
        "total": m4_count + m3_count,
        "registry_total": total_fastener_count(params),
        "supplementary_m4": foot_m4,
        "supplementary_m3": base_clad_m3,
        "mass_kg": mass_kg,
    }


def indicative_fastener_mass_kg(params: Parameters) -> float:
    """Indicative bought-in fastener mass (M3/M4 steel screws, excl. brackets)."""
    density_kg_m3 = 7850.0
    m4_len = float(params.value("hardware.fastener_m4_pan_head_length_mm"))
    m3_len = float(params.value("hardware.fastener_m3_pan_head_length_mm"))
    m4_d = float(params.value("hardware.fastener_m4_nominal_diameter_mm"))
    m3_d = float(params.value("hardware.fastener_m3_nominal_diameter_mm"))
    counts = joint_instance_counts(params)
    m4_count = 0
    m3_count = 0
    for spec in joint_type_registry(params):
        n = counts[spec.joint_type_id] * spec.qty_per_joint
        if spec.fastener_size == "M4":
            m4_count += n
        elif spec.fastener_size == "M3":
            m3_count += n
    m4_vol = m4_count * 3.14159 * (m4_d / 2) ** 2 * m4_len
    m3_vol = m3_count * 3.14159 * (m3_d / 2) ** 2 * m3_len
    return (m4_vol + m3_vol) / 1e9 * density_kg_m3


def indicative_bracket_mass_kg(params: Parameters) -> float:
    """Indicative corner-bracket mass (20×20×2 mm L-gusset per rail-end node)."""
    leg = float(params.value("hardware.corner_bracket_leg_mm"))
    thick = float(params.value("hardware.corner_bracket_thickness_mm"))
    density = float(params.value("materials.aluminium_density_kg_m3"))
    count = (
        joint_instance_counts(params)["JT-FRAME-CORNER"]
        + joint_instance_counts(params)["JT-TRAY-RAIL-FRAME"]
    )
    # L-bracket ≈ two legs minus overlap corner.
    vol_mm3 = count * (2 * leg * thick * leg - thick**3)
    return vol_mm3 / 1e9 * density


def _foot_center_xy(
    suffix: str, *, width: float, depth: float, foot_diameter: float
) -> tuple[float, float]:
    """Foot disk centre — matches build_feet inset = diameter/2 (not corner_radius)."""
    inset = foot_diameter / 2.0
    centers = {
        "FL": (inset, inset),
        "FR": (width - inset, inset),
        "RL": (inset, depth - inset),
        "RR": (width - inset, depth - inset),
    }
    return centers[suffix]


def _stack_cap_plate_bounds(
    suffix: str, *, plate_size: float, width: float, depth: float
) -> tuple[float, float, float, float]:
    """XY bounds for cap plate covering the post L envelope at one corner."""
    if suffix == "FL":
        return (0.0, 0.0, plate_size, plate_size)
    if suffix == "FR":
        return (width - plate_size, 0.0, width, plate_size)
    if suffix == "RL":
        return (0.0, depth - plate_size, plate_size, depth)
    if suffix == "RR":
        return (width - plate_size, depth - plate_size, width, depth)
    raise ValueError(f"unknown stack cap suffix: {suffix}")


def _stack_cap_notch_boss_bounds(
    suffix: str,
    *,
    profile: float,
    plate_size: float,
    width: float,
    depth: float,
) -> tuple[float, float, float, float]:
    """XY bounds of the post L-notch void under the cap (region with no post material below)."""
    if suffix == "FL":
        return (profile, profile, plate_size, plate_size)
    if suffix == "FR":
        return (width - plate_size, profile, width - profile, plate_size)
    if suffix == "RL":
        return (profile, depth - profile, plate_size, depth)
    if suffix == "RR":
        return (width - plate_size, depth - profile, width - profile, depth)
    raise ValueError(f"unknown stack cap suffix: {suffix}")


def _build_single_stack_cap(
    params: Parameters,
    datums: Datums,
    suffix: str,
) -> PartRecord:
    """Solid Al bearing plate + shallow foot-registration recess (STACK-001)."""
    plate_size = float(params.value("stacking.cap_plate_size_mm"))
    thickness = float(params.value("stacking.cap_thickness_mm"))
    recess_depth = float(params.value("stacking.foot_recess_depth_mm"))
    clearance = float(params.value("stacking.foot_recess_clearance_mm"))
    boss_depth = float(params.value("stacking.notch_boss_depth_mm"))
    profile = float(params.value("materials.frame_profile_size_mm"))
    foot_diameter = float(params.value("hardware.foot_diameter_mm"))
    width = datums.case_envelope.x.max_mm
    depth = datums.case_envelope.y.max_mm
    z_base = float(params.value("case.height"))

    x0, y0, x1, y1 = _stack_cap_plate_bounds(
        suffix, plate_size=plate_size, width=width, depth=depth
    )
    solid: Part = box_from_bounds(x0, y0, z_base, x1, y1, z_base + thickness)

    bx0, by0, bx1, by1 = _stack_cap_notch_boss_bounds(
        suffix,
        profile=profile,
        plate_size=plate_size,
        width=width,
        depth=depth,
    )
    if boss_depth > 0.0 and bx1 > bx0 and by1 > by0:
        boss = box_from_bounds(bx0, by0, z_base - boss_depth, bx1, by1, z_base)
        solid = solid + boss

    cx, cy = _foot_center_xy(
        suffix, width=width, depth=depth, foot_diameter=foot_diameter
    )
    recess_radius = max(0.0, (foot_diameter + clearance) / 2.0)
    if recess_depth > 0.0 and recess_radius > 0.0:
        cutter = Cylinder(
            recess_radius,
            recess_depth + 0.01,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
        ).move(Location((cx, cy, z_base + thickness - recess_depth)))
        solid = solid - cutter

    return PartRecord(
        part_id=f"STACK-CAP-{suffix}-001",
        material=STACK_CAP_MATERIAL,
        solid=solid,
    )


def build_stack_caps(params: Parameters, datums: Datums) -> list[PartRecord]:
    """Four weld-free stacking interface caps at case top corners (D-064)."""
    return [_build_single_stack_cap(params, datums, suffix) for suffix in ("FL", "FR", "RL", "RR")]


def build_feet(params: Parameters, datums: Datums) -> list[PartRecord]:
    diameter = float(params.value("hardware.foot_diameter_mm"))
    height = float(params.value("materials.foot_height_mm"))
    width = datums.case_envelope.x.max_mm
    depth = datums.case_envelope.y.max_mm
    inset = diameter / 2
    corners = [
        ("FOOT-001", inset - diameter / 2, inset - diameter / 2),
        ("FOOT-002", width - inset - diameter / 2, inset - diameter / 2),
        ("FOOT-003", inset - diameter / 2, depth - inset - diameter / 2),
        ("FOOT-004", width - inset - diameter / 2, depth - inset - diameter / 2),
    ]
    parts: list[PartRecord] = []
    radius = diameter / 2.0
    for part_id, x0, y0 in corners:
        cx = x0 + radius
        cy = y0 + radius
        solid = Cylinder(
            radius,
            height,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
        ).move(Location((cx, cy, 0.0)))
        parts.append(PartRecord(part_id=part_id, material=FOOT_MATERIAL, solid=solid))
    return parts


def _build_corner_bracket_solid(
    params: Parameters,
    *,
    x: float,
    y: float,
    z: float,
    leg_x: float,
    leg_y: float,
) -> object:
    """Lightweight L-bracket solid for mass/BOM honesty (CONCEPT only)."""
    leg = float(params.value("hardware.corner_bracket_leg_mm"))
    thick = float(params.value("hardware.corner_bracket_thickness_mm"))
    leg_a = Box(leg, thick, leg, align=(Align.MIN, Align.MIN, Align.MIN)).move(
        Location((x, y, z))
    )
    leg_b = Box(thick, leg, leg, align=(Align.MIN, Align.MIN, Align.MIN)).move(
        Location((x, y, z))
    )
    return leg_a + leg_b


def build_corner_bracket_parts(params: Parameters, datums: Datums) -> list[PartRecord]:
    """Representative corner brackets at front-left base rail ends (CONCEPT mass sample).

    Full bracket set would duplicate at every rail-end node; one cluster documents the
    part family without exploding the assembly part count.
    """
    profile = float(params.value("materials.frame_profile_size_mm"))
    foot_h = float(params.value("materials.foot_height_mm"))
    inset = profile + float(params.value("case.corner_radius")) * 0.1
    z = foot_h
    bracket = _build_corner_bracket_solid(
        params,
        x=inset,
        y=0.0,
        z=z,
        leg_x=1.0,
        leg_y=1.0,
    )
    return [
        PartRecord(
            part_id="BRACKET-CORNER-SAMPLE-001",
            material=BRACKET_MATERIAL,
            solid=bracket,
            verify_on_real_machine=True,
        )
    ]


def build_handles(params: Parameters, datums: Datums) -> list[PartRecord]:
    """Handle grip geometry is modeled as through-cuts in PANEL-OUT-LEFT/RIGHT-001."""
    _ = params, datums
    return []


def build_hardware_parts(params: Parameters, datums: Datums) -> list[PartRecord]:
    return (
        build_feet(params, datums)
        + build_stack_caps(params, datums)
        + build_handles(params, datums)
    )
