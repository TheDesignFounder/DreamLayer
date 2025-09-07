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
DREAMLAYER_COMFYUI_CPU_MODE // if no nvidia drivers available run using CPU only. default is false

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
STABILITY_API_KEY=sk-...
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

_The installation scripts will automatically install all dependencies and set up the environment._

---

## Why DreamLayer AI?

| 🔍 Feature                      | 🚀 How it’s better                                                                                          |
| ------------------------------- | ----------------------------------------------------------------------------------------------------------- |
| **Familiar Layout**             | If you’ve used A1111 or Forge, you’ll feel at home in sec. Zero learning curve                              |
| **Modern UX**                   | Responsive design with light & dark themes and a clutter-free interface that lets you work faster           |
| **ComfyUI Engine Inside**       | All generation runs on a proven, modular, stable ComfyUI backend. Ready for custom nodes and advanced hacks |
| **Closed-Source Model Support** | One-click swap to GPT-4o Image, Ideogram V3, Runway Gen-4, Recraft V3, and more                             |
| **Local first**                 | Runs entirely on your GPU with no hosting fees, full privacy, and instant acceleration out of the box       |

---

## Requirements

- Python 3.8+
- Node.js 16+
- 8GB+ RAM recommended

---

## ⭐ Why Star This Repo Now?

Starring helps us trend on GitHub which brings more contributors and faster features.  
Early stargazers get perks:

- **GitHub Hall of Fame**: Your handle listed forever in the README under Founding Supporter
- **Early Builds**: Download private binaries before everyone else
- **Community first hiring**: We prioritize contributors and stargazers for all freelance, full-time, and AI artist or engineering roles.
- **Closed Beta Invites**: Give feedback that shapes 1.0
- **Discord badge**: Exclusive Founding Supporter role

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

## 📚 Documentation

Full docs will ship with the first code release.

[DreamLayer AI - Documentation](https://dreamlayer-ai.github.io/DreamLayer/)

---

## License

DreamLayer AI will ship under the GPL-3.0 license when the code is released.  
All trademarks and closed-source models referenced belong to their respective owners.

---

<p align="center">### Made with ❤️ by builders, for builders • See you in July 2025!</p>

---

## 🧪 Testing

DreamLayer AI includes a comprehensive test suite covering all functionality including ClipScore integration, database operations, and API endpoints.

### Quick Start Testing

```bash
# Install test dependencies
pip install -r tests/requirements.txt

# Run all tests
python tests/run_all_tests.py

# Run specific test categories
python tests/run_all_tests.py unit          # Unit tests only
python tests/run_all_tests.py integration  # Integration tests only
python tests/run_all_tests.py api          # API endpoint tests
python tests/run_all_tests.py clipscore    # ClipScore functionality tests

# Run with verbose output
python tests/run_all_tests.py all -v
```

### Test Categories

| Test File | Coverage | Description |
|-----------|----------|-------------|
| `test_txt2img_server.py` | Text-to-Image API | Tests txt2img generation and database integration |
| `test_img2img_server.py` | Image-to-Image API | Tests img2img generation and database integration |
| `test_run_registry.py` | Run Registry API | Tests database-first API with ClipScore retrieval |
| `test_report_bundle.py` | Report Generation | Tests Mac-compatible report bundle creation |
| `test_clip_score.py` | ClipScore Integration | Tests CLIP model calculation and database storage |
| `test_database_integration.py` | Database Operations | Tests 3-table schema and database operations |

### Test Features

- ✅ **Unit Tests** - Individual component testing
- ✅ **Integration Tests** - End-to-end workflow testing  
- ✅ **API Tests** - HTTP endpoint testing with Flask test client
- ✅ **Database Tests** - SQLite operations with temporary test databases
- ✅ **Mock Testing** - External dependency mocking (ComfyUI, CLIP model)
- ✅ **Error Handling** - Edge cases and error condition testing
- ✅ **Mac Compatibility** - ZIP file generation testing

### Running Individual Tests

```bash
# Run specific test file
python -m pytest tests/test_clip_score.py -v

# Run specific test method
python -m pytest tests/test_clip_score.py::TestClipScore::test_clip_score_calculation_with_mock -v

# Run with coverage report
python -m pytest tests/ --cov=dream_layer_backend --cov-report=html
```

### Test Requirements

The test suite requires these additional dependencies:
- `pytest` - Test framework
- `pytest-cov` - Coverage reporting
- `pytest-mock` - Mocking utilities
- `requests-mock` - HTTP request mocking

Install with: `pip install -r tests/requirements.txt`

