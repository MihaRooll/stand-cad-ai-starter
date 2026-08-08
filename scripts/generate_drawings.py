"""Generate PRELIMINARY/CONCEPT drawing package (PDF + REFERENCE_ONLY DXF) from live geometry."""

from __future__ import annotations

import csv
import importlib.util
import sys
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from build123d import ExportDXF, Plane

from stand_cad.geometry.analysis import (
    SHELL_THICKNESS_PATHS,
    handle_finger_intrusion_volume_mm3,
    part_mass_kg,
)
from stand_cad.geometry.assembly import (
    AssemblyState,
    build_service_plotter_1_assembly,
    build_service_plotter_2_assembly,
    build_transport_assembly,
    build_tray1_quick_access_assembly,
)
from stand_cad.geometry.datums import Datums
from stand_cad.geometry.export import CONCEPT_REVISION, export_transport_mesh_bundle
from stand_cad.geometry.hardware import (
    indicative_bracket_mass_kg,
    indicative_fastener_roll_up,
    joint_instance_counts,
    joint_type_registry,
)
from stand_cad.geometry.part_trace import part_trace_fn
from stand_cad.geometry.primitives import (
    bounding_box_bounds,
    bounding_box_size,
    box_from_bounds,
    intersection_volume,
)
from stand_cad.geometry.registry import PartRecord
from stand_cad.parameters import Parameters, load_parameters

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

DEFAULT_PARAMETERS = REPO_ROOT / "config" / "parameters.yaml"
DEFAULT_VALIDATION_DIR = REPO_ROOT / "output" / "validation" / f"rev{CONCEPT_REVISION}"
DEFAULT_VIEWS_DIR = DEFAULT_VALIDATION_DIR / "views"
DEFAULT_DXF_DIR = DEFAULT_VALIDATION_DIR / "dxf"
DEFAULT_DRAWINGS_DIR = DEFAULT_VALIDATION_DIR / "drawings"
DEFAULT_CONCEPT_DIR = REPO_ROOT / "output" / "concept"
PDF_NAME = (
    f"light_plotter_tower_DRAWINGS_PRELIMINARY_CONCEPT_NOT_FOR_PRODUCTION_rev{CONCEPT_REVISION}.pdf"
)

BASE_MARKINGS = ("PRELIMINARY", "CONCEPT", "NOT FOR PRODUCTION")

FABRICATED_MATERIALS = frozenset(
    {
        "aluminium_angle_15x15x1.5",
        "cast_opal_pmma_3mm",
        "white_composite_3_4mm",
        "sandwich_panel_10_12mm",
        "transparent_petg_2mm",
        "hdpe_insert_thin",
    }
)

FLAT_PANEL_MATERIALS = frozenset(
    {
        "cast_opal_pmma_3mm",
        "white_composite_3_4mm",
        "sandwich_panel_10_12mm",
        "transparent_petg_2mm",
        "hdpe_insert_thin",
    }
)

BOM_EXCLUDED_MATERIALS = frozenset(
    {
        "equipment_reference",
        "reference_envelope",
        "service_volume",
    }
)

_TOKEN_LABELS = {
    "FL": "front-left",
    "FR": "front-right",
    "RL": "rear-left",
    "RR": "rear-right",
    "L": "left",
    "R": "right",
    "C": "centre",
    "LOWER": "lower",
    "UPPER": "upper",
    "ORG": "organizer",
    "BASE": "base",
    "TOP": "top",
    "MID": "mid",
    "IN": "inner",
    "OUT": "outer",
    "CLAD": "cladding",
    "POST": "post",
    "RAIL": "rail",
    "PANEL": "panel",
    "TRAY": "tray",
    "SHELF": "shelf",
    "FOOT": "foot",
    "FRAME": "frame",
    "MEDIA": "media",
    "SUPPORT": "support",
    "SVC": "service",
    "CABLE": "cable",
    "PASSTHROUGH": "pass-through",
}


class TrackingParameters(Parameters):
    """Parameters wrapper that records every leaf path accessed via get()."""

    def __init__(self, raw: dict, accessed: set[str]) -> None:
        super().__init__(raw)
        self._accessed = accessed

    def get(self, path: str):
        self._accessed.add(path)
        return super().get(path)


def leaves_touched(base_params: Parameters, build_fn: Callable[[Parameters], object]) -> set[str]:
    accessed: set[str] = set()
    tp = TrackingParameters(base_params._raw, accessed)
    build_fn(tp)
    return accessed


def to_measure_leaves(base_params: Parameters, accessed: set[str]) -> list[str]:
    return sorted(p for p in accessed if base_params.get(p).provenance == "to_measure")


def leaves_touched_for_part(base_params: Parameters, part_id: str) -> set[str]:
    """Record leaves touched when building one fabricated part in isolation."""
    accessed: set[str] = set()
    tp = TrackingParameters(base_params._raw, accessed)
    tp_datums = Datums.from_parameters(tp)
    part_trace_fn(part_id)(tp, tp_datums)
    return accessed


@dataclass(frozen=True)
class SheetSpec:
    sheet_id: str
    title: str
    sheet_number: int
    sheet_total: int
    markings: tuple[str, ...]
    to_measure_leaves: tuple[str, ...]
    images: tuple[Path, ...] = ()
    notes: tuple[str, ...] = ()
    table: tuple[tuple[str, ...], ...] = ()


