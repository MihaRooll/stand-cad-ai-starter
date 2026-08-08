"""Assembly composition for TZ section 13 states."""

from __future__ import annotations

from copy import copy
from dataclasses import dataclass, field
from pathlib import Path

from build123d import Compound

from stand_cad.geometry.datums import Datums
from stand_cad.geometry.dividers import build_divider_parts, build_shelf_support_parts
from stand_cad.geometry.doors import DoorState, build_door_parts
from stand_cad.geometry.equipment import build_equipment_parts
from stand_cad.geometry.frame import build_frame_parts
from stand_cad.geometry.hardware import build_hardware_parts
from stand_cad.geometry.kinematics import (
    ShuttlePosition,
    apply_tray_extension,
    build_interlock_parts,
    build_test_body_parts,
)
from stand_cad.geometry.organizer import build_organizer_parts
from stand_cad.geometry.panels import build_panel_parts
from stand_cad.geometry.primitives import box_from_bounds
from stand_cad.geometry.registry import PartRecord
from stand_cad.geometry.services import build_service_parts
from stand_cad.geometry.trays import build_lid_envelope_parts, build_tray_parts
from stand_cad.parameters import Parameters

_PARAMETERS_PATH = Path(__file__).resolve().parents[3] / "config" / "parameters.yaml"
_STATIC_PARTS_CACHE: dict[tuple, dict[str, PartRecord]] = {}
_STATE_CACHE: dict[tuple, AssemblyState] = {}


def _parameters_mtime() -> float:
    return _PARAMETERS_PATH.stat().st_mtime


def clear_assembly_cache() -> None:
    """Drop cached static parts and built states (tests that mutate parameters)."""
    _STATIC_PARTS_CACHE.clear()
    _STATE_CACHE.clear()


@dataclass
class AssemblyState:
    """One modeled configuration state with indexed parts."""

    name: str
    parts: dict[str, PartRecord] = field(default_factory=dict)

    def compound(self) -> Compound:
        return Compound(children=[record.solid for record in self.parts.values()])


def _merge_parts(*part_lists: list[PartRecord]) -> dict[str, PartRecord]:
    parts: dict[str, PartRecord] = {}
    for part_list in part_lists:
        for record in part_list:
            parts[record.part_id] = record
    return parts


def _copy_parts(parts: dict[str, PartRecord]) -> dict[str, PartRecord]:
    """Return shallow PartRecord copies with independent OCCT solids."""
    return {
        part_id: PartRecord(
            part_id=record.part_id,
            material=record.material,
            solid=copy(record.solid),
            verify_on_real_machine=record.verify_on_real_machine,
        )
        for part_id, record in parts.items()
    }


def _build_static_parts(
    params: Parameters,
    datums: Datums,
    *,
    shelf_count: int | None = None,
) -> dict[str, PartRecord]:
    """Frame, panels, organizer, dividers, services, hardware, equipment, trays (closed)."""
    cache_key = ("static", _parameters_mtime(), shelf_count)
    if cache_key not in _STATIC_PARTS_CACHE:
        _STATIC_PARTS_CACHE[cache_key] = _merge_parts(
            build_frame_parts(params, datums),
            build_panel_parts(params, datums),
            build_organizer_parts(params, datums),
            build_divider_parts(params, datums, shelf_count=shelf_count),
            build_shelf_support_parts(params, datums, shelf_count=shelf_count),
            build_service_parts(params, datums),
            build_hardware_parts(params, datums),
            build_equipment_parts(params, datums),
            build_tray_parts(params, datums),
        )
    return _copy_parts(_STATIC_PARTS_CACHE[cache_key])


def _build_state(
    params: Parameters,
    name: str,
    *,
    shelf_count: int | None = None,
    lower_extension_mm: float = 0.0,
    upper_extension_mm: float = 0.0,
    shuttle_position: ShuttlePosition = ShuttlePosition.NEUTRAL,
    include_test_bodies: bool = False,
    include_lid_envelopes: bool = False,
    door_state: dict[str, DoorState] | None = None,
) -> AssemblyState:
    door_lower = (door_state or {}).get("lower", "closed")
    door_upper = (door_state or {}).get("upper", "closed")
    cache_key = (
        name,
        _parameters_mtime(),
        shelf_count,
        lower_extension_mm,
        upper_extension_mm,
        shuttle_position.value,
        include_test_bodies,
        include_lid_envelopes,
        door_lower,
        door_upper,
    )
    cached = _STATE_CACHE.get(cache_key)
    if cached is not None:
        return AssemblyState(name=cached.name, parts=_copy_parts(cached.parts))

    datums = Datums.from_parameters(params)
    parts = _build_static_parts(params, datums, shelf_count=shelf_count)
    if include_lid_envelopes:
        for record in build_lid_envelope_parts(params, datums):
            parts[record.part_id] = record
    parts.update(
        {
            r.part_id: r
            for r in build_interlock_parts(
                params, datums, shuttle_position=shuttle_position
            )
        }
    )
    parts = apply_tray_extension(
        parts,
        lower_extension_mm=lower_extension_mm,
        upper_extension_mm=upper_extension_mm,
    )
    for record in build_door_parts(
        params, datums, door_state=door_state, include_struts=True
    ):
        parts[record.part_id] = record
    if include_test_bodies:
        for record in build_test_body_parts(params, datums):
            parts[record.part_id] = record
    state = AssemblyState(name=name, parts=parts)
    _STATE_CACHE[cache_key] = state
    return AssemblyState(name=state.name, parts=_copy_parts(state.parts))


