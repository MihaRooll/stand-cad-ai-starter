"""Numeric collision/clearance helpers (Ruling 5 mating-pair allowlist)."""

from __future__ import annotations

from itertools import combinations

from stand_cad.geometry.kinematics import LOWER_KINEMATIC_GROUP, UPPER_KINEMATIC_GROUP
from stand_cad.geometry.primitives import (
    bounding_box_bounds,
    intersection_volume,
    minimum_clearance,
)
from stand_cad.geometry.registry import PartRecord
from stand_cad.parameters import Parameters

COLLISION_THRESHOLD_PATH = "tolerance.part_assembly_feature_mm"
SERVICE_VOLUME_MATERIAL = "service_volume"

CONTAINED_PAIRS = frozenset(
    {
        ("EQUIP-PLOTTER1-001", "ENV-PLOTTER1-001"),
        ("EQUIP-PLOTTER2-001", "ENV-PLOTTER2-001"),
    }
)

# Excluded from the generic disjoint/mating pair loop only — checked separately.
COLLISION_EXCLUDE = frozenset(
    {
        "ENV-PLOTTER1-001",
        "ENV-PLOTTER2-001",
        "LID-ENVELOPE-P1-001",
        "LID-ENVELOPE-P2-001",
        "TESTBODY-PRIMARY-L1-001",
        "TESTBODY-PRIMARY-L2-001",
        "TESTBODY-LONG-L1-001",
        "TESTBODY-LONG-L2-001",
    }
)

FOOT_IDS = frozenset({"FOOT-001", "FOOT-002", "FOOT-003", "FOOT-004"})

REAR_BOTTOM_SERVICE_CLUSTER = frozenset(
    {"COVER-SVC-001", "MAINS-INLET-001", "AIRPATH-001", "ADAPTER-P1-001"}
)

SERVICE_MOUNT_PREFIXES = ("PANEL-", "FRAME-", "COVER-SVC-001")

RAW_MATING_PAIRS = [
    ("TRAY-LOWER-001", "SLIDE-LOWER-LEFT-001"),
    ("TRAY-LOWER-001", "SLIDE-LOWER-RIGHT-001"),
    ("TRAY-LOWER-001", "SLIDE-LOWER-CENTER-001"),
    ("TRAY-UPPER-001", "SLIDE-UPPER-LEFT-001"),
    ("TRAY-UPPER-001", "SLIDE-UPPER-RIGHT-001"),
    ("TRAY-UPPER-001", "SLIDE-UPPER-CENTER-001"),
    ("EQUIP-PLOTTER1-001", "TRAY-LOWER-001"),
    ("EQUIP-PLOTTER2-001", "TRAY-UPPER-001"),
    ("EQUIP-PLOTTER1-001", "SLIDE-LOWER-LEFT-001"),
    ("EQUIP-PLOTTER1-001", "SLIDE-LOWER-RIGHT-001"),
    ("EQUIP-PLOTTER1-001", "SLIDE-LOWER-CENTER-001"),
    ("EQUIP-PLOTTER2-001", "SLIDE-UPPER-LEFT-001"),
    ("EQUIP-PLOTTER2-001", "SLIDE-UPPER-RIGHT-001"),
    ("EQUIP-PLOTTER2-001", "SLIDE-UPPER-CENTER-001"),
    ("EQUIP-PLOTTER1-001", "INTERLOCK-SHUTTLE-001"),
    ("EQUIP-PLOTTER2-001", "INTERLOCK-SHUTTLE-001"),
    ("VIBMOUNT-P1-001", "TRAY-LOWER-001"),
    ("VIBMOUNT-P1-001", "EQUIP-PLOTTER1-001"),
    ("VIBMOUNT-P1-002", "TRAY-LOWER-001"),
    ("VIBMOUNT-P1-002", "EQUIP-PLOTTER1-001"),
    ("VIBMOUNT-P1-003", "TRAY-LOWER-001"),
    ("VIBMOUNT-P1-003", "EQUIP-PLOTTER1-001"),
    ("VIBMOUNT-P1-004", "TRAY-LOWER-001"),
    ("VIBMOUNT-P1-004", "EQUIP-PLOTTER1-001"),
    ("VIBMOUNT-P2-001", "TRAY-UPPER-001"),
    ("VIBMOUNT-P2-001", "EQUIP-PLOTTER2-001"),
    ("VIBMOUNT-P2-002", "TRAY-UPPER-001"),
    ("VIBMOUNT-P2-002", "EQUIP-PLOTTER2-001"),
    ("VIBMOUNT-P2-003", "TRAY-UPPER-001"),
    ("VIBMOUNT-P2-003", "EQUIP-PLOTTER2-001"),
    ("VIBMOUNT-P2-004", "TRAY-UPPER-001"),
    ("VIBMOUNT-P2-004", "EQUIP-PLOTTER2-001"),
    ("INTERLOCK-TAB-LOWER-001", "INTERLOCK-SHUTTLE-001"),
    ("INTERLOCK-TAB-UPPER-001", "INTERLOCK-SHUTTLE-001"),
    ("FRAME-RAIL-TRAY-LOWER-L-001", "SLIDE-LOWER-LEFT-001"),
    ("FRAME-RAIL-TRAY-LOWER-R-001", "SLIDE-LOWER-RIGHT-001"),
    ("FRAME-RAIL-TRAY-LOWER-C-001", "SLIDE-LOWER-CENTER-001"),
    ("FRAME-RAIL-TRAY-UPPER-L-001", "SLIDE-UPPER-LEFT-001"),
    ("FRAME-RAIL-TRAY-UPPER-R-001", "SLIDE-UPPER-RIGHT-001"),
    ("FRAME-RAIL-TRAY-UPPER-C-001", "SLIDE-UPPER-CENTER-001"),
    ("SOFTSTOP-LOWER-001", "TRAY-LOWER-001"),
    ("SOFTSTOP-UPPER-001", "TRAY-UPPER-001"),
    ("SHELF-000", "ORG-FLOOR-001"),
    ("SHELF-000", "ORG-INSERT-001"),
    ("SHELF-001", "ORG-FLOOR-001"),
    ("SHELF-001", "ORG-INSERT-001"),
    ("SHELF-002", "ORG-FLOOR-001"),
    ("SHELF-002", "ORG-INSERT-001"),
    ("MEDIA-SUPPORT-L1-001", "PANEL-IN-REAR-001"),
    ("MEDIA-SUPPORT-L2-001", "PANEL-IN-REAR-001"),
    ("EQUIP-PLOTTER1-001", "MEDIA-SUPPORT-L1-001"),
    ("EQUIP-PLOTTER2-001", "MEDIA-SUPPORT-L2-001"),
    ("MAINS-INLET-001", "PANEL-IN-REAR-001"),
    ("MAINS-INLET-001", "PANEL-OUT-REAR-001"),
    ("MAINS-INLET-001", "PANEL-IN-BOTTOM-001"),
    ("SVC-CABLE-PASSTHROUGH-001", "PANEL-OUT-RIGHT-001"),
    ("COVER-SVC-001", "PANEL-IN-BOTTOM-001"),
    ("COVER-SVC-001", "PANEL-OUT-REAR-001"),
    ("CABLE-CH-001", "PANEL-OUT-LEFT-001"),
    ("CABLE-CH-001", "PANEL-IN-BOTTOM-001"),
    ("LIGHT-STRIP-001", "PANEL-OUT-REAR-001"),
    ("LIGHT-STRIP-001", "FRAME-RAIL-TOP-REAR-001"),
]

DOOR_IDS = frozenset({"DOOR-LOWER-001", "DOOR-UPPER-001"})

# Closed drop-front doors share the tray front plane — zero clearance is expected.
DOOR_CLOSED_FRONT_MATE_PREFIXES = (
    "TRAY-",
    "SLIDE-",
    "EQUIP-PLOTTER",
    "PANEL-CLAD-FRONT-TRAY-",
    "FRAME-RAIL-BASE-FRONT-",
    "FRAME-RAIL-ORG-FRONT-",
    "FRAME-RAIL-TRAY-",
)

