"""Shared build123d helpers — no literal dimensions."""

from __future__ import annotations

from copy import copy

from build123d import Align, Box, Location, Part

from stand_cad.parameters import Parameters


def box_from_bounds(
    x_min: float,
    y_min: float,
    z_min: float,
    x_max: float,
    y_max: float,
    z_max: float,
) -> Part:
    """Axis-aligned box from min/max corner coordinates (mm)."""
    return Box(
        x_max - x_min,
        y_max - y_min,
        z_max - z_min,
        align=(Align.MIN, Align.MIN, Align.MIN),
    ).move(Location((x_min, y_min, z_min)))


def translate_solid(solid: Part, *, dx: float = 0.0, dy: float = 0.0, dz: float = 0.0) -> Part:
    """Return a copy of solid translated along axes (mm)."""
    return copy(solid).move(Location((dx, dy, dz)))


def numeric_or_provisional(params: Parameters, path: str, provisional: float) -> float:
    """Return a numeric leaf value or a documented provisional for to_measure leaves."""
    value = params.value(path)
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return float(value)
    return provisional


def intersection_volume(a: Part, b: Part) -> float:
    """Boolean intersection volume; zero when solids are disjoint.

    Boolean failures propagate — a crashed op must not masquerade as zero overlap.
    """
    result = a & b
    if result is None:
        return 0.0
    vol = getattr(result, "volume", 0.0)
    return float(vol) if vol and vol > 0 else 0.0


def minimum_clearance(a: Part, b: Part) -> float:
    """Minimum distance between two solids (mm); zero when intersecting."""
    if intersection_volume(a, b) > 1e-3:
        return 0.0
    from OCP.BRepExtrema import BRepExtrema_DistShapeShape

    dist = BRepExtrema_DistShapeShape(a.wrapped, b.wrapped)
    dist.Perform()
    if dist.IsDone():
        return float(dist.Value())
    return float("inf")


def bounding_box_size(solid: Part) -> tuple[float, float, float]:
    """Return (size_x, size_y, size_z) from a solid bounding box."""
    bbox = solid.bounding_box()
    mn = bbox.min
    mx = bbox.max
    return (mx.X - mn.X, mx.Y - mn.Y, mx.Z - mn.Z)


def bounding_box_bounds(
    solid: Part,
) -> tuple[tuple[float, float], tuple[float, float], tuple[float, float]]:
    """Return ((x_min, x_max), (y_min, y_max), (z_min, z_max))."""
    bbox = solid.bounding_box()
    mn = bbox.min
    mx = bbox.max
    return ((mn.X, mx.X), (mn.Y, mx.Y), (mn.Z, mx.Z))


def solid_point_state(solid: Part, x: float, y: float, z: float) -> str:
    """Return IN, OUT, or ON for a point against a solid (mm)."""
    from OCP.BRepClass3d import BRepClass3d_SolidClassifier
    from OCP.gp import gp_Pnt
    from OCP.TopAbs import TopAbs_IN, TopAbs_ON, TopAbs_OUT

    classifier = BRepClass3d_SolidClassifier(solid.wrapped)
    classifier.Perform(gp_Pnt(x, y, z), 1e-6)
    state = classifier.State()
    if state == TopAbs_IN:
        return "IN"
    if state == TopAbs_ON:
        return "ON"
    if state == TopAbs_OUT:
        return "OUT"
    return "UNKNOWN"
