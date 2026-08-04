# A passing test is not evidence of physical correctness.
"""Geometry tests for PLT-002 static structure and Packet-3 completion."""

from __future__ import annotations

from pathlib import Path

import pytest

from stand_cad.geometry.analysis import (
    empty_case_mass_kg,
    indicative_tip_factor,
    indicative_tray_deflection_mm,
)
from stand_cad.geometry.assembly import (
    build_film_body_parts,
    build_operating_with_test_bodies_assembly,
    build_organizer_loaded_assembly,
    build_transport_assembly,
)
from stand_cad.geometry.datums import Datums
from stand_cad.geometry.primitives import (
    bounding_box_bounds,
    bounding_box_size,
    box_from_bounds,
    intersection_volume,
    minimum_clearance,
)
from stand_cad.parameters import (
    HORIZONTAL_ORGANIZER_CLEAR_MIN_MM,
    load_parameters,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
PARAMETERS_PATH = REPO_ROOT / "config" / "parameters.yaml"


@pytest.fixture(scope="module")
def params():
    return load_parameters(PARAMETERS_PATH)


@pytest.fixture(scope="module")
def transport(params):
    return build_transport_assembly(params)


@pytest.fixture(scope="module")
def datums(params):
    return Datums.from_parameters(params)


def test_overall_assembly_bounding_box(params, transport):
    tol = float(params.value("tolerance.assembly_mm"))
    compound = transport.compound()
    size = bounding_box_size(compound)
    expected = (
        float(params.value("case.width")),
        float(params.value("case.depth")),
        float(params.value("case.height")),
    )
    for actual, target in zip(size, expected, strict=True):
        assert actual == pytest.approx(target, abs=tol)


def test_plotter_physical_bodies(params, transport, datums):
    tol = float(params.value("tolerance.assembly_mm"))
    pw = float(params.value("plotter.physical_width"))
    pd = float(params.value("plotter.physical_depth"))
    ph = float(params.value("plotter.physical_height"))
    expected_size = (pw, pd, ph)
    assert pw == pytest.approx(570.0)

    for index, part_id in ((1, "EQUIP-PLOTTER1-001"), (2, "EQUIP-PLOTTER2-001")):
        solid = transport.parts[part_id].solid
        size = bounding_box_size(solid)
        for actual, target in zip(size, expected_size, strict=True):
            assert actual == pytest.approx(target, abs=tol)
        bounds = bounding_box_bounds(solid)
        datum = datums.plotter1_physical if index == 1 else datums.plotter2_physical
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
        "SVC-INSERT-L1-001",
        "SVC-INSERT-L2-001",
        "EDGEGUARD-L1-001",
        "EDGEGUARD-L2-001",
        "REARSUPPORT-L1-001",
        "REARSUPPORT-L2-001",
    }
)


def test_tier_clearance_minimum(params):
    """PLT-007 — both plotter tiers meet owner 170 mm minimum bay clearance."""
    p = load_parameters(PARAMETERS_PATH)
    tier_min = float(p.value("plotter.tier_clearance_min_mm"))
    assert p.tier_clearance_lower_mm == pytest.approx(170.0)
    assert p.tier_clearance_upper_mm == pytest.approx(170.0)
    assert p.tier_clearance_lower_mm >= tier_min
    assert p.tier_clearance_upper_mm >= tier_min


def test_horizontal_shelf_regeneration(params):
    """PLT-007 — three shelf dividers for four compartments."""
    state = build_transport_assembly(params)
    assert params.horizontal_shelf_divider_count == 3
    shelf_ids = [pid for pid in state.parts if pid.startswith("SHELF-")]
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
)


@pytest.mark.parametrize("body_kind", ["primary", "long"])
@pytest.mark.parametrize("level", ["L1", "L2"])
@pytest.mark.parametrize("y_offset_mm", [0.0, 25.0, 50.0, 75.0])
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
    slot_h = float(params.value("services.svc_insert_height_mm"))
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