# Closed drop-front door front-plane bearing ceiling (mm³) — plane-touch / skin
# bearing only; rejects volumetric burial when extended tray intrudes (closed posture).
DOOR_FRONT_PLANE_MAX_BEARING_MM3 = 500.0

# Cosmetic strut ↔ post/panel/rail attachment at corner (7 mm Ø cylinder clip).
DOOR_STRUT_MAX_BEARING_MM3 = 350.0

# Open-front structural/cladding ↔ tray-stack skin bearing ceiling (mm³) — plane-touch /
# skin contact only; rejects volumetric burial through is_open_front_kinematic_contact
# and the four front clad/rail penetrating patterns. Live max 540 mm³ (2026-08-08).
OPEN_FRONT_MAX_BEARING_MM3 = 750.0

# Slide rail ↔ adjacent vibration-mount pad skin bearing (mm³) — plane-touch only.
# Live max 0 mm³ across eight SLIDE-* ↔ VIBMOUNT-* pairs (2026-08-08 transport).
SLIDE_VIBMOUNT_MAX_BEARING_MM3 = 500.0

# Equipment plotter ↔ tray/slide seating skin bearing (mm³) — plane-touch only.
# Live max 0 mm³ across eight EQUIP-PLOTTER* ↔ TRAY-* / SLIDE-* seating pairs
# (2026-08-08 transport). Other MATING_PAIRS (SOFT↔TRAY, …) stay uncapped —
# see D-087 residual P2; VIB↔EQUIP gated separately (D-091); TRAY↔SLIDE (D-089).
EQUIP_SEATING_MAX_BEARING_MM3 = 500.0

# Vibration-mount pad ↔ equipment plotter skin bearing (mm³) — full pad embed only.
# Live max 2000 mm³ (20×20×5 pad) across eight VIBMOUNT-P* ↔ EQUIP-PLOTTER* pairs
# (2026-08-08 transport). Hygiene ceiling; D-091 — not a live beyond-pad burial fix.
VIB_EQUIP_MAX_BEARING_MM3 = 2500.0

# Tray platform ↔ slide rail skin bearing (mm³) — plane-touch only after Path A
# Z-stack (slide fully below tray). Live max 0 mm³ across six TRAY-* ↔ SLIDE-*
# pairs (2026-08-08 transport); pre-fix burial ~96525 mm³ rejected.
TRAY_SLIDE_MAX_BEARING_MM3 = 500.0

# Cross-tier staggered Y-overlap skin bearing (mm³) — tiers share front-face Y (D-033)
# and stack in Z; Y overlap alone is intentional, not collision. Live max 0 mm³ across
# 149 transport / 38 service_p1 / 149 service_p2 cross-tier marker pairs with y_overlap
# > threshold (2026-08-08); pre-fix burial EQUIP-PLOTTER1 ↔ FRAME-RAIL-TRAY-UPPER ~43875
# mm³ rejected (D-097).
STAGGERED_TIER_MAX_BEARING_MM3 = 500.0

# Service cover ↔ panel skin bearing (mm³) — flush mount on bottom/rear panels.
# Live max 7901.25 mm³ (COVER-SVC-001 ↔ PANEL-IN-BOTTOM-001 / PANEL-IN-REAR-001)
# and 1048.99 mm³ (↔ PANEL-OUT-REAR-001, 2026-08-08 transport). IN-REAR mates
# via share_face only (not on MATING_PAIRS) — gate that path too (D-095).
COVER_SVC_PANEL_MAX_BEARING_MM3 = 10_000.0

# Service cover ↔ base rear rail skin bearing (mm³) — share_face mount on rear base rail.
# Live max 7350.0 mm³ (COVER-SVC-001 ↔ FRAME-RAIL-BASE-REAR-001, 2026-08-08 transport).
COVER_SVC_FRAME_BASE_MAX_BEARING_MM3 = 10_000.0

# Service cover ↔ rear corner post penetrating / share_face overlap (mm³).
# Live max 122.9474 mm³ (COVER-SVC-001 ↔ FRAME-POST-RL/RR-001, 2026-08-08 transport).
COVER_SVC_FRAME_POST_MAX_BEARING_MM3 = 500.0

COVER_SVC_FRAME_POST_PENETRATING_PATTERNS: frozenset[tuple[str, str]] = frozenset(
    {
        ("COVER-SVC-001", "FRAME-POST-RL-"),
        ("COVER-SVC-001", "FRAME-POST-RR-"),
    }
)

OPEN_FRONT_PENETRATING_PATTERNS: frozenset[tuple[str, str]] = frozenset(
    {
        ("PANEL-CLAD-FRONT-", "TRAY-LOWER-"),
        ("PANEL-CLAD-FRONT-", "SLIDE-LOWER-"),
        ("FRAME-RAIL-BASE-FRONT-", "TRAY-LOWER-"),
        ("FRAME-RAIL-BASE-FRONT-", "SLIDE-LOWER-"),
    }
)

# Organizer rear rail ↔ rear inner panel penetrating joint (mm³) — bolt-through overlap.
# Live max 31500 mm³ (FRAME-RAIL-ORG-REAR-001 ↔ PANEL-IN-REAR-001, 2026-08-08 transport).
ORG_REAR_PENETRATING_MAX_BEARING_MM3 = 35_000.0

# Mid partition ↔ upper tier slide/tray/softstop penetrating joints (mm³).
# Live max 30712.5 mm³ (SLIDE-UPPER-* ↔ PANEL-IN-MID-001, 2026-08-08 transport).
MID_UPPER_PENETRATING_MAX_BEARING_MM3 = 35_000.0

ORG_REAR_PENETRATING_PATTERNS: frozenset[tuple[str, str]] = frozenset(
    {
        ("FRAME-RAIL-ORG-", "PANEL-IN-REAR-"),
    }
)

MID_UPPER_PENETRATING_PATTERNS: frozenset[tuple[str, str]] = frozenset(
    {
        ("SLIDE-UPPER-", "PANEL-IN-MID-001"),
        ("TRAY-UPPER-001", "PANEL-IN-MID-001"),
        ("SOFTSTOP-UPPER-001", "PANEL-IN-MID-001"),
    }
)

# Frame post ↔ inner panel penetrating joint (mm³) — bolt-through / pocket overlap.
# Live max 18652.9 mm³ (FRAME-POST-RR/RL-001 ↔ PANEL-IN-REAR-001, 2026-08-08 transport).
POST_PANEL_PENETRATING_MAX_BEARING_MM3 = 25_000.0

POST_PANEL_PENETRATING_PATTERNS: frozenset[tuple[str, str]] = frozenset(
    {
        ("FRAME-POST-", "PANEL-IN-"),
    }
)

# Tray ring rail ↔ inner panel penetrating joint (mm³) — bolt-through / pocket overlap.
# Live max 10237.5 mm³ (FRAME-RAIL-TRAY-LOWER-L/R-001 ↔ PANEL-IN-BOTTOM-001, 2026-08-08 transport).
TRAY_RAIL_PANEL_PENETRATING_MAX_BEARING_MM3 = 15_000.0

TRAY_RAIL_PANEL_PENETRATING_PATTERNS: frozenset[tuple[str, str]] = frozenset(
    {
        ("FRAME-RAIL-TRAY-", "PANEL-IN-"),
    }
)


def _door_is_open_horizontal(solid, *, threshold: float = 1.0) -> bool:
    """True when a drop-front door has swung to horizontal work-surface posture."""
    (_, _), (y0, y1), (z0, z1) = bounding_box_bounds(solid)
    y_span = y1 - y0
    z_span = z1 - z0
    if z_span < threshold:
        return y_span > threshold
    return y_span > z_span * 5.0


