# Dream Layer Backend

This directory contains the backend server components for the Dream Layer project, including the CLI for LoRA merging.

## Components
- `dream_layer.py`: Main application file
- `txt2img_server.py`: Text-to-Image generation server
- `img2img_server.py`: Image-to-Image generation server
- `cli.py`: Command-line interface for LoRA merging

## CLI Installation

The CLI uses proper Python packaging (no sys.path hacks!). To install:

### Prerequisites
- Python 3.8 or higher
- pip
- ComfyUI (must be in the project root directory)

### Installation
```bash
# From the project root directory
./install_cli.sh
```

This will:
1. Install ComfyUI as a local package
2. Install DreamLayer CLI as a package
3. Create the global `dreamlayer` command

### Using the CLI
```bash
# Show help
dreamlayer --help

# Show merge-lora help
dreamlayer merge-lora --help

# Run a LoRA merge
dreamlayer merge-lora base.safetensors lora.safetensors merged.safetensors

# Run with custom scale
dreamlayer merge-lora base.safetensors lora.safetensors merged.safetensors --scale 0.8
```

### Testing the CLI
You can create test tensor files and test the CLI:

```bash
# Create test tensor files (from project root)
python create_test_tensors.py

# Test the CLI with the generated files
dreamlayer merge-lora test_base.safetensors test_lora.safetensors test_merged.safetensors

# Test with custom scale
dreamlayer merge-lora test_base.safetensors test_lora.safetensors test_merged.safetensors --scale 0.8
```

**Note:** Test files are now available in the project root for easier access!

### Benefits
✅ **No sys.path manipulation** - Clean, proper Python packaging
✅ **Global command available** - Use `dreamlayer` from anywhere
✅ **Better error handling** - Clear import errors if something is missing
✅ **IDE support** - Better autocomplete and debugging

## Server Setup
1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Start the servers:
```bash
# Start comfyui server
python dream_layer.py

# Start txt2img server
python txt2img_server.py

# Start img2img server (in a separate terminal)
python img2img_server.py
```

The servers will be available at:
- Text-to-Image API: http://localhost:5001/api/txt2img
- Image-to-Image API: http://localhost:5001/api/img2img