"""Organizer floor and replaceable insert for horizontal film shelves."""

from __future__ import annotations

from stand_cad.geometry.datums import Datums
from stand_cad.geometry.primitives import box_from_bounds
from stand_cad.geometry.registry import PartRecord
from stand_cad.parameters import Parameters

ORG_FLOOR_MATERIAL = "sandwich_panel_10_12mm"
ORG_INSERT_MATERIAL = "hdpe_insert_thin"


def _build_org_floor(params: Parameters, datums: Datums) -> PartRecord:
    floor_t = float(params.value("materials.organizer_floor_thickness_mm"))
    org_x = float(params.value("film_storage_horizontal.x"))
    org_y = float(params.value("film_storage_horizontal.y"))
    org_z_top = datums.organizer_floor_top_z_mm
    org_z_bottom = org_z_top - floor_t
    clear_w = float(params.value("film_storage_horizontal.clear_width"))
    clear_d = float(params.value("film_storage_horizontal.clear_depth"))
    return PartRecord(
        part_id="ORG-FLOOR-001",
        material=ORG_FLOOR_MATERIAL,
        solid=box_from_bounds(
            org_x,
            org_y,
            org_z_bottom,
            org_x + clear_w,
            org_y + clear_d,
            org_z_top,
        ),
    )


def _build_org_insert(params: Parameters, datums: Datums) -> PartRecord:
    insert_t = params.org_insert_thickness_mm
    org_x = float(params.value("film_storage_horizontal.x"))
    org_y = float(params.value("film_storage_horizontal.y"))
    org_z_top = datums.organizer_floor_top_z_mm
    clear_w = float(params.value("film_storage_horizontal.clear_width"))
    clear_d = float(params.value("film_storage_horizontal.clear_depth"))
    return PartRecord(
        part_id="ORG-INSERT-001",
        material=ORG_INSERT_MATERIAL,
        solid=box_from_bounds(
            org_x,
            org_y,
            org_z_top,
            org_x + clear_w,
            org_y + clear_d,
            org_z_top + insert_t,
        ),
        verify_on_real_machine=True,
    )


def build_organizer_parts(params: Parameters, datums: Datums) -> list[PartRecord]:
    return [_build_org_floor(params, datums), _build_org_insert(params, datums)]