def pair_key(a: str, b: str) -> tuple[str, str]:
    return (a, b) if a <= b else (b, a)


MATING_PAIRS = frozenset(pair_key(a, b) for a, b in RAW_MATING_PAIRS)


def aabb_share_face(
    solid_a,
    solid_b,
    threshold: float,
) -> bool:
    """True when two axis-aligned boxes touch on a shared face within threshold."""
    bounds_a = bounding_box_bounds(solid_a)
    bounds_b = bounding_box_bounds(solid_b)
    for axis in range(3):
        for face_a in bounds_a[axis]:
            for face_b in bounds_b[axis]:
                if abs(face_a - face_b) > threshold:
                    continue
                other_axes = [index for index in range(3) if index != axis]
                overlap_ok = all(
                    min(bounds_a[other][1], bounds_b[other][1])
                    - max(bounds_a[other][0], bounds_b[other][0])
                    > -threshold
                    for other in other_axes
                )
                if overlap_ok:
                    return True
    return False


def is_foot_structure_contact(
    a: str,
    b: str,
    parts: dict[str, PartRecord],
    threshold: float,
) -> bool:
    """Foot rests on Z=0; mates only with structure supported on the foot top face."""
    if a not in FOOT_IDS and b not in FOOT_IDS:
        return False
    foot_id = a if a in FOOT_IDS else b
    other_id = b if foot_id == a else a
    foot_bounds = bounding_box_bounds(parts[foot_id].solid)
    other_bounds = bounding_box_bounds(parts[other_id].solid)
    if abs(foot_bounds[2][0]) > threshold:
        return False
    x_overlap = min(foot_bounds[0][1], other_bounds[0][1]) - max(
        foot_bounds[0][0], other_bounds[0][0]
    )
    y_overlap = min(foot_bounds[1][1], other_bounds[1][1]) - max(
        foot_bounds[1][0], other_bounds[1][0]
    )
    if x_overlap <= threshold or y_overlap <= threshold:
        return False
    foot_top = foot_bounds[2][1]
    if abs(other_bounds[2][0] - foot_top) <= threshold:
        return True
    if other_bounds[2][0] <= threshold:
        # Structure starting at the floor that extends through the foot height band
        # while overlapping XY is interpenetration, not a foot-top mate.
        if other_bounds[2][1] > foot_top + threshold:
            if x_overlap > threshold and y_overlap > threshold:
                return False
        if (
            other_bounds[2][1] <= foot_top + threshold
            and aabb_share_face(parts[foot_id].solid, parts[other_id].solid, threshold)
        ):
            return True
    return False


def _prefix_pair(a: str, b: str, prefix_a: str, prefix_b: str) -> bool:
    return (a.startswith(prefix_a) and b.startswith(prefix_b)) or (
        a.startswith(prefix_b) and b.startswith(prefix_a)
    )


def _share_face_if_prefix(
    a: str,
    b: str,
    parts: dict[str, PartRecord],
    threshold: float,
    prefix_a: str,
    prefix_b: str,
) -> bool:
    if not _prefix_pair(a, b, prefix_a, prefix_b):
        return False
    return aabb_share_face(parts[a].solid, parts[b].solid, threshold)


def is_service_volume_mount(
    a: str,
    b: str,
    parts: dict[str, PartRecord],
    threshold: float,
) -> bool:
    """Service volumes mate only with enclosing panels/frames they physically touch."""
    materials = (parts[a].material, parts[b].material)
    if SERVICE_VOLUME_MATERIAL not in materials:
        return False
    svc_id = a if parts[a].material == SERVICE_VOLUME_MATERIAL else b
    other_id = b if svc_id == a else a
    if other_id in REAR_BOTTOM_SERVICE_CLUSTER:
        return (
            minimum_clearance(parts[svc_id].solid, parts[other_id].solid) < threshold
        )
    if not other_id.startswith(SERVICE_MOUNT_PREFIXES):
        return False
    return minimum_clearance(parts[svc_id].solid, parts[other_id].solid) < threshold


def _id_matches(part_id: str, pattern: str) -> bool:
    """Match exact part ID or prefix pattern ending with '-'."""
    if pattern.endswith("-"):
        return part_id.startswith(pattern)
    return part_id == pattern


def _matches_penetrating_patterns(
    a: str,
    b: str,
    patterns: frozenset[tuple[str, str]],
) -> bool:
    """True when part IDs match any (pattern_a, pattern_b) in either order."""
    for pattern_a, pattern_b in patterns:
        if (_id_matches(a, pattern_a) and _id_matches(b, pattern_b)) or (
            _id_matches(a, pattern_b) and _id_matches(b, pattern_a)
        ):
            return True
    return False


SIDE_SLAB_IDS = frozenset({"PANEL-OUT-LEFT-001", "PANEL-OUT-RIGHT-001"})

SIDE_SLAB_FRAME_PREFIXES = (
    "FRAME-POST-",
    "FRAME-RAIL-BASE-LEFT-",
    "FRAME-RAIL-BASE-RIGHT-",
)

# Pre-cavity solid-slab burial at a corner post was ~428×10³ mm³ synthetic (rejected —
# far above ``_max_legitimate_skin_bearing_volume_mm3`` ≈56×10³). Legitimate cavity-wall
# bearing on X skin + front/rear Y return reaches ~47–48×10³ mm³ at zero clearance.
SIDE_SLAB_FRAME_MAX_INTERSECTION_MM3 = 35_000.0  # legacy rail-only reference


def _max_legitimate_skin_bearing_volume_mm3(
    params: Parameters,
    panel_bounds: tuple[tuple[float, float], ...],
    frame_id: str,
) -> float:
    """Volume ceiling when Al frame bears on the 3 mm cavity-wall skin (not solid acrylic burial).

    TZ lines 218–219: hidden aluminium frame inside the wall pocket; the opal skin is
    non-load-bearing cosmetic PMMA. Corner posts mate flush to the inner face of the outer
    X skin and the front/rear Y returns — zero clearance is an expected bearing joint.
    """
    wall_mm = float(params.value("materials.outer_panel_thickness_mm"))
    side_clear = float(params.side_slab_thickness_mm)
    profile = float(params.value("materials.frame_profile_size_mm"))
    contact_height = panel_bounds[2][1] - panel_bounds[2][0]
    if frame_id.startswith("FRAME-POST-"):
        return (profile + side_clear) * wall_mm * contact_height
    return profile * wall_mm * contact_height * 2.0


def _is_side_slab_frame_pair(a: str, b: str) -> tuple[str, str] | None:
    """Return (panel_id, frame_id) when a is a side slab mated to a wall-pocket frame member."""
    if a in SIDE_SLAB_IDS and any(b.startswith(prefix) for prefix in SIDE_SLAB_FRAME_PREFIXES):
        return a, b
    if b in SIDE_SLAB_IDS and any(a.startswith(prefix) for prefix in SIDE_SLAB_FRAME_PREFIXES):
        return b, a
    return None


