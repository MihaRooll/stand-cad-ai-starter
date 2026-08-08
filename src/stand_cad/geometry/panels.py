"""Outer shell, inner structural panels — PLT-004 restructured side slabs."""

from __future__ import annotations

from build123d import (
    Align,
    BuildPart,
    BuildSketch,
    Circle,
    Location,
    Part,
    Plane,
    Rectangle,
    RectangleRounded,
    extrude,
    fillet,
)

from stand_cad.geometry.datums import Datums
from stand_cad.geometry.primitives import box_from_bounds
from stand_cad.geometry.registry import PartRecord
from stand_cad.parameters import Parameters

OUTER_PANEL_MATERIAL = "cast_opal_pmma_3mm"
INNER_PANEL_MATERIAL = "white_composite_3_4mm"


def _feed_plane_z(params: Parameters, level: str) -> float:
    """Provisional feed-plane height above tray finished top (VERIFY ON REAL MACHINE)."""
    prefix = "lower" if level == "L1" else "upper"
    tray_top = float(params.value(f"plotter.{prefix}_z"))
    return tray_top + float(params.value("plotter.feed_plane_z_provisional_mm"))


def _subtract_box(
    solid: Part, x0: float, y0: float, z0: float, x1: float, y1: float, z1: float
) -> Part:
    """Boolean subtract an axis-aligned box from solid."""
    cutter = box_from_bounds(x0, y0, z0, x1, y1, z1)
    return solid - cutter


def _side_clearance_mm(params: Parameters) -> float:
    """Derived side clearance: (case.width - case.internal_width) / 2."""
    width = float(params.value("case.width"))
    internal = float(params.value("case.internal_width"))
    return (width - internal) / 2.0


def _handle_mount_z_fallback(params: Parameters) -> float:
    """Derived lowest sightline-feasible Z at depth-centred Y (D-050)."""
    return params.computed_handle_mount_z_mm


def _handle_mount_y_fallback(params: Parameters, datums: Datums) -> float:
    """Derived loaded-case CoM Y balance point (D-051)."""
    del datums
    return params.computed_handle_mount_y_mm


def _handle_mount_z(params: Parameters) -> float:
    raw = params.value("hardware.handle_mount_z_mm")
    if isinstance(raw, (int, float)) and not isinstance(raw, bool):
        return float(raw)
    return _handle_mount_z_fallback(params)


def _handle_mount_y(params: Parameters, datums: Datums) -> float:
    raw = params.value("hardware.handle_mount_y_mm")
    if isinstance(raw, (int, float)) and not isinstance(raw, bool):
        return float(raw)
    return _handle_mount_y_fallback(params, datums)


def side_slab_bullnose_radius_mm(params: Parameters) -> float:
    """Configured full bullnose radius on side-slab front vertical + top edges."""
    return float(params.value("case.side_slab_bullnose_radius_mm"))


def _achieved_bullnose_on_profile(
    params: Parameters, *, profile_width_mm: float, profile_depth_mm: float
) -> float:
    """Clamp configured bullnose to what the slab cross-section can geometrically accept."""
    bullnose = side_slab_bullnose_radius_mm(params)
    max_r = min(bullnose, profile_width_mm / 2.0 - 0.1, profile_depth_mm / 2.0 - 0.1)
    return max(max_r, 0.5)


def achieved_side_slab_front_bullnose_radius_mm(params: Parameters) -> float:
    """Achieved radius on the front vertical exterior edge of a side slab."""
    side_clear = _side_clearance_mm(params)
    gap = float(params.value("materials.outer_panel_shadow_gap_mm"))
    depth = float(params.value("case.depth")) - gap
    return _achieved_bullnose_on_profile(
        params, profile_width_mm=side_clear, profile_depth_mm=depth
    )


def achieved_side_slab_top_bullnose_radius_mm(params: Parameters) -> float:
    """Achieved radius on the top-front horizontal exterior edge (same ceiling as front)."""
    return achieved_side_slab_front_bullnose_radius_mm(params)


def achieved_side_slab_corner_radius_mm(params: Parameters) -> float:
    """Backward-compatible alias — PLT-006 uses front bullnose only."""
    return achieved_side_slab_front_bullnose_radius_mm(params)


