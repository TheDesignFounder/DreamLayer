# Installation Guide

Complete, OS-agnostic installation guide for DreamLayer AI with GPU/CPU setup instructions.

## 📋 System Requirements

### Minimum Requirements

- **OS:** Windows 10+, macOS 10.15+, or Linux (Ubuntu 18.04+)
- **Python:** 3.8 or higher
- **Node.js:** 16.0 or higher
- **RAM:** 8GB minimum (16GB recommended)
- **Storage:** 10GB free space

### Recommended Requirements

- **GPU:** NVIDIA RTX 3060+ (8GB+ VRAM) or Apple Silicon M1+
- **RAM:** 16GB or higher
- **Storage:** 50GB+ free space (for models)
- **Network:** Stable internet connection for model downloads

### GPU Support

- **NVIDIA:** CUDA 11.8+ with compatible drivers
- **Apple Silicon:** Native MPS acceleration
- **AMD:** ROCm support (experimental)
- **CPU:** Fallback mode (slower but functional)

## 🛠️ Pre-Installation Setup

### 1. Install Python

**Windows:**

```bash
# Download from python.org or use winget
winget install Python.Python.3.11
```

**macOS:**

```bash
# Using Homebrew
brew install python@3.11

# Or download from python.org
```

**Linux (Ubuntu/Debian):**

```bash
sudo apt update
sudo apt install python3.11 python3.11-pip python3.11-venv
```

### 2. Install Node.js

**Windows:**

```bash
# Download from nodejs.org or use winget
winget install OpenJS.NodeJS
```

**macOS:**

```bash
# Using Homebrew
brew install node

# Or download from nodejs.org
```

**Linux (Ubuntu/Debian):**

```bash
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs
```

### 3. Install Git

**Windows:**

```bash
# Download from git-scm.com or use winget
winget install Git.Git
```

**macOS:**

```bash
# Using Homebrew
brew install git

# Or download from git-scm.com
```

**Linux (Ubuntu/Debian):**

```bash
sudo apt install git
```

## 📦 Installation Methods

### Method 1: Automated Installation (Recommended)

#### macOS/Linux

```bash
# Clone the repository
git clone https://github.com/DreamLayer-AI/DreamLayer.git
cd DreamLayer

# Make scripts executable
chmod +x install_mac_dependencies.sh
chmod +x start_dream_layer.sh

# Run installation
./install_mac_dependencies.sh
```

#### Windows

```bash
# Clone the repository
git clone https://github.com/DreamLayer-AI/DreamLayer.git
cd DreamLayer

# Run installation
install_windows_dependencies.bat
```

### Method 2: Manual Installation

#### 1. Clone Repository

```bash
git clone https://github.com/DreamLayer-AI/DreamLayer.git
cd DreamLayer
```

#### 2. Install Python Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install Python packages
pip install -r requirements.txt
```

#### 3. Install Node.js Dependencies

```bash
cd dream_layer_frontend
npm install
cd ..
```

#### 4. Setup ComfyUI

```bash
# ComfyUI should be included in the repository
# If not, clone it manually:
git clone https://github.com/comfyanonymous/ComfyUI.git
```

## 🔧 Configuration

### 1. Environment Variables

Create a `.env` file in the root directory:

```bash
# API Keys (optional - for cloud models)
OPENAI_API_KEY=your_openai_api_key_here
IDEOGRAM_API_KEY=your_ideogram_api_key_here
BFL_API_KEY=your_bfl_api_key_here
STABILITY_API_KEY=your_stability_api_key_here

# Server Configuration
FLASK_PORT=5000
COMFYUI_PORT=8188
FRONTEND_PORT=8080
```

### 2. Directory Configuration

Set up your directories in the web interface:

1. **Start DreamLayer** (see [Quick Start](quick_start.md))
2. **Go to Settings** → **Paths**
3. **Configure directories:**
   - **Output Directory:** Where generated images are saved
   - **Models Directory:** Where your models are stored

### 3. Model Setup

#### Download Models

```bash
# Create models directory
mkdir -p models/checkpoints
mkdir -p models/loras
mkdir -p models/controlnet
mkdir -p models/upscalers

# Download Stable Diffusion models
# Example: SD 1.5
wget https://huggingface.co/runwayml/stable-diffusion-v1-5/resolve/main/v1-5-pruned.safetensors -O models/checkpoints/sd15.safetensors
```

#### Supported Model Formats

- **Checkpoints:** `.safetensors`, `.ckpt`
- **LoRA:** `.safetensors`, `.pt`
- **ControlNet:** `.safetensors`, `.pth`
- **Upscalers:** `.pth`, `.bin`

## 🚀 Starting DreamLayer

### Automated Start

**macOS/Linux:**

```bash
./start_dream_layer.sh
```

**Windows:**

```bash
start_dream_layer.bat
```

### Manual Start

#### 1. Start ComfyUI Server

```bash
cd ComfyUI
python main.py --listen 0.0.0.0 --port 8188
```

#### 2. Start Flask API Server

```bash
cd dream_layer_backend
python dream_layer.py
```

#### 3. Start Frontend Development Server

```bash
cd dream_layer_frontend
npm run dev
```

### Access DreamLayer

Open your browser and navigate to:

- **Frontend:** http://localhost:8080
- **API:** http://localhost:5000
- **ComfyUI:** http://localhost:8188

## 🔍 Verification

### Check Installation

1. **Verify Python packages:**

   ```bash
   python -c "import torch; print(f'PyTorch: {torch.__version__}')"
   python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')"
   ```

2. **Verify Node.js packages:**

   ```bash
   cd dream_layer_frontend
   npm list --depth=0
   ```

3. **Test API endpoints:**
   ```bash
   curl http://localhost:5000/api/models
   ```

### Performance Testing

1. **Generate a test image** using the web interface
2. **Check generation time** (should be <30 seconds on GPU)
3. **Verify output quality** and file saving

## 🚨 Troubleshooting

### Common Issues

#### Python Import Errors

```bash
# Reinstall packages
pip install --force-reinstall -r requirements.txt
```

#### CUDA Issues

```bash
# Check CUDA installation
nvidia-smi
python -c "import torch; print(torch.cuda.is_available())"

# Reinstall PyTorch with CUDA
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

#### Port Conflicts

```bash
# Check port usage
netstat -tulpn | grep :8080
netstat -tulpn | grep :5000
netstat -tulpn | grep :8188

# Kill processes using ports
kill -9 <PID>
```

#### Memory Issues

```bash
# Reduce batch size in settings
# Use CPU mode for testing
# Close other applications
```

### Getting Help

- **Documentation:** [Usage Guide](usage.md)
- **Issues:** [GitHub Issues](https://github.com/DreamLayer-AI/DreamLayer/issues)
- **Discussions:** [GitHub Discussions](https://github.com/DreamLayer-AI/DreamLayer/discussions)

## 🔄 Updates

### Updating DreamLayer

```bash
# Pull latest changes
git pull origin main

# Reinstall dependencies (if needed)
./install_mac_dependencies.sh  # or install_windows_dependencies.bat
```

### Updating Models

```bash
# Models are automatically detected on restart
# Or refresh in the web interface
```

---

_Need help? Check out the [Quick Start Guide](quick_start.md) for a faster setup._