def is_side_slab_frame_cavity_joint(
    a: str,
    b: str,
    parts: dict[str, PartRecord],
    params: Parameters,
    threshold: float,
) -> bool:
    """Frame members legitimately occupy the side-slab air pocket behind the 3 mm opal skin.

    Allows zero-clearance **bearing contact** where aluminium posts/rails meet the inner face
    of the opal skin (designed joint per TZ hidden-frame-in-wall intent). Rejects volumetric
    burial in solid acrylic (~428×10³ mm³ synthetic at corner — far above max_bearing).
    """
    pair = _is_side_slab_frame_pair(a, b)
    if pair is None:
        return False
    panel_id, frame_id = pair
    side_clear = float(params.side_slab_thickness_mm)
    case_width = float(params.value("case.width"))
    case_depth = float(params.value("case.depth"))
    frame_bounds = bounding_box_bounds(parts[frame_id].solid)
    panel_bounds = bounding_box_bounds(parts[panel_id].solid)

    # Corner posts span the wall pocket plus an inward leg (~40 mm); require X overlap
    # with the pocket band [0, side_clear] / [width - side_clear, width], not full confinement.
    if panel_id == "PANEL-OUT-LEFT-001":
        if not (
            frame_bounds[0][0] < side_clear + threshold
            and frame_bounds[0][1] > -threshold
        ):
            return False
    else:
        if not (
            frame_bounds[0][1] > case_width - side_clear - threshold
            and frame_bounds[0][0] < case_width + threshold
        ):
            return False

    # Corner posts mate at front/rear Y returns only — reject mid-wall skin burial that
    # passes X overlap and volume ceiling but sits away from the return bands.
    if frame_id.startswith("FRAME-POST-"):
        front_y_overlap = (
            frame_bounds[1][0] < side_clear + threshold
            and frame_bounds[1][1] > -threshold
        )
        rear_y_overlap = (
            frame_bounds[1][1] > case_depth - side_clear - threshold
            and frame_bounds[1][0] < case_depth + threshold
        )
        if not (front_y_overlap or rear_y_overlap):
            return False

    if not (
        frame_bounds[2][1] > panel_bounds[2][0] - threshold
        and frame_bounds[2][0] < panel_bounds[2][1] + threshold
    ):
        return False

    inter_vol = intersection_volume(parts[panel_id].solid, parts[frame_id].solid)
    max_bearing = _max_legitimate_skin_bearing_volume_mm3(params, panel_bounds, frame_id)
    if inter_vol > max_bearing + threshold:
        return False

    clearance = minimum_clearance(parts[panel_id].solid, parts[frame_id].solid)
    return clearance < threshold or inter_vol > threshold


PENETRATING_JOINT_PATTERNS: tuple[tuple[str, str], ...] = (
    # Corner posts pierce inner panel stack at shared corners.
    ("FRAME-POST-", "PANEL-IN-"),
    # Rear service cover overlaps rear corner posts.
    ("COVER-SVC-001", "FRAME-POST-RL-"),
    ("COVER-SVC-001", "FRAME-POST-RR-"),
    # Mains inlet pocket shares rear base rail structure.
    ("FRAME-RAIL-BASE-REAR-", "MAINS-INLET-"),
    # Organizer support rails bolt to rear inner panel.
    ("FRAME-RAIL-ORG-", "PANEL-IN-REAR-"),
    # Tray carrier rails attach to inner partition panels.
    ("FRAME-RAIL-TRAY-", "PANEL-IN-"),
    # Interlock tabs pass through inner panel cutouts.
    ("INTERLOCK-TAB-", "PANEL-IN-"),
    ("SLIDE-UPPER-", "PANEL-IN-MID-001"),
    ("TRAY-UPPER-001", "PANEL-IN-MID-001"),
    ("SOFTSTOP-UPPER-001", "PANEL-IN-MID-001"),
    ("PANEL-CLAD-FRONT-", "TRAY-LOWER-"),
    ("PANEL-CLAD-FRONT-", "SLIDE-LOWER-"),
    ("FRAME-RAIL-BASE-FRONT-", "TRAY-LOWER-"),
    ("FRAME-RAIL-BASE-FRONT-", "SLIDE-LOWER-"),
)


STACK_CAP_TOP_RAIL_MATES: dict[str, frozenset[str]] = {
    "STACK-CAP-FL-001": frozenset({"FRAME-RAIL-TOP-LEFT-001"}),
    "STACK-CAP-FR-001": frozenset({"FRAME-RAIL-TOP-RIGHT-001"}),
    "STACK-CAP-RL-001": frozenset({"FRAME-RAIL-TOP-REAR-001", "FRAME-RAIL-TOP-LEFT-001"}),
    "STACK-CAP-RR-001": frozenset({"FRAME-RAIL-TOP-REAR-001", "FRAME-RAIL-TOP-RIGHT-001"}),
}

STACK_CAP_REAR_PANEL_MATES: dict[str, frozenset[str]] = {
    "STACK-CAP-RL-001": frozenset({"PANEL-IN-REAR-001", "PANEL-OUT-REAR-001"}),
    "STACK-CAP-RR-001": frozenset({"PANEL-IN-REAR-001", "PANEL-OUT-REAR-001"}),
}

STACK_CAP_SIDE_PANEL_MATES: dict[str, frozenset[str]] = {
    "STACK-CAP-FL-001": frozenset({"PANEL-OUT-LEFT-001"}),
    "STACK-CAP-FR-001": frozenset({"PANEL-OUT-RIGHT-001"}),
    "STACK-CAP-RL-001": frozenset({"PANEL-OUT-LEFT-001"}),
    "STACK-CAP-RR-001": frozenset({"PANEL-OUT-RIGHT-001"}),
}

# Corner cap↔rail/panel bearing overlap ceiling (mm³) — rejects mid-span burial.
STACK_CAP_MAX_BEARING_MM3 = 8_000.0
# Cap plate + notch boss into matching post (includes boss below case.height).
STACK_CAP_POST_MAX_INTERSECTION_MM3 = 20_000.0


def _stack_cap_z_adjacent(
    cap_bounds: tuple[tuple[float, float], tuple[float, float], tuple[float, float]],
    other_bounds: tuple[tuple[float, float], tuple[float, float], tuple[float, float]],
    threshold: float,
) -> bool:
    """Cap bottom mates other top, or Z bands overlap for corner bearing."""
    cap_z0, cap_z1 = cap_bounds[2]
    other_z0, other_z1 = other_bounds[2]
    if abs(cap_z0 - other_z1) <= threshold:
        return True
    if abs(other_z0 - cap_z1) <= threshold:
        return True
    z_overlap = min(cap_z1, other_z1) - max(cap_z0, other_z0)
    return z_overlap > threshold


def _stack_cap_corner_xy_overlap(
    cap_bounds: tuple[tuple[float, float], tuple[float, float], tuple[float, float]],
    other_bounds: tuple[tuple[float, float], tuple[float, float], tuple[float, float]],
    threshold: float,
) -> bool:
    x_overlap = min(cap_bounds[0][1], other_bounds[0][1]) - max(
        cap_bounds[0][0], other_bounds[0][0]
    )
    y_overlap = min(cap_bounds[1][1], other_bounds[1][1]) - max(
        cap_bounds[1][0], other_bounds[1][0]
    )
    return x_overlap > threshold and y_overlap > threshold


def is_stack_cap_mate(
    a: str,
    b: str,
    parts: dict[str, PartRecord],
    threshold: float,
) -> bool:
    """STACK-001 / D-064 — stacking caps bear on post tops and overlap top ring at corners."""
    cap_id = a if a.startswith("STACK-CAP-") else b if b.startswith("STACK-CAP-") else None
    if cap_id is None:
        return False
    other_id = b if cap_id == a else a
    cap_solid = parts[cap_id].solid
    other_solid = parts[other_id].solid
    if minimum_clearance(cap_solid, other_solid) >= threshold:
        return False
    cap_bounds = bounding_box_bounds(cap_solid)
    other_bounds = bounding_box_bounds(other_solid)
    inter_vol = intersection_volume(cap_solid, other_solid)
    if other_id.startswith("FRAME-POST-"):
        suffix = cap_id.removeprefix("STACK-CAP-").removesuffix("-001")
        if other_id == f"FRAME-POST-{suffix}-001":
            return inter_vol <= STACK_CAP_POST_MAX_INTERSECTION_MM3 + threshold
    if other_id.startswith("FRAME-RAIL-TOP-"):
        allowed = STACK_CAP_TOP_RAIL_MATES.get(cap_id, frozenset())
        if other_id not in allowed:
            return False
        if not _stack_cap_corner_xy_overlap(cap_bounds, other_bounds, threshold):
            return False
        if not _stack_cap_z_adjacent(cap_bounds, other_bounds, threshold):
            return False
        return inter_vol <= STACK_CAP_MAX_BEARING_MM3 + threshold
    if other_id in ("PANEL-IN-REAR-001", "PANEL-OUT-REAR-001"):
        allowed = STACK_CAP_REAR_PANEL_MATES.get(cap_id, frozenset())
        if other_id not in allowed:
            return False
        if not _stack_cap_corner_xy_overlap(cap_bounds, other_bounds, threshold):
            return False
        if not _stack_cap_z_adjacent(cap_bounds, other_bounds, threshold):
            return False
        return inter_vol <= STACK_CAP_MAX_BEARING_MM3 + threshold
    if other_id.startswith("PANEL-OUT-"):
        allowed = STACK_CAP_SIDE_PANEL_MATES.get(cap_id, frozenset())
        if other_id not in allowed:
            return False
        if not _stack_cap_corner_xy_overlap(cap_bounds, other_bounds, threshold):
            return False
        if not _stack_cap_z_adjacent(cap_bounds, other_bounds, threshold):
            return False
        return inter_vol <= STACK_CAP_MAX_BEARING_MM3 + threshold
    return False