def _apply_top_front_bullnose(solid: Part, radius: float) -> Part:
    """Fillet the slab top-front horizontal edge with the same bullnose radius."""
    try:
        top_z = solid.bounding_box().max.Z
        min_y = solid.bounding_box().min.Y
        edges = [
            edge
            for edge in solid.edges()
            if abs(edge.center().Z - top_z) < 0.5
            and abs(edge.center().Y - min_y) < 0.5
            and edge.length > radius
        ]
        if not edges:
            return solid
        return fillet(edges[:4], radius=radius)
    except Exception:  # noqa: BLE001 — build123d fillet stability varies by kernel
        return solid


def _apply_top_rear_bullnose(solid: Part, radius: float) -> Part:
    """Fillet the slab top-rear horizontal edge — companion to the top-front bullnose above."""
    try:
        top_z = solid.bounding_box().max.Z
        max_y = solid.bounding_box().max.Y
        edges = [
            edge
            for edge in solid.edges()
            if abs(edge.center().Z - top_z) < 0.5
            and abs(edge.center().Y - max_y) < 0.5
            and edge.length > radius
        ]
        if not edges:
            return solid
        return fillet(edges[:4], radius=radius)
    except Exception:  # noqa: BLE001 — build123d fillet stability varies by kernel
        return solid


def _extrude_side_slab(
    *,
    x_min: float,
    x_max: float,
    y_min: float,
    y_max: float,
    z_min: float,
    z_max: float,
    side: str,
    bullnose_radius: float,
    wall_mm: float,
) -> Part:
    """Cavity-wall side slab: 3 mm opal skin on exterior + front/rear returns, air pocket behind.

    Preserves the full 20 mm outer profile depth (``side_clear``) so R10 bullnose fillets on the
    unchanged exterior 2D profile continue to work.  The outer X face and front Y return carry the
    opal PMMA skin; the remaining pocket is air for light-strip clearance and aluminium frame
    members (TZ lines 218–219, 212).
    """
    height = z_max - z_min
    width = x_max - x_min
    depth = y_max - y_min
    max_r = min(bullnose_radius, width / 2.0 - 0.1, depth / 2.0 - 0.1)
    max_r = max(max_r, 0.5)

    with BuildPart() as outer_builder:
        with BuildSketch(Plane.XY) as sketch:
            Rectangle(width, depth, align=(Align.MIN, Align.MIN))
            # Round both exterior vertical edges (front AND rear), not just front — an unrounded
            # rear corner is a sharp 90 deg edge at full case height (owner 2026-08-06 safety
            # request: no exposed sharp cube edges that could cut/bruise on contact). Same
            # bullnose radius as the front (D-025) for a consistent all-round profile; select
            # both vertices from the pristine rectangle before any fillet so vertex references
            # stay valid for a single combined fillet call.
            front_candidates = [v for v in sketch.vertices() if abs(v.Y) < 0.01]
            rear_candidates = [v for v in sketch.vertices() if abs(v.Y - depth) < 0.01]
            exterior_key = min if side == "left" else max
            corner_vertices = []
            if front_candidates:
                corner_vertices.append(exterior_key(front_candidates, key=lambda v: v.X))
            if rear_candidates:
                corner_vertices.append(exterior_key(rear_candidates, key=lambda v: v.X))
            if corner_vertices:
                fillet(corner_vertices, radius=max_r)
        extrude(amount=height)
    solid = outer_builder.part.move(Location((x_min, y_min, z_min)))
    solid = _apply_top_front_bullnose(solid, max_r)
    solid = _apply_top_rear_bullnose(solid, max_r)

    # Cavity pocket: exterior skin on outer X face; front/rear Y returns for edge stiffness.
    if side == "left":
        cavity_x0 = x_min + wall_mm
        cavity_x1 = x_max
    else:
        cavity_x0 = x_min
        cavity_x1 = x_max - wall_mm
    cavity_y0 = y_min + wall_mm
    cavity_y1 = y_max - wall_mm
    if cavity_x1 > cavity_x0 and cavity_y1 > cavity_y0:
        solid = _subtract_box(solid, cavity_x0, cavity_y0, z_min, cavity_x1, cavity_y1, z_max)

    return solid


