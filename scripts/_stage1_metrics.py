"""One-off Stage-1 metrics printer — run via ``uv run python scripts/_stage1_metrics.py``."""

from __future__ import annotations

from pathlib import Path

from stand_cad.geometry.analysis import (
    empty_case_mass_kg,
    indicative_tray_deflection_mm,
    loaded_case_centre_of_mass_mm,
    mass_report_rows,
    part_mass_kg,
    stability_report_inputs,
)
from stand_cad.geometry.assembly import build_service_plotter_2_assembly, build_transport_assembly
from stand_cad.geometry.collision import _max_legitimate_skin_bearing_volume_mm3
from stand_cad.geometry.primitives import bounding_box_bounds, intersection_volume
from stand_cad.parameters import load_parameters

DEFAULT_PARAMETERS_PATH = Path(__file__).resolve().parent.parent / "config" / "parameters.yaml"


def _print_side_slab_frame_overlaps(parts: dict, label: str) -> None:
    pairs = [
        ("PANEL-OUT-LEFT-001", "FRAME-POST-FL-001"),
        ("PANEL-OUT-LEFT-001", "FRAME-POST-RL-001"),
        ("PANEL-OUT-RIGHT-001", "FRAME-POST-FR-001"),
        ("PANEL-OUT-RIGHT-001", "FRAME-POST-RR-001"),
        ("PANEL-OUT-LEFT-001", "FRAME-RAIL-BASE-LEFT-001"),
        ("PANEL-OUT-RIGHT-001", "FRAME-RAIL-BASE-RIGHT-001"),
    ]
    print(f"\n=== Side-slab / frame overlaps ({label}) ===")
    for panel_id, frame_id in pairs:
        if panel_id not in parts or frame_id not in parts:
            continue
        vol = intersection_volume(parts[panel_id].solid, parts[frame_id].solid)
        print(f"  {panel_id} vs {frame_id}: {vol:.1f} mm^3")


def _shell_material_totals(rows, material: str) -> float:
    return sum(r.mass_kg for r in rows if r.material == material)


def main() -> None:
    params = load_parameters(DEFAULT_PARAMETERS_PATH)
    transport = build_transport_assembly(params)
    parts = transport.parts

    print("=== Side slab masses ===")
    for pid in ("PANEL-OUT-LEFT-001", "PANEL-OUT-RIGHT-001"):
        rec = parts[pid]
        print(
            f"  {pid}: shell={part_mass_kg(rec, params):.4f} kg "
            f"solid_vol={rec.solid.volume:.0f} mm^3"
        )

    rows = mass_report_rows(parts, params)
    structural = empty_case_mass_kg(parts, params)
    plotter_mass = sum(params.plotter_mass_kg(i) for i in (1, 2))
    all_parts = structural + plotter_mass

    print("\n=== Mass totals ===")
    print(f"  structural: {structural:.3f} kg")
    print(f"  all-parts (+ plotters): {all_parts:.3f} kg")

    com = loaded_case_centre_of_mass_mm(parts, params)
    print("\n=== Loaded CoM (x, y, z) ===")
    print(f"  ({com[0]:.1f}, {com[1]:.1f}, {com[2]:.1f}) mm")
    print(f"  handle_mount_y_mm should be: {com[1]:.1f}")

    for level in ("lower", "upper"):
        report = stability_report_inputs(params, parts, extended_level=level)
        if report.applicable:
            print(f"  tip factor {level}: {report.factor:.3f}")
        elif report.extension_mm <= 0.0:
            print(f"  tip factor {level}: N/A (zero travel / D-076)")
        else:
            print(
                f"  tip factor {level}: N/A "
                f"(non-finite / insufficient overturn arm)"
            )

    defl = indicative_tray_deflection_mm(params)
    print("\n=== Deflection ===")
    print(f"  {defl:.3f} mm")

    p2_bb = bounding_box_bounds(parts["EQUIP-PLOTTER2-001"].solid)
    print("\n=== EQUIP-PLOTTER2-001 Z span ===")
    print(f"  z=[{p2_bb[2][0]:.1f}, {p2_bb[2][1]:.1f}] height={p2_bb[2][1]-p2_bb[2][0]:.1f} mm")

    org_floor = parts["ORG-FLOOR-001"].solid
    org_z_min = bounding_box_bounds(org_floor)[2][0]
    tier2_gap = org_z_min - p2_bb[2][1]
    print(f"  tier-2 lid headroom (plotter top -> ORG-FLOOR underside): {tier2_gap:.1f} mm")

    service_p2 = build_service_plotter_2_assembly(params)
    lid = service_p2.parts["LID-ENVELOPE-P2-001"]
    shuttle = service_p2.parts["INTERLOCK-SHUTTLE-001"]
    shuttle_vol = intersection_volume(lid.solid, shuttle.solid)
    print("\n=== Lid/shuttle (service_plotter_2, tier-2 lid) ===")
    print(f"  LID-ENVELOPE-P2-001 vs INTERLOCK-SHUTTLE-001: {shuttle_vol:.1f} mm^3")

    service_p1 = __import__(
        "stand_cad.geometry.assembly", fromlist=["build_service_plotter_1_assembly"]
    ).build_service_plotter_1_assembly(params)
    lid1 = service_p1.parts["LID-ENVELOPE-P1-001"]
    shuttle1 = service_p1.parts["INTERLOCK-SHUTTLE-001"]
    p1_vol = intersection_volume(lid1.solid, shuttle1.solid)
    print(f"  LID-ENVELOPE-P1-001 vs INTERLOCK-SHUTTLE-001: {p1_vol:.1f} mm^3")

    print("\n=== Per-material shell mass (cast_opal / white_composite / sandwich) ===")
    for mat in ("cast_opal_pmma_3mm", "white_composite_3_4mm", "sandwich_panel_10_12mm"):
        print(f"  {mat}: {_shell_material_totals(rows, mat):.4f} kg")

    print("\n=== Cavity joint bearing ceiling (corner post, left slab) ===")
    panel_bounds = bounding_box_bounds(parts["PANEL-OUT-LEFT-001"].solid)
    post_ceiling = _max_legitimate_skin_bearing_volume_mm3(
        params, panel_bounds, "FRAME-POST-FL-001"
    )
    print(f"  _max_legitimate_skin_bearing_volume_mm3 (FL post) = {post_ceiling:.0f}")

    _print_side_slab_frame_overlaps(parts, "post-change")


if __name__ == "__main__":
    main()
