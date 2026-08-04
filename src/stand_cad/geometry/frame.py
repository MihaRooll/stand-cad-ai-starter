"""Decomposed frame members — aluminium angle profile."""

from __future__ import annotations

from build123d import Align, Cylinder, Location, Part

from stand_cad.geometry.datums import Datums
from stand_cad.geometry.primitives import box_from_bounds
from stand_cad.geometry.registry import PartRecord
from stand_cad.parameters import Parameters

FRAME_MATERIAL = "aluminium_angle_15x15x1.5"
FRAME_CLAD_MATERIAL = "cast_opal_pmma_3mm"


def _side_clearance_mm(params: Parameters) -> float:
    width = float(params.value("case.width"))
    internal = float(params.value("case.internal_width"))
    return (width - internal) / 2.0


def _profile_size(params: Parameters) -> float:
    return float(params.value("materials.frame_profile_size_mm"))


def _film_storage_front_clearance_notch_x_z(
    params: Parameters, datums: Datums
) -> tuple[float, float, float, float]:
    """X/Z zone front-left post/cladding needs clear for film front withdrawal.

    Spans the organizer film-storage clear-volume band only — plotter-tier post
    material below ``organizer_floor_top_z_mm`` stays intact for rail connectivity.
    """
    inset = _corner_inset(params)
    profile = _profile_size(params)
    org_x = float(params.value("film_storage_horizontal.x"))
    x0 = org_x
    x1 = inset + profile
    z0 = datums.organizer_clear_volume.z.min_mm
    z1 = datums.organizer_clear_volume.z.max_mm
    return x0, z0, x1, z1


def _tray1_clearance_notch_x_z(
    params: Parameters, datums: Datums
) -> tuple[float, float, float, float]:
    """X/Z zone tray 1 (+slides) needs clear through the front base rail/cladding.

    Z covers slide-bottom to tray-top so both TRAY-LOWER-001 and
    SLIDE-LOWER-LEFT/RIGHT-001 have real clearance at any lower_extension
    position between closed and trays.lower_extension, including the new
    trays.lower_quick_access_extension_mm rest position (D-033).
    """
    lower = datums.plotter1_physical
    slide_h = float(params.value("trays.slide_rail_height_mm"))
    z1 = lower.z.min_mm
    z0 = z1 - params.tray_panel_thickness_mm - slide_h
    return lower.x.min_mm, z0, lower.x.max_mm, z1


def _corner_inset(params: Parameters) -> float:
    """Inset from absolute case corners so hidden frame stays behind R25 exterior."""
    return float(params.value("case.corner_radius"))


def _corner_trim_center(
    part_id: str,
    *,
    inset: float,
    width: float,
    depth: float,
) -> tuple[float, float]:
    """Cylinder axis for the rounded exterior corner associated with a post."""
    if part_id.endswith("FL-001"):
        return (inset, inset)
    if part_id.endswith("FR-001"):
        return (width - inset, inset)
    if part_id.endswith("RL-001"):
        return (inset, depth - inset)
    if part_id.endswith("RR-001"):
        return (width - inset, depth - inset)
    raise ValueError(f"unknown frame post id: {part_id}")


def _trim_post_for_rounded_exterior(
    solid: Part,
    *,
    center_x: float,
    center_y: float,
    radius: float,
    height: float,
    z_base: float,
) -> Part:
    """Remove post material encroaching past the exterior R fillet arc."""
    cutter = Cylinder(radius, height, align=(Align.CENTER, Align.CENTER, Align.MIN)).move(
        Location((center_x, center_y, z_base))
    )
    return solid - cutter


def _corner_post_solid(
    part_id: str,
    *,
    profile: float,
    inset: float,
    width: float,
    depth: float,
    height: float,
    z_base: float,
) -> Part:
    """L-shaped corner post bridging the two perimeter rails that meet there."""
    z0 = z_base
    z1 = z_base + height
    if part_id.endswith("FL-001"):
        leg_h = box_from_bounds(0.0, 0.0, z0, inset + profile, profile, z1)
        leg_v = box_from_bounds(0.0, 0.0, z0, profile, inset + profile, z1)
    elif part_id.endswith("FR-001"):
        leg_h = box_from_bounds(width - inset - profile, 0.0, z0, width, profile, z1)
        leg_v = box_from_bounds(width - profile, 0.0, z0, width, inset + profile, z1)
    elif part_id.endswith("RL-001"):
        leg_v = box_from_bounds(0.0, depth - inset - profile, z0, profile, depth, z1)
        leg_h = box_from_bounds(0.0, depth - profile, z0, inset + profile, depth, z1)
    elif part_id.endswith("RR-001"):
        leg_v = box_from_bounds(
            width - profile, depth - inset - profile, z0, width, depth, z1
        )
        leg_h = box_from_bounds(
            width - inset - profile, depth - profile, z0, width, depth, z1
        )
    else:
        raise ValueError(f"unknown frame post id: {part_id}")
    return leg_h + leg_v


def _post_part_ids() -> tuple[str, ...]:
    return (
        "FRAME-POST-FL-001",
        "FRAME-POST-FR-001",
        "FRAME-POST-RL-001",
        "FRAME-POST-RR-001",
    )


