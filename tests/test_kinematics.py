# A passing test is not evidence of physical correctness.
"""Kinematics, interlock, and collision tests for Packet 2-3."""

from __future__ import annotations

from pathlib import Path

import pytest

from stand_cad.geometry.assembly import (
    build_operating_with_test_bodies_assembly,
    build_service_plotter_1_assembly,
    build_service_plotter_2_assembly,
    build_transport_assembly,
    build_tray1_quick_access_assembly,
)
from stand_cad.geometry.collision import (
    COLLISION_THRESHOLD_PATH,
    check_collision_pairs,
    check_containment_pairs,
)
from stand_cad.geometry.kinematics import (
    apply_tray_extension,
    slides_fully_extended_solids,
    tray_fully_extended_solid,
)
from stand_cad.geometry.primitives import (
    bounding_box_bounds,
    intersection_volume,
    translate_solid,
)
from stand_cad.parameters import load_parameters

REPO_ROOT = Path(__file__).resolve().parents[1]
PARAMETERS_PATH = REPO_ROOT / "config" / "parameters.yaml"


@pytest.fixture(scope="module")
def params():
    return load_parameters(PARAMETERS_PATH)


@pytest.fixture(scope="module")
def transport(params):
    return build_transport_assembly(params)


@pytest.fixture(scope="module")
def service_p1(params):
    return build_service_plotter_1_assembly(params)


@pytest.fixture(scope="module")
def service_p2(params):
    return build_service_plotter_2_assembly(params)


@pytest.fixture(scope="module")
def tray1_quick_access(params):
    return build_tray1_quick_access_assembly(params)


def _extended_tray_solid(params, level: str):
    from stand_cad.geometry.datums import Datums

    datums = Datums.from_parameters(params)
    return tray_fully_extended_solid(params, datums, level)


def test_centre_slide_rails_exist_kinematic_and_clear(params, transport):
    """PLT-011/PLT-008 — centre slides in kinematic group and full-extension set."""
    from stand_cad.geometry.datums import Datums
    from stand_cad.geometry.kinematics import (
        LOWER_KINEMATIC_GROUP,
        UPPER_KINEMATIC_GROUP,
        slides_fully_extended_solids,
    )

    for slide_id, group in (
        ("SLIDE-LOWER-CENTER-001", LOWER_KINEMATIC_GROUP),
        ("SLIDE-UPPER-CENTER-001", UPPER_KINEMATIC_GROUP),
    ):
        assert slide_id in transport.parts
        assert slide_id in group
        rail_id = slide_id.replace("SLIDE-", "FRAME-RAIL-TRAY-").replace(
            "CENTER-001", "C-001"
        )
        assert rail_id in transport.parts
        assert rail_id not in group

    datums = Datums.from_parameters(params)
    assert len(slides_fully_extended_solids(params, datums, "lower")) == 3
    assert len(slides_fully_extended_solids(params, datums, "upper")) == 3

    shuttle_x = bounding_box_bounds(transport.parts["INTERLOCK-SHUTTLE-001"].solid)[0]
    center_x = bounding_box_bounds(transport.parts["SLIDE-LOWER-CENTER-001"].solid)[0]
    assert center_x[1] <= shuttle_x[0] or center_x[0] >= shuttle_x[1], (
        "centre slide X-window must not overlap interlock shuttle X-window"
    )


def test_centre_slide_clear_of_soft_stop(params, transport):
    """PLT-008 F-1 — centre slide must not volumetrically overlap rear soft stop."""
    for soft_id, slide_id in (
        ("SOFTSTOP-LOWER-001", "SLIDE-LOWER-CENTER-001"),
        ("SOFTSTOP-UPPER-001", "SLIDE-UPPER-CENTER-001"),
    ):
        vol = intersection_volume(
            transport.parts[soft_id].solid,
            transport.parts[slide_id].solid,
        )
        assert vol == pytest.approx(0.0, abs=1e-3), (
            f"{soft_id} vs {slide_id} intersection {vol} mm^3 must be zero"
        )


def test_centre_slide_clear_of_media_test_bodies(params):
    """PLT-008 F-2 — centre slides clear of all media-path test bodies on both tiers."""
    operating = build_operating_with_test_bodies_assembly(params)
    for level in ("L1", "L2"):
        slide_id = f"SLIDE-{'LOWER' if level == 'L1' else 'UPPER'}-CENTER-001"
        center_slide = operating.parts[slide_id].solid
        for body_kind in ("PRIMARY", "LONG"):
            body_id = f"TESTBODY-{body_kind}-{level}-001"
            vol = intersection_volume(center_slide, operating.parts[body_id].solid)
            assert vol == pytest.approx(0.0, abs=1e-3), (
                f"{slide_id} intersects {body_id} by {vol} mm^3"
            )