def _subtract_rounded_through_x(
    solid: Part,
    *,
    x0: float,
    x1: float,
    y0: float,
    y1: float,
    z0: float,
    z1: float,
    edge_radius: float,
) -> Part:
    """Through-cut along X with rounded Y-Z footprint (TZ:304 edge break)."""
    eps = 0.5
    span_y = y1 - y0
    span_z = z1 - z0
    with BuildPart() as builder:
        with BuildSketch(Plane.YZ):
            RectangleRounded(span_y, span_z, edge_radius, align=(Align.MIN, Align.MIN))
        extrude(amount=(x1 - x0) + 2 * eps)
    cutter = builder.part.move(Location((x0 - eps, y0, z0)))
    return solid - cutter


def _subtract_rounded_through_y(
    solid: Part,
    *,
    x0: float,
    x1: float,
    y0: float,
    y1: float,
    z0: float,
    z1: float,
    edge_radius: float,
) -> Part:
    """Through-cut along Y with rounded X-Z footprint (edge break on the aperture rim)."""
    eps = 0.5
    span_x = x1 - x0
    span_z = z1 - z0
    with BuildPart() as builder:
        with BuildSketch(Plane.XZ):
            RectangleRounded(span_x, span_z, edge_radius, align=(Align.MIN, Align.MIN))
        # Plane.XZ extrude +Y is opposite sketch normal; negative amount cuts +Y through panel.
        extrude(amount=-((y1 - y0) + 2 * eps))
    cutter = builder.part.move(Location((x0, y0 - eps, z0)))
    return solid - cutter


def _subtract_vent_slots_x(
    solid: Part,
    params: Parameters,
    datums: Datums,
    *,
    y0: float,
    y1: float,
) -> Part:
    """Parallel rectangular vent slots through panel thickness along Y (rear panel)."""
    count = int(params.value("hardware.vent_slot_count"))
    slot_w = float(params.value("hardware.vent_slot_width_mm"))
    slot_h = float(params.value("hardware.vent_slot_height_mm"))
    pitch = float(params.value("hardware.vent_slot_pitch_mm"))
    band_z = float(params.value("hardware.vent_band_z_mm"))
    width = datums.case_envelope.x.max_mm
    cx = width / 2.0
    total_span = count * slot_w + (count - 1) * pitch
    x_start = cx - total_span / 2.0
    eps = 0.5
    result = solid
    for index in range(count):
        x0 = x_start + index * (slot_w + pitch)
        result = _subtract_box(
            result,
            x0,
            y0 - eps,
            band_z - slot_h / 2,
            x0 + slot_w,
            y1 + eps,
            band_z + slot_h / 2,
        )
    return result


def _subtract_vent_slots_z(
    solid: Part,
    params: Parameters,
    *,
    x_center: float,
    y_center: float,
    z0: float,
    z1: float,
) -> Part:
    """Parallel rectangular vent slots through bottom panel thickness along Z."""
    count = int(params.value("hardware.vent_slot_count"))
    slot_w = float(params.value("hardware.vent_slot_width_mm"))
    slot_h = float(params.value("hardware.vent_slot_height_mm"))
    pitch = float(params.value("hardware.vent_slot_pitch_mm"))
    total_span = count * slot_w + (count - 1) * pitch
    x_start = x_center - total_span / 2.0
    eps = 0.5
    result = solid
    for index in range(count):
        x_lo = x_start + index * (slot_w + pitch)
        result = _subtract_box(
            result,
            x_lo,
            y_center - slot_h / 2,
            z0 - eps,
            x_lo + slot_w,
            y_center + slot_h / 2,
            z1 + eps,
        )
    return result


def _subtract_cable_passthrough_x(
    solid: Part, params: Parameters, *, x0: float, x1: float
) -> Part:
    """Round cable pass-through cut through right side-panel X-thickness (D-047)."""
    diameter = float(params.value("hardware.cable_passthrough_diameter_mm"))
    radius = diameter / 2.0
    y_center = float(params.value("hardware.cable_passthrough_mount_y_mm"))
    z_center = float(params.value("hardware.cable_passthrough_mount_z_mm"))
    eps = 0.5
    span_x = (x1 - x0) + 2 * eps
    with BuildPart() as builder:
        with BuildSketch(Plane.YZ):
            Circle(radius)
        extrude(amount=span_x)
    cutter = builder.part.move(Location((x0 - eps, y_center, z_center)))
    return solid - cutter


