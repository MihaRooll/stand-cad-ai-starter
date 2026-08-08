"""Media-path glide supports, cable-passthrough grommet, and service-volume placeholders."""

from __future__ import annotations

from build123d import Align, Axis, Cylinder, Location, chamfer

from stand_cad.geometry.datums import Datums
from stand_cad.geometry.primitives import box_from_bounds
from stand_cad.geometry.registry import PartRecord
from stand_cad.parameters import Parameters

SVC_INSERT_MATERIAL = "white_composite_3_4mm"
GROMMET_MATERIAL = "soft_trim_brush"
COVER_MATERIAL = "white_composite_3_4mm"
MAINS_INLET_MATERIAL = "hardware_mains_inlet"
SERVICE_VOLUME_MATERIAL = "service_volume"


def _side_clearance_mm(params: Parameters) -> float:
    """Derived side clearance: (case.width - case.internal_width) / 2."""
    width = float(params.value("case.width"))
    internal = float(params.value("case.internal_width"))
    return (width - internal) / 2.0


def _feed_plane_z(params: Parameters, level: str) -> float:
    """Provisional feed-plane height above tray finished top (VERIFY ON REAL MACHINE)."""
    prefix = "lower" if level == "L1" else "upper"
    tray_top = float(params.value(f"plotter.{prefix}_z"))
    return tray_top + float(params.value("plotter.feed_plane_z_provisional_mm"))


def _media_path_centre_x(params: Parameters, datums: Datums) -> float:
    return datums.case_envelope.x.max_mm / 2


def _rear_panel_y(params: Parameters, datums: Datums) -> tuple[float, float]:
    gap = float(params.value("materials.outer_panel_shadow_gap_mm"))
    thickness = float(params.value("materials.inner_panel_thickness_mm"))
    depth = datums.case_envelope.y.max_mm
    y_outer = depth - gap - thickness
    y_inner = depth - gap
    return y_outer, y_inner


def _build_media_support(params: Parameters, datums: Datums, *, level: str) -> PartRecord:
    """Continuous flat support from the plotter's rear edge to the rear wall inner face (D-046)."""
    cx = _media_path_centre_x(params, datums)
    feed_z = _feed_plane_z(params, level)
    clear_w = float(params.value("media_path.clear_width"))
    slot_h = float(params.value("media_path.slot_height_target"))
    support_t = float(params.value("materials.inner_panel_thickness_mm"))
    gap = float(params.value("materials.outer_panel_shadow_gap_mm"))
    inner_t = float(params.value("materials.inner_panel_thickness_mm"))
    plotter_physical = datums.plotter1_physical if level == "L1" else datums.plotter2_physical
    y0 = plotter_physical.y.max_mm
    y1 = datums.case_envelope.y.max_mm - gap - inner_t
    top_z = feed_z - slot_h / 2.0
    return PartRecord(
        part_id=f"MEDIA-SUPPORT-{level}-001",
        material=SVC_INSERT_MATERIAL,
        solid=box_from_bounds(
            cx - clear_w / 2,
            y0,
            top_z - support_t,
            cx + clear_w / 2,
            y1,
            top_z,
        ),
        verify_on_real_machine=True,
    )


def _build_cover_svc(params: Parameters, datums: Datums) -> PartRecord:
    gap = float(params.value("materials.outer_panel_shadow_gap_mm"))
    foot_h = float(params.value("materials.foot_height_mm"))
    width = datums.case_envelope.x.max_mm
    depth = datums.case_envelope.y.max_mm
    cover_t = float(params.value("services.cover_svc_thickness_mm"))
    return PartRecord(
        part_id="COVER-SVC-001",
        material=COVER_MATERIAL,
        solid=box_from_bounds(
            gap,
            depth - gap - cover_t,
            foot_h,
            width - gap,
            depth - gap,
            foot_h + cover_t,
        ),
        verify_on_real_machine=True,
    )


def _build_mains_inlet(params: Parameters, datums: Datums) -> PartRecord:
    gap = float(params.value("materials.outer_panel_shadow_gap_mm"))
    foot_h = float(params.value("materials.foot_height_mm"))
    width = datums.case_envelope.x.max_mm
    cover_t = float(params.value("services.cover_svc_thickness_mm"))
    mi_w = float(params.value("services.mains_inlet_width_mm"))
    mi_h = float(params.value("services.mains_inlet_height_mm"))
    mi_d = float(params.value("services.mains_inlet_depth_mm"))
    y_outer, _y_inner = _rear_panel_y(params, datums)
    return PartRecord(
        part_id="MAINS-INLET-001",
        material=MAINS_INLET_MATERIAL,
        solid=box_from_bounds(
            width / 2 - mi_w / 2,
            y_outer - mi_d,
            foot_h + cover_t + gap,
            width / 2 + mi_w / 2,
            y_outer,
            foot_h + cover_t + gap + mi_h,
        ),
        verify_on_real_machine=True,
    )


