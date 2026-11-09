import argparse
from pathlib import Path

import cv2
import numpy as np


def create_fluorescence_mask(leaf_mask: np.ndarray, fluorescence_image: np.ndarray):
    """Return the leaf-segmented image and its fluorescence mask."""
    _, binary_leaf_mask = cv2.threshold(leaf_mask, 128, 255, cv2.THRESH_BINARY)
    segmented_image = cv2.bitwise_and(
        fluorescence_image, fluorescence_image, mask=binary_leaf_mask
    )

    grayscale_image = cv2.cvtColor(segmented_image, cv2.COLOR_BGR2GRAY)
    adaptive_mask = cv2.adaptiveThreshold(
        grayscale_image,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        11,
        2,
    )

    hsv_image = cv2.cvtColor(segmented_image, cv2.COLOR_BGR2HSV)
    lower_blue = np.array([90, 50, 50])
    upper_blue = np.array([140, 255, 255])
    blue_mask = cv2.inRange(hsv_image, lower_blue, upper_blue)
    fluorescence_mask = cv2.bitwise_and(adaptive_mask, blue_mask)

    # Morphological operations for noise removal
    morphology_kernel = np.ones((5, 5), np.uint8)
    fluorescence_mask = cv2.morphologyEx(fluorescence_mask, cv2.MORPH_CLOSE, morphology_kernel, iterations=2)
    fluorescence_mask = cv2.morphologyEx(fluorescence_mask, cv2.MORPH_OPEN, morphology_kernel, iterations=1)

    # Edge detection for refinement
    edges = cv2.Canny(fluorescence_mask, 50, 150)
    refined_mask = cv2.bitwise_or(fluorescence_mask, edges)
    return segmented_image, refined_mask


def process_images(leaf_mask_directory: Path, leaf_segment_directory: Path, uv_image_directory: Path, fluorescence_mask_directory: Path, overlay_directory: Path):
    """Create fluorescence masks and diagnostic images for all leaf masks."""
    output_directories = (
        leaf_segment_directory,
        fluorescence_mask_directory,
        overlay_directory,
    )
    for output_directory in output_directories:
        output_directory.mkdir(parents=True, exist_ok=True)

    for leaf_mask_path in sorted(leaf_mask_directory.glob("*.tif")):
        image_name = leaf_mask_path.name
        fluorescence_image_path = uv_image_directory / image_name

        leaf_mask = cv2.imread(str(leaf_mask_path), cv2.IMREAD_GRAYSCALE)
        fluorescence_image = cv2.imread(str(fluorescence_image_path))
        if leaf_mask is None or fluorescence_image is None:
            print(f"Skipping {image_name}: one or both images could not be loaded.")
            continue

        segmented_image, fluorescence_mask = create_fluorescence_mask(
            leaf_mask, fluorescence_image
        )
        overlay_image = cv2.bitwise_and(
            fluorescence_image,
            fluorescence_image,
            mask=fluorescence_mask,
        )

        cv2.imwrite(str(leaf_segment_directory / image_name), segmented_image)
        cv2.imwrite(str(fluorescence_mask_directory / image_name), fluorescence_mask)
        cv2.imwrite(str(overlay_directory / image_name), overlay_image)
        print(f"Saved fluorescence outputs: {image_name}")

    print("Fluorescence masking completed.")

def main() -> None:
    parser = argparse.ArgumentParser(description="Create fluorescence masks from UV images")

    parser.add_argument("--leaf_mask_folder", type=Path, required=True, help="Path to directory with leaf masks")
    parser.add_argument("--leaf_seg_folder", type=Path, required=True, help="Path to directory in which to save leaf-segmented UV images")
    parser.add_argument("--uv_folder", type=Path, required=True, help="Path to directory containing source UV image")
    parser.add_argument("--mask_output_folder", type=Path, required=True, help="Path to directory in which to save fluorescence masks")
    parser.add_argument("--overlay_output_folder", type=Path, required=True, help="Path to directory in which to save overlay image")

    args = parser.parse_args()

    process_images(
        args.leaf_mask_folder,
        args.leaf_seg_folder,
        args.uv_folder,
        args.mask_output_folder,
        args.overlay_output_folder,
    )


if __name__ == "__main__":
    main()