def _apply_rear_corner_fillets(
    solid: Part,
    *,
    radius: float,
    height: float,
    corners: list[tuple[float, float]],
) -> Part:
    """Notch rear panel corners for exterior R fillet (rear panel only — 3 mm Y thickness)."""
    from build123d import Align, Cylinder

    result = solid
    for cx, cy in corners:
        cyl = Cylinder(radius, height, align=(Align.CENTER, Align.CENTER, Align.MIN)).move(
            Location((cx, cy, 0.0))
        )
        result = result - cyl
    return result


def _physical_corner_center(
    corner_xy: tuple[float, float],
    radius: float,
    width: float,
    depth: float,
) -> tuple[float, float]:
    """Cylinder axis center for a rounded exterior case corner."""
    x, y = corner_xy
    cx = radius if x <= width / 2 else width - radius
    cy = radius if y <= depth / 2 else depth - radius
    return (cx, cy)


def _rear_panel_corners(width: float, depth: float) -> list[tuple[float, float]]:
    return [(0.0, depth), (width, depth)]


def _build_rear_panel(params: Parameters, datums: Datums) -> PartRecord:
    thickness = float(params.value("materials.outer_panel_thickness_mm"))
    gap = float(params.value("materials.outer_panel_shadow_gap_mm"))
    foot_h = float(params.value("materials.foot_height_mm"))
    corner_r = float(params.value("case.corner_radius"))
    width = datums.case_envelope.x.max_mm
    depth = datums.case_envelope.y.max_mm
    height = datums.case_envelope.z.max_mm
    panel_height = height - foot_h
    slot_w = float(params.value("media_path.clear_width"))
    slot_h = float(params.value("media_path.slot_height_target"))
    edge_radius = float(params.value("media_path.rear_channel_edge_break_radius_mm"))
    cx = width / 2.0

    solid = box_from_bounds(gap, depth - thickness, foot_h, width - gap, depth, height)
    eps = 0.5
    y0 = depth - thickness - eps
    y1 = depth + eps
    for level in ("L1", "L2"):
        feed_z = _feed_plane_z(params, level)
        solid = _subtract_rounded_through_y(
            solid,
            x0=cx - slot_w / 2,
            x1=cx + slot_w / 2,
            y0=y0,
            y1=y1,
            z0=feed_z - slot_h / 2,
            z1=feed_z + slot_h / 2,
            edge_radius=edge_radius,
        )

    solid = _subtract_vent_slots_x(solid, params, datums, y0=y0, y1=y1)

    corner_centers = [
        _physical_corner_center(c, corner_r, width, depth)
        for c in _rear_panel_corners(width, depth)
    ]
    solid = _apply_rear_corner_fillets(
        solid, radius=corner_r, height=panel_height, corners=corner_centers
    )
    return PartRecord(part_id="PANEL-OUT-REAR-001", material=OUTER_PANEL_MATERIAL, solid=solid)