def is_penetrating_structural_joint(
    a: str,
    b: str,
    parts: dict[str, PartRecord],
    threshold: float,
) -> bool:
    """Zero-clearance overlap without a full shared face — requires proven intersection."""
    for pattern_a, pattern_b in PENETRATING_JOINT_PATTERNS:
        matched = (_id_matches(a, pattern_a) and _id_matches(b, pattern_b)) or (
            _id_matches(a, pattern_b) and _id_matches(b, pattern_a)
        )
        if not matched:
            continue
        solid_a = parts[a].solid
        solid_b = parts[b].solid
        if minimum_clearance(solid_a, solid_b) >= threshold:
            continue
        inter_vol = intersection_volume(solid_a, solid_b)
        if (pattern_a, pattern_b) in OPEN_FRONT_PENETRATING_PATTERNS:
            if inter_vol > OPEN_FRONT_MAX_BEARING_MM3 + threshold:
                continue
        elif (pattern_a, pattern_b) in ORG_REAR_PENETRATING_PATTERNS:
            if inter_vol > ORG_REAR_PENETRATING_MAX_BEARING_MM3 + threshold:
                continue
        elif (pattern_a, pattern_b) in MID_UPPER_PENETRATING_PATTERNS:
            if inter_vol > MID_UPPER_PENETRATING_MAX_BEARING_MM3 + threshold:
                continue
        elif (pattern_a, pattern_b) in POST_PANEL_PENETRATING_PATTERNS:
            if inter_vol > POST_PANEL_PENETRATING_MAX_BEARING_MM3 + threshold:
                continue
        elif (pattern_a, pattern_b) in TRAY_RAIL_PANEL_PENETRATING_PATTERNS:
            if inter_vol > TRAY_RAIL_PANEL_PENETRATING_MAX_BEARING_MM3 + threshold:
                continue
        elif (pattern_a, pattern_b) in COVER_SVC_FRAME_POST_PENETRATING_PATTERNS:
            if inter_vol > COVER_SVC_FRAME_POST_MAX_BEARING_MM3 + threshold:
                continue
        if inter_vol > threshold:
            return True
    return False


def is_door_mate(
    a: str,
    b: str,
    parts: dict[str, PartRecord],
    threshold: float,
) -> bool:
    """Drop-front doors (D-073) — closed-plane and open-strut contacts at the front opening."""
    door_a = a in DOOR_IDS
    door_b = b in DOOR_IDS
    strut_a = a.startswith("DOOR-STRUT-")
    strut_b = b.startswith("DOOR-STRUT-")
    if not (door_a or door_b or strut_a or strut_b):
        return False

    solid_a = parts[a].solid
    solid_b = parts[b].solid
    clearance = minimum_clearance(solid_a, solid_b)
    if clearance >= threshold:
        return False

    if door_a and door_b:
        return True

    door_id = a if door_a else b if door_b else None
    strut_id = a if strut_a else b if strut_b else None
    other_id = b if a in (door_id, strut_id) else a

    if strut_id is not None:
        if other_id in DOOR_IDS or other_id.startswith("DOOR-STRUT-"):
            return True
        if other_id.startswith(("FRAME-RAIL-", "PANEL-OUT-", "PANEL-IN-", "FRAME-POST-")):
            inter_vol = intersection_volume(solid_a, solid_b)
            return inter_vol <= DOOR_STRUT_MAX_BEARING_MM3 + threshold
        return False

    if door_id is not None:
        door_solid = parts[door_id].solid
        is_open = _door_is_open_horizontal(door_solid, threshold=threshold)

        if other_id.startswith("DOOR-STRUT-"):
            return True
        if other_id.startswith("FRAME-POST-"):
            inter_vol = intersection_volume(solid_a, solid_b)
            ceiling = threshold if is_open else DOOR_FRONT_PLANE_MAX_BEARING_MM3 + threshold
            return inter_vol <= ceiling
        if other_id == "PANEL-IN-MID-001":
            inter_vol = intersection_volume(solid_a, solid_b)
            if is_open:
                return inter_vol <= threshold
            return inter_vol <= DOOR_FRONT_PLANE_MAX_BEARING_MM3 + threshold
        if other_id.startswith(DOOR_CLOSED_FRONT_MATE_PREFIXES):
            inter_vol = intersection_volume(solid_a, solid_b)
            if is_open:
                return inter_vol <= threshold
            return inter_vol <= DOOR_FRONT_PLANE_MAX_BEARING_MM3 + threshold
        if other_id.startswith(("SOFTSTOP-LOWER-", "SOFTSTOP-UPPER-")):
            inter_vol = intersection_volume(solid_a, solid_b)
            if is_open:
                return inter_vol <= threshold
            return inter_vol <= DOOR_FRONT_PLANE_MAX_BEARING_MM3 + threshold
        if other_id.startswith("PANEL-CLAD-FRONT-") and other_id.endswith("-001"):
            inter_vol = intersection_volume(solid_a, solid_b)
            if is_open:
                return inter_vol <= threshold
            return inter_vol <= DOOR_FRONT_PLANE_MAX_BEARING_MM3 + threshold

    return False


def is_frame_post_bearing(
    a: str,
    b: str,
    parts: dict[str, PartRecord],
    threshold: float,
) -> bool:
    """D-075 — corner posts bear on cleats and front-corner tray hardware (plane touch)."""
    post_id = (
        a
        if a.startswith("FRAME-POST-")
        else b
        if b.startswith("FRAME-POST-")
        else None
    )
    if post_id is None:
        return False
    other_id = b if post_id == a else a
    if other_id.startswith(("DOOR-", "DOOR-STRUT-")):
        return False
    solid_a = parts[a].solid
    solid_b = parts[b].solid
    if minimum_clearance(solid_a, solid_b) >= threshold:
        return False
    inter_vol = intersection_volume(solid_a, solid_b)
    if other_id.startswith("SHELF-SUPPORT-"):
        return inter_vol <= 200.0 + threshold
    if other_id.startswith(("SLIDE-LOWER-", "TRAY-LOWER-", "EQUIP-PLOTTER1-")):
        return inter_vol <= threshold
    if other_id.startswith(("SLIDE-UPPER-", "TRAY-UPPER-", "EQUIP-PLOTTER2-")):
        return inter_vol <= threshold
    return False


def is_slide_vibmount_bearing(
    a: str,
    b: str,
    parts: dict[str, PartRecord],
    threshold: float,
) -> bool:
    """Slide rail plane bears on adjacent vibration-mount pads — skin contact only."""
    tier_pairs = (
        ("SLIDE-LOWER-", "VIBMOUNT-P1-"),
        ("SLIDE-UPPER-", "VIBMOUNT-P2-"),
    )
    for slide_prefix, vib_prefix in tier_pairs:
        if (_id_matches(a, slide_prefix) and _id_matches(b, vib_prefix)) or (
            _id_matches(b, slide_prefix) and _id_matches(a, vib_prefix)
        ):
            if minimum_clearance(parts[a].solid, parts[b].solid) >= threshold:
                return False
            inter_vol = intersection_volume(parts[a].solid, parts[b].solid)
            return inter_vol <= SLIDE_VIBMOUNT_MAX_BEARING_MM3 + threshold
    return False