# REFERENCE_ONLY visualization placeholder — not verified film colour or material.
FILM_BODY_MATERIAL = "film_sheet_reference"
_HIDDEN_OUTER_SHELL_PREFIXES = ("PANEL-OUT-",)
# Owner 2026-08-06 — "just the box, nothing extra" review mode: keep outer shell, inner
# structural panels (compartment dividers), frame, feet, and stacking caps only. Drop every
# tray/slide/hardware/shelf/equipment part — those are content/mechanism, not "the case".
_CASE_ONLY_KEEP_PREFIXES = (
    "PANEL-OUT-",
    "PANEL-IN-",
    "FRAME-",
    "PANEL-CLAD-FRONT-",
    "DOOR-",
    "FOOT-",
    "STACK-CAP-",
)


def _suppress_outer_shell(parts: dict[str, PartRecord]) -> dict[str, PartRecord]:
    """Drop opaque outer shell panels so internal organizer content is visible."""
    return {
        part_id: record
        for part_id, record in parts.items()
        if not part_id.startswith(_HIDDEN_OUTER_SHELL_PREFIXES)
    }


def _keep_case_only(parts: dict[str, PartRecord]) -> dict[str, PartRecord]:
    """Keep only outer/inner shell, frame, feet, and stacking caps — drop all else."""
    return {
        part_id: record
        for part_id, record in parts.items()
        if part_id.startswith(_CASE_ONLY_KEEP_PREFIXES)
    }


_HIDDEN_EQUIPMENT_PLACEHOLDER_PREFIXES = ("EQUIP-PLOTTER", "ENV-PLOTTER")


def _suppress_equipment_placeholders(parts: dict[str, PartRecord]) -> dict[str, PartRecord]:
    """Drop plotter placeholder boxes for display only (owner 2026-08-06 — annoying clutter).

    Mass/CoM/stability analysis reads plotter mass from ``params.plotter_mass_kg()`` and only
    uses these boxes' *position* by part_id lookup, so this filter must stay display-only:
    never applied inside ``build_transport_assembly`` itself, only in the display wrapper below,
    so ``generate_mass_report.py`` (which imports ``build_transport_assembly`` directly) keeps
    counting real plotter mass and CoM contribution.
    """
    return {
        part_id: record
        for part_id, record in parts.items()
        if not part_id.startswith(_HIDDEN_EQUIPMENT_PLACEHOLDER_PREFIXES)
    }


def build_transport_display_assembly(
    params: Parameters, *, shelf_count: int | None = None
) -> AssemblyState:
    """Default display state for viewer/PNG/STEP export — plotter placeholder boxes hidden.

    They're behind a closed door in the real design now (owner 2026-08-06 drop-front door
    concept) so showing a bare red box by default read as clutter. Use ``build_transport_assembly``
    directly for mass/CoM/stability analysis, which is unaffected by this display filter.
    """
    state = build_transport_assembly(params, shelf_count=shelf_count)
    state.parts = _suppress_equipment_placeholders(state.parts)
    state.name = "transport_display"
    return state


def build_case_only_assembly(
    params: Parameters, *, shelf_count: int | None = None
) -> AssemblyState:
    """Empty-cabinet display mode — case shell/frame/feet only, no trays/shelves/equipment/hardware.

    Display-only filter (owner 2026-08-06, second review mode alongside the full assembly with
    equipment); never applied to ``build_transport_assembly`` itself so mass/CoM/stability
    analysis scripts keep the real, fully-populated assembly.
    """
    state = build_transport_assembly(params, shelf_count=shelf_count)
    state.parts = _keep_case_only(state.parts)
    state.name = "case_only"
    return state