def _build_side_slab_with_handle(
    params: Parameters,
    datums: Datums,
    *,
    side: str,
) -> PartRecord:
    gap = float(params.value("materials.outer_panel_shadow_gap_mm"))
    foot_h = float(params.value("materials.foot_height_mm"))
    bullnose_r = side_slab_bullnose_radius_mm(params)
    wall_mm = float(params.value("materials.outer_panel_thickness_mm"))
    grip_len = float(params.value("hardware.handle_grip_length_mm"))
    grip_depth = float(params.value("hardware.handle_grip_depth_mm"))
    edge_r = float(params.value("hardware.handle_cutout_edge_radius_mm"))
    width = datums.case_envelope.x.max_mm
    depth = datums.case_envelope.y.max_mm
    height = datums.case_envelope.z.max_mm
    side_clear = _side_clearance_mm(params)
    mount_z = _handle_mount_z(params)
    y_center = _handle_mount_y(params, datums)

    if side == "left":
        part_id = "PANEL-OUT-LEFT-001"
        x0, x1 = 0.0, side_clear
    else:
        part_id = "PANEL-OUT-RIGHT-001"
        x0, x1 = width - side_clear, width

    solid = _extrude_side_slab(
        x_min=x0,
        x_max=x1,
        y_min=0.0,
        y_max=depth - gap,
        z_min=foot_h,
        z_max=height,
        side=side,
        bullnose_radius=bullnose_r,
        wall_mm=wall_mm,
    )
    solid = _subtract_rounded_through_x(
        solid,
        x0=x0,
        x1=x1,
        y0=y_center - grip_len / 2,
        y1=y_center + grip_len / 2,
        z0=mount_z - grip_depth / 2,
        z1=mount_z + grip_depth / 2,
        edge_radius=edge_r,
    )
    if side == "right":
        port_w = float(params.value("hardware.service_port_cutout_width_mm"))
        port_h = float(params.value("hardware.service_port_cutout_height_mm"))
        port_y = float(params.value("hardware.service_port_mount_y_mm"))
        port_z = float(params.value("hardware.service_port_mount_z_mm"))
        port_edge_r = float(params.value("services.service_port_edge_break_radius_mm"))
        solid = _subtract_rounded_through_x(
            solid,
            x0=x0 - 1.0,
            x1=x1 + 1.0,
            y0=port_y - port_w / 2,
            y1=port_y + port_w / 2,
            z0=port_z - port_h / 2,
            z1=port_z + port_h / 2,
            edge_radius=port_edge_r,
        )
        solid = _subtract_cable_passthrough_x(solid, params, x0=x0, x1=x1)
    return PartRecord(part_id=part_id, material=OUTER_PANEL_MATERIAL, solid=solid)


def build_outer_panels(params: Parameters, datums: Datums) -> list[PartRecord]:
    """Outer opal shell: full-height side slabs, closed rear with feed slots and vents."""
    return [
        _build_rear_panel(params, datums),
        _build_side_slab_with_handle(params, datums, side="left"),
        _build_side_slab_with_handle(params, datums, side="right"),
    ]


def build_inner_panels(params: Parameters, datums: Datums) -> list[PartRecord]:
    return [
        _build_inner_bottom_panel(params, datums),
        _build_inner_rear_panel(params, datums),
        _build_inner_mid_panel(params, datums),
    ]


def _build_inner_bottom_panel(params: Parameters, datums: Datums) -> PartRecord:
    thickness = float(params.value("materials.inner_panel_thickness_mm"))
    foot_h = float(params.value("materials.foot_height_mm"))
    width = datums.case_envelope.x.max_mm
    depth = datums.case_envelope.y.max_mm
    gap = float(params.value("materials.outer_panel_shadow_gap_mm"))

    bottom_z = foot_h + thickness
    bottom_solid = box_from_bounds(gap, gap, foot_h, width - gap, depth - gap, bottom_z)
    ap_d = float(params.value("services.airpath_depth_mm"))
    airpath_cx = width / 2.0
    airpath_cy = depth - gap - ap_d / 2.0
    bottom_solid = _subtract_vent_slots_z(
        bottom_solid,
        params,
        x_center=airpath_cx,
        y_center=airpath_cy,
        z0=foot_h,
        z1=bottom_z,
    )
    return PartRecord(
        part_id="PANEL-IN-BOTTOM-001",
        material=INNER_PANEL_MATERIAL,
        solid=bottom_solid,
    )