def is_equip_seating_pair(a: str, b: str) -> bool:
    """True when a,b is an equipment plotter ↔ tray/slide seating pair."""
    tier_pairs = (
        ("EQUIP-PLOTTER1-", "TRAY-LOWER-"),
        ("EQUIP-PLOTTER1-", "SLIDE-LOWER-"),
        ("EQUIP-PLOTTER2-", "TRAY-UPPER-"),
        ("EQUIP-PLOTTER2-", "SLIDE-UPPER-"),
    )
    for equip_prefix, target_prefix in tier_pairs:
        if (_id_matches(a, equip_prefix) and _id_matches(b, target_prefix)) or (
            _id_matches(b, equip_prefix) and _id_matches(a, target_prefix)
        ):
            return True
    return False


def is_equip_seating_bearing(
    a: str,
    b: str,
    parts: dict[str, PartRecord],
    threshold: float,
) -> bool:
    """Equipment plotter plane bears on tray/slide seating surface — skin contact only."""
    if not is_equip_seating_pair(a, b):
        return False
    if minimum_clearance(parts[a].solid, parts[b].solid) >= threshold:
        return False
    inter_vol = intersection_volume(parts[a].solid, parts[b].solid)
    return inter_vol <= EQUIP_SEATING_MAX_BEARING_MM3 + threshold


def is_vib_equip_bearing_pair(a: str, b: str) -> bool:
    """True when a,b is a tier-correct vibration-mount pad ↔ equipment plotter pair."""
    tier_pairs = (
        ("VIBMOUNT-P1-", "EQUIP-PLOTTER1-"),
        ("VIBMOUNT-P2-", "EQUIP-PLOTTER2-"),
    )
    for vib_prefix, equip_prefix in tier_pairs:
        if (_id_matches(a, vib_prefix) and _id_matches(b, equip_prefix)) or (
            _id_matches(b, vib_prefix) and _id_matches(a, equip_prefix)
        ):
            return True
    return False


def is_vib_equip_bearing(
    a: str,
    b: str,
    parts: dict[str, PartRecord],
    threshold: float,
) -> bool:
    """Vibration-mount pad embeds into equipment plotter underside — pad volume only."""
    if not is_vib_equip_bearing_pair(a, b):
        return False
    if minimum_clearance(parts[a].solid, parts[b].solid) >= threshold:
        return False
    inter_vol = intersection_volume(parts[a].solid, parts[b].solid)
    return inter_vol <= VIB_EQUIP_MAX_BEARING_MM3 + threshold


def is_tray_slide_pair(a: str, b: str) -> bool:
    """True when a,b is a tier-correct tray platform ↔ slide rail pair."""
    tier_pairs = (
        ("TRAY-LOWER-001", "SLIDE-LOWER-"),
        ("TRAY-UPPER-001", "SLIDE-UPPER-"),
    )
    for tray_id, slide_prefix in tier_pairs:
        if (a == tray_id and _id_matches(b, slide_prefix)) or (
            b == tray_id and _id_matches(a, slide_prefix)
        ):
            return True
    return False


def is_tray_slide_bearing(
    a: str,
    b: str,
    parts: dict[str, PartRecord],
    threshold: float,
) -> bool:
    """Tray platform ↔ slide rail skin bearing — plane-touch only."""
    if not is_tray_slide_pair(a, b):
        return False
    if minimum_clearance(parts[a].solid, parts[b].solid) >= threshold:
        return False
    inter_vol = intersection_volume(parts[a].solid, parts[b].solid)
    return inter_vol <= TRAY_SLIDE_MAX_BEARING_MM3 + threshold


def is_cover_svc_panel_pair(a: str, b: str) -> bool:
    """True when a,b is a service cover ↔ panel mating pair."""
    return (_id_matches(a, "COVER-SVC-") and _id_matches(b, "PANEL-")) or (
        _id_matches(b, "COVER-SVC-") and _id_matches(a, "PANEL-")
    )


def is_cover_svc_panel_bearing(
    a: str,
    b: str,
    parts: dict[str, PartRecord],
    threshold: float,
) -> bool:
    """Service cover flush-mounted on panel — skin bearing only."""
    if not is_cover_svc_panel_pair(a, b):
        return False
    if minimum_clearance(parts[a].solid, parts[b].solid) >= threshold:
        return False
    inter_vol = intersection_volume(parts[a].solid, parts[b].solid)
    return inter_vol <= COVER_SVC_PANEL_MAX_BEARING_MM3 + threshold


def is_cover_svc_frame_base_pair(a: str, b: str) -> bool:
    """True when a,b is a service cover ↔ base rail mating pair."""
    return (_id_matches(a, "COVER-SVC-") and _id_matches(b, "FRAME-RAIL-BASE-")) or (
        _id_matches(b, "COVER-SVC-") and _id_matches(a, "FRAME-RAIL-BASE-")
    )


def is_cover_svc_frame_base_bearing(
    a: str,
    b: str,
    parts: dict[str, PartRecord],
    threshold: float,
) -> bool:
    """Service cover flush-mounted on base rail — skin bearing only."""
    if not is_cover_svc_frame_base_pair(a, b):
        return False
    if minimum_clearance(parts[a].solid, parts[b].solid) >= threshold:
        return False
    inter_vol = intersection_volume(parts[a].solid, parts[b].solid)
    return inter_vol <= COVER_SVC_FRAME_BASE_MAX_BEARING_MM3 + threshold


def is_cover_svc_frame_post_pair(a: str, b: str) -> bool:
    """True when a,b is a service cover ↔ rear corner post mating pair."""
    return (
        _id_matches(a, "COVER-SVC-")
        and (_id_matches(b, "FRAME-POST-RL-") or _id_matches(b, "FRAME-POST-RR-"))
    ) or (
        _id_matches(b, "COVER-SVC-")
        and (_id_matches(a, "FRAME-POST-RL-") or _id_matches(a, "FRAME-POST-RR-"))
    )


def is_cover_svc_frame_post_bearing(
    a: str,
    b: str,
    parts: dict[str, PartRecord],
    threshold: float,
) -> bool:
    """Service cover overlap with rear corner post — penetrating / share_face skin only."""
    if not is_cover_svc_frame_post_pair(a, b):
        return False
    if minimum_clearance(parts[a].solid, parts[b].solid) >= threshold:
        return False
    inter_vol = intersection_volume(parts[a].solid, parts[b].solid)
    return inter_vol <= COVER_SVC_FRAME_POST_MAX_BEARING_MM3 + threshold


