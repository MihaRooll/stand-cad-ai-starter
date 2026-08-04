"""Regenerate PLT-003 rev1 validation PNG views from live assembly builders.

Uses OCP tessellation and an in-process orthographic z-buffer rasterizer (numpy) so the
evidence pack is reproducible from the repository without MCP or matplotlib.

Also exports SVG orthographic line drawings (HLR), STL, and GLB for the transport assembly.
"""

from __future__ import annotations

import struct
import zlib
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from build123d import (
    Edge,
    ExportSVG,
    HLRAlgo_Projector,
    HLRBRep_Algo,
    HLRBRep_HLRToShape,
)
from OCP.BRep import BRep_Tool
from OCP.BRepMesh import BRepMesh_IncrementalMesh
from OCP.gp import gp_Ax2, gp_Dir, gp_Pnt
from OCP.TopAbs import TopAbs_EDGE, TopAbs_FACE
from OCP.TopExp import TopExp_Explorer
from OCP.TopLoc import TopLoc_Location
from OCP.TopoDS import TopoDS

from stand_cad.geometry.assembly import (
    AssemblyState,
    build_organizer_loaded_assembly,
    build_panels_hidden_assembly,
    build_service_plotter_1_assembly,
    build_service_plotter_2_assembly,
    build_transport_assembly,
)
from stand_cad.geometry.export import CONCEPT_REVISION, export_transport_mesh_bundle
from stand_cad.geometry.registry import PartRecord
from stand_cad.parameters import Parameters, load_parameters

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PARAMETERS = REPO_ROOT / "config" / "parameters.yaml"
DEFAULT_OUTPUT_DIR = REPO_ROOT / "output" / "validation" / f"rev{CONCEPT_REVISION}" / "views"
DEFAULT_CONCEPT_DIR = REPO_ROOT / "output" / "concept"
CONCEPT_STEM = f"light_plotter_tower_ASSEMBLY_CONCEPT_REFERENCE_ONLY_rev{CONCEPT_REVISION}"

MATERIAL_RGB: dict[str, tuple[int, int, int]] = {
    "cast_opal_pmma_3mm": (245, 245, 250),
    "white_composite_3_4mm": (252, 252, 252),
    "aluminium_angle_15x15x1.5": (175, 178, 188),
    "sandwich_panel_10_12mm": (205, 205, 215),
    "transparent_petg_2mm": (120, 185, 235),
    "hdpe_insert_thin": (210, 210, 200),
    "silicone_foot": (70, 70, 75),
    "integrated_side_handle": (240, 240, 240),
    "full_extension_slide_hardware": (160, 165, 175),
    "elastomer_soft_stop": (90, 90, 95),
    "elastomer_vibration_mount": (90, 90, 95),
    "interlock_shuttle_hardware": (160, 165, 175),
    "interlock_tab_hardware": (160, 165, 175),
    "soft_trim_brush": (100, 100, 105),
    "hardware_mains_inlet": (150, 155, 165),
    "equipment_reference": (220, 90, 90),
    "reference_envelope": (80, 160, 240),
    "film_sheet_reference": (140, 175, 210),
    "service_volume": (240, 190, 110),
}

# REFERENCE_ONLY palette cycling for FILM-BODY-* stacks (not verified film colours).
FILM_BODY_PALETTE: tuple[tuple[int, int, int], ...] = (
    (120, 170, 220),
    (100, 150, 200),
    (140, 185, 225),
    (90, 140, 195),
    (130, 175, 215),
    (110, 160, 205),
    (150, 190, 230),
    (95, 145, 190),
    (125, 180, 220),
    (105, 155, 200),
)

DEFAULT_RGB = (190, 190, 195)

# Contrast backgrounds for legibility (Finding 1 / Finding 5 — near-white panel on white PNG).
BASE_PLATE_CLOSEUP_BACKGROUND_RGB = (150, 150, 150)
SIDE_VIEW_BACKGROUND_RGB = (150, 150, 150)
REAR_VIEW_BACKGROUND_RGB = (150, 150, 150)

# Front-dominant camera for organizer evidence (Finding 2 — not shared transport iso).
ORGANIZER_VIEW_DIRECTION = (0.0, -1.0, 0.15)


@dataclass(frozen=True)
class ViewSpec:
    """Orthographic camera: view direction (from model toward camera) and up vector."""

    direction: tuple[float, float, float]
    up: tuple[float, float, float] = (0.0, 0.0, 1.0)


