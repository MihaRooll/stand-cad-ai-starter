"""Assembly composition for TZ section 13 states."""

from __future__ import annotations

from dataclasses import dataclass, field

from build123d import Compound

from stand_cad.geometry.datums import Datums
from stand_cad.geometry.dividers import build_divider_parts
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


def _build_static_parts(
    params: Parameters,
    datums: Datums,
    *,
    cells: int | None = None,
) -> dict[str, PartRecord]:
    """Frame, panels, organizer, dividers, services, hardware, equipment, trays (closed)."""
    return _merge_parts(
        build_frame_parts(params, datums),
        build_panel_parts(params, datums),
        build_organizer_parts(params, datums),
        build_divider_parts(params, datums, cells=cells),
        build_service_parts(params, datums),
        build_hardware_parts(params, datums),
        build_equipment_parts(params, datums),
        build_tray_parts(params, datums),
    )


def _build_state(
    params: Parameters,
    name: str,
    *,
    cells: int | None = None,
    lower_extension_mm: float = 0.0,
    upper_extension_mm: float = 0.0,
    shuttle_position: ShuttlePosition = ShuttlePosition.NEUTRAL,
    include_test_bodies: bool = False,
    include_lid_envelopes: bool = False,
) -> AssemblyState:
    datums = Datums.from_parameters(params)
    parts = _build_static_parts(params, datums, cells=cells)
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
    if include_test_bodies:
        for record in build_test_body_parts(params, datums):
            parts[record.part_id] = record
    return AssemblyState(name=name, parts=parts)


# REFERENCE_ONLY visualization placeholder — not verified film colour or material.
FILM_BODY_MATERIAL = "film_sheet_reference"
_HIDDEN_OUTER_SHELL_PREFIXES = ("PANEL-OUT-",)


def _suppress_outer_shell(parts: dict[str, PartRecord]) -> dict[str, PartRecord]:
    """Drop opaque outer shell panels so internal organizer content is visible."""
    return {
        part_id: record
        for part_id, record in parts.items()
        if not part_id.startswith(_HIDDEN_OUTER_SHELL_PREFIXES)
    }


def build_film_body_parts(
    params: Parameters,
    datums: Datums,
    *,
    cell_indices: tuple[int, ...] | None = None,
) -> list[PartRecord]:
    """Representative vertical film envelopes (320 x 500 mm) for validation renders."""
    cells = int(params.value("film_storage.cells"))
    if cell_indices is None:
        cell_indices = tuple(range(cells))
    org_x = float(params.value("film_storage.x"))
    rail_front = float(params.value("film_storage.comb_rail_front_depth_mm"))
    org_y = float(params.value("film_storage.y")) + rail_front
    cell_w = params.cell_width_mm
    divider_t = float(params.value("film_storage.divider_thickness"))
    film_h = float(params.value("film_storage.film_design_height"))
    film_d = float(params.value("film_storage.film_depth"))
    z0 = datums.organizer_floor_top_z_mm + params.org_insert_thickness_mm
    parts: list[PartRecord] = []
    for index in cell_indices:
        x0 = org_x + index * (cell_w + divider_t)
        part_id = f"FILM-BODY-{index:03d}"
        parts.append(
            PartRecord(
                part_id=part_id,
                material=FILM_BODY_MATERIAL,
                solid=box_from_bounds(
                    x0,
                    org_y,
                    z0,
                    x0 + cell_w,
                    org_y + film_d,
                    z0 + film_h,
                ),
            )
        )
    return parts


def build_organizer_loaded_assembly(
    params: Parameters, *, cells: int | None = None
) -> AssemblyState:
    """Transport state with representative film bodies in several organizer cells."""
    state = build_transport_assembly(params, cells=cells)
    datums = Datums.from_parameters(params)
    for record in build_film_body_parts(params, datums):
        state.parts[record.part_id] = record
    state.parts = _suppress_outer_shell(state.parts)
    state.name = "organizer_loaded"
    return state


def build_panels_hidden_assembly(
    params: Parameters, *, cells: int | None = None
) -> AssemblyState:
    """Transport state with outer shell panels suppressed for internal-structure review."""
    state = build_transport_assembly(params, cells=cells)
    state.parts = _suppress_outer_shell(state.parts)
    state.name = "panels_hidden"
    return state


def build_transport_shell_top_view_assembly(
    params: Parameters, *, cells: int | None = None
) -> AssemblyState:
    """Transport state for orthographic top evidence (no lid — open organizer top)."""
    state = build_transport_assembly(params, cells=cells)
    state.name = "transport_shell_top_view"
    return state


def build_transport_assembly(params: Parameters, *, cells: int | None = None) -> AssemblyState:
    """Transport state — both trays closed, shuttle neutral."""
    return _build_state(params, "transport", cells=cells, shuttle_position=ShuttlePosition.NEUTRAL)


def build_service_plotter_1_assembly(
    params: Parameters, *, cells: int | None = None
) -> AssemblyState:
    """Service plotter 1 — lower tray extended, upper closed, shuttle blocks upper."""
    return _build_state(
        params,
        "service_plotter_1",
        cells=cells,
        lower_extension_mm=float(params.value("trays.lower_extension")),
        shuttle_position=ShuttlePosition.BLOCKS_UPPER,
        include_lid_envelopes=True,
    )


def build_service_plotter_2_assembly(
    params: Parameters, *, cells: int | None = None
) -> AssemblyState:
    """Service plotter 2 — upper tray extended, lower closed, shuttle blocks lower."""
    return _build_state(
        params,
        "service_plotter_2",
        cells=cells,
        upper_extension_mm=float(params.value("trays.upper_extension")),
        shuttle_position=ShuttlePosition.BLOCKS_LOWER,
        include_lid_envelopes=True,
    )


def build_operating_with_test_bodies_assembly(
    params: Parameters, *, cells: int | None = None
) -> AssemblyState:
    """Operating state — both trays closed with representative media-path test bodies."""
    return _build_state(
        params,
        "operating_with_test_bodies",
        cells=cells,
        shuttle_position=ShuttlePosition.NEUTRAL,
        include_test_bodies=True,
    )
