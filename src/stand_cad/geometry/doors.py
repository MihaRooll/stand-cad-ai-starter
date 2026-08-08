"""Drop-front piano-hinge compartment doors and cosmetic support struts."""

from __future__ import annotations

import math
from copy import copy
from typing import Literal

from build123d import Align, Axis, Cylinder, Location, Part

from stand_cad.geometry.datums import BoxDatum, Datums
from stand_cad.geometry.frame import FRAME_CLAD_MATERIAL
from stand_cad.geometry.primitives import box_from_bounds
from stand_cad.geometry.registry import PartRecord
from stand_cad.parameters import Parameters

DoorState = Literal["open", "closed"]
STRUT_MATERIAL = "aluminium_strut_hardware"
_STRUT_DIAMETER_MM = 7.0


def _tier_datum(level: str, datums: Datums) -> BoxDatum:
    if level == "lower":
        return datums.plotter1_physical
    if level == "upper":
        return datums.plotter2_physical
    raise ValueError(f"unknown door level: {level}")


def _tier_opening_z_bounds(params: Parameters, level: str) -> tuple[float, float]:
    """Vertical span of the compartment opening (hinge bottom .. divider underside)."""
    tray_t = params.tray_panel_thickness_mm
    lower_z = float(params.value("plotter.lower_z"))
    upper_z = float(params.value("plotter.upper_z"))
    org_z = float(params.value("film_storage_horizontal.z"))
    profile = float(params.value("materials.frame_profile_size_mm"))
    if level == "lower":
        z_bottom = lower_z - tray_t
        z_top = upper_z - tray_t
    elif level == "upper":
        z_bottom = upper_z - tray_t
        z_top = org_z - profile
    else:
        raise ValueError(f"unknown door level: {level}")
    return z_bottom, z_top


def _closed_door_bounds(
    params: Parameters,
    datums: Datums,
    *,
    level: str,
) -> tuple[float, float, float, float, float, float]:
    """Vertical door panel at the tray front plane (Y = datum.y.min)."""
    datum = _tier_datum(level, datums)
    thickness = float(params.value("materials.outer_panel_thickness_mm"))
    y_front = datum.y.min_mm
    z_bottom, z_top = _tier_opening_z_bounds(params, level)
    return (
        datum.x.min_mm,
        y_front - thickness,
        z_bottom,
        datum.x.max_mm,
        y_front,
        z_top,
    )


def _rotate_about_x_at(solid: Part, angle_deg: float, *, y0: float, z0: float) -> Part:
    rotated = copy(solid)
    rotated = rotated.move(Location((0.0, -y0, -z0)))
    rotated = rotated.rotate(Axis.X, angle_deg)
    rotated = rotated.move(Location((0.0, y0, z0)))
    return rotated


def _open_door_settle_dz_mm(params: Parameters, *, level: str, z_bottom: float) -> float:
    """Post-open Z settle so horizontal door top clears slide bottoms (D-076).

    Tray slides travel over the locked horizontal door; door top must sit at or
    below ``slide_bottom_z - tolerance.assembly_mm``.
    """
    slide_h = float(params.value("trays.slide_rail_height_mm"))
    tray_t = params.tray_panel_thickness_mm
    asm_tol = float(params.value("tolerance.assembly_mm"))
    thickness = float(params.value("materials.outer_panel_thickness_mm"))
    if level == "lower":
        datum_z = float(params.value("plotter.lower_z"))
    elif level == "upper":
        datum_z = float(params.value("plotter.upper_z"))
    else:
        raise ValueError(f"unknown door level: {level}")
    slide_bottom_z = datum_z - tray_t - slide_h
    target_top_z = slide_bottom_z - asm_tol
    # After 90° rotation about bottom hinge, door top is at z_bottom (unsettled).
    return target_top_z - thickness - (z_bottom - thickness)


def open_door_settled_horizontal_z_band_mm(
    params: Parameters, *, level: str
) -> tuple[float, float]:
    """Z span [min, max] of a horizontal door slab after Path A settle (D-076/D-089)."""
    slide_h = float(params.value("trays.slide_rail_height_mm"))
    tray_t = params.tray_panel_thickness_mm
    asm_tol = float(params.value("tolerance.assembly_mm"))
    thickness = float(params.value("materials.outer_panel_thickness_mm"))
    if level == "lower":
        datum_z = float(params.value("plotter.lower_z"))
    elif level == "upper":
        datum_z = float(params.value("plotter.upper_z"))
    else:
        raise ValueError(f"unknown door level: {level}")
    slide_bottom_z = datum_z - tray_t - slide_h
    target_top_z = slide_bottom_z - asm_tol
    return target_top_z - thickness, target_top_z


