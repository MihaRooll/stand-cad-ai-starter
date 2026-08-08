"""Named coordinate datums derived from Parameters only."""

from __future__ import annotations

from dataclasses import dataclass

from stand_cad.parameters import Parameters


@dataclass(frozen=True)
class AxisBounds:
    min_mm: float
    max_mm: float

    @property
    def size_mm(self) -> float:
        return self.max_mm - self.min_mm


@dataclass(frozen=True)
class BoxDatum:
    x: AxisBounds
    y: AxisBounds
    z: AxisBounds


@dataclass(frozen=True)
class Datums:
    """Coordinate chain — all values from Parameters."""

    origin: tuple[float, float, float]
    case_envelope: BoxDatum
    plotter1_physical: BoxDatum
    plotter2_physical: BoxDatum
    plotter1_envelope: BoxDatum
    plotter2_envelope: BoxDatum
    organizer_floor_top_z_mm: float
    organizer_clear_volume: BoxDatum
    top_structure: BoxDatum

    @classmethod
    def from_parameters(cls, params: Parameters) -> Datums:
        width = float(params.value("case.width"))
        depth = float(params.value("case.depth"))
        height = float(params.value("case.height"))

        def _bounds(
            triple: tuple[tuple[float, float], tuple[float, float], tuple[float, float]],
        ) -> BoxDatum:
            return BoxDatum(
                x=AxisBounds(*triple[0]),
                y=AxisBounds(*triple[1]),
                z=AxisBounds(*triple[2]),
            )

        org_x = float(params.value("film_storage_horizontal.x"))
        org_y = float(params.value("film_storage_horizontal.y"))
        org_z = float(params.value("film_storage_horizontal.z"))
        clear_w = float(params.value("film_storage_horizontal.clear_width"))
        clear_d = float(params.value("film_storage_horizontal.clear_depth"))
        clear_h = params.horizontal_shelf_stack_height_mm

        top_z_min = float(params.value("top_structure.z_min_mm"))
        top_z_max = float(params.value("top_structure.z_max_mm"))

        return cls(
            origin=(0.0, 0.0, 0.0),
            case_envelope=BoxDatum(
                x=AxisBounds(0.0, width),
                y=AxisBounds(0.0, depth),
                z=AxisBounds(0.0, height),
            ),
            plotter1_physical=_bounds(params.plotter_physical_bounds(1)),
            plotter2_physical=_bounds(params.plotter_physical_bounds(2)),
            plotter1_envelope=_bounds(params.plotter_envelope_bounds(1)),
            plotter2_envelope=_bounds(params.plotter_envelope_bounds(2)),
            organizer_floor_top_z_mm=org_z,
            organizer_clear_volume=BoxDatum(
                x=AxisBounds(org_x, org_x + clear_w),
                y=AxisBounds(org_y, org_y + clear_d),
                z=AxisBounds(org_z, org_z + clear_h),
            ),
            top_structure=BoxDatum(
                x=AxisBounds(0.0, width),
                y=AxisBounds(0.0, depth),
                z=AxisBounds(top_z_min, top_z_max),
            ),
        )