def _build_inner_rear_panel(params: Parameters, datums: Datums) -> PartRecord:
    thickness = float(params.value("materials.inner_panel_thickness_mm"))
    foot_h = float(params.value("materials.foot_height_mm"))
    width = datums.case_envelope.x.max_mm
    depth = datums.case_envelope.y.max_mm
    gap = float(params.value("materials.outer_panel_shadow_gap_mm"))
    rear_inner_y0 = depth - thickness - gap
    rear_inner_y1 = depth - gap
    slot_w = float(params.value("media_path.clear_width"))
    slot_h = float(params.value("media_path.slot_height_target"))
    edge_radius = float(params.value("media_path.rear_channel_edge_break_radius_mm"))
    cx = width / 2.0
    rear_solid = box_from_bounds(
        gap,
        rear_inner_y0,
        foot_h,
        width - gap,
        rear_inner_y1,
        datums.top_structure.z.min_mm,
    )
    eps = 0.5
    y_cut0 = rear_inner_y0 - eps
    y_cut1 = rear_inner_y1 + eps
    for level in ("L1", "L2"):
        feed_z = _feed_plane_z(params, level)
        rear_solid = _subtract_rounded_through_y(
            rear_solid,
            x0=cx - slot_w / 2,
            x1=cx + slot_w / 2,
            y0=y_cut0,
            y1=y_cut1,
            z0=feed_z - slot_h / 2,
            z1=feed_z + slot_h / 2,
            edge_radius=edge_radius,
        )
    return PartRecord(
        part_id="PANEL-IN-REAR-001",
        material=INNER_PANEL_MATERIAL,
        solid=rear_solid,
    )


def _build_inner_mid_panel(params: Parameters, datums: Datums) -> PartRecord:
    thickness = float(params.value("materials.inner_panel_thickness_mm"))
    width = datums.case_envelope.x.max_mm
    depth = datums.case_envelope.y.max_mm
    gap = float(params.value("materials.outer_panel_shadow_gap_mm"))
    mid_z = (datums.plotter1_physical.z.max_mm + datums.plotter2_physical.z.min_mm) / 2
    # Front Y at closed-door / tray front plane — not shadow gap (FIX-COLL-002 Path A).
    mid_front_y = datums.plotter1_physical.y.min_mm
    return PartRecord(
        part_id="PANEL-IN-MID-001",
        material=INNER_PANEL_MATERIAL,
        solid=box_from_bounds(
            gap,
            mid_front_y,
            mid_z - thickness / 2,
            width - gap,
            depth - gap,
            mid_z + thickness / 2,
        ),
    )


def build_panel_parts(params: Parameters, datums: Datums) -> list[PartRecord]:
    return build_outer_panels(params, datums) + build_inner_panels(params, datums)


def handle_cutout_through_ray_x_bounds(
    params: Parameters, datums: Datums, *, side: str
) -> tuple[float, float]:
    """X span for sightline probes: full case width along the handle through-ray."""
    del side  # left/right share the same interior sweep for transport symmetry
    width = datums.case_envelope.x.max_mm
    return (0.0, width)


def handle_cutout_footprint(params: Parameters, datums: Datums, *, side: str) -> dict[str, float]:
    """Return axis-aligned handle cutout bounds for tests (x0/x1/y0/y1/z0/z1)."""
    width = datums.case_envelope.x.max_mm
    side_clear = _side_clearance_mm(params)
    grip_len = float(params.value("hardware.handle_grip_length_mm"))
    grip_depth = float(params.value("hardware.handle_grip_depth_mm"))
    mount_z = _handle_mount_z(params)
    y_center = _handle_mount_y(params, datums)
    if side == "left":
        x0, x1 = 0.0, side_clear
    else:
        x0, x1 = width - side_clear, width
    return {
        "x0": x0,
        "x1": x1,
        "y0": y_center - grip_len / 2,
        "y1": y_center + grip_len / 2,
        "z0": mount_z - grip_depth / 2,
        "z1": mount_z + grip_depth / 2,
    }


def cable_passthrough_footprint(params: Parameters, datums: Datums) -> dict[str, float]:
    """Return axis-aligned cable pass-through bounding box for tests (x0/x1/y0/y1/z0/z1)."""
    diameter = float(params.value("hardware.cable_passthrough_diameter_mm"))
    radius = diameter / 2.0
    width = datums.case_envelope.x.max_mm
    side_clear = _side_clearance_mm(params)
    y_center = float(params.value("hardware.cable_passthrough_mount_y_mm"))
    z_center = float(params.value("hardware.cable_passthrough_mount_z_mm"))
    return {
        "x0": width - side_clear,
        "x1": width,
        "y0": y_center - radius,
        "y1": y_center + radius,
        "z0": z_center - radius,
        "z1": z_center + radius,
    }