def test_tray_extension_rear_face_clearance(params, service_p1, service_p2):
    """PLT-008 partial — rear face past front plane by front_overhang_min_mm."""
    front_limit = -float(params.value("trays.front_overhang_min_mm"))
    for state, tray_id in (
        (service_p1, "TRAY-LOWER-001"),
        (service_p2, "TRAY-UPPER-001"),
    ):
        bounds = bounding_box_bounds(state.parts[tray_id].solid)
        rear_face_y = bounds[1][1]
        assert rear_face_y <= front_limit, (
            f"{tray_id} rear Y={rear_face_y} must be <= {front_limit}"
        )


def test_tray1_quick_access_forward_travel_is_130mm(params, transport, tray1_quick_access):
    """D-033 — tier 1 tray forward slide is a real, dimensioned, >=130 mm travel."""
    quick_access_mm = float(params.value("trays.lower_quick_access_extension_mm"))
    assert quick_access_mm >= 130.0
    closed_front_y = bounding_box_bounds(transport.parts["TRAY-LOWER-001"].solid)[1][0]
    quick_front_y = bounding_box_bounds(tray1_quick_access.parts["TRAY-LOWER-001"].solid)[1][0]
    assert closed_front_y - quick_front_y == pytest.approx(quick_access_mm)


def test_tray1_quick_access_distinct_from_full_extension(params):
    """D-033 — quick access (130 mm) is a lesser position than full service extension (250 mm)."""
    quick_access_mm = float(params.value("trays.lower_quick_access_extension_mm"))
    full_extension_mm = float(params.value("trays.lower_extension"))
    assert quick_access_mm < full_extension_mm


def test_lid_envelope_no_intersection_in_service_states(params, service_p1, service_p2):
    """PLT-008 — provisional lid envelope vs surrounding parts (verify_on_real_machine)."""
    for state, lid_id, other_plotter_prefix in (
        (service_p1, "LID-ENVELOPE-P1-001", "EQUIP-PLOTTER2"),
        (service_p2, "LID-ENVELOPE-P2-001", "EQUIP-PLOTTER1"),
    ):
        lid = state.parts[lid_id].solid
        for part_id, record in state.parts.items():
            if part_id == lid_id:
                continue
            if part_id.startswith(other_plotter_prefix):
                vol = intersection_volume(lid, record.solid)
                assert vol == pytest.approx(0.0, abs=1e-3), (
                    f"provisional {lid_id} intersects {part_id} (VERIFY ON REAL MACHINE)"
                )
            if part_id == "PANEL-IN-MID-001" or part_id.startswith("PANEL-OUT-"):
                vol = intersection_volume(lid, record.solid)
                assert vol == pytest.approx(0.0, abs=1e-3), (
                    f"provisional {lid_id} intersects {part_id} (VERIFY ON REAL MACHINE)"
                )


def test_interlock_blocks_upper_tray_extension(params, service_p1):
    """PLT-009 — shuttle at blocks-upper interferes with upper slide rails fully extended."""
    shuttle = service_p1.parts["INTERLOCK-SHUTTLE-001"].solid
    from stand_cad.geometry.datums import Datums

    datums = Datums.from_parameters(params)
    upper_slides = slides_fully_extended_solids(params, datums, "upper")
    blocked = any(intersection_volume(shuttle, slide) > 1e-3 for slide in upper_slides)
    assert blocked, "shuttle must block upper slide path in service_plotter_1"


def test_interlock_blocks_lower_tray_extension(params, service_p2):
    """PLT-009 — shuttle at blocks-lower interferes with lower slide rails fully extended."""
    shuttle = service_p2.parts["INTERLOCK-SHUTTLE-001"].solid
    from stand_cad.geometry.datums import Datums

    datums = Datums.from_parameters(params)
    lower_slides = slides_fully_extended_solids(params, datums, "lower")
    blocked = any(intersection_volume(shuttle, slide) > 1e-3 for slide in lower_slides)
    assert blocked, "shuttle must block lower slide path in service_plotter_2"


def test_interlock_shuttle_neutral_no_tray_interference(params, transport):
    """PLT-009 — neutral shuttle must not intersect closed tray volumes."""
    shuttle = transport.parts["INTERLOCK-SHUTTLE-001"].solid
    for tray_id in ("TRAY-LOWER-001", "TRAY-UPPER-001"):
        vol = intersection_volume(shuttle, transport.parts[tray_id].solid)
        assert vol == pytest.approx(0.0, abs=1e-3), (
            f"neutral shuttle intersects closed {tray_id}"
        )


TIER2_UNDER_TRAY_PARTS = (
    "FRAME-RAIL-TRAY-UPPER-L-001",
    "FRAME-RAIL-TRAY-UPPER-R-001",
    "FRAME-RAIL-TRAY-UPPER-C-001",
    "SLIDE-UPPER-LEFT-001",
    "SLIDE-UPPER-RIGHT-001",
    "SLIDE-UPPER-CENTER-001",
    "INTERLOCK-TAB-UPPER-001",
)

