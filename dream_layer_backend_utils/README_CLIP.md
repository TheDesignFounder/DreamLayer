# Enhanced Grid Exporter with CLIP Auto-Labeling

This enhanced version of the labeled grid exporter includes CLIP (Contrastive Language-Image Pre-training) integration for automatic image labeling when no CSV metadata is provided.

## Features

- **CLIP Auto-Labeling**: Automatically generate descriptive labels for images using OpenAI's CLIP model
- **Zero-Shot Classification**: No training required - works out of the box
- **Fallback Support**: Falls back to filename-based labels if CLIP fails
- **Multiple CLIP Models**: Support for different CLIP model variants
- **Backward Compatibility**: All existing functionality preserved

## Installation

Install the required dependencies:

```bash
pip install -r requirements_clip.txt
```

Or install manually:

```bash
pip install torch transformers Pillow numpy
```

## Usage

### Command Line Interface

#### Basic CLIP Auto-Labeling
```bash
python labeled_grid_exporter.py input_directory output_grid.png --use-clip
```

#### Specify CLIP Model
```bash
python labeled_grid_exporter.py input_directory output_grid.png --use-clip --clip-model openai/clip-vit-large-patch14
```

#### With Grid Customization
```bash
python labeled_grid_exporter.py input_directory output_grid.png \
    --use-clip \
    --rows 4 --cols 3 \
    --cell-size 300 300 \
    --font-size 16 \
    --margin 15
```

#### Batch Processing with CLIP
```bash
python labeled_grid_exporter.py input_directory output_grid.png \
    --batch dir1 dir2 dir3 \
    --use-clip \
    --format jpg
```

### Python API

#### Basic Usage
```python
from labeled_grid_exporter import assemble_grid_enhanced, GridTemplate

template = GridTemplate("my_grid", 3, 3, (256, 256))

result = assemble_grid_enhanced(
    input_dir="path/to/images",
    output_path="output_grid.png",
    template=template,
    use_clip=True  # Enable CLIP auto-labeling
)
```

#### Advanced Usage
```python
from labeled_grid_exporter import assemble_grid_enhanced, GridTemplate, CLIPLabeler

# Create custom grid template
template = GridTemplate(
    name="custom",
    rows=4,
    cols=4,
    cell_size=(300, 300),
    margin=20,
    font_size=18
)

# Generate grid with CLIP labeling
result = assemble_grid_enhanced(
    input_dir="path/to/images",
    output_path="output_grid.png",
    template=template,
    use_clip=True,
    clip_model="openai/clip-vit-large-patch14",
    export_format="jpg",
    background_color=(240, 240, 240)
)
```

## CLIP Models

Available CLIP models (from fastest to highest quality):

- `openai/clip-vit-base-patch16` - Fastest, good for quick processing
- `openai/clip-vit-base-patch32` - Balanced speed and quality (default)
- `openai/clip-vit-large-patch14` - Higher quality, slower
- `openai/clip-vit-large-patch14-336` - Highest quality, supports larger images

## How CLIP Labeling Works

1. **Image Analysis**: CLIP analyzes each image using its vision encoder
2. **Caption Candidates**: Compares against a predefined set of descriptive captions
3. **Confidence Scoring**: Selects the caption with highest confidence
4. **Fallback**: If confidence is low, tries more specific prompts
5. **Label Generation**: Uses the best caption as the image label

## Label Priority

The system follows this priority order for labels:

1. **CSV Labels** (if `--csv` provided) - Uses specified columns from CSV
2. **CLIP Labels** (if `--use-clip` and no CSV) - Auto-generated descriptions
3. **Filename** (fallback) - Uses the image filename

## Examples

### Example 1: Basic Auto-Labeling
```bash
# Generate a 3x3 grid with CLIP auto-labels
python labeled_grid_exporter.py ./my_images ./output_grid.png --use-clip
```

### Example 2: High-Quality Labels
```bash
# Use larger CLIP model for better quality labels
python labeled_grid_exporter.py ./my_images ./output_grid.png \
    --use-clip \
    --clip-model openai/clip-vit-large-patch14 \
    --cell-size 400 400 \
    --font-size 20
```

### Example 3: Batch Processing
```bash
# Process multiple directories with CLIP labeling
python labeled_grid_exporter.py ./base_dir ./output/ \
    --batch ./dir1 ./dir2 ./dir3 \
    --use-clip \
    --format jpg \
    --rows 2 --cols 3
```

## Performance Considerations

- **First Run**: CLIP model will be downloaded (~150MB for base model)
- **GPU Usage**: Automatically uses CUDA if available, falls back to CPU
- **Memory**: Larger models require more RAM/VRAM
- **Speed**: Processing time scales with image count and model size

## Troubleshooting

### Common Issues

1. **Import Error**: Install transformers library
   ```bash
   pip install transformers
   ```

2. **CUDA Out of Memory**: Use smaller CLIP model or CPU
   ```bash
   --clip-model openai/clip-vit-base-patch16
   ```

3. **Slow Processing**: Use smaller model or reduce image count
   ```bash
   --clip-model openai/clip-vit-base-patch16
   ```

4. **Poor Labels**: Try larger model or different caption candidates
   ```bash
   --clip-model openai/clip-vit-large-patch14
   ```

### Debug Mode
```bash
python labeled_grid_exporter.py input_dir output.png --use-clip --verbose
```

## API Reference

### CLIPLabeler Class

```python
class CLIPLabeler:
    def __init__(self, model_name="openai/clip-vit-base-patch32", device=None)
    def generate_label(self, image: Image.Image, max_length: int = 50) -> str
    def batch_generate_labels(self, images: List[Image.Image], max_length: int = 50) -> List[str]
```

### Enhanced Functions

```python
def assemble_grid_enhanced(
    input_dir: str,
    output_path: str,
    template: GridTemplate,
    label_columns: List[str] = None,
    csv_path: str = None,
    export_format: str = 'png',
    preprocessing: Dict = None,
    background_color: Tuple[int, int, int] = (255, 255, 255),
    progress_callback: Callable = None,
    use_clip: bool = False,
    clip_model: str = "openai/clip-vit-base-patch32"
) -> Dict
```

## License

This enhancement maintains the same license as the original grid exporter. 