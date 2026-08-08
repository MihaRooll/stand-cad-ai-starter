"""Horizontal shelf dividers for flat film storage (PLT-007).

Vertical comb-rail / finger-notch dividers removed; recovery at commit 69b1261.
"""

from __future__ import annotations

from build123d import Part

from stand_cad.geometry.datums import Datums
from stand_cad.geometry.primitives import box_from_bounds
from stand_cad.geometry.registry import PartRecord
from stand_cad.parameters import Parameters, with_shelf_count

SHELF_MATERIAL = "transparent_petg_2mm"
SHELF_SUPPORT_MATERIAL = "aluminium_angle_15x15x1.5"


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


def build_single_shelf_divider(
    part_id: str, params: Parameters, datums: Datums
) -> PartRecord:
    """Build one horizontal shelf divider by part_id (e.g. SHELF-000)."""
    index = int(part_id.split("-")[1])
    org_x = float(params.value("film_storage_horizontal.x"))
    org_y = float(params.value("film_storage_horizontal.y"))
    clear_w = float(params.value("film_storage_horizontal.clear_width"))
    clear_d = float(params.value("film_storage_horizontal.clear_depth"))
    divider_t = float(params.value("film_storage_horizontal.divider_thickness"))
    z_bases = _shelf_divider_z_bases(params, datums)
    if index >= len(z_bases):
        raise ValueError(f"unknown shelf divider id: {part_id}")
    z_base = z_bases[index]
    return PartRecord(
        part_id=part_id,
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


def build_divider_parts(
    params: Parameters,
    datums: Datums,
    *,
    shelf_count: int | None = None,
) -> list[PartRecord]:
    """Thin horizontal shelf plates between flat-film compartments."""
    if shelf_count is not None:
        params = with_shelf_count(params, shelf_count)

    parts: list[PartRecord] = []
    for index, _z_base in enumerate(_shelf_divider_z_bases(params, datums)):
        parts.append(build_single_shelf_divider(f"SHELF-{index:03d}", params, datums))
    return parts


def _shelf_support_x_bounds(params: Parameters, datums: Datums, side: str) -> tuple[float, float]:
    """Cavity-depth span (outer skin inner face to shelf edge) — see D-058 follow-up."""
    wall_mm = float(params.value("materials.outer_panel_thickness_mm"))
    side_clear = (
        float(params.value("case.width")) - float(params.value("case.internal_width"))
    ) / 2.0
    width = datums.case_envelope.x.max_mm
    if side == "left":
        return wall_mm, side_clear
    return width - side_clear, width - wall_mm


def _shelf_support_l_angle_solid(
    params: Parameters,
    datums: Datums,
    *,
    side: str,
    z_base: float,
) -> Part:
    """15×15×1.5 L-angle — vertical leg in cavity X-band; horizontal leg bears shelf."""
    profile = float(params.value("materials.frame_profile_size_mm"))
    wall = float(params.value("materials.frame_wall_thickness_mm"))
    divider_t = float(params.value("film_storage_horizontal.divider_thickness"))
    org_y = float(params.value("film_storage_horizontal.y"))
    clear_d = float(params.value("film_storage_horizontal.clear_depth"))
    y0 = org_y
    y1 = org_y + clear_d
    x_cavity0, x_cavity1 = _shelf_support_x_bounds(params, datums, side)

    z_shelf_center = z_base + divider_t / 2.0
    z_vert0 = z_shelf_center - profile / 2.0
    z_vert1 = z_shelf_center + profile / 2.0
    z_horiz0 = z_base - wall
    z_horiz1 = z_base

    if side == "left":
        leg_v = box_from_bounds(x_cavity0, y0, z_vert0, x_cavity0 + profile, y1, z_vert1)
        leg_h = box_from_bounds(x_cavity0, y0, z_horiz0, x_cavity1, y1, z_horiz1)
    elif side == "right":
        leg_v = box_from_bounds(x_cavity1 - profile, y0, z_vert0, x_cavity1, y1, z_vert1)
        leg_h = box_from_bounds(x_cavity0, y0, z_horiz0, x_cavity1, y1, z_horiz1)
    else:
        raise ValueError(f"unknown shelf support side: {side}")
    return leg_v + leg_h


def build_single_shelf_support(
    part_id: str, params: Parameters, datums: Datums
) -> PartRecord:
    """L-angle cleat closing the side-slab cavity gap so a SHELF-* divider has real bearing.

    D-065 cycle-2: **15×15×1.5 mm Al L-angle** (not a 2 mm flat plate). Vertical leg sits in the
    cavity X-band only (left X∈[3,18] mm, right X∈[632,647] mm) with **15 mm** Z height centred on
    the shelf band; horizontal leg spans the **17 mm** cavity depth (3→20 / mirror) with top face at
    ``z_base`` bearing the shelf at **0.000 mm** clearance. Rivnuts in the **vertical leg** (1.5 mm
    wall stock); **3×M4** along Y unchanged. Attachment decided **D-065** — no adhesive.
    """
    side_code, index_str = part_id.removeprefix("SHELF-SUPPORT-").split("-")
    index = int(index_str)
    side = "left" if side_code == "L" else "right"
    z_bases = _shelf_divider_z_bases(params, datums)
    if index >= len(z_bases):
        raise ValueError(f"unknown shelf support id: {part_id}")
    z_base = z_bases[index]
    return PartRecord(
        part_id=part_id,
        material=SHELF_SUPPORT_MATERIAL,
        solid=_shelf_support_l_angle_solid(params, datums, side=side, z_base=z_base),
        verify_on_real_machine=True,
    )


def build_shelf_support_parts(
    params: Parameters,
    datums: Datums,
    *,
    shelf_count: int | None = None,
) -> list[PartRecord]:
    """Left/right mechanical shelf-support cleats for every SHELF-* divider (D-059/D-065)."""
    if shelf_count is not None:
        params = with_shelf_count(params, shelf_count)
    parts: list[PartRecord] = []
    for index, _z_base in enumerate(_shelf_divider_z_bases(params, datums)):
        for side_code in ("L", "R"):
            parts.append(
                build_single_shelf_support(
                    f"SHELF-SUPPORT-{side_code}-{index:03d}", params, datums
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
