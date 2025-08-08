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
  &nbsp;|&nbsp;
  <a href="https://huggingface.co/blog/ytmack7/stable-diffusion-ui-for-creatives">AI Art</a>
</p>


![DreamLayer-UI](https://github.com/user-attachments/assets/d2cb7e4c-0194-4413-ac03-998bbb25c903)

---

## What is DreamLayer AI?

DreamLayer AI is an open-source Stable Diffusion WebUI that keeps the familiar Automatic1111 ⁄ Forge layout you know, replaces the clutter with a modern design system, and runs every generation step on ComfyUI in the background.  
No node graph on screen, no server rental, just a lightning-fast local interface for:

* **AI artists** producing portfolio-ready images  
* **Developers and prompt engineers** iterating on prompts and LoRAs  
* **Researchers** benchmarking new models and samplers  

> **Status:** ✨ **Now live:** Open Alpha • **Beta V1 ships:** **Mid-July 2025**

> ⭐ Star the repo for updates & to get early-supporter perks

---

## Quick Start

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

⏱️ Takes about 5-10 minutes. No terminal needed. Just click, run, and you’re in. 🚀

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
### Env Variables
**install_dependencies_linux**
DLVENV_PATH // preferred path to python virtual env. default is /tmp/dlvenv

**start_dream_layer**
DREAMLAYER_COMFYUI_CPU_MODE // if no nvidia drivers available run using CPU only.  default is false

### Access

- **Frontend:** http://localhost:8080
- **ComfyUI:** http://localhost:8188


### Installing Models ⭐️

DreamLayer ships without weights to keep the download small. You have two ways to add models:

### a) Closed-source API models

DreamLayer can also call external APIs (OpenAI DALL·E, Flux, Ideogram). 

To enable them:

Edit your `.env` file at `dream_layer/.env`:

```bash
OPENAI_API_KEY=sk-...
BFL_API_KEY=flux-...
IDEOGRAM_API_KEY=id-...
```

Once a key is present, the model becomes visible in the dropdown.
No key = feature stays hidden.

### b) Open-source checkpoints (offline)

**Step 1:** Download .safetensors or .ckpt files from:
- Hugging Face
- Civitai
- Your own training runs

**Step 2:** Place the models in the appropriate folders (auto-created on first run):
- Checkpoints/ → # full checkpoints (.safetensors)
- Lora/ → # LoRA & LoCon files
- ControlNet/ → # ControlNet models
- VAE/ → # optional VAEs

**Step 3:** Click Settings ▸ Refresh Model List in the UI — the models appear in dropdowns.

> Tip: Use symbolic links if your checkpoints live on another drive.

*The installation scripts will automatically install all dependencies and set up the environment.* 


---

## Why DreamLayer AI?

| 🔍 Feature | 🚀 How it’s better |
|------------|-----------|
| **Familiar Layout** | If you’ve used A1111 or Forge, you’ll feel at home in sec. Zero learning curve |
| **Modern UX** | Responsive design with light & dark themes and a clutter-free interface that lets you work faster |
| **ComfyUI Engine Inside** | All generation runs on a proven, modular, stable ComfyUI backend. Ready for custom nodes and advanced hacks |
| **Closed-Source Model Support** | One-click swap to GPT-4o Image, Ideogram V3, Runway Gen-4, Recraft V3, and more |
| **Local first** | Runs entirely on your GPU with no hosting fees, full privacy, and instant acceleration out of the box |



---

## Requirements

- Python 3.8+
- Node.js 16+
- 8GB+ RAM recommended

---

## ⭐ Why Star This Repo Now?

Starring helps us trend on GitHub which brings more contributors and faster features.  
Early stargazers get perks:

* **GitHub Hall of Fame**: Your handle listed forever in the README under Founding Supporter  
* **Early Builds**: Download private binaries before everyone else
* **Community first hiring**: We prioritize contributors and stargazers for all freelance, full-time, and AI artist or engineering roles.    
* **Closed Beta Invites**: Give feedback that shapes 1.0  
* **Discord badge**: Exclusive Founding Supporter role

> ⭐ **Hit the star button right now** and join us at the ground floor ☺️

---

## Get Involved Today

1. **Star** this repository.  
2. **Watch** releases for the July code drop.  
3. **Join** the Discord (link coming soon) and say hi.
4. **Open issues** for ideas or feedback & Submit PRs once the code is live
5. **Share** the screenshot on X ⁄ Twitter with `#DreamLayerAI` to spread the word.

All contributions code, docs, art, tutorials—are welcome!

### Contributing

- Create a PR and follow the evidence requirements in the template.
- See [CHANGELOG Guidelines](docs/CHANGELOG_GUIDELINES.md) for detailed contribution process.

---

## 🎨 Labeled Grid Exporter

### What It Does

The Labeled Grid Exporter is a powerful utility that creates organized image grids from AI-generated artwork with metadata labels overlaid on each image. Perfect for showcasing Stable Diffusion outputs with their generation parameters like seed, sampler, steps, and CFG values.

![Task 3 Demo](docs/task3_demo_small.png)

**New in Task 3:** AI-powered auto-labeling with CLIP! The script now intelligently understands image content and generates meaningful descriptions automatically when no CSV metadata is provided.

### How to Run It

```bash
# Basic usage - create a simple grid
python dream_layer_backend_utils/labeled_grid_exporter.py input_folder/ output_grid.png

# With metadata labels from CSV
python dream_layer_backend_utils/labeled_grid_exporter.py input_folder/ output_grid.png --csv metadata.csv --labels seed sampler steps cfg preset

# With AI-powered auto-labeling (no CSV needed)
python dream_layer_backend_utils/labeled_grid_exporter.py input_folder/ output_grid.png --use-clip --rows 3 --cols 3
```

### CLI Arguments and Examples

**Core Arguments:**
- `input_dir` - Directory containing images to process
- `output_path` - Path for the output grid image
- `--csv` - Optional CSV file with metadata
- `--labels` - Column names to use as labels (e.g., seed sampler steps cfg)
- `--rows` / `--cols` - Grid dimensions
- `--cell-size` - Cell dimensions in pixels (default: 256x256)
- `--margin` - Spacing between images (default: 10px)
- `--font-size` - Label text size (default: 16)

**Advanced Features:**
- `--use-clip` - Enable AI auto-labeling with CLIP
- `--clip-model` - Specify CLIP model variant
- `--batch` - Process multiple directories
- `--template` - Save/load grid configurations

**Complete Examples:**

```bash
# ComfyUI workflow output
python dream_layer_backend_utils/labeled_grid_exporter.py comfyui_outputs/ showcase.png --csv generation_log.csv --labels seed sampler steps cfg model --rows 3 --cols 3

# Custom styling
python dream_layer_backend_utils/labeled_grid_exporter.py images/ grid.png --cell-size 512 512 --margin 20 --font-size 24 --background 240 240 240

# Batch processing with AI labeling
python dream_layer_backend_utils/labeled_grid_exporter.py --batch folder1/ folder2/ folder3/ output_dir/ --use-clip --rows 2 --cols 4

# Quick demo
python dream_layer_backend_utils/labeled_grid_exporter.py tests/fixtures/images tests/fixtures/demo_grid.png --csv tests/fixtures/metadata.csv --labels seed sampler steps cfg preset --rows 2 --cols 2
```

**Sample CSV Format:**
```csv
filename,seed,sampler,steps,cfg,preset,model
image_001.png,12345,euler_a,20,7.0,Standard,sd_xl_base.safetensors
image_002.png,67890,dpm++_2m,25,8.5,Quality,sd_xl_base.safetensors
```

Run `python dream_layer_backend_utils/labeled_grid_exporter.py --help` for complete documentation.

---

## 📚 Documentation

Full docs will ship with the first code release.

[DreamLayer AI - Documentation](https://dreamlayer-ai.github.io/DreamLayer/)


---

## License

DreamLayer AI will ship under the GPL-3.0 license when the code is released.  
All trademarks and closed-source models referenced belong to their respective owners.

---

<p align="center">### Made with ❤️ by builders, for builders • See you in July 2025!</p>