def _load_render_module():
    path = REPO_ROOT / "scripts" / "render_validation_views.py"
    spec = importlib.util.spec_from_file_location("render_validation_views", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["render_validation_views"] = module
    spec.loader.exec_module(module)
    return module


def _load_mass_report_module():
    path = REPO_ROOT / "scripts" / "generate_mass_report.py"
    spec = importlib.util.spec_from_file_location("generate_mass_report", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["generate_mass_report"] = module
    spec.loader.exec_module(module)
    return module


def _markings_for(to_measure: list[str]) -> tuple[str, ...]:
    marks = list(BASE_MARKINGS)
    if to_measure:
        marks.append("VERIFY ON REAL MACHINE")
    return tuple(marks)


def _part_description(part_id: str) -> str:
    tokens = part_id.replace("-", " ").split()
    words: list[str] = []
    for token in tokens:
        if token.isdigit() or (token.startswith("0") and token[1:].isdigit()):
            continue
        label = _TOKEN_LABELS.get(token, token.lower())
        words.append(label)
    if not words:
        return part_id
    return " ".join(words).capitalize()


def _part_thickness_label(record: PartRecord, params: Parameters) -> str:
    if record.material == "aluminium_angle_15x15x1.5":
        profile = float(params.value("materials.frame_profile_size_mm"))
        wall = float(params.value("materials.frame_wall_thickness_mm"))
        return f"{profile}×{profile}×{wall} mm angle"
    path = SHELL_THICKNESS_PATHS.get(record.material)
    if path is None:
        return "—"
    raw = params.value(path)
    if isinstance(raw, (int, float)):
        return f"{float(raw):g} mm"
    return str(raw)


def _provenance_tag(params: Parameters, path: str) -> str:
    return params.get(path).provenance


def _dxf_filename(part_id: str) -> str:
    return f"{part_id}_REFERENCE_ONLY_rev{CONCEPT_REVISION}.dxf"


_SIDE_SLAB_PART_IDS = frozenset({"PANEL-OUT-LEFT-001", "PANEL-OUT-RIGHT-001"})


def _flat_panel_detail_notes(
    part_id: str, record: PartRecord, dxf_path: Path, params: Parameters
) -> tuple[str, ...]:
    """DET sheet notes for flat-panel families — honest about cavity walls vs simple blanks."""
    thickness_note = f"Thickness: {_part_thickness_label(record, params)}."
    dxf_note = f"DXF outline: {dxf_path.name} (REFERENCE_ONLY — not manufacturer-ready)."
    if part_id in _SIDE_SLAB_PART_IDS:
        width = float(params.value("case.width"))
        internal = float(params.value("case.internal_width"))
        side_clear = (width - internal) / 2
        wall = float(params.value("materials.outer_panel_thickness_mm"))
        return (
            thickness_note,
            dxf_note,
            "Cavity-wall construction (D-055): 3 mm opal outer skin + front/rear Y returns with "
            f"~{side_clear - wall:.0f} mm air cavity inside {side_clear:.0f} mm side_clear — "
            "NOT a solid 20 mm acrylic slab.",
            "DXF is largest-face 2D outline only — not a formed flat pattern; manufacturer "
            "DFM owns fold/thermoform/bond method for the U-shell.",
        )
    return (
        thickness_note,
        dxf_note,
        "Flat sheet blank — no forming/bending required in current concept geometry.",
    )


def _read_mass_csv(path: Path) -> dict[str, float]:
    text = path.read_text(encoding="utf-8")
    lines: list[str] = []
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("#") or stripped.startswith('"#'):
            continue
        lines.append(line)
    reader = csv.DictReader(lines)
    return {
        row["part_id"]: float(row["mass_kg"])
        for row in reader
        if row.get("part_id") and row.get("mass_kg")
    }


def _modeling_limitations_notes(params: Parameters, transport: AssemblyState) -> tuple[str, ...]:
    side_clear = float(params.value("case.width")) - float(params.value("case.internal_width"))
    side_clear /= 2.0
    wall_mm = float(params.value("materials.outer_panel_thickness_mm"))
    side_notes: list[str] = []
    for part_id in ("PANEL-OUT-LEFT-001", "PANEL-OUT-RIGHT-001"):
        record = transport.parts[part_id]
        modeled_mass = part_mass_kg(record, params)
        solid_vol_mass = (
            float(record.solid.volume)
            / 1e9
            * float(params.value("materials.pmma_density_kg_m3"))
        )
        delta = abs(solid_vol_mass - modeled_mass)
        side_notes.append(
            f"{part_id}: D-055 cavity-wall (3 mm opal outer skin + front/rear Y returns, "
            f"~{side_clear - wall_mm:.0f} mm air cavity within {side_clear:.0f} mm side_clear) — "
            f"shell-model mass {modeled_mass:.4f} kg vs modeled-solid volume "
            f"{solid_vol_mass:.4f} kg (Δ≈{delta:.3f} kg — geometry/formula mismatch only, "
            f"NOT a solid 20 mm slab understatement)"
        )

    mid = transport.parts["PANEL-IN-MID-001"].solid
    mid_hits: list[str] = []
    for rail_id in (
        "FRAME-RAIL-TRAY-UPPER-L-001",
        "FRAME-RAIL-TRAY-UPPER-R-001",
        "FRAME-RAIL-TRAY-UPPER-C-001",
    ):
        vol = intersection_volume(mid, transport.parts[rail_id].solid)
        if vol > 0:
            mid_hits.append(f"PANEL-IN-MID-001 × {rail_id}: {vol:,.1f} mm³")

    floor_load = float(params.value("film_storage_horizontal.floor_design_load_kg"))

    return (
        "",
        "Known modelling limitations (not discharged by this package):",
        "- Weld-free joining specified (D-061) — 20×20×2 mm Al corner brackets + M4/M3 pan-head "
        "screws into rivnuts; exact grip lengths and torques remain to_measure; manufacturer "
        "may counter-propose equivalent gussets per docs/15_ASSEMBLY_INSTRUCTIONS.md.",
        (
            f"- Unsupported organizer floor — ORG-FLOOR-001 has no verified "
            f"structural/deflection check under "
            f"film_storage_horizontal.floor_design_load_kg ({floor_load:.0f} kg), unlike trays."
        ),
        "- PANEL-IN-MID-001 intersects upper tray rails (live intersection_volume): "
        + ("; ".join(mid_hits) if mid_hits else "none detected"),
        "- MEDIA-SUPPORT-L1/L2-001 glide-surface adequacy under real film stock has no structural "
        "check (state/DEFERRED_VERIFICATION.md D-046 remains open).",
        "- Frame modeled as solid prisms — FRAME-POST-*/FRAME-RAIL-* use rectangular solids; "
        "open-section equal-leg angle mass uses (2×profile−wall)×wall section in analysis.py "
        "(D-063 — supersedes erroneous 4×profile×wall formula).",
        "- Side slabs (D-055) — 3 mm opal PMMA cavity walls, not solid 20 mm acrylic:",
        *side_notes,
        "- Absent transport retention — no straps/latches/tie-downs modeled for plotters or film.",
        "- Absent thermal and electrical engineering — services.adapter_*/ctrl_rgbw_*/airpath_* "
        "volumes are unselected-hardware placeholders only.",
    )


_RFQ_DFM_QUESTIONS: tuple[str, ...] = (
    "Manufacturer DFM / quotation questions (docs/12_PRODUCTION_RFQ_TEMPLATE.md Q1–Q15):",
    "Q1 Joining counter-proposals — confirm or propose alternatives for each JOIN-001 type.",
    "Q2 Grip lengths / torques — M4×12 / M3×10 nominal; all install torques to_measure.",
    "Q3 Panel-to-frame — 3 mm opal cavity walls not primary load path; screw pitch ~150 mm.",
    "Q4 Slide mounting — JT-TRAY-SLIDE-FRAME hole pattern to_measure until slide selected.",
    "Q5 Recommended construction/material/thickness changes and rationale.",
    "Q6 Processes and machines proposed.",
    "Q7 Minimum bend radii, flange lengths, hole-to-bend distances, tool clearances.",
    "Q8 Flat patterns from formed STEP vs customer DXF — bend deduction / K-factor ownership.",
    "Q9 Economically held tolerances vs drawing changes required.",
    "Q10 Insert/fastener accessibility with side slabs installed last.",
    "Q11 Powder-coat prep, masking, colour/texture, minimum batch constraints.",
    "Q12 Ambiguous or impossible-to-inspect package details.",
    "Q13 First-article inspection scope and measurement report format.",
    "Q14 Quote NRE, prototype, optional second prototype, delivery, lead times separately.",
    "Q15 Identify every intended deviation before manufacture.",
)


def _open_questions_notes(params: Parameters, transport: AssemblyState) -> tuple[str, ...]:
    handle_y = float(params.value("hardware.handle_mount_y_mm"))
    handle_z = float(params.value("hardware.handle_mount_z_mm"))
    grip_len = float(params.value("hardware.handle_grip_length_mm"))
    grip_depth = float(params.value("hardware.handle_grip_depth_mm"))
    pw = float(params.value("plotter.physical_width"))
    p2 = transport.parts["EQUIP-PLOTTER2-001"].solid
    _, y_bounds, z_bounds = bounding_box_bounds(p2)
    intrusion = handle_finger_intrusion_volume_mm3(
        handle_mount_y_mm=handle_y,
        handle_mount_z_mm=handle_z,
        grip_length_mm=grip_len,
        grip_depth_mm=grip_depth,
        plotter_y_bounds=(y_bounds[0], y_bounds[1]),
        plotter_z_bounds=(z_bounds[0], z_bounds[1]),
        plotter_x_span_mm=pw,
    )
    deferred_ref = 1_782_932.0
    intrusion_note = (
        f"Handle-concept blocker (D-050/D-051): through-cutout grip at Y={handle_y} mm / "
        f"Z={handle_z} mm intersects tier-2 plotter bay — live finger-reach overlap "
        f"{intrusion:,.1f} mm³"
    )
    if abs(intrusion - deferred_ref) > 1000:
        intrusion_note += (
            f" (DEFERRED_VERIFICATION cites ~{deferred_ref:,.0f} mm³ — discrepancy flagged)"
        )

    return (
        "§A — Physical measurements on real equipment (docs/10_USER_INPUT_REQUIRED.md):",
        "1. Feed-plane height above machine lower support plane → plotter.feed_plane_z_from_base.",
        "2. Rear material exit coordinates.",
        "3. Real open-lid envelope and hinge position.",
        "4. Power and USB connector coordinates.",
        "5. OEM power adapter dimensions and minimum cable bend radius.",
        "6. Plotter foot positions and drill-free fixing points.",
        "7. Real film thickness/stiffness → film_storage_horizontal.min_stack_height_mm.",
        "8. Actual purchased sheet thickness → materials.actual_sheet_thickness_mm.",
        "Cameo 4 governing dimensions CLOSED; service-port connector type remains open.",
        "",
        "§B — Manufacturing authorization (docs/10_USER_INPUT_REQUIRED.md):",
        "Manufacturer DFM authorization open — owner must authorize RFQ vendors and approve "
        "prototype quotation before Gate G5 (ADR-003).",
        "",
        "Handle / carry ergonomics (state/DEFERRED_VERIFICATION.md D-050/D-051):",
        intrusion_note,
        "Owner deferred: external bolt-on handle, blind side pocket, or aft low-mounted cutout.",
        "Physical carry test required: balance-point grip vs loaded CoM, "
        "knee strike, front-heavy tip.",
        "",
        *_RFQ_DFM_QUESTIONS,
        "",
        *_modeling_limitations_notes(params, transport),
    )


def build_right_side_service_closeup_assembly(params: Parameters) -> AssemblyState:
    state = build_transport_assembly(params)
    state.parts = {
        part_id: record
        for part_id, record in state.parts.items()
        if part_id in ("PANEL-OUT-RIGHT-001", "SVC-CABLE-PASSTHROUGH-001")
    }
    state.name = "right_side_service_closeup"
    return state


def build_media_path_section_assembly(params: Parameters) -> tuple[AssemblyState, float]:
    state = build_transport_assembly(params)
    width = float(params.value("case.width"))
    depth = float(params.value("case.depth"))
    height = float(params.value("case.height"))
    x_mid = width / 2.0
    slab = box_from_bounds(x_mid - 1.0, 0.0, 0.0, x_mid + 1.0, depth, height)
    sliced: dict[str, PartRecord] = {}
    for part_id, record in state.parts.items():
        try:
            result = record.solid & slab
            if float(result.volume) < 1e-3:
                continue
            sliced[part_id] = PartRecord(
                part_id=record.part_id,
                material=record.material,
                solid=result,
                verify_on_real_machine=record.verify_on_real_machine,
            )
        except Exception:  # noqa: BLE001 — boolean slice may fail on degenerate parts
            continue
    return AssemblyState(name="media_path_section", parts=sliced), x_mid


def _render_section_view(
    params: Parameters,
    render,
    views_dir: Path,
) -> Path:
    section_state, x_mid = build_media_path_section_assembly(params)
    output = views_dir / "media_path_section_right.png"
    render.render_assembly_view(
        section_state,
        render.ViewSpec((1.0, 0.0, 0.0)),
        output,
        background_rgb=render.SIDE_VIEW_BACKGROUND_RGB,
    )
    return output


def _render_elev_view(params: Parameters, render, views_dir: Path) -> Path:
    output = views_dir / "elev_right_service_closeup.png"
    state = build_right_side_service_closeup_assembly(params)
    render.render_assembly_view(
        state,
        render.ViewSpec((1.0, 0.0, 0.0)),
        output,
        width=1920,
        height=1440,
        background_rgb=render.SIDE_VIEW_BACKGROUND_RGB,
    )
    return output


def build_all_sheet_specs(
    params: Parameters,
    *,
    views_dir: Path,
    dxf_dir: Path,
    mass_csv: Path,
    mass_totals: dict[str, float],
    render=None,
) -> list[SheetSpec]:
    """Pure sheet-spec builder — no reportlab dependency."""
    if render is None:
        render = _load_render_module()

    transport = build_transport_assembly(params)
    mass_by_part = _read_mass_csv(mass_csv)

    section_png = _render_section_view(params, render, views_dir)
    elev_png = _render_elev_view(params, render, views_dir)

    width = float(params.value("case.width"))
    depth = float(params.value("case.depth"))
    height = float(params.value("case.height"))
    channel_w = float(params.value("media_path.clear_width"))
    channel_h = float(params.value("media_path.slot_height_target"))
    lower_z = float(params.value("plotter.lower_z"))
    upper_z = float(params.value("plotter.upper_z"))
    feed_prov = float(params.value("plotter.feed_plane_z_provisional_mm"))
    feed_prov_path = "plotter.feed_plane_z_provisional_mm"
    l1_feed = lower_z + feed_prov
    l2_feed = upper_z + feed_prov

    media_support_notes: list[str] = []
    for part_id in ("MEDIA-SUPPORT-L1-001", "MEDIA-SUPPORT-L2-001"):
        if part_id in transport.parts:
            _, _, z_bounds = bounding_box_bounds(transport.parts[part_id].solid)
            media_support_notes.append(
                f"{part_id} Z bounds: [{z_bounds[0]:.1f}, {z_bounds[1]:.1f}] mm"
            )

    sheets: list[SheetSpec] = []

    ga_accessed = leaves_touched(params, lambda p: build_transport_assembly(p))
    ga_accessed |= leaves_touched(params, lambda p: Datums.from_parameters(p))
    ga_tm = to_measure_leaves(params, ga_accessed)
    sheets.append(
        SheetSpec(
            sheet_id="GA-001",
            title="General arrangement",
            sheet_number=0,
            sheet_total=0,
            markings=_markings_for(ga_tm),
            to_measure_leaves=tuple(ga_tm),
            images=(
                views_dir / "transport_front.png",
                views_dir / "transport_right.png",
                views_dir / "transport_top.png",
                views_dir / "transport_iso.png",
            ),
            notes=(
                f"Overall envelope: {width:.0f} × {depth:.0f} × {height:.0f} mm "
                f"(case.width / case.depth / case.height).",
                "Datum scheme (src/stand_cad/geometry/datums.py): origin at case front-left-bottom "
                "corner (0, 0, 0); +X toward right, +Y toward rear, +Z upward.",
                f"Case envelope X∈[0,{width:.0f}] Y∈[0,{depth:.0f}] Z∈[0,{height:.0f}] mm.",
                "Third-angle orthographic projection — front from −Y, right from +X, top from +Z "
                "(matches scripts/render_validation_views.py ViewSpec directions).",
            ),
        )
    )

    op_accessed: set[str] = set()
    for builder in (
        build_service_plotter_1_assembly,
        build_service_plotter_2_assembly,
        build_tray1_quick_access_assembly,
    ):
        op_accessed |= leaves_touched(params, builder)
    op_tm = to_measure_leaves(params, op_accessed)
    lower_ext = float(params.value("trays.lower_extension"))
    upper_ext = float(params.value("trays.upper_extension"))
    quick_ext = float(params.value("trays.lower_quick_access_extension_mm"))
    op_notes = (
        "Operating / service states — front and rear material-travel clearances (mm):",
        f"Tier 1 full service ({lower_ext:.0f} mm ext): front "
        f"{params.material_travel_clearance_front_mm(1, tray_extension_mm=lower_ext):.0f} mm "
        f"({_provenance_tag(params, 'trays.lower_extension')}); rear "
        f"{params.material_travel_clearance_rear_mm(1, tray_extension_mm=lower_ext):.0f} mm.",
        f"Tier 2 full service ({upper_ext:.0f} mm ext): front "
        f"{params.material_travel_clearance_front_mm(2, tray_extension_mm=upper_ext):.0f} mm; rear "
        f"{params.material_travel_clearance_rear_mm(2, tray_extension_mm=upper_ext):.0f} mm "
        f"({_provenance_tag(params, 'trays.upper_extension')}).",
        f"Tier 1 quick-access ({quick_ext:.0f} mm ext): front "
        f"{params.material_travel_clearance_front_mm(1, tray_extension_mm=quick_ext):.0f} mm; rear "
        f"{params.material_travel_clearance_rear_mm(1, tray_extension_mm=quick_ext):.0f} mm "
        f"({_provenance_tag(params, 'trays.lower_quick_access_extension_mm')}).",
    )
    sheets.append(
        SheetSpec(
            sheet_id="OP-001",
            title="Operating / service states",
            sheet_number=0,
            sheet_total=0,
            markings=_markings_for(op_tm),
            to_measure_leaves=tuple(op_tm),
            images=(
                views_dir / "service_plotter_1_iso.png",
                views_dir / "service_plotter_2_iso.png",
                views_dir / "tray1_quick_access_iso.png",
            ),
            notes=op_notes,
        )
    )

    sec_accessed = leaves_touched(params, lambda p: build_media_path_section_assembly(p)[0])
    sec_tm = to_measure_leaves(params, sec_accessed)
    _, x_mid = build_media_path_section_assembly(params)
    sec_notes = (
        f"True boolean cross-section at X = case.width/2 = {x_mid:.1f} mm (±1 mm slab).",
        "Not a full-assembly isometric — sliced solids from build_transport_assembly only.",
        f"Rear media channel: {channel_w:.0f} × {channel_h:.0f} mm clear "
        f"(media_path.clear_width × media_path.slot_height_target) at both tiers.",
        *media_support_notes,
        f"Tier-1 PROVISIONAL feed-plane height: {l1_feed:.1f} mm "
        f"(plotter.lower_z + {feed_prov_path}={feed_prov:.0f} mm, provenance "
        f"{_provenance_tag(params, feed_prov_path)}).",
        f"Tier-2 PROVISIONAL feed-plane height: {l2_feed:.1f} mm "
        f"(plotter.upper_z + {feed_prov_path}).",
        "plotter.feed_plane_z_from_base remains TO_MEASURE — not used here.",
    )
    sheets.append(
        SheetSpec(
            sheet_id="SEC-001",
            title="Media path section",
            sheet_number=0,
            sheet_total=0,
            markings=_markings_for(sec_tm),
            to_measure_leaves=tuple(sec_tm),
            images=(section_png,),
            notes=sec_notes,
        )
    )

    elev_accessed = leaves_touched(params, build_right_side_service_closeup_assembly)
    elev_tm = to_measure_leaves(params, elev_accessed)
    sp_y = float(params.value("hardware.service_port_mount_y_mm"))
    sp_z = float(params.value("hardware.service_port_mount_z_mm"))
    cp_y = float(params.value("hardware.cable_passthrough_mount_y_mm"))
    cp_z = float(params.value("hardware.cable_passthrough_mount_z_mm"))
    sp_w = float(params.value("hardware.service_port_cutout_width_mm"))
    sp_h = float(params.value("hardware.service_port_cutout_height_mm"))
    cp_d = float(params.value("hardware.cable_passthrough_diameter_mm"))
    elev_notes = (
        "Right-side elevation — PANEL-OUT-RIGHT-001 + SVC-CABLE-PASSTHROUGH-001 (D-047 placement).",
        f"Service port centre: Y={sp_y:.0f} mm, Z={sp_z:.0f} mm; cutout {sp_w:.0f}×{sp_h:.0f} mm.",
        f"Cable pass-through centre: Y={cp_y:.0f} mm, Z={cp_z:.0f} mm; Ø{cp_d:.0f} mm.",
        (
            f"Provenance: service_port_mount → "
            f"{_provenance_tag(params, 'hardware.service_port_mount_y_mm')}; "
            f"cutout dims → {_provenance_tag(params, 'hardware.service_port_cutout_width_mm')}; "
            f"cable diameter → {_provenance_tag(params, 'hardware.cable_passthrough_diameter_mm')}."
        ),
    )
    sheets.append(
        SheetSpec(
            sheet_id="ELEV-001",
            title="Right-side elevation — service port + cable pass-through",
            sheet_number=0,
            sheet_total=0,
            markings=_markings_for(elev_tm),
            to_measure_leaves=tuple(elev_tm),
            images=(elev_png,),
            notes=elev_notes,
        )
    )

    fabricated = sorted(
        (pid, rec)
        for pid, rec in transport.parts.items()
        if rec.material in FABRICATED_MATERIALS
    )
    for index, (part_id, record) in enumerate(fabricated, start=1):
        det_accessed = leaves_touched_for_part(params, part_id)
        det_tm = to_measure_leaves(params, det_accessed)
        sx, sy, sz = bounding_box_size(record.solid)
        det_notes: list[str] = [
            f"Part ID: {part_id}",
            f"Material: {record.material}",
            f"Bounding box: {sx:.1f} × {sy:.1f} × {sz:.1f} mm",
        ]
        if record.material == "aluminium_angle_15x15x1.5":
            cut_len = max(sx, sy, sz)
            det_notes.append(f"Cut length: {cut_len:.1f} mm (max bbox dimension).")
            det_notes.append(
                f"Profile: {_part_thickness_label(record, params)} — "
                "cut-to-length stock, no DXF."
            )
        elif record.material in FLAT_PANEL_MATERIALS:
            dxf_path = dxf_dir / _dxf_filename(part_id)
            det_notes.extend(_flat_panel_detail_notes(part_id, record, dxf_path, params))
        else:
            det_notes.append(f"Thickness: {_part_thickness_label(record, params)}.")
        sheets.append(
            SheetSpec(
                sheet_id=f"DET-{index:03d}",
                title=f"Detail — {part_id}",
                sheet_number=0,
                sheet_total=0,
                markings=_markings_for(det_tm),
                to_measure_leaves=tuple(det_tm),
                notes=tuple(det_notes),
            )
        )

    join_accessed = leaves_touched(params, build_transport_assembly)
    join_tm = to_measure_leaves(params, join_accessed)
    join_rows: list[tuple[str, ...]] = [
        ("joint_type_id", "part_a", "part_b", "method", "fastener", "qty/joint", "instances"),
    ]
    counts = joint_instance_counts(params)
    for spec in joint_type_registry(params):
        join_rows.append(
            (
                spec.joint_type_id,
                spec.part_a_pattern,
                spec.part_b_pattern,
                spec.method[:80] + ("…" if len(spec.method) > 80 else ""),
                f"{spec.fastener_size} {spec.fastener_type}",
                str(spec.qty_per_joint),
                str(counts[spec.joint_type_id]),
            )
        )
    fastener_roll = indicative_fastener_roll_up(params)
    fastener_kg = float(fastener_roll["mass_kg"])
    bracket_kg = indicative_bracket_mass_kg(params)
    bracket_nodes = counts["JT-FRAME-CORNER"] + counts["JT-TRAY-RAIL-FRAME"]
    join_notes = (
        "Weld-free joining (D-061/D-060) — NO WELDING on 15×15×1.5 mm aluminium angle frame.",
        "JT-FRAME-CORNER (D-063): 1×M4 per bracket leg (qty/joint=2) — dual M4 per 15 mm angle "
        "leg rejected for insufficient edge distance; bracket hole positions to_measure.",
        "JT-TRAY-RAIL-FRAME: tray ring rails use same D-063 bracket schedule (12 nodes × qty 2); "
        "separated from perimeter JT-FRAME-CORNER for assembly/JOIN-001 clarity.",
        f"Indicative bought-in fastener mass (excluded from structural total): "
        f"{fastener_kg:.3f} kg ({fastener_roll['total']} screws: "
        f"{fastener_roll['m4']} M4 + {fastener_roll['m3']} M3; "
        f"registry {fastener_roll['registry_total']} + "
        f"{fastener_roll['supplementary_m4']} FOOT M4 + "
        f"{fastener_roll['supplementary_m3']} base-clad M3; lengths to_measure).",
        f"Indicative corner-bracket mass (20×20×2 mm L-gusset × "
        f"{bracket_nodes} nodes: {counts['JT-FRAME-CORNER']} JT-FRAME-CORNER + "
        f"{counts['JT-TRAY-RAIL-FRAME']} JT-TRAY-RAIL-FRAME): "
        f"{bracket_kg:.3f} kg — corner brackets not modeled as individual STEP solids; "
        "mass from hardware.indicative_bracket_mass_kg only.",
        "JT-HANDLE-HARDWARE: owner OPEN §F — through-cut grip only; no bolt-on spec decided.",
        "JT-SHELF-SUPPORT-SKIN (D-065): 15×15×1.5 L-angle cleat; 3×M4 into vertical-leg rivnuts "
        "— front/mid/rear along Y (~150 mm pitch); adhesive-free.",
        "FOOT-*: 1×M4 through foot centre into post-base rivnut — silicone pad isolation only, "
        "no adhesive. PANEL-CLAD-FRONT-BASE-001: countersunk M3 into base-rail rivnuts.",
        "Manufacturer may counter-propose bracket stock / rivnut brands — see RFQ questions.",
        "Full sequence: docs/15_ASSEMBLY_INSTRUCTIONS.md.",
    )
    sheets.append(
        SheetSpec(
            sheet_id="JOIN-001",
            title="Weld-free joint schedule",
            sheet_number=0,
            sheet_total=0,
            markings=_markings_for(join_tm),
            to_measure_leaves=tuple(join_tm),
            notes=join_notes,
            table=join_rows,
        )
    )

    bom_accessed = leaves_touched(params, build_transport_assembly)
    bom_tm = to_measure_leaves(params, bom_accessed)
    bom_rows: list[tuple[str, ...]] = [
        ("part_id", "description", "qty", "material", "thickness", "mass_kg"),
    ]
    bom_parts = [
        (pid, rec)
        for pid, rec in sorted(transport.parts.items())
        if rec.material not in BOM_EXCLUDED_MATERIALS
    ]
    for part_id, record in bom_parts:
        thickness = _part_thickness_label(record, params)
        if record.material not in FABRICATED_MATERIALS and thickness == "—":
            thickness = "—"
        mass = mass_by_part.get(part_id, part_mass_kg(record, params))
        mass_cell = f"{mass:.4f}"
        if part_id in ("PANEL-OUT-LEFT-001", "PANEL-OUT-RIGHT-001"):
            mass_cell += "*"
        bom_rows.append(
            (
                part_id,
                _part_description(part_id),
                "1",
                record.material,
                thickness,
                mass_cell,
            )
        )
    bom_notes = (
        "Bill of materials — one row per registry part_id (quantity always 1; identical parts "
        "not geometrically aggregated — documented simplification).",
        f"Excluded materials: {', '.join(sorted(BOM_EXCLUDED_MATERIALS))}.",
        "* PANEL-OUT-LEFT/RIGHT-001: cavity-wall shell mass (D-055) — see OPEN-001.",
        f"Mass totals from regenerated mass_report.csv: structural_kg="
        f"{mass_totals['structural_kg']:.3f}, all_parts_kg={mass_totals['all_parts_kg']:.3f}.",
    )
    sheets.append(
        SheetSpec(
            sheet_id="BOM-001",
            title="Bill of materials",
            sheet_number=0,
            sheet_total=0,
            markings=_markings_for(bom_tm),
            to_measure_leaves=tuple(bom_tm),
            table=tuple(bom_rows),
            notes=bom_notes,
        )
    )

    open_accessed = leaves_touched(params, build_transport_assembly)
    open_tm = to_measure_leaves(params, open_accessed)
    sheets.append(
        SheetSpec(
            sheet_id="OPEN-001",
            title="Open questions",
            sheet_number=0,
            sheet_total=0,
            markings=_markings_for(open_tm),
            to_measure_leaves=tuple(open_tm),
            notes=_open_questions_notes(params, transport),
        )
    )

    total = len(sheets)
    return [
        SheetSpec(
            sheet_id=s.sheet_id,
            title=s.title,
            sheet_number=index,
            sheet_total=total,
            markings=s.markings,
            to_measure_leaves=s.to_measure_leaves,
            images=s.images,
            notes=s.notes,
            table=s.table,
        )
        for index, s in enumerate(sheets, start=1)
    ]


def export_dxf_outlines(
    params: Parameters,
    dxf_dir: Path,
) -> list[Path]:
    """Export REFERENCE_ONLY flat-panel DXF outlines."""
    state = build_transport_assembly(params)
    dxf_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    for part_id, record in sorted(state.parts.items()):
        if record.material not in FLAT_PANEL_MATERIALS:
            continue
        output_path = dxf_dir / _dxf_filename(part_id)
        faces = sorted(record.solid.faces(), key=lambda f: f.area, reverse=True)
        face = faces[0]
        local_face = Plane(face).to_local_coords(face)
        doc = ExportDXF()
        doc.add_shape(local_face)
        doc.write(str(output_path))
        written.append(output_path)
    return written


def render_drawing_pdf(sheets: list[SheetSpec], output_path: Path) -> None:
    """Render sheet specs to a multi-page A3 PDF via reportlab."""
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A3
    from reportlab.lib.units import mm
    from reportlab.lib.utils import ImageReader
    from reportlab.pdfgen import canvas
    from reportlab.platypus import Table, TableStyle

    output_path.parent.mkdir(parents=True, exist_ok=True)
    page_w, page_h = A3
    margin = 15 * mm
    title_block_h = 28 * mm
    run_date = date.today().isoformat()

    c = canvas.Canvas(str(output_path), pagesize=A3)

    for sheet in sheets:
        y_cursor = page_h - margin

        c.setFont("Helvetica-Bold", 14)
        for mark in sheet.markings:
            c.setStrokeColor(colors.red)
            c.setFillColor(colors.red)
            c.rect(margin, y_cursor - 16, page_w - 2 * margin, 18, stroke=1, fill=0)
            c.drawString(margin + 6, y_cursor - 12, mark)
            y_cursor -= 22

        y_cursor -= 4
        c.setFillColor(colors.black)
        c.setFont("Helvetica-Bold", 12)
        c.drawString(margin, y_cursor, f"{sheet.sheet_id} — {sheet.title}")
        y_cursor -= 16

        content_bottom = margin + title_block_h + 8
        img_box_h = max(y_cursor - content_bottom, 40 * mm)
        if sheet.images:
            img_count = len(sheet.images)
            cols = min(img_count, 2)
            rows = (img_count + cols - 1) // cols
            cell_w = (page_w - 2 * margin) / cols
            cell_h = img_box_h / rows
            for idx, img_path in enumerate(sheet.images):
                if not img_path.is_file():
                    continue
                row = idx // cols
                col = idx % cols
                x = margin + col * cell_w + 4
                y = y_cursor - (row + 1) * cell_h + 4
                try:
                    reader = ImageReader(str(img_path))
                    iw, ih = reader.getSize()
                    scale = min((cell_w - 8) / iw, (cell_h - 8) / ih)
                    draw_w = iw * scale
                    draw_h = ih * scale
                    c.drawImage(
                        reader,
                        x + (cell_w - 8 - draw_w) / 2,
                        y + (cell_h - 8 - draw_h) / 2,
                        draw_w,
                        draw_h,
                    )
                except Exception:  # noqa: BLE001
                    c.setFont("Helvetica", 8)
                    c.drawString(x, y + cell_h / 2, f"[missing: {img_path.name}]")
            y_cursor -= img_box_h

        text = c.beginText(margin, y_cursor)
        text.setFont("Helvetica", 9)
        for note in sheet.notes:
            for line in _wrap_text(note, 110):
                text.textLine(line)
            text.textLine("")
        if sheet.to_measure_leaves:
            text.setFont("Helvetica-Bold", 9)
            text.textLine(
                "Depends on unmeasured (to_measure) parameters — "
                "see docs/10_USER_INPUT_REQUIRED.md:"
            )
            text.setFont("Helvetica", 8)
            for leaf in sheet.to_measure_leaves:
                text.textLine(f"  • {leaf}")
        c.drawText(text)

        if sheet.table:
            tbl = Table(list(sheet.table), repeatRows=1)
            tbl.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                        ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
                        ("FONTSIZE", (0, 0), (-1, -1), 7),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ]
                )
            )
            tw, th = tbl.wrap(page_w - 2 * margin, page_h)
            tbl_y = max(content_bottom + th, margin + title_block_h + th)
            if tbl_y > page_h * 0.4:
                tbl_y = content_bottom + 4
            tbl.drawOn(c, margin, tbl_y)

        c.setFont("Helvetica", 8)
        c.drawString(margin, title_block_h - 4, "Light Plotter Tower")
        c.drawString(margin, title_block_h - 14, f"Revision: rev{CONCEPT_REVISION}")
        c.drawString(margin, title_block_h - 24, f"Date: {run_date}")
        c.drawString(
            120 * mm,
            title_block_h - 4,
            f"Sheet {sheet.sheet_number} / {sheet.sheet_total}",
        )
        c.drawString(120 * mm, title_block_h - 14, "Units: mm")
        c.drawString(120 * mm, title_block_h - 24, "Projection: third-angle")
        c.line(margin, title_block_h + 2, page_w - margin, title_block_h + 2)
        c.showPage()

    c.save()


