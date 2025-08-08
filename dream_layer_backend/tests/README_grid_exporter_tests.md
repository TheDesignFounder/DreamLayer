# Labeled Grid Exporter Test Suite

This directory contains comprehensive snapshot tests for the labeled grid exporter functionality, which is part of Task #3 of the DreamLayer Open Source Challenge.

## Overview

The test suite validates the labeled grid exporter by:
1. ✅ **Generating dummy test images programmatically** - Creates 4 test images with different colors and patterns
2. ✅ **Creating test CSV data** - Generates metadata that matches the test images
3. ✅ **Running the grid exporter** - Tests various configurations and scenarios
4. ✅ **Validating output** - Ensures grids are exported correctly with expected dimensions and content

## Test Files

- `test_labeled_grid_exporter.py` - Main test suite with comprehensive test cases
- `run_grid_exporter_tests.py` - Simple test runner script with nice output formatting

## Test Coverage

The test suite covers all major functionality:

### 1. Input Validation
- ✅ Valid input directory and output path
- ✅ Invalid input directory (raises appropriate error)
- ✅ Invalid CSV file (raises appropriate error)
- ✅ Output directory creation

### 2. CSV Metadata Handling
- ✅ Reading CSV files with metadata
- ✅ Parsing different column types (seed, sampler, steps, cfg, model)
- ✅ Handling missing or malformed CSV data

### 3. Image Collection
- ✅ Collecting images with metadata from CSV
- ✅ Collecting images without metadata (filename-only labels)
- ✅ Filtering supported image formats
- ✅ Error handling for missing or corrupted images

### 4. Grid Layout Calculation
- ✅ Fixed rows/columns specification
- ✅ Automatic grid layout calculation
- ✅ Edge cases (0 images, 1 image)
- ✅ Nearly square layout optimization

### 5. Grid Assembly
- ✅ Basic grid assembly without metadata
- ✅ Grid assembly with CSV metadata labels
- ✅ Automatic layout calculation
- ✅ Custom font size and margin settings
- ✅ Error handling for empty input

### 6. Output Validation
- ✅ File existence and non-empty content
- ✅ Valid image format (PNG, JPEG, etc.)
- ✅ Reasonable dimensions for grid layout
- ✅ Non-blank content (contains actual image data)
- ✅ File size validation

### 7. End-to-End Workflow
- ✅ Complete workflow from input validation to output
- ✅ Integration of all components
- ✅ Real-world usage scenario

## Running the Tests

### Option 1: Using pytest directly
```bash
cd dream_layer_backend
python -m pytest tests/test_labeled_grid_exporter.py -v
```

### Option 2: Using the test runner script
```bash
cd dream_layer_backend
python run_grid_exporter_tests.py
```

### Option 3: Running specific tests
```bash
# Run only end-to-end workflow test
python -m pytest tests/test_labeled_grid_exporter.py::TestLabeledGridExporter::test_end_to_end_workflow -v -s

# Run only validation tests
python -m pytest tests/test_labeled_grid_exporter.py -k "validate" -v
```

## Test Data Generation

The test suite automatically generates:

### Test Images
- **4 dummy images** with different colors (red, green, blue, yellow)
- **512x512 pixel resolution** each
- **Text overlays** with image information
- **Pattern overlays** for visual interest
- **PNG format** for consistency

### Test CSV Metadata
```csv
filename,seed,sampler,steps,cfg,model
test_image_1.png,12345,euler_a,20,7.5,stable-diffusion-v1-5
test_image_2.png,67890,dpm++_2m,30,8.0,stable-diffusion-v2-1
test_image_3.png,11111,ddim,25,6.5,stable-diffusion-v1-5
test_image_4.png,22222,euler,15,9.0,stable-diffusion-v2-1
```

## Expected Test Results

When all tests pass, you should see:

```
============================= 12 passed in ~4-5s =============================

✅ All tests passed!

Test Summary:
- ✅ Input validation (success and failure cases)
- ✅ CSV metadata reading
- ✅ Image collection (with and without metadata)
- ✅ Grid dimension calculation
- ✅ Grid assembly (basic, with metadata, auto-layout)
- ✅ Custom font and margin settings
- ✅ Error handling (empty input)
- ✅ End-to-end workflow

🎉 The labeled grid exporter is working correctly!
```

## Sample Output Validation

The end-to-end test generates a grid with these characteristics:
- **Dimensions**: ~1064x1114 pixels (2x2 grid with 512x512 images + margins + labels)
- **Format**: PNG
- **File size**: ~40-50 KB
- **Content**: Non-blank with colored test images and metadata labels

## Troubleshooting

### Common Issues

1. **Import errors**: Make sure you're in the `dream_layer_backend` directory
2. **Missing dependencies**: Install required packages: `pip install pytest pillow`
3. **Font issues**: Tests use fallback fonts if system fonts aren't available
4. **Permission errors**: Ensure write permissions for temporary directories

### Debug Mode

Run tests with verbose output and print statements:
```bash
python -m pytest tests/test_labeled_grid_exporter.py -v -s
```

### Individual Test Debugging

To debug a specific test:
```bash
python -m pytest tests/test_labeled_grid_exporter.py::TestLabeledGridExporter::test_name -v -s --pdb
```

## Integration with CI/CD

The test suite is designed to be easily integrated into CI/CD pipelines:

```yaml
# Example GitHub Actions step
- name: Test Labeled Grid Exporter
  run: |
    cd dream_layer_backend
    python -m pytest tests/test_labeled_grid_exporter.py -v
```

## Contributing

When adding new features to the labeled grid exporter:

1. **Add corresponding tests** for new functionality
2. **Update this README** if test structure changes
3. **Ensure all tests pass** before submitting changes
4. **Add edge case tests** for error conditions

## Test Architecture

The test suite uses pytest fixtures for efficient setup:

- `test_data_dir`: Temporary directory for all test data
- `test_images_dir`: Directory containing generated test images
- `test_csv_path`: Path to generated test CSV file
- `output_dir`: Directory for test output files

All fixtures are automatically cleaned up after tests complete.

## Performance

- **Test execution time**: ~4-5 seconds
- **Memory usage**: Minimal (temporary files cleaned up automatically)
- **Disk usage**: Temporary files in system temp directory
- **CPU usage**: Low (simple image generation and processing)

## Future Enhancements

Potential improvements to the test suite:

1. **Performance benchmarks** for large image sets
2. **Memory leak detection** for long-running operations
3. **Cross-platform font testing** for different operating systems
4. **Image quality validation** using perceptual hashing
5. **Concurrent processing tests** for batch operations 