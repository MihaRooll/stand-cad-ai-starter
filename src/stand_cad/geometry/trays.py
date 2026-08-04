"""Tray platforms, slides, soft stops, vibration mounts, and lid envelopes."""

from __future__ import annotations

from stand_cad.geometry.datums import BoxDatum, Datums
from stand_cad.geometry.primitives import box_from_bounds
from stand_cad.geometry.registry import PartRecord
from stand_cad.parameters import Parameters

TRAY_MATERIAL = "sandwich_panel_10_12mm"
SLIDE_MATERIAL = "full_extension_slide_hardware"
SOFTSTOP_MATERIAL = "elastomer_soft_stop"
VIBMOUNT_MATERIAL = "elastomer_vibration_mount"
LID_ENVELOPE_MATERIAL = "reference_envelope"
FRAME_MATERIAL = "aluminium_angle_15x15x1.5"


def _tray_bounds(
    params: Parameters, datum: BoxDatum
) -> tuple[float, float, float, float, float, float]:
    """Closed tray platform under plotter footprint."""
    thickness = params.tray_panel_thickness_mm
    return (
        datum.x.min_mm,
        datum.y.min_mm,
        datum.z.min_mm - thickness,
        datum.x.max_mm,
        datum.y.max_mm,
        datum.z.min_mm,
    )


def _slide_bounds(
    params: Parameters,
    tray_bounds: tuple[float, float, float, float, float, float],
    *,
    side: str,
) -> tuple[float, float, float, float, float, float]:
    rail_w = float(params.value("trays.slide_rail_width_mm"))
    rail_h = float(params.value("trays.slide_rail_height_mm"))
    x0, y0, _z0, x1, y1, z_tray_bottom = tray_bounds
    if side == "left":
        sx0 = x0
        sx1 = x0 + rail_w
    else:
        sx0 = x1 - rail_w
        sx1 = x1
    return (sx0, y0, z_tray_bottom - rail_h, sx1, y1, z_tray_bottom)


def _soft_stop_bounds(
    params: Parameters,
    tray_bounds: tuple[float, float, float, float, float, float],
) -> tuple[float, float, float, float, float, float]:
    size = float(params.value("trays.soft_stop_size_mm"))
    x0, y0, z0, x1, y1, z1 = tray_bounds
    cx = (x0 + x1) / 2
    cy = y1
    cz = (z0 + z1) / 2
    half = size / 2
    return (cx - half, cy - half, cz - half, cx + half, cy + half, cz + half)


def _vib_mount_positions(
    params: Parameters,
    datum: BoxDatum,
) -> list[tuple[float, float]]:
    """Four mount centres under plotter corners (inset from edges)."""
    diameter = float(params.value("trays.vibration_mount_diameter_mm"))
    inset = diameter
    return [
        (datum.x.min_mm + inset, datum.y.min_mm + inset),
        (datum.x.max_mm - inset, datum.y.min_mm + inset),
        (datum.x.min_mm + inset, datum.y.max_mm - inset),
        (datum.x.max_mm - inset, datum.y.max_mm - inset),
    ]


def _vib_mount_bounds(
    params: Parameters,
    tray_bounds: tuple[float, float, float, float, float, float],
    cx: float,
    cy: float,
) -> tuple[float, float, float, float, float, float]:
    diameter = float(params.value("trays.vibration_mount_diameter_mm"))
    height = float(params.value("trays.vibration_mount_height_mm"))
    _x0, _y0, _z0, _x1, _y1, z_tray_top = tray_bounds
    half = diameter / 2
    return (cx - half, cy - half, z_tray_top, cx + half, cy + half, z_tray_top + height)


def _lid_envelope_bounds(
    params: Parameters,
    datum: BoxDatum,
) -> tuple[float, float, float, float, float, float]:
    lid_h = float(params.value("plotter.lid_open_envelope_height_mm"))
    return (
        datum.x.min_mm,
        datum.y.min_mm,
        datum.z.max_mm,
        datum.x.max_mm,
        datum.y.max_mm,
        datum.z.max_mm + lid_h,
    )


