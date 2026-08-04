"""Horizontal shelf dividers for flat film storage (PLT-007).

Vertical comb-rail / finger-notch dividers removed; recovery at commit 69b1261.
"""

from __future__ import annotations

from stand_cad.geometry.datums import Datums
from stand_cad.geometry.primitives import box_from_bounds
from stand_cad.geometry.registry import PartRecord
from stand_cad.parameters import Parameters, with_shelf_count

SHELF_MATERIAL = "transparent_petg_2mm"


def _shelf_divider_z_bases(params: Parameters, datums: Datums) -> list[float]:
    """Z base (bottom face) of each horizontal shelf divider between compartments."""
    org_z = datums.organizer_floor_top_z_mm
    insert_t = params.org_insert_thickness_mm
    clear_h = float(params.value("film_storage_horizontal.compartment_clear_height_mm"))
    divider_t = float(params.value("film_storage_horizontal.divider_thickness"))
    shelf_count = int(params.value("film_storage_horizontal.shelf_count"))
    z = org_z + insert_t
    bases: list[float] = []
    for _ in range(shelf_count - 1):
        z += clear_h
        bases.append(z)
        z += divider_t
    return bases


def build_divider_parts(
    params: Parameters,
    datums: Datums,
    *,
    shelf_count: int | None = None,
) -> list[PartRecord]:
    """Thin horizontal shelf plates between flat-film compartments."""
    if shelf_count is not None:
        params = with_shelf_count(params, shelf_count)

    org_x = float(params.value("film_storage_horizontal.x"))
    org_y = float(params.value("film_storage_horizontal.y"))
    clear_w = float(params.value("film_storage_horizontal.clear_width"))
    clear_d = float(params.value("film_storage_horizontal.clear_depth"))
    divider_t = float(params.value("film_storage_horizontal.divider_thickness"))

    parts: list[PartRecord] = []
    for index, z_base in enumerate(_shelf_divider_z_bases(params, datums)):
        parts.append(
            PartRecord(
                part_id=f"SHELF-{index:03d}",
                material=SHELF_MATERIAL,
                solid=box_from_bounds(
                    org_x,
                    org_y,
                    z_base,
                    org_x + clear_w,
                    org_y + clear_d,
                    z_base + divider_t,
                ),
                verify_on_real_machine=True,
            )
        )
    return parts


def shelf_divider_centres(params: Parameters, datums: Datums) -> list[tuple[float, float, float]]:
    """Centre (x, y, z) of each horizontal shelf divider — for engagement checks."""
    org_x = float(params.value("film_storage_horizontal.x"))
    org_y = float(params.value("film_storage_horizontal.y"))
    clear_w = float(params.value("film_storage_horizontal.clear_width"))
    clear_d = float(params.value("film_storage_horizontal.clear_depth"))
    divider_t = float(params.value("film_storage_horizontal.divider_thickness"))
    centres: list[tuple[float, float, float]] = []
    for z_base in _shelf_divider_z_bases(params, datums):
        centres.append(
            (
                org_x + clear_w / 2,
                org_y + clear_d / 2,
                z_base + divider_t / 2,
            )
        )
    return centres
