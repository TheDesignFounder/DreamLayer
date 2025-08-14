<h1 align="center">DreamLayer AI</h1>
<p align="center">
  <strong>The Cleanest, Fastest Stable Diffusion WebUI.</strong><br>
  Built for AI artists, researchers, developers, and prompt engineers. Fully open source, and no hosting required.
</p>

<p align="center">
  <b>⭐ Star to Get Early-Supporter Perks ⭐</b> 
</p>

<p align="center">
  <a href="https://dreamlayer-ai.github.io/DreamLayer/">&nbsp;DreamLayer AI - Documentation</a>
</p>

<p align="center">
  <b>Product Vision:</b>
  <a href="https://huggingface.co/blog/ytmack7/benchmarking-diffusion-models">AI Research</a>
</p>


![DreamLayer-UI](https://github.com/user-attachments/assets/d2cb7e4c-0194-4413-ac03-998bbb25c903)

---

## What is DreamLayer AI?

DreamLayer AI is an open-source Stable Diffusion WebUI that keeps the familiar Automatic1111 ⁄ Forge layout you know, replaces the clutter with a modern design system, and runs every generation step on ComfyUI in the background.  
No node graph on screen, no server rental, just a lightning-fast local interface for:

- **AI artists** producing portfolio-ready images
- **Developers and prompt engineers** iterating on prompts and LoRAs
- **Researchers** benchmarking new models and samplers

> **Status:** ✨ **Now live:** Open Alpha • **Beta V1 ships:** **Mid-July 2025**

> ⭐ Star the repo for updates & to get early-supporter perks

---

## ✨ New Features

### 📦 Report Bundle System
Create reproducible generation reports with a single click:
- **Automatic bundling**: Combines results.csv, config.json, and generated images
- **Schema validation**: Ensures CSV compliance and image path resolution
- **Deterministic output**: Stable ZIP creation with SHA256 verification
- **CLI integration**: Use `--report-bundle` flag for automatic reports

```bash
# Generate report bundle
python dream_layer.py --report-bundle --report-out ./my_report.zip
```

### 🎯 Baseline Manager (Presets)
Version-pinned preset system for reproducible generations:
- **Preset hashing**: SHA256-based configuration fingerprinting
- **Version control**: Track preset evolution over time
- **Easy management**: Create, save, and apply presets via CLI or UI
- **Default presets**: Pre-configured for common use cases

```bash
# Apply preset
python dream_layer.py --preset high_quality

# Save current config as preset
python dream_layer.py --save-preset "my_custom_preset"
```

### 🧩 Large-Image Tiling + Blend
Generate high-resolution images with seamless tiling:
- **Smart tiling**: Automatic tile size and overlap calculation
- **Multiple blend modes**: Cosine, linear, and Laplacian blending
- **Seamless joins**: No visible artifacts between tiles
- **Memory efficient**: Process large images without GPU memory issues

```bash
# Enable tiled generation
python dream_layer.py --tiled --tile-size 512 --tile-overlap 64 --blend-mode cosine
```

### 📊 Quality Metrics (CLIP, SSIM, LPIPS)
Comprehensive image quality assessment:
- **CLIP scoring**: Text-image similarity using OpenAI CLIP
- **SSIM**: Structural similarity index for image comparison
- **LPIPS**: Learned perceptual similarity for human-like assessment
- **Batch processing**: Efficient scoring of multiple images
- **Optional dependencies**: Graceful fallback when packages unavailable

```bash
# Enable quality metrics
python dream_layer.py --metrics-clip --metrics-ssim --metrics-lpips
```

## 🧪 Testing

Run the test suite to verify functionality:

```bash
cd dream_layer_backend
python -m pytest tests/ -v
```

### Test Dependencies
The test suite automatically skips tests that require optional dependencies:

| Dependency | Purpose | Test Behavior |
|------------|---------|---------------|
| **torch** | PyTorch for CLIP/LPIPS | Tests skipped if missing |
| **transformers** | HuggingFace models | Tests skipped if missing |
| **lpips** | Perceptual similarity | Tests skipped if missing |
| **scikit-image** | SSIM computation | Tests skipped if missing |
| **numpy** | Array operations | Always required |
| **PIL** | Image processing | Always required |

**Note**: Core functionality tests will always run, ensuring the application works without heavy ML dependencies.

## 📦 Dependencies

### Required Dependencies
- `flask>=3.0.0` - Web framework
- `flask-cors>=4.0.0` - Cross-origin support
- `pillow>=10.0.0` - Image processing
- `requests>=2.31.0` - HTTP client
- `python-dotenv>=7.0.0` - Environment management
- `pytest>=7.8.0` - Testing framework

### Optional Dependencies
Uncomment the lines below in `requirements.txt` to enable additional features:

```bash
# For SSIM (Structural Similarity Index)
scikit-image>=0.19.0

# For LPIPS (Learned Perceptual Image Patch Similarity)
lpips>=0.1.4
torch>=1.9.0
torchvision>=0.10.0

# For CLIP scoring
transformers>=4.20.0
ftfy>=6.1.0
regex>=2022.1.18

# For tiling and image processing
numpy>=1.21.0
scipy>=1.7.0
```

## 🔍 Feature Details

### Report Bundle Determinism
Report bundles are created with deterministic ZIP files:
- Fixed timestamps (1980-01-01 00:00:00) for all entries
- Sorted file order for consistent structure
- Identical contents produce identical SHA256 hashes

**Quick Check**: Generate two bundles from the same run - they should have identical SHA256 hashes.

### Preset Hash Stability
Preset hashes are computed from configuration content only:
- Excludes name and version for stability
- Identical configurations produce identical hashes
- Hash changes only when parameters change

### Quality Metrics Fallbacks
When optional dependencies are unavailable:
- CLIP: Returns `None` scores with warning
- LPIPS: Returns `None` scores with warning  
- SSIM: Returns `None` scores with warning
- Application continues to function normally

## 🚀 Quick Start

### ⭐️ Run with Cursor (Smooth Setup with a Few Clicks)

Easiest way to run DreamLayer 😃 Best for non-technical users

1. **Download this repo**
2. **Open the folder in [Cursor](https://www.cursor.so/)** (an AI-native code editor)
3. Type `run it` or press the **"Run"** button — then follow the guided steps

Cursor will:

- Walk you through each setup step
- Install Python and Node dependencies
- Create a virtual environment
- Start the backend and frontend
- Output a **localhost:8080** link you can open in your browser

⏱️ Takes about 5-10 minutes. No terminal needed. Just click, run, and you're in. 🚀

> On macOS, PyTorch setup may take a few retries. Just keep pressing **Run** when prompted. Cursor will guide you through it.

### Installation

**linux:**

```bash
./install_linux_dependencies.sh
```

**macOS:**

```bash
./install_mac_dependencies.sh
```

**Windows:**

```bash
install_windows_dependencies.ps1
```

### Start Application

**linux:**

```bash
./start_dream_layer.sh
```

**macOS:**

```bash
./start_dream_layer.sh
```

**Windows:**

```bash
start_dream_layer.bat
```

## 🔧 Configuration

### Environment Variables

Set up API keys for cloud models:

```bash
# .env file
OPENAI_API_KEY=your_openai_api_key_here
IDEOGRAM_API_KEY=your_ideogram_api_key_here
BFL_API_KEY=your_bfl_api_key_here
STABILITY_API_KEY=your_stability_api_key_here
```

### Directory Structure

```
DreamLayer/
├── dream_layer_backend/
│   ├── dream_layer.py          # Main Flask API
│   ├── txt2img_server.py       # Text-to-image server
│   ├── img2img_server.py       # Image-to-image server
│   ├── tools/                  # Report bundle tools
│   │   ├── report_bundle.py    # ZIP creation
│   │   └── report_schema.py    # CSV validation
│   ├── core/                   # Core functionality
│   │   ├── presets.py          # Preset management
│   │   └── tiling.py           # Image tiling
│   └── metrics/                # Quality assessment
│       ├── clip_score.py       # CLIP similarity
│       └── ssim_lpips.py       # SSIM & LPIPS
├── dream_layer_frontend/       # React frontend
├── ComfyUI/                    # ComfyUI engine
├── workflows/                  # Pre-configured workflows
│   ├── txt2img/
│   └── img2img/
└── Dream_Layer_Resources/      # Output and resources
    └── output/                 # Generated images
```

## 🧪 Testing

Run comprehensive tests for all new features:

```bash
# Run all tests
pytest tests/

# Run specific feature tests
pytest tests/test_report_bundle.py
pytest tests/test_presets_e2e.py
pytest tests/test_tiling_blend.py
pytest tests/test_quality_metrics.py
```

### Test Dependencies & Skipping

The test suite automatically skips tests that require optional dependencies:

| Dependency | Purpose | Test Behavior |
|------------|---------|---------------|
| **torch + transformers** | CLIP scoring | Tests auto-skip with `@pytest.mark.requires_torch` |
| **lpips** | Perceptual similarity | Tests auto-skip with `@pytest.mark.requires_lpips` |
| **scikit-image** | SSIM computation | Always enabled (lightweight) |
| **tensorflow** | Legacy support | Not required for core functionality |

**Optional deps & test skipping:**
- `torch/transformers` → CLIP (auto-skip if missing)
- `lpips` → LPIPS (auto-skip if missing)  
- `scikit-image` → SSIM (always on, lightweight)

**Example:** Running tests without PyTorch will skip CLIP-related tests but run all others:
```bash
# All tests pass without heavy dependencies
python -m pytest tests/ --tb=short -q
```

### Deterministic Bundle Verification

**Deterministic bundle:** Two bundles with identical contents produce the same SHA256.

To verify that two bundles from the same run produce identical hashes:

```bash
# Build two bundles from the same run
python dream_layer.py --report-bundle --report-out ./bundle1.zip
python dream_layer.py --report-bundle --report-out ./bundle2.zip

# Verify identical hashes (should match)
sha256sum bundle1.zip bundle2.zip
```

## 📦 Dependencies

### Required
- Python 3.8+
- Node.js 16+
- Flask, Pillow, requests

### Optional (for enhanced features)
```bash
# Quality metrics
pip install scikit-image lpips transformers torch torchvision

# Image processing
pip install numpy scipy
```

## 🔍 Feature Details

### Report Bundle System
- **Schema validation**: Ensures CSV compliance with required columns
- **Path rewriting**: Converts absolute paths to relative within bundle
- **Deterministic ZIPs**: Consistent file ordering and timestamps
- **SHA256 verification**: Content integrity checking

### Preset Management
- **Hash computation**: Stable SHA256 of configuration parameters
- **Version tracking**: Incremental preset evolution
- **Compatibility checking**: Verify preset validity across systems
- **Default presets**: High-quality, fast, and balanced configurations

### Tiling System
- **Optimal sizing**: Automatic tile size calculation based on image dimensions
- **Overlap management**: Configurable overlap for seamless blending
- **Blend algorithms**: Cosine, linear, and Laplacian blending modes
- **Memory optimization**: Efficient processing of large images

### Quality Metrics
- **CLIP scoring**: OpenAI CLIP model for text-image similarity
- **SSIM computation**: Structural similarity using scikit-image
- **LPIPS assessment**: Perceptual similarity using AlexNet/VGG
- **Batch processing**: Efficient scoring of multiple images
- **Graceful degradation**: Fallback when dependencies unavailable

## 🚀 Performance Optimization

### GPU Optimization

1. **Enable CUDA** - Ensure PyTorch is installed with CUDA support
2. **Optimize VRAM** - Use appropriate model sizes for your GPU
3. **Batch Processing** - Generate multiple images at once

### Memory Management

```python
# Clear GPU memory after generation
import torch
torch.cuda.empty_cache()
```

### Tiling Optimization

```python
# Calculate optimal tile size for your GPU
from core.tiling import calculate_optimal_tile_size

tile_size, overlap = calculate_optimal_tile_size(
    width=2048, 
    height=2048, 
    max_tile_size=512,  # Based on GPU memory
    min_tile_size=256
)
```

## 📚 Documentation

Full documentation available at: [DreamLayer AI - Documentation](https://dreamlayer-ai.github.io/DreamLayer/)

## 🤝 Contributing

We welcome contributions! Please see our contributing guidelines and code of conduct.

### Development Setup

1. **Install pre-commit hooks** (recommended):
```bash
pip install pre-commit
pre-commit install
```

2. **Run tests**:
```bash
cd dream_layer_backend
python -m pytest tests/ -v
```

3. **Code formatting** (automatic with pre-commit):
```bash
pre-commit run --all-files
```

## 📄 License

DreamLayer AI is licensed under the GPL-3.0 license.

---

<p align="center">### Made with ❤️ by builders, for builders</p>
