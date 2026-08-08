# A passing test is not evidence of physical correctness.
"""Geometry tests for PLT-002 static structure and Packet-3 completion."""

from __future__ import annotations

from pathlib import Path

import pytest

from stand_cad.geometry.analysis import (
    empty_case_mass_kg,
    handle_finger_intrusion_volume_mm3,
    indicative_tray_deflection_mm,
    loaded_case_centre_of_mass_mm,
)
from stand_cad.geometry.assembly import (
    build_film_body_parts,
    build_operating_with_test_bodies_assembly,
    build_organizer_loaded_assembly,
    build_transport_assembly,
    build_transport_display_assembly,
)
from stand_cad.geometry.datums import Datums
from stand_cad.geometry.primitives import (
    bounding_box_bounds,
    bounding_box_size,
    box_from_bounds,
    intersection_volume,
    minimum_clearance,
    translate_solid,
)
from stand_cad.parameters import (
    HORIZONTAL_ORGANIZER_CLEAR_MIN_MM,
    load_parameters,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
PARAMETERS_PATH = REPO_ROOT / "config" / "parameters.yaml"


def test_overall_assembly_bounding_box(params, transport):
    tol = float(params.value("tolerance.assembly_mm"))
    cap_t = float(params.value("stacking.cap_thickness_mm"))
    compound = transport.compound()
    size = bounding_box_size(compound)
    expected = (
        float(params.value("case.width")),
        float(params.value("case.depth")),
        float(params.value("case.height")) + cap_t,
    )
    for actual, target in zip(size, expected, strict=True):
        assert actual == pytest.approx(target, abs=tol)


def test_plotter_physical_bodies(params, transport, datums):
    """Per-slot EQUIP bodies use actual machine height; governing envelope stays in ENV-* tests."""
    tol = float(params.value("tolerance.assembly_mm"))
    pw = float(params.value("plotter.physical_width"))
    pd = float(params.value("plotter.physical_depth"))

    slot_specs = (
        (1, "EQUIP-PLOTTER1-001", datums.plotter1_physical, params.plotter_height_mm(1)),
        (2, "EQUIP-PLOTTER2-001", datums.plotter2_physical, params.plotter_height_mm(2)),
    )
    assert params.plotter_height_mm(1) == pytest.approx(170.0)
    assert params.plotter_height_mm(2) == pytest.approx(124.0)

    for _index, part_id, datum, expected_height in slot_specs:
        solid = transport.parts[part_id].solid
        size = bounding_box_size(solid)
        expected_size = (pw, pd, expected_height)
        for actual, target in zip(size, expected_size, strict=True):
            assert actual == pytest.approx(target, abs=tol)
        bounds = bounding_box_bounds(solid)
        assert bounds[0][0] == pytest.approx(datum.x.min_mm, abs=tol)
        assert bounds[0][1] == pytest.approx(datum.x.max_mm, abs=tol)
        assert bounds[1][0] == pytest.approx(datum.y.min_mm, abs=tol)
        assert bounds[1][1] == pytest.approx(datum.y.max_mm, abs=tol)
        assert bounds[2][0] == pytest.approx(datum.z.min_mm, abs=tol)
        assert bounds[2][1] == pytest.approx(datum.z.max_mm, abs=tol)


def test_plotter_front_faces_aligned_from_built_geometry(transport, datums):
    """D-033 — tier 1 and tier 2 plotter front faces share the same Y."""
    p1_front = datums.plotter1_physical.y.min_mm
    p2_front = datums.plotter2_physical.y.min_mm
    p1_solid = transport.parts["EQUIP-PLOTTER1-001"].solid
    p2_solid = transport.parts["EQUIP-PLOTTER2-001"].solid
    measured_setback = (
        bounding_box_bounds(p2_solid)[1][0] - bounding_box_bounds(p1_solid)[1][0]
    )
    expected_setback = p2_front - p1_front
    assert measured_setback == pytest.approx(expected_setback)
    assert measured_setback == pytest.approx(0.0)


def test_plotter_envelopes_no_3d_intersection_and_z_clearance(params, transport):
    """Governing Cameo 4 envelope (170 mm height) — either machine may occupy either slot."""
    tol = float(params.value("tolerance.assembly_mm"))
    env1 = transport.parts["ENV-PLOTTER1-001"].solid
    env2 = transport.parts["ENV-PLOTTER2-001"].solid
    assert intersection_volume(env1, env2) == pytest.approx(0.0, abs=1e-3)

    b1 = bounding_box_bounds(env1)
    b2 = bounding_box_bounds(env2)
    measured_clearance = b2[2][0] - b1[2][1]
    expected_clearance = params.plotter_envelope_z_clearance_mm
    assert measured_clearance == pytest.approx(expected_clearance, abs=tol)
    assert expected_clearance == pytest.approx(
        float(params.value("plotter.upper_z"))
        - params.tier_envelope_offset_z_mm
        - (
            float(params.value("plotter.lower_z"))
            - params.tier_envelope_offset_z_mm
            + params.tier_envelope_height_mm
        ),
        abs=tol,
    )


def test_organizer_clear_volume(params, transport, datums):
    clear = datums.organizer_clear_volume
    min_w, min_d, min_h = HORIZONTAL_ORGANIZER_CLEAR_MIN_MM
    assert clear.x.size_mm >= min_w
    assert clear.y.size_mm >= min_d
    assert clear.z.size_mm >= min_h

    interior = box_from_bounds(
        clear.x.min_mm,
        clear.y.min_mm,
        clear.z.min_mm,
        clear.x.max_mm,
        clear.y.max_mm,
        clear.z.max_mm,
    )
    allowed = {
        "ORG-FLOOR-001",
        "ORG-INSERT-001",
    }
    for part_id, record in transport.parts.items():
        if part_id in allowed or part_id.startswith("SHELF-"):
            continue
        encroachment = intersection_volume(record.solid, interior)
        assert encroachment == pytest.approx(0.0, abs=1e-3), (
            f"{part_id} encroaches organizer clear volume by {encroachment} mm^3"
        )


MEDIA_PATH_SUPPORT_PARTS = frozenset(
    {
        "MEDIA-SUPPORT-L1-001",
        "MEDIA-SUPPORT-L2-001",
    }
)


def test_tier_clearance_minimum(params):
    """PLT-007/PLT-009 — both plotter tiers meet owner 170 mm minimum bay clearance."""
    p = load_parameters(PARAMETERS_PATH)
    tier_min = float(p.value("plotter.tier_clearance_min_mm"))
    assert p.tier_clearance_lower_mm == pytest.approx(197.0)
    assert p.tier_clearance_upper_mm == pytest.approx(170.0)
    assert p.tier_clearance_lower_mm >= tier_min
    assert p.tier_clearance_upper_mm >= tier_min


def test_horizontal_shelf_regeneration(params):
    """PLT-007 — three shelf dividers for four compartments."""
    state = build_transport_assembly(params)
    assert params.horizontal_shelf_divider_count == 3
    shelf_ids = [
        pid
        for pid in state.parts
        if pid.startswith("SHELF-") and not pid.startswith("SHELF-SUPPORT-")
    ]
    assert len(shelf_ids) == 3
    datums = Datums.from_parameters(params)
    org_z = datums.organizer_floor_top_z_mm
    threshold = float(params.value("tolerance.part_assembly_feature_mm"))
    for shelf_id in shelf_ids:
        shelf = state.parts[shelf_id].solid
        assert shelf.volume > 0
        bounds = bounding_box_bounds(shelf)
        assert bounds[2][0] >= org_z - threshold


def test_film_horizontal_compartment_height(params, transport):
    """PLT-007 — flat film bodies sit in 25 mm clear compartments."""
    p = params
    datums = Datums.from_parameters(p)
    clear_h = float(p.value("film_storage_horizontal.compartment_clear_height_mm"))
    film_t = float(p.value("media_path.test_body_primary.thickness"))
    assert film_t < clear_h
    parts = build_film_body_parts(params, datums, shelf_indices=(0,))
    film = parts[0].solid
    size = bounding_box_size(film)
    assert size[2] == pytest.approx(film_t, abs=0.5)
    for part_id, record in transport.parts.items():
        if part_id.startswith(("SHELF-", "ORG-")):
            continue
        if part_id.startswith(("ENV-", "EQUIP-", "LID-")):
            continue
        encroach = intersection_volume(film, record.solid)
        assert encroach == pytest.approx(0.0, abs=1e-3), (
            f"film body intersects {part_id} by {encroach} mm^3"
        )


MEDIA_SWEEP_PANEL_ALLOW = frozenset(
    {
        "PANEL-OUT-REAR-001",
        "PANEL-IN-REAR-001",
        "PANEL-IN-MID-001",
    }
)

MEDIA_SWEEP_SKIP_PREFIXES = (
    "EQUIP-",
    "ENV-",
    "TRAY-",
    "SLIDE-",
    "VIBMOUNT-",
    "SOFTSTOP-",
    "INTERLOCK-",
    "ADAPTER-",
    "TESTBODY-",
    "LID-",
    "ORG-",
    "SHELF-",
    "LIGHT-",
    "CTRL-",
    "CABLE-",
    "AIRPATH-",
    "COVER-",
    "MAINS-",
    "DOOR-",
)


@pytest.mark.parametrize("body_kind", ["primary", "long"])
@pytest.mark.parametrize("level", ["L1", "L2"])
@pytest.mark.parametrize(
    "y_offset_mm",
    [float(step) for step in range(0, 76, 10)],
)
def test_media_path_body_sweep_no_unintended_contact(
    params, transport, body_kind, level, y_offset_mm
):
    """PLT-007 — media-path test bodies at multiple Y positions without unintended contact."""
    datums = Datums.from_parameters(params)
    threshold = float(params.value("tolerance.part_assembly_feature_mm"))
    prefix = "lower" if level == "L1" else "upper"
    feed_z = float(params.value(f"plotter.{prefix}_z")) + float(
        params.value("plotter.feed_plane_z_provisional_mm")
    )
    clear_w = float(params.value("media_path.clear_width"))
    slot_h = float(params.value("media_path.slot_height_target"))
    cx = datums.case_envelope.x.max_mm / 2
    if level == "L1":
        y_base = datums.plotter1_physical.y.min_mm
    else:
        y_base = datums.plotter2_physical.y.min_mm
    y0 = y_base + y_offset_mm
    if body_kind == "primary":
        d = float(params.value("media_path.test_body_primary.depth"))
    else:
        d = float(params.value("media_path.test_body_long.depth"))
    body = box_from_bounds(
        cx - clear_w / 2,
        y0,
        feed_z - slot_h / 2,
        cx + clear_w / 2,
        y0 + d,
        feed_z + slot_h / 2,
    )
    for part_id, record in transport.parts.items():
        if part_id in MEDIA_PATH_SUPPORT_PARTS or part_id in MEDIA_SWEEP_PANEL_ALLOW:
            continue
        if part_id.startswith(MEDIA_SWEEP_SKIP_PREFIXES):
            continue
        clearance = minimum_clearance(body, record.solid)
        assert clearance >= threshold, (
            f"{body_kind}/{level} at Y+{y_offset_mm}: hits {part_id} "
            f"clearance {clearance:.3f} mm < {threshold} mm"
        )


def test_registry_no_mains_inlet_placeholder_and_no_laptop_monitor_router(params, transport):
    """PLT-013 / D-071 — service-volume placeholders removed; no laptop/monitor/router IDs."""
    assert "MAINS-INLET-001" not in transport.parts
    forbidden = ("laptop", "monitor", "router")
    for part_id in transport.parts:
        lower = part_id.lower()
        assert not any(word in lower for word in forbidden), part_id
        material = transport.parts[part_id].material.lower()
        assert not any(word in material for word in forbidden)


def test_indicative_tip_factor_non_authoritative(params, transport):
    """PLT-010 indicative — NOT authoritative for Gate G4 engineering review."""
    import math

    from stand_cad.geometry.analysis import stability_report_inputs

    minimum = float(params.value("stability.tip_factor_min"))
    parts = transport.parts

    lower = stability_report_inputs(params, parts, extended_level="lower")
    assert lower.applicable
    assert math.isfinite(lower.factor)
    assert lower.factor >= minimum, (
        f"indicative tip factor (lower) {lower.factor:.3f} < {minimum} "
        "(NOT authoritative for Gate G4 — concept-stage estimate only)"
    )

    upper = stability_report_inputs(params, parts, extended_level="upper")
    assert float(params.value("trays.upper_extension")) <= 0.0
    assert not upper.applicable, (
        "upper tier at zero travel (D-076) must not be compared to tip_factor_min"
    )
    assert upper.overturn_moment_n_mm <= 0.0
    assert not math.isfinite(upper.factor)


def test_stability_report_tip_factor_na_wording(tmp_path):
    """FIX-TIP-001 AC-3 — upper@0 report section must not imply inf compliance."""
    import importlib.util
    import sys

    module_path = REPO_ROOT / "scripts" / "generate_mass_report.py"
    spec = importlib.util.spec_from_file_location("generate_mass_report", module_path)
    assert spec is not None and spec.loader is not None
    mass_mod = importlib.util.module_from_spec(spec)
    sys.modules["generate_mass_report"] = mass_mod
    spec.loader.exec_module(mass_mod)

    report_path = tmp_path / "stability_report.md"
    mass_mod.write_stability_report(
        REPO_ROOT / "config" / "parameters.yaml",
        report_path,
    )
    text = report_path.read_text(encoding="utf-8")
    upper_start = text.index("## Upper tray (zero travel / fixed)")
    upper_end = text.index("## Operational media pass-through", upper_start)
    upper_section = text[upper_start:upper_end]

    assert "N/A" in upper_section
    assert "not applicable" in upper_section
    assert "Tip factor: inf" not in upper_section
    assert "(minimum" not in upper_section.split("Tip factor")[1].split("\n")[0]


def test_stability_tip_factor_positive_extension_not_applicable(
    params, transport, monkeypatch, tmp_path
):
    """FIX-TIP-001 F-1/F-5 — extension>0, overturn<=0: not applicable, not zero travel."""
    import importlib.util
    import math
    import sys

    from stand_cad.geometry.analysis import stability_report_inputs

    real_value = params.value

    def patched_value(key: str):
        if key == "trays.upper_extension":
            return 50.0
        return real_value(key)

    monkeypatch.setattr(params, "value", patched_value)
    parts = transport.parts
    report = stability_report_inputs(params, parts, extended_level="upper")
    assert report.extension_mm == 50.0
    assert report.extension_mm > 0.0
    assert report.overturn_moment_n_mm <= 0.0
    assert not report.applicable
    assert not math.isfinite(report.factor)

    module_path = REPO_ROOT / "scripts" / "generate_mass_report.py"
    spec = importlib.util.spec_from_file_location("generate_mass_report", module_path)
    assert spec is not None and spec.loader is not None
    mass_mod = importlib.util.module_from_spec(spec)
    sys.modules["generate_mass_report"] = mass_mod
    spec.loader.exec_module(mass_mod)
    monkeypatch.setattr(mass_mod, "load_parameters", lambda _path: params)

    report_path = tmp_path / "stability_positive_ext_na.md"
    mass_mod.write_stability_report(
        REPO_ROOT / "config" / "parameters.yaml",
        report_path,
    )
    text = report_path.read_text(encoding="utf-8")
    section_start = text.index("## Upper tray extended (tip factor not applicable)")
    section_end = text.index("## Operational media pass-through", section_start)
    upper_section = text[section_start:section_end]

    assert "zero travel" not in upper_section.split("\n", 1)[0]
    assert "Tip factor: inf" not in upper_section
    assert "(minimum" not in upper_section
    assert "non-finite" in upper_section or "insufficient overturn arm" in upper_section


def test_stability_split_mass_conservation(params, transport):
    """PLT-010 D-039 — moving + stationary masses equal total installed system mass."""
    from stand_cad.geometry.analysis import stability_report_inputs

    parts = transport.parts
    structural = sum(
        1
        for _ in (
            stability_report_inputs(params, parts, extended_level="lower"),
            stability_report_inputs(params, parts, extended_level="upper"),
        )
    )
    assert structural == 2
    for level in ("lower", "upper"):
        report = stability_report_inputs(params, parts, extended_level=level)
        split_total = report.moving_mass_kg + report.stationary_mass_kg
        assert split_total == pytest.approx(report.total_mass_kg, rel=1e-6, abs=1e-4)


def test_tray_rail_front_cladding(params, transport):
    """PLT-010 — opal cladding spans rail Z band down to tray bottom (D-068 widen)."""
    from stand_cad.geometry.datums import Datums

    clad_depth = float(params.value("materials.outer_panel_thickness_mm"))
    datums = Datums.from_parameters(params)
    for level in ("LOWER", "UPPER"):
        datum = datums.plotter1_physical if level == "LOWER" else datums.plotter2_physical
        tray_bottom_z = datum.z.min_mm
        for suffix in ("L", "R", "C"):
            rail_id = f"FRAME-RAIL-TRAY-{level}-{suffix}-001"
            clad_id = f"PANEL-CLAD-FRONT-TRAY-{level}-{suffix}-001"
            assert clad_id in transport.parts
            rail = transport.parts[rail_id]
            clad = transport.parts[clad_id]
            assert clad.material == "cast_opal_pmma_3mm"
            assert clad.verify_on_real_machine is False
            rail_bb = bounding_box_bounds(rail.solid)
            clad_bb = bounding_box_bounds(clad.solid)
            for axis in (0,):
                assert clad_bb[axis][0] == pytest.approx(rail_bb[axis][0], abs=0.5)
                assert clad_bb[axis][1] == pytest.approx(rail_bb[axis][1], abs=0.5)
            assert clad_bb[2][0] == pytest.approx(rail_bb[2][0], abs=0.5)
            assert clad_bb[2][1] == pytest.approx(tray_bottom_z, abs=0.5)
            assert clad_bb[1][1] == pytest.approx(rail_bb[1][0] + clad_depth, abs=0.5)
            assert rail_bb[1][0] == pytest.approx(15.0, abs=0.5)
            clad_height = clad_bb[2][1] - clad_bb[2][0]
            assert clad_height == pytest.approx(tray_bottom_z - rail_bb[2][0], abs=0.5)


def test_indicative_tray_deflection_non_authoritative(params):
    """PLT-011 indicative — NOT authoritative for Gate G4 FEA.

    Three-rail model: conservative independent half-span beams (P/2 on L/2).
    """
    deflection = indicative_tray_deflection_mm(params)
    assert deflection > 0
    assert deflection < float("inf")
    span_mm = float(params.value("plotter.physical_width"))
    load_n = float(params.value("trays.design_load_kg")) * 9.80665
    e_mpa = float(params.value("materials.tray_panel_youngs_modulus_mpa"))
    width_mm = float(params.value("plotter.physical_depth"))
    t_mm = params.tray_panel_thickness_mm
    i_mm4 = width_mm * t_mm**3 / 12
    assert deflection == pytest.approx(
        5 * (load_n / 2) * (span_mm / 2) ** 3 / (384 * e_mpa * i_mm4),
        rel=1e-6,
    )


def test_indicative_tray_deflection_meets_tz_ceiling(params):
    """PLT-011 — indicative three-rail model must stay under TZ line 184 ceiling."""
    deflection = indicative_tray_deflection_mm(params)
    ceiling = float(params.value("trays.deflection_max_mm"))
    assert deflection < ceiling, (
        f"indicative tray deflection {deflection:.3f} mm >= {ceiling} mm "
        "(TZ line 184 / trays.deflection_max_mm — regression on three-rail fix)"
    )


def test_indicative_empty_case_mass_non_authoritative(params, transport):
    """PLT-012 indicative — NOT authoritative for Gate G4 mass sign-off."""
    mass = empty_case_mass_kg(transport.parts, params)
    ceiling = float(params.value("mass_targets.empty_case_max_kg"))
    assert mass <= ceiling, (
        f"indicative empty-case mass {mass:.2f} kg > {ceiling} kg "
        "(NOT authoritative for Gate G4 — concept-stage estimate only)"
    )
    assert mass > 0


def test_mass_report_header_honest_excluded_categories(tmp_path, transport):
    """FIX-MASS-001 AC-2 — header must not claim absent categories are physically present."""
    import importlib.util
    import sys

    parts = transport.parts
    absent_prefixes = ("MAINS-INLET", "INTERLOCK-", "EDGEGUARD-")
    for prefix in absent_prefixes:
        assert not any(pid.startswith(prefix) for pid in parts), (
            f"precondition: no {prefix}* in transport after D-046/D-067/D-071"
        )

    module_path = REPO_ROOT / "scripts" / "generate_mass_report.py"
    spec = importlib.util.spec_from_file_location("generate_mass_report", module_path)
    assert spec is not None and spec.loader is not None
    mass_mod = importlib.util.module_from_spec(spec)
    sys.modules["generate_mass_report"] = mass_mod
    spec.loader.exec_module(mass_mod)

    report_path = tmp_path / "mass_report.csv"
    mass_mod.write_mass_report(PARAMETERS_PATH, report_path)
    text = report_path.read_text(encoding="utf-8")
    excluded_line = next(
        line for line in text.splitlines() if "Other excluded categories" in line
    )

    for absent in absent_prefixes:
        assert absent.rstrip("-") not in excluded_line and absent not in excluded_line, (
            f"header must not mention removed category {absent}: {excluded_line}"
        )

    assert "SLIDE" in excluded_line
    assert "VIBMOUNT" in excluded_line
    assert "physically present" in excluded_line


def test_idempotent_rebuild_matching_metrics(params):
    """PLT-016 — two in-process transport builds yield matching bbox/volume."""
    tol = float(params.value("tolerance.part_assembly_feature_mm"))
    s1 = build_transport_assembly(params)
    s2 = build_transport_assembly(params)
    c1 = s1.compound()
    c2 = s2.compound()
    assert bounding_box_size(c1) == pytest.approx(bounding_box_size(c2), abs=tol)
    assert c1.volume == pytest.approx(c2.volume, rel=1e-6)


def test_step_export_readback(params, tmp_path):
    """PLT-015 — exported STEP read-back has non-zero solids and matching bbox."""
    from stand_cad.geometry.export import (
        export_transport_step,
        measure_compound,
        read_back_step_metrics,
    )

    step_path = tmp_path / "tower_ASSEMBLY_CONCEPT_REFERENCE_ONLY_rev1.step"
    export_transport_step(params, step_path)
    assert "CONCEPT" in step_path.name
    assert "REFERENCE_ONLY" in step_path.name
    live = measure_compound(build_transport_assembly(params).compound())
    readback = read_back_step_metrics(step_path)
    assert readback["solid_count"] > 0
    tol = float(params.value("tolerance.assembly_mm"))
    assert readback["bbox_size_mm"] == pytest.approx(live["bbox_size_mm"], abs=tol)


def test_side_slab_single_solid(params, transport):
    """PLT-004 AC-2 — each side slab is one connected solid (no corner-cylinder fragmentation)."""
    for part_id in ("PANEL-OUT-LEFT-001", "PANEL-OUT-RIGHT-001"):
        solid = transport.parts[part_id].solid
        assert len(solid.solids()) == 1, part_id


def test_side_slab_footprint(params, transport, datums):
    """PLT-004 AC-2 — side slabs span full side clearance from foot top to case height."""
    tol = float(params.value("tolerance.part_cnc_laser_mm"))
    foot_h = float(params.value("materials.foot_height_mm"))
    side_clear = (
        float(params.value("case.width")) - float(params.value("case.internal_width"))
    ) / 2
    height = datums.case_envelope.z.max_mm
    for part_id in ("PANEL-OUT-LEFT-001", "PANEL-OUT-RIGHT-001"):
        bounds = bounding_box_bounds(transport.parts[part_id].solid)
        assert bounds[2][1] == pytest.approx(height, abs=tol + 3.5)
        assert bounds[2][0] == pytest.approx(foot_h, abs=tol + 1.0)
        x_size = bounds[0][1] - bounds[0][0]
        assert x_size == pytest.approx(side_clear, abs=tol + 1.0)


def test_frame_contained_in_side_slabs(params, transport):
    """PLT-004 — hidden frame posts/rails stay inside side-slab X footprint."""
    left = transport.parts["PANEL-OUT-LEFT-001"].solid
    right = transport.parts["PANEL-OUT-RIGHT-001"].solid
    side_clear = (
        float(params.value("case.width")) - float(params.value("case.internal_width"))
    ) / 2
    tol = float(params.value("tolerance.part_assembly_feature_mm"))
    for part_id, record in transport.parts.items():
        if not part_id.startswith("FRAME-"):
            continue
        bounds = bounding_box_bounds(record.solid)
        if bounds[0][1] <= side_clear + tol:
            assert minimum_clearance(record.solid, left) < tol or bounds[0][1] <= side_clear
        if bounds[0][0] >= float(params.value("case.width")) - side_clear - tol:
            assert minimum_clearance(record.solid, right) < tol


def test_no_front_outer_panel(params, transport):
    """PLT-004 AC-3 — PANEL-OUT-FRONT-001 removed; plotter zones open at front."""
    assert "PANEL-OUT-FRONT-001" not in transport.parts
    from stand_cad.geometry.primitives import solid_point_state

    datums = Datums.from_parameters(params)
    y_probe = 1.0
    cx = datums.case_envelope.x.max_mm / 2.0
    for envelope in (datums.plotter1_envelope, datums.plotter2_envelope):
        z_mid = (envelope.z.min_mm + envelope.z.max_mm) / 2.0
        blockers = [
            pid
            for pid, rec in transport.parts.items()
            if pid.startswith("PANEL-OUT-")
            and solid_point_state(rec.solid, cx, y_probe, z_mid) in ("IN", "ON")
        ]
        assert not blockers, f"front blocked at z={z_mid}: {blockers}"


def test_transport_exterior_corner_clear_at_r24(params, transport, datums):
    """F-1 — no transport part material within R24 of absolute case corners (corner sweep)."""
    import math

    from stand_cad.geometry.primitives import solid_point_state

    corner_r = float(params.value("case.corner_radius"))
    probe_r = corner_r - 1.0
    width = datums.case_envelope.x.max_mm
    depth = datums.case_envelope.y.max_mm
    panel_top = datums.case_envelope.z.max_mm
    z_heights = [panel_top * 0.25, panel_top * 0.5, panel_top * 0.75]
    corner_specs = (
        ("fl", 0.0, 0.0, 1.0, 1.0),
        ("fr", width, 0.0, -1.0, 1.0),
        ("rl", 0.0, depth, 1.0, -1.0),
        ("rr", width, depth, -1.0, -1.0),
    )
    sweep_angles = tuple(float(angle) for angle in range(0, 91, 5))
    flat_panel_prefixes = ("PANEL-IN-", "PANEL-OUT-", "PANEL-CLAD-FRONT-")
    for name, cx, cy, sx, sy in corner_specs:
        for angle_deg in sweep_angles:
            rad = math.radians(angle_deg)
            x = cx + sx * probe_r * math.cos(rad)
            y = cy + sy * probe_r * math.sin(rad)
            for z in z_heights:
                frame_offenders = [
                    part_id
                    for part_id, record in transport.parts.items()
                    if part_id.startswith("FRAME-")
                    and solid_point_state(record.solid, x, y, z) == "IN"
                ]
                assert not frame_offenders, (
                    f"corner {name} angle={angle_deg} z={z:.1f} "
                    f"point=({x:.2f},{y:.2f}) frame: {frame_offenders}"
                )
                structure_offenders = [
                    part_id
                    for part_id, record in transport.parts.items()
                    if not any(part_id.startswith(prefix) for prefix in flat_panel_prefixes)
                    and solid_point_state(record.solid, x, y, z) == "IN"
                ]
                assert not structure_offenders, (
                    f"corner {name} angle={angle_deg} z={z:.1f} "
                    f"point=({x:.2f},{y:.2f}): {structure_offenders}"
                )


def test_perimeter_base_rails_present(params, transport):
    """D-075 — base ring rails present at four faces (corner posts restored)."""
    for face in ("FRONT", "REAR", "LEFT", "RIGHT"):
        part_id = f"FRAME-RAIL-BASE-{face}-001"
        assert part_id in transport.parts
        bounds = bounding_box_bounds(transport.parts[part_id].solid)
        assert bounds[2][0] == pytest.approx(
            float(params.value("materials.foot_height_mm")), abs=0.5
        )


def test_organizer_front_open(params, transport, datums):
    """PLT-007 — no outer front panel; horizontal shelves present above organizer floor."""
    assert "PANEL-OUT-FRONT-001" not in transport.parts
    org = datums.organizer_clear_volume
    z_base = datums.organizer_floor_top_z_mm + params.org_insert_thickness_mm
    shelf = transport.parts["SHELF-000"].solid
    shelf_probe = box_from_bounds(
        (org.x.min_mm + org.x.max_mm) / 2 - 5,
        org.y.min_mm + 5,
        z_base + float(params.value("film_storage_horizontal.compartment_clear_height_mm")) - 2,
        (org.x.min_mm + org.x.max_mm) / 2 + 5,
        org.y.min_mm + 15,
        z_base
        + float(params.value("film_storage_horizontal.compartment_clear_height_mm"))
        + 2,
    )
    assert intersection_volume(shelf_probe, shelf) > 0


def test_rear_media_feed_slots(params, transport, datums):
    """PLT-003 addendum — two rear feed slots at provisional feed-plane Z bands."""
    from stand_cad.geometry.panels import _feed_plane_z
    from stand_cad.geometry.primitives import solid_point_state

    rear = transport.parts["PANEL-OUT-REAR-001"].solid
    rear_inner = transport.parts["PANEL-IN-REAR-001"].solid
    depth = datums.case_envelope.y.max_mm
    thickness = float(params.value("materials.outer_panel_thickness_mm"))
    inner_t = float(params.value("materials.inner_panel_thickness_mm"))
    gap = float(params.value("materials.outer_panel_shadow_gap_mm"))
    slot_w = float(params.value("media_path.clear_width"))
    slot_h = float(params.value("media_path.slot_height_target"))
    cx = datums.case_envelope.x.max_mm / 2.0
    y_mid = depth - thickness / 2.0
    y_inner_mid = depth - gap - inner_t / 2.0

    for level in ("L1", "L2"):
        feed_z = _feed_plane_z(params, level)
        assert solid_point_state(rear, cx, y_mid, feed_z) == "OUT"
        assert solid_point_state(rear, cx, y_mid, feed_z + slot_h / 2.0 + 5.0) == "IN"
        assert solid_point_state(rear, cx + slot_w / 2.0 + 5.0, y_mid, feed_z) == "IN"
        assert solid_point_state(rear_inner, cx, y_inner_mid, feed_z) == "OUT"
        assert solid_point_state(rear_inner, cx + slot_w / 2.0 + 5.0, y_inner_mid, feed_z) == "IN"


def test_rear_media_channel_clear_of_obstructions(params, transport, datums):
    """D-046 — 450×10 mm rear exit channel free of solids from plotter rear to beyond rear wall."""
    from stand_cad.geometry.panels import _feed_plane_z

    clear_w = float(params.value("media_path.clear_width"))
    slot_h = float(params.value("media_path.slot_height_target"))
    cx = datums.case_envelope.x.max_mm / 2.0
    y_step = 20.0
    min_clearances: dict[str, float] = {}

    for level in ("L1", "L2"):
        feed_z = _feed_plane_z(params, level)
        plotter = datums.plotter1_physical if level == "L1" else datums.plotter2_physical
        y_start = plotter.y.max_mm
        y_end = datums.case_envelope.y.max_mm + 20.0
        support_id = f"MEDIA-SUPPORT-{level}-001"
        level_min = float("inf")

        y = y_start
        while y <= y_end:
            probe = box_from_bounds(
                cx - clear_w / 2,
                y,
                feed_z - slot_h / 2,
                cx + clear_w / 2,
                y + y_step,
                feed_z + slot_h / 2,
            )
            for part_id, record in transport.parts.items():
                if part_id == support_id:
                    continue
                if part_id in MEDIA_SWEEP_PANEL_ALLOW:
                    continue
                if part_id.startswith(MEDIA_SWEEP_SKIP_PREFIXES):
                    continue
                encroach = intersection_volume(probe, record.solid)
                assert encroach == pytest.approx(0.0, abs=1e-3), (
                    f"{level} Y={y:.1f}: {part_id} encroaches channel by {encroach} mm^3"
                )
                clearance = minimum_clearance(probe, record.solid)
                if clearance < level_min:
                    level_min = clearance
            y += y_step

        min_clearances[level] = level_min
        assert level_min < float("inf")

    print(
        f"rear_media_channel_min_clearance_mm L1={min_clearances['L1']:.3f} "
        f"L2={min_clearances['L2']:.3f}"
    )


def test_handle_cutout_dimensions(params, transport, datums):
    """PLT-004 — 110×35 mm rounded through-cut on each side slab."""
    from stand_cad.geometry.panels import handle_cutout_footprint
    from stand_cad.geometry.primitives import solid_point_state

    grip_len = float(params.value("hardware.handle_grip_length_mm"))
    grip_depth = float(params.value("hardware.handle_grip_depth_mm"))
    width = datums.case_envelope.x.max_mm

    for side in ("left", "right"):
        part_id = f"PANEL-OUT-{side.upper()}-001"
        panel = transport.parts[part_id].solid
        fp = handle_cutout_footprint(params, datums, side=side)
        mount_z = (fp["z0"] + fp["z1"]) / 2
        y_center = (fp["y0"] + fp["y1"]) / 2
        x_probe = 0.0 if side == "left" else width
        assert solid_point_state(panel, x_probe, y_center, mount_z) == "OUT"
        assert solid_point_state(panel, x_probe, y_center - grip_len / 4, mount_z) == "OUT"
        assert solid_point_state(panel, x_probe, y_center, mount_z - grip_depth / 4) == "OUT"
        wall = float(params.value("materials.outer_panel_thickness_mm"))
        x_solid = wall / 2 if side == "left" else width - wall / 2
        assert solid_point_state(panel, x_solid, y_center + grip_len / 2 + 5, mount_z) == "IN"
        assert solid_point_state(panel, x_solid, fp["y0"] + 0.5, fp["z0"] + 0.5) == "IN"


def test_handle_cutout_sightline_clear(params, transport, datums):
    """PLT-005 F-1 — full-width through-ray grid clear of every other registered part."""
    from stand_cad.geometry.panels import (
        handle_cutout_footprint,
        handle_cutout_through_ray_x_bounds,
    )

    threshold = float(params.value("tolerance.part_assembly_feature_mm"))
    y_steps = 5
    z_steps = 5
    x_steps = 13
    for side in ("left", "right"):
        part_id = f"PANEL-OUT-{side.upper()}-001"
        panel_solid = transport.parts[part_id].solid
        fp = handle_cutout_footprint(params, datums, side=side)
        x_min, x_max = handle_cutout_through_ray_x_bounds(params, datums, side=side)
        for yi in range(y_steps):
            y = fp["y0"] + (fp["y1"] - fp["y0"]) * (yi + 0.5) / y_steps
            for zi in range(z_steps):
                z = fp["z0"] + (fp["z1"] - fp["z0"]) * (zi + 0.5) / z_steps
                for xi in range(x_steps):
                    x = x_min + (x_max - x_min) * (xi + 0.5) / x_steps
                    probe = box_from_bounds(x - 0.5, y - 0.5, z - 0.5, x + 0.5, y + 0.5, z + 0.5)
                    for other_id, record in transport.parts.items():
                        if other_id == part_id:
                            continue
                        if other_id.startswith(("ENV-", "EQUIP-", "LID-")):
                            continue
                        vol = intersection_volume(probe, record.solid)
                        assert vol <= threshold, (
                            f"{part_id} handle grid ({x:.1f},{y:.1f},{z:.1f}) "
                            f"blocked by {other_id}: {vol:.3f} mm^3"
                        )
                    assert intersection_volume(probe, panel_solid) <= threshold


def test_no_top_structure_lid(params, transport):
    """PLT-004 AC-4 — TOP-STRUCTURE-001 removed; organizer top is open."""
    assert "TOP-STRUCTURE-001" not in transport.parts


def test_organizer_top_open(params, transport, datums):
    """PLT-004 AC-4 — no lid over organizer clear volume."""
    org = datums.organizer_clear_volume
    lid_offenders = [
        part_id
        for part_id, record in transport.parts.items()
        if part_id.startswith("PANEL-OUT-") or part_id.startswith("TOP-")
    ]
    probe = box_from_bounds(
        org.x.min_mm + 5,
        org.y.min_mm + 5,
        org.z.max_mm - 10,
        org.x.max_mm - 5,
        org.y.max_mm - 5,
        datums.case_envelope.z.max_mm,
    )
    for part_id in lid_offenders:
        vol = intersection_volume(probe, transport.parts[part_id].solid)
        assert vol == pytest.approx(0.0, abs=1e-3), f"{part_id} covers organizer top"


def test_shelf_divider_count_formula(params):
    """PLT-007 — shelf_count=4 → three horizontal SHELF-* dividers."""
    shelf_count = int(params.value("film_storage_horizontal.shelf_count"))
    assert params.horizontal_shelf_divider_count == shelf_count - 1
    assert params.horizontal_shelf_divider_count == 3
    transport = build_transport_assembly(params)
    shelves = [
        pid
        for pid in transport.parts
        if pid.startswith("SHELF-") and not pid.startswith("SHELF-SUPPORT-")
    ]
    assert len(shelves) == params.horizontal_shelf_divider_count


def test_bottom_vent_slots(params, transport, datums):
    """PLT-004 AC-5 — bottom panel vent slots are real through-cuts under AIRPATH footprint."""
    from stand_cad.geometry.primitives import solid_point_state

    bottom = transport.parts["PANEL-IN-BOTTOM-001"].solid
    width = datums.case_envelope.x.max_mm
    depth = datums.case_envelope.y.max_mm
    gap = float(params.value("materials.outer_panel_shadow_gap_mm"))
    ap_d = float(params.value("services.airpath_depth_mm"))
    foot_h = float(params.value("materials.foot_height_mm"))
    inner_t = float(params.value("materials.inner_panel_thickness_mm"))
    cy = depth - gap - ap_d / 2.0
    cx = width / 2.0
    slot_w = float(params.value("hardware.vent_slot_width_mm"))
    slot_h = float(params.value("hardware.vent_slot_height_mm"))
    pitch = float(params.value("hardware.vent_slot_pitch_mm"))
    count = int(params.value("hardware.vent_slot_count"))
    z_mid = foot_h + inner_t / 2
    probe = box_from_bounds(
        cx - 1,
        cy - 1,
        z_mid - 1,
        cx + 1,
        cy + 1,
        z_mid + 1,
    )
    assert intersection_volume(probe, bottom) == pytest.approx(0.0, abs=1e-3)
    solid_probe = box_from_bounds(
        cx - slot_w / 4,
        cy - slot_h / 4,
        foot_h + 0.5,
        cx + slot_w / 4,
        cy + slot_h / 4,
        foot_h + inner_t - 0.5,
    )
    assert intersection_volume(solid_probe, bottom) == pytest.approx(0.0, abs=1e-3)
    total_span = count * slot_w + (count - 1) * pitch
    x_start = cx - total_span / 2.0
    between_x = x_start + slot_w + pitch / 2.0
    assert solid_point_state(bottom, between_x, cy, z_mid) == "IN"


def test_shelf_dimensions(params, transport):
    """PLT-007 — horizontal shelf spans organizer clear width × depth."""
    shelf = transport.parts["SHELF-000"].solid
    bounds = bounding_box_bounds(shelf)
    tol = float(params.value("tolerance.part_cnc_laser_mm"))
    divider_t = float(params.value("film_storage_horizontal.divider_thickness"))
    clear_w = float(params.value("film_storage_horizontal.clear_width"))
    clear_d = float(params.value("film_storage_horizontal.clear_depth"))
    org_x = float(params.value("film_storage_horizontal.x"))
    org_y = float(params.value("film_storage_horizontal.y"))
    size = bounding_box_size(shelf)
    assert size[0] == pytest.approx(clear_w, abs=tol)
    assert size[1] == pytest.approx(clear_d, abs=tol)
    assert size[2] == pytest.approx(divider_t, abs=tol)
    assert bounds[0][0] == pytest.approx(org_x, abs=tol)
    assert bounds[1][0] == pytest.approx(org_y, abs=tol)


def test_film_body_count_all_shelves(params):
    """PLT-007 — default film bodies cover every horizontal shelf compartment."""
    datums = Datums.from_parameters(params)
    shelf_count = int(params.value("film_storage_horizontal.shelf_count"))
    parts = build_film_body_parts(params, datums)
    assert len(parts) == shelf_count
    assert all(record.material == "film_sheet_reference" for record in parts)


@pytest.mark.parametrize("shelf_index", list(range(4)))
def test_film_bodies_no_adjacent_intersection(params, shelf_index):
    """PLT-007 — flat film sheets do not intersect neighbouring film bodies."""
    state = build_organizer_loaded_assembly(params)
    film_id = f"FILM-BODY-{shelf_index:03d}"
    assert film_id in state.parts
    film = state.parts[film_id].solid
    threshold = float(params.value("tolerance.part_assembly_feature_mm"))
    for part_id, record in state.parts.items():
        if not part_id.startswith("FILM-BODY-") or part_id == film_id:
            continue
        encroach = intersection_volume(film, record.solid)
        assert encroach <= threshold, f"{film_id} intersects {part_id} by {encroach} mm^3"


@pytest.mark.parametrize("shelf_index", list(range(4)))
@pytest.mark.parametrize(
    "withdrawal_mm",
    [float(step) for step in range(0, 351, 10)],
)
def test_film_body_front_withdrawal_clears_front_tray_cladding(
    params, shelf_index, withdrawal_mm
):
    """PLT-007 — film front withdrawal must not intersect tray front cladding strips."""
    state = build_organizer_loaded_assembly(params)
    film_id = f"FILM-BODY-{shelf_index:03d}"
    assert film_id in state.parts
    moved = translate_solid(
        state.parts[film_id].solid,
        dy=-withdrawal_mm,
    )
    for part_id, record in state.parts.items():
        if not part_id.startswith("PANEL-CLAD-FRONT-TRAY-"):
            continue
        vol = intersection_volume(moved, record.solid)
        assert vol == pytest.approx(0.0, abs=1e-3), (
            f"{film_id} withdrawn {withdrawal_mm} mm hits {part_id} by {vol} mm^3"
        )


def test_film_bodies_span_sheet_depth_across_width(params):
    """PLT-007 — 500 mm nominal sheet edge along X from org left; margin to right wall."""
    datums = Datums.from_parameters(params)
    org_x = float(params.value("film_storage_horizontal.x"))
    sheet_span_x = float(params.value("film_storage_horizontal.sheet_depth_mm"))
    clear_w = float(params.value("film_storage_horizontal.clear_width"))
    parts = build_film_body_parts(params, datums)
    first = parts[0]
    bounds = bounding_box_bounds(first.solid)
    assert bounds[0][0] == pytest.approx(org_x, abs=0.5)
    assert bounds[0][1] == pytest.approx(org_x + sheet_span_x, abs=0.5)
    assert org_x + clear_w - (org_x + sheet_span_x) == pytest.approx(110.0)


def test_handle_mount_y_at_loaded_com(params, transport):
    """D-051 — grip Y tracks indicative loaded-case CoM for level carry (not geometric centre)."""
    com_tol = float(params.value("tolerance.part_assembly_feature_mm"))
    com = loaded_case_centre_of_mass_mm(transport.parts, params)
    handle_y = float(params.value("hardware.handle_mount_y_mm"))
    assert handle_y == pytest.approx(com[1], abs=com_tol), (
        f"handle_mount_y_mm ({handle_y}) must track loaded CoM Y ({com[1]:.3f} mm) "
        f"within {com_tol} mm — update config when layout/depth changes"
    )
    # Geometric depth centre retained (D-050 reference) — owner chose CoM over this value.
    depth_centre = params.computed_geometric_depth_centre_y_mm
    assert depth_centre == pytest.approx(float(params.value("case.depth")) / 2.0)
    assert depth_centre == pytest.approx(210.0)
    assert handle_y != pytest.approx(depth_centre, abs=1.0)


def test_handle_tier2_finger_intrusion_at_balance_point(params, transport):
    """D-051 — through-cutout grip overlaps tier-2 plotter bay; owner deferred handle concept."""
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
    assert intrusion > 0.0
    assert intrusion == pytest.approx(1_502_833.5, rel=1e-4)
    geom_y = params.computed_geometric_depth_centre_y_mm
    geom_intrusion = handle_finger_intrusion_volume_mm3(
        handle_mount_y_mm=geom_y,
        handle_mount_z_mm=handle_z,
        grip_length_mm=grip_len,
        grip_depth_mm=grip_depth,
        plotter_y_bounds=(y_bounds[0], y_bounds[1]),
        plotter_z_bounds=(z_bounds[0], z_bounds[1]),
        plotter_x_span_mm=pw,
    )
    assert geom_intrusion == pytest.approx(987_525.0, rel=1e-4)


def test_handle_clears_tier1_trays_slides(params, transport, datums):
    """D-051 — balance-point grip still clears tier-1 plotter, trays, and slide hardware."""
    from stand_cad.geometry.panels import handle_cutout_footprint

    handle_y = float(params.value("hardware.handle_mount_y_mm"))
    handle_z = float(params.value("hardware.handle_mount_z_mm"))
    grip_len = float(params.value("hardware.handle_grip_length_mm"))
    grip_depth = float(params.value("hardware.handle_grip_depth_mm"))
    pw = float(params.value("plotter.physical_width"))
    p1 = transport.parts["EQUIP-PLOTTER1-001"].solid
    _, y1_bounds, z1_bounds = bounding_box_bounds(p1)
    tier1_intrusion = handle_finger_intrusion_volume_mm3(
        handle_mount_y_mm=handle_y,
        handle_mount_z_mm=handle_z,
        grip_length_mm=grip_len,
        grip_depth_mm=grip_depth,
        plotter_y_bounds=(y1_bounds[0], y1_bounds[1]),
        plotter_z_bounds=(z1_bounds[0], z1_bounds[1]),
        plotter_x_span_mm=pw,
    )
    assert tier1_intrusion == pytest.approx(0.0, abs=1e-3)
    fp = handle_cutout_footprint(params, datums, side="right")
    handle_probe = box_from_bounds(
        fp["x0"] - 1,
        fp["y0"],
        fp["z0"],
        fp["x1"] + 1,
        fp["y1"],
        fp["z1"],
    )
    tol = float(params.value("tolerance.part_assembly_feature_mm"))
    for part_id, record in transport.parts.items():
        if not (
            part_id.startswith(("TRAY-", "SLIDE-"))
            or part_id.startswith("FRAME-RAIL-TRAY-")
        ):
            continue
        vol = intersection_volume(handle_probe, record.solid)
        assert vol <= tol, f"{part_id} intersects handle grip by {vol:.3f} mm^3"


def test_handle_mount_z_lowest_sightline_feasible(params):
    """D-050 — handle Z at lowest sightline-feasible band above tier-2 stack."""
    upper_z = float(params.value("plotter.upper_z"))
    slide_h = float(params.value("trays.slide_rail_height_mm"))
    expected = params.computed_handle_mount_z_mm
    assert expected == pytest.approx(upper_z + slide_h + 2.0)
    assert float(params.value("hardware.handle_mount_z_mm")) == pytest.approx(expected)
    assert expected == pytest.approx(263.0)
    assert expected < params.side_panel_centre_z_mm


def test_vertical_organizer_rightmost_cell_boundary_arithmetic(params):
    """D-031 — vertical cell 9 bounded by org floor at X=630, not missing divider."""
    org_x = float(params.value("film_storage_horizontal.x"))
    clear_w = float(params.value("film_storage_horizontal.clear_width"))
    cells = 10
    divider_t = float(params.value("materials.divider_thickness_mm"))
    cell_w = (clear_w - (cells - 1) * divider_t) / cells
    assert cell_w == pytest.approx(59.2)
    cell9_x_min = org_x + 9 * (cell_w + divider_t)
    cell9_x_max = cell9_x_min + cell_w
    assert cell9_x_max == pytest.approx(org_x + clear_w)
    assert cell9_x_max == pytest.approx(630.0)


def test_horizontal_organizer_compartments_bounded_by_walls(params, transport):
    """D-031 — horizontal floor/shelves span to X=630 with explicit right wall."""
    org_x = float(params.value("film_storage_horizontal.x"))
    clear_w = float(params.value("film_storage_horizontal.clear_width"))
    width = float(params.value("case.width"))
    side_clear = params.side_slab_thickness_mm
    right_inner_x = width - side_clear
    floor_bounds = bounding_box_bounds(transport.parts["ORG-FLOOR-001"].solid)
    assert floor_bounds[0][1] == pytest.approx(org_x + clear_w)
    assert org_x + clear_w == pytest.approx(right_inner_x)
    for part_id in ("ORG-INSERT-001", "SHELF-000", "SHELF-001", "SHELF-002"):
        bounds = bounding_box_bounds(transport.parts[part_id].solid)
        assert bounds[0][1] == pytest.approx(org_x + clear_w)


def test_side_slab_bullnose_radius(params):
    """PLT-006 — R10 full bullnose on exterior front vertical + top edges (Main ruling)."""
    from stand_cad.geometry.panels import (
        achieved_side_slab_front_bullnose_radius_mm,
        achieved_side_slab_top_bullnose_radius_mm,
        side_slab_bullnose_radius_mm,
    )

    configured = side_slab_bullnose_radius_mm(params)
    front = achieved_side_slab_front_bullnose_radius_mm(params)
    top = achieved_side_slab_top_bullnose_radius_mm(params)
    width = float(params.value("case.width"))
    internal = float(params.value("case.internal_width"))
    side_clear = (width - internal) / 2
    assert side_clear == pytest.approx(20.0)
    assert configured == pytest.approx(10.0)
    assert front == pytest.approx(9.9, abs=0.15)
    assert top == pytest.approx(9.9, abs=0.15)


def test_frame_front_rail_cladding(params, transport):
    """D-069/D-044 — BASE/ORG front cladding removed; top-front rail still absent."""
    for prefix in ("BASE", "ORG"):
        assert f"PANEL-CLAD-FRONT-{prefix}-001" not in transport.parts
    tray_clad = [pid for pid in transport.parts if pid.startswith("PANEL-CLAD-FRONT-TRAY-")]
    assert len(tray_clad) == 6
    assert "FRAME-RAIL-TOP-FRONT-001" not in transport.parts
    assert "PANEL-CLAD-FRONT-TOP-001" not in transport.parts
    for part_id in (
        "FRAME-RAIL-TOP-LEFT-001",
        "FRAME-RAIL-TOP-RIGHT-001",
        "FRAME-RAIL-TOP-REAR-001",
    ):
        assert part_id in transport.parts


def test_top_warm_member_is_light_strip(params, transport, datums):
    """PLT-006/007 AC-C4 — warm top bar is LIGHT-STRIP-001 under TOP-REAR rail (D-059)."""
    light = transport.parts["LIGHT-STRIP-001"]
    rail = transport.parts["FRAME-RAIL-TOP-REAR-001"]
    shelf = transport.parts["SHELF-002"]
    light_bb = bounding_box_bounds(light.solid)
    shelf_bb = bounding_box_bounds(shelf.solid)
    case_h = float(params.value("case.height"))
    profile = float(params.value("materials.frame_profile_size_mm"))
    rail_bottom_z = datums.top_structure.z.min_mm - profile
    (_lx0, _lx1), (_ly_min, _ly1), (lz_min, lz_max) = light_bb
    (_sx0, _sx1), (_sy_min, _sy1), (sz_min, sz_max) = shelf_bb
    assert lz_max == pytest.approx(rail_bottom_z, abs=1.0)
    assert lz_max <= case_h + 0.01
    assert intersection_volume(light.solid, rail.solid) == pytest.approx(0.0, abs=1.0)
    assert sz_max < datums.organizer_floor_top_z_mm + params.horizontal_shelf_stack_height_mm
    assert light.material == "service_volume"
    assert shelf.material == "transparent_petg_2mm"
    assert lz_min >= rail_bottom_z - float(params.value("services.light_strip_height_mm")) - 1.0
    assert sz_max < lz_min


def test_rear_vent_slots_grid(params, transport, datums):
    """PLT-005 Finding 5 — grid probe through rear vent slot centers (real through-cuts)."""
    rear = transport.parts["PANEL-OUT-REAR-001"].solid
    band_z = float(params.value("hardware.vent_band_z_mm"))
    slot_w = float(params.value("hardware.vent_slot_width_mm"))
    slot_h = float(params.value("hardware.vent_slot_height_mm"))
    pitch = float(params.value("hardware.vent_slot_pitch_mm"))
    count = int(params.value("hardware.vent_slot_count"))
    width = datums.case_envelope.x.max_mm
    depth = datums.case_envelope.y.max_mm
    cx = width / 2.0
    total_span = count * slot_w + (count - 1) * pitch
    x_start = cx - total_span / 2.0
    y_mid = depth - 1.5
    for index in range(count):
        slot_cx = x_start + index * (slot_w + pitch) + slot_w / 2.0
        for yi in range(3):
            y = y_mid + (yi - 1) * 0.5
            for zi in range(3):
                z = band_z + (zi - 1) * (slot_h / 4.0)
                probe = box_from_bounds(
                    slot_cx - 0.5, y - 0.5, z - 0.5, slot_cx + 0.5, y + 0.5, z + 0.5
                )
                assert intersection_volume(probe, rear) == pytest.approx(0.0, abs=1e-3)


def test_rear_vent_slots(params, transport, datums):
    """Finding 5 — rear panel vent slot cutouts exist at slot centers."""
    rear = transport.parts["PANEL-OUT-REAR-001"].solid
    band_z = float(params.value("hardware.vent_band_z_mm"))
    slot_w = float(params.value("hardware.vent_slot_width_mm"))
    slot_h = float(params.value("hardware.vent_slot_height_mm"))
    width = datums.case_envelope.x.max_mm
    cx = width / 2.0
    probe = box_from_bounds(
        cx - 1,
        datums.case_envelope.y.max_mm - 2,
        band_z - 1,
        cx + 1,
        datums.case_envelope.y.max_mm + 2,
        band_z + 1,
    )
    assert intersection_volume(probe, rear) == pytest.approx(0.0, abs=1e-3)
    solid_probe = box_from_bounds(
        cx - slot_w / 4,
        datums.case_envelope.y.max_mm - 4,
        band_z - slot_h / 4,
        cx + slot_w / 4,
        datums.case_envelope.y.max_mm + 1,
        band_z + slot_h / 4,
    )
    assert intersection_volume(solid_probe, rear) == pytest.approx(0.0, abs=1e-3)


def test_cable_passthrough_through_cut(params, transport, datums):
    """D-047 — right side panel has a real through-cut for the cable pass-through."""
    from stand_cad.geometry.panels import cable_passthrough_footprint

    fp = cable_passthrough_footprint(params, datums)
    cy = (fp["y0"] + fp["y1"]) / 2
    cz = (fp["z0"] + fp["z1"]) / 2
    probe = box_from_bounds(fp["x0"] - 1, cy - 1, cz - 1, fp["x1"] + 1, cy + 1, cz + 1)
    solid = transport.parts["PANEL-OUT-RIGHT-001"].solid
    assert intersection_volume(probe, solid) == pytest.approx(0.0, abs=1e-3)


def test_cable_passthrough_bore_clear(params, transport, datums):
    """D-047 — the grommet has a real open bore; a probe passes cleanly through it."""
    from stand_cad.geometry.panels import cable_passthrough_footprint

    grommet = transport.parts["SVC-CABLE-PASSTHROUGH-001"].solid
    fp = cable_passthrough_footprint(params, datums)
    cy = (fp["y0"] + fp["y1"]) / 2
    cz = (fp["z0"] + fp["z1"]) / 2
    probe = box_from_bounds(fp["x0"] - 1, cy - 1, cz - 1, fp["x1"] + 1, cy + 1, cz + 1)
    assert intersection_volume(probe, grommet) == pytest.approx(0.0, abs=1e-3)


def test_cable_passthrough_registered(params, transport):
    """D-036 — stable part ID, material, and verify-on-real-machine marker."""
    record = transport.parts["SVC-CABLE-PASSTHROUGH-001"]
    assert record.material == "soft_trim_brush"
    assert record.verify_on_real_machine is True


def test_cable_passthrough_grommet_clears_neighbours(params, transport):
    """D-047 — SVC-CABLE-PASSTHROUGH-001 clears USB service port and distant neighbours."""
    tol = float(params.value("tolerance.part_assembly_feature_mm"))
    grommet = transport.parts["SVC-CABLE-PASSTHROUGH-001"].solid
    port_w = float(params.value("hardware.service_port_cutout_width_mm"))
    port_h = float(params.value("hardware.service_port_cutout_height_mm"))
    port_y = float(params.value("hardware.service_port_mount_y_mm"))
    port_z = float(params.value("hardware.service_port_mount_z_mm"))
    port_probe = box_from_bounds(
        600,
        port_y - port_w / 2,
        port_z - port_h / 2,
        700,
        port_y + port_w / 2,
        port_z + port_h / 2,
    )
    clearance = minimum_clearance(grommet, port_probe)
    assert clearance >= tol, f"USB service port clearance {clearance:.3f} < {tol} mm"
    for neighbour_id in (
        "MEDIA-SUPPORT-L1-001",
        "MEDIA-SUPPORT-L2-001",
        "LIGHT-STRIP-001",
    ):
        neighbour = transport.parts[neighbour_id].solid
        neighbour_clearance = minimum_clearance(grommet, neighbour)
        assert neighbour_clearance >= tol, (
            f"{neighbour_id} clearance {neighbour_clearance:.3f} < {tol} mm"
        )


def test_cable_passthrough_clears_handle_cutout(params, transport, datums):
    """D-050 — cable pass-through and handle grip volume maintain mutual clearance."""
    from stand_cad.geometry.panels import cable_passthrough_footprint, handle_cutout_footprint

    tol = float(params.value("tolerance.part_assembly_feature_mm"))
    grommet = transport.parts["SVC-CABLE-PASSTHROUGH-001"].solid
    handle_fp = handle_cutout_footprint(params, datums, side="right")
    handle_probe = box_from_bounds(
        handle_fp["x0"] - 1,
        handle_fp["y0"],
        handle_fp["z0"],
        handle_fp["x1"] + 1,
        handle_fp["y1"],
        handle_fp["z1"],
    )
    assert minimum_clearance(grommet, handle_probe) >= tol
    cable_fp = cable_passthrough_footprint(params, datums)
    cable_probe = box_from_bounds(
        cable_fp["x0"] - 1,
        cable_fp["y0"],
        cable_fp["z0"],
        cable_fp["x1"] + 1,
        cable_fp["y1"],
        cable_fp["z1"],
    )
    assert minimum_clearance(handle_probe, cable_probe) >= tol


def test_feet_cylindrical_volume(params, transport):
    """Finding 5 — feet are cylinders matching diameter semantics."""
    import math

    diameter = float(params.value("hardware.foot_diameter_mm"))
    height = float(params.value("materials.foot_height_mm"))
    radius = diameter / 2.0
    expected = math.pi * radius**2 * height
    tol = float(params.value("tolerance.part_cnc_laser_mm"))
    foot = transport.parts["FOOT-001"].solid
    assert foot.volume == pytest.approx(expected, abs=height * tol)


def test_corner_posts_emitted(params, transport):
    """D-075 — four FRAME-POST-* corner posts in transport assembly."""
    expected = {
        "FRAME-POST-FL-001",
        "FRAME-POST-FR-001",
        "FRAME-POST-RL-001",
        "FRAME-POST-RR-001",
    }
    post_ids = {pid for pid in transport.parts if pid.startswith("FRAME-POST-")}
    assert post_ids == expected


def test_foot_mates_base_rails_at_foot_top(params, transport):
    """PLT-005 F-2 — feet mate base perimeter rails at foot top (D-075 posts restored)."""
    from stand_cad.geometry.collision import is_foot_structure_contact

    foot_h = float(params.value("materials.foot_height_mm"))
    threshold = float(params.value("tolerance.part_assembly_feature_mm"))
    base_rails = (
        "FRAME-RAIL-BASE-FRONT-001",
        "FRAME-RAIL-BASE-LEFT-001",
        "FRAME-RAIL-BASE-RIGHT-001",
        "FRAME-RAIL-BASE-REAR-001",
    )
    mated = [
        rail_id
        for rail_id in base_rails
        if is_foot_structure_contact("FOOT-001", rail_id, transport.parts, threshold)
    ]
    assert len(mated) >= 2, f"FOOT-001 must mate at least two base rails, got {mated}"
    foot_band = box_from_bounds(0, 0, 0, 650, 420, foot_h)
    for rail_id in base_rails:
        rail = transport.parts[rail_id].solid
        assert intersection_volume(foot_band, rail) == pytest.approx(0.0, abs=1e-3)


def test_is_foot_structure_contact_rejects_floor_post_interpenetration(params, transport):
    """PLT-005 F-2 — old Z=0 post/foot overlap is not waved through as a mate."""
    from stand_cad.geometry.collision import is_foot_structure_contact
    from stand_cad.geometry.registry import PartRecord

    threshold = float(params.value("tolerance.part_assembly_feature_mm"))
    foot = transport.parts["FOOT-001"]
    legacy_post = PartRecord(
        part_id="FRAME-POST-FL-001-LEGACY",
        material="aluminium_angle_15x15x1.5",
        solid=box_from_bounds(0.0, 0.0, 0.0, 40.0, 40.0, 675.0),
    )
    parts = {foot.part_id: foot, legacy_post.part_id: legacy_post}
    assert not is_foot_structure_contact(
        foot.part_id, legacy_post.part_id, parts, threshold
    )


def test_side_slab_cavity_joint_base_rails_still_exempt(params, transport):
    """SWE-003 / D-075 — base side rails ↔ side slabs remain legitimate bearing joints."""
    from stand_cad.geometry.collision import (
        _max_legitimate_skin_bearing_volume_mm3,
        is_side_slab_frame_cavity_joint,
    )

    threshold = float(params.value("tolerance.part_assembly_feature_mm"))
    pairs = (
        ("FRAME-RAIL-BASE-LEFT-001", "PANEL-OUT-LEFT-001"),
        ("FRAME-RAIL-BASE-RIGHT-001", "PANEL-OUT-RIGHT-001"),
    )
    for frame_id, panel_id in pairs:
        panel = transport.parts[panel_id]
        frame = transport.parts[frame_id]
        inter_vol = intersection_volume(panel.solid, frame.solid)
        panel_bounds = bounding_box_bounds(panel.solid)
        max_bearing = _max_legitimate_skin_bearing_volume_mm3(
            params, panel_bounds, frame_id
        )
        assert inter_vol < max_bearing + threshold
        assert minimum_clearance(panel.solid, frame.solid) == pytest.approx(0.0, abs=1e-3)
        assert is_side_slab_frame_cavity_joint(
            frame_id, panel_id, transport.parts, params, threshold
        )


def test_side_slab_cavity_joint_rejects_mid_wall_post_y_gate(params, transport):
    """SWE-003 — mid-wall post with inter_vol below max_bearing must not exempt (Y gate)."""
    from stand_cad.geometry.collision import (
        _max_legitimate_skin_bearing_volume_mm3,
        is_side_slab_frame_cavity_joint,
    )
    from stand_cad.geometry.registry import PartRecord

    threshold = float(params.value("tolerance.part_assembly_feature_mm"))
    panel_id = "PANEL-OUT-LEFT-001"
    frame_id = "FRAME-POST-FL-001"
    panel = transport.parts[panel_id]
    panel_bounds = bounding_box_bounds(panel.solid)
    foot_h = float(params.value("materials.foot_height_mm"))
    mid_post = PartRecord(
        part_id=frame_id,
        material="aluminium_angle_15x15x1.5",
        solid=box_from_bounds(0.0, 150.0, foot_h, 40.0, 170.0, foot_h + 50.0),
    )
    parts = dict(transport.parts)
    parts[frame_id] = mid_post
    inter_vol = intersection_volume(panel.solid, mid_post.solid)
    max_bearing = _max_legitimate_skin_bearing_volume_mm3(
        params, panel_bounds, frame_id
    )
    assert inter_vol < max_bearing
    assert minimum_clearance(panel.solid, mid_post.solid) == pytest.approx(0.0, abs=1e-3)
    assert not is_side_slab_frame_cavity_joint(
        frame_id, panel_id, parts, params, threshold
    )


def test_side_slab_cavity_joint_rejects_solid_fill_burial(params, transport):
    """SWE-003 — solid side-slab fill at corner (~428×10³ mm³) exceeds max_bearing."""
    from stand_cad.geometry.collision import (
        _max_legitimate_skin_bearing_volume_mm3,
        is_side_slab_frame_cavity_joint,
    )
    from stand_cad.geometry.registry import PartRecord

    threshold = float(params.value("tolerance.part_assembly_feature_mm"))
    depth = float(params.value("case.depth"))
    side_clear = params.side_slab_thickness_mm
    panel_id = "PANEL-OUT-LEFT-001"
    frame_id = "FRAME-RAIL-BASE-LEFT-001"
    panel_bounds = bounding_box_bounds(transport.parts[panel_id].solid)
    foot_h = float(params.value("materials.foot_height_mm"))
    z_top = panel_bounds[2][1]
    solid_panel = PartRecord(
        part_id=panel_id,
        material="cast_opal_pmma_3mm",
        solid=box_from_bounds(0.0, 0.0, foot_h, side_clear, depth, z_top),
    )
    corner_post = PartRecord(
        part_id=frame_id,
        material="aluminium_angle_15x15x1.5",
        solid=box_from_bounds(0.0, 0.0, foot_h, 40.0, 40.0, z_top),
    )
    parts = {panel_id: solid_panel, frame_id: corner_post}
    inter_vol = intersection_volume(solid_panel.solid, corner_post.solid)
    max_bearing = _max_legitimate_skin_bearing_volume_mm3(
        params, panel_bounds, frame_id
    )
    assert inter_vol == pytest.approx(422_559.0, rel=0.01)
    assert inter_vol > max_bearing + threshold
    assert not is_side_slab_frame_cavity_joint(
        frame_id, panel_id, parts, params, threshold
    )


def test_side_slab_meets_rear_panel(params, transport, datums):
    """PLT-004 — side slab rear edge meets rear outer panel (shared corner joint)."""
    gap = float(params.value("materials.outer_panel_shadow_gap_mm"))
    tol = float(params.value("tolerance.part_assembly_feature_mm"))
    depth = datums.case_envelope.y.max_mm
    left = transport.parts["PANEL-OUT-LEFT-001"].solid
    rear = transport.parts["PANEL-OUT-REAR-001"].solid
    left_bounds = bounding_box_bounds(left)
    assert left_bounds[1][1] == pytest.approx(depth - gap, abs=tol + 0.5)
    assert minimum_clearance(left, rear) < tol


def test_storage_state_does_not_claim_356mm_travel(params):
    """Closed niche is storage — 356 mm Silhouette travel clearance not required."""
    required = float(params.value("operational.material_travel_clearance_mm"))
    assert params.material_travel_clearance_front_mm(1) == pytest.approx(15.0)
    assert params.material_travel_clearance_front_mm(1) < required


def test_cutting_extended_tray_front_clearance_below_manufacturer_minimum(params):
    """Full tray extension — front travel clearance still below 356 mm at case.depth=420."""
    required = float(params.value("operational.material_travel_clearance_mm"))
    lower_ext = float(params.value("trays.lower_extension"))
    front = params.material_travel_clearance_front_mm(1, tray_extension_mm=lower_ext)
    assert front == pytest.approx(-235.0)
    assert front < required
    rear = params.material_travel_clearance_rear_mm(1, tray_extension_mm=lower_ext)
    assert rear == pytest.approx(460.0)
    assert rear >= required


def test_pass_through_depth_exceeds_case_envelope(params):
    """Open front-to-rear pass-through needs 907 mm — case.depth 420 mm cannot close."""
    required = params.pass_through_depth_required_mm()
    assert required == pytest.approx(907.0)
    depth = float(params.value("case.depth"))
    assert depth < required


def test_tier_y_clearances_aligned_front_faces(params):
    """D-033 — tier 2 front face aligned with tier 1; setback removed, owner 2026-08-04."""
    lower_y = float(params.value("plotter.lower_y"))
    upper_y = float(params.value("plotter.upper_y"))
    depth = float(params.value("plotter.physical_depth"))
    case_depth = float(params.value("case.depth"))
    assert upper_y == pytest.approx(lower_y)
    assert float(params.value("plotter.upper_setback")) == pytest.approx(0.0)
    assert params.material_travel_clearance_front_mm(1) == pytest.approx(15.0)
    assert params.material_travel_clearance_rear_mm(2) == pytest.approx(210.0)
    assert lower_y + depth <= case_depth
    assert upper_y + depth <= case_depth


def test_operating_state_front_rear_pass_through_open(params):
    """PLT-007 — front opening and rear feed slots stay open in operating state."""
    from stand_cad.geometry.panels import _feed_plane_z
    from stand_cad.geometry.primitives import solid_point_state

    state = build_operating_with_test_bodies_assembly(params)
    datums = Datums.from_parameters(params)
    rear = state.parts["PANEL-OUT-REAR-001"].solid
    width = datums.case_envelope.x.max_mm
    depth = datums.case_envelope.y.max_mm
    cx = width / 2.0
    slot_w = float(params.value("media_path.clear_width"))
    slot_h = float(params.value("media_path.slot_height_target"))
    gap = float(params.value("materials.outer_panel_shadow_gap_mm"))
    thickness = float(params.value("materials.outer_panel_thickness_mm"))
    y_rear_mid = depth - gap - thickness / 2

    for level in ("L1", "L2"):
        feed_z = _feed_plane_z(params, level)
        assert solid_point_state(rear, cx, y_rear_mid, feed_z) == "OUT"
        assert solid_point_state(rear, cx - slot_w / 2 + 1, y_rear_mid, feed_z) == "OUT"
        assert solid_point_state(rear, cx + slot_w / 2 - 1, y_rear_mid, feed_z) == "OUT"
        assert solid_point_state(rear, cx, y_rear_mid, feed_z - slot_h / 2 + 1) == "OUT"
        assert solid_point_state(rear, cx, y_rear_mid, feed_z + slot_h / 2 - 1) == "OUT"

        y_front = 1.0
        blockers = [
            pid
            for pid, rec in state.parts.items()
            if pid.startswith("PANEL-OUT-")
            and solid_point_state(rec.solid, cx, y_front, feed_z) in ("IN", "ON")
        ]
        assert not blockers, f"{level} front pass-through blocked by {blockers}"


def test_service_port_cutout_on_right_panel(params, transport):
    """PLT-007 — provisional USB service port through-cut at documented Y/Z on right slab."""
    from stand_cad.geometry.primitives import solid_point_state

    panel = transport.parts["PANEL-OUT-RIGHT-001"].solid
    width = float(params.value("case.width"))
    side_clear = params.side_slab_thickness_mm
    wall_mm = float(params.value("materials.outer_panel_thickness_mm"))
    port_y = float(params.value("hardware.service_port_mount_y_mm"))
    port_z = float(params.value("hardware.service_port_mount_z_mm"))
    handle_y = float(params.value("hardware.handle_mount_y_mm"))
    grip_len = float(params.value("hardware.handle_grip_length_mm"))
    port_w = float(params.value("hardware.service_port_cutout_width_mm"))
    x1 = width
    x_exterior = x1 - wall_mm / 2
    x_cavity = width - side_clear / 2
    assert port_y == pytest.approx(275.0)
    port_aft_margin = port_y - port_w / 2 - (handle_y + grip_len / 2)
    assert port_aft_margin >= 12.0
    assert port_aft_margin == pytest.approx(30.7, abs=0.5)
    # Outer 3 mm skin: port centre is open; solid skin remains above the cutout.
    assert solid_point_state(panel, x_exterior, port_y, port_z) == "OUT"
    assert solid_point_state(panel, x_exterior, port_y, port_z + 20) == "IN"
    # Cavity void plus through-cut gives a connector path at mid-depth (not solid acrylic).
    assert solid_point_state(panel, x_cavity, port_y, port_z) == "OUT"


def test_validation_evidence_not_older_than_parameters():
    """D-040 — validation evidence under rev{CONCEPT_REVISION} must follow parameters.yaml."""
    from stand_cad.geometry.export import CONCEPT_REVISION

    evidence_dir = REPO_ROOT / "output" / "validation" / f"rev{CONCEPT_REVISION}"
    if not evidence_dir.is_dir():
        pytest.skip(
            f"no validation evidence at {evidence_dir} — run scripts/regenerate.py first"
        )

    params_mtime = PARAMETERS_PATH.stat().st_mtime
    evidence_files = [path for path in evidence_dir.rglob("*") if path.is_file()]
    assert evidence_files, f"validation directory {evidence_dir} contains no files"
    newest_mtime = max(path.stat().st_mtime for path in evidence_files)
    newest_path = max(evidence_files, key=lambda path: path.stat().st_mtime)
    assert newest_mtime >= params_mtime, (
        f"newest evidence {newest_path.relative_to(REPO_ROOT)} "
        f"(mtime {newest_mtime}) is older than {PARAMETERS_PATH} (mtime {params_mtime}); "
        "run scripts/regenerate.py"
    )


def test_case_height_540_after_d089(params, transport):
    """D-058/D-089 — case.height 540 mm after Path A +11 mm stack."""
    tol = float(params.value("tolerance.assembly_mm"))
    cap_t = float(params.value("stacking.cap_thickness_mm"))
    assert float(params.value("case.height")) == pytest.approx(540.0)
    assert float(params.value("top_structure.height_mm")) == pytest.approx(0.0)
    size = bounding_box_size(transport.compound())
    assert size[2] == pytest.approx(540.0 + cap_t, abs=tol)


def test_light_strip_below_roofline_d059(params, transport):
    """D-059 — LIGHT-STRIP-001 must not protrude above case.height."""
    case_h = float(params.value("case.height"))
    _, _, (_z0, z1) = bounding_box_bounds(transport.parts["LIGHT-STRIP-001"].solid)
    assert z1 <= case_h + 0.01
    for neighbor in (
        "FRAME-RAIL-TOP-REAR-001",
        "PANEL-OUT-REAR-001",
    ):
        vol = intersection_volume(
            transport.parts["LIGHT-STRIP-001"].solid,
            transport.parts[neighbor].solid,
        )
        assert vol == pytest.approx(0.0, abs=1.0), f"LIGHT-STRIP vs {neighbor}: {vol} mm³"


def test_shelf_supports_bear_on_side_panels(params, transport):
    """D-059 — SHELF-SUPPORT-* closes gap with zero clearance to panel + shelf."""
    from stand_cad.geometry.primitives import minimum_clearance

    pairs = (
        ("SHELF-SUPPORT-L-000", "PANEL-OUT-LEFT-001", "SHELF-000"),
        ("SHELF-SUPPORT-R-000", "PANEL-OUT-RIGHT-001", "SHELF-000"),
        ("SHELF-SUPPORT-L-002", "PANEL-OUT-LEFT-001", "SHELF-002"),
        ("SHELF-SUPPORT-R-002", "PANEL-OUT-RIGHT-001", "SHELF-002"),
    )
    for support_id, panel_id, shelf_id in pairs:
        assert minimum_clearance(
            transport.parts[support_id].solid,
            transport.parts[panel_id].solid,
        ) == pytest.approx(0.0, abs=0.01)
        assert minimum_clearance(
            transport.parts[support_id].solid,
            transport.parts[shelf_id].solid,
        ) == pytest.approx(0.0, abs=0.01)


def test_side_slab_rear_vertical_bullnose(params, transport):
    """D-059 — rear exterior vertical edge filleted like front."""
    left = transport.parts["PANEL-OUT-LEFT-001"].solid
    width = float(params.value("case.width"))
    case_h = float(params.value("case.height"))
    depth = float(params.value("case.depth"))
    rear_probe = box_from_bounds(0.0, depth - 2.0, 0.0, 2.0, depth, min(20.0, case_h))
    front_probe = box_from_bounds(width - 2.0, 0.0, 0.0, width, 2.0, min(20.0, case_h))
    rear_vol = intersection_volume(rear_probe, left)
    front_vol = intersection_volume(front_probe, left)
    assert rear_vol < rear_probe.volume * 0.95
    assert front_vol < front_probe.volume * 0.95
    assert abs(rear_vol - front_vol) < rear_probe.volume * 0.15


def test_transport_display_hides_plotter_boxes_but_mass_path_keeps_them(params):
    """D-072 — display filter is display-only; mass analysis uses full transport assembly."""
    mass_source = (REPO_ROOT / "scripts" / "generate_mass_report.py").read_text(encoding="utf-8")
    full = build_transport_assembly(params)
    display = build_transport_display_assembly(params)
    assert any(pid.startswith("EQUIP-PLOTTER") for pid in full.parts)
    assert not any(pid.startswith("EQUIP-PLOTTER") for pid in display.parts)
    assert "build_transport_display_assembly" not in mass_source
    assert "build_transport_assembly" in mass_source


def test_doors_present_in_transport(params, transport):
    """D-073 — piano-hinge doors emitted closed in transport state."""
    assert "DOOR-LOWER-001" in transport.parts
    assert "DOOR-UPPER-001" in transport.parts
    assert transport.parts["DOOR-LOWER-001"].material == "cast_opal_pmma_3mm"


def test_tray1_quick_access_opens_lower_door(params, tray1_quick_access):
    """D-076 — quick-access state opens lower door with struts present."""
    assert "DOOR-LOWER-001" in tray1_quick_access.parts
    assert "DOOR-STRUT-LOWER-L-001" in tray1_quick_access.parts
    assert "DOOR-STRUT-LOWER-R-001" in tray1_quick_access.parts


def test_door_mate_allows_closed_plane_contact(params, transport):
    """F-1 — closed-door front-plane mates stay exempt at zero intersection volume."""
    from stand_cad.geometry.collision import DOOR_FRONT_PLANE_MAX_BEARING_MM3, is_door_mate

    threshold = float(params.value("tolerance.part_assembly_feature_mm"))
    door_id = "DOOR-LOWER-001"
    for mate_id in ("TRAY-LOWER-001", "SLIDE-LOWER-LEFT-001", "EQUIP-PLOTTER1-001"):
        inter_vol = intersection_volume(
            transport.parts[door_id].solid,
            transport.parts[mate_id].solid,
        )
        assert inter_vol <= DOOR_FRONT_PLANE_MAX_BEARING_MM3 + threshold
        assert is_door_mate(door_id, mate_id, transport.parts, threshold)


def test_door_mate_rejects_volumetric_burial(params, transport):
    """F-1 — synthetic large burial must not pass is_door_mate (pattern: cavity-joint ceiling)."""
    from stand_cad.geometry.collision import DOOR_FRONT_PLANE_MAX_BEARING_MM3, is_door_mate
    from stand_cad.geometry.registry import PartRecord

    threshold = float(params.value("tolerance.part_assembly_feature_mm"))
    door_id = "DOOR-LOWER-001"
    slide_id = "SLIDE-LOWER-LEFT-001"
    slide = transport.parts[slide_id]
    slide_bounds = bounding_box_bounds(slide.solid)
    buried_door = PartRecord(
        part_id=door_id,
        material="cast_opal_pmma_3mm",
        solid=box_from_bounds(
            slide_bounds[0][0],
            slide_bounds[1][0],
            slide_bounds[2][0],
            slide_bounds[0][1],
            slide_bounds[1][1] + 50.0,
            slide_bounds[2][1],
        ),
    )
    parts = dict(transport.parts)
    parts[door_id] = buried_door
    inter_vol = intersection_volume(buried_door.solid, slide.solid)
    assert inter_vol > DOOR_FRONT_PLANE_MAX_BEARING_MM3 + threshold
    assert inter_vol > 20_000.0
    assert not is_door_mate(door_id, slide_id, parts, threshold)


def test_door_mate_allows_closed_plane_contact_with_mid_panel(params, transport):
    """FIX-COLL-002 AC-1 — live closed-door ↔ mid panel stays under front-plane ceiling."""
    from stand_cad.geometry.collision import DOOR_FRONT_PLANE_MAX_BEARING_MM3, is_door_mate

    threshold = float(params.value("tolerance.part_assembly_feature_mm"))
    door_id = "DOOR-LOWER-001"
    mid_id = "PANEL-IN-MID-001"
    inter_vol = intersection_volume(
        transport.parts[door_id].solid,
        transport.parts[mid_id].solid,
    )
    assert inter_vol <= DOOR_FRONT_PLANE_MAX_BEARING_MM3 + threshold
    assert is_door_mate(door_id, mid_id, transport.parts, threshold)


def test_door_mate_rejects_mid_panel_volumetric_burial(params, transport):
    """FIX-COLL-002 AC-1 — synthetic deep door↔mid burial must not pass is_door_mate."""
    from stand_cad.geometry.collision import DOOR_FRONT_PLANE_MAX_BEARING_MM3, is_door_mate
    from stand_cad.geometry.registry import PartRecord

    threshold = float(params.value("tolerance.part_assembly_feature_mm"))
    door_id = "DOOR-LOWER-001"
    mid_id = "PANEL-IN-MID-001"
    mid = transport.parts[mid_id]
    mid_bounds = bounding_box_bounds(mid.solid)
    buried_door = PartRecord(
        part_id=door_id,
        material="cast_opal_pmma_3mm",
        solid=box_from_bounds(
            mid_bounds[0][0],
            mid_bounds[1][0] - 10.0,
            mid_bounds[2][0] - 5.0,
            mid_bounds[0][1],
            mid_bounds[1][1] + 30.0,
            mid_bounds[2][1] + 5.0,
        ),
    )
    parts = dict(transport.parts)
    parts[door_id] = buried_door
    inter_vol = intersection_volume(buried_door.solid, mid.solid)
    assert inter_vol > DOOR_FRONT_PLANE_MAX_BEARING_MM3 + threshold
    assert inter_vol > 5_000.0
    assert not is_door_mate(door_id, mid_id, parts, threshold)


def test_door_mate_rejects_softstop_volumetric_burial(params, transport):
    """FIX-COLL-002 AC-1 — synthetic deep door↔softstop burial must not pass is_door_mate."""
    from stand_cad.geometry.collision import DOOR_FRONT_PLANE_MAX_BEARING_MM3, is_door_mate
    from stand_cad.geometry.registry import PartRecord

    threshold = float(params.value("tolerance.part_assembly_feature_mm"))
    door_id = "DOOR-LOWER-001"
    soft_id = "SOFTSTOP-LOWER-001"
    soft = transport.parts[soft_id]
    soft_bounds = bounding_box_bounds(soft.solid)
    buried_door = PartRecord(
        part_id=door_id,
        material="cast_opal_pmma_3mm",
        solid=box_from_bounds(
            soft_bounds[0][0],
            soft_bounds[1][0] - 5.0,
            soft_bounds[2][0] - 5.0,
            soft_bounds[0][1],
            soft_bounds[1][1] + 40.0,
            soft_bounds[2][1] + 40.0,
        ),
    )
    parts = dict(transport.parts)
    parts[door_id] = buried_door
    inter_vol = intersection_volume(buried_door.solid, soft.solid)
    assert inter_vol > DOOR_FRONT_PLANE_MAX_BEARING_MM3 + threshold
    assert not is_door_mate(door_id, soft_id, parts, threshold)


def test_door_mate_open_door_rejects_tray_burial(params, service_p1):
    """F-2 — open horizontal door must not use closed-plane 500 mm³ ceiling vs tray/slide."""
    from stand_cad.geometry.collision import (
        _door_is_open_horizontal,
        is_door_mate,
    )
    from stand_cad.geometry.registry import PartRecord

    threshold = float(params.value("tolerance.part_assembly_feature_mm"))
    door_id = "DOOR-LOWER-001"
    slide_id = "SLIDE-LOWER-LEFT-001"
    open_door = service_p1.parts[door_id]
    assert _door_is_open_horizontal(open_door.solid, threshold=threshold)
    slide = service_p1.parts[slide_id]
    slide_bounds = bounding_box_bounds(slide.solid)
    buried_open = PartRecord(
        part_id=door_id,
        material=open_door.material,
        solid=box_from_bounds(
            slide_bounds[0][0],
            slide_bounds[1][0],
            slide_bounds[2][0],
            slide_bounds[0][1],
            slide_bounds[1][1] + 30.0,
            slide_bounds[2][1] + 5.0,
        ),
    )
    parts = dict(service_p1.parts)
    parts[door_id] = buried_open
    inter_vol = intersection_volume(buried_open.solid, slide.solid)
    assert inter_vol > threshold
    assert not is_door_mate(door_id, slide_id, parts, threshold)


def test_open_door_clears_base_front_rail_notch(params, service_p1):
    """FIX-COLL-005 — open door clears BASE-FRONT via notch (not allowlist)."""
    from stand_cad.geometry.collision import (
        _door_is_open_horizontal,
        check_collision_pairs,
        is_door_mate,
    )

    threshold = float(params.value("tolerance.part_assembly_feature_mm"))
    door_id = "DOOR-LOWER-001"
    rail_id = "FRAME-RAIL-BASE-FRONT-001"
    door = service_p1.parts[door_id]
    rail = service_p1.parts[rail_id]
    assert _door_is_open_horizontal(door.solid, threshold=threshold)
    inter_vol = intersection_volume(door.solid, rail.solid)
    assert inter_vol <= threshold
    assert inter_vol < 26_000.0
    assert is_door_mate(door_id, rail_id, service_p1.parts, threshold)
    violations = check_collision_pairs(service_p1.parts, params, "service_p1")
    assert not any(door_id in msg and rail_id in msg for msg in violations)


def test_open_door_mate_rejects_base_front_volumetric_burial(params, service_p1):
    """FIX-COLL-005 — synthetic open-door burial into BASE-FRONT must not pass is_door_mate."""
    from stand_cad.geometry.collision import (
        DOOR_FRONT_PLANE_MAX_BEARING_MM3,
        _door_is_open_horizontal,
        is_door_mate,
    )
    from stand_cad.geometry.registry import PartRecord

    threshold = float(params.value("tolerance.part_assembly_feature_mm"))
    door_id = "DOOR-LOWER-001"
    rail_id = "FRAME-RAIL-BASE-FRONT-001"
    open_door = service_p1.parts[door_id]
    assert _door_is_open_horizontal(open_door.solid, threshold=threshold)
    rail_bounds = bounding_box_bounds(service_p1.parts[rail_id].solid)
    buried_open = PartRecord(
        part_id=door_id,
        material=open_door.material,
        solid=box_from_bounds(
            rail_bounds[0][0],
            rail_bounds[1][0],
            rail_bounds[2][0],
            rail_bounds[0][1],
            rail_bounds[1][1] + 40.0,
            rail_bounds[2][1] + 8.0,
        ),
    )
    parts = dict(service_p1.parts)
    parts[door_id] = buried_open
    inter_vol = intersection_volume(buried_open.solid, service_p1.parts[rail_id].solid)
    assert inter_vol > DOOR_FRONT_PLANE_MAX_BEARING_MM3 + threshold
    assert inter_vol > 20_000.0
    assert not is_door_mate(door_id, rail_id, parts, threshold)


def test_open_door_clears_bottom_panel_notch(params, service_p1):
    """FIX-COLL-005 D-089 — settled open door clears PANEL-IN-BOTTOM front pocket."""
    from stand_cad.geometry.collision import _door_is_open_horizontal, check_collision_pairs

    threshold = float(params.value("tolerance.part_assembly_feature_mm"))
    door_id = "DOOR-LOWER-001"
    panel_id = "PANEL-IN-BOTTOM-001"
    door = service_p1.parts[door_id]
    panel = service_p1.parts[panel_id]
    assert _door_is_open_horizontal(door.solid, threshold=threshold)
    inter_vol = intersection_volume(door.solid, panel.solid)
    assert inter_vol <= threshold
    assert inter_vol < 26_000.0
    assert minimum_clearance(door.solid, panel.solid) >= threshold
    violations = check_collision_pairs(service_p1.parts, params, "service_p1")
    assert not any(door_id in msg and panel_id in msg for msg in violations)


def test_door_mate_open_door_rejects_mid_panel_burial(params, service_p1):
    """FIX-COLL-002 F-3 — open horizontal door must not use closed-plane ceiling vs mid panel."""
    from stand_cad.geometry.collision import _door_is_open_horizontal, is_door_mate
    from stand_cad.geometry.registry import PartRecord

    threshold = float(params.value("tolerance.part_assembly_feature_mm"))
    door_id = "DOOR-LOWER-001"
    mid_id = "PANEL-IN-MID-001"
    open_door = service_p1.parts[door_id]
    assert _door_is_open_horizontal(open_door.solid, threshold=threshold)
    mid = service_p1.parts[mid_id]
    mid_bounds = bounding_box_bounds(mid.solid)
    buried_open = PartRecord(
        part_id=door_id,
        material=open_door.material,
        solid=box_from_bounds(
            mid_bounds[0][0],
            mid_bounds[1][0] - 5.0,
            mid_bounds[2][0] - 5.0,
            mid_bounds[0][1],
            mid_bounds[1][1] + 30.0,
            mid_bounds[2][1] + 5.0,
        ),
    )
    parts = dict(service_p1.parts)
    parts[door_id] = buried_open
    inter_vol = intersection_volume(buried_open.solid, mid.solid)
    assert inter_vol > threshold
    assert not is_door_mate(door_id, mid_id, parts, threshold)


def test_door_mate_open_door_rejects_softstop_burial(params, service_p1):
    """FIX-COLL-002 F-3 — open horizontal door must not use closed-plane ceiling vs softstop."""
    from stand_cad.geometry.collision import _door_is_open_horizontal, is_door_mate
    from stand_cad.geometry.registry import PartRecord

    threshold = float(params.value("tolerance.part_assembly_feature_mm"))
    door_id = "DOOR-LOWER-001"
    soft_id = "SOFTSTOP-LOWER-001"
    open_door = service_p1.parts[door_id]
    assert _door_is_open_horizontal(open_door.solid, threshold=threshold)
    soft = service_p1.parts[soft_id]
    soft_bounds = bounding_box_bounds(soft.solid)
    buried_open = PartRecord(
        part_id=door_id,
        material=open_door.material,
        solid=box_from_bounds(
            soft_bounds[0][0],
            soft_bounds[1][0] - 5.0,
            soft_bounds[2][0] - 5.0,
            soft_bounds[0][1],
            soft_bounds[1][1] + 30.0,
            soft_bounds[2][1] + 5.0,
        ),
    )
    parts = dict(service_p1.parts)
    parts[door_id] = buried_open
    inter_vol = intersection_volume(buried_open.solid, soft.solid)
    assert inter_vol > threshold
    assert not is_door_mate(door_id, soft_id, parts, threshold)


def test_strut_mate_rejects_volumetric_burial(params, service_p1):
    """F-3 — strut ↔ post/panel bearing capped; large burial rejected."""
    from stand_cad.geometry.collision import DOOR_STRUT_MAX_BEARING_MM3, is_door_mate
    from stand_cad.geometry.primitives import box_from_bounds
    from stand_cad.geometry.registry import PartRecord

    threshold = float(params.value("tolerance.part_assembly_feature_mm"))
    strut_id = "DOOR-STRUT-LOWER-L-001"
    post_id = "FRAME-POST-FL-001"
    strut = service_p1.parts[strut_id]
    post = service_p1.parts[post_id]
    post_bounds = bounding_box_bounds(post.solid)
    buried_strut = PartRecord(
        part_id=strut_id,
        material=strut.material,
        solid=box_from_bounds(
            post_bounds[0][0],
            post_bounds[1][0],
            post_bounds[2][0],
            post_bounds[0][1] + 40.0,
            post_bounds[1][1] + 40.0,
            post_bounds[2][1] + 40.0,
        ),
    )
    parts = dict(service_p1.parts)
    parts[strut_id] = buried_strut
    inter_vol = intersection_volume(buried_strut.solid, post.solid)
    assert inter_vol > DOOR_STRUT_MAX_BEARING_MM3 + threshold
    assert not is_door_mate(strut_id, post_id, parts, threshold)
    # Live attachment stays under ceiling.
    assert is_door_mate(
        strut_id, post_id, service_p1.parts, threshold
    )


def test_open_front_kinematic_contact_rejects_volumetric_burial(params, transport):
    """FIX-COLL-001 — synthetic rail burial must not pass open-front or is_mating."""
    from stand_cad.geometry.collision import (
        OPEN_FRONT_MAX_BEARING_MM3,
        is_mating,
        is_open_front_kinematic_contact,
    )
    from stand_cad.geometry.registry import PartRecord

    threshold = float(params.value("tolerance.part_assembly_feature_mm"))
    rail_id = "FRAME-RAIL-BASE-FRONT-001"
    equip_id = "EQUIP-PLOTTER1-001"
    equip = transport.parts[equip_id]
    equip_bounds = bounding_box_bounds(equip.solid)
    rail = transport.parts[rail_id]
    buried_rail = PartRecord(
        part_id=rail_id,
        material=rail.material,
        solid=box_from_bounds(
            equip_bounds[0][0],
            equip_bounds[1][0],
            equip_bounds[2][0],
            equip_bounds[0][1],
            equip_bounds[1][1] + 50.0,
            equip_bounds[2][1],
        ),
    )
    parts = dict(transport.parts)
    parts[rail_id] = buried_rail
    inter_vol = intersection_volume(buried_rail.solid, equip.solid)
    assert inter_vol > OPEN_FRONT_MAX_BEARING_MM3 + threshold
    assert inter_vol > 20_000.0
    assert not is_open_front_kinematic_contact(rail_id, equip_id, parts, threshold)
    assert not is_mating(rail_id, equip_id, parts, threshold=threshold, params=params)


def test_open_front_penetrating_rejects_volumetric_burial(params, transport):
    """FIX-COLL-001 AC-3 — front penetrating pattern must reject deep burial."""
    from stand_cad.geometry.collision import (
        OPEN_FRONT_MAX_BEARING_MM3,
        is_mating,
        is_open_front_kinematic_contact,
        is_penetrating_structural_joint,
    )
    from stand_cad.geometry.registry import PartRecord

    threshold = float(params.value("tolerance.part_assembly_feature_mm"))
    clad_id = "PANEL-CLAD-FRONT-TRAY-LOWER-L-001"
    slide_id = "SLIDE-LOWER-LEFT-001"
    slide = transport.parts[slide_id]
    slide_bounds = bounding_box_bounds(slide.solid)
    clad = transport.parts[clad_id]
    buried_clad = PartRecord(
        part_id=clad_id,
        material=clad.material,
        solid=box_from_bounds(
            slide_bounds[0][0],
            slide_bounds[1][0],
            slide_bounds[2][0],
            slide_bounds[0][1],
            slide_bounds[1][1] + 50.0,
            slide_bounds[2][1],
        ),
    )
    parts = dict(transport.parts)
    parts[clad_id] = buried_clad
    inter_vol = intersection_volume(buried_clad.solid, slide.solid)
    assert inter_vol > OPEN_FRONT_MAX_BEARING_MM3 + threshold
    assert inter_vol > 20_000.0
    assert not is_penetrating_structural_joint(clad_id, slide_id, parts, threshold)
    assert not is_open_front_kinematic_contact(clad_id, slide_id, parts, threshold)
    assert not is_mating(clad_id, slide_id, parts, threshold=threshold, params=params)


def test_org_rear_penetrating_rejects_volumetric_burial(params, transport):
    """FIX-COLL-007 AC-2 — ORG-REAR penetrating pattern must reject deep burial."""
    from stand_cad.geometry.collision import (
        ORG_REAR_PENETRATING_MAX_BEARING_MM3,
        is_mating,
        is_penetrating_structural_joint,
    )
    from stand_cad.geometry.registry import PartRecord

    threshold = float(params.value("tolerance.part_assembly_feature_mm"))
    rail_id = "FRAME-RAIL-ORG-REAR-001"
    panel_id = "PANEL-IN-REAR-001"
    panel = transport.parts[panel_id]
    panel_bounds = bounding_box_bounds(panel.solid)
    rail = transport.parts[rail_id]
    # Offset overlap — volumetric burial without coplanar AABB face
    # (avoids PANEL-IN-/FRAME- share_face path).
    buried_rail = PartRecord(
        part_id=rail_id,
        material=rail.material,
        solid=box_from_bounds(
            panel_bounds[0][0] + 2.0,
            panel_bounds[1][0] + 2.0,
            panel_bounds[2][0] + 2.0,
            panel_bounds[0][0] + 200.0,
            panel_bounds[1][0] + 200.0,
            panel_bounds[2][0] + 200.0,
        ),
    )
    parts = dict(transport.parts)
    parts[rail_id] = buried_rail
    inter_vol = intersection_volume(buried_rail.solid, panel.solid)
    assert inter_vol > ORG_REAR_PENETRATING_MAX_BEARING_MM3 + threshold
    assert inter_vol > 40_000.0
    assert not is_penetrating_structural_joint(rail_id, panel_id, parts, threshold)
    assert not is_mating(rail_id, panel_id, parts, threshold=threshold, params=params)


def test_org_rear_share_face_burial_rejects_volumetric_burial(params, transport):
    """FIX-COLL-007 cycle 2 F-1 — coplanar-face ORG-REAR burial must not silent-green."""
    from stand_cad.geometry.collision import (
        ORG_REAR_PENETRATING_MAX_BEARING_MM3,
        aabb_share_face,
        is_mating,
        is_penetrating_structural_joint,
    )
    from stand_cad.geometry.registry import PartRecord

    threshold = float(params.value("tolerance.part_assembly_feature_mm"))
    rail_id = "FRAME-RAIL-ORG-REAR-001"
    panel_id = "PANEL-IN-REAR-001"
    panel = transport.parts[panel_id]
    panel_bounds = bounding_box_bounds(panel.solid)
    rail = transport.parts[rail_id]
    buried_rail = PartRecord(
        part_id=rail_id,
        material=rail.material,
        solid=box_from_bounds(
            panel_bounds[0][0],
            panel_bounds[1][0],
            panel_bounds[2][0],
            panel_bounds[0][1],
            panel_bounds[1][1] + 50.0,
            panel_bounds[2][1],
        ),
    )
    parts = dict(transport.parts)
    parts[rail_id] = buried_rail
    inter_vol = intersection_volume(buried_rail.solid, panel.solid)
    assert aabb_share_face(buried_rail.solid, panel.solid, threshold)
    assert inter_vol > ORG_REAR_PENETRATING_MAX_BEARING_MM3 + threshold
    assert inter_vol > 40_000.0
    assert not is_penetrating_structural_joint(rail_id, panel_id, parts, threshold)
    assert not is_mating(rail_id, panel_id, parts, threshold=threshold, params=params)


def test_org_rear_penetrating_live_mate_passes(params, transport):
    """FIX-COLL-007 AC-1 — live ORG-REAR intersection stays under class ceiling."""
    from stand_cad.geometry.collision import (
        ORG_REAR_PENETRATING_MAX_BEARING_MM3,
        is_mating,
        is_penetrating_structural_joint,
    )

    threshold = float(params.value("tolerance.part_assembly_feature_mm"))
    rail_id = "FRAME-RAIL-ORG-REAR-001"
    panel_id = "PANEL-IN-REAR-001"
    parts = transport.parts
    inter_vol = intersection_volume(parts[rail_id].solid, parts[panel_id].solid)
    assert inter_vol <= ORG_REAR_PENETRATING_MAX_BEARING_MM3 + threshold
    assert is_penetrating_structural_joint(rail_id, panel_id, parts, threshold)
    assert is_mating(rail_id, panel_id, parts, threshold=threshold, params=params)


def test_post_panel_penetrating_rejects_volumetric_burial(params, transport):
    """FIX-COLL-008 AC-2 — POST↔PANEL-IN penetrating pattern must reject deep burial."""
    from stand_cad.geometry.collision import (
        POST_PANEL_PENETRATING_MAX_BEARING_MM3,
        is_mating,
        is_penetrating_structural_joint,
    )
    from stand_cad.geometry.registry import PartRecord

    threshold = float(params.value("tolerance.part_assembly_feature_mm"))
    post_id = "FRAME-POST-RR-001"
    panel_id = "PANEL-IN-REAR-001"
    panel = transport.parts[panel_id]
    panel_bounds = bounding_box_bounds(panel.solid)
    post = transport.parts[post_id]
    # Offset overlap — volumetric burial without coplanar AABB face
    # (avoids PANEL-IN-/FRAME- share_face path).
    buried_post = PartRecord(
        part_id=post_id,
        material=post.material,
        solid=box_from_bounds(
            panel_bounds[0][0] + 2.0,
            panel_bounds[1][0] + 2.0,
            panel_bounds[2][0] + 2.0,
            panel_bounds[0][0] + 200.0,
            panel_bounds[1][0] + 200.0,
            panel_bounds[2][0] + 200.0,
        ),
    )
    parts = dict(transport.parts)
    parts[post_id] = buried_post
    inter_vol = intersection_volume(buried_post.solid, panel.solid)
    assert inter_vol > POST_PANEL_PENETRATING_MAX_BEARING_MM3 + threshold
    assert inter_vol > 30_000.0
    assert not is_penetrating_structural_joint(post_id, panel_id, parts, threshold)
    assert not is_mating(post_id, panel_id, parts, threshold=threshold, params=params)


def test_post_panel_share_face_burial_rejects_volumetric_burial(params, transport):
    """FIX-COLL-008 cycle 1 — coplanar-face POST↔PANEL-IN burial must not silent-green."""
    from stand_cad.geometry.collision import (
        POST_PANEL_PENETRATING_MAX_BEARING_MM3,
        aabb_share_face,
        is_mating,
        is_penetrating_structural_joint,
    )
    from stand_cad.geometry.registry import PartRecord

    threshold = float(params.value("tolerance.part_assembly_feature_mm"))
    post_id = "FRAME-POST-RR-001"
    panel_id = "PANEL-IN-REAR-001"
    panel = transport.parts[panel_id]
    panel_bounds = bounding_box_bounds(panel.solid)
    post = transport.parts[post_id]
    buried_post = PartRecord(
        part_id=post_id,
        material=post.material,
        solid=box_from_bounds(
            panel_bounds[0][0],
            panel_bounds[1][0],
            panel_bounds[2][0],
            panel_bounds[0][1],
            panel_bounds[1][1] + 50.0,
            panel_bounds[2][1],
        ),
    )
    parts = dict(transport.parts)
    parts[post_id] = buried_post
    inter_vol = intersection_volume(buried_post.solid, panel.solid)
    assert aabb_share_face(buried_post.solid, panel.solid, threshold)
    assert inter_vol > POST_PANEL_PENETRATING_MAX_BEARING_MM3 + threshold
    assert inter_vol > 30_000.0
    assert not is_penetrating_structural_joint(post_id, panel_id, parts, threshold)
    assert not is_mating(post_id, panel_id, parts, threshold=threshold, params=params)


def test_post_panel_penetrating_live_mate_passes(params, transport):
    """FIX-COLL-008 AC-1 — live POST↔PANEL-IN intersection stays under class ceiling."""
    from stand_cad.geometry.collision import (
        POST_PANEL_PENETRATING_MAX_BEARING_MM3,
        is_mating,
        is_penetrating_structural_joint,
    )

    threshold = float(params.value("tolerance.part_assembly_feature_mm"))
    post_id = "FRAME-POST-RR-001"
    panel_id = "PANEL-IN-REAR-001"
    parts = transport.parts
    inter_vol = intersection_volume(parts[post_id].solid, parts[panel_id].solid)
    assert inter_vol <= POST_PANEL_PENETRATING_MAX_BEARING_MM3 + threshold
    assert is_penetrating_structural_joint(post_id, panel_id, parts, threshold)
    assert is_mating(post_id, panel_id, parts, threshold=threshold, params=params)


def test_tray_rail_panel_penetrating_rejects_volumetric_burial(params, transport):
    """FIX-COLL-009 AC-2 — TRAY-rail↔PANEL-IN penetrating pattern must reject deep burial."""
    from stand_cad.geometry.collision import (
        TRAY_RAIL_PANEL_PENETRATING_MAX_BEARING_MM3,
        is_mating,
        is_penetrating_structural_joint,
    )
    from stand_cad.geometry.registry import PartRecord

    threshold = float(params.value("tolerance.part_assembly_feature_mm"))
    rail_id = "FRAME-RAIL-TRAY-LOWER-L-001"
    panel_id = "PANEL-IN-BOTTOM-001"
    panel = transport.parts[panel_id]
    panel_bounds = bounding_box_bounds(panel.solid)
    rail = transport.parts[rail_id]
    # Offset overlap — volumetric burial without coplanar AABB face
    # (avoids PANEL-IN-/FRAME- share_face path).
    buried_rail = PartRecord(
        part_id=rail_id,
        material=rail.material,
        solid=box_from_bounds(
            panel_bounds[0][0] + 2.0,
            panel_bounds[1][0] + 2.0,
            panel_bounds[2][0] + 2.0,
            panel_bounds[0][0] + 200.0,
            panel_bounds[1][0] + 200.0,
            panel_bounds[2][0] + 200.0,
        ),
    )
    parts = dict(transport.parts)
    parts[rail_id] = buried_rail
    inter_vol = intersection_volume(buried_rail.solid, panel.solid)
    assert inter_vol > TRAY_RAIL_PANEL_PENETRATING_MAX_BEARING_MM3 + threshold
    assert inter_vol > 30_000.0
    assert not is_penetrating_structural_joint(rail_id, panel_id, parts, threshold)
    assert not is_mating(rail_id, panel_id, parts, threshold=threshold, params=params)


def test_tray_rail_panel_share_face_burial_rejects_volumetric_burial(params, transport):
    """FIX-COLL-009 cycle 1 — coplanar-face TRAY-rail↔PANEL-IN burial must not silent-green."""
    from stand_cad.geometry.collision import (
        TRAY_RAIL_PANEL_PENETRATING_MAX_BEARING_MM3,
        aabb_share_face,
        is_mating,
        is_penetrating_structural_joint,
    )
    from stand_cad.geometry.registry import PartRecord

    threshold = float(params.value("tolerance.part_assembly_feature_mm"))
    rail_id = "FRAME-RAIL-TRAY-LOWER-L-001"
    panel_id = "PANEL-IN-BOTTOM-001"
    panel = transport.parts[panel_id]
    panel_bounds = bounding_box_bounds(panel.solid)
    rail = transport.parts[rail_id]
    buried_rail = PartRecord(
        part_id=rail_id,
        material=rail.material,
        solid=box_from_bounds(
            panel_bounds[0][0],
            panel_bounds[1][0],
            panel_bounds[2][0],
            panel_bounds[0][1],
            panel_bounds[1][1] + 50.0,
            panel_bounds[2][1],
        ),
    )
    parts = dict(transport.parts)
    parts[rail_id] = buried_rail
    inter_vol = intersection_volume(buried_rail.solid, panel.solid)
    assert aabb_share_face(buried_rail.solid, panel.solid, threshold)
    assert inter_vol > TRAY_RAIL_PANEL_PENETRATING_MAX_BEARING_MM3 + threshold
    assert inter_vol > 30_000.0
    assert not is_penetrating_structural_joint(rail_id, panel_id, parts, threshold)
    assert not is_mating(rail_id, panel_id, parts, threshold=threshold, params=params)


def test_tray_rail_panel_penetrating_live_mate_passes(params, transport):
    """FIX-COLL-009 AC-1 — live TRAY-rail↔PANEL-IN intersection stays under class ceiling."""
    from stand_cad.geometry.collision import (
        TRAY_RAIL_PANEL_PENETRATING_MAX_BEARING_MM3,
        is_mating,
        is_penetrating_structural_joint,
    )

    threshold = float(params.value("tolerance.part_assembly_feature_mm"))
    rail_id = "FRAME-RAIL-TRAY-LOWER-L-001"
    panel_id = "PANEL-IN-BOTTOM-001"
    parts = transport.parts
    inter_vol = intersection_volume(parts[rail_id].solid, parts[panel_id].solid)
    assert inter_vol <= TRAY_RAIL_PANEL_PENETRATING_MAX_BEARING_MM3 + threshold
    assert is_penetrating_structural_joint(rail_id, panel_id, parts, threshold)
    assert is_mating(rail_id, panel_id, parts, threshold=threshold, params=params)


def test_cover_svc_panel_live_mate_passes(params, transport):
    """FIX-COLL-010 AC-1 — live COVER-SVC↔PANEL MATING pairs stay under class ceiling."""
    from stand_cad.geometry.collision import (
        COVER_SVC_PANEL_MAX_BEARING_MM3,
        MATING_PAIRS,
        is_cover_svc_panel_bearing,
        is_mating,
        pair_key,
    )

    threshold = float(params.value("tolerance.part_assembly_feature_mm"))
    cover_id = "COVER-SVC-001"
    for panel_id in ("PANEL-IN-BOTTOM-001", "PANEL-OUT-REAR-001"):
        assert pair_key(cover_id, panel_id) in MATING_PAIRS
        inter_vol = intersection_volume(
            transport.parts[cover_id].solid,
            transport.parts[panel_id].solid,
        )
        assert inter_vol <= COVER_SVC_PANEL_MAX_BEARING_MM3 + threshold
        assert is_cover_svc_panel_bearing(cover_id, panel_id, transport.parts, threshold)
        assert is_mating(cover_id, panel_id, transport.parts, threshold=threshold, params=params)


def test_cover_svc_panel_in_rear_share_face_live_mate_passes(params, transport):
    """FIX-COLL-010 — live COVER-SVC↔PANEL-IN-REAR share_face path stays under ceiling."""
    from stand_cad.geometry.collision import (
        COVER_SVC_PANEL_MAX_BEARING_MM3,
        MATING_PAIRS,
        is_mating,
        pair_key,
    )

    threshold = float(params.value("tolerance.part_assembly_feature_mm"))
    cover_id = "COVER-SVC-001"
    panel_id = "PANEL-IN-REAR-001"
    assert pair_key(cover_id, panel_id) not in MATING_PAIRS
    inter_vol = intersection_volume(
        transport.parts[cover_id].solid,
        transport.parts[panel_id].solid,
    )
    assert inter_vol <= COVER_SVC_PANEL_MAX_BEARING_MM3 + threshold
    assert is_mating(cover_id, panel_id, transport.parts, threshold=threshold, params=params)


def test_cover_svc_panel_rejects_volumetric_burial(params, transport):
    """FIX-COLL-010 AC-2 — COVER-SVC↔PANEL MATING pair must reject deep burial."""
    from stand_cad.geometry.collision import (
        COVER_SVC_PANEL_MAX_BEARING_MM3,
        MATING_PAIRS,
        is_cover_svc_panel_bearing,
        is_mating,
        pair_key,
    )
    from stand_cad.geometry.registry import PartRecord

    threshold = float(params.value("tolerance.part_assembly_feature_mm"))
    cover_id = "COVER-SVC-001"
    panel_id = "PANEL-IN-BOTTOM-001"
    assert pair_key(cover_id, panel_id) in MATING_PAIRS
    cover = transport.parts[cover_id]
    panel = transport.parts[panel_id]
    panel_bounds = bounding_box_bounds(panel.solid)
    buried_cover = PartRecord(
        part_id=cover_id,
        material=cover.material,
        solid=box_from_bounds(
            panel_bounds[0][0] + 2.0,
            panel_bounds[1][0] + 2.0,
            panel_bounds[2][0] + 2.0,
            panel_bounds[0][0] + 200.0,
            panel_bounds[1][0] + 200.0,
            panel_bounds[2][0] + 200.0,
        ),
    )
    parts = dict(transport.parts)
    parts[cover_id] = buried_cover
    inter_vol = intersection_volume(buried_cover.solid, panel.solid)
    assert inter_vol > COVER_SVC_PANEL_MAX_BEARING_MM3 + threshold
    assert inter_vol > 30_000.0
    assert not is_cover_svc_panel_bearing(cover_id, panel_id, parts, threshold)
    assert not is_mating(cover_id, panel_id, parts, threshold=threshold, params=params)


def test_cover_svc_panel_share_face_burial_rejects_volumetric_burial(params, transport):
    """FIX-COLL-010 cycle 1 — coplanar-face COVER-SVC↔PANEL-IN-REAR burial must not silent-green."""
    from stand_cad.geometry.collision import (
        COVER_SVC_PANEL_MAX_BEARING_MM3,
        aabb_share_face,
        is_cover_svc_panel_bearing,
        is_mating,
    )
    from stand_cad.geometry.registry import PartRecord

    threshold = float(params.value("tolerance.part_assembly_feature_mm"))
    cover_id = "COVER-SVC-001"
    panel_id = "PANEL-IN-REAR-001"
    panel = transport.parts[panel_id]
    panel_bounds = bounding_box_bounds(panel.solid)
    cover = transport.parts[cover_id]
    buried_cover = PartRecord(
        part_id=cover_id,
        material=cover.material,
        solid=box_from_bounds(
            panel_bounds[0][0],
            panel_bounds[1][0],
            panel_bounds[2][0],
            panel_bounds[0][1],
            panel_bounds[1][1] + 50.0,
            panel_bounds[2][1],
        ),
    )
    parts = dict(transport.parts)
    parts[cover_id] = buried_cover
    inter_vol = intersection_volume(buried_cover.solid, panel.solid)
    assert aabb_share_face(buried_cover.solid, panel.solid, threshold)
    assert inter_vol > COVER_SVC_PANEL_MAX_BEARING_MM3 + threshold
    assert inter_vol > 30_000.0
    assert not is_cover_svc_panel_bearing(cover_id, panel_id, parts, threshold)
    assert not is_mating(cover_id, panel_id, parts, threshold=threshold, params=params)


def test_cover_svc_frame_base_live_mate_passes(params, transport):
    """FIX-COLL-011 AC-1 — live COVER-SVC↔BASE-REAR share_face stays under class ceiling."""
    from stand_cad.geometry.collision import (
        COVER_SVC_FRAME_BASE_MAX_BEARING_MM3,
        is_cover_svc_frame_base_bearing,
        is_mating,
    )

    threshold = float(params.value("tolerance.part_assembly_feature_mm"))
    cover_id = "COVER-SVC-001"
    rail_id = "FRAME-RAIL-BASE-REAR-001"
    parts = transport.parts
    inter_vol = intersection_volume(parts[cover_id].solid, parts[rail_id].solid)
    assert inter_vol <= COVER_SVC_FRAME_BASE_MAX_BEARING_MM3 + threshold
    assert is_cover_svc_frame_base_bearing(cover_id, rail_id, parts, threshold)
    assert is_mating(cover_id, rail_id, parts, threshold=threshold, params=params)


def test_cover_svc_frame_post_live_mate_passes(params, transport):
    """FIX-COLL-011 AC-2 — live COVER-SVC↔POST share_face + penetrating stay under ceiling."""
    from stand_cad.geometry.collision import (
        COVER_SVC_FRAME_POST_MAX_BEARING_MM3,
        is_cover_svc_frame_post_bearing,
        is_mating,
        is_penetrating_structural_joint,
    )

    threshold = float(params.value("tolerance.part_assembly_feature_mm"))
    cover_id = "COVER-SVC-001"
    for post_id in ("FRAME-POST-RL-001", "FRAME-POST-RR-001"):
        parts = transport.parts
        inter_vol = intersection_volume(parts[cover_id].solid, parts[post_id].solid)
        assert inter_vol <= COVER_SVC_FRAME_POST_MAX_BEARING_MM3 + threshold
        assert is_cover_svc_frame_post_bearing(cover_id, post_id, parts, threshold)
        assert is_penetrating_structural_joint(cover_id, post_id, parts, threshold)
        assert is_mating(cover_id, post_id, parts, threshold=threshold, params=params)


def test_cover_svc_frame_base_burial_rejects_volumetric_burial(params, transport):
    """FIX-COLL-011 AC-3 — COVER-SVC↔BASE-REAR share_face burial must not silent-green."""
    from stand_cad.geometry.collision import (
        COVER_SVC_FRAME_BASE_MAX_BEARING_MM3,
        aabb_share_face,
        is_cover_svc_frame_base_bearing,
        is_mating,
    )
    from stand_cad.geometry.registry import PartRecord

    threshold = float(params.value("tolerance.part_assembly_feature_mm"))
    cover_id = "COVER-SVC-001"
    rail_id = "FRAME-RAIL-BASE-REAR-001"
    rail = transport.parts[rail_id]
    rail_bounds = bounding_box_bounds(rail.solid)
    cover = transport.parts[cover_id]
    buried_cover = PartRecord(
        part_id=cover_id,
        material=cover.material,
        solid=box_from_bounds(
            rail_bounds[0][0],
            rail_bounds[1][0],
            rail_bounds[2][0],
            rail_bounds[0][1],
            rail_bounds[1][1] + 50.0,
            rail_bounds[2][1],
        ),
    )
    parts = dict(transport.parts)
    parts[cover_id] = buried_cover
    inter_vol = intersection_volume(buried_cover.solid, rail.solid)
    assert aabb_share_face(buried_cover.solid, rail.solid, threshold)
    assert inter_vol > COVER_SVC_FRAME_BASE_MAX_BEARING_MM3 + threshold
    assert inter_vol > 30_000.0
    assert not is_cover_svc_frame_base_bearing(cover_id, rail_id, parts, threshold)
    assert not is_mating(cover_id, rail_id, parts, threshold=threshold, params=params)


def test_cover_svc_frame_post_share_face_burial_rejects_volumetric_burial(params, transport):
    """FIX-COLL-011 AC-3 — coplanar-face COVER-SVC↔POST burial must not silent-green."""
    from stand_cad.geometry.collision import (
        COVER_SVC_FRAME_POST_MAX_BEARING_MM3,
        aabb_share_face,
        is_cover_svc_frame_post_bearing,
        is_mating,
        is_penetrating_structural_joint,
    )
    from stand_cad.geometry.registry import PartRecord

    threshold = float(params.value("tolerance.part_assembly_feature_mm"))
    cover_id = "COVER-SVC-001"
    post_id = "FRAME-POST-RR-001"
    post = transport.parts[post_id]
    post_bounds = bounding_box_bounds(post.solid)
    cover = transport.parts[cover_id]
    buried_cover = PartRecord(
        part_id=cover_id,
        material=cover.material,
        solid=box_from_bounds(
            post_bounds[0][0],
            post_bounds[1][0],
            post_bounds[2][0],
            post_bounds[0][1],
            post_bounds[1][1] + 50.0,
            post_bounds[2][1],
        ),
    )
    parts = dict(transport.parts)
    parts[cover_id] = buried_cover
    inter_vol = intersection_volume(buried_cover.solid, post.solid)
    assert aabb_share_face(buried_cover.solid, post.solid, threshold)
    assert inter_vol > COVER_SVC_FRAME_POST_MAX_BEARING_MM3 + threshold
    assert inter_vol > 30_000.0
    assert not is_cover_svc_frame_post_bearing(cover_id, post_id, parts, threshold)
    assert not is_penetrating_structural_joint(cover_id, post_id, parts, threshold)
    assert not is_mating(cover_id, post_id, parts, threshold=threshold, params=params)


def test_cover_svc_frame_post_penetrating_burial_rejects_volumetric_burial(params, transport):
    """FIX-COLL-011 AC-3 — COVER-SVC↔POST penetrating pattern must reject deep burial."""
    from stand_cad.geometry.collision import (
        COVER_SVC_FRAME_POST_MAX_BEARING_MM3,
        is_mating,
        is_penetrating_structural_joint,
    )
    from stand_cad.geometry.registry import PartRecord

    threshold = float(params.value("tolerance.part_assembly_feature_mm"))
    cover_id = "COVER-SVC-001"
    post_id = "FRAME-POST-RR-001"
    post = transport.parts[post_id]
    post_bounds = bounding_box_bounds(post.solid)
    cover = transport.parts[cover_id]
    buried_cover = PartRecord(
        part_id=cover_id,
        material=cover.material,
        solid=box_from_bounds(
            post_bounds[0][0] + 2.0,
            post_bounds[1][0] + 2.0,
            post_bounds[2][0] + 2.0,
            post_bounds[0][0] + 200.0,
            post_bounds[1][0] + 200.0,
            post_bounds[2][0] + 200.0,
        ),
    )
    parts = dict(transport.parts)
    parts[cover_id] = buried_cover
    inter_vol = intersection_volume(buried_cover.solid, post.solid)
    assert inter_vol > COVER_SVC_FRAME_POST_MAX_BEARING_MM3 + threshold
    assert inter_vol > 30_000.0
    assert not is_penetrating_structural_joint(cover_id, post_id, parts, threshold)
    assert not is_mating(cover_id, post_id, parts, threshold=threshold, params=params)


def test_mid_upper_penetrating_rejects_volumetric_burial(params, transport):
    """FIX-COLL-007 AC-2 — MID ↔ SLIDE-UPPER penetrating pattern must reject deep burial."""
    from stand_cad.geometry.collision import (
        MID_UPPER_PENETRATING_MAX_BEARING_MM3,
        is_mating,
        is_penetrating_structural_joint,
    )
    from stand_cad.geometry.registry import PartRecord

    threshold = float(params.value("tolerance.part_assembly_feature_mm"))
    slide_id = "SLIDE-UPPER-LEFT-001"
    mid_id = "PANEL-IN-MID-001"
    mid = transport.parts[mid_id]
    mid_bounds = bounding_box_bounds(mid.solid)
    slide = transport.parts[slide_id]
    # Offset overlap — volumetric burial without coplanar AABB face.
    buried_slide = PartRecord(
        part_id=slide_id,
        material=slide.material,
        solid=box_from_bounds(
            mid_bounds[0][0] + 2.0,
            mid_bounds[1][0] + 2.0,
            mid_bounds[2][0] + 2.0,
            mid_bounds[0][0] + 200.0,
            mid_bounds[1][0] + 200.0,
            mid_bounds[2][0] + 200.0,
        ),
    )
    parts = dict(transport.parts)
    parts[slide_id] = buried_slide
    inter_vol = intersection_volume(buried_slide.solid, mid.solid)
    assert inter_vol > MID_UPPER_PENETRATING_MAX_BEARING_MM3 + threshold
    assert inter_vol > 40_000.0
    assert not is_penetrating_structural_joint(slide_id, mid_id, parts, threshold)
    assert not is_mating(slide_id, mid_id, parts, threshold=threshold, params=params)


def test_mid_upper_penetrating_live_mate_passes(params, transport):
    """FIX-COLL-007 AC-1 — live MID ↔ SLIDE-UPPER intersection stays under class ceiling."""
    from stand_cad.geometry.collision import (
        MID_UPPER_PENETRATING_MAX_BEARING_MM3,
        is_mating,
        is_penetrating_structural_joint,
    )

    threshold = float(params.value("tolerance.part_assembly_feature_mm"))
    slide_id = "SLIDE-UPPER-LEFT-001"
    mid_id = "PANEL-IN-MID-001"
    parts = transport.parts
    inter_vol = intersection_volume(parts[slide_id].solid, parts[mid_id].solid)
    assert inter_vol <= MID_UPPER_PENETRATING_MAX_BEARING_MM3 + threshold
    assert is_penetrating_structural_joint(slide_id, mid_id, parts, threshold)
    assert is_mating(slide_id, mid_id, parts, threshold=threshold, params=params)


def test_kinematic_group_membership_alone_rejects_equip_softstop_burial(params, transport):
    """FIX-COLL-003 AC-1 — same-group membership must not exempt deep EQUIP↔SOFTSTOP burial."""
    from stand_cad.geometry.collision import MATING_PAIRS, is_mating, pair_key
    from stand_cad.geometry.registry import PartRecord

    threshold = float(params.value("tolerance.part_assembly_feature_mm"))
    equip_id = "EQUIP-PLOTTER1-001"
    soft_id = "SOFTSTOP-LOWER-001"
    assert pair_key(equip_id, soft_id) not in MATING_PAIRS
    equip = transport.parts[equip_id]
    equip_bounds = bounding_box_bounds(equip.solid)
    buried_soft = PartRecord(
        part_id=soft_id,
        material=transport.parts[soft_id].material,
        solid=box_from_bounds(
            equip_bounds[0][0],
            equip_bounds[1][0],
            equip_bounds[2][0],
            equip_bounds[0][1],
            equip_bounds[1][1] + 50.0,
            equip_bounds[2][1],
        ),
    )
    parts = dict(transport.parts)
    parts[soft_id] = buried_soft
    inter_vol = intersection_volume(equip.solid, buried_soft.solid)
    assert inter_vol > 20_000.0
    assert not is_mating(equip_id, soft_id, parts, threshold=threshold, params=params)


def test_slide_vibmount_bearing_rejects_volumetric_burial(params, transport):
    """FIX-COLL-003 — slide↔vibmount skin ceiling rejects deep burial."""
    from stand_cad.geometry.collision import (
        SLIDE_VIBMOUNT_MAX_BEARING_MM3,
        is_mating,
        is_slide_vibmount_bearing,
    )
    from stand_cad.geometry.registry import PartRecord

    threshold = float(params.value("tolerance.part_assembly_feature_mm"))
    slide_id = "SLIDE-LOWER-LEFT-001"
    vib_id = "VIBMOUNT-P1-001"
    slide = transport.parts[slide_id]
    slide_bounds = bounding_box_bounds(slide.solid)
    buried_vib = PartRecord(
        part_id=vib_id,
        material=transport.parts[vib_id].material,
        solid=box_from_bounds(
            slide_bounds[0][0],
            slide_bounds[1][0],
            slide_bounds[2][0],
            slide_bounds[0][1],
            slide_bounds[1][1] + 50.0,
            slide_bounds[2][1],
        ),
    )
    parts = dict(transport.parts)
    parts[vib_id] = buried_vib
    inter_vol = intersection_volume(slide.solid, buried_vib.solid)
    assert inter_vol > SLIDE_VIBMOUNT_MAX_BEARING_MM3 + threshold
    assert inter_vol > 20_000.0
    assert not is_slide_vibmount_bearing(slide_id, vib_id, parts, threshold)
    assert not is_mating(slide_id, vib_id, parts, threshold=threshold, params=params)
    # D-089 Path A — slide below tray; vib mount on tray top; live pairs separated.
    live_clr = minimum_clearance(
        transport.parts[slide_id].solid,
        transport.parts[vib_id].solid,
    )
    assert live_clr >= threshold
    assert not is_slide_vibmount_bearing(slide_id, vib_id, transport.parts, threshold)


def test_equip_seating_bearing_rejects_tray_volumetric_burial(params, transport):
    """FIX-COLL-004 — EQUIP↔TRAY seating ceiling rejects deep burial."""
    from stand_cad.geometry.collision import (
        EQUIP_SEATING_MAX_BEARING_MM3,
        MATING_PAIRS,
        is_equip_seating_bearing,
        is_mating,
        pair_key,
    )
    from stand_cad.geometry.registry import PartRecord

    threshold = float(params.value("tolerance.part_assembly_feature_mm"))
    equip_id = "EQUIP-PLOTTER1-001"
    tray_id = "TRAY-LOWER-001"
    assert pair_key(equip_id, tray_id) in MATING_PAIRS
    equip = transport.parts[equip_id]
    equip_bounds = bounding_box_bounds(equip.solid)
    buried_tray = PartRecord(
        part_id=tray_id,
        material=transport.parts[tray_id].material,
        solid=box_from_bounds(
            equip_bounds[0][0],
            equip_bounds[1][0],
            equip_bounds[2][0],
            equip_bounds[0][1],
            equip_bounds[1][1] + 50.0,
            equip_bounds[2][1],
        ),
    )
    parts = dict(transport.parts)
    parts[tray_id] = buried_tray
    inter_vol = intersection_volume(equip.solid, buried_tray.solid)
    assert inter_vol > EQUIP_SEATING_MAX_BEARING_MM3 + threshold
    assert inter_vol > 20_000.0
    assert not is_equip_seating_bearing(equip_id, tray_id, parts, threshold)
    assert not is_mating(equip_id, tray_id, parts, threshold=threshold, params=params)
    live_inter = intersection_volume(
        transport.parts[equip_id].solid,
        transport.parts[tray_id].solid,
    )
    assert live_inter <= EQUIP_SEATING_MAX_BEARING_MM3 + threshold
    assert is_equip_seating_bearing(equip_id, tray_id, transport.parts, threshold)
    assert is_mating(equip_id, tray_id, transport.parts, threshold=threshold, params=params)


def test_equip_seating_bearing_rejects_slide_volumetric_burial(params, transport):
    """FIX-COLL-004 — EQUIP↔SLIDE seating ceiling rejects deep burial."""
    from stand_cad.geometry.collision import (
        EQUIP_SEATING_MAX_BEARING_MM3,
        MATING_PAIRS,
        is_equip_seating_bearing,
        is_mating,
        pair_key,
    )
    from stand_cad.geometry.registry import PartRecord

    threshold = float(params.value("tolerance.part_assembly_feature_mm"))
    equip_id = "EQUIP-PLOTTER1-001"
    slide_id = "SLIDE-LOWER-LEFT-001"
    assert pair_key(equip_id, slide_id) in MATING_PAIRS
    equip = transport.parts[equip_id]
    equip_bounds = bounding_box_bounds(equip.solid)
    buried_slide = PartRecord(
        part_id=slide_id,
        material=transport.parts[slide_id].material,
        solid=box_from_bounds(
            equip_bounds[0][0],
            equip_bounds[1][0],
            equip_bounds[2][0],
            equip_bounds[0][1],
            equip_bounds[1][1] + 50.0,
            equip_bounds[2][1],
        ),
    )
    parts = dict(transport.parts)
    parts[slide_id] = buried_slide
    inter_vol = intersection_volume(equip.solid, buried_slide.solid)
    assert inter_vol > EQUIP_SEATING_MAX_BEARING_MM3 + threshold
    assert inter_vol > 20_000.0
    assert not is_equip_seating_bearing(equip_id, slide_id, parts, threshold)
    assert not is_mating(equip_id, slide_id, parts, threshold=threshold, params=params)
    # D-089 Path A — plotter seats on tray; slide below tray; live pair separated.
    live_clr = minimum_clearance(
        transport.parts[equip_id].solid,
        transport.parts[slide_id].solid,
    )
    assert live_clr >= threshold
    assert not is_equip_seating_bearing(equip_id, slide_id, transport.parts, threshold)


def test_staggered_tier_y_overlap_live_transport_plane_touch(params, transport):
    """FIX-COLL-012 — live cross-tier Y-overlap pairs with vol≈0 still exempt."""
    from stand_cad.geometry.collision import (
        STAGGERED_TIER_MAX_BEARING_MM3,
        is_mating,
        is_staggered_tier_y_overlap,
    )

    threshold = float(params.value("tolerance.part_assembly_feature_mm"))
    lower_id = "EQUIP-PLOTTER1-001"
    upper_id = "FRAME-RAIL-TRAY-UPPER-L-001"
    live_inter = intersection_volume(
        transport.parts[lower_id].solid,
        transport.parts[upper_id].solid,
    )
    assert live_inter <= STAGGERED_TIER_MAX_BEARING_MM3 + threshold
    assert is_staggered_tier_y_overlap(lower_id, upper_id, transport.parts, threshold)
    assert is_mating(
        lower_id, upper_id, transport.parts, threshold=threshold, params=params
    )


def test_staggered_tier_y_overlap_rejects_volumetric_burial(params, transport):
    """FIX-COLL-012 — cross-tier Y-overlap must not silent-green deep burial."""
    from stand_cad.geometry.collision import (
        STAGGERED_TIER_MAX_BEARING_MM3,
        is_mating,
        is_staggered_tier_y_overlap,
    )
    from stand_cad.geometry.registry import PartRecord

    threshold = float(params.value("tolerance.part_assembly_feature_mm"))
    equip_id = "EQUIP-PLOTTER1-001"
    rail_id = "FRAME-RAIL-TRAY-UPPER-L-001"
    equip = transport.parts[equip_id]
    equip_bounds = bounding_box_bounds(equip.solid)
    buried_rail = PartRecord(
        part_id=rail_id,
        material=transport.parts[rail_id].material,
        solid=box_from_bounds(
            equip_bounds[0][0],
            equip_bounds[1][0],
            equip_bounds[2][0],
            equip_bounds[0][1],
            equip_bounds[1][1],
            equip_bounds[2][1] + 50.0,
        ),
    )
    parts = dict(transport.parts)
    parts[rail_id] = buried_rail
    inter_vol = intersection_volume(equip.solid, buried_rail.solid)
    assert inter_vol > STAGGERED_TIER_MAX_BEARING_MM3 + threshold
    assert inter_vol > 20_000.0
    assert not is_staggered_tier_y_overlap(equip_id, rail_id, parts, threshold)
    assert not is_mating(equip_id, rail_id, parts, threshold=threshold, params=params)
    live_inter = intersection_volume(
        transport.parts[equip_id].solid,
        transport.parts[rail_id].solid,
    )
    assert live_inter <= STAGGERED_TIER_MAX_BEARING_MM3 + threshold
    assert is_staggered_tier_y_overlap(equip_id, rail_id, transport.parts, threshold)
    assert is_mating(
        equip_id, rail_id, transport.parts, threshold=threshold, params=params
    )


def test_cross_tier_tray_slide_rail_share_face_burial_rejects_volumetric_burial(
    params, transport
):
    """FIX-COLL-013 — cross-tier TRAY/SLIDE↔rail share_face burial must not silent-green."""
    from stand_cad.geometry.collision import (
        STAGGERED_TIER_MAX_BEARING_MM3,
        aabb_share_face,
        is_mating,
        is_staggered_tier_y_overlap,
    )
    from stand_cad.geometry.registry import PartRecord

    threshold = float(params.value("tolerance.part_assembly_feature_mm"))
    tray_id = "TRAY-LOWER-001"
    slide_id = "SLIDE-LOWER-LEFT-001"
    rail_id = "FRAME-RAIL-TRAY-UPPER-L-001"
    rail_material = transport.parts[rail_id].material

    tray = transport.parts[tray_id]
    tray_bounds = bounding_box_bounds(tray.solid)
    buried_rail = PartRecord(
        part_id=rail_id,
        material=rail_material,
        solid=box_from_bounds(
            tray_bounds[0][0],
            tray_bounds[1][0],
            tray_bounds[2][0],
            tray_bounds[0][1],
            tray_bounds[1][1] + 50.0,
            tray_bounds[2][1],
        ),
    )
    parts = dict(transport.parts)
    parts[rail_id] = buried_rail
    inter_vol = intersection_volume(tray.solid, buried_rail.solid)
    assert aabb_share_face(tray.solid, buried_rail.solid, threshold)
    assert inter_vol > STAGGERED_TIER_MAX_BEARING_MM3 + threshold
    assert inter_vol > 20_000.0
    assert not is_staggered_tier_y_overlap(tray_id, rail_id, parts, threshold)
    assert not is_mating(tray_id, rail_id, parts, threshold=threshold, params=params)

    slide = transport.parts[slide_id]
    slide_bounds = bounding_box_bounds(slide.solid)
    buried_rail = PartRecord(
        part_id=rail_id,
        material=rail_material,
        solid=box_from_bounds(
            slide_bounds[0][0],
            slide_bounds[1][0],
            slide_bounds[2][0],
            slide_bounds[0][1],
            slide_bounds[1][1] + 50.0,
            slide_bounds[2][1],
        ),
    )
    parts = dict(transport.parts)
    parts[rail_id] = buried_rail
    inter_vol = intersection_volume(slide.solid, buried_rail.solid)
    assert aabb_share_face(slide.solid, buried_rail.solid, threshold)
    assert inter_vol > STAGGERED_TIER_MAX_BEARING_MM3 + threshold
    assert inter_vol > 20_000.0
    assert not is_staggered_tier_y_overlap(slide_id, rail_id, parts, threshold)
    assert not is_mating(slide_id, rail_id, parts, threshold=threshold, params=params)


def test_cross_tier_tray_slide_rail_same_tier_slide_live_mate_passes(params, transport):
    """FIX-COLL-013 AC-2 — same-tier SLIDE↔FRAME-RAIL-TRAY MATING_PAIRS still mate."""
    from stand_cad.geometry.collision import MATING_PAIRS, is_mating, pair_key

    threshold = float(params.value("tolerance.part_assembly_feature_mm"))
    slide_id = "SLIDE-LOWER-LEFT-001"
    rail_id = "FRAME-RAIL-TRAY-LOWER-L-001"
    assert pair_key(slide_id, rail_id) in MATING_PAIRS
    assert is_mating(slide_id, rail_id, transport.parts, threshold=threshold, params=params)


def test_tray_slide_bearing_rejects_volumetric_burial(params, transport):
    """FIX-COLL-005 — TRAY↔SLIDE bearing ceiling rejects deep burial."""
    from stand_cad.geometry.collision import (
        MATING_PAIRS,
        TRAY_SLIDE_MAX_BEARING_MM3,
        is_mating,
        is_tray_slide_bearing,
        pair_key,
    )
    from stand_cad.geometry.registry import PartRecord

    threshold = float(params.value("tolerance.part_assembly_feature_mm"))
    tray_id = "TRAY-LOWER-001"
    slide_id = "SLIDE-LOWER-LEFT-001"
    assert pair_key(tray_id, slide_id) in MATING_PAIRS
    tray = transport.parts[tray_id]
    tray_bounds = bounding_box_bounds(tray.solid)
    buried_slide = PartRecord(
        part_id=slide_id,
        material=transport.parts[slide_id].material,
        solid=box_from_bounds(
            tray_bounds[0][0],
            tray_bounds[1][0],
            tray_bounds[2][0],
            tray_bounds[0][1],
            tray_bounds[1][1],
            tray_bounds[2][1],
        ),
    )
    parts = dict(transport.parts)
    parts[slide_id] = buried_slide
    inter_vol = intersection_volume(tray.solid, buried_slide.solid)
    assert inter_vol > TRAY_SLIDE_MAX_BEARING_MM3 + threshold
    assert inter_vol > 20_000.0
    assert not is_tray_slide_bearing(tray_id, slide_id, parts, threshold)
    assert not is_mating(tray_id, slide_id, parts, threshold=threshold, params=params)
    live_inter = intersection_volume(
        transport.parts[tray_id].solid,
        transport.parts[slide_id].solid,
    )
    assert live_inter <= TRAY_SLIDE_MAX_BEARING_MM3 + threshold
    assert is_tray_slide_bearing(tray_id, slide_id, transport.parts, threshold)
    assert is_mating(
        tray_id, slide_id, transport.parts, threshold=threshold, params=params
    )


def test_vib_equip_bearing_rejects_volumetric_burial(params, transport):
    """FIX-COLL-006 — VIB↔EQUIP pad ceiling rejects deep burial."""
    from stand_cad.geometry.collision import (
        MATING_PAIRS,
        VIB_EQUIP_MAX_BEARING_MM3,
        is_mating,
        is_vib_equip_bearing,
        pair_key,
    )
    from stand_cad.geometry.registry import PartRecord

    threshold = float(params.value("tolerance.part_assembly_feature_mm"))
    vib_id = "VIBMOUNT-P1-001"
    equip_id = "EQUIP-PLOTTER1-001"
    assert pair_key(vib_id, equip_id) in MATING_PAIRS
    equip = transport.parts[equip_id]
    equip_bounds = bounding_box_bounds(equip.solid)
    buried_vib = PartRecord(
        part_id=vib_id,
        material=transport.parts[vib_id].material,
        solid=box_from_bounds(
            equip_bounds[0][0],
            equip_bounds[1][0],
            equip_bounds[2][0],
            equip_bounds[0][1],
            equip_bounds[1][1] + 50.0,
            equip_bounds[2][1],
        ),
    )
    parts = dict(transport.parts)
    parts[vib_id] = buried_vib
    inter_vol = intersection_volume(equip.solid, buried_vib.solid)
    assert inter_vol > VIB_EQUIP_MAX_BEARING_MM3 + threshold
    assert inter_vol > 20_000.0
    assert not is_vib_equip_bearing(vib_id, equip_id, parts, threshold)
    assert not is_mating(vib_id, equip_id, parts, threshold=threshold, params=params)


def test_live_transport_vib_equip_pairs_no_false_collision(params, transport):
    """FIX-COLL-006 AC-3 — live transport VIB↔EQUIP pairs stay mated under ceiling."""
    from stand_cad.geometry.collision import (
        VIB_EQUIP_MAX_BEARING_MM3,
        check_collision_pairs,
        is_mating,
        is_vib_equip_bearing,
        is_vib_equip_bearing_pair,
    )

    threshold = float(params.value("tolerance.part_assembly_feature_mm"))
    vib_equip_pairs = (
        ("VIBMOUNT-P1-001", "EQUIP-PLOTTER1-001"),
        ("VIBMOUNT-P1-002", "EQUIP-PLOTTER1-001"),
        ("VIBMOUNT-P1-003", "EQUIP-PLOTTER1-001"),
        ("VIBMOUNT-P1-004", "EQUIP-PLOTTER1-001"),
        ("VIBMOUNT-P2-001", "EQUIP-PLOTTER2-001"),
        ("VIBMOUNT-P2-002", "EQUIP-PLOTTER2-001"),
        ("VIBMOUNT-P2-003", "EQUIP-PLOTTER2-001"),
        ("VIBMOUNT-P2-004", "EQUIP-PLOTTER2-001"),
    )
    for vib_id, equip_id in vib_equip_pairs:
        assert is_vib_equip_bearing_pair(vib_id, equip_id)
        inter_vol = intersection_volume(
            transport.parts[vib_id].solid,
            transport.parts[equip_id].solid,
        )
        assert abs(inter_vol - 2000.0) <= threshold + 1.0, (
            f"{vib_id}<->{equip_id} inter_vol={inter_vol} mm³ expected ~2000 pad embed"
        )
        assert inter_vol <= VIB_EQUIP_MAX_BEARING_MM3 + threshold
        assert is_vib_equip_bearing(vib_id, equip_id, transport.parts, threshold)
        assert is_mating(
            vib_id,
            equip_id,
            transport.parts,
            threshold=threshold,
            params=params,
        )
    violations = check_collision_pairs(transport.parts, params, "transport")
    for vib_id, equip_id in vib_equip_pairs:
        assert not any(
            vib_id in msg and equip_id in msg for msg in violations
        ), f"False positive: {vib_id}<->{equip_id}"


def test_live_tray_slide_bearing_under_ceiling(params, transport, service_p1):
    """FIX-COLL-005 — live TRAY↔SLIDE pairs stay mated under ceiling (transport + service)."""
    from stand_cad.geometry.collision import (
        TRAY_SLIDE_MAX_BEARING_MM3,
        check_collision_pairs,
        is_mating,
        is_tray_slide_bearing,
        is_tray_slide_pair,
    )

    threshold = float(params.value("tolerance.part_assembly_feature_mm"))
    tray_slide_pairs = (
        ("TRAY-LOWER-001", "SLIDE-LOWER-LEFT-001"),
        ("TRAY-LOWER-001", "SLIDE-LOWER-RIGHT-001"),
        ("TRAY-LOWER-001", "SLIDE-LOWER-CENTER-001"),
        ("TRAY-UPPER-001", "SLIDE-UPPER-LEFT-001"),
        ("TRAY-UPPER-001", "SLIDE-UPPER-RIGHT-001"),
        ("TRAY-UPPER-001", "SLIDE-UPPER-CENTER-001"),
    )
    for assembly in (transport, service_p1):
        for tray_id, slide_id in tray_slide_pairs:
            assert is_tray_slide_pair(tray_id, slide_id)
            inter_vol = intersection_volume(
                assembly.parts[tray_id].solid,
                assembly.parts[slide_id].solid,
            )
            assert inter_vol <= TRAY_SLIDE_MAX_BEARING_MM3 + threshold
            assert inter_vol < 96525.0, (
                f"{tray_id}<->{slide_id} inter_vol={inter_vol} mm³ still at pre-fix burial level"
            )
            assert is_tray_slide_bearing(tray_id, slide_id, assembly.parts, threshold)
            assert is_mating(
                tray_id,
                slide_id,
                assembly.parts,
                threshold=threshold,
                params=params,
            )
        violations = check_collision_pairs(assembly.parts, params, "transport")
        for tray_id, slide_id in tray_slide_pairs:
            assert not any(
                tray_id in msg and slide_id in msg for msg in violations
            ), f"False positive: {tray_id}<->{slide_id}"


def test_live_transport_seating_pairs_no_false_collision(params, transport):
    """FIX-COLL-004 AC-3 — live transport seating pairs stay mated under ceiling."""
    from stand_cad.geometry.collision import (
        EQUIP_SEATING_MAX_BEARING_MM3,
        check_collision_pairs,
        is_equip_seating_bearing,
        is_mating,
    )

    threshold = float(params.value("tolerance.part_assembly_feature_mm"))
    seating_pairs = (
        ("EQUIP-PLOTTER1-001", "TRAY-LOWER-001"),
        ("EQUIP-PLOTTER2-001", "TRAY-UPPER-001"),
    )
    for equip_id, target_id in seating_pairs:
        inter_vol = intersection_volume(
            transport.parts[equip_id].solid,
            transport.parts[target_id].solid,
        )
        assert inter_vol <= EQUIP_SEATING_MAX_BEARING_MM3 + threshold
        assert is_equip_seating_bearing(equip_id, target_id, transport.parts, threshold)
        assert is_mating(
            equip_id,
            target_id,
            transport.parts,
            threshold=threshold,
            params=params,
        )
    violations = check_collision_pairs(transport.parts, params, "transport")
    for equip_id, target_id in seating_pairs:
        assert not any(
            equip_id in msg and target_id in msg for msg in violations
        ), f"False positive: {equip_id}<->{target_id}"


def test_post_cladding_and_base_org_cladding_not_emitted(params, transport):
    """D-069/D-070 — owner removed BASE/ORG/POST front cladding strips."""
    removed = [
        "PANEL-CLAD-FRONT-BASE-001",
        "PANEL-CLAD-FRONT-ORG-001",
        "PANEL-CLAD-FRONT-POST-FL-001",
        "PANEL-CLAD-FRONT-POST-FR-001",
    ]
    for part_id in removed:
        assert part_id not in transport.parts
    tray_clad = [pid for pid in transport.parts if pid.startswith("PANEL-CLAD-FRONT-TRAY-")]
    assert len(tray_clad) == 6


def test_weld_free_joint_registry(params):
    """D-061 — joint types encoded in parameters.yaml + hardware.py registry."""
    from stand_cad.geometry.hardware import (
        JOINT_TYPE_IDS,
        joint_instance_counts,
        joint_type_registry,
        total_fastener_count,
    )

    specs = joint_type_registry(params)
    assert len(specs) == len(JOINT_TYPE_IDS)
    assert len(JOINT_TYPE_IDS) == 8
    assert {s.joint_type_id for s in specs} == set(JOINT_TYPE_IDS)
    counts = joint_instance_counts(params)
    assert counts["JT-HANDLE-HARDWARE"] == 0
    assert counts["JT-FRAME-CORNER"] == 22
    assert counts["JT-TRAY-RAIL-FRAME"] == 12
    assert counts["JT-STACK-CAP-POST"] == 4
    frame_spec = next(s for s in specs if s.joint_type_id == "JT-FRAME-CORNER")
    tray_spec = next(s for s in specs if s.joint_type_id == "JT-TRAY-RAIL-FRAME")
    stack_spec = next(s for s in specs if s.joint_type_id == "JT-STACK-CAP-POST")
    shelf_spec = next(s for s in specs if s.joint_type_id == "JT-SHELF-SUPPORT-SKIN")
    assert frame_spec.qty_per_joint == 2
    assert tray_spec.qty_per_joint == 2
    assert stack_spec.qty_per_joint == 2
    assert shelf_spec.qty_per_joint == 3
    assert "no adhesive" in shelf_spec.method.lower()
    assert stack_spec.fastener_size == "M4"
    assert total_fastener_count(params) > 50
    handle = next(s for s in specs if s.joint_type_id == "JT-HANDLE-HARDWARE")
    assert handle.qty_per_joint == 0
    assert "through-cut" in handle.method


def test_stack_cap_bearing_bridges_l_notch(params, transport):
    """STACK-001 / D-064 — cap plate bridges hollow quadrant (D-075 posts restored)."""
    from stand_cad.geometry.primitives import solid_point_state

    cap_t = float(params.value("stacking.cap_thickness_mm"))
    recess_depth = float(params.value("stacking.foot_recess_depth_mm"))
    case_h = float(params.value("case.height"))
    z_probe = case_h + cap_t / 2.0
    floor_z = case_h + (cap_t - recess_depth) / 2.0
    hollow_probes = {
        "FL": (27.0, 27.0),
        "FR": (622.0, 27.0),
        "RL": (27.0, 412.0),
        "RR": (622.0, 412.0),
    }
    for suffix, (px, py) in hollow_probes.items():
        cap_id = f"STACK-CAP-{suffix}-001"
        cap = transport.parts[cap_id].solid
        assert solid_point_state(cap, px, py, z_probe) in ("IN", "ON")
        assert solid_point_state(cap, px, py, floor_z) in ("IN", "ON")


def test_stack_cap_foot_recess_registration(params, transport):
    """STACK-001 / D-064 — recess Ø = foot_d + clearance; registration wall outside foot."""
    from build123d import Align, Cylinder, Location

    from stand_cad.geometry.primitives import solid_point_state

    foot_d = float(params.value("hardware.foot_diameter_mm"))
    clearance = float(params.value("stacking.foot_recess_clearance_mm"))
    recess_depth = float(params.value("stacking.foot_recess_depth_mm"))
    cap_t = float(params.value("stacking.cap_thickness_mm"))
    case_h = float(params.value("case.height"))
    width = float(params.value("case.width"))
    depth = float(params.value("case.depth"))
    inset = foot_d / 2.0
    recess_d = foot_d + clearance
    recess_r = recess_d / 2.0
    foot_r = foot_d / 2.0
    foot_map = {
        "FL": ("STACK-CAP-FL-001", inset, inset),
        "FR": ("STACK-CAP-FR-001", width - inset, inset),
        "RL": ("STACK-CAP-RL-001", inset, depth - inset),
        "RR": ("STACK-CAP-RR-001", width - inset, depth - inset),
    }
    z_top = case_h + cap_t
    z_in_recess = z_top - recess_depth / 2.0
    z_below_recess = case_h + recess_depth / 2.0
    inward_dx = {"FL": 1.0, "FR": -1.0, "RL": 1.0, "RR": -1.0}
    inward_dy = {"FL": 1.0, "FR": 1.0, "RL": -1.0, "RR": -1.0}
    wall_inset = recess_r - 0.1
    for suffix, (cap_id, cx, cy) in foot_map.items():
        cap = transport.parts[cap_id].solid
        dx = inward_dx[suffix]
        dy = inward_dy[suffix]
        assert solid_point_state(cap, cx, cy, z_in_recess) == "OUT"
        assert solid_point_state(cap, cx, cy, z_below_recess) in ("IN", "ON")
        assert solid_point_state(
            cap, cx + dx * (foot_r - 0.1), cy, z_in_recess
        ) == "OUT"
        assert solid_point_state(
            cap, cx + dx * wall_inset, cy + dy * wall_inset, z_in_recess
        ) in ("IN", "ON")
        foot_proxy = Cylinder(
            foot_r,
            recess_depth,
            align=(Align.CENTER, Align.CENTER, Align.MIN),
        ).move(Location((cx, cy, z_top - recess_depth)))
        assert intersection_volume(foot_proxy, cap) == pytest.approx(0.0, abs=1.0)
    assert recess_d == pytest.approx(foot_d + clearance, abs=1e-6)
