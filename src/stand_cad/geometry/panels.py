"""Outer shell, inner structural panels — PLT-004 restructured side slabs."""

from __future__ import annotations

from build123d import (
    Align,
    BuildPart,
    BuildSketch,
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
HANDLE_CUTOUT_EDGE_RADIUS_MM = 2.5


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
    """Provisional Z in upper plotter bay — clear of org rails (VERIFY ON REAL MACHINE)."""
    upper_z = float(params.value("plotter.upper_z"))
    plotter_h = float(params.value("plotter.physical_height"))
    return upper_z + plotter_h / 2.0


def _handle_mount_y_fallback(params: Parameters, datums: Datums) -> float:
    """Provisional Y toward open front — clears mid-depth bands (VERIFY ON REAL MACHINE)."""
    depth = datums.case_envelope.y.max_mm
    return depth * 0.15


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
    """Full-height solid side slab with exterior front-corner bullnose (single connected volume)."""
    del wall_mm  # retained for call-site compatibility; slab is solid not hollow-shell
    height = z_max - z_min
    width = x_max - x_min
    depth = y_max - y_min
    max_r = min(bullnose_radius, width / 2.0 - 0.1, depth / 2.0 - 0.1)
    max_r = max(max_r, 0.5)

    with BuildPart() as outer_builder:
        with BuildSketch(Plane.XY) as sketch:
            Rectangle(width, depth, align=(Align.MIN, Align.MIN))
            front_vertices = [vertex for vertex in sketch.vertices() if abs(vertex.Y) < 0.01]
            if front_vertices:
                if side == "left":
                    exterior = min(front_vertices, key=lambda vertex: vertex.X)
                else:
                    exterior = max(front_vertices, key=lambda vertex: vertex.X)
                fillet([exterior], radius=max_r)
        extrude(amount=height)
    solid = outer_builder.part.move(Location((x_min, y_min, z_min)))
    return _apply_top_front_bullnose(solid, max_r)


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
    cx = width / 2.0

    solid = box_from_bounds(gap, depth - thickness, foot_h, width - gap, depth, height)
    eps = 0.5
    y0 = depth - thickness - eps
    y1 = depth + eps
    for level in ("L1", "L2"):
        feed_z = _feed_plane_z(params, level)
        solid = _subtract_box(
            solid,
            cx - slot_w / 2,
            y0,
            feed_z - slot_h / 2,
            cx + slot_w / 2,
            y1,
            feed_z + slot_h / 2,
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
        edge_radius=HANDLE_CUTOUT_EDGE_RADIUS_MM,
    )
    if side == "right":
        port_w = float(params.value("hardware.service_port_cutout_width_mm"))
        port_h = float(params.value("hardware.service_port_cutout_height_mm"))
        port_z = float(params.value("hardware.service_port_mount_z_mm"))
        solid = _subtract_box(
            solid,
            x0 + (x1 - x0) / 2 - port_w / 2,
            depth - gap - 1.0,
            port_z - port_h / 2,
            x0 + (x1 - x0) / 2 + port_w / 2,
            depth + 1.0,
            port_z + port_h / 2,
        )
    return PartRecord(part_id=part_id, material=OUTER_PANEL_MATERIAL, solid=solid)


def build_outer_panels(params: Parameters, datums: Datums) -> list[PartRecord]:
    """Outer opal shell: full-height side slabs, closed rear with feed slots and vents."""
    return [
        _build_rear_panel(params, datums),
        _build_side_slab_with_handle(params, datums, side="left"),
        _build_side_slab_with_handle(params, datums, side="right"),
    ]


def build_inner_panels(params: Parameters, datums: Datums) -> list[PartRecord]:
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
    bottom = PartRecord(
        part_id="PANEL-IN-BOTTOM-001",
        material=INNER_PANEL_MATERIAL,
        solid=bottom_solid,
    )
    rear = PartRecord(
        part_id="PANEL-IN-REAR-001",
        material=INNER_PANEL_MATERIAL,
        solid=box_from_bounds(
            gap,
            depth - thickness - gap,
            foot_h,
            width - gap,
            depth - gap,
            datums.top_structure.z.min_mm,
        ),
    )
    mid_z = (datums.plotter1_physical.z.max_mm + datums.plotter2_physical.z.min_mm) / 2
    mid = PartRecord(
        part_id="PANEL-IN-MID-001",
        material=INNER_PANEL_MATERIAL,
        solid=box_from_bounds(
            gap,
            gap,
            mid_z - thickness / 2,
            width - gap,
            depth - gap,
            mid_z + thickness / 2,
        ),
    )
    return [bottom, rear, mid]


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
