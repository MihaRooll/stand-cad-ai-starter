"""Parametric CAD infrastructure for the Light Plotter Tower project.

General-purpose loaders, validators, and schema gates shared across the build123d
generator stack; product-specific dimensions live in config/parameters.yaml.
"""

from .parameters import (
    Parameter,
    Parameters,
    load_parameters,
    validate_parameters,
    validate_release_readiness,
)
from .schema import ValidationIssue, validate_documents

__all__ = [
    "Parameter",
    "Parameters",
    "ValidationIssue",
    "load_parameters",
    "validate_documents",
    "validate_parameters",
    "validate_release_readiness",
]