def is_mating(
    a: str,
    b: str,
    parts: dict[str, PartRecord] | None = None,
    *,
    threshold: float | None = None,
    params: Parameters | None = None,
) -> bool:
    """Return True when zero-distance contact between a and b is expected."""
    if pair_key(a, b) in MATING_PAIRS:
        if is_equip_seating_pair(a, b):
            if parts is None or threshold is None:
                return False
            return is_equip_seating_bearing(a, b, parts, threshold)
        if is_tray_slide_pair(a, b):
            if parts is None or threshold is None:
                return False
            return is_tray_slide_bearing(a, b, parts, threshold)
        if is_vib_equip_bearing_pair(a, b):
            if parts is None or threshold is None:
                return False
            return is_vib_equip_bearing(a, b, parts, threshold)
        if is_cover_svc_panel_pair(a, b):
            if parts is None or threshold is None:
                return False
            return is_cover_svc_panel_bearing(a, b, parts, threshold)
        return True
    if parts is None or threshold is None:
        return False

    if is_door_mate(a, b, parts, threshold):
        return True

    if is_slide_vibmount_bearing(a, b, parts, threshold):
        return True

    if is_foot_structure_contact(a, b, parts, threshold):
        return True

    if is_stack_cap_mate(a, b, parts, threshold):
        return True

    if is_frame_post_bearing(a, b, parts, threshold):
        return True

    solid_a = parts[a].solid
    solid_b = parts[b].solid

    # Aluminium frame members sharing a corner/edge joint.
    if a.startswith("FRAME-") and b.startswith("FRAME-"):
        return aabb_share_face(solid_a, solid_b, threshold)

    # Inner/outer panel sandwich and shell corner joints.
    if _share_face_if_prefix(a, b, parts, threshold, "PANEL-IN-", "PANEL-OUT-"):
        return True
    if _share_face_if_prefix(a, b, parts, threshold, "PANEL-IN-", "PANEL-IN-"):
        return True
    if _share_face_if_prefix(a, b, parts, threshold, "PANEL-OUT-", "PANEL-OUT-"):
        return True
    # Panels flush-mounted to frame rails/posts.
    if _share_face_if_prefix(a, b, parts, threshold, "PANEL-IN-", "FRAME-"):
        if not (
            _matches_penetrating_patterns(a, b, ORG_REAR_PENETRATING_PATTERNS)
            or _matches_penetrating_patterns(a, b, POST_PANEL_PENETRATING_PATTERNS)
            or _matches_penetrating_patterns(a, b, TRAY_RAIL_PANEL_PENETRATING_PATTERNS)
        ):
            return True
    if _is_side_slab_frame_pair(a, b) is not None:
        if params is None:
            return False
        return is_side_slab_frame_cavity_joint(a, b, parts, params, threshold)
    if _share_face_if_prefix(a, b, parts, threshold, "PANEL-OUT-", "FRAME-"):
        return True
    # Cosmetic opal strips flush over front frame rails and side-slab inner faces (PLT-006).
    if a.startswith("PANEL-CLAD-FRONT-") or b.startswith("PANEL-CLAD-FRONT-"):
        other = b if a.startswith("PANEL-CLAD-FRONT-") else a
        if other.startswith(("FRAME-", "PANEL-OUT-", "PANEL-IN-", "PANEL-CLAD-FRONT-")):
            if aabb_share_face(solid_a, solid_b, threshold):
                return True
        # Tray-rail cladding (PLT-010) meets inner partition skins at Y=y0 without a full
        # AABB face — same cosmetic-over-shell intent as BASE/ORG/TOP front strips.
        clad_id = a if a.startswith("PANEL-CLAD-FRONT-TRAY-") else b
        if clad_id.startswith("PANEL-CLAD-FRONT-TRAY-") and other.startswith("PANEL-IN-"):
            if minimum_clearance(solid_a, solid_b) < threshold:
                return True

    # Side slabs meet organizer stack at the internal side-clearance boundary (X=20 / X=630).
    for side_prefix in ("PANEL-OUT-LEFT", "PANEL-OUT-RIGHT"):
        if _share_face_if_prefix(a, b, parts, threshold, side_prefix, "ORG-"):
            return True
        if _share_face_if_prefix(a, b, parts, threshold, side_prefix, "SHELF-"):
            return True

    # D-059 shelf-support cleats bear on side panels (D-075 posts restored at corners).
    for support_prefix in ("SHELF-SUPPORT-L-", "SHELF-SUPPORT-R-"):
        if a.startswith(support_prefix) and b.startswith("PANEL-OUT-"):
            if minimum_clearance(solid_a, solid_b) < threshold:
                return True
        if b.startswith(support_prefix) and a.startswith("PANEL-OUT-"):
            if minimum_clearance(solid_a, solid_b) < threshold:
                return True

    # Organizer stack and org-support rails.
    if _share_face_if_prefix(a, b, parts, threshold, "ORG-", "ORG-"):
        return True
    if _share_face_if_prefix(a, b, parts, threshold, "ORG-", "FRAME-RAIL-ORG"):
        return True

    # Tray/slide pairs mounted on tray carrier rails (same-tier only — D-098).
    if _share_face_if_prefix(a, b, parts, threshold, "TRAY-", "FRAME-RAIL-TRAY"):
        if not _is_cross_tier_tray_slide_rail_pair(a, b):
            return True
    if _share_face_if_prefix(a, b, parts, threshold, "SLIDE-", "FRAME-RAIL-TRAY"):
        if not _is_cross_tier_tray_slide_rail_pair(a, b):
            return True

    # Interlock hardware in the captive channel between slide zones.
    if a.startswith("INTERLOCK-") or b.startswith("INTERLOCK-"):
        other = b if a.startswith("INTERLOCK-") else a
        interlock_id = a if a.startswith("INTERLOCK-") else b
        channel_prefixes = (
            "FRAME-RAIL-TRAY",
            "FRAME-RAIL-BASE",
            "PANEL-IN-",
            "TRAY-",
            "SLIDE-",
            "PANEL-OUT-",
        )
        if other.startswith(channel_prefixes) or other.startswith("INTERLOCK-"):
            if aabb_share_face(solid_a, solid_b, threshold):
                return True
        if interlock_id == "INTERLOCK-SHUTTLE-001" and other.startswith("INTERLOCK-TAB-"):
            return True

    # Horizontal shelf plates seated on organizer floor/insert — share bottom face only.
    if a.startswith("SHELF-") or b.startswith("SHELF-"):
        other = b if a.startswith("SHELF-") else a
        if other.startswith(("ORG-", "SHELF-")):
            if aabb_share_face(solid_a, solid_b, threshold):
                return True

    # Media-path service cluster on rear panel.
    if _share_face_if_prefix(a, b, parts, threshold, "REARSUPPORT-", "PANEL-"):
        return True
    if _share_face_if_prefix(a, b, parts, threshold, "REARSUPPORT-", "SVC-INSERT-"):
        return True
    if _share_face_if_prefix(a, b, parts, threshold, "EDGEGUARD-", "SVC-INSERT-"):
        return True
    if _share_face_if_prefix(a, b, parts, threshold, "EDGEGUARD-", "PANEL-"):
        return True
    if _share_face_if_prefix(a, b, parts, threshold, "EDGEGUARD-", "REARSUPPORT-"):
        return True
    if _share_face_if_prefix(a, b, parts, threshold, "SVC-INSERT-", "PANEL-"):
        return True
    if _share_face_if_prefix(a, b, parts, threshold, "MAINS-INLET-", "PANEL-"):
        return True
    if is_cover_svc_panel_pair(a, b):
        if _share_face_if_prefix(a, b, parts, threshold, "COVER-SVC-", "PANEL-"):
            return is_cover_svc_panel_bearing(a, b, parts, threshold)
    if is_cover_svc_frame_base_pair(a, b):
        if _share_face_if_prefix(a, b, parts, threshold, "COVER-SVC-", "FRAME-RAIL-BASE"):
            return is_cover_svc_frame_base_bearing(a, b, parts, threshold)
    if is_cover_svc_frame_post_pair(a, b):
        if _share_face_if_prefix(a, b, parts, threshold, "COVER-SVC-", "FRAME-POST-R"):
            return is_cover_svc_frame_post_bearing(a, b, parts, threshold)

    # Rear/bottom service pocket cluster — intentional shared faces.
    if a in REAR_BOTTOM_SERVICE_CLUSTER and b in REAR_BOTTOM_SERVICE_CLUSTER:
        if aabb_share_face(solid_a, solid_b, threshold):
            return True

    if is_service_volume_mount(a, b, parts, threshold):
        return True

    if is_penetrating_structural_joint(a, b, parts, threshold):
        return True

    if is_staggered_tier_y_overlap(a, b, parts, threshold):
        return True

    if is_open_front_kinematic_contact(a, b, parts, threshold):
        return True

    return False


