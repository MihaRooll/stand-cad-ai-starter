"""Feet and side handles."""

from __future__ import annotations

from build123d import Align, Cylinder, Location

from stand_cad.geometry.datums import Datums
from stand_cad.geometry.registry import PartRecord
from stand_cad.parameters import Parameters

FOOT_MATERIAL = "silicone_foot"


def build_feet(params: Parameters, datums: Datums) -> list[PartRecord]:
    diameter = float(params.value("hardware.foot_diameter_mm"))
    height = float(params.value("materials.foot_height_mm"))
    width = datums.case_envelope.x.max_mm
    depth = datums.case_envelope.y.max_mm
    inset = diameter / 2
    corners = [
        ("FOOT-001", inset - diameter / 2, inset - diameter / 2),
        ("FOOT-002", width - inset - diameter / 2, inset - diameter / 2),
        ("FOOT-003", inset - diameter / 2, depth - inset - diameter / 2),
        ("FOOT-004", width - inset - diameter / 2, depth - inset - diameter / 2),
    ]
    parts: list[PartRecord] = []
    radius = diameter / 2.0
    for part_id, x0, y0 in corners:
        cx = x0 + radius
        cy = y0 + radius
        solid = Cylinder(
            radius,
            height,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
        ).move(Location((cx, cy, 0.0)))
        parts.append(PartRecord(part_id=part_id, material=FOOT_MATERIAL, solid=solid))
    return parts


def build_handles(params: Parameters, datums: Datums) -> list[PartRecord]:
    """Handle grip geometry is modeled as through-cuts in PANEL-OUT-LEFT/RIGHT-001."""
    _ = params, datums
    return []


def build_hardware_parts(params: Parameters, datums: Datums) -> list[PartRecord]:
    return build_feet(params, datums) + build_handles(params, datums)
