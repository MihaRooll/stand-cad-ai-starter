"""Organizer floor and replaceable insert."""

from __future__ import annotations

from stand_cad.geometry.datums import Datums
from stand_cad.geometry.primitives import box_from_bounds
from stand_cad.geometry.registry import PartRecord
from stand_cad.parameters import Parameters

ORG_FLOOR_MATERIAL = "sandwich_panel_10_12mm"
ORG_INSERT_MATERIAL = "hdpe_insert_thin"


def build_organizer_parts(params: Parameters, datums: Datums) -> list[PartRecord]:
    floor_t = float(params.value("materials.organizer_floor_thickness_mm"))
    insert_t = params.org_insert_thickness_mm
    org_x = float(params.value("film_storage.x"))
    org_y = float(params.value("film_storage.y"))
    org_z_top = datums.organizer_floor_top_z_mm
    org_z_bottom = org_z_top - floor_t

    floor = PartRecord(
        part_id="ORG-FLOOR-001",
        material=ORG_FLOOR_MATERIAL,
        solid=box_from_bounds(
            org_x,
            org_y,
            org_z_bottom,
            org_x + float(params.value("film_storage.clear_width")),
            org_y + float(params.value("film_storage.clear_depth")),
            org_z_top,
        ),
    )
    insert = PartRecord(
        part_id="ORG-INSERT-001",
        material=ORG_INSERT_MATERIAL,
        solid=box_from_bounds(
            org_x,
            org_y,
            org_z_top,
            org_x + float(params.value("film_storage.clear_width")),
            org_y + float(params.value("film_storage.clear_depth")),
            org_z_top + insert_t,
        ),
        verify_on_real_machine=True,
    )
    return [floor, insert]
