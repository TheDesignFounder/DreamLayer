# Labeled Grid Exporter

A powerful Python utility for creating labeled image grids from AI-generated artwork, designed for the DreamLayer Open Source Challenge.

## 🎯 Overview

The Labeled Grid Exporter takes a collection of images and assembles them into a visually organized grid with metadata labels overlaid on each image. Perfect for showcasing Stable Diffusion outputs with their generation parameters.

## ✨ Features

- **📁 Directory Processing**: Automatically processes all images in a directory
- **📊 CSV Metadata Integration**: Reads generation parameters from CSV files
- **🎨 Flexible Layout**: Automatic or manual grid layout configuration
- **🏷️ Custom Labels**: Configurable label content and styling
- **🖼️ Multiple Formats**: Supports PNG, JPG, WebP, TIFF, and more
- **⚡ High Performance**: Optimized for large image collections
- **🔧 CLI & API**: Both command-line and programmatic interfaces

## 🚀 Quick Start

### Installation

The grid exporter is included with DreamLayer. No additional installation required.

**Dependencies:**
- Python 3.7+
- Pillow (PIL)
- Standard library modules (csv, os, math, logging)

### Basic Usage

```bash
# Create a simple grid from images
python labeled_grid_exporter.py \
  --input-dir ./outputs \
  --output grid.png

# Create a grid with metadata labels
python labeled_grid_exporter.py \
  --input-dir ./outputs \
  --csv metadata.csv \
  --label-columns seed sampler steps cfg \
  --output labeled_grid.png
```

## 📖 Detailed Usage

### Command Line Interface

```bash
python labeled_grid_exporter.py [OPTIONS]

Required Arguments:
  --input-dir PATH        Directory containing images to grid
  --output PATH           Path to save the output grid image

Optional Arguments:
  --csv PATH              CSV file with metadata (must include 'filename' column)
  --label-columns TEXT    Metadata columns for labels (e.g., seed sampler steps cfg)
  --rows INTEGER          Number of rows in grid (auto-calculated if not specified)
  --cols INTEGER          Number of columns in grid (auto-calculated if not specified)
  --font-size INTEGER     Font size for labels (default: 16)
  --margin INTEGER        Margin around images and labels (default: 10)
  --verbose               Enable verbose logging
```

### Programmatic Usage

```python
from dream_layer_backend_utils.labeled_grid_exporter import (
    validate_inputs, read_metadata, collect_images, assemble_grid
)

# Setup
input_dir = "./outputs"
csv_path = "./metadata.csv"
output_path = "./grid.png"

# Validate inputs
validate_inputs(input_dir, output_path, csv_path)

# Read metadata
csv_records = read_metadata(csv_path)

# Collect images with metadata
images_info = collect_images(input_dir, csv_records)

# Assemble grid
assemble_grid(
    images_info=images_info,
    label_keys=["seed", "sampler", "steps", "cfg"],
    output_path=output_path,
    rows=2,
    cols=2,
    font_size=16,
    margin=10
)
```

## 📊 CSV Metadata Format

The CSV file should include a `filename` column that matches your image files (without extension):

```csv
filename,seed,sampler,steps,cfg,model,prompt
image_001,12345,euler_a,20,7.5,sd-v1-5,"a beautiful landscape"
image_002,67890,dpm++_2m,30,8.0,sd-v2-1,"portrait of a cat"
image_003,11111,ddim,25,6.5,sd-v1-5,"abstract art"
```

### Supported Metadata Fields

- **seed**: Random seed used for generation
- **sampler**: Sampling method (euler_a, dpm++_2m, ddim, etc.)
- **steps**: Number of denoising steps
- **cfg**: Classifier-free guidance scale
- **model**: Model name/version
- **prompt**: Text prompt used
- **negative_prompt**: Negative prompt
- **width/height**: Image dimensions
- **any custom field**: Add your own metadata columns

## 🎨 Output Examples

### Sample Output: `grid.png`

The grid exporter creates high-quality PNG images with:
- **High Resolution**: Maintains image quality
- **Semi-transparent Labels**: Easy to read without obscuring images
- **Consistent Layout**: Uniform cell sizes and spacing
- **Optimized File Size**: Efficient compression

