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
    ("SVC-INSERT-L1-001", "PANEL-IN-REAR-001"),
    ("SVC-INSERT-L2-001", "PANEL-IN-REAR-001"),
    ("SVC-INSERT-L1-001", "PANEL-OUT-REAR-001"),
    ("SVC-INSERT-L2-001", "PANEL-OUT-REAR-001"),
    ("EDGEGUARD-L1-001", "SVC-INSERT-L1-001"),
    ("EDGEGUARD-L2-001", "SVC-INSERT-L2-001"),
    ("EDGEGUARD-L1-001", "PANEL-IN-REAR-001"),
    ("EDGEGUARD-L2-001", "PANEL-IN-REAR-001"),
    ("EDGEGUARD-L1-001", "REARSUPPORT-L1-001"),
    ("EDGEGUARD-L2-001", "REARSUPPORT-L2-001"),
    ("MAINS-INLET-001", "PANEL-IN-REAR-001"),
    ("MAINS-INLET-001", "PANEL-OUT-REAR-001"),
    ("MAINS-INLET-001", "PANEL-IN-BOTTOM-001"),
    ("COVER-SVC-001", "PANEL-IN-BOTTOM-001"),
    ("COVER-SVC-001", "PANEL-OUT-REAR-001"),
    ("CABLE-CH-001", "PANEL-OUT-LEFT-001"),
    ("CABLE-CH-001", "PANEL-IN-BOTTOM-001"),
    ("LIGHT-STRIP-001", "PANEL-OUT-REAR-001"),
    ("LIGHT-STRIP-001", "FRAME-RAIL-TOP-REAR-001"),
    ("PANEL-CLAD-FRONT-POST-FL-001", "PANEL-IN-MID-001"),
    ("PANEL-CLAD-FRONT-POST-FR-001", "PANEL-IN-MID-001"),
]


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
    ("PANEL-CLAD-FRONT-POST-", "EQUIP-PLOTTER1-"),
)


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
        if intersection_volume(solid_a, solid_b) > threshold:
            return True
    return False


def is_mating(
    a: str,
    b: str,
    parts: dict[str, PartRecord] | None = None,
    *,
    threshold: float | None = None,
) -> bool:
    """Return True when zero-distance contact between a and b is expected."""
    if pair_key(a, b) in MATING_PAIRS:
        return True
    if parts is None or threshold is None:
        return False

    for group in (LOWER_KINEMATIC_GROUP, UPPER_KINEMATIC_GROUP):
        if a in group and b in group:
            return True

    if is_foot_structure_contact(a, b, parts, threshold):
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
        return True
    if _share_face_if_prefix(a, b, parts, threshold, "PANEL-OUT-", "FRAME-"):
        return True
    # Cosmetic opal strips flush over front frame rails and side-slab inner faces (PLT-006).
    if a.startswith("PANEL-CLAD-FRONT-") or b.startswith("PANEL-CLAD-FRONT-"):
        other = b if a.startswith("PANEL-CLAD-FRONT-") else a
        if other.startswith(("FRAME-", "PANEL-OUT-", "PANEL-IN-", "PANEL-CLAD-FRONT-")):
            if aabb_share_face(solid_a, solid_b, threshold):
                return True

    # Side slabs meet organizer stack at the internal side-clearance boundary (X=20 / X=630).
    for side_prefix in ("PANEL-OUT-LEFT", "PANEL-OUT-RIGHT"):
        if _share_face_if_prefix(a, b, parts, threshold, side_prefix, "ORG-"):
            return True
        if _share_face_if_prefix(a, b, parts, threshold, side_prefix, "SHELF-"):
            return True

    # Organizer stack and org-support rails.
    if _share_face_if_prefix(a, b, parts, threshold, "ORG-", "ORG-"):
        return True
    if _share_face_if_prefix(a, b, parts, threshold, "ORG-", "FRAME-RAIL-ORG"):
        return True

    # Tray/slide pairs mounted on tray carrier rails.
    if _share_face_if_prefix(a, b, parts, threshold, "TRAY-", "FRAME-RAIL-TRAY"):
        return True
    if _share_face_if_prefix(a, b, parts, threshold, "SLIDE-", "FRAME-RAIL-TRAY"):
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
    if _share_face_if_prefix(a, b, parts, threshold, "COVER-SVC-", "PANEL-"):
        return True
    if _share_face_if_prefix(a, b, parts, threshold, "COVER-SVC-", "FRAME-RAIL-BASE"):
        return True
    if _share_face_if_prefix(a, b, parts, threshold, "COVER-SVC-", "FRAME-POST-R"):
        return True

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
        "FRAME-POST-FL-",
        "FRAME-POST-FR-",
    )
    stack_prefixes = (
        "TRAY-LOWER-",
        "SLIDE-LOWER-",
        "EQUIP-PLOTTER1-",
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
    design, not a collision.
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
    return y_overlap > threshold


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
        if is_mating(a_id, b_id, parts, threshold=threshold):
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
