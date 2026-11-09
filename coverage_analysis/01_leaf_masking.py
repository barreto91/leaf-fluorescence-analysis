import argparse
from pathlib import Path

import cv2
import numpy as np

def create_leaf_mask(image: np.ndarray):
    """creates a smoothed binary leaf mask from a an vis image"""
    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    hsv_image = cv2.cvtColor(rgb_image, cv2.COLOR_RGB2HSV)

    lower_green = np.array([25, 40, 40])
    upper_green = np.array([90, 255, 255])
    mask = cv2.inRange(hsv_image, lower_green, upper_green)

    # apply erosion
    erosion_kernel = np.ones((3, 3), np.uint8)
    mask = cv2.erode(mask, erosion_kernel, iterations=1)

    # apply morphological closing
    closing_kernel = np.ones((10, 10), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, closing_kernel)

    # fill holes using contour detection
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(mask, contours, -1, 255, thickness=cv2.FILLED)

    return cv2.GaussianBlur(mask, (5, 5), 0)


def process_images(input_directory: Path, output_directory: Path):
    """Create and save one leaf mask for every TIFF input image"""
    output_directory.mkdir(parents=True, exist_ok=True)

    for image_path in sorted(input_directory.glob("*.tif")):
        image = cv2.imread(str(image_path))
        if image is None:
            print(f"Skipping {image_path.name}: image could not be loaded.")
            continue

        mask = create_leaf_mask(image)
        output_path = output_directory / image_path.name
        cv2.imwrite(str(output_path), mask)
        print(f"Saved mask: {output_path}")

def main():
    parser = argparse.ArgumentParser(description="create leaf masks from vis images")
    parser.add_argument("--input_folder", type=Path, required=True, help="Path to directory containing vis leaf images")
    parser.add_argument("--output_folder", type=Path, required=True, help="Path to base output directory for leaf masks")

    args = parser.parse_args()

    process_images(args.input_folder, args.output_folder)
    
if __name__ == "__main__":
    main()
