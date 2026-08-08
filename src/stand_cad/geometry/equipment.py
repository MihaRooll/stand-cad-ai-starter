"""Plotter equipment placeholders and design envelopes."""

from __future__ import annotations

from stand_cad.geometry.datums import Datums
from stand_cad.geometry.primitives import box_from_bounds
from stand_cad.geometry.registry import PartRecord
from stand_cad.parameters import Parameters

EQUIP_MATERIAL = "equipment_reference"
ENV_MATERIAL = "reference_envelope"


def _box_from_datum(part_id: str, material: str, datum, *, verify: bool = False) -> PartRecord:
    return PartRecord(
        part_id=part_id,
        material=material,
        solid=box_from_bounds(
            datum.x.min_mm,
            datum.y.min_mm,
            datum.z.min_mm,
            datum.x.max_mm,
            datum.y.max_mm,
            datum.z.max_mm,
        ),
        verify_on_real_machine=verify,
    )


def build_equipment_parts(params: Parameters, datums: Datums) -> list[PartRecord]:
    del params  # datums already resolved from params
    return [
        _box_from_datum("EQUIP-PLOTTER1-001", EQUIP_MATERIAL, datums.plotter1_physical),
        _box_from_datum("EQUIP-PLOTTER2-001", EQUIP_MATERIAL, datums.plotter2_physical),
        _box_from_datum("ENV-PLOTTER1-001", ENV_MATERIAL, datums.plotter1_envelope),
        _box_from_datum("ENV-PLOTTER2-001", ENV_MATERIAL, datums.plotter2_envelope),
    ]
