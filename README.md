<h1 align="center">DreamLayer AI</h1>
<p align="center">
  <strong>The Fastest Way to Benchmark Diffusion Models.</strong><br>
  Built for AI researchers, labs, and developers. Automates prompts, seeds, and metrics so benchmarks that take weeks now run reproducibly in hours.
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

DreamLayer AI is an open source platform for benchmarking and evaluating diffusion models. It currently supports image generation, with video and audio model benchmarking coming soon. It automates the full workflow from prompts and seeds to metrics and logging, making experiments reproducible by default.

No custom scripts, no manual logging, no wasted compute. A streamlined workflow for:

- **AI researchers** benchmarking models, datasets, and samplers
- **Labs and teams** running reproducible evaluations across multiple seeds and configs
- **Developers** integrating custom metrics and evaluation pipelines

> **Status:** ✨ **Now live: Beta V1**

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

**Windows (PowerShell):**

```powershell
# If needed, allow script execution for this session:
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

.\install_windows_dependencies.ps1
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

Edit your `.env` file in the repository root (`./.env`):

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

### Optional: Download Evaluation Datasets

For FID scoring, download the CIFAR-10 reference dataset:

```bash
python scripts/fetch_datasets.py
```

> **Note:** The YOLO model (`yolov8n.pt`, ~6MB) for object detection metrics auto-downloads on first use.

---

## Why DreamLayer AI?

| 🔍 Feature                      | 🚀 How it’s better                                                                                          |
| ------------------------------- | ----------------------------------------------------------------------------------------------------------- |
| **Automated Benchmarking**             | Turn a 1–2 week manual benchmarking task into 3–5 hours per model                              |
| **Reproducibility**                   | Every run is logged with prompts, seeds, configs, and metrics for exact replay           |
| **Metrics Built In**       | CLIP Score, FID, Precision, Recall, F1 with support for custom metrics |
| **Multi Modal Ready** | Benchmark image, video, and audio models with one pipeline                             |
| **Researcher Friendly**                 | Runs locally or on your GPUs with CSV exports, reports, and leaderboard ready outputs       |

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

-----

## ⭐ Founding Supporters

We’re grateful to our earliest supporters who starred the repo and supported us from the start 🚀

<table>
  <tr>
    <td valign="top">@NyayadhishViraj: https://github.com/NyayadhishViraj</td>
    <td valign="top">@yash120394: https://github.com/yash120394</td>
    <td valign="top">@amyzliu: https://github.com/amyzliu</td>
  </tr>
  <tr>
    <td valign="top">@joshiVishrut: https://github.com/joshiVishrut</td>
    <td valign="top">@shreyaspapi: https://github.com/shreyaspapi</td>
    <td valign="top">@vj72: https://github.com/vj72</td>
  </tr>
  <tr>
    <td valign="top">@yashpkm: https://github.com/yashpkm</td>
    <td valign="top">@sauravraiguru: https://github.com/sauravraiguru</td>
    <td valign="top">@krishpat3366: https://github.com/krishpat3366</td>
  </tr>
  <tr>
    <td valign="top">@prmdk: https://github.com/prmdk</td>
    <td valign="top">@pkydev: https://github.com/pkydev</td>
    <td valign="top">@calahoti: https://github.com/calahoti</td>
  </tr>
  <tr>
    <td valign="top">@evangelinensy: https://github.com/evangelinensy</td>
    <td valign="top">@swift9909: https://github.com/swift9909</td>
    <td valign="top">@amit-chhabra-infinitusai: https://github.com/amit-chhabra-infinitusai</td>
  </tr>
  <tr>
    <td valign="top">@chhabraamit: https://github.com/chhabraamit</td>
    <td valign="top">@miraalk: https://github.com/miraalk</td>
    <td valign="top">@BB-2603: https://github.com/BB-2603</td>
  </tr>
  <tr>
    <td valign="top">@brianod: https://github.com/brianod</td>
    <td valign="top">@ParasVc98: https://github.com/ParasVc98</td>
    <td valign="top">@janetxrm: https://github.com/janetxrm</td>
  </tr>
  <tr>
    <td valign="top">@uAreElle: https://github.com/uAreElle</td>
    <td valign="top">@dk1223: https://github.com/dk1223</td>
    <td valign="top">@mathurah: https://github.com/mathurah</td>
  </tr>
  <tr>
    <td valign="top">@rajgopal123: https://github.com/rajgopal123</td>
    <td valign="top">@Akhil9325: https://github.com/Akhil9325</td>
    <td valign="top">@JeseKi: https://github.com/JeseKi</td>
  </tr>
  <tr>
    <td valign="top">@Ggia71: https://github.com/Ggia71</td>
    <td valign="top">@olivermontes: https://github.com/olivermontes</td>
    <td valign="top">@pksrawal: https://github.com/pksrawal</td>
  </tr>
  <tr>
    <td valign="top">@haroldkabiling: https://github.com/haroldkabiling</td>
    <td valign="top">@rajat4064g: https://github.com/rajat4064g</td>
    <td valign="top">@geeknik: https://github.com/geeknik</td>
  </tr>
  <tr>
    <td valign="top">@Jovy550: https://github.com/Jovy550</td>
    <td valign="top">@sru-cyber: https://github.com/sru-cyber</td>
    <td valign="top">@animeshmitra21: https://github.com/animeshmitra21</td>
  </tr>
  <tr>
    <td valign="top">@johannyu: https://github.com/johannyu</td>
    <td valign="top">@arnob-sengupta: https://github.com/arnob-sengupta</td>
    <td valign="top">@florrdv: https://github.com/florrdv</td>
  </tr>
  <tr>
    <td valign="top">@michelle-chiu: https://github.com/michelle-chiu</td>
    <td valign="top">@minseungseon: https://github.com/minseungseon</td>
    <td valign="top">@shraddha55: https://github.com/shraddha55</td>
  </tr>
  <tr>
    <td valign="top">@GozieN: https://github.com/GozieN</td>
    <td valign="top">@heypeppercrunch: https://github.com/heypeppercrunch</td>
    <td valign="top">@SWAYAMK44: https://github.com/SWAYAMK44</td>
  </tr>
  <tr>
    <td valign="top">@IC-Induja: https://github.com/IC-Induja</td>
    <td valign="top">@toluolubode: https://github.com/toluolubode</td>
    <td valign="top">@aliceli-rr: https://github.com/aliceli-rr</td>
  </tr>
  <tr>
    <td valign="top">@MadhuBajaj15: https://github.com/MadhuBajaj15</td>
    <td valign="top">@RupaliLahoti: https://github.com/RupaliLahoti</td>
    <td valign="top">@Pravoli: https://github.com/Pravoli</td>
  </tr>
  <tr>
    <td valign="top">@lhepchabz: https://github.com/lhepchabz</td>
    <td valign="top">@ahad-s: https://github.com/ahad-s</td>
    <td valign="top">@MarcXMe: https://github.com/MarcXMe</td>
  </tr>
  <tr>
    <td valign="top">@shivang710: https://github.com/shivang710</td>
    <td valign="top">@umairinam76: https://github.com/umairinam76</td>
    <td valign="top">@mhmmdihza: https://github.com/mhmmdihza</td>
  </tr>
  <tr>
    <td valign="top">@Cod-cypher: https://github.com/Cod-cypher</td>
    <td valign="top">@Intechlligent1: https://github.com/Intechlligent1</td>
    <td valign="top">@ramadimasatria: https://github.com/ramadimasatria</td>
  </tr>
  <tr>
    <td valign="top">@rajasami156: https://github.com/rajasami156</td>
    <td valign="top">@UmerBaig123: https://github.com/UmerBaig123</td>
    <td valign="top">@MrRStarkey: https://github.com/MrRStarkey</td>
  </tr>
  <tr>
    <td valign="top">@kxhelilaj: https://github.com/kxhelilaj</td>
    <td valign="top">@saadsh15: https://github.com/saadsh15</td>
    <td valign="top">@serdarzuli: https://github.com/serdarzuli</td>
  </tr>
  <tr>
    <td valign="top">@kevinstubbs: https://github.com/kevinstubbs</td>
    <td valign="top">@jakedent: https://github.com/jakedent</td>
    <td valign="top">@iknoorrawal: https://github.com/iknoorrawal</td>
  </tr>
  <tr>
    <td valign="top">@chaowss: https://github.com/chaowss</td>
    <td valign="top">@MGJillaniMughal: https://github.com/MGJillaniMughal</td>
    <td valign="top">@najeebulhassan: https://github.com/najeebulhassan</td>
  </tr>
  <tr>
    <td valign="top">@Mr-MeerMoazzam: https://github.com/Mr-MeerMoazzam</td>
    <td valign="top">@Whitecoolman: https://github.com/Whitecoolman</td>
    <td valign="top">@ChaymaBrk: https://github.com/ChaymaBrk</td>
  </tr>
  <tr>
    <td valign="top">@Wasif-Maqsood: https://github.com/Wasif-Maqsood</td>
    <td valign="top">@Sofstica-Najeeb-Khan: https://github.com/Sofstica-Najeeb-Khan</td>
    <td valign="top">@TahirHameed74: https://github.com/TahirHameed74</td>
  </tr>
  <tr>
    <td valign="top">@micheal0034: https://github.com/micheal0034</td>
    <td valign="top">@Obaid005: https://github.com/Obaid005</td>
    <td valign="top">@Najeeb-Idrees: https://github.com/Najeeb-Idrees</td>
  </tr>
  <tr>
    <td valign="top">@cciliayang: https://github.com/cciliayang</td>
    <td valign="top">@jenniferchen11: https://github.com/jenniferchen11</td>
    <td valign="top">@abuzarmushtaq: https://github.com/abuzarmushtaq</td>
  </tr>
  <tr>
    <td valign="top">@jihad1973: https://github.com/jihad1973</td>
    <td valign="top">@Ponvishnu: https://github.com/Ponvishnu</td>
    <td valign="top">@darkhorse00512: https://github.com/darkhorse00512</td>
  </tr>
  <tr>
    <td valign="top">@birendra027: https://github.com/birendra027</td>
    <td valign="top">@Haziq046: https://github.com/Haziq046</td>
    <td valign="top">@kaivalyagandhi: https://github.com/kaivalyagandhi</td>
  </tr>
  <tr>
    <td valign="top">@avikonduru: https://github.com/avikonduru</td>
    <td valign="top">@sexylasagna: https://github.com/sexylasagna</td>
    <td valign="top">@nk183: https://github.com/nk183</td>
  </tr>
  <tr>
    <td valign="top">@AliMurtaza096: https://github.com/AliMurtaza096</td>
    <td valign="top">@nokid7: https://github.com/nokid7</td>
    <td valign="top">@NjbSyd: https://github.com/NjbSyd</td>
  </tr>
  <tr>
    <td valign="top">@aslirajesh: https://github.com/aslirajesh</td>
    <td valign="top">@cs96ai: https://github.com/cs96ai</td>
    <td valign="top">@ethansbenjamin: https://github.com/ethansbenjamin</td>
  </tr>
  <tr>
    <td valign="top">@alonso130r: https://github.com/alonso130r</td>
    <td valign="top">@Najeebahmed11: https://github.com/Najeebahmed11</td>
    <td valign="top">@surequinn: https://github.com/surequinn</td>
  </tr>
  <tr>
    <td valign="top">@crispychili: https://github.com/crispychili</td>
    <td valign="top">@scchang-catherine: https://github.com/scchang-catherine</td>
    <td valign="top">@alimurtaza-idrak: https://github.com/alimurtaza-idrak</td>
  </tr>
  <tr>
    <td valign="top">@karanbalaji: https://github.com/karanbalaji</td>
    <td valign="top">@Husnain306: https://github.com/Husnain306</td>
    <td valign="top">@upadhyaykshiti: https://github.com/upadhyaykshiti</td>
  </tr>
  <tr>
    <td valign="top">@YoussefZayed: https://github.com/YoussefZayed</td>
    <td valign="top">@Kblack0610: https://github.com/Kblack0610</td>
    <td valign="top">@yousheng44: https://github.com/yousheng44</td>
  </tr>
  <tr>
    <td valign="top">@harrishanlogan: https://github.com/harrishanlogan</td>
    <td valign="top">@kfj001: https://github.com/kfj001</td>
    <td valign="top">@mananomartinez: https://github.com/mananomartinez</td>
  </tr>
  <tr>
    <td valign="top">@pr0mila: https://github.com/pr0mila</td>
    <td valign="top">@anshit-chaudhari: https://github.com/anshit-chaudhari</td>
    <td valign="top">@srinijammula: https://github.com/srinijammula</td>
  </tr>
  <tr>
    <td valign="top">@Austincain1006: https://github.com/Austincain1006</td>
    <td valign="top">@VThejas: https://github.com/VThejas</td>
    <td valign="top">@garvitalwar: https://github.com/garvitalwar</td>
  </tr>
  <tr>
    <td valign="top">@Gao-Yang-cpu: https://github.com/Gao-Yang-cpu</td>
    <td valign="top">@swisherrr: https://github.com/swisherrr</td>
    <td valign="top">@Malavya-Raval: https://github.com/Malavya-Raval</td>
  </tr>
  <tr>
    <td valign="top">@TedDBear: https://github.com/TedDBear</td>
    <td valign="top">@aniahb101: https://github.com/aniahb101</td>
    <td valign="top">@NisargKotak: https://github.com/NisargKotak</td>
  </tr>
  <tr>
    <td valign="top">@pratik-31: https://github.com/pratik-31</td>
    <td valign="top">@ivankitanovski: https://github.com/ivankitanovski</td>
    <td valign="top">@aliya-khalil21: https://github.com/aliya-khalil21</td>
  </tr>
  <tr>
    <td valign="top">@Shubham91999: https://github.com/Shubham91999</td>
    <td valign="top">@Kohink: https://github.com/Kohink</td>
    <td valign="top">@ajinkya-rasane: https://github.com/ajinkya-rasane</td>
  </tr>
  <tr>
    <td valign="top">@TLSZS0418: https://github.com/TLSZS0418</td>
    <td valign="top">@fan70m: https://github.com/fan70m</td>
    <td valign="top">@az-rye: https://github.com/az-rye</td>
  </tr>
  <tr>
    <td valign="top">@akshay-SE-Maldev: https://github.com/akshay-SE-Maldev</td>
    <td valign="top">@Mickey9315: https://github.com/Mickey9315</td>
    <td valign="top">@juiceomilk: https://github.com/juiceomilk</td>
  </tr>
  <tr>
    <td valign="top">@madhavramini: https://github.com/madhavramini</td>
    <td valign="top">@AviralYO: https://github.com/AviralYO</td>
    <td valign="top">@devanshi-ptk: https://github.com/devanshi-ptk</td>
  </tr>
  <tr>
    <td valign="top">@srimur: https://github.com/srimur</td>
    <td valign="top">@shivamkhare95: https://github.com/shivamkhare95</td>
    <td valign="top">@Mgiri1234: https://github.com/Mgiri1234</td>
  </tr>
  <tr>
    <td valign="top">@shreyyyansh: https://github.com/shreyyyansh</td>
    <td valign="top">@Kreed22: https://github.com/Kreed22</td>
    <td valign="top">@nidhikhatri18: https://github.com/nidhikhatri18</td>
  </tr>
  <tr>
    <td valign="top">@divyaprakash0426: https://github.com/divyaprakash0426</td>
    <td valign="top">@himangi05: https://github.com/himangi05</td>
    <td valign="top">@carynn101: https://github.com/carynn101</td>
  </tr>
  <tr>
    <td valign="top">@TeamBuilderApp: https://github.com/TeamBuilderApp</td>
    <td valign="top">@NainAbdi: https://github.com/NainAbdi</td>
    <td valign="top">@Nishkarsh1606: https://github.com/Nishkarsh1606</td>
  </tr>
  <tr>
    <td valign="top">@bendemonium: https://github.com/bendemonium</td>
    <td valign="top">@tonyshi1111: https://github.com/tonyshi1111</td>
    <td valign="top">@Naranja-Sagged: https://github.com/Naranja-Sagged</td>
  </tr>
  <tr>
    <td valign="top">@Jairo-Morelli: https://github.com/Jairo-Morelli</td>
    <td valign="top">@Mickey105: https://github.com/Mickey105</td>
    <td valign="top">@alfsiezar: https://github.com/alfsiezar</td>
  </tr>
  <tr>
    <td valign="top">@abdulrehan1729: https://github.com/abdulrehan1729</td>
    <td valign="top">@ISubomi: https://github.com/ISubomi</td>
    <td valign="top">@BhavanaPolakala: https://github.com/BhavanaPolakala</td>
  </tr>
  <tr>
    <td valign="top">@jack-makers: https://github.com/jack-makers</td>
    <td valign="top">@pavansurya09: https://github.com/pavansurya09</td>
    <td valign="top">@PrithhviSunil: https://github.com/PrithhviSunil</td>
  </tr>
  <tr>
    <td valign="top">@shriakhilc: https://github.com/shriakhilc</td>
    <td valign="top">@Ankith1999: https://github.com/Ankith1999</td>
    <td valign="top">@Emenlentino: https://github.com/Emenlentino</td>
  </tr>
  <tr>
    <td valign="top">@zaynnqureshi17: https://github.com/zaynnqureshi17</td>
    <td valign="top">@Ashish-3000: https://github.com/Ashish-3000</td>
    <td valign="top">@wavegate: https://github.com/wavegate</td>
  </tr>
  <tr>
    <td valign="top">@richexplorer: https://github.com/richexplorer</td>
    <td valign="top">@keeansarani: https://github.com/keeansarani</td>
    <td valign="top">@Mustafaahmed00: https://github.com/Mustafaahmed00</td>
  </tr>
  <tr>
    <td valign="top">@almzayyen: https://github.com/almzayyen</td>
    <td valign="top">@derickmr: https://github.com/derickmr</td>
    <td valign="top">@gastondana627: https://github.com/gastondana627</td>
  </tr>
</table>


