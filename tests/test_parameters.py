"""Tests for config/parameters.yaml loader and validation."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path

import pytest

from stand_cad.parameters import (
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
            "depth": _leaf(550),
            "height": _leaf(690),
            "internal_width": _leaf(610),
        },
        "plotter": {
            "upper_setback": _leaf(150),
            "upper_y": _leaf(170),
            "lower_y": _leaf(20),
        },
        "film_storage": {
            "cells": _leaf(10),
            "divider_thickness": _leaf(2),
            "clear_width": _leaf(610),
            "clear_depth": _leaf(510),
            "clear_height": _leaf(325),
            "film_design_height": _leaf(320),
            "min_stack_width_mm": _leaf("TO_MEASURE", "to_measure"),
            "max_load_kg": _leaf(10),
        },
        "materials": {
            "divider_thickness_mm": _leaf(2),
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


def test_default_cell_width_matches_expected():
    params = load_parameters(PARAMETERS_PATH)
    assert params.cell_width_mm == pytest.approx(59.2)


def test_default_divider_count_matches_expected():
    params = load_parameters(PARAMETERS_PATH)
    assert params.divider_count == 9


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


def test_cells_below_range_fails():
    doc = _valid_doc()
    doc["film_storage"]["cells"] = _leaf(5)
    assert "PARAM-002" in _error_codes(doc)


def test_cells_above_range_fails():
    doc = _valid_doc()
    doc["film_storage"]["cells"] = _leaf(13)
    assert "PARAM-002" in _error_codes(doc)


def test_cells_at_range_boundaries_pass():
    for cells in (6, 12):
        doc = _valid_doc()
        doc["film_storage"]["cells"] = _leaf(cells)
        assert "PARAM-002" not in _error_codes(doc)


def test_cell_width_below_absolute_floor_fails():
    doc = _valid_doc()
    doc["case"]["internal_width"] = _leaf(100)
    doc["film_storage"]["cells"] = _leaf(12)
    doc["film_storage"]["divider_thickness"] = _leaf(2)
    assert "PARAM-003" in _error_codes(doc)


def test_cell_width_below_required_film_stack_fails():
    doc = _valid_doc()
    doc["film_storage"]["min_stack_width_mm"] = _leaf(60)
    assert "PARAM-004" in _error_codes(doc)


def test_cell_width_stack_check_skipped_while_to_measure():
    doc = _valid_doc()
    doc["film_storage"]["min_stack_width_mm"] = _leaf("TO_MEASURE", "to_measure")
    assert "PARAM-004" not in _error_codes(doc)


def test_organizer_clear_volume_below_minimum_fails_clear_width():
    doc = _valid_doc()
    doc["film_storage"]["clear_width"] = _leaf(609)
    assert "PARAM-005" in _error_codes(doc)


def test_organizer_clear_volume_below_minimum_fails_clear_depth():
    doc = _valid_doc()
    doc["film_storage"]["clear_depth"] = _leaf(509)
    assert "PARAM-005" in _error_codes(doc)


def test_organizer_clear_volume_below_minimum_fails_clear_height():
    doc = _valid_doc()
    doc["film_storage"]["clear_height"] = _leaf(324)
    assert "PARAM-005" in _error_codes(doc)


def test_organizer_clear_volume_at_minimum_passes():
    doc = _valid_doc()
    doc["film_storage"]["clear_width"] = _leaf(610)
    doc["film_storage"]["clear_depth"] = _leaf(510)
    doc["film_storage"]["clear_height"] = _leaf(325)
    assert "PARAM-005" not in _error_codes(doc)


def test_overall_envelope_mismatch_fails():
    doc = _valid_doc()
    doc["case"]["width"] = _leaf(651)
    assert "PARAM-006" in _error_codes(doc)


def test_overall_envelope_match_passes():
    doc = _valid_doc()
    assert "PARAM-006" not in _error_codes(doc)


def test_plotter_setback_not_150_fails():
    doc = _valid_doc()
    doc["plotter"]["upper_setback"] = _leaf(149)
    assert "PARAM-007" in _error_codes(doc)


def test_plotter_setback_150_passes():
    doc = _valid_doc()
    assert "PARAM-007" not in _error_codes(doc)


def test_plotter_setback_inconsistent_with_coordinates_fails():
    doc = _valid_doc()
    doc["plotter"]["upper_y"] = _leaf(180)
    assert "PARAM-008" in _error_codes(doc)


def test_film_headroom_below_5mm_fails():
    doc = _valid_doc()
    doc["film_storage"]["clear_height"] = _leaf(324)
    doc["film_storage"]["film_design_height"] = _leaf(320)
    assert "PARAM-009" in _error_codes(doc)


def test_film_headroom_exactly_5mm_passes():
    doc = _valid_doc()
    doc["film_storage"]["clear_height"] = _leaf(325)
    doc["film_storage"]["film_design_height"] = _leaf(320)
    assert "PARAM-009" not in _error_codes(doc)


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
    assert len(rel027) == 41
    paths = {issue.message.split(":")[0] for issue in rel027}
    assert paths == {
        "film_storage.comb_rail_front_depth_mm",
        "film_storage.comb_slot_depth_mm",
        "film_storage.min_stack_width_mm",
        "hardware.vent_band_z_mm",
        "hardware.vent_slot_count",
        "hardware.vent_slot_height_mm",
        "hardware.vent_slot_pitch_mm",
        "hardware.vent_slot_width_mm",
        "materials.actual_sheet_thickness_mm",
        "materials.org_insert_thickness_mm",
        "materials.tray_panel_youngs_modulus_mpa",
        "plotter.feed_plane_z_from_base",
        "plotter.feed_plane_z_provisional_mm",
        "plotter.lid_open_envelope_height_mm",
        "services.adapter_light_depth_mm",
        "services.adapter_light_height_mm",
        "services.adapter_light_width_mm",
        "services.adapter_plotter_depth_mm",
        "services.adapter_plotter_height_mm",
        "services.adapter_plotter_width_mm",
        "services.airpath_depth_mm",
        "services.airpath_height_mm",
        "services.airpath_width_mm",
        "services.cable_channel_height_mm",
        "services.cable_channel_width_mm",
        "services.ctrl_rgbw_depth_mm",
        "services.ctrl_rgbw_height_mm",
        "services.ctrl_rgbw_width_mm",
        "services.edgeguard_depth_mm",
        "services.light_strip_height_mm",
        "services.light_strip_length_mm",
        "services.light_strip_width_mm",
        "services.mains_inlet_depth_mm",
        "services.mains_inlet_height_mm",
        "services.mains_inlet_width_mm",
        "services.rearsupport_depth_mm",
        "trays.slide_rail_height_mm",
        "trays.slide_rail_width_mm",
        "trays.soft_stop_size_mm",
        "trays.vibration_mount_diameter_mm",
        "trays.vibration_mount_height_mm",
    }


def test_production_release_passes_with_no_to_measure_parameters():
    doc = deepcopy(_valid_doc())
    doc["film_storage"]["min_stack_width_mm"] = _leaf(25)
    doc["plotter"] = {
        "upper_setback": _leaf(150),
        "upper_y": _leaf(170),
        "lower_y": _leaf(20),
        "feed_plane_z_from_base": _leaf(50),
    }
    doc["materials"] = {
        "divider_thickness_mm": _leaf(2),
        "actual_sheet_thickness_mm": _leaf(3.0),
    }
    doc["mass_targets"] = {"film_marked_limit_kg": _leaf(10)}
    doc["film_storage"]["max_load_kg"] = _leaf(10)
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
    assert len(rel027) == 41


def test_validate_release_readiness_clean_synthetic_doc_has_zero_errors():
    project, equipment = _production_project_and_equipment()
    doc = deepcopy(_valid_doc())
    doc["film_storage"]["min_stack_width_mm"] = _leaf(25)
    doc["plotter"] = {
        "upper_setback": _leaf(150),
        "upper_y": _leaf(170),
        "lower_y": _leaf(20),
        "feed_plane_z_from_base": _leaf(50),
    }
    doc["materials"] = {
        "divider_thickness_mm": _leaf(2),
        "actual_sheet_thickness_mm": _leaf(3.0),
    }
    doc["mass_targets"] = {"film_marked_limit_kg": _leaf(10)}
    params = _params_from_doc(doc)
    issues = validate_release_readiness(project, equipment, params)
    errors = [issue for issue in issues if issue.severity == "ERROR"]
    assert errors == []