def _build_cable_passthrough_grommet(params: Parameters, datums: Datums) -> PartRecord:
    width = datums.case_envelope.x.max_mm
    cp_diameter = float(params.value("hardware.cable_passthrough_diameter_mm"))
    cp_radius = cp_diameter / 2.0
    cp_wall = float(params.value("services.cable_passthrough_grommet_wall_mm"))
    cp_bore_radius = cp_radius - cp_wall
    cp_edge_r = float(params.value("services.cable_passthrough_edge_break_radius_mm"))
    cp_outer_t = float(params.value("materials.outer_panel_thickness_mm"))
    cp_y = float(params.value("hardware.cable_passthrough_mount_y_mm"))
    cp_z = float(params.value("hardware.cable_passthrough_mount_z_mm"))
    cp_eps = 0.5
    cp_outer_cyl = Cylinder(
        cp_radius, cp_outer_t, align=(Align.CENTER, Align.CENTER, Align.MIN)
    ).rotate(Axis.Y, 90)
    cp_inner_cyl = (
        Cylinder(
            cp_bore_radius, cp_outer_t + 2 * cp_eps, align=(Align.CENTER, Align.CENTER, Align.MIN)
        )
        .rotate(Axis.Y, 90)
        .move(Location((0, 0, -cp_eps)))
    )
    cp_ring = cp_outer_cyl - cp_inner_cyl
    cp_rim_edges = [edge for edge in cp_ring.edges() if edge.length > 10]
    cp_bore_rims = [edge for edge in cp_rim_edges if edge.length <= cp_radius * 6]
    cp_grommet = chamfer(cp_bore_rims, length=cp_edge_r)
    cp_grommet = cp_grommet.move(Location((width - cp_outer_t, cp_y, cp_z)))
    return PartRecord(
        part_id="SVC-CABLE-PASSTHROUGH-001",
        material=GROMMET_MATERIAL,
        solid=cp_grommet,
        verify_on_real_machine=True,
    )


def _build_light_strip(params: Parameters, datums: Datums) -> PartRecord:
    gap = float(params.value("materials.outer_panel_shadow_gap_mm"))
    width = datums.case_envelope.x.max_mm
    depth = datums.case_envelope.y.max_mm
    outer_t = float(params.value("materials.outer_panel_thickness_mm"))
    ls_len = float(params.value("services.light_strip_length_mm"))
    ls_w = float(params.value("services.light_strip_width_mm"))
    ls_h = float(params.value("services.light_strip_height_mm"))
    # D-058: top_structure.z_max_mm == case.height now (no unfilled headroom band above the
    # rail line where this used to sit, z_min..z_min+ls_h). Tuck it under FRAME-RAIL-TOP-REAR's
    # bottom face instead — stacking it at the new roofline would bury it inside that rail
    # (rail occupies z_min-profile..z_min at this same Y band).
    profile = float(params.value("materials.frame_profile_size_mm"))
    rail_bottom_z = datums.top_structure.z.min_mm - profile
    return PartRecord(
        part_id="LIGHT-STRIP-001",
        material=SERVICE_VOLUME_MATERIAL,
        solid=box_from_bounds(
            (width - ls_len) / 2,
            depth - gap - ls_w - outer_t,
            rail_bottom_z - ls_h,
            (width + ls_len) / 2,
            depth - gap - outer_t,
            rail_bottom_z,
        ),
        verify_on_real_machine=True,
    )


def _build_adapter_light(params: Parameters, datums: Datums) -> PartRecord:
    gap = float(params.value("materials.outer_panel_shadow_gap_mm"))
    foot_h = float(params.value("materials.foot_height_mm"))
    depth = datums.case_envelope.y.max_mm
    cover_t = float(params.value("services.cover_svc_thickness_mm"))
    mi_h = float(params.value("services.mains_inlet_height_mm"))
    al_w = float(params.value("services.adapter_light_width_mm"))
    al_d = float(params.value("services.adapter_light_depth_mm"))
    al_h = float(params.value("services.adapter_light_height_mm"))
    return PartRecord(
        part_id="ADAPTER-LIGHT-001",
        material=SERVICE_VOLUME_MATERIAL,
        solid=box_from_bounds(
            gap,
            depth - gap - al_d,
            foot_h + cover_t + gap + mi_h + gap,
            gap + al_w,
            depth - gap,
            foot_h + cover_t + gap + mi_h + gap + al_h,
        ),
        verify_on_real_machine=True,
    )


