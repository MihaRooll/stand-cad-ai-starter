"""Tray kinematics, interlock mechanism, and rigid-group transforms."""

from __future__ import annotations

from enum import StrEnum

from build123d import Part

from stand_cad.geometry.datums import Datums
from stand_cad.geometry.primitives import box_from_bounds, translate_solid
from stand_cad.geometry.registry import PartRecord
from stand_cad.parameters import Parameters

INTERLOCK_SHUTTLE_MATERIAL = "interlock_shuttle_hardware"
INTERLOCK_TAB_MATERIAL = "interlock_tab_hardware"


class ShuttlePosition(StrEnum):
    NEUTRAL = "neutral"
    BLOCKS_UPPER = "blocks_upper"
    BLOCKS_LOWER = "blocks_lower"


LOWER_KINEMATIC_GROUP = frozenset(
    {
        "TRAY-LOWER-001",
        "SLIDE-LOWER-LEFT-001",
        "SLIDE-LOWER-RIGHT-001",
        "SLIDE-LOWER-CENTER-001",
        "SOFTSTOP-LOWER-001",
        "VIBMOUNT-P1-001",
        "VIBMOUNT-P1-002",
        "VIBMOUNT-P1-003",
        "VIBMOUNT-P1-004",
        "EQUIP-PLOTTER1-001",
        "ENV-PLOTTER1-001",
        "LID-ENVELOPE-P1-001",
        "INTERLOCK-TAB-LOWER-001",
    }
)

UPPER_KINEMATIC_GROUP = frozenset(
    {
        "TRAY-UPPER-001",
        "SLIDE-UPPER-LEFT-001",
        "SLIDE-UPPER-RIGHT-001",
        "SLIDE-UPPER-CENTER-001",
        "SOFTSTOP-UPPER-001",
        "VIBMOUNT-P2-001",
        "VIBMOUNT-P2-002",
        "VIBMOUNT-P2-003",
        "VIBMOUNT-P2-004",
        "EQUIP-PLOTTER2-001",
        "ENV-PLOTTER2-001",
        "LID-ENVELOPE-P2-001",
        "INTERLOCK-TAB-UPPER-001",
    }
)


def _slide_zone_z(params: Parameters, plotter_z: float) -> float:
    """Z centre of slide mounting zone for a plotter level."""
    slide_h = float(params.value("trays.slide_rail_height_mm"))
    return plotter_z - params.tray_panel_thickness_mm - slide_h / 2


def _shuttle_neutral_z(params: Parameters) -> float:
    lower_z = _slide_zone_z(params, float(params.value("plotter.lower_z")))
    upper_z = _slide_zone_z(params, float(params.value("plotter.upper_z")))
    return (lower_z + upper_z) / 2


def _shuttle_z_for_position(params: Parameters, position: ShuttlePosition) -> float:
    if position == ShuttlePosition.NEUTRAL:
        return _shuttle_neutral_z(params)
    if position == ShuttlePosition.BLOCKS_UPPER:
        return _slide_zone_z(params, float(params.value("plotter.upper_z")))
    if position == ShuttlePosition.BLOCKS_LOWER:
        return _slide_zone_z(params, float(params.value("plotter.lower_z")))
    raise ValueError(f"unknown shuttle position: {position}")


def _shuttle_y_span(
    params: Parameters,
    datums: Datums,
    *,
    position: ShuttlePosition,
) -> tuple[float, float]:
    """Y extent for shuttle — spans the slide path it must block in service states."""
    channel_w = params.interlock_shuttle_channel_width_mm
    if position == ShuttlePosition.NEUTRAL:
        y_center = (
            datums.plotter1_physical.y.max_mm + datums.plotter2_physical.y.min_mm
        ) / 2
        half = channel_w / 2
        return y_center - half, y_center + half
    if position == ShuttlePosition.BLOCKS_UPPER:
        lower_ext = float(params.value("trays.lower_extension"))
        upper_ext = float(params.value("trays.upper_extension"))
        tab_front_y = datums.plotter1_physical.y.max_mm - lower_ext
        upper_slide_front_y = datums.plotter2_physical.y.min_mm - upper_ext
        return upper_slide_front_y, tab_front_y + params.interlock_tab_engagement_mm
    upper_ext = float(params.value("trays.upper_extension"))
    lower_ext = float(params.value("trays.lower_extension"))
    tab_front_y = datums.plotter2_physical.y.min_mm - upper_ext
    lower_slide_front_y = datums.plotter1_physical.y.max_mm - lower_ext
    return tab_front_y - params.interlock_tab_engagement_mm, lower_slide_front_y