**Sample Grid Characteristics:**
- **Dimensions**: ~1064×1114 pixels (2×2 grid with 512×512 images)
- **Format**: PNG with transparency support
- **File Size**: ~40-50 KB (optimized)
- **Labels**: "seed: 12345 | sampler: euler_a | steps: 20 | cfg: 7.5"

## 🔧 Configuration Options

### Grid Layout

```bash
# Automatic layout (recommended)
python labeled_grid_exporter.py --input-dir ./images --output auto_grid.png

# Fixed 2x3 grid
python labeled_grid_exporter.py --input-dir ./images --output fixed_grid.png --rows 2 --cols 3

# Fixed columns, auto-calculate rows
python labeled_grid_exporter.py --input-dir ./images --output cols_grid.png --cols 4
```

### Label Customization

```bash
# Custom font size
python labeled_grid_exporter.py --input-dir ./images --output large_font.png --font-size 24

# Larger margins
python labeled_grid_exporter.py --input-dir ./images --output spaced_grid.png --margin 20

# Specific label columns
python labeled_grid_exporter.py --input-dir ./images --csv meta.csv \
  --label-columns seed sampler model --output custom_labels.png
```

## 📁 Supported Image Formats

- **PNG** (.png) - Recommended for best quality
- **JPEG** (.jpg, .jpeg) - Good compression
- **WebP** (.webp) - Modern format with good compression
- **TIFF** (.tiff, .tif) - High quality, larger files
- **BMP** (.bmp) - Uncompressed
- **GIF** (.gif) - Animated images supported

## 🧪 Testing

Run the comprehensive test suite:

```bash
# Run all tests
python run_grid_exporter_tests.py

# Run specific tests
python -m pytest tests/test_labeled_grid_exporter.py -v

# Run with detailed output
python -m pytest tests/test_labeled_grid_exporter.py::TestLabeledGridExporter::test_end_to_end_workflow -v -s
```

## 🔍 Troubleshooting

### Common Issues

1. **"Input directory does not exist"**
   - Check the path is correct
   - Ensure you have read permissions

2. **"No supported image files found"**
   - Verify images are in supported formats
   - Check file extensions are lowercase

3. **"CSV file does not exist"**
   - Ensure CSV file path is correct
   - Check file has proper permissions

4. **"Cannot create output directory"**
   - Ensure write permissions for output location
   - Check disk space is available

### Debug Mode

Enable verbose logging for detailed information:

```bash
python labeled_grid_exporter.py --input-dir ./images --output debug.png --verbose
```

## 🏗️ Architecture

### Core Functions

- **`validate_inputs()`**: Validates input paths and permissions
- **`read_metadata()`**: Parses CSV files with error handling
- **`collect_images()`**: Scans directories and merges metadata
- **`determine_grid()`**: Calculates optimal grid layout
- **`assemble_grid()`**: Creates the final grid image
- **`_load_font()`**: Cross-platform font loading

### Design Principles

- **Error Handling**: Graceful failure with descriptive messages
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **Performance**: Optimized for large image collections
- **Flexibility**: Supports various input formats and configurations
- **Quality**: High-resolution output with professional appearance

## 🤝 Contributing

### Adding New Features

1. **Add Tests**: Create corresponding test cases
2. **Update Documentation**: Modify this README
3. **Follow Style**: Use consistent code formatting
4. **Test Thoroughly**: Ensure all tests pass

### Code Style

- **Type Hints**: Use Python type annotations
- **Docstrings**: Include comprehensive function documentation
- **Error Handling**: Provide descriptive error messages
- **Logging**: Use appropriate log levels

## 📄 License

This project is part of the DreamLayer Open Source Challenge and follows the same licensing terms as the main DreamLayer project.

## 🙏 Acknowledgments

- **DreamLayer Team**: For the open source challenge opportunity
- **Pillow (PIL)**: For robust image processing capabilities
- **Python Community**: For excellent tooling and documentation

---

**Created for Task #3 of the DreamLayer Open Source Challenge** 🎨✨ 