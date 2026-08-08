"""Decomposed frame members — aluminium angle profile."""

from __future__ import annotations

from build123d import Align, Cylinder, Location, Part

from stand_cad.geometry.datums import Datums
from stand_cad.geometry.primitives import box_from_bounds
from stand_cad.geometry.registry import PartRecord
from stand_cad.geometry.trays import _tray_bounds, _tray_frame_rail_bounds
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


def _corner_post_cap_solid(
    part_id: str,
    *,
    profile: float,
    width: float,
    depth: float,
    height: float,
    z_base: float,
) -> Part:
    """Thin symmetric corner stub above the rail line — single square post, no sideways leg.

    The main ``_corner_post_solid`` L-shape bridges both perimeter rails and stays hidden
    inside the side-slab cavity below the rail line; above it (the exposed `top_structure`
    band, D-056) a bare bridging leg would read as a lopsided tab in a top-down view. The cap
    matches the rail's own profile x profile cross-section at the bare corner point only.
    """
    z0 = z_base
    z1 = z_base + height
    if part_id.endswith("FL-001"):
        return box_from_bounds(0.0, 0.0, z0, profile, profile, z1)
    if part_id.endswith("FR-001"):
        return box_from_bounds(width - profile, 0.0, z0, width, profile, z1)
    if part_id.endswith("RL-001"):
        return box_from_bounds(0.0, depth - profile, z0, profile, depth, z1)
    if part_id.endswith("RR-001"):
        return box_from_bounds(width - profile, depth - profile, z0, width, depth, z1)
    raise ValueError(f"unknown frame post id: {part_id}")


def build_single_frame_post(part_id: str, params: Parameters, datums: Datums) -> PartRecord:
    """Build one corner post by part_id."""
    if part_id not in _post_part_ids():
        raise ValueError(f"unknown frame post id: {part_id}")
    inset = _corner_inset(params)
    width = datums.case_envelope.x.max_mm
    depth = datums.case_envelope.y.max_mm
    profile = _profile_size(params)
    foot_h = float(params.value("materials.foot_height_mm"))
    rail_top_z = datums.top_structure.z.min_mm
    case_top_z = datums.top_structure.z.max_mm
    post_height = rail_top_z - foot_h
    solid = _corner_post_solid(
        part_id,
        profile=profile,
        inset=inset,
        width=width,
        depth=depth,
        height=post_height,
        z_base=foot_h,
    )
    cap_height = case_top_z - rail_top_z
    if cap_height > 0.0:
        cap = _corner_post_cap_solid(
            part_id,
            profile=profile,
            width=width,
            depth=depth,
            height=cap_height,
            z_base=rail_top_z,
        )
        solid = solid + cap
    total_height = case_top_z - foot_h
    cx, cy = _corner_trim_center(part_id, inset=inset, width=width, depth=depth)
    solid = _trim_post_for_rounded_exterior(
        solid,
        center_x=cx,
        center_y=cy,
        radius=inset,
        height=total_height,
        z_base=foot_h,
    )
    if part_id == "FRAME-POST-FL-001":
        x0, z0, x1_notch, z1_notch = _film_storage_front_clearance_notch_x_z(params, datums)
        notch = box_from_bounds(x0, 0.0, z0, x1_notch, profile, z1_notch)
        solid = solid - notch
    elif part_id == "FRAME-POST-FR-001":
        # Cosmetic-only mirror of the FL withdrawal notch (owner 2026-08-06): the film sheets
        # are left-aligned in the storage bay with a 110 mm margin before the right wall
        # (test_film_bodies_span_sheet_depth_across_width), so nothing ever needs this
        # clearance on the right — cut purely so both front corners read as visually symmetric.
        x0, z0, x1_notch, z1_notch = _film_storage_front_clearance_notch_x_z(params, datums)
        mirror_x0, mirror_x1 = width - x1_notch, width - x0
        notch = box_from_bounds(mirror_x0, 0.0, z0, mirror_x1, profile, z1_notch)
        solid = solid - notch
    return PartRecord(part_id=part_id, material=FRAME_MATERIAL, solid=solid)


def build_frame_posts(params: Parameters, datums: Datums) -> list[PartRecord]:
    # Owner 2026-08-07 (D-075) — restored after D-070's post-less corners were judged not
    # structurally proven for a real bolted/weld-free cabinet; back to full vertical posts.
    return [build_single_frame_post(part_id, params, datums) for part_id in _post_part_ids()]


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


def build_single_frame_rail(part_id: str, params: Parameters, datums: Datums) -> PartRecord:
    """Build one perimeter rail by part_id."""
    profile = _profile_size(params)
    foot_h = float(params.value("materials.foot_height_mm"))
    org_z = datums.organizer_floor_top_z_mm
    top_z = datums.top_structure.z.min_mm
    if "-BASE-" in part_id:
        z_base = foot_h
    elif "-TOP-" in part_id:
        z_base = top_z - profile
    elif "-ORG-" in part_id:
        z_base = org_z - profile
    else:
        raise ValueError(f"unknown frame rail id: {part_id}")
    return _perimeter_rail(params, datums, part_id=part_id, z_base=z_base)


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
            if prefix == "TOP" and face == "FRONT":
                continue  # D-044 — top-front cross member removed, owner 2026-08-05
            part_id = f"FRAME-RAIL-{prefix}-{face}-001"
            parts.append(_perimeter_rail(params, datums, part_id=part_id, z_base=z_base))
    return parts