def build_film_body_parts(
    params: Parameters,
    datums: Datums,
    *,
    shelf_indices: tuple[int, ...] | None = None,
) -> list[PartRecord]:
    """Representative flat film sheets (330 x 500 mm, 3 mm reference thickness) per shelf."""
    shelf_count = int(params.value("film_storage_horizontal.shelf_count"))
    if shelf_indices is None:
        shelf_indices = tuple(range(shelf_count))
    org_x = float(params.value("film_storage_horizontal.x"))
    org_y = float(params.value("film_storage_horizontal.y"))
    sheet_span_x = float(params.value("film_storage_horizontal.sheet_depth_mm"))
    sheet_span_y = float(params.value("film_storage_horizontal.sheet_width_mm"))
    film_t = float(params.value("media_path.test_body_primary.thickness"))
    clear_h = float(params.value("film_storage_horizontal.compartment_clear_height_mm"))
    divider_t = float(params.value("film_storage_horizontal.divider_thickness"))
    z_base = datums.organizer_floor_top_z_mm + params.org_insert_thickness_mm
    parts: list[PartRecord] = []
    for index in shelf_indices:
        z0 = z_base + index * (clear_h + divider_t)
        z1 = z0 + film_t
        part_id = f"FILM-BODY-{index:03d}"
        parts.append(
            PartRecord(
                part_id=part_id,
                material=FILM_BODY_MATERIAL,
                solid=box_from_bounds(
                    org_x,
                    org_y,
                    z0,
                    org_x + sheet_span_x,
                    org_y + sheet_span_y,
                    z1,
                ),
            )
        )
    return parts


def build_organizer_loaded_assembly(
    params: Parameters, *, shelf_count: int | None = None
) -> AssemblyState:
    """Transport state with representative flat film bodies in each shelf compartment."""
    state = build_transport_assembly(params, shelf_count=shelf_count)
    datums = Datums.from_parameters(params)
    for record in build_film_body_parts(params, datums):
        state.parts[record.part_id] = record
    state.parts = _suppress_outer_shell(state.parts)
    state.name = "organizer_loaded"
    return state


def build_panels_hidden_assembly(
    params: Parameters, *, shelf_count: int | None = None
) -> AssemblyState:
    """Transport state with outer shell panels suppressed for internal-structure review."""
    state = build_transport_assembly(params, shelf_count=shelf_count)
    state.parts = _suppress_outer_shell(state.parts)
    state.name = "panels_hidden"
    return state


def build_transport_shell_top_view_assembly(
    params: Parameters, *, shelf_count: int | None = None
) -> AssemblyState:
    """Transport state for orthographic top evidence (no lid — open organizer top)."""
    state = build_transport_assembly(params, shelf_count=shelf_count)
    state.name = "transport_shell_top_view"
    return state


def build_transport_assembly(
    params: Parameters, *, shelf_count: int | None = None
) -> AssemblyState:
    """Transport state — both trays closed, shuttle neutral."""
    return _build_state(
        params,
        "transport",
        shelf_count=shelf_count,
        shuttle_position=ShuttlePosition.NEUTRAL,
    )


def build_service_plotter_1_assembly(
    params: Parameters, *, shelf_count: int | None = None
) -> AssemblyState:
    """Service plotter 1 — lower tray extended, upper closed, shuttle blocks upper."""
    return _build_state(
        params,
        "service_plotter_1",
        shelf_count=shelf_count,
        lower_extension_mm=float(params.value("trays.lower_extension")),
        shuttle_position=ShuttlePosition.BLOCKS_UPPER,
        include_lid_envelopes=True,
        door_state={"lower": "open", "upper": "closed"},
    )


def build_service_plotter_2_assembly(
    params: Parameters, *, shelf_count: int | None = None
) -> AssemblyState:
    """Service plotter 2 — upper door open, upper tray fixed (D-076 upper_extension=0)."""
    return _build_state(
        params,
        "service_plotter_2",
        shelf_count=shelf_count,
        upper_extension_mm=0.0,
        shuttle_position=ShuttlePosition.BLOCKS_LOWER,
        include_lid_envelopes=True,
        door_state={"lower": "closed", "upper": "open"},
    )


def build_tray1_quick_access_assembly(
    params: Parameters, *, shelf_count: int | None = None
) -> AssemblyState:
    """Tier 1 tray quick-access — documented minimum 130 mm forward slide (D-033).

    Distinct from build_service_plotter_1_assembly (250 mm full-service extension):
    this is a lesser, quick-access position and does not engage the tray-extension
    interlock (shuttle stays neutral) — tier 2 stays closed.
    """
    return _build_state(
        params,
        "tray1_quick_access",
        shelf_count=shelf_count,
        lower_extension_mm=float(params.value("trays.lower_quick_access_extension_mm")),
        shuttle_position=ShuttlePosition.NEUTRAL,
        door_state={"lower": "open", "upper": "closed"},
    )


def build_operating_with_test_bodies_assembly(
    params: Parameters, *, shelf_count: int | None = None
) -> AssemblyState:
    """Operating state — both trays closed with representative media-path test bodies."""
    return _build_state(
        params,
        "operating_with_test_bodies",
        shelf_count=shelf_count,
        shuttle_position=ShuttlePosition.NEUTRAL,
        include_test_bodies=True,
    )