def _wrap_text(text: str, width: int) -> list[str]:
    words = text.split()
    if not words:
        return [""]
    lines: list[str] = []
    current: list[str] = []
    for word in words:
        trial = " ".join([*current, word])
        if len(trial) <= width:
            current.append(word)
        else:
            if current:
                lines.append(" ".join(current))
            current = [word]
    if current:
        lines.append(" ".join(current))
    return lines


def main() -> None:
    params = load_parameters(DEFAULT_PARAMETERS)
    render = _load_render_module()
    mass_mod = _load_mass_report_module()

    print(f"Generating PRELIMINARY drawing package rev{CONCEPT_REVISION}...")
    render.render_all_views(params, DEFAULT_VIEWS_DIR)
    mesh_paths = export_transport_mesh_bundle(
        params,
        DEFAULT_CONCEPT_DIR,
        stem=f"light_plotter_tower_ASSEMBLY_CONCEPT_REFERENCE_ONLY_rev{CONCEPT_REVISION}",
        generated_from="scripts/generate_drawings.py",
    )
    for label, path in mesh_paths.items():
        if path is not None:
            print(f"  {label}: {path}")

    mass_totals = mass_mod.write_all_reports(
        params_path=DEFAULT_PARAMETERS,
        validation_dir=DEFAULT_VALIDATION_DIR,
    )
    mass_csv = DEFAULT_VALIDATION_DIR / "mass_report.csv"
    print(f"  mass_report: {mass_csv}")

    sheets = build_all_sheet_specs(
        params,
        views_dir=DEFAULT_VIEWS_DIR,
        dxf_dir=DEFAULT_DXF_DIR,
        mass_csv=mass_csv,
        mass_totals=mass_totals,
        render=render,
    )

    pdf_path = DEFAULT_DRAWINGS_DIR / PDF_NAME
    render_drawing_pdf(sheets, pdf_path)
    dxf_paths = export_dxf_outlines(params, DEFAULT_DXF_DIR)

    verify_count = sum(1 for s in sheets if "VERIFY ON REAL MACHINE" in s.markings)
    det_sheets = [s for s in sheets if s.sheet_id.startswith("DET-")]
    det_counts = [len(s.to_measure_leaves) for s in det_sheets]
    zero_det = sum(1 for count in det_counts if count == 0)
    print(f"\nRevision: rev{CONCEPT_REVISION}")
    print(f"Sheets: {len(sheets)} ({verify_count} carry VERIFY ON REAL MACHINE)")
    if det_counts:
        print(
            f"DET to_measure leaf counts: {zero_det} sheets with 0, "
            f"{len(det_counts) - zero_det} with >0, "
            f"min={min(det_counts)}, max={max(det_counts)}"
        )
    print(f"PDF: {pdf_path}")
    print(f"DXF files: {len(dxf_paths)} in {DEFAULT_DXF_DIR}")
    print(
        f"BOM totals: structural_kg={mass_totals['structural_kg']:.3f}, "
        f"all_parts_kg={mass_totals['all_parts_kg']:.3f}"
    )


if __name__ == "__main__":
    main()
