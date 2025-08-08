# Labeled Grid Exporter

A powerful Python utility for creating labeled image grids from AI-generated artwork, designed for the DreamLayer project.

## Purpose

The Labeled Grid Exporter takes a collection of images and assembles them into a visually organized grid with metadata labels overlaid on each image. Perfect for showcasing Stable Diffusion outputs with their generation parameters.

## Quick Start

### Basic Usage

```bash
# Create a simple grid from images
python labeled_grid_exporter.py images/ output.png

# Create a grid with metadata labels  
python labeled_grid_exporter.py images/ output.png --csv metadata.csv --labels seed sampler steps cfg preset
```

### Example Command

```bash
python labeled_grid_exporter.py tests/fixtures/images tests/fixtures/grid.png --csv tests/fixtures/metadata.csv --labels seed sampler steps cfg preset --rows 2 --cols 2
```

## Sample CSV Format

```csv
filename,seed,sampler,steps,cfg,preset
image_001.png,12345,euler_a,20,7.0,Standard
image_002.png,67890,dpm++,25,8.5,Quality
image_003.png,11111,heun,30,6.0,Fast
image_004.png,22222,lms,15,9.0,Creative
```

## Features

- **Directory Processing**: Automatically processes all images in a directory
- **CSV Metadata Integration**: Reads generation parameters from CSV files  
- **Flexible Layout**: Automatic or manual grid layout configuration
- **Custom Labels**: Configurable label content and styling
- **Multiple Formats**: Supports PNG, JPG, WebP, TIFF, and more
- **ComfyUI Compatible**: Works seamlessly with ComfyUI outputs
- **CLIP Auto-labeling**: AI-powered labeling when no CSV is provided

## CLI Options

```
positional arguments:
  input_dir             Input directory containing images
  output_path           Output path for the grid image

options:
  --csv CSV             CSV file with metadata
  --labels LABELS       Column names to use as labels
  --rows ROWS           Number of rows in grid
  --cols COLS           Number of columns in grid
  --cell-size WIDTH HEIGHT  Cell size (default: 256 256)
  --margin MARGIN       Margin between images (default: 10)
  --font-size SIZE      Font size for labels (default: 16)
  --use-clip            Use CLIP to auto-generate labels
  --help                Show this help message
```

## Requirements

- Python 3.7+
- Pillow (PIL)
- Optional: torch, transformers (for CLIP features)

## Installation

The grid exporter is included with DreamLayer. For CLIP features:

```bash
pip install -r requirements_clip.txt
```