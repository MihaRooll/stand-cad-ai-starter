"""Organizer comb rail, film dividers, and front retainer."""

from __future__ import annotations

from build123d import Align, Cylinder, Location, Part

from stand_cad.geometry.datums import Datums
from stand_cad.geometry.primitives import box_from_bounds
from stand_cad.geometry.registry import PartRecord
from stand_cad.parameters import Parameters, with_cells

COMB_RAIL_MATERIAL = "sandwich_panel_10_12mm"
DIVIDER_MATERIAL = "transparent_petg_2mm"
RETAINER_MATERIAL = "transparent_petg_2mm"


def _divider_x_positions(params: Parameters) -> list[float]:
    """X min coordinate for each divider (plan section 5 formula)."""
    org_x = float(params.value("film_storage.x"))
    cell_w = params.cell_width_mm
    divider_t = float(params.value("film_storage.divider_thickness"))
    return [org_x + i * (cell_w + divider_t) for i in range(params.divider_count)]


def _build_comb_rail_solid(params: Parameters, datums: Datums) -> Part:
    """Comb retention rail with through-slots at each divider position."""
    org_x = float(params.value("film_storage.x"))
    org_y = float(params.value("film_storage.y"))
    clear_w = float(params.value("film_storage.clear_width"))
    org_z = datums.organizer_floor_top_z_mm
    slot_depth = float(params.value("film_storage.comb_slot_depth_mm"))
    rail_depth = float(params.value("film_storage.comb_rail_front_depth_mm"))
    divider_t = float(params.value("film_storage.divider_thickness"))
    clearance = params.comb_slot_clearance_mm

    rail = box_from_bounds(
        org_x,
        org_y,
        org_z,
        org_x + clear_w,
        org_y + rail_depth,
        org_z + slot_depth,
    )
    slot_pad = clearance / 2
    for x_min in _divider_x_positions(params):
        slot = box_from_bounds(
            x_min - clearance / 2,
            org_y - slot_pad,
            org_z - slot_pad,
            x_min + divider_t + clearance / 2,
            org_y + rail_depth + slot_pad,
            org_z + slot_depth + slot_pad,
        )
        rail = rail - slot
    return rail


def _build_divider_solid(params: Parameters, datums: Datums, index: int) -> Part:
    org_y = float(params.value("film_storage.y"))
    org_z = datums.organizer_floor_top_z_mm
    insert_t = params.org_insert_thickness_mm
    divider_t = float(params.value("film_storage.divider_thickness"))
    divider_h = params.divider_height_mm
    divider_d = float(params.value("film_storage.divider_depth"))
    finger_r = params.finger_cutout_radius_mm
    x_min = _divider_x_positions(params)[index]
    z_bottom = org_z
    z_top = org_z + insert_t + divider_h
    y_front = org_y
    solid = box_from_bounds(
        x_min,
        y_front,
        z_bottom,
        x_min + divider_t,
        y_front + divider_d,
        z_top,
    )
    # Semicircular finger notch at top-front edge (TZ section 6, R25-35).
    x_mid = x_min + divider_t / 2
    cutter = Cylinder(
        finger_r,
        divider_t + 2.0,
        align=(Align.CENTER, Align.CENTER, Align.CENTER),
    ).move(Location((x_mid, y_front + finger_r, z_top - finger_r)))
    return solid - cutter


def build_divider_parts(
    params: Parameters,
    datums: Datums,
    *,
    cells: int | None = None,
) -> list[PartRecord]:
    """Comb rail, parametrized dividers, and front retainer."""
    if cells is not None:
        params = with_cells(params, cells)

    retainer_h = params.front_retainer_height_mm
    org_x = float(params.value("film_storage.x"))
    clear_w = float(params.value("film_storage.clear_width"))
    org_y = float(params.value("film_storage.y"))
    rail_front = float(params.value("film_storage.comb_rail_front_depth_mm"))
    insert_t = params.org_insert_thickness_mm
    z_base = datums.organizer_floor_top_z_mm + insert_t
    parts: list[PartRecord] = [
        PartRecord(
            part_id="ORG-COMB-RAIL-001",
            material=COMB_RAIL_MATERIAL,
            solid=_build_comb_rail_solid(params, datums),
            verify_on_real_machine=True,
        ),
        PartRecord(
            part_id="RETAINER-001",
            material=RETAINER_MATERIAL,
            solid=box_from_bounds(
                org_x,
                org_y,
                z_base,
                org_x + clear_w,
                org_y + rail_front,
                z_base + retainer_h,
            ),
        ),
    ]
    for index in range(params.divider_count):
        parts.append(
            PartRecord(
                part_id=f"DIVIDER-{index:03d}",
                material=DIVIDER_MATERIAL,
                solid=_build_divider_solid(params, datums, index),
                verify_on_real_machine=True,
            )
        )
    return parts


def divider_slot_centres(params: Parameters, datums: Datums) -> list[tuple[float, float, float]]:
    """Slot centre (x, y, z) for each divider position — for engagement checks."""
    org_y = float(params.value("film_storage.y"))
    org_z = datums.organizer_floor_top_z_mm
    rail_depth = float(params.value("film_storage.comb_rail_front_depth_mm"))
    slot_depth = float(params.value("film_storage.comb_slot_depth_mm"))
    divider_t = float(params.value("film_storage.divider_thickness"))
    centres: list[tuple[float, float, float]] = []
    for x_min in _divider_x_positions(params):
        centres.append(
            (
                x_min + divider_t / 2,
                org_y + rail_depth / 2,
                org_z + slot_depth / 2,
            )
        )
    return centres
