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
    build_interlock_parts,
    tray_fully_extended_solid,
)
from stand_cad.geometry.primitives import (
    bounding_box_bounds,
    intersection_volume,
    translate_solid,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
PARAMETERS_PATH = REPO_ROOT / "config" / "parameters.yaml"


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


def test_interlock_parts_not_emitted(params, transport):
    """D-067 — owner removed interlock hardware from live assembly."""
    from stand_cad.geometry.datums import Datums
    from stand_cad.geometry.kinematics import ShuttlePosition

    datums = Datums.from_parameters(params)
    assert (
        build_interlock_parts(params, datums, shuttle_position=ShuttlePosition.NEUTRAL)
        == []
    )
    interlock_ids = [pid for pid in transport.parts if pid.startswith("INTERLOCK-")]
    assert interlock_ids == []


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


def test_tray_extension_rear_face_clearance(params, service_p1):
    """PLT-008 partial — lower tier at full service extension meets TZ overhang (D-049)."""
    overhang_min = float(params.value("trays.front_overhang_min_mm"))
    extension = float(params.value("trays.lower_extension"))
    front_y = params.material_travel_clearance_front_mm(1, tray_extension_mm=extension)
    rear_y = params.plotter_y_rear_mm(1, tray_extension_mm=extension)
    assert rear_y <= -overhang_min, (
        f"tier 1 plotter rear Y={rear_y} must be ≤ "
        f"−{overhang_min} at {extension} mm extension"
    )
    assert front_y <= 0.0, (
        f"tier 1 plotter front Y={front_y} must be ≤ 0 at "
        f"{extension} mm extension"
    )


def test_upper_tray_fixed_no_slide_out(params):
    """D-076 — upper tier access is door-open only; no slide-out travel."""
    assert float(params.value("trays.upper_extension")) == pytest.approx(0.0)


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


@pytest.mark.xfail(
    strict=True,
    reason=(
        "docs/10 §M — provisional 80 mm lid envelope exceeds measured transport headroom "
        "(tier 1 gap 27 mm / tier 2 gap 50 mm); owner redesign pending"
    ),
)
def test_lid_envelope_no_intersection_in_service_states(params, service_p1, service_p2, transport):
    """PLT-008 — provisional lid envelope vs surrounding parts (verify_on_real_machine).

    Panel/other-plotter checks pass; transport headroom canary fails until §M closed.
    """
    lid_height_mm = float(params.value("plotter.lid_open_envelope_height_mm"))
    tier_gaps_mm = (
        (
            "EQUIP-PLOTTER1-001",
            "TRAY-UPPER-001",
            "LID-ENVELOPE-P1-001",
        ),
        (
            "EQUIP-PLOTTER2-001",
            "ORG-FLOOR-001",
            "LID-ENVELOPE-P2-001",
        ),
    )
    for plotter_id, structure_id, lid_id in tier_gaps_mm:
        plotter_z_max = bounding_box_bounds(transport.parts[plotter_id].solid)[2][1]
        structure_z_min = bounding_box_bounds(transport.parts[structure_id].solid)[2][0]
        clear_gap_mm = structure_z_min - plotter_z_max
        assert clear_gap_mm >= lid_height_mm, (
            f"transport {lid_id}: {clear_gap_mm:.1f} mm headroom < "
            f"{lid_height_mm:.1f} mm provisional envelope (docs/10 §M)"
        )

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


TIER2_UNDER_TRAY_PARTS = (
    "FRAME-RAIL-TRAY-UPPER-L-001",
    "FRAME-RAIL-TRAY-UPPER-R-001",
    "FRAME-RAIL-TRAY-UPPER-C-001",
    "SLIDE-UPPER-LEFT-001",
    "SLIDE-UPPER-RIGHT-001",
    "SLIDE-UPPER-CENTER-001",
)

TRAY1_EXTENSION_POSITIONS_MM = (0, 65, 130, 180, 230, 250)

EXPECTED_TIER2_Z_GAP_MM = {
    "FRAME-RAIL-TRAY-UPPER-L-001": 11.0,
    "FRAME-RAIL-TRAY-UPPER-R-001": 11.0,
    "FRAME-RAIL-TRAY-UPPER-C-001": 11.0,
    "SLIDE-UPPER-LEFT-001": 26.0,
    "SLIDE-UPPER-RIGHT-001": 26.0,
    "SLIDE-UPPER-CENTER-001": 26.0,
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
        "operating_with_test_bodies",
        "service_plotter_1",
        "tray1_quick_access",
        "service_plotter_2",
    ],
)
def test_numeric_collision_clearance(params, builder_name):
    """Ruling 5 — mating-pair allowlist; all other pairs >= part_assembly_feature_mm."""
    builders = {
        "transport": build_transport_assembly,
        "operating_with_test_bodies": build_operating_with_test_bodies_assembly,
        "service_plotter_1": build_service_plotter_1_assembly,
        "tray1_quick_access": build_tray1_quick_access_assembly,
        "service_plotter_2": build_service_plotter_2_assembly,
    }
    state = builders[builder_name](params)
    violations = check_collision_pairs(state.parts, params, builder_name)
    assert violations == [], "\n".join(violations[:20])


