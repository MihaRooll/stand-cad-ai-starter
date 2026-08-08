"""Idempotent entry point for CONCEPT/REFERENCE_ONLY assembly STEP export."""


from stand_cad.geometry.export import generate_concept_model


def main() -> None:
    result = generate_concept_model()
    print(f"Exported {result['step_path']} ({result['part_count']} parts)")
    print(f"Live bbox: {result['live_metrics']['bbox_size_mm']}")
    print(f"Read-back solids: {result['readback_metrics']['solid_count']}")


if __name__ == "__main__":
    main()
