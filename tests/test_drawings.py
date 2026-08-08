"""Tests for PRELIMINARY drawing package sheet-spec model and file emission."""

from __future__ import annotations

import importlib.util
import sys
import tempfile
from pathlib import Path

import pytest

from stand_cad.geometry.assembly import build_transport_assembly
from stand_cad.parameters import load_parameters

REPO_ROOT = Path(__file__).resolve().parents[1]
PARAMETERS_PATH = REPO_ROOT / "config" / "parameters.yaml"
_DRAWINGS_MODULE_PATH = REPO_ROOT / "scripts" / "generate_drawings.py"
_MASS_MODULE_PATH = REPO_ROOT / "scripts" / "generate_mass_report.py"
_RENDER_MODULE_PATH = REPO_ROOT / "scripts" / "render_validation_views.py"

BASE_MARKINGS = frozenset({"PRELIMINARY", "CONCEPT", "NOT FOR PRODUCTION"})


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@pytest.fixture(scope="module")
def params():
    return load_parameters(PARAMETERS_PATH)


@pytest.fixture(scope="module")
def drawings_mod():
    return _load_module("generate_drawings", _DRAWINGS_MODULE_PATH)


@pytest.fixture(scope="module")
def mass_mod():
    return _load_module("generate_mass_report", _MASS_MODULE_PATH)


@pytest.fixture(scope="module")
def render_mod():
    return _load_module("render_validation_views", _RENDER_MODULE_PATH)


@pytest.fixture(scope="module")
def validation_dir(tmp_path_factory):
    return tmp_path_factory.mktemp("rev_drawings")


@pytest.fixture(scope="module")
def sheet_pack(params, drawings_mod, mass_mod, render_mod, validation_dir):
    views_dir = validation_dir / "views"
    dxf_dir = validation_dir / "dxf"
    views_dir.mkdir(parents=True, exist_ok=True)
    render_mod.render_all_views(params, views_dir)
    mass_totals = mass_mod.write_all_reports(
        params_path=PARAMETERS_PATH,
        validation_dir=validation_dir,
    )
    mass_csv = validation_dir / "mass_report.csv"
    sheets = drawings_mod.build_all_sheet_specs(
        params,
        views_dir=views_dir,
        dxf_dir=dxf_dir,
        mass_csv=mass_csv,
        mass_totals=mass_totals,
        render=render_mod,
    )
    return sheets, params, mass_totals, views_dir, dxf_dir


def test_every_sheet_has_base_markings(sheet_pack):
    sheets, _, _, _, _ = sheet_pack
    for sheet in sheets:
        assert BASE_MARKINGS <= set(sheet.markings)


def test_verify_marking_iff_to_measure_leaves(sheet_pack):
    sheets, _, _, _, _ = sheet_pack
    for sheet in sheets:
        has_verify = "VERIFY ON REAL MACHINE" in sheet.markings
        has_tm = len(sheet.to_measure_leaves) > 0
        assert has_verify == has_tm


def test_to_measure_leaves_are_to_measure_provenance(sheet_pack):
    sheets, params, _, _, _ = sheet_pack
    for sheet in sheets:
        for path in sheet.to_measure_leaves:
            assert params.get(path).provenance == "to_measure"


def test_bom_row_count_matches_registry(sheet_pack, drawings_mod):
    sheets, params, _, _, _ = sheet_pack
    bom = next(s for s in sheets if s.sheet_id == "BOM-001")
    expected = sum(
        1
        for rec in build_transport_assembly(params).parts.values()
        if rec.material not in drawings_mod.BOM_EXCLUDED_MATERIALS
    )
    assert len(bom.table) - 1 == expected


def test_det_sheet_count_matches_fabricated_parts(sheet_pack, drawings_mod):
    sheets, params, _, _, _ = sheet_pack
    det_sheets = [s for s in sheets if s.sheet_id.startswith("DET-")]
    expected = sum(
        1
        for rec in build_transport_assembly(params).parts.values()
        if rec.material in drawings_mod.FABRICATED_MATERIALS
    )
    assert len(det_sheets) == expected


def test_sheet_numbering_contiguous(sheet_pack):
    sheets, _, _, _, _ = sheet_pack
    total = len(sheets)
    numbers = [s.sheet_number for s in sheets]
    assert all(s.sheet_total == total for s in sheets)
    assert numbers == list(range(1, total + 1))


