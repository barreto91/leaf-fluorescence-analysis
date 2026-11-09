import argparse
from pathlib import Path

import cv2
import numpy as np
import pandas as pd


def load_quadrant_images(leaf_quadrant_directory: Path, image_name: str):
    """Load the four quadrant masks for an image."""
    leaf_quadrants = {
        q: cv2.imread(str(leaf_quadrant_directory / q / image_name))
        for q in ["top_left", "top_right", "bottom_left", "bottom_right"]
    }
    return leaf_quadrants


def get_coverage_per_quadrant(fluorescence_mask, leaf_quadrants):
    """Calculate dye coverage (DyC) per leaf quadrant (top-left, top-right, bottom-left, bottom-right)"""

    def safe_divide(numerator, denominator):
        return numerator / denominator if denominator != 0 else 0  # Avoid division by zero

    DyC_TL = safe_divide(np.sum(fluorescence_mask * (leaf_quadrants["top_left"] > 0)), np.sum(leaf_quadrants["top_left"]))
    DyC_TR = safe_divide(np.sum(fluorescence_mask * (leaf_quadrants["top_right"] > 0)), np.sum(leaf_quadrants["top_right"]))
    DyC_BL = safe_divide(np.sum(fluorescence_mask * (leaf_quadrants["bottom_left"] > 0)), np.sum(leaf_quadrants["bottom_left"]))
    DyC_BR = safe_divide(np.sum(fluorescence_mask * (leaf_quadrants["bottom_right"] > 0)), np.sum(leaf_quadrants["bottom_right"]))
    DyC = {"DyC_TL": DyC_TL,
           "DyC_TR": DyC_TR,
           "DyC_BL": DyC_BL,
           "DyC_BR": DyC_BR
           }
    return DyC


def get_asymmetry(DyC):
    """
    Calculate ∆V and ∆H using the formula:
    ∆V = | (DyC_TL + DyC_TR) / 2 − (DyC_BL + DyC_BR) / 2 |
    ∆H = | (DyC_TR + DyC_BR) / 2 − (DyC_TL + DyC_BL) / 2 |
    with
    DyC_TL being dye coverage at quadrant top-left
    DyC_TR being dye coverage at quadrant top-right
    DyC_BL being dye coverage at quadrant bottom-left
    DyC_BR being dye coverage at quadrant bottom-right

    Returns:
        ∆V, ∆H
    """
    top_avg    = (DyC["DyC_TL"] + DyC["DyC_TR"]) / 2
    bottom_avg = (DyC["DyC_BL"] + DyC["DyC_BR"]) / 2
    delta_v = abs(top_avg - bottom_avg)

    right_avg = (DyC["DyC_TR"] + DyC["DyC_BR"]) / 2
    left_avg  = (DyC["DyC_TL"] + DyC["DyC_BL"]) / 2
    delta_h = abs(right_avg - left_avg)

    return delta_v, delta_h


def process_tracer_distribution_analysis(fluorescence_mask_directory: Path, leaf_quadrant_directory: Path, output_directory: Path):
    """Analyze each fluorescence mask and save the results as CSV."""
    results = []
    for fluorescence_mask_path in sorted(fluorescence_mask_directory.glob("*.tif")):
        file_name = fluorescence_mask_path.name
        tracer_mask = cv2.imread(str(fluorescence_mask_path))
        leaf_quadrants = load_quadrant_images(leaf_quadrant_directory, file_name)

        if tracer_mask is None or any(q is None for q in leaf_quadrants.values()):
            print(f"Skipping {file_name}: one or more masks could not be loaded.")
            continue

        DyC = get_coverage_per_quadrant(fluorescence_mask=tracer_mask, leaf_quadrants=leaf_quadrants)
        delta_v, delta_h = get_asymmetry(DyC=DyC)
        results.append([file_name, DyC["DyC_TL"], DyC["DyC_TR"], DyC["DyC_BL"], DyC["DyC_BR"], delta_v, delta_h])

    df_results = pd.DataFrame(results, columns=["file_name", "DyC_TL", "DyC_TR", "DyC_BL", "DyC_BR", "delta_v", "delta_h"])
    output_directory.mkdir(parents=True, exist_ok=True)
    output_path = output_directory / "results.csv"
    df_results.to_csv(output_path, index=False)
    print(f"Saved results: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Analyze tracer coverage and asymmetry per leaf quadrant")

    parser.add_argument("--fluorescence_mask_folder", type=Path, required=True, help="Path to directory containing fluorescence masks")
    parser.add_argument("--leaf_quadrant_folder", type=Path, required=True, help="Path to base directory containing the four leaf quadrants")
    parser.add_argument("--output_destination", type=Path, required=True, help="Path to output directory for results.csv")

    args = parser.parse_args()

    process_tracer_distribution_analysis(args.fluorescence_mask_folder, args.leaf_quadrant_folder, args.output_destination)


if __name__ == "__main__":
    main()
