"""Per-part construction dispatch for DET sheet to_measure tracing."""

from __future__ import annotations

from collections.abc import Callable

from stand_cad.geometry.datums import Datums
from stand_cad.geometry.dividers import build_single_shelf_divider, build_single_shelf_support
from stand_cad.geometry.doors import build_door_level_parts
from stand_cad.geometry.frame import (
    build_single_frame_cladding_part,
    build_single_frame_post,
    build_single_frame_rail,
)
from stand_cad.geometry.organizer import _build_org_floor, _build_org_insert
from stand_cad.geometry.panels import (
    _build_inner_bottom_panel,
    _build_inner_mid_panel,
    _build_inner_rear_panel,
    _build_rear_panel,
    _build_side_slab_with_handle,
)
from stand_cad.geometry.registry import PartRecord
from stand_cad.geometry.services import (
    _build_cover_svc,
    _build_media_support,
)
from stand_cad.geometry.trays import build_single_tray_fabricated_part
from stand_cad.parameters import Parameters

PartTraceFn = Callable[[Parameters, Datums], PartRecord]


def _trace_media_support_l1(params: Parameters, datums: Datums) -> PartRecord:
    return _build_media_support(params, datums, level="L1")


def _trace_media_support_l2(params: Parameters, datums: Datums) -> PartRecord:
    return _build_media_support(params, datums, level="L2")


def _trace_side_left(params: Parameters, datums: Datums) -> PartRecord:
    return _build_side_slab_with_handle(params, datums, side="left")


def _trace_side_right(params: Parameters, datums: Datums) -> PartRecord:
    return _build_side_slab_with_handle(params, datums, side="right")


def _trace_frame_rail(part_id: str) -> PartTraceFn:
    return lambda params, datums, pid=part_id: build_single_frame_rail(pid, params, datums)


def _trace_frame_clad(part_id: str) -> PartTraceFn:
    return lambda params, datums, pid=part_id: build_single_frame_cladding_part(pid, params, datums)


def _trace_door(part_id: str) -> PartTraceFn:
    level = "lower" if "LOWER" in part_id else "upper"

    def _build(params: Parameters, datums: Datums, pid: str = part_id) -> PartRecord:
        for record in build_door_level_parts(params, datums, level=level, state="closed"):
            if record.part_id == pid:
                return record
        raise ValueError(f"door trace could not build {pid!r}")

    return _build


def _trace_tray_part(part_id: str) -> PartTraceFn:
    def _build(params: Parameters, datums: Datums, pid: str = part_id) -> PartRecord:
        return build_single_tray_fabricated_part(pid, params, datums)

    return _build


def _trace_shelf(part_id: str) -> PartTraceFn:
    return lambda params, datums, pid=part_id: build_single_shelf_divider(pid, params, datums)


_PART_TRACE_REGISTRY: dict[str, PartTraceFn] = {
    "COVER-SVC-001": _build_cover_svc,
    "MEDIA-SUPPORT-L1-001": _trace_media_support_l1,
    "MEDIA-SUPPORT-L2-001": _trace_media_support_l2,
    "PANEL-OUT-REAR-001": _build_rear_panel,
    "PANEL-OUT-LEFT-001": _trace_side_left,
    "PANEL-OUT-RIGHT-001": _trace_side_right,
    "PANEL-IN-BOTTOM-001": _build_inner_bottom_panel,
    "PANEL-IN-REAR-001": _build_inner_rear_panel,
    "PANEL-IN-MID-001": _build_inner_mid_panel,
    "ORG-FLOOR-001": _build_org_floor,
    "ORG-INSERT-001": _build_org_insert,
    "DOOR-LOWER-001": _trace_door("DOOR-LOWER-001"),
    "DOOR-UPPER-001": _trace_door("DOOR-UPPER-001"),
}


def _register_frame_rails() -> None:
    for prefix in ("BASE", "TOP", "ORG"):
        for face in ("FRONT", "REAR", "LEFT", "RIGHT"):
            if prefix == "TOP" and face == "FRONT":
                continue
            part_id = f"FRAME-RAIL-{prefix}-{face}-001"
            _PART_TRACE_REGISTRY[part_id] = _trace_frame_rail(part_id)


def _register_frame_cladding() -> None:
    # BASE/ORG/POST cladding removed (D-069) — tray strips only in live assembly.
    for level in ("LOWER", "UPPER"):
        for suffix in ("L", "R", "C"):
            part_id = f"PANEL-CLAD-FRONT-TRAY-{level}-{suffix}-001"
            _PART_TRACE_REGISTRY[part_id] = _trace_frame_clad(part_id)


def _register_tray_parts() -> None:
    for level in ("LOWER", "UPPER"):
        tray_id = f"TRAY-{level}-001"
        _PART_TRACE_REGISTRY[tray_id] = _trace_tray_part(tray_id)
        for suffix in ("L", "R", "C"):
            rail_id = f"FRAME-RAIL-TRAY-{level}-{suffix}-001"
            _PART_TRACE_REGISTRY[rail_id] = _trace_tray_part(rail_id)


def _register_shelves() -> None:
    for index in range(3):
        part_id = f"SHELF-{index:03d}"
        _PART_TRACE_REGISTRY[part_id] = _trace_shelf(part_id)


def _trace_shelf_support(part_id: str) -> PartTraceFn:
    return lambda params, datums, pid=part_id: build_single_shelf_support(pid, params, datums)


def _register_shelf_supports() -> None:
    for index in range(3):
        for side_code in ("L", "R"):
            part_id = f"SHELF-SUPPORT-{side_code}-{index:03d}"
            _PART_TRACE_REGISTRY[part_id] = _trace_shelf_support(part_id)


def _trace_frame_post(part_id: str) -> PartTraceFn:
    return lambda params, datums, pid=part_id: build_single_frame_post(pid, params, datums)


def _register_frame_posts() -> None:
    for suffix in ("FL", "FR", "RL", "RR"):
        part_id = f"FRAME-POST-{suffix}-001"
        _PART_TRACE_REGISTRY[part_id] = _trace_frame_post(part_id)


_register_frame_rails()
_register_frame_posts()
_register_frame_cladding()
_register_tray_parts()
_register_shelves()
_register_shelf_supports()


def part_trace_fn(part_id: str) -> PartTraceFn:
    """Return the single-part trace callable for a fabricated part_id."""
    try:
        return _PART_TRACE_REGISTRY[part_id]
    except KeyError as exc:
        raise KeyError(f"no per-part trace callable registered for {part_id!r}") from exc