def test_registry_single_mains_inlet_and_no_laptop_monitor_router(params, transport):
    """PLT-013 — exactly one MAINS-INLET-001; no laptop/monitor/router part IDs."""
    mains = [pid for pid in transport.parts if pid == "MAINS-INLET-001"]
    assert len(mains) == 1
    forbidden = ("laptop", "monitor", "router")
    for part_id in transport.parts:
        lower = part_id.lower()
        assert not any(word in lower for word in forbidden), part_id
        material = transport.parts[part_id].material.lower()
        assert not any(word in material for word in forbidden)


def test_indicative_tip_factor_non_authoritative(params):
    """PLT-010 indicative — NOT authoritative for Gate G4 engineering review."""
    factor = indicative_tip_factor(params, extended_level="lower")
    minimum = float(params.value("stability.tip_factor_min"))
    assert factor >= minimum, (
        f"indicative tip factor {factor:.3f} < {minimum} "
        "(NOT authoritative for Gate G4 — concept-stage estimate only)"
    )


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
        assert bounds[2][1] == pytest.approx(height, abs=tol + 1.0)
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


@pytest.mark.parametrize(
    ("post_suffix", "rail_a", "rail_b"),
    [
        ("FL", "FRAME-RAIL-BASE-FRONT-001", "FRAME-RAIL-BASE-LEFT-001"),
        ("FR", "FRAME-RAIL-BASE-FRONT-001", "FRAME-RAIL-BASE-RIGHT-001"),
        ("RL", "FRAME-RAIL-BASE-REAR-001", "FRAME-RAIL-BASE-LEFT-001"),
        ("RR", "FRAME-RAIL-BASE-REAR-001", "FRAME-RAIL-BASE-RIGHT-001"),
    ],
)
def test_frame_corner_post_rail_connectivity(
    params, transport, post_suffix, rail_a, rail_b
):
    """F-5 — each corner post overlaps the two base rails that meet at that corner."""
    tol = float(params.value("tolerance.part_assembly_feature_mm"))
    post_id = f"FRAME-POST-{post_suffix}-001"
    post = transport.parts[post_id].solid
    for rail_id in (rail_a, rail_b):
        rail = transport.parts[rail_id].solid
        overlap = intersection_volume(post, rail)
        clearance = minimum_clearance(post, rail)
        assert overlap > 0 or clearance < tol, (
            f"{post_id} disconnected from {rail_id}: "
            f"intersection={overlap:.3f} mm^3 clearance={clearance:.3f} mm"
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
    depth = datums.case_envelope.y.max_mm
    thickness = float(params.value("materials.outer_panel_thickness_mm"))
    slot_w = float(params.value("media_path.clear_width"))
    slot_h = float(params.value("media_path.slot_height_target"))
    cx = datums.case_envelope.x.max_mm / 2.0
    y_mid = depth - thickness / 2.0

    for level in ("L1", "L2"):
        feed_z = _feed_plane_z(params, level)
        assert solid_point_state(rear, cx, y_mid, feed_z) == "OUT"
        assert solid_point_state(rear, cx, y_mid, feed_z + slot_h / 2.0 + 5.0) == "IN"
        assert solid_point_state(rear, cx + slot_w / 2.0 + 5.0, y_mid, feed_z) == "IN"


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
    shelves = [pid for pid in transport.parts if pid.startswith("SHELF-")]
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


def test_handle_mount_z_side_panel_centred(params):
    """PLT-007 — handle Z at side-panel centre, not CoM (D-030: +47 mm above loaded CoM)."""
    foot_h = float(params.value("materials.foot_height_mm"))
    height = float(params.value("case.height"))
    expected = (foot_h + height) / 2
    assert float(params.value("hardware.handle_mount_z_mm")) == pytest.approx(expected)
    assert expected == pytest.approx(263.0)


def test_vertical_organizer_rightmost_cell_boundary_arithmetic():
    """D-031 — vertical cell 9 bounded by org floor at X=630, not missing divider."""
    org_x = 20.0
    clear_w = 610.0
    cells = 10
    divider_t = 2.0
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
    """PLT-006 AC-C1 — opal cladding covers front BASE/ORG/TOP rail spans in the opening."""
    width = float(params.value("case.width"))
    inset = float(params.value("case.corner_radius"))
    profile = float(params.value("materials.frame_profile_size_mm"))
    foot_h = float(params.value("materials.foot_height_mm"))
    for prefix in ("BASE", "ORG", "TOP"):
        part_id = f"PANEL-CLAD-FRONT-{prefix}-001"
        assert part_id in transport.parts
        record = transport.parts[part_id]
        assert record.material == "cast_opal_pmma_3mm"
        (x_min, x_max), (y_min, y_max), (z_min, z_max) = bounding_box_bounds(record.solid)
        assert x_min == pytest.approx(inset, abs=0.5)
        assert x_max == pytest.approx(width - inset, abs=0.5)
        assert y_min == pytest.approx(0.0, abs=0.5)
        assert y_max == pytest.approx(profile, abs=0.5)
        assert z_min >= foot_h - 0.5
        assert z_max - z_min == pytest.approx(profile, abs=0.5)


def test_top_warm_member_is_light_strip(params, transport, datums):
    """PLT-006/007 AC-C4 — warm top bar is LIGHT-STRIP-001, not a shelf divider."""
    light = transport.parts["LIGHT-STRIP-001"]
    shelf = transport.parts["SHELF-002"]
    light_bb = bounding_box_bounds(light.solid)
    shelf_bb = bounding_box_bounds(shelf.solid)
    top_z = float(params.value("top_structure.z_min_mm"))
    (_lx0, _lx1), (_ly_min, _ly1), (lz_min, _lz1) = light_bb
    (_sx0, _sx1), (_sy_min, _sy1), (sz_min, sz_max) = shelf_bb
    assert lz_min == pytest.approx(top_z, abs=1.0)
    assert sz_max < datums.organizer_floor_top_z_mm + params.horizontal_shelf_stack_height_mm
    assert light.material == "service_volume"
    assert shelf.material == "transparent_petg_2mm"
    assert lz_min >= top_z - 1.0
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


def test_frame_posts_start_at_foot_height(params, transport):
    """PLT-005 F-2 — corner posts sit on foot top, not on Z=0."""
    foot_h = float(params.value("materials.foot_height_mm"))
    tol = float(params.value("tolerance.part_assembly_feature_mm"))
    for part_id in (
        "FRAME-POST-FL-001",
        "FRAME-POST-FR-001",
        "FRAME-POST-RL-001",
        "FRAME-POST-RR-001",
    ):
        bounds = bounding_box_bounds(transport.parts[part_id].solid)
        assert bounds[2][0] == pytest.approx(foot_h, abs=tol + 0.5)


def test_foot_frame_post_no_z0_interpenetration(params, transport):
    """PLT-005 F-2 — foot volume band Z[0,foot_h] contains only the foot."""
    from stand_cad.geometry.collision import is_foot_structure_contact

    foot_h = float(params.value("materials.foot_height_mm"))
    threshold = float(params.value("tolerance.part_assembly_feature_mm"))
    post = transport.parts["FRAME-POST-FL-001"].solid
    foot_band = box_from_bounds(0, 0, 0, 650, 550, foot_h)
    assert intersection_volume(foot_band, post) == pytest.approx(0.0, abs=1e-3)
    assert is_foot_structure_contact(
        "FOOT-001", "FRAME-POST-FL-001", transport.parts, threshold
    )


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
    """Full tray extension — front travel clearance still below 356 mm at case.depth=550."""
    required = float(params.value("operational.material_travel_clearance_mm"))
    lower_ext = float(params.value("trays.lower_extension"))
    front = params.material_travel_clearance_front_mm(1, tray_extension_mm=lower_ext)
    assert front == pytest.approx(-235.0)
    assert front < required
    rear = params.material_travel_clearance_rear_mm(1, tray_extension_mm=lower_ext)
    assert rear == pytest.approx(590.0)
    assert rear >= required


def test_pass_through_depth_exceeds_case_envelope(params):
    """Open front-to-rear pass-through needs 907 mm — case.depth 550 mm cannot close."""
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
    assert params.material_travel_clearance_rear_mm(2) == pytest.approx(340.0)
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
    port_y = float(params.value("hardware.service_port_mount_y_mm"))
    port_z = float(params.value("hardware.service_port_mount_z_mm"))
    x_mid = width - side_clear / 2
    assert port_y == pytest.approx(275.0)
    assert solid_point_state(panel, x_mid, port_y, port_z) == "OUT"
    assert solid_point_state(panel, x_mid, port_y, port_z + 20) == "IN"
