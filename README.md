# Single-leaf-based coverage analysis of plant protection products

This repository contains the Python source code for the image-analysis pipeline described in:

**Evaluating Drone-Based Versus Conventional Spraying Systems for Fungicide Application in Sugar Beet: Impacts on Canopy Penetration and Disease Dynamics**

The pipeline was developed to quantify fluorescent tracer coverage and its spatial distribution across leaf surfaces. It processes visible-light images and corresponding UV-fluorescence images and produces quadrant-specific dye coverage metrics and measures of vertical and horizontal deposition asymmetry.

## Repository structure

```text
leaf-fluorescence-analysis/
├── README.md
├── environment.yml
├── LICENSE
├── CITATION.cff
├── .gitignore
├── data/
│   └── source/
│       ├── vis/                 # Example visible-light images
│       └── uv/                  # Corresponding UV-fluorescence images
└── coverage_analysis/
    ├── 01_leaf_masking.py
    ├── 02_spatial_partitioning.py
    ├── 03_masking_tracer.py
    └── 04_tracer_distribution_patterns.py
```

The `data/source/` directory is intended for the example images distributed with the repository. Intermediate processing outputs are written to `data/processed/` when the pipeline is run using the commands below.

## Pipeline overview

The workflow consists of four steps:

1. **Leaf masking (`01_leaf_masking.py`)** – segments leaves from the background in visible-light (`vis`) images.
2. **Spatial partitioning (`02_spatial_partitioning.py`)** – divides each leaf mask into four quadrants: top-left, top-right, bottom-left, and bottom-right.
3. **Fluorescent tracer masking (`03_masking_tracer.py`)** – detects blue/UV fluorescence within the leaf mask and writes the segmented image, fluorescence mask, and overlay.
4. **Tracer distribution metrics (`04_tracer_distribution_patterns.py`)** – calculates dye coverage for each leaf quadrant and vertical and horizontal asymmetry.

Run the scripts in numerical order.

## Requirements and installation

The software environment is specified in `environment.yml`. The instructions below use Conda and are intended for Linux, Windows, and macOS.

Clone the repository:

```bash
git clone https://github.com/barreto91/leaf-fluorescence-analysis.git
cd leaf-fluorescence-analysis
```

Create and activate the Conda environment:

```bash
conda env create -f environment.yml
conda activate conda env create -f environment.yml
conda activate leaf-fluorescence-analysis
```

> **Note:** The environment name in the activation command must match the `name:` field in `environment.yml`. If that field has a different value, use that name instead.

## Running the example pipeline

The commands below assume that the repository has the directory structure shown above and that the example visible-light and UV images are stored in `data/source/vis/` and `data/source/uv/`, respectively.

From the repository root, run the following commands.

### 1. Create leaf masks

```bash
python coverage_analysis/01_leaf_masking.py --input_folder "data/source/vis" --output_folder "data/processed/leaf_mask"
```

### 2. Divide leaves into sections

```bash
python coverage_analysis/02_spatial_partitioning.py --mask_folder "data/processed/leaf_mask" --output_folder "data/processed/leaf_segments"
```

This step creates one subdirectory for each section: `top_left`, `top_right`, `bottom_left`, and `bottom_right`.

### 3. Detect fluorescent tracer

**Check the input directory name:** the original README used `leaf_seg` for this script, whereas Step 2 writes to `leaf_segments`. Confirm which directory name the script expects before running this command. The command below retains the original `leaf_seg` argument.

```bash
python coverage_analysis/03_masking_tracer.py --leaf_mask_folder "data/processed/leaf_mask" --leaf_seg_folder "data/processed/leaf_segments" --uv_folder "data/source/uv" --mask_output_folder "data/processed/fluorescence_mask" --overlay_output_folder "data/processed/fluorescence_overlay"
```

### 4. Calculate tracer distribution metrics

```bash
python coverage_analysis/04_tracer_distribution_patterns.py --fluorescence_mask_folder "data/processed/fluorescence_mask" --leaf_quadrant_folder "data/processed/leaf_segments" --output_destination "data/processed"
```

The final step writes `results.csv` to the specified output destination. The reported columns are:

| Column | Description |
|---|---|
| `file_name` | Source TIFF filename |
| `DyC_TL` | Dye coverage in the top-left section |
| `DyC_TR` | Dye coverage in the top-right section |
| `DyC_BL` | Dye coverage in the bottom-left section |
| `DyC_BR` | Dye coverage in the bottom-right section |
| `delta_v` | Absolute difference between average top and bottom coverage |
| `delta_h` | Absolute difference between average right and left coverage |

The quadrant-specific dye coverage is calculated as the number of fluorescent pixels divided by the number of leaf pixels in the corresponding quadrant. `delta_v` and `delta_h` describe the absolute differences between the mean coverage of the upper and lower, and right and left, leaf halves, respectively.

## Data

The repository is intended to include a representative example dataset in `data/source/`. Visible-light and UV-fluorescence images should be paired by filename or another consistent naming convention.

Only include images that you have permission to redistribute. If the complete experimental image dataset is not publicly available, state this clearly and provide only the example images that can be shared.

## Citation

If you use this software, please cite the associated paper and the archived software release. Citation information will be added here after the paper details and repository DOI have been finalized.

See [`CITATION.cff`](CITATION.cff) for the software citation metadata.

## Authors

- Abel Barreto
- Hendrik Könning

## License

The source code is distributed under the MIT License, provided that this license is appropriate for the authors' intended reuse and distribution. See [`LICENSE`](LICENSE). The license for the code does not automatically apply to the example images or other third-party material.