OPEN_DOOR_SERVICE_STATES = (
    ("service_plotter_1", build_service_plotter_1_assembly),
    ("tray1_quick_access", build_tray1_quick_access_assembly),
    ("service_plotter_2", build_service_plotter_2_assembly),
)

DOOR_TRAY_KINEMATIC_PREFIXES = (
    "TRAY-",
    "SLIDE-",
    "EQUIP-PLOTTER",
)

LOWER_DOOR_CLEARANCE_EXTENSIONS_MM = (0, 130, 180, 250)


@pytest.mark.parametrize("builder_name,builder", OPEN_DOOR_SERVICE_STATES)
def test_open_door_service_states_collision_clear(params, builder_name, builder):
    """D-076 — full collision sweep clean for open-door service configurations."""
    state = builder(params)
    violations = check_collision_pairs(state.parts, params, builder_name)
    assert violations == [], "\n".join(violations[:20])


def _door_strut_ids(parts: dict, *, level: str) -> list[str]:
    prefix = f"DOOR-STRUT-{level.upper()}-"
    return sorted(pid for pid in parts if pid.startswith(prefix))


def _kinematic_target_ids(parts: dict, *, level: str) -> list[str]:
    level_token = level.upper()
    return sorted(
        pid
        for pid in parts
        if any(
            pid.startswith(prefix)
            for prefix in (
                f"TRAY-{level_token}-",
                f"SLIDE-{level_token}-",
                f"EQUIP-PLOTTER{1 if level == 'lower' else 2}-",
            )
        )
    )


@pytest.mark.parametrize("lower_extension_mm", LOWER_DOOR_CLEARANCE_EXTENSIONS_MM)
def test_lower_open_door_kinematic_clearance_sweep(params, lower_extension_mm):
    """D-076 — door and struts vs tray/slide/plotter vol≈0 at sampled extensions."""
    from stand_cad.geometry.assembly import _build_state

    state = _build_state(
        params,
        f"door_sweep_{lower_extension_mm}",
        lower_extension_mm=lower_extension_mm,
        door_state={"lower": "open", "upper": "closed"},
    )
    door = state.parts["DOOR-LOWER-001"].solid
    targets = _kinematic_target_ids(state.parts, level="lower")
    for target_id in targets:
        vol = intersection_volume(door, state.parts[target_id].solid)
        assert vol == pytest.approx(0.0, abs=1e-3), (
            f"dy={lower_extension_mm} DOOR-LOWER vs {target_id} vol={vol} mm^3"
        )
    for strut_id in _door_strut_ids(state.parts, level="lower"):
        strut = state.parts[strut_id].solid
        for target_id in targets:
            vol = intersection_volume(strut, state.parts[target_id].solid)
            assert vol == pytest.approx(0.0, abs=1e-3), (
                f"dy={lower_extension_mm} {strut_id} vs {target_id} vol={vol} mm^3"
            )


def test_upper_open_door_kinematic_clearance_sweep(params, service_p2):
    """D-076 — upper door/struts vs upper tray/slide/plotter vol≈0 at zero extension."""
    door = service_p2.parts["DOOR-UPPER-001"].solid
    targets = _kinematic_target_ids(service_p2.parts, level="upper")
    for target_id in targets:
        vol = intersection_volume(door, service_p2.parts[target_id].solid)
        assert vol == pytest.approx(0.0, abs=1e-3), (
            f"DOOR-UPPER vs {target_id} vol={vol} mm^3"
        )
    for strut_id in _door_strut_ids(service_p2.parts, level="upper"):
        strut = service_p2.parts[strut_id].solid
        for target_id in targets:
            vol = intersection_volume(strut, service_p2.parts[target_id].solid)
            assert vol == pytest.approx(0.0, abs=1e-3), (
                f"{strut_id} vs {target_id} vol={vol} mm^3"
            )


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