def build_single_frame_cladding_part(
    part_id: str, params: Parameters, datums: Datums
) -> PartRecord:
    """Build one front cladding strip by part_id."""
    profile = _profile_size(params)
    clad_depth = float(params.value("materials.outer_panel_thickness_mm"))
    inset = _corner_inset(params)
    width = datums.case_envelope.x.max_mm
    foot_h = float(params.value("materials.foot_height_mm"))
    org_z = datums.organizer_floor_top_z_mm
    top_z = datums.top_structure.z.min_mm
    side_clear = _side_clearance_mm(params)

    if part_id.startswith("PANEL-CLAD-FRONT-") and part_id.endswith("-001"):
        body = part_id.removeprefix("PANEL-CLAD-FRONT-").removesuffix("-001")
        if body in ("BASE", "ORG", "TOP"):
            z_base_by_prefix = {
                "BASE": foot_h,
                "ORG": org_z - profile,
                "TOP": top_z - profile,
            }
            z_base = z_base_by_prefix[body]
            z_top = z_base + profile
            solid = box_from_bounds(
                inset,
                0.0,
                z_base,
                width - inset,
                clad_depth,
                z_top,
            )
            if part_id == "PANEL-CLAD-FRONT-BASE-001":
                x0, z0, x1_notch, z1_notch = _tray1_clearance_notch_x_z(params, datums)
                notch = box_from_bounds(x0, 0.0, z0, x1_notch, clad_depth, z1_notch)
                solid = solid - notch
            return PartRecord(part_id=part_id, material=FRAME_CLAD_MATERIAL, solid=solid)
        if body.startswith("POST-"):
            suffix = body.removeprefix("POST-")
            post_height = datums.top_structure.z.max_mm - foot_h
            z_top = foot_h + post_height
            post_clad_specs = {
                "FL": (side_clear, inset + profile),
                "FR": (width - inset - profile, width - side_clear),
            }
            x0, x1 = post_clad_specs[suffix]
            solid = box_from_bounds(x0, 0.0, foot_h, x1, clad_depth, z_top)
            if suffix == "FL":
                nx0, nz0, nx1, nz1 = _film_storage_front_clearance_notch_x_z(params, datums)
                notch = box_from_bounds(nx0, 0.0, nz0, nx1, clad_depth, nz1)
                solid = solid - notch
            elif suffix == "FR":
                # Cosmetic-only mirror of the FL notch (owner 2026-08-06) — see matching
                # comment in build_single_frame_post; not functionally required on this side.
                nx0, nz0, nx1, nz1 = _film_storage_front_clearance_notch_x_z(params, datums)
                mirror_nx0, mirror_nx1 = width - nx1, width - nx0
                notch = box_from_bounds(mirror_nx0, 0.0, nz0, mirror_nx1, clad_depth, nz1)
                solid = solid - notch
            return PartRecord(part_id=part_id, material=FRAME_CLAD_MATERIAL, solid=solid)
        if body.startswith("TRAY-"):
            # TRAY-LOWER-L / TRAY-UPPER-C etc.
            level_suffix, side_suffix = body.removeprefix("TRAY-").split("-", 1)
            level = "LOWER" if level_suffix == "LOWER" else "UPPER"
            side_by_suffix = {"L": "left", "R": "right", "C": "center"}
            side = side_by_suffix[side_suffix]
            datum = datums.plotter1_physical if level == "LOWER" else datums.plotter2_physical
            tray_b = _tray_bounds(params, datum)
            rail_bounds = _tray_frame_rail_bounds(params, tray_b, side=side)
            x0, y0, z_base, x1, _y1, _z_top = rail_bounds
            z_tray_bottom = tray_b[5]
            solid = box_from_bounds(x0, y0, z_base, x1, y0 + clad_depth, z_tray_bottom)
            return PartRecord(part_id=part_id, material=FRAME_CLAD_MATERIAL, solid=solid)

    raise ValueError(f"unknown frame cladding part id: {part_id}")


def build_frame_cladding(params: Parameters, datums: Datums) -> list[PartRecord]:
    """Opal cosmetic strips over front-facing perimeter rails in the open front opening.

    Conceals grey aluminium FRAME-RAIL-* segments visible in transport_iso / transport_front /
    organizer_closeup evidence views without changing frame structure (PLT-006 AC-C1, TZ line 231).
    """
    profile = _profile_size(params)
    foot_h = float(params.value("materials.foot_height_mm"))
    org_z = datums.organizer_floor_top_z_mm
    top_z = datums.top_structure.z.min_mm

    part_ids: list[str] = []
    rail_sets: list[tuple[str, float]] = [
        ("BASE", foot_h),
        ("ORG", org_z - profile),
        ("TOP", top_z - profile),
    ]
    for prefix, _z_base in rail_sets:
        if prefix in ("TOP", "BASE", "ORG"):
            continue
        part_ids.append(f"PANEL-CLAD-FRONT-{prefix}-001")
    for level in ("LOWER", "UPPER"):
        for suffix in ("L", "R", "C"):
            part_ids.append(f"PANEL-CLAD-FRONT-TRAY-{level}-{suffix}-001")
    return [build_single_frame_cladding_part(part_id, params, datums) for part_id in part_ids]


def build_frame_parts(params: Parameters, datums: Datums) -> list[PartRecord]:
    return (
        build_frame_posts(params, datums)
        + build_frame_rails(params, datums)
        + build_frame_cladding(params, datums)
    )
