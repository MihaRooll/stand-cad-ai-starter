"""Tests for config/parameters.yaml loader and validation."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest

from stand_cad.geometry.assembly import build_transport_assembly
from stand_cad.geometry.primitives import bounding_box_bounds, bounding_box_size
from stand_cad.parameters import (
    HORIZONTAL_SHELF_COUNT,
    MIN_LOWER_QUICK_ACCESS_EXTENSION_MM,
    REQUIRED_CASE_WIDTH_MM,
    REQUIRED_UPPER_SETBACK_MM,
    Parameters,
    load_parameters,
    validate_parameters,
    validate_release_readiness,
)

REPO_ROOT = Path(__file__).resolve().parents[1]
PARAMETERS_PATH = REPO_ROOT / "config" / "parameters.yaml"


def _leaf(value: object, provenance: str = "verified", note: str = "") -> dict:
    return {"value": value, "provenance": provenance, "note": note}


def _valid_doc() -> dict:
    """Minimal complete nested dict with passing values for validation rules."""
    return {
        "schema_version": 1,
        "units": "mm",
        "case": {
            "width": _leaf(650),
            "depth": _leaf(420),
            "height": _leaf(502),
            "internal_width": _leaf(610),
            "depth_tolerance_mm": _leaf(5, "derived"),
        },
        "plotter": {
            "upper_setback": _leaf(0),
            "upper_y": _leaf(15),
            "lower_y": _leaf(15),
            "lower_z": _leaf(30),
            "upper_z": _leaf(211),
            "tier_clearance_min_mm": _leaf(170),
            "physical_width": _leaf(570),
            "physical_depth": _leaf(195),
            "physical_height": _leaf(170),
            "design_width": _leaf(584),
            "design_depth": _leaf(219),
            "design_height": _leaf(178),
            "x": _leaf(40, "derived"),
        },
        "plotter_cameo4": {
            "width_mm": _leaf(570),
            "depth_mm": _leaf(195),
            "height_mm": _leaf(170),
            "mass_kg": _leaf(4.7),
        },
        "plotter_cameo5": {
            "width_mm": _leaf(566),
            "depth_mm": _leaf(176),
            "height_mm": _leaf(124),
            "mass_kg": _leaf(5.2),
        },
        "trays": {
            "lower_extension": _leaf(250),
            "upper_extension": _leaf(0),
            "lower_quick_access_extension_mm": _leaf(130),
            "front_overhang_min_mm": _leaf(40),
        },
        "operational": {
            "material_travel_clearance_mm": _leaf(356),
        },
        "film_storage_horizontal": {
            "shelf_count": _leaf(4),
            "divider_thickness": _leaf(2),
            "clear_width": _leaf(610),
            "clear_depth": _leaf(330),
            "compartment_clear_height_mm": _leaf(25),
            "z": _leaf(396),
            "x": _leaf(20),
            "max_load_kg": _leaf(10),
        },
        "materials": {
            "divider_thickness_mm": _leaf(2),
            "frame_profile_size_mm": _leaf(15),
            "tray_panel_thickness_min_mm": _leaf(10),
            "tray_panel_thickness_max_mm": _leaf(12),
        },
        "top_structure": {
            "height_mm": _leaf(0),
            "z_min_mm": _leaf(529),
            "z_max_mm": _leaf(529),
        },
        "mass_targets": {
            "film_marked_limit_kg": _leaf(10),
        },
    }


def _params_from_doc(doc: dict) -> Parameters:
    return Parameters(doc)


def _error_codes(doc: dict, *, production_release: bool = False) -> set[str]:
    issues = validate_parameters(_params_from_doc(doc), production_release=production_release)
    return {issue.code for issue in issues if issue.severity == "ERROR"}


def test_repository_parameters_yaml_loads_and_validates_clean():
    params = load_parameters(PARAMETERS_PATH)
    issues = validate_parameters(params)
    errors = [issue for issue in issues if issue.severity == "ERROR"]
    assert errors == []


def test_default_shelf_stack_height_matches_expected():
    params = load_parameters(PARAMETERS_PATH)
    assert params.horizontal_shelf_stack_height_mm == pytest.approx(106.0)


def test_default_shelf_divider_count_matches_expected():
    params = load_parameters(PARAMETERS_PATH)
    assert params.horizontal_shelf_divider_count == 3


def test_computed_case_height_matches_yaml():
    params = load_parameters(PARAMETERS_PATH)
    assert params.computed_case_height_mm == pytest.approx(529.0)
    assert float(params.value("case.height")) == pytest.approx(529.0)


def test_computed_upper_z_mm_matches_yaml():
    params = load_parameters(PARAMETERS_PATH)
    assert params.computed_upper_z_mm == pytest.approx(float(params.value("plotter.upper_z")))

    transport = build_transport_assembly(params)
    tray_bounds = bounding_box_bounds(transport.parts["TRAY-UPPER-001"].solid)
    tray_top_z_mm = tray_bounds[2][1]
    tolerance = float(params.value("tolerance.part_assembly_feature_mm"))
    assert tray_top_z_mm == pytest.approx(params.computed_upper_z_mm, abs=tolerance), (
        "TRAY-UPPER-001 top Z must match computed upper tray datum"
    )


def test_tier_clearances_meet_minimum():
    params = load_parameters(PARAMETERS_PATH)
    tier_min = float(params.value("plotter.tier_clearance_min_mm"))
    assert params.tier_clearance_lower_mm >= tier_min
    assert params.tier_clearance_upper_mm >= tier_min


def test_missing_provenance_marker_fails():
    doc = _valid_doc()
    doc["case"]["width"] = {"value": 650}
    assert "PARAM-001" in _error_codes(doc)


def test_invalid_provenance_value_fails():
    doc = _valid_doc()
    doc["case"]["width"] = _leaf(650, "guess")
    assert "PARAM-001" in _error_codes(doc)


def test_bare_scalar_leaf_surfaces_param_001():
    doc = _valid_doc()
    doc["case"]["width"] = 650
    issues = validate_parameters(_params_from_doc(doc))
    assert any(issue.code == "PARAM-001" for issue in issues)


def test_shelf_count_not_four_fails():
    doc = _valid_doc()
    doc["film_storage_horizontal"]["shelf_count"] = _leaf(3)
    assert "PARAM-002" in _error_codes(doc)


def test_shelf_count_four_passes():
    doc = _valid_doc()
    assert "PARAM-002" not in _error_codes(doc)


def test_organizer_clear_volume_below_minimum_fails_clear_width():
    doc = _valid_doc()
    doc["film_storage_horizontal"]["clear_width"] = _leaf(609)
    assert "PARAM-005" in _error_codes(doc)


def test_organizer_clear_volume_below_minimum_fails_clear_depth():
    doc = _valid_doc()
    doc["film_storage_horizontal"]["clear_depth"] = _leaf(329)
    assert "PARAM-005" in _error_codes(doc)


def test_organizer_clear_volume_at_minimum_passes():
    doc = _valid_doc()
    doc["film_storage_horizontal"]["clear_width"] = _leaf(610)
    doc["film_storage_horizontal"]["clear_depth"] = _leaf(330)
    assert "PARAM-005" not in _error_codes(doc)


def test_overall_width_mismatch_fails():
    doc = _valid_doc()
    doc["case"]["width"] = _leaf(651)
    assert "PARAM-006" in _error_codes(doc)


def test_overall_depth_outside_tolerance_fails():
    doc = _valid_doc()
    doc["case"]["depth"] = _leaf(426)
    assert "PARAM-006" in _error_codes(doc)


def test_overall_envelope_match_passes():
    doc = _valid_doc()
    assert "PARAM-006" not in _error_codes(doc)


def test_case_height_inconsistent_with_stack_fails():
    doc = _valid_doc()
    doc["case"]["height"] = _leaf(690)
    assert "PARAM-006" in _error_codes(doc)


def test_plotter_setback_nonzero_fails():
    doc = _valid_doc()
    doc["plotter"]["upper_setback"] = _leaf(130)
    assert "PARAM-007" in _error_codes(doc)


def test_plotter_setback_zero_passes():
    doc = _valid_doc()
    assert "PARAM-007" not in _error_codes(doc)


def test_plotter_setback_inconsistent_with_coordinates_fails():
    doc = _valid_doc()
    doc["plotter"]["upper_y"] = _leaf(180)
    assert "PARAM-008" in _error_codes(doc)


def test_quick_access_extension_below_minimum_fails():
    doc = _valid_doc()
    doc["trays"]["lower_quick_access_extension_mm"] = _leaf(129)
    assert "PARAM-013" in _error_codes(doc)


def test_quick_access_extension_at_minimum_passes():
    doc = _valid_doc()
    doc["trays"]["lower_quick_access_extension_mm"] = _leaf(130)
    assert "PARAM-013" not in _error_codes(doc)
    assert "PARAM-014" not in _error_codes(doc)


def test_quick_access_extension_not_less_than_full_extension_fails():
    doc = _valid_doc()
    doc["trays"]["lower_quick_access_extension_mm"] = _leaf(250)
    assert "PARAM-014" in _error_codes(doc)


def test_tier_clearance_below_minimum_fails():
    doc = _valid_doc()
    doc["plotter"]["upper_z"] = _leaf(200)
    assert "PARAM-012" in _error_codes(doc)


def test_divider_thickness_cross_check_fails():
    doc = _valid_doc()
    doc["materials"]["divider_thickness_mm"] = _leaf(3)
    assert "PARAM-010" in _error_codes(doc)


def test_divider_thickness_cross_check_passes():
    doc = _valid_doc()
    assert "PARAM-010" not in _error_codes(doc)


def test_film_load_limit_cross_check_fails():
    doc = _valid_doc()
    doc["mass_targets"]["film_marked_limit_kg"] = _leaf(12)
    assert "PARAM-011" in _error_codes(doc)


def test_film_load_limit_cross_check_passes():
    doc = _valid_doc()
    assert "PARAM-011" not in _error_codes(doc)


def test_production_release_blocks_on_to_measure_parameters():
    params = load_parameters(PARAMETERS_PATH)
    issues = validate_parameters(params, production_release=True)
    rel027 = [issue for issue in issues if issue.code == "REL-027"]
    assert len(rel027) == 55
    paths = {issue.message.split(":")[0] for issue in rel027}
    assert "hardware.service_port_cutout_width_mm" in paths
    assert "hardware.service_port_cutout_height_mm" in paths
    assert "plotter_cameo4.width_mm" not in paths


def test_production_release_passes_with_no_to_measure_parameters():
    doc = deepcopy(_valid_doc())
    doc["plotter"].update({
        "upper_setback": _leaf(0),
        "upper_y": _leaf(15),
        "lower_y": _leaf(15),
        "lower_z": _leaf(30),
        "upper_z": _leaf(211),
        "tier_clearance_min_mm": _leaf(170),
        "feed_plane_z_from_base": _leaf(50),
    })
    doc["plotter_cameo4"] = {
        "height_mm": _leaf(170),
        "width_mm": _leaf(580),
        "depth_mm": _leaf(200),
    }
    doc["materials"] = {
        "divider_thickness_mm": _leaf(2),
        "frame_profile_size_mm": _leaf(15),
        "tray_panel_thickness_min_mm": _leaf(10),
        "tray_panel_thickness_max_mm": _leaf(12),
        "actual_sheet_thickness_mm": _leaf(3.0),
    }
    doc["mass_targets"] = {"film_marked_limit_kg": _leaf(10)}
    doc["film_storage_horizontal"]["max_load_kg"] = _leaf(10)
    issues = validate_parameters(_params_from_doc(doc), production_release=True)
    rel027 = [issue for issue in issues if issue.code == "REL-027"]
    assert rel027 == []


def _production_project_and_equipment():
    project = {
        "schema_version": 1,
        "project": {
            "id": "PLT",
            "mode": "production",
            "production_release": True,
            "release_kind": "prototype",
            "revision": "A",
            "units": "mm",
        },
        "constraints": {
            "max_outer_width_mm": 1000,
            "max_outer_depth_mm": 800,
            "max_outer_height_mm": 1200,
            "max_total_mass_kg": 100,
            "constraints_verified": True,
        },
        "workflow": {"workflow_verified": True},
        "manufacturing": {
            "target_manufacturer": "Example Manufacturer",
            "dfm_record_id": "DFM-001",
            "uses_bent_sheet_metal": False,
            "bend_data_confirmed": False,
            "flat_pattern_owner": "TBD",
        },
    }
    equipment = {
        "schema_version": 1,
        "equipment": [
            {
                "id": "CAMEO5",
                "manufacturer": "Silhouette",
                "enabled": True,
                "quantity": 2,
                "width_mm": 566,
                "depth_mm": 176,
                "height_mm": 124,
                "mass_kg": 5.2,
                "verified": True,
                "envelopes_verified": True,
                "support_verified": True,
                "transport_verified": True,
                "powered": False,
                "heat_source": False,
                "model": "Cameo 5",
                "source_type": "user_measurement",
                "source_reference": "TZ section 3",
                "transport_orientation": "upright",
            }
        ],
    }
    return project, equipment


def test_validate_release_readiness_surfaces_rel027_with_real_config():
    project, equipment = _production_project_and_equipment()
    params = load_parameters(PARAMETERS_PATH)
    issues = validate_release_readiness(project, equipment, params)
    rel027 = [issue for issue in issues if issue.code == "REL-027"]
    assert len(rel027) == 55


def test_validate_release_readiness_clean_synthetic_doc_has_zero_errors():
    project, equipment = _production_project_and_equipment()
    doc = deepcopy(_valid_doc())
    doc["plotter"].update({
        "upper_setback": _leaf(0),
        "upper_y": _leaf(15),
        "lower_y": _leaf(15),
        "lower_z": _leaf(30),
        "upper_z": _leaf(211),
        "tier_clearance_min_mm": _leaf(170),
        "feed_plane_z_from_base": _leaf(50),
    })
    doc["plotter_cameo4"] = {
        "height_mm": _leaf(170),
        "width_mm": _leaf(580),
        "depth_mm": _leaf(200),
    }
    doc["materials"] = {
        "divider_thickness_mm": _leaf(2),
        "frame_profile_size_mm": _leaf(15),
        "tray_panel_thickness_min_mm": _leaf(10),
        "tray_panel_thickness_max_mm": _leaf(12),
        "actual_sheet_thickness_mm": _leaf(3.0),
    }
    doc["mass_targets"] = {"film_marked_limit_kg": _leaf(10)}
    params = _params_from_doc(doc)
    issues = validate_release_readiness(project, equipment, params)
    errors = [issue for issue in issues if issue.severity == "ERROR"]
    assert errors == []


def test_design_envelope_derived_from_cameo4():
    params = load_parameters(PARAMETERS_PATH)
    assert float(params.value("plotter.design_width")) == pytest.approx(584.0)
    assert float(params.value("plotter.design_depth")) == pytest.approx(219.0)
    assert float(params.value("plotter.design_height")) == pytest.approx(178.0)
    assert params.envelope_offset_x_mm == pytest.approx(7.0)
    assert params.envelope_offset_y_mm == pytest.approx(12.0)
    assert params.envelope_offset_z_mm == pytest.approx(4.0)

    transport = build_transport_assembly(params)
    env_bounds = bounding_box_bounds(transport.parts["ENV-PLOTTER1-001"].solid)
    equip_bounds = bounding_box_bounds(transport.parts["EQUIP-PLOTTER1-001"].solid)
    env_size = bounding_box_size(transport.parts["ENV-PLOTTER1-001"].solid)
    tolerance = float(params.value("tolerance.part_assembly_feature_mm"))

    assert env_size[0] == pytest.approx(float(params.value("plotter.design_width")), abs=tolerance)
    assert env_size[1] == pytest.approx(float(params.value("plotter.design_depth")), abs=tolerance)
    assert env_size[2] == pytest.approx(float(params.value("plotter.design_height")), abs=tolerance)

    assert env_bounds[0][0] - equip_bounds[0][0] == pytest.approx(
        -params.envelope_offset_x_mm, abs=tolerance
    )
    assert env_bounds[0][1] - equip_bounds[0][1] == pytest.approx(
        params.envelope_offset_x_mm, abs=tolerance
    )
    assert env_bounds[1][0] - equip_bounds[1][0] == pytest.approx(
        -params.envelope_offset_y_mm, abs=tolerance
    )
    assert env_bounds[1][1] - equip_bounds[1][1] == pytest.approx(
        params.envelope_offset_y_mm, abs=tolerance
    )
    assert env_bounds[2][0] - equip_bounds[2][0] == pytest.approx(
        -params.envelope_offset_z_mm, abs=tolerance
    )
    assert env_bounds[2][1] - equip_bounds[2][1] == pytest.approx(
        params.envelope_offset_z_mm, abs=tolerance
    )


def test_side_slab_thickness_and_clear_width():
    params = load_parameters(PARAMETERS_PATH)
    assert params.side_slab_thickness_mm == pytest.approx(20.0)
    assert float(params.value("case.internal_width")) == pytest.approx(610.0)
    per_side = (610 - 570) / 2
    assert per_side == pytest.approx(20.0)
    assert REQUIRED_CASE_WIDTH_MM == 650
    assert REQUIRED_UPPER_SETBACK_MM == 0
    assert MIN_LOWER_QUICK_ACCESS_EXTENSION_MM == 130
    assert HORIZONTAL_SHELF_COUNT == 4


def test_validate_parameters_missing_required_leaf_returns_issue_not_keyerror():
    doc = deepcopy(_valid_doc())
    del doc["plotter"]["physical_depth"]
    issues = validate_parameters(_params_from_doc(doc))
    assert any("plotter.physical_depth" in issue.message for issue in issues)