TRAY1_EXTENSION_POSITIONS_MM = (0, 65, 130, 180, 250)

# Post-fix Z-gap (plotter top Z=200 → hardware bottom); constant across tray-1 travel.
EXPECTED_TIER2_Z_GAP_MM = {
    "FRAME-RAIL-TRAY-UPPER-L-001": 11.0,
    "FRAME-RAIL-TRAY-UPPER-R-001": 11.0,
    "FRAME-RAIL-TRAY-UPPER-C-001": 11.0,
    "SLIDE-UPPER-LEFT-001": 26.0,
    "SLIDE-UPPER-RIGHT-001": 26.0,
    "SLIDE-UPPER-CENTER-001": 26.0,
    "INTERLOCK-TAB-UPPER-001": 15.0,
}


def _plotter1_tier2_z_gap_mm(plotter_solid, hardware_solid) -> float:
    """Vertical gap between plotter 1 top and tier-2 under-tray hardware bottom."""
    plotter_bounds = bounding_box_bounds(plotter_solid)
    hardware_bounds = bounding_box_bounds(hardware_solid)
    plotter_z_max = plotter_bounds[2][1]
    hardware_z_min = hardware_bounds[2][0]
    if hardware_z_min >= plotter_z_max:
        return hardware_z_min - plotter_z_max
    return 0.0


@pytest.mark.parametrize("lower_extension_mm", TRAY1_EXTENSION_POSITIONS_MM)
@pytest.mark.parametrize("hardware_id", TIER2_UNDER_TRAY_PARTS)
def test_plotter1_clear_of_tier2_under_tray_hardware(
    params, transport, lower_extension_mm, hardware_id
):
    """PLT-009 F-5 — zero intersection vs tier-2 under-tray stack at all tray-1 positions."""
    parts = apply_tray_extension(
        transport.parts,
        lower_extension_mm=lower_extension_mm,
        upper_extension_mm=0.0,
    )
    plotter = parts["EQUIP-PLOTTER1-001"].solid
    hardware = parts[hardware_id].solid
    vol = intersection_volume(plotter, hardware)
    z_gap = _plotter1_tier2_z_gap_mm(plotter, hardware)
    assert vol == pytest.approx(0.0, abs=1e-3), (
        f"dy={lower_extension_mm} {hardware_id} intersects plotter by {vol} mm^3"
    )
    expected_z_gap = EXPECTED_TIER2_Z_GAP_MM[hardware_id]
    assert z_gap == pytest.approx(expected_z_gap, abs=0.5), (
        f"dy={lower_extension_mm} {hardware_id} Z-gap={z_gap} mm (expected {expected_z_gap} mm)"
    )


@pytest.mark.parametrize(
    "builder_name",
    [
        "transport",
        "service_plotter_1",
        "service_plotter_2",
        "operating_with_test_bodies",
        "tray1_quick_access",
    ],
)
def test_numeric_collision_clearance(params, builder_name):
    """Ruling 5 — mating-pair allowlist; all other pairs >= part_assembly_feature_mm."""
    builders = {
        "transport": build_transport_assembly,
        "service_plotter_1": build_service_plotter_1_assembly,
        "service_plotter_2": build_service_plotter_2_assembly,
        "operating_with_test_bodies": build_operating_with_test_bodies_assembly,
        "tray1_quick_access": build_tray1_quick_access_assembly,
    }
    state = builders[builder_name](params)
    violations = check_collision_pairs(state.parts, params, builder_name)
    assert violations == [], "\n".join(violations[:20])


def test_operating_with_test_bodies_builds(params):
    """PLT-007 partial — operating state exists with test body volumes."""
    state = build_operating_with_test_bodies_assembly(params)
    assert "TESTBODY-PRIMARY-L1-001" in state.parts
    assert "TESTBODY-LONG-L2-001" in state.parts
    assert state.parts["TESTBODY-PRIMARY-L1-001"].solid.volume > 0


def test_collision_threshold_from_parameters(params):
    """Document threshold path used by collision sweep."""
    assert float(params.value(COLLISION_THRESHOLD_PATH)) == pytest.approx(0.5)


def test_equipment_containment_in_envelope(params, transport):
    """PLT-002 — equipment bodies must be fully contained in design envelopes."""
    violations = check_containment_pairs(transport.parts, params)
    assert violations == []


def test_equipment_containment_fails_when_mispositioned(params, transport):
    """PLT-002 regression — containment check fails on deliberate mis-position."""
    from stand_cad.geometry.registry import PartRecord

    equip = transport.parts["EQUIP-PLOTTER1-001"]
    shifted = PartRecord(
        part_id=equip.part_id,
        material=equip.material,
        solid=translate_solid(equip.solid, dz=50.0),
    )
    misaligned = dict(transport.parts)
    misaligned[equip.part_id] = shifted
    misaligned_violations = check_containment_pairs(misaligned, params)
    assert misaligned_violations != []
    assert check_containment_pairs(transport.parts, params) == []