def is_open_front_kinematic_contact(
    a: str,
    b: str,
    parts: dict[str, PartRecord],
    threshold: float,
) -> bool:
    """Front structural/cladding members share the open-front volume with either tray stack.

    Both tiers now share the same front-face Y (D-033), and tier 1 has a documented
    quick-access forward slide distinct from its full extension — the tray/slide/plotter
    stack for either tier is expected to touch front perimeter structure (corner posts,
    base/org front rails, cosmetic cladding) as it travels through the open front opening.
    Concept-stage block geometry does not model precise slide/rail channel clearance
    notches; verify actual clearance on the real prototype (`trays.slide_rail_*`,
    `to_measure`).
    """
    open_front_prefixes = (
        "PANEL-CLAD-FRONT-",
        "FRAME-RAIL-BASE-FRONT-",
        "FRAME-RAIL-ORG-FRONT-",
    )
    stack_prefixes = (
        "TRAY-LOWER-",
        "SLIDE-LOWER-",
        "EQUIP-PLOTTER1-",
        "INTERLOCK-TAB-LOWER-",
        "TRAY-UPPER-",
        "SLIDE-UPPER-",
        "EQUIP-PLOTTER2-",
        "INTERLOCK-TAB-UPPER-",
    )
    for clad_prefix in open_front_prefixes:
        for stack_prefix in stack_prefixes:
            if (_id_matches(a, clad_prefix) and _id_matches(b, stack_prefix)) or (
                _id_matches(b, clad_prefix) and _id_matches(a, stack_prefix)
            ):
                if minimum_clearance(parts[a].solid, parts[b].solid) < threshold:
                    inter_vol = intersection_volume(parts[a].solid, parts[b].solid)
                    return inter_vol <= OPEN_FRONT_MAX_BEARING_MM3 + threshold
    return False


def _is_cross_tier_tray_slide_rail_pair(a: str, b: str) -> bool:
    """TRAY-/SLIDE- on one tier vs opposite-tier FRAME-RAIL-TRAY (D-098).

    Uncapped share_face must not apply — defer to ``is_staggered_tier_y_overlap``.
    """
    tray_slide_lower = ("TRAY-LOWER-", "SLIDE-LOWER-")
    tray_slide_upper = ("TRAY-UPPER-", "SLIDE-UPPER-")
    rail_lower = "FRAME-RAIL-TRAY-LOWER-"
    rail_upper = "FRAME-RAIL-TRAY-UPPER-"

    def _lower_tray_slide(part_id: str) -> bool:
        return any(part_id.startswith(marker) for marker in tray_slide_lower)

    def _upper_tray_slide(part_id: str) -> bool:
        return any(part_id.startswith(marker) for marker in tray_slide_upper)

    if (_lower_tray_slide(a) and b.startswith(rail_upper)) or (
        _lower_tray_slide(b) and a.startswith(rail_upper)
    ):
        return True
    if (_upper_tray_slide(a) and b.startswith(rail_lower)) or (
        _upper_tray_slide(b) and a.startswith(rail_lower)
    ):
        return True
    return False


def is_staggered_tier_y_overlap(
    a: str,
    b: str,
    parts: dict[str, PartRecord],
    threshold: float,
) -> bool:
    """Tiers share the same front-face Y (D-033) and fully overlap in Y.

    They stack in Z instead, so cross-tier Y overlap is intentional by
    design, not a collision. Requires ``intersection_volume <=
    STAGGERED_TIER_MAX_BEARING_MM3 + threshold`` (D-097) — Y overlap alone
    must not silent-green volumetric burial (historical ~43875 mm³).
    """
    lower_markers = (
        "EQUIP-PLOTTER1-",
        "TRAY-LOWER-",
        "SLIDE-LOWER-",
        "FRAME-RAIL-TRAY-LOWER-",
        "SOFTSTOP-LOWER-",
        "VIBMOUNT-P1-",
        "INTERLOCK-TAB-LOWER-",
    )
    upper_markers = (
        "EQUIP-PLOTTER2-",
        "TRAY-UPPER-",
        "SLIDE-UPPER-",
        "FRAME-RAIL-TRAY-UPPER-",
        "SOFTSTOP-UPPER-",
        "VIBMOUNT-P2-",
        "INTERLOCK-TAB-UPPER-",
    )

    def _tier(part_id: str) -> str | None:
        if any(part_id.startswith(marker) for marker in lower_markers):
            return "lower"
        if any(part_id.startswith(marker) for marker in upper_markers):
            return "upper"
        return None

    tier_a = _tier(a)
    tier_b = _tier(b)
    if tier_a is None or tier_b is None or tier_a == tier_b:
        return False
    bounds_a = bounding_box_bounds(parts[a].solid)
    bounds_b = bounding_box_bounds(parts[b].solid)
    y_overlap = min(bounds_a[1][1], bounds_b[1][1]) - max(bounds_a[1][0], bounds_b[1][0])
    if y_overlap <= threshold:
        return False
    inter_vol = intersection_volume(parts[a].solid, parts[b].solid)
    return inter_vol <= STAGGERED_TIER_MAX_BEARING_MM3 + threshold


def intentional_block_pair(state_name: str, a: str, b: str) -> bool:
    """Shuttle blocking contact in service states — excluded from clearance sweep."""
    shuttle = "INTERLOCK-SHUTTLE-001"
    if shuttle not in (a, b):
        return False
    other = b if a == shuttle else a
    if state_name == "service_plotter_1":
        blocked = UPPER_KINEMATIC_GROUP | {
            "PANEL-IN-MID-001",
            "SLIDE-UPPER-RIGHT-001",
            "FRAME-RAIL-TRAY-UPPER-R-001",
        }
        return other in blocked or other.startswith("PANEL-OUT-")
    if state_name == "service_plotter_2":
        blocked = LOWER_KINEMATIC_GROUP | {
            "SLIDE-LOWER-RIGHT-001",
            "FRAME-RAIL-TRAY-LOWER-R-001",
            "FRAME-RAIL-BASE-FRONT-001",
        }
        return other in blocked
    return False


def check_containment_pairs(
    parts: dict[str, PartRecord],
    params: Parameters,
) -> list[str]:
    """Assert equipment reference bodies are fully contained in their design envelopes."""
    threshold = float(params.value(COLLISION_THRESHOLD_PATH))
    violations: list[str] = []
    for equip_id, env_id in CONTAINED_PAIRS:
        equip = parts[equip_id].solid
        env = parts[env_id].solid
        inter = intersection_volume(equip, env)
        equip_vol = equip.volume
        if abs(inter - equip_vol) > threshold:
            violations.append(
                f"{equip_id} not contained in {env_id}: "
                f"intersection {inter:.3f} mm^3 != equip volume {equip_vol:.3f} mm^3 "
                f"(tolerance {threshold} mm from {COLLISION_THRESHOLD_PATH})"
            )
    return violations


def check_collision_pairs(
    parts: dict[str, PartRecord],
    params: Parameters,
    state_name: str,
) -> list[str]:
    """Return violation messages; empty list means pass."""
    threshold = float(params.value(COLLISION_THRESHOLD_PATH))
    violations = check_containment_pairs(parts, params)

    part_ids = sorted(pid for pid in parts if pid not in COLLISION_EXCLUDE)
    for a_id, b_id in combinations(part_ids, 2):
        if is_mating(a_id, b_id, parts, threshold=threshold, params=params):
            continue
        if intentional_block_pair(state_name, a_id, b_id):
            continue
        clearance = minimum_clearance(parts[a_id].solid, parts[b_id].solid)
        if clearance < threshold:
            violations.append(
                f"{state_name}: {a_id}<->{b_id} clearance {clearance:.3f} mm "
                f"< threshold {threshold} mm from {COLLISION_THRESHOLD_PATH}"
            )
    return violations