def _interlock_shuttle_bounds(
    params: Parameters,
    datums: Datums,
    *,
    position: ShuttlePosition,
) -> tuple[float, float, float, float, float, float]:
    rail_w = float(params.value("trays.slide_rail_width_mm"))
    rail_h = float(params.value("trays.slide_rail_height_mm"))
    shuttle_h = rail_h * 2
    shuttle_z = _shuttle_z_for_position(params, position)
    plotter_x1 = datums.plotter1_physical.x.max_mm
    x0 = plotter_x1 - rail_w
    x1 = plotter_x1
    y0, y1 = _shuttle_y_span(params, datums, position=position)
    return (
        x0,
        y0,
        shuttle_z - shuttle_h / 2,
        x1,
        y1,
        shuttle_z + shuttle_h / 2,
    )


def build_interlock_parts(
    params: Parameters,
    datums: Datums,
    *,
    shuttle_position: ShuttlePosition,
) -> list[PartRecord]:
    """Captive shuttle and tray-mounted tabs at a discrete interlock state."""
    tab_depth = params.interlock_tab_engagement_mm
    tab_h = float(params.value("trays.slide_rail_height_mm"))
    plotter_x1 = datums.plotter1_physical.x.max_mm

    shuttle_bounds = _interlock_shuttle_bounds(
        params, datums, position=shuttle_position
    )
    shuttle = PartRecord(
        part_id="INTERLOCK-SHUTTLE-001",
        material=INTERLOCK_SHUTTLE_MATERIAL,
        solid=box_from_bounds(*shuttle_bounds),
        verify_on_real_machine=True,
    )

    lower_tray_y = datums.plotter1_physical.y.max_mm
    lower_tab = PartRecord(
        part_id="INTERLOCK-TAB-LOWER-001",
        material=INTERLOCK_TAB_MATERIAL,
        solid=box_from_bounds(
            plotter_x1 - tab_depth,
            lower_tray_y - tab_depth,
            _slide_zone_z(params, float(params.value("plotter.lower_z"))) - tab_h / 2,
            plotter_x1,
            lower_tray_y,
            _slide_zone_z(params, float(params.value("plotter.lower_z"))) + tab_h / 2,
        ),
        verify_on_real_machine=True,
    )

    upper_tray_y = datums.plotter2_physical.y.min_mm
    upper_tab = PartRecord(
        part_id="INTERLOCK-TAB-UPPER-001",
        material=INTERLOCK_TAB_MATERIAL,
        solid=box_from_bounds(
            plotter_x1 - tab_depth,
            upper_tray_y,
            _slide_zone_z(params, float(params.value("plotter.upper_z"))) - tab_h / 2,
            plotter_x1,
            upper_tray_y + tab_depth,
            _slide_zone_z(params, float(params.value("plotter.upper_z"))) + tab_h / 2,
        ),
        verify_on_real_machine=True,
    )
    return [shuttle, lower_tab, upper_tab]