def _door_solid(
    params: Parameters,
    datums: Datums,
    *,
    level: str,
    state: DoorState,
) -> Part:
    x0, y0, z_bottom, x1, y1, z_top = _closed_door_bounds(params, datums, level=level)
    panel = box_from_bounds(x0, y0, z_bottom, x1, y1, z_top)
    if state == "closed":
        return panel
    # Piano hinge on bottom edge — swing forward (−Y) to horizontal work surface.
    opened = _rotate_about_x_at(panel, 90.0, y0=y1, z0=z_bottom)
    settle_dz = _open_door_settle_dz_mm(params, level=level, z_bottom=z_bottom)
    if abs(settle_dz) > 1e-9:
        opened = opened.move(Location((0.0, 0.0, settle_dz)))
    return opened


def _align_z_to_vector(solid: Part, dx: float, dy: float, dz: float) -> Part:
    length = math.sqrt(dx * dx + dy * dy + dz * dz)
    if length < 1e-9:
        return solid
    cos_theta = dz / length
    ax, ay, az = -dy, dx, 0.0
    axis_len = math.sqrt(ax * ax + ay * ay + az * az)
    if axis_len < 1e-9:
        if dz < 0:
            return solid.rotate(Axis.X, 180)
        return solid
    angle = math.degrees(math.acos(max(-1.0, min(1.0, cos_theta))))
    return solid.rotate(Axis((0.0, 0.0, 0.0), (ax / axis_len, ay / axis_len, az / axis_len)), angle)


def _strut_solid(
    p0: tuple[float, float, float],
    p1: tuple[float, float, float],
    *,
    diameter: float,
) -> Part:
    x0, y0, z0 = p0
    x1, y1, z1 = p1
    dx, dy, dz = x1 - x0, y1 - y0, z1 - z0
    length = math.sqrt(dx * dx + dy * dy + dz * dz)
    if length < 1e-6:
        return Cylinder(diameter / 2, 1.0, align=(Align.CENTER, Align.CENTER, Align.MIN))
    cyl = Cylinder(diameter / 2, length, align=(Align.CENTER, Align.CENTER, Align.MIN))
    cyl = _align_z_to_vector(cyl, dx, dy, dz)
    return cyl.move(Location(p0))


def _strut_attachment_points(
    params: Parameters,
    datums: Datums,
    *,
    level: str,
    side: Literal["left", "right"],
) -> tuple[tuple[float, float, float], tuple[float, float, float]]:
    """Strut along corner-post outer face at settled open-door Z (D-076).

    Routes outside tray X-span so struts remain present at all tray extensions.
    """
    datum = _tier_datum(level, datums)
    z_bottom, z_top = _tier_opening_z_bounds(params, level)
    y_front = datum.y.min_mm
    door_height = z_top - z_bottom
    thickness = float(params.value("materials.outer_panel_thickness_mm"))
    width = float(params.value("case.width"))
    settle_dz = _open_door_settle_dz_mm(params, level=level, z_bottom=z_bottom)
    door_z = z_bottom - thickness + settle_dz + thickness / 2
    door_y_back = y_front - door_height + thickness
    if side == "left":
        post_x = 0.0
    else:
        post_x = width
    foot_h = float(params.value("materials.foot_height_mm"))
    asm_tol = float(params.value("tolerance.part_assembly_feature_mm"))
    foot_clear_z = foot_h + _STRUT_DIAMETER_MM / 2 + asm_tol + 0.25
    post_z = max(door_z, foot_clear_z)
    return (post_x, door_y_back, door_z), (post_x, y_front, post_z)


def build_door_level_parts(
    params: Parameters,
    datums: Datums,
    *,
    level: str,
    state: DoorState,
    include_struts: bool = True,
) -> list[PartRecord]:
    if level == "lower":
        door_id = "DOOR-LOWER-001"
        strut_prefix = "DOOR-STRUT-LOWER"
    elif level == "upper":
        door_id = "DOOR-UPPER-001"
        strut_prefix = "DOOR-STRUT-UPPER"
    else:
        raise ValueError(f"unknown door level: {level}")

    parts: list[PartRecord] = [
        PartRecord(
            part_id=door_id,
            material=FRAME_CLAD_MATERIAL,
            solid=_door_solid(params, datums, level=level, state=state),
        )
    ]
    if state == "open" and include_struts:
        for side, suffix in (("left", "L"), ("right", "R")):
            p0, p1 = _strut_attachment_points(params, datums, level=level, side=side)
            parts.append(
                PartRecord(
                    part_id=f"{strut_prefix}-{suffix}-001",
                    material=STRUT_MATERIAL,
                    solid=_strut_solid(p0, p1, diameter=_STRUT_DIAMETER_MM),
                    verify_on_real_machine=True,
                )
            )
    return parts


def build_door_parts(
    params: Parameters,
    datums: Datums,
    *,
    door_state: dict[str, DoorState] | None = None,
    include_struts: bool = True,
) -> list[PartRecord]:
    """One drop-front door per plotter tier; struts only when that tier's door is open."""
    states: dict[str, DoorState] = {"lower": "closed", "upper": "closed"}
    if door_state:
        states.update(door_state)
    parts: list[PartRecord] = []
    for level in ("lower", "upper"):
        parts.extend(
            build_door_level_parts(
                params,
                datums,
                level=level,
                state=states[level],
                include_struts=include_struts,
            )
        )
    return parts
