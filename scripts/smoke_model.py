"""Create one simple STEP solid to prove the local CAD toolchain works.

This is not stand geometry and must never be included in a manufacturing package.
"""

from pathlib import Path

from build123d import Box, export_step


def main() -> None:
    output_dir = Path("output/smoke")
    output_dir.mkdir(parents=True, exist_ok=True)
    block = Box(100, 60, 20)
    target = output_dir / "calibration_block_REFERENCE_ONLY.step"
    export_step(block, target)
    bounds = block.bounding_box().size
    actual = (round(bounds.X, 6), round(bounds.Y, 6), round(bounds.Z, 6))
    expected = (100.0, 60.0, 20.0)
    if actual != expected:
        raise RuntimeError(f"Unexpected smoke-model bounds: {actual}, expected {expected}")
    print(f"Created {target} with bounds {actual}")


if __name__ == "__main__":
    main()