@dataclass(frozen=True)
class RenderTarget:
    filename: str
    builder: Callable[[Parameters], AssemblyState]
    view: ViewSpec


def _normalize(vec: Sequence[float]) -> tuple[float, float, float]:
    arr = np.asarray(vec, dtype=float)
    length = float(np.linalg.norm(arr))
    if length <= 0:
        raise ValueError("zero-length vector")
    arr = arr / length
    return (float(arr[0]), float(arr[1]), float(arr[2]))


def _view_basis(view: ViewSpec) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return (right, up, view_dir) unit vectors; view_dir points from model toward camera."""
    view_dir = np.array(_normalize(view.direction), dtype=float)
    up_hint = np.array(view.up, dtype=float)
    if abs(float(np.dot(view_dir, up_hint))) > 0.95:
        up_hint = np.array([0.0, 1.0, 0.0], dtype=float)
    right = np.cross(up_hint, view_dir)
    right = right / np.linalg.norm(right)
    up = np.cross(view_dir, right)
    up = up / np.linalg.norm(up)
    return right, up, view_dir


def tessellate_shape(
    shape: object, linear_deflection: float = 1.5
) -> tuple[np.ndarray, np.ndarray]:
    """Tessellate a TopoDS shape into Nx3 vertices and Mx3 triangle index arrays."""
    BRepMesh_IncrementalMesh(shape, linear_deflection, False, 0.5, True)
    vertices: list[tuple[float, float, float]] = []
    triangles: list[tuple[int, int, int]] = []
    offset = 0
    explorer = TopExp_Explorer(shape, TopAbs_FACE)
    while explorer.More():
        face = TopoDS.Face_s(explorer.Current())
        location = TopLoc_Location()
        triangulation = BRep_Tool.Triangulation_s(face, location)
        if triangulation is None:
            explorer.Next()
            continue
        transform = location.Transformation()
        node_count = triangulation.NbNodes()
        for index in range(1, node_count + 1):
            point = triangulation.Node(index)
            point.Transform(transform)
            vertices.append((point.X(), point.Y(), point.Z()))
        tri_count = triangulation.NbTriangles()
        for index in range(1, tri_count + 1):
            tri = triangulation.Triangle(index)
            n1, n2, n3 = tri.Get()
            triangles.append((offset + n1 - 1, offset + n2 - 1, offset + n3 - 1))
        offset += node_count
        explorer.Next()
    if not vertices:
        return np.empty((0, 3), dtype=float), np.empty((0, 3), dtype=int)
    return np.asarray(vertices, dtype=float), np.asarray(triangles, dtype=int)


# Plotter design envelopes are non-physical clearance volumes; omit from PNG rasterizer
# so EQUIP-PLOTTER bodies show through front openings. Do not key on material
# "reference_envelope" — FILM-BODY-* uses the same tag but must render.
_SKIP_PNG_RASTER_PREFIXES = ("ENV-PLOTTER",)


def _collect_meshes(
    parts: dict[str, PartRecord], linear_deflection: float
) -> list[tuple[np.ndarray, np.ndarray, tuple[int, int, int]]]:
    meshes: list[tuple[np.ndarray, np.ndarray, tuple[int, int, int]]] = []
    for part_id, record in parts.items():
        if part_id.startswith(_SKIP_PNG_RASTER_PREFIXES):
            continue
        verts, tris = tessellate_shape(record.solid.wrapped, linear_deflection)
        if len(tris) == 0:
            continue
        if part_id.startswith("FILM-BODY-"):
            index = int(part_id.rsplit("-", 1)[-1])
            color = FILM_BODY_PALETTE[index % len(FILM_BODY_PALETTE)]
        else:
            color = MATERIAL_RGB.get(record.material, DEFAULT_RGB)
        meshes.append((verts, tris, color))
    return meshes


def _project_vertices(
    vertices: np.ndarray,
    right: np.ndarray,
    up: np.ndarray,
    view_dir: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    projected_x = vertices @ right
    projected_y = vertices @ up
    depth = vertices @ view_dir
    return projected_x, projected_y, depth


def _fit_to_canvas(
    xs: np.ndarray,
    ys: np.ndarray,
    width: int,
    height: int,
    margin: float = 0.08,
) -> tuple[float, float, float]:
    """Return (center_x, center_y, scale) mapping model coords to pixel space."""
    min_x, max_x = float(xs.min()), float(xs.max())
    min_y, max_y = float(ys.min()), float(ys.max())
    span_x = max(max_x - min_x, 1.0)
    span_y = max(max_y - min_y, 1.0)
    usable_w = width * (1.0 - 2.0 * margin)
    usable_h = height * (1.0 - 2.0 * margin)
    scale = min(usable_w / span_x, usable_h / span_y)
    cx = (min_x + max_x) / 2.0
    cy = (min_y + max_y) / 2.0
    return cx, cy, scale


def _map_to_screen(
    xs: np.ndarray,
    ys: np.ndarray,
    width: int,
    height: int,
    cx: float,
    cy: float,
    scale: float,
) -> tuple[np.ndarray, np.ndarray]:
    screen_x = (xs - cx) * scale + width / 2.0
    screen_y = (cy - ys) * scale + height / 2.0
    return screen_x, screen_y


def _rasterize_triangle(
    image: np.ndarray,
    depth: np.ndarray,
    x0: float,
    y0: float,
    z0: float,
    x1: float,
    y1: float,
    z1: float,
    x2: float,
    y2: float,
    z2: float,
    color: tuple[int, int, int],
) -> None:
    min_x = max(int(np.floor(min(x0, x1, x2))), 0)
    max_x = min(int(np.ceil(max(x0, x1, x2))), image.shape[1] - 1)
    min_y = max(int(np.floor(min(y0, y1, y2))), 0)
    max_y = min(int(np.ceil(max(y0, y1, y2))), image.shape[0] - 1)
    if min_x > max_x or min_y > max_y:
        return
    denom = (y1 - y2) * (x0 - x2) + (x2 - x1) * (y0 - y2)
    if abs(denom) < 1e-9:
        return
    for py in range(min_y, max_y + 1):
        for px in range(min_x, max_x + 1):
            w0 = ((y1 - y2) * (px - x2) + (x2 - x1) * (py - y2)) / denom
            w1 = ((y2 - y0) * (px - x2) + (x0 - x2) * (py - y2)) / denom
            w2 = 1.0 - w0 - w1
            if w0 < -1e-6 or w1 < -1e-6 or w2 < -1e-6:
                continue
            z = w0 * z0 + w1 * z1 + w2 * z2
            # view_dir points from model toward camera, so depth increases for nearer points.
            if z > depth[py, px]:
                depth[py, px] = z
                image[py, px] = color


def render_assembly_view(
    state: AssemblyState,
    view: ViewSpec,
    output_path: Path,
    *,
    width: int = 1280,
    height: int = 960,
    linear_deflection: float = 1.5,
    background_rgb: tuple[int, int, int] = (255, 255, 255),
) -> None:
    """Render one orthographic PNG for an assembly state."""
    right, up, view_dir = _view_basis(view)
    meshes = _collect_meshes(state.parts, linear_deflection)
    if not meshes:
        raise RuntimeError(f"No tessellated geometry for state {state.name!r}")

    all_x: list[np.ndarray] = []
    all_y: list[np.ndarray] = []
    for verts, tris, _ in meshes:
        px, py, _ = _project_vertices(verts, right, up, view_dir)
        all_x.append(px[tris].reshape(-1))
        all_y.append(py[tris].reshape(-1))
    fit_x = np.concatenate(all_x)
    fit_y = np.concatenate(all_y)
    cx, cy, scale = _fit_to_canvas(fit_x, fit_y, width, height)

    bg = np.array(background_rgb, dtype=np.uint8)
    image = np.tile(bg, (height, width, 1))
    zbuf = np.full((height, width), -np.inf, dtype=float)

    for verts, tris, color in meshes:
        px, py, pz = _project_vertices(verts, right, up, view_dir)
        sx, sy = _map_to_screen(px, py, width, height, cx, cy, scale)
        for i0, i1, i2 in tris:
            _rasterize_triangle(
                image,
                zbuf,
                sx[i0],
                sy[i0],
                pz[i0],
                sx[i1],
                sy[i1],
                pz[i1],
                sx[i2],
                sy[i2],
                pz[i2],
                color,
            )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    write_png(output_path, image)


def write_png(path: Path, rgb: np.ndarray) -> None:
    """Write an RGB uint8 array to PNG using only the Python standard library."""
    if rgb.dtype != np.uint8 or rgb.ndim != 3 or rgb.shape[2] != 3:
        raise ValueError("expected HxWx3 uint8 RGB array")
    height, width, _ = rgb.shape
    raw = b"".join(
        b"\x00" + rgb[row, :, :].tobytes() for row in range(height)
    )
    compressed = zlib.compress(raw, level=9)

    def chunk(tag: bytes, data: bytes) -> bytes:
        crc = zlib.crc32(tag + data) & 0xFFFFFFFF
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", crc)

    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", ihdr)
    png += chunk(b"IDAT", compressed)
    png += chunk(b"IEND", b"")
    path.write_bytes(png)


def build_base_plate_closeup_assembly(params: Parameters) -> AssemblyState:
    """Bottom inner panel and feet only — underside vent-slot evidence."""
    state = build_transport_assembly(params)
    keep = {
        "PANEL-IN-BOTTOM-001",
        "FOOT-001",
        "FOOT-002",
        "FOOT-003",
        "FOOT-004",
    }
    state.parts = {part_id: record for part_id, record in state.parts.items() if part_id in keep}
    state.name = "base_plate_closeup"
    return state


def build_organizer_closeup_assembly(params: Parameters) -> AssemblyState:
    """Organizer-loaded state — film bodies + dividers for close-up band evidence."""
    state = build_organizer_loaded_assembly(params)
    state.name = "organizer_closeup"
    return state


def build_rear_vent_closeup_assembly(params: Parameters) -> AssemblyState:
    """Rear outer panel only — vent slots against open grey backdrop (no inner rear)."""
    state = build_transport_assembly(params)
    state.parts = {
        part_id: record
        for part_id, record in state.parts.items()
        if part_id == "PANEL-OUT-REAR-001"
    }
    state.name = "rear_vent_closeup"
    return state


def build_single_part_assembly(params: Parameters, part_id: str) -> AssemblyState:
    """Isolate one registry part for identity / colour evidence renders."""
    state = build_transport_assembly(params)
    if part_id not in state.parts:
        raise KeyError(f"part {part_id!r} not in transport assembly")
    state.parts = {part_id: state.parts[part_id]}
    state.name = f"single_{part_id.lower().replace('-', '_')}"
    return state


def build_light_strip_only_assembly(params: Parameters) -> AssemblyState:
    return build_single_part_assembly(params, "LIGHT-STRIP-001")


def build_retainer_only_assembly(params: Parameters) -> AssemblyState:
    return build_single_part_assembly(params, "RETAINER-001")


def default_render_targets() -> list[RenderTarget]:
    iso = ViewSpec(direction=(-1.0, -1.0, 1.0))
    organizer_view = ViewSpec(direction=ORGANIZER_VIEW_DIRECTION)
    return [
        RenderTarget("transport_iso.png", build_transport_assembly, iso),
        RenderTarget("transport_front.png", build_transport_assembly, ViewSpec((0.0, -1.0, 0.0))),
        RenderTarget("transport_rear.png", build_transport_assembly, ViewSpec((0.0, 1.0, 0.0))),
        RenderTarget("transport_left.png", build_transport_assembly, ViewSpec((-1.0, 0.0, 0.0))),
        RenderTarget("transport_right.png", build_transport_assembly, ViewSpec((1.0, 0.0, 0.0))),
        RenderTarget(
            "transport_top.png",
            build_transport_assembly,
            ViewSpec((0.0, 0.0, 1.0)),
        ),
        RenderTarget("service_plotter_1_iso.png", build_service_plotter_1_assembly, iso),
        RenderTarget("service_plotter_2_iso.png", build_service_plotter_2_assembly, iso),
        RenderTarget("organizer_loaded_iso.png", build_organizer_loaded_assembly, organizer_view),
        RenderTarget("panels_hidden_iso.png", build_panels_hidden_assembly, iso),
        RenderTarget(
            "organizer_closeup.png",
            build_organizer_closeup_assembly,
            organizer_view,
        ),
        RenderTarget(
            "base_plate_closeup.png",
            build_base_plate_closeup_assembly,
            ViewSpec(direction=(0.0, 0.0, -1.0)),
        ),
        RenderTarget(
            "rear_vent_closeup.png",
            build_rear_vent_closeup_assembly,
            ViewSpec(direction=(0.0, 1.0, 0.0)),
        ),
        RenderTarget(
            "evidence_light_strip_only.png",
            build_light_strip_only_assembly,
            organizer_view,
        ),
        RenderTarget(
            "evidence_retainer_only.png",
            build_retainer_only_assembly,
            organizer_view,
        ),
    ]


def default_svg_targets() -> list[RenderTarget]:
    """Orthographic HLR line drawings for transport state only."""
    return [
        RenderTarget("transport_front.svg", build_transport_assembly, ViewSpec((0.0, -1.0, 0.0))),
        RenderTarget("transport_rear.svg", build_transport_assembly, ViewSpec((0.0, 1.0, 0.0))),
        RenderTarget("transport_left.svg", build_transport_assembly, ViewSpec((-1.0, 0.0, 0.0))),
        RenderTarget("transport_right.svg", build_transport_assembly, ViewSpec((1.0, 0.0, 0.0))),
        RenderTarget("transport_top.svg", build_transport_assembly, ViewSpec((0.0, 0.0, 1.0))),
    ]


def _hlr_edges_for_compound(compound: object, view_dir: tuple[float, float, float]) -> list[Edge]:
    """Hidden-line removal visible edges for one orthographic view."""
    dx, dy, dz = _normalize(view_dir)
    algo = HLRBRep_Algo()
    algo.Add(compound)
    projector = HLRAlgo_Projector(gp_Ax2(gp_Pnt(0.0, 0.0, 0.0), gp_Dir(dx, dy, dz)))
    algo.Projector(projector)
    algo.Update()
    algo.Hide()
    hlr = HLRBRep_HLRToShape(algo)
    vis = hlr.VCompound()
    if vis.IsNull():
        return []
    edges: list[Edge] = []
    explorer = TopExp_Explorer(vis, TopAbs_EDGE)
    while explorer.More():
        edges.append(Edge(TopoDS.Edge_s(explorer.Current())))
        explorer.Next()
    return edges


def _edge_is_exportable(edge: Edge) -> bool:
    """Skip HLR edges that crash build123d SVG export (common on fillet arcs)."""
    try:
        edge.geom_adaptor()
    except Exception:  # noqa: BLE001 — OCP raises Standard_NullObject
        return False
    return True


def render_assembly_svg(
    state: AssemblyState,
    view: ViewSpec,
    output_path: Path,
) -> None:
    """Render one orthographic SVG line drawing via OCP HLR."""
    compound = state.compound().wrapped
    edges = _hlr_edges_for_compound(compound, view.direction)
    if not edges:
        raise RuntimeError(f"No HLR edges for state {state.name!r}")
    exporter = ExportSVG()
    for edge in edges:
        if not _edge_is_exportable(edge):
            continue
        try:
            exporter.add_shape(edge)
        except BaseException:  # noqa: BLE001 — OCP Standard_NullObject may escape Exception
            continue
    output_path.parent.mkdir(parents=True, exist_ok=True)
    exporter.write(output_path)


def export_transport_mesh_formats(
    params: Parameters,
    output_dir: Path = DEFAULT_CONCEPT_DIR,
    *,
    stem: str = CONCEPT_STEM,
) -> dict[str, Path]:
    """Export transport assembly STL, labeled GLB, and viewer manifest."""
    return export_transport_mesh_bundle(
        params,
        output_dir,
        stem=stem,
        generated_from="scripts/render_validation_views.py",
    )


def render_all_views(
    params: Parameters,
    output_dir: Path = DEFAULT_OUTPUT_DIR,
    *,
    width: int = 1280,
    height: int = 960,
) -> list[Path]:
    written: list[Path] = []
    for target in default_render_targets():
        state = target.builder(params)
        path = output_dir / target.filename
        w, h = (
            (1920, 1440)
            if target.filename
            in ("organizer_closeup.png", "base_plate_closeup.png", "rear_vent_closeup.png")
            else (width, height)
        )
        if target.filename in (
            "base_plate_closeup.png",
            "rear_vent_closeup.png",
        ):
            bg = BASE_PLATE_CLOSEUP_BACKGROUND_RGB
        elif target.filename in ("transport_left.png", "transport_right.png"):
            bg = SIDE_VIEW_BACKGROUND_RGB
        elif target.filename == "transport_rear.png":
            bg = REAR_VIEW_BACKGROUND_RGB
        else:
            bg = (255, 255, 255)
        render_assembly_view(state, target.view, path, width=w, height=h, background_rgb=bg)
        written.append(path)
    for target in default_svg_targets():
        state = target.builder(params)
        path = output_dir / target.filename
        render_assembly_svg(state, target.view, path)
        written.append(path)
    return written


def main() -> None:
    params = load_parameters(DEFAULT_PARAMETERS)
    paths = render_all_views(params)
    mesh_paths = export_transport_mesh_formats(params)
    for path in paths:
        print(path)
    for label, path in mesh_paths.items():
        if path is not None:
            print(f"{label}: {path}")


if __name__ == "__main__":
    main()
