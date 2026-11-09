import argparse
from pathlib import Path

import cv2
import numpy as np
import tifffile

QUADRANT_NAMES = ("top_left", "top_right", "bottom_left", "bottom_right")


def create_leaf_quadrants(mask: np.ndarray):
    """Split a leaf mask at the center of its largest contour's bounding box."""
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None

    largest_contour = max(contours, key=cv2.contourArea)
    x, y, width, height = cv2.boundingRect(largest_contour)
    center_x = x + width // 2 # Vertical division
    center_y = y + height // 2 # Horizontal division

    # Create section masks
    left_mask = np.zeros_like(mask)
    right_mask = np.zeros_like(mask)
    top_mask = np.zeros_like(mask)
    bottom_mask = np.zeros_like(mask)

    # Fill halves
    left_mask[:, :center_x] = mask[:, :center_x]
    right_mask[:, center_x:] = mask[:, center_x:]
    top_mask[:center_y, :] = mask[:center_y, :]
    bottom_mask[center_y:, :] = mask[center_y:, :]

    quadrants = {
        "top_left": cv2.bitwise_and(left_mask, top_mask),
        "top_right": cv2.bitwise_and(right_mask, top_mask),
        "bottom_left": cv2.bitwise_and(left_mask, bottom_mask),
        "bottom_right": cv2.bitwise_and(right_mask, bottom_mask),
    }
    return quadrants


def process_masks(input_directory: Path, output_directory: Path):
    """Create and save four quadrants for every leaf mask."""
    quadrant_directories = {
        quadrant_name: output_directory / quadrant_name
        for quadrant_name in QUADRANT_NAMES
    }
    for quadrant_directory in quadrant_directories.values():
        quadrant_directory.mkdir(parents=True, exist_ok=True)

    for mask_path in sorted(input_directory.glob("*.tif")):
        mask = tifffile.imread(mask_path).astype(np.uint8)
        quadrants = create_leaf_quadrants(mask)
        if quadrants is None:
            print(f"Skipping {mask_path.name}: no contours found.")
            continue

        for quadrant_name, quadrant_mask in quadrants.items():
            output_path = quadrant_directories[quadrant_name] / mask_path.name
            tifffile.imwrite(output_path, quadrant_mask)

        print(f"Saved quadrants: {mask_path.name}")

    print("Spatial partitioning completed.")


def main():
    parser = argparse.ArgumentParser(description="Divide leaf masks into four spatial quadrants.")
    parser.add_argument("--mask_folder", type=Path, required=True, help="Path to directory containing leaf masks")
    parser.add_argument("--output_folder", type=Path, required=True, help="Path to base directory in which to save the four quadrants.",)
    
    args = parser.parse_args()
    
    process_masks(args.mask_folder, args.output_folder)


if __name__ == "__main__":
    main()