def _tray_frame_rail_bounds(
    params: Parameters,
    tray_bounds: tuple[float, float, float, float, float, float],
    *,
    side: str,
) -> tuple[float, float, float, float, float, float]:
    profile = float(params.value("materials.frame_profile_size_mm"))
    rail_h = float(params.value("trays.slide_rail_height_mm"))
    x0, y0, _z0, x1, y1, z_tray_bottom = tray_bounds
    z_base = z_tray_bottom - rail_h - profile
    z_top = z_base + profile
    if side == "left":
        return (x0, y0, z_base, x0 + profile, y1, z_top)
    return (x1 - profile, y0, z_base, x1, y1, z_top)


def build_tray_level_parts(
    params: Parameters,
    datums: Datums,
    *,
    level: str,
    include_lid_envelope: bool = False,
) -> list[PartRecord]:
    """Build tray, slides, soft stop, vib mounts, lid envelope for one plotter level."""
    if level == "lower":
        datum = datums.plotter1_physical
        tray_id = "TRAY-LOWER-001"
        slide_prefix = "SLIDE-LOWER"
        soft_id = "SOFTSTOP-LOWER-001"
        vib_prefix = "VIBMOUNT-P1"
        lid_id = "LID-ENVELOPE-P1-001"
        rail_prefix = "FRAME-RAIL-TRAY-LOWER"
    elif level == "upper":
        datum = datums.plotter2_physical
        tray_id = "TRAY-UPPER-001"
        slide_prefix = "SLIDE-UPPER"
        soft_id = "SOFTSTOP-UPPER-001"
        vib_prefix = "VIBMOUNT-P2"
        lid_id = "LID-ENVELOPE-P2-001"
        rail_prefix = "FRAME-RAIL-TRAY-UPPER"
    else:
        raise ValueError(f"unknown tray level: {level}")

    tray_b = _tray_bounds(params, datum)
    parts: list[PartRecord] = [
        PartRecord(
            part_id=tray_id,
            material=TRAY_MATERIAL,
            solid=box_from_bounds(*tray_b),
        ),
    ]
    for side, suffix in (("left", "LEFT"), ("right", "RIGHT")):
        slide_b = _slide_bounds(params, tray_b, side=side)
        parts.append(
            PartRecord(
                part_id=f"{slide_prefix}-{suffix}-001",
                material=SLIDE_MATERIAL,
                solid=box_from_bounds(*slide_b),
                verify_on_real_machine=True,
            )
        )
        rail_b = _tray_frame_rail_bounds(params, tray_b, side=side)
        lr = "L" if side == "left" else "R"
        parts.append(
            PartRecord(
                part_id=f"{rail_prefix}-{lr}-001",
                material=FRAME_MATERIAL,
                solid=box_from_bounds(*rail_b),
            )
        )
    parts.append(
        PartRecord(
            part_id=soft_id,
            material=SOFTSTOP_MATERIAL,
            solid=box_from_bounds(*_soft_stop_bounds(params, tray_b)),
            verify_on_real_machine=True,
        )
    )
    for index, (cx, cy) in enumerate(_vib_mount_positions(params, datum), start=1):
        parts.append(
            PartRecord(
                part_id=f"{vib_prefix}-{index:03d}",
                material=VIBMOUNT_MATERIAL,
                solid=box_from_bounds(*_vib_mount_bounds(params, tray_b, cx, cy)),
                verify_on_real_machine=True,
            )
        )
    if include_lid_envelope:
        parts.append(
            PartRecord(
                part_id=lid_id,
                material=LID_ENVELOPE_MATERIAL,
                solid=box_from_bounds(*_lid_envelope_bounds(params, datum)),
                verify_on_real_machine=True,
            )
        )
    return parts


def build_lid_envelope_parts(params: Parameters, datums: Datums) -> list[PartRecord]:
    """Provisional open-lid envelopes — service states only."""
    lids: list[PartRecord] = []
    for level in ("lower", "upper"):
        lids.extend(
            part
            for part in build_tray_level_parts(
                params, datums, level=level, include_lid_envelope=True
            )
            if part.part_id.startswith("LID-ENVELOPE-")
        )
    return lids


def build_tray_parts(params: Parameters, datums: Datums) -> list[PartRecord]:
    """Both tray levels at closed (transport) positions — no lid envelopes."""
    return build_tray_level_parts(params, datums, level="lower") + build_tray_level_parts(
        params, datums, level="upper"
    )
