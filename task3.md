# Task #3: Labeled Grid Exporter

## Overview
Create a labeled grid exporter for DreamLayer ComfyUI outputs that takes AI-generated images and creates organized grids with metadata labels overlaid on each image.

## Requirements

### Core Functionality
1. **Grid Building**: Process N images from a folder into a visual grid
2. **CSV Metadata Support**: Optional CSV file with metadata (seed, sampler, steps, cfg, preset, etc.)
3. **Filename Fallback**: Use filenames as labels when CSV is missing
4. **Metadata Display**: Show sampler, steps, CFG, preset, seed when available
5. **Deterministic Output**: Same input should produce same output
6. **Configuration**: Configurable rows/cols, font size, margin
7. **Error Handling**: Handle empty folders, invalid CSV, unsupported image types gracefully

### Workflow Integration
1. **ComfyUI Compatibility**: Work with ComfyUI/Easy Grids standard PNG outputs
2. **Layout Support**: Support 3x3 or any NxM layout
3. **Aspect Preservation**: Maintain aspect ratio, no stretching

### Testing Requirements
1. **Test Suite**: Pytest runs green locally
2. **Fixture Tests**: Create 4 dummy images + tiny CSV for testing
3. **Edge Cases**: Test no CSV, malformed CSV, empty directory scenarios
4. **Snapshot Testing**: Validate grid output dimensions and content

### Developer Experience
1. **CLI Interface**: Clear `--help` documentation
2. **Documentation**: README with purpose, quickstart, examples
3. **Sample Output**: Include or easily generate example output
4. **Repository Hygiene**: Proper .gitignore coverage

### Code Quality
1. **Formatting**: Code formatted with black
2. **Linting**: Clean ruff/flake8 output
3. **Performance**: Font fallback, path validation, robust error handling
4. **No Dead Code**: Remove unused imports and functions

## Expected CLI Interface

```bash
python labeled_grid_exporter.py [input_dir] [output_path] [OPTIONS]

Options:
  --csv CSV                 CSV file with metadata
  --labels LABELS           Column names to use as labels
  --rows ROWS              Number of rows in grid
  --cols COLS              Number of columns in grid  
  --font-size FONT_SIZE    Font size for labels
  --margin MARGIN          Margin between images
```

## Test Commands

```bash
# Format check
python -m black --check .

# Linting
ruff . # or flake8 .

# Tests
pytest -q

# Smoke test
python labeled_grid_exporter.py tests/fixtures/images tests/fixtures/grid.png --csv tests/fixtures/metadata.csv --labels seed sampler steps cfg preset --rows 2 --cols 2
```

## Success Criteria
- All tests pass
- Smoke test generates proper grid
- Code is properly formatted and linted
- Documentation is complete and clear
- Error handling is robust