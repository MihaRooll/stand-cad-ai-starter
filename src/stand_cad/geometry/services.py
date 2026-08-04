"""Media-path service inserts, edge guards, rear supports, and service volumes."""

from __future__ import annotations

from stand_cad.geometry.datums import Datums
from stand_cad.geometry.primitives import box_from_bounds
from stand_cad.geometry.registry import PartRecord
from stand_cad.parameters import Parameters

SVC_INSERT_MATERIAL = "white_composite_3_4mm"
EDGEGUARD_MATERIAL = "soft_trim_brush"
REARSUPPORT_MATERIAL = "white_composite_3_4mm"
COVER_MATERIAL = "white_composite_3_4mm"
MAINS_INLET_MATERIAL = "hardware_mains_inlet"
SERVICE_VOLUME_MATERIAL = "service_volume"


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


def _build_level_service_inserts(
    params: Parameters,
    datums: Datums,
    *,
    level: str,
) -> list[PartRecord]:
    """SVC-INSERT and EDGEGUARD for one plotter level."""
    cx = _media_path_centre_x(params, datums)
    feed_z = _feed_plane_z(params, level)
    insert_w = float(params.value("services.svc_insert_width_mm"))
    insert_h = float(params.value("services.svc_insert_height_mm"))
    edge_d = float(params.value("services.edgeguard_depth_mm"))
    edge_h = float(params.value("services.edgeguard_height_mm"))
    y_outer, y_inner = _rear_panel_y(params, datums)
    z0 = feed_z - insert_h / 2
    z1 = feed_z + insert_h / 2

    insert = PartRecord(
        part_id=f"SVC-INSERT-{level}-001",
        material=SVC_INSERT_MATERIAL,
        solid=box_from_bounds(
            cx - insert_w / 2,
            y_outer,
            z0,
            cx + insert_w / 2,
            y_inner,
            z1,
        ),
        verify_on_real_machine=True,
    )
    edge_top = PartRecord(
        part_id=f"EDGEGUARD-{level}-001",
        material=EDGEGUARD_MATERIAL,
        solid=box_from_bounds(
            cx - insert_w / 2,
            y_outer - edge_d,
            z1 - edge_h,
            cx + insert_w / 2,
            y_outer,
            z1,
        ),
        verify_on_real_machine=True,
    )
    return [insert, edge_top]


def _build_rear_support(params: Parameters, datums: Datums, *, level: str) -> PartRecord:
    cx = _media_path_centre_x(params, datums)
    feed_z = _feed_plane_z(params, level)
    depth = float(params.value("services.rearsupport_depth_mm"))
    height = float(params.value("services.rearsupport_height_mm"))
    gap = float(params.value("materials.outer_panel_shadow_gap_mm"))
    thickness = float(params.value("materials.inner_panel_thickness_mm"))
    y_inner = datums.case_envelope.y.max_mm - gap
    y_outer = y_inner - thickness
    return PartRecord(
        part_id=f"REARSUPPORT-{level}-001",
        material=REARSUPPORT_MATERIAL,
        solid=box_from_bounds(
            cx - float(params.value("media_path.clear_width")) / 2,
            y_outer - depth,
            feed_z - height / 2,
            cx + float(params.value("media_path.clear_width")) / 2,
            y_outer,
            feed_z + height / 2,
        ),
        verify_on_real_machine=True,
    )


def build_service_parts(params: Parameters, datums: Datums) -> list[PartRecord]:
    """All Packet-3 service, media-path, and electrical service-volume parts."""
    gap = float(params.value("materials.outer_panel_shadow_gap_mm"))
    foot_h = float(params.value("materials.foot_height_mm"))
    width = datums.case_envelope.x.max_mm
    depth = datums.case_envelope.y.max_mm
    outer_t = float(params.value("materials.outer_panel_thickness_mm"))

    parts: list[PartRecord] = []
    for level in ("L1", "L2"):
        parts.extend(_build_level_service_inserts(params, datums, level=level))
        parts.append(_build_rear_support(params, datums, level=level))

    cover_t = float(params.value("services.cover_svc_thickness_mm"))
    parts.append(
        PartRecord(
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
    )

    mi_w = float(params.value("services.mains_inlet_width_mm"))
    mi_h = float(params.value("services.mains_inlet_height_mm"))
    mi_d = float(params.value("services.mains_inlet_depth_mm"))
    y_outer, _y_inner = _rear_panel_y(params, datums)
    parts.append(
        PartRecord(
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
    )

    ls_len = float(params.value("services.light_strip_length_mm"))
    ls_w = float(params.value("services.light_strip_width_mm"))
    ls_h = float(params.value("services.light_strip_height_mm"))
    top_z = float(params.value("top_structure.z_min_mm"))
    parts.append(
        PartRecord(
            part_id="LIGHT-STRIP-001",
            material=SERVICE_VOLUME_MATERIAL,
            solid=box_from_bounds(
                (width - ls_len) / 2,
                depth - gap - ls_w - outer_t,
                top_z,
                (width + ls_len) / 2,
                depth - gap - outer_t,
                top_z + ls_h,
            ),
            verify_on_real_machine=True,
        )
    )

    al_w = float(params.value("services.adapter_light_width_mm"))
    al_d = float(params.value("services.adapter_light_depth_mm"))
    al_h = float(params.value("services.adapter_light_height_mm"))
    parts.append(
        PartRecord(
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
    )

    cr_w = float(params.value("services.ctrl_rgbw_width_mm"))
    cr_d = float(params.value("services.ctrl_rgbw_depth_mm"))
    cr_h = float(params.value("services.ctrl_rgbw_height_mm"))
    parts.append(
        PartRecord(
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
    )

    ap_w = float(params.value("services.adapter_plotter_width_mm"))
    ap_d = float(params.value("services.adapter_plotter_depth_mm"))
    ap_h = float(params.value("services.adapter_plotter_height_mm"))
    foot_inset = float(params.value("hardware.foot_diameter_mm"))
    pocket_y0 = depth - gap - ap_d
    pocket_y1 = depth - gap
    adapter_placements = (
        ("P1", float(params.value("plotter.lower_z")), gap + foot_inset, gap + foot_inset + ap_w),
        (
            "P2",
            float(params.value("plotter.upper_z")),
            width - gap - foot_inset - ap_w,
            width - gap - foot_inset,
        ),
    )
    for suffix, plotter_z, ax0, ax1 in adapter_placements:
        parts.append(
            PartRecord(
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
        )

    ch_w = float(params.value("services.cable_channel_width_mm"))
    ch_h = float(params.value("services.cable_channel_height_mm"))
    org_y = float(params.value("film_storage.y"))
    parts.append(
        PartRecord(
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
    )

    ap_w2 = float(params.value("services.airpath_width_mm"))
    ap_d2 = float(params.value("services.airpath_depth_mm"))
    ap_h2 = float(params.value("services.airpath_height_mm"))
    parts.append(
        PartRecord(
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
    )

    return parts
