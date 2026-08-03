import csv
from copy import deepcopy
from pathlib import Path

from stand_cad.schema import validate_documents


def base_documents():
    project = {
        "schema_version": 1,
        "project": {
            "mode": "demo",
            "production_release": False,
            "release_kind": "none",
        },
        "constraints": {},
        "workflow": {},
        "manufacturing": {},
    }
    equipment = {
        "schema_version": 1,
        "equipment": [
            {
                "id": "DEMO",
                "manufacturer": "Demo Manufacturer",
                "enabled": True,
                "quantity": 1,
                "width_mm": 100,
                "depth_mm": 100,
                "height_mm": 100,
                "mass_kg": 1,
                "verified": False,
                "envelopes_verified": False,
                "support_verified": False,
                "transport_verified": False,
                "powered": False,
                "heat_source": False,
                "model": "DEMO",
                "source_type": "synthetic_demo",
                "source_reference": "",
                "transport_orientation": "upright",
            }
        ],
    }
    return project, equipment


def test_demo_requires_explicit_permission():
    project, equipment = base_documents()
    issues = validate_documents(project, equipment)
    assert any(issue.code == "CFG-003" for issue in issues)


def test_demo_passes_when_explicitly_allowed():
    project, equipment = base_documents()
    issues = validate_documents(project, equipment, allow_demo=True)
    assert not [issue for issue in issues if issue.severity == "ERROR"]


def test_production_fails_closed_for_unverified_inputs():
    project, equipment = base_documents()
    project = deepcopy(project)
    project["project"] = {
        "id": "STAND",
        "mode": "production",
        "production_release": True,
        "release_kind": "prototype",
        "revision": "A",
        "units": "mm",
    }
    issues = validate_documents(project, equipment)
    codes = {issue.code for issue in issues}
    assert "REL-002" in codes
    assert "REL-009" in codes
    assert "REL-016" in codes
    assert "REL-017" in codes


def test_nonpositive_enabled_equipment_dimension_fails():
    project, equipment = base_documents()
    equipment["equipment"][0]["width_mm"] = 0
    issues = validate_documents(project, equipment, allow_demo=True)
    assert any(issue.code == "EQP-003" for issue in issues)


def test_non_sheet_metal_prototype_does_not_require_bend_data():
    project, equipment = base_documents()
    project["project"] = {
        "id": "STAND",
        "mode": "production",
        "production_release": True,
        "release_kind": "prototype",
        "revision": "A",
        "units": "mm",
    }
    project["constraints"] = {
        "max_outer_width_mm": 1000,
        "max_outer_depth_mm": 800,
        "max_outer_height_mm": 1200,
        "max_total_mass_kg": 100,
        "constraints_verified": True,
    }
    project["workflow"] = {"workflow_verified": True}
    project["manufacturing"] = {
        "target_manufacturer": "Example Manufacturer",
        "dfm_record_id": "DFM-001",
        "uses_bent_sheet_metal": False,
        "bend_data_confirmed": False,
        "flat_pattern_owner": "TBD",
    }
    item = equipment["equipment"][0]
    item.update(
        {
            "verified": True,
            "envelopes_verified": True,
            "support_verified": True,
            "transport_verified": True,
            "source_type": "user_measurement",
            "source_reference": "MEAS-001",
            "model": "Exact Model 1",
            "manufacturer": "Exact Manufacturer",
            "transport_orientation": "upright",
        }
    )
    issues = validate_documents(project, equipment)
    assert not [issue for issue in issues if issue.severity == "ERROR"]


def test_bent_sheet_metal_prototype_requires_bend_owner_and_data():
    project, equipment = base_documents()
    project["project"] = {
        "id": "STAND",
        "mode": "production",
        "production_release": True,
        "release_kind": "prototype",
        "revision": "A",
        "units": "mm",
    }
    project["constraints"] = {
        "max_outer_width_mm": 1000,
        "max_outer_depth_mm": 800,
        "max_outer_height_mm": 1200,
        "max_total_mass_kg": 100,
        "constraints_verified": True,
    }
    project["workflow"] = {"workflow_verified": True}
    project["manufacturing"] = {
        "target_manufacturer": "Example Manufacturer",
        "dfm_record_id": "DFM-001",
        "uses_bent_sheet_metal": True,
        "bend_data_confirmed": False,
        "flat_pattern_owner": "TBD",
    }
    item = equipment["equipment"][0]
    item.update(
        {
            "verified": True,
            "envelopes_verified": True,
            "support_verified": True,
            "transport_verified": True,
            "source_type": "user_measurement",
            "source_reference": "MEAS-001",
            "model": "Exact Model 1",
            "manufacturer": "Exact Manufacturer",
            "transport_orientation": "upright",
        }
    )
    issues = validate_documents(project, equipment)
    codes = {issue.code for issue in issues}
    assert "REL-010" in codes
    assert "REL-011" in codes


def test_series_release_requires_prototype_inspection_record():
    project, equipment = base_documents()
    project["project"] = {
        "id": "STAND",
        "mode": "production",
        "production_release": True,
        "release_kind": "series",
        "revision": "B",
        "units": "mm",
    }
    issues = validate_documents(project, equipment)
    assert any(issue.code == "REL-015" for issue in issues)


def test_non_production_configuration_cannot_claim_release_kind():
    project, equipment = base_documents()
    project["project"]["release_kind"] = "prototype"
    issues = validate_documents(project, equipment, allow_demo=True)
    assert any(issue.code == "REL-023" for issue in issues)


def test_traceability_csv_is_rectangular_and_has_expected_columns():
    traceability_path = (
        Path(__file__).resolve().parents[1] / "state" / "REQUIREMENTS_TRACEABILITY.csv"
    )
    with traceability_path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        assert reader.fieldnames == [
            "requirement_id",
            "summary",
            "source",
            "status",
            "design_element",
            "verification",
            "evidence",
            "revision",
            "owner",
            "notes",
        ]
        rows = list(reader)

    assert rows
    assert all(None not in row for row in rows)