def test_det_part_to_measure_tracing_reviewer_spot_checks(sheet_pack, drawings_mod):
    """Per-part DET tracing must match isolated part construction (adversarial F-1/F-3)."""
    sheets, params, _, _, _ = sheet_pack
    det_by_title = {
        sheet.title.removeprefix("Detail — "): sheet
        for sheet in sheets
        if sheet.sheet_id.startswith("DET-")
    }

    def tm_set(part_id: str) -> set[str]:
        return set(det_by_title[part_id].to_measure_leaves)

    assert tm_set("COVER-SVC-001") == set()
    assert tm_set("PANEL-IN-MID-001") == set()
    assert tm_set("MEDIA-SUPPORT-L1-001") == {"plotter.feed_plane_z_provisional_mm"}
    assert tm_set("MEDIA-SUPPORT-L2-001") == {"plotter.feed_plane_z_provisional_mm"}
    rear_tm = tm_set("PANEL-OUT-REAR-001")
    assert "hardware.cable_passthrough_diameter_mm" not in rear_tm
    assert "hardware.service_port_cutout_width_mm" not in rear_tm
    assert "hardware.service_port_cutout_height_mm" not in rear_tm

    # Live-registry cross-check: traced leaves match direct per-part trace helper.
    for part_id in (
        "COVER-SVC-001",
        "PANEL-IN-MID-001",
        "MEDIA-SUPPORT-L1-001",
        "PANEL-OUT-REAR-001",
    ):
        expected = set(
            drawings_mod.to_measure_leaves(
                params,
                drawings_mod.leaves_touched_for_part(params, part_id),
            )
        )
        assert tm_set(part_id) == expected


def test_pdf_and_dxf_emission_end_to_end(params, drawings_mod, mass_mod, render_mod):
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        views_dir = root / "views"
        dxf_dir = root / "dxf"
        drawings_dir = root / "drawings"
        views_dir.mkdir()
        render_mod.render_all_views(params, views_dir)
        mass_totals = mass_mod.write_all_reports(
            params_path=PARAMETERS_PATH,
            validation_dir=root,
        )
        mass_csv = root / "mass_report.csv"
        sheets = drawings_mod.build_all_sheet_specs(
            params,
            views_dir=views_dir,
            dxf_dir=dxf_dir,
            mass_csv=mass_csv,
            mass_totals=mass_totals,
            render=render_mod,
        )
        pdf_path = drawings_dir / drawings_mod.PDF_NAME
        drawings_mod.render_drawing_pdf(sheets, pdf_path)
        dxf_paths = drawings_mod.export_dxf_outlines(params, dxf_dir)
        assert pdf_path.is_file() and pdf_path.stat().st_size > 0
        assert len(dxf_paths) > 0
        assert all(p.stat().st_size > 0 for p in dxf_paths)
        rev = drawings_mod.CONCEPT_REVISION
        for path in dxf_paths:
            assert "REFERENCE_ONLY" in path.name, path.name
            assert path.name.endswith(f"_rev{rev}.dxf"), path.name
            assert "_REFERENCE_ONLY_rev" in path.name, path.name


def test_side_slab_det_notes_honest_cavity_wall(sheet_pack):
    """F4-2 — side slabs must not claim flat blank / no forming."""
    sheets, _, _, _, _ = sheet_pack
    for part_id in ("PANEL-OUT-LEFT-001", "PANEL-OUT-RIGHT-001"):
        det = next(s for s in sheets if s.title == f"Detail — {part_id}")
        notes_text = " ".join(det.notes).lower()
        assert "flat sheet part, no forming" not in notes_text
        assert "cavity-wall" in notes_text or "cavity wall" in notes_text
        assert "not a formed flat pattern" in notes_text


def test_open_sheet_includes_rfq_dfm_questions(sheet_pack):
    """F4-3 — OPEN-001 carries manufacturer DFM question list."""
    sheets, _, _, _, _ = sheet_pack
    open_sheet = next(s for s in sheets if s.sheet_id == "OPEN-001")
    notes_text = " ".join(open_sheet.notes)
    assert "Q1 Joining counter-proposals" in notes_text
    assert "Q15 Identify every intended deviation" in notes_text


def test_join_sheet_bracket_node_count(sheet_pack, drawings_mod):
    """F4-4 — JOIN-001 bracket roll-up cites 34 nodes (22 + 12)."""
    sheets, params, _, _, _ = sheet_pack
    join = next(s for s in sheets if s.sheet_id == "JOIN-001")
    counts = drawings_mod.joint_instance_counts(params)
    bracket_nodes = counts["JT-FRAME-CORNER"] + counts["JT-TRAY-RAIL-FRAME"]
    notes_text = " ".join(join.notes)
    assert f"{bracket_nodes} nodes" in notes_text
    assert "JT-FRAME-CORNER" in notes_text
    assert "JT-TRAY-RAIL-FRAME" in notes_text