def build_frame_posts(params: Parameters, datums: Datums) -> list[PartRecord]:
    inset = _corner_inset(params)
    width = datums.case_envelope.x.max_mm
    depth = datums.case_envelope.y.max_mm
    profile = _profile_size(params)
    foot_h = float(params.value("materials.foot_height_mm"))
    post_height = datums.top_structure.z.min_mm - foot_h
    parts: list[PartRecord] = []
    for part_id in _post_part_ids():
        solid = _corner_post_solid(
            part_id,
            profile=profile,
            inset=inset,
            width=width,
            depth=depth,
            height=post_height,
            z_base=foot_h,
        )
        cx, cy = _corner_trim_center(part_id, inset=inset, width=width, depth=depth)
        solid = _trim_post_for_rounded_exterior(
            solid,
            center_x=cx,
            center_y=cy,
            radius=inset,
            height=post_height,
            z_base=foot_h,
        )
        if part_id == "FRAME-POST-FL-001":
            x0, z0, x1_notch, z1_notch = _film_storage_front_clearance_notch_x_z(
                params, datums
            )
            notch = box_from_bounds(x0, 0.0, z0, x1_notch, profile, z1_notch)
            solid = solid - notch
        parts.append(PartRecord(part_id=part_id, material=FRAME_MATERIAL, solid=solid))
    return parts


def _perimeter_rail(
    params: Parameters,
    datums: Datums,
    *,
    part_id: str,
    z_base: float,
) -> PartRecord:
    profile = _profile_size(params)
    inset = _corner_inset(params)
    width = datums.case_envelope.x.max_mm
    depth = datums.case_envelope.y.max_mm
    z_top = z_base + profile

    if part_id.endswith("FRONT-001"):
        solid = box_from_bounds(inset, 0.0, z_base, width - inset, profile, z_top)
    elif part_id.endswith("REAR-001"):
        solid = box_from_bounds(
            inset, depth - profile, z_base, width - inset, depth, z_top
        )
    elif part_id.endswith("LEFT-001"):
        solid = box_from_bounds(0.0, inset, z_base, profile, depth - inset, z_top)
    elif part_id.endswith("RIGHT-001"):
        solid = box_from_bounds(
            width - profile, inset, z_base, width, depth - inset, z_top
        )
    else:
        raise ValueError(f"unknown rail part id: {part_id}")

    if part_id == "FRAME-RAIL-BASE-FRONT-001":
        x0, z0, x1_notch, z1_notch = _tray1_clearance_notch_x_z(params, datums)
        notch = box_from_bounds(x0, 0.0, z0, x1_notch, profile, z1_notch)
        solid = solid - notch

    return PartRecord(part_id=part_id, material=FRAME_MATERIAL, solid=solid)


def build_frame_rails(params: Parameters, datums: Datums) -> list[PartRecord]:
    profile = _profile_size(params)
    foot_h = float(params.value("materials.foot_height_mm"))
    org_z = datums.organizer_floor_top_z_mm
    top_z = datums.top_structure.z.min_mm

    rail_sets: list[tuple[str, float]] = [
        ("BASE", foot_h),
        ("TOP", top_z - profile),
        ("ORG", org_z - profile),
    ]
    parts: list[PartRecord] = []
    for prefix, z_base in rail_sets:
        for face in ("FRONT", "REAR", "LEFT", "RIGHT"):
            part_id = f"FRAME-RAIL-{prefix}-{face}-001"
            parts.append(_perimeter_rail(params, datums, part_id=part_id, z_base=z_base))
    return parts


def build_frame_cladding(params: Parameters, datums: Datums) -> list[PartRecord]:
    """Opal cosmetic strips over front-facing perimeter rails in the open front opening.

    Conceals grey aluminium FRAME-RAIL-* segments visible in transport_iso / transport_front /
    organizer_closeup evidence views without changing frame structure (PLT-006 AC-C1, TZ line 231).
    """
    profile = _profile_size(params)
    inset = _corner_inset(params)
    width = datums.case_envelope.x.max_mm
    foot_h = float(params.value("materials.foot_height_mm"))
    org_z = datums.organizer_floor_top_z_mm
    top_z = datums.top_structure.z.min_mm

    rail_sets: list[tuple[str, float]] = [
        ("BASE", foot_h),
        ("ORG", org_z - profile),
        ("TOP", top_z - profile),
    ]
    parts: list[PartRecord] = []
    for prefix, z_base in rail_sets:
        part_id = f"PANEL-CLAD-FRONT-{prefix}-001"
        z_top = z_base + profile
        solid = box_from_bounds(
            inset,
            0.0,
            z_base,
            width - inset,
            profile,
            z_top,
        )
        if part_id == "PANEL-CLAD-FRONT-BASE-001":
            x0, z0, x1_notch, z1_notch = _tray1_clearance_notch_x_z(params, datums)
            notch = box_from_bounds(x0, 0.0, z0, x1_notch, profile, z1_notch)
            solid = solid - notch
        parts.append(PartRecord(part_id=part_id, material=FRAME_CLAD_MATERIAL, solid=solid))

    side_clear = _side_clearance_mm(params)
    post_height = datums.top_structure.z.min_mm - foot_h
    z_top = foot_h + post_height
    post_clad_specs = (
        ("FL", side_clear, inset + profile),
        ("FR", width - inset - profile, width - side_clear),
    )
    for suffix, x0, x1 in post_clad_specs:
        solid = box_from_bounds(x0, 0.0, foot_h, x1, profile, z_top)
        if suffix == "FL":
            nx0, nz0, nx1, nz1 = _film_storage_front_clearance_notch_x_z(params, datums)
            notch = box_from_bounds(nx0, 0.0, nz0, nx1, profile, nz1)
            solid = solid - notch
        parts.append(
            PartRecord(
                part_id=f"PANEL-CLAD-FRONT-POST-{suffix}-001",
                material=FRAME_CLAD_MATERIAL,
                solid=solid,
            )
        )
    return parts


def build_frame_parts(params: Parameters, datums: Datums) -> list[PartRecord]:
    return (
        build_frame_posts(params, datums)
        + build_frame_rails(params, datums)
        + build_frame_cladding(params, datums)
    )