def apply_tray_extension(
    parts: dict[str, PartRecord],
    *,
    lower_extension_mm: float,
    upper_extension_mm: float,
) -> dict[str, PartRecord]:
    """Return parts dict with kinematic groups translated by -extension along Y."""
    result = dict(parts)
    if lower_extension_mm:
        dy = -lower_extension_mm
        for part_id in LOWER_KINEMATIC_GROUP:
            if part_id in result:
                record = result[part_id]
                result[part_id] = PartRecord(
                    part_id=record.part_id,
                    material=record.material,
                    solid=translate_solid(record.solid, dy=dy),
                    verify_on_real_machine=record.verify_on_real_machine,
                )
    if upper_extension_mm:
        dy = -upper_extension_mm
        for part_id in UPPER_KINEMATIC_GROUP:
            if part_id in result:
                record = result[part_id]
                result[part_id] = PartRecord(
                    part_id=record.part_id,
                    material=record.material,
                    solid=translate_solid(record.solid, dy=dy),
                    verify_on_real_machine=record.verify_on_real_machine,
                )
    return result


def build_test_body_parts(params: Parameters, datums: Datums) -> list[PartRecord]:
    """Representative media-path test volumes at one Y position per level."""
    clear_w = float(params.value("media_path.clear_width"))
    parts: list[PartRecord] = []

    for suffix, plotter_z, y_pos in (
        ("PRIMARY-L1", float(params.value("plotter.lower_z")), datums.plotter1_physical.y.min_mm),
        ("PRIMARY-L2", float(params.value("plotter.upper_z")), datums.plotter2_physical.y.min_mm),
    ):
        h = float(params.value("media_path.test_body_primary.height"))
        d = float(params.value("media_path.test_body_primary.depth"))
        t = float(params.value("media_path.test_body_primary.thickness"))
        cx = datums.case_envelope.x.max_mm / 2
        parts.append(
            PartRecord(
                part_id=f"TESTBODY-{suffix}-001",
                material="media_path_test_body",
                solid=box_from_bounds(
                    cx - clear_w / 2,
                    y_pos,
                    plotter_z + float(params.value("plotter.physical_height")) / 2,
                    cx + clear_w / 2,
                    y_pos + d,
                    plotter_z + float(params.value("plotter.physical_height")) / 2 + t,
                ),
            )
        )

    for suffix, plotter_z, y_pos in (
        ("LONG-L1", float(params.value("plotter.lower_z")), datums.plotter1_physical.y.min_mm),
        ("LONG-L2", float(params.value("plotter.upper_z")), datums.plotter2_physical.y.min_mm),
    ):
        h = float(params.value("media_path.test_body_long.height"))
        d = float(params.value("media_path.test_body_long.depth"))
        t = float(params.value("media_path.test_body_long.thickness"))
        cx = datums.case_envelope.x.max_mm / 2
        parts.append(
            PartRecord(
                part_id=f"TESTBODY-{suffix}-001",
                material="media_path_test_body",
                solid=box_from_bounds(
                    cx - clear_w / 2,
                    y_pos,
                    plotter_z + float(params.value("plotter.physical_height")) / 2,
                    cx + clear_w / 2,
                    y_pos + d,
                    plotter_z + float(params.value("plotter.physical_height")) / 2 + h,
                ),
            )
        )
    return parts


def tray_fully_extended_solid(params: Parameters, datums: Datums, level: str):
    """Tray solid at full extension — for swept-path interference checks."""
    from stand_cad.geometry.trays import build_tray_level_parts

    extension = float(
        params.value("trays.lower_extension" if level == "lower" else "trays.upper_extension")
    )
    closed = build_tray_level_parts(params, datums, level=level)[0].solid
    return translate_solid(closed, dy=-extension)


def slides_fully_extended_solids(
    params: Parameters, datums: Datums, level: str
) -> list[Part]:
    """Slide rail solids at full extension — interlock blocking checks the rail path."""
    from stand_cad.geometry.trays import build_tray_level_parts

    extension = float(
        params.value("trays.lower_extension" if level == "lower" else "trays.upper_extension")
    )
    level_parts = build_tray_level_parts(params, datums, level=level)
    slides = [record for record in level_parts if record.part_id.startswith("SLIDE-")]
    return [translate_solid(record.solid, dy=-extension) for record in slides]
