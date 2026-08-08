# A passing test is not evidence of physical correctness.
"""Shared session-scoped fixtures for geometry and kinematics tests."""

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
from stand_cad.geometry.datums import Datums
from stand_cad.parameters import load_parameters

REPO_ROOT = Path(__file__).resolve().parents[1]
PARAMETERS_PATH = REPO_ROOT / "config" / "parameters.yaml"


@pytest.fixture(scope="session")
def params():
    return load_parameters(PARAMETERS_PATH)


@pytest.fixture(scope="session")
def datums(params):
    return Datums.from_parameters(params)


@pytest.fixture(scope="session")
def transport(params):
    return build_transport_assembly(params)


@pytest.fixture(scope="session")
def service_p1(params):
    return build_service_plotter_1_assembly(params)


@pytest.fixture(scope="session")
def service_p2(params):
    return build_service_plotter_2_assembly(params)


@pytest.fixture(scope="session")
def tray1_quick_access(params):
    return build_tray1_quick_access_assembly(params)


@pytest.fixture(scope="session")
def operating_with_test_bodies(params):
    return build_operating_with_test_bodies_assembly(params)
