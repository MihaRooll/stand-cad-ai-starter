"""Part metadata registry for geometry builders."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class PartRecord:
    """One build123d solid with traceability metadata."""

    part_id: str
    material: str
    solid: Any
    verify_on_real_machine: bool = False
