"""Decomposed frame members — aluminium angle profile."""

from __future__ import annotations

from build123d import Align, Cylinder, Location, Part

from stand_cad.geometry.datums import Datums
from stand_cad.geometry.primitives import box_from_bounds
from stand_cad.geometry.registry import PartRecord
from stand_cad.parameters import Parameters

FRAME_MATERIAL = "aluminium_angle_15x15x1.5"


def _profile_size(params: Parameters) -> float:
    return float(params.value("materials.frame_profile_size_mm"))


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


def build_frame_parts(params: Parameters, datums: Datums) -> list[PartRecord]:
    return build_frame_posts(params, datums) + build_frame_rails(params, datums)