def _build_ctrl_rgbw(params: Parameters, datums: Datums) -> PartRecord:
    gap = float(params.value("materials.outer_panel_shadow_gap_mm"))
    foot_h = float(params.value("materials.foot_height_mm"))
    depth = datums.case_envelope.y.max_mm
    cover_t = float(params.value("services.cover_svc_thickness_mm"))
    mi_h = float(params.value("services.mains_inlet_height_mm"))
    al_d = float(params.value("services.adapter_light_depth_mm"))
    cr_w = float(params.value("services.ctrl_rgbw_width_mm"))
    cr_d = float(params.value("services.ctrl_rgbw_depth_mm"))
    cr_h = float(params.value("services.ctrl_rgbw_height_mm"))
    return PartRecord(
        part_id="CTRL-RGBW-001",
        material=SERVICE_VOLUME_MATERIAL,
        solid=box_from_bounds(
            gap,
            depth - gap - al_d - cr_d - gap,
            foot_h + cover_t + gap + mi_h + gap,
            gap + cr_w,
            depth - gap - al_d - gap,
            foot_h + cover_t + gap + mi_h + gap + cr_h,
        ),
        verify_on_real_machine=True,
    )


def _build_adapter_plotter(
    params: Parameters, datums: Datums, *, suffix: str, plotter_z: float, ax0: float, ax1: float
) -> PartRecord:
    gap = float(params.value("materials.outer_panel_shadow_gap_mm"))
    depth = datums.case_envelope.y.max_mm
    ap_d = float(params.value("services.adapter_plotter_depth_mm"))
    ap_h = float(params.value("services.adapter_plotter_height_mm"))
    pocket_y0 = depth - gap - ap_d
    pocket_y1 = depth - gap
    return PartRecord(
        part_id=f"ADAPTER-{suffix}-001",
        material=SERVICE_VOLUME_MATERIAL,
        solid=box_from_bounds(
            ax0,
            pocket_y0,
            plotter_z - ap_h / 2,
            ax1,
            pocket_y1,
            plotter_z + ap_h / 2,
        ),
        verify_on_real_machine=True,
    )


def _build_cable_channel(params: Parameters, datums: Datums) -> PartRecord:
    gap = float(params.value("materials.outer_panel_shadow_gap_mm"))
    foot_h = float(params.value("materials.foot_height_mm"))
    cover_t = float(params.value("services.cover_svc_thickness_mm"))
    outer_t = float(params.value("materials.outer_panel_thickness_mm"))
    org_y = float(params.value("film_storage_horizontal.y"))
    ch_w = float(params.value("services.cable_channel_width_mm"))
    ch_h = float(params.value("services.cable_channel_height_mm"))
    return PartRecord(
        part_id="CABLE-CH-001",
        material=SERVICE_VOLUME_MATERIAL,
        solid=box_from_bounds(
            gap + outer_t,
            gap + outer_t,
            foot_h + cover_t + gap,
            gap + outer_t + ch_w,
            org_y - gap,
            foot_h + cover_t + gap + ch_h,
        ),
        verify_on_real_machine=True,
    )


def _build_airpath(params: Parameters, datums: Datums) -> PartRecord:
    gap = float(params.value("materials.outer_panel_shadow_gap_mm"))
    foot_h = float(params.value("materials.foot_height_mm"))
    width = datums.case_envelope.x.max_mm
    depth = datums.case_envelope.y.max_mm
    ap_w2 = float(params.value("services.airpath_width_mm"))
    ap_d2 = float(params.value("services.airpath_depth_mm"))
    ap_h2 = float(params.value("services.airpath_height_mm"))
    return PartRecord(
        part_id="AIRPATH-001",
        material=SERVICE_VOLUME_MATERIAL,
        solid=box_from_bounds(
            (width - ap_w2) / 2,
            depth - gap - ap_d2,
            foot_h,
            (width + ap_w2) / 2,
            depth - gap,
            foot_h + ap_h2,
        ),
        verify_on_real_machine=True,
    )


def build_service_parts(params: Parameters, datums: Datums) -> list[PartRecord]:
    """Media-path and cable-service parts.

    Owner 2026-08-06 — MAINS-INLET-001, ADAPTER-LIGHT-001, CTRL-RGBW-001, ADAPTER-P1/P2-001,
    AIRPATH-001 removed as unwanted visual clutter ("cubes"); electrical/adapter service
    volumes are not being modelled as separate placeholder geometry for now.
    """
    parts: list[PartRecord] = []
    for level in ("L1", "L2"):
        parts.append(_build_media_support(params, datums, level=level))
    parts.append(_build_cover_svc(params, datums))
    parts.append(_build_cable_passthrough_grommet(params, datums))
    parts.append(_build_light_strip(params, datums))
    parts.append(_build_cable_channel(params, datums))
    return parts
