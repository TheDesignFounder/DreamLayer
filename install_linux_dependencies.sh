#!/bin/bash

# Dream Layer linux Dependencies Installation Script
# This script installs all the necessary dependencies for running Dream Layer on linux

set -e  # Exit on any error

. /etc/os-release

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

IS_CI="${CI:-false}"
# Set venv path from environment variable or default
DLVENV_PATH="${DLVENV_PATH:-/tmp/dlvenv}"

# Function to print colored output
print_header() {
    echo -e "\n${PURPLE}================================${NC}"
    echo -e "${PURPLE}$1${NC}"
    echo -e "${PURPLE}================================${NC}\n"
}

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_step() {
    echo -e "${CYAN}[STEP]${NC} $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check linux version
check_linux_version() {
    local distro=$NAME
    local version=$VERSION_ID
    
    print_status "Detected linux distribution: $distro version: $version"
}

# Function to install Python
install_python() {
    # detect and choose pkg install command
    if command_exists apt-get; then
        PKG_INSTALL="sudo apt-get update && sudo apt-get install -y python3 python3-pip python3-venv"
        USE_APT=true
    elif command_exists dnf; then
        PKG_INSTALL="sudo dnf install -y python3 python3-pip"
    elif command_exists pacman; then
        PKG_INSTALL="sudo pacman -Syu --noconfirm python python-pip"
    else
        echo "❌ Unsupported distro or missing package manager." >&2
        return 1
    fi

    # Install Python + pip if missing
    if ! command_exists python3; then
        print_step "Installing Python and pip..."
        eval "$PKG_INSTALL"
        print_success "Installed Python and pip."
    else
        version=$(python3 --version 2>&1 | cut -d' ' -f2)
        print_status "Python is already installed: $version"
    fi

    # check version ≥ 3.8
    version=$(python3 --version 2>&1 | cut -d' ' -f2)
    major=${version%%.*}
    minor=$(echo "$version" | cut -d. -f2)
    if [[ "$major" -lt 3 || ( "$major" -eq 3 && "$minor" -lt 8 ) ]]; then
        print_warning "Python < 3.8 detected, but upgrading is distro-dependent."
        # optionally source a newer distro repo or compile manually
    else
        print_success "Python version is compatible (3.8+)"
    fi

    # Ensure pip is present using distro package if needed
    if ! command_exists pip3; then
        if [ "${USE_APT:-false}" = true ]; then
            print_step "Installing pip3 via apt..."
            sudo apt-get install -y python3-pip
        else
            print_step "Bootstrapping pip via ensurepip..."
            sudo python3 -m ensurepip --upgrade || true
        fi
    fi

    if [ "${USE_APT:-false}" = true ]; then
        print_step "Ensuring virtual environment support is installed..."
        sudo apt-get update

        # Try generic package first
        if ! dpkg -s python3-venv >/dev/null 2>&1; then
            print_step "Installing python3-venv..."
            sudo apt-get install -y python3-venv || {
                # Fallback: install version-specific package
                PYVER=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
                sudo apt-get install -y "python3.${PYVER}-venv"
            }
        fi
    fi

    # Create persistent venv (don't delete it!)
    if [ ! -d "$DLVENV_PATH" ]; then
        print_step "Creating virtual environment at $DLVENV_PATH..."
        python3 -m venv "$DLVENV_PATH"
    fi
    
    # shellcheck disable=SC1090
    source "$DLVENV_PATH/bin/activate"

    print_step "Upgrading pip, setuptools, wheel INSIDE venv..."
    pip install --upgrade pip setuptools wheel
    print_success "Inside venv pip is now: $(pip --version)"

    # Keep venv activated for subsequent installations
    print_success "✅ Virtual environment ready at $DLVENV_PATH"
}

# Function to install Node.js
install_nodejs() {
    print_step "Installing Node.js..."

    if command_exists node && command_exists npm; then
        print_status "Node.js is already installed: $(node -v), npm: $(npm -v)"
        return 0
    fi

    if command_exists apt-get; then
        curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
        sudo apt-get install -y nodejs npm
    elif command_exists dnf; then
        sudo dnf module enable -y nodejs:20 || true
        sudo dnf install -y nodejs npm
    elif command_exists pacman; then
        sudo pacman -Syu --noconfirm nodejs npm
    else
        print_error "Unsupported distro for Node.js installation"
        exit 1
    fi

   # Ensure 'node' points to 'nodejs' if needed
    if ! command -v node >/dev/null && command -v nodejs >/dev/null; then
        NODEJS_PATH="$(command -v nodejs)"
        TARGET_LINK="/usr/local/bin/node"

        if [ -w "$(dirname "$TARGET_LINK")" ]; then
            ln -s "$NODEJS_PATH" "$TARGET_LINK" 2>/dev/null || {
                echo "[ERROR] Failed to create symlink $TARGET_LINK → $NODEJS_PATH"
            }
        else
            echo "[WARNING] Cannot create symlink: no write permission to $(dirname "$TARGET_LINK")"
            echo "          Try running with elevated permissions or install 'node' manually."
        fi
    fi

    if ! command_exists node || ! command_exists npm; then
        print_error "Failed to install Node.js and npm"
        exit 1
    fi

    print_success "Installed Node.js: $(node -v), npm: $(npm -v)"
}

# Function to install system dependencies
install_system_dependencies() {
    set -e
    print_step "Installing system dependencies..."

    # Base package names (common across most distros)
    local base_pkgs=(
        "git"           # Version control
        "wget"          # Download utility
        "curl"          # Transfer utility
        "ffmpeg"        # Video/audio processing (useful for AI/media projects)
        "pkg-config"    # Package configuration
        "lsof"          # Process monitoring (used in startup script)
    )

    # Platform-specific library names
    declare -A lib_map
    if command_exists apt-get; then
        PM="apt"
        lib_map=(
            [libjpeg]=libjpeg-dev # JPEG library
            [libpng]=libpng-dev # PNG library
            [freetype]=libfreetype6-dev # Font rendering
            [imagemagick]=imagemagick # Image processing
        )
        INSTALL_CMD="sudo apt-get install -y"
        sudo apt-get update  # run once outside the loop
    elif command_exists dnf; then
        PM="dnf"
        lib_map=(
            [libjpeg]=libjpeg-devel # JPEG library
            [libpng]=libpng-devel # PNG library
            [freetype]=freetype-devel # Font rendering
            [imagemagick]=ImageMagick # Image processing
        )
        INSTALL_CMD="sudo dnf install -y"
    elif command_exists pacman; then
        PM="pacman"
        lib_map=(
            [libjpeg]=libjpeg-turbo # JPEG library
            [libpng]=libpng # PNG library
            [freetype]=freetype2 # Font rendering
            [imagemagick]=imagemagick # Image processing (lowercase for Arch)
        )
        INSTALL_CMD="sudo pacman -Syu --noconfirm"
    else
        echo "❌ Unsupported distro: no known package manager found." >&2
        return 1
    fi

    # Merge base packages with mapped libs
    local packages=("${base_pkgs[@]}")
    for key in libjpeg libpng freetype imagemagick; do
        packages+=("${lib_map[$key]}")
    done

    # Install all packages in one command for efficiency
    print_step "Installing packages via $PM: ${packages[*]}"
    $INSTALL_CMD "${packages[@]}"

    print_success "✅ All dependencies installed via $PM"
}

# Function to install Python dependencies
install_python_dependencies() {
    print_step "Installing Python dependencies..."
    
    # Get the directory where this script is located
    local SCRIPT_DIR
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    cd "$SCRIPT_DIR"

    # Ensure we're in the venv (should be activated from install_python)
    if [[ "$VIRTUAL_ENV" != "$DLVENV_PATH" ]]; then
        print_step "Activating virtual environment..."
        # shellcheck disable=SC1090
        source "$DLVENV_PATH/bin/activate"
    fi
    
    # Install backend dependencies
    if [ -f "dream_layer_backend/requirements.txt" ]; then
        print_step "Installing Dream Layer backend dependencies..."
        python3 -m pip install -r dream_layer_backend/requirements.txt
        print_success "Backend dependencies installed"
    else
        print_warning "dream_layer_backend/requirements.txt not found"
    fi
    
    # Install ComfyUI dependencies
    if [ -f "ComfyUI/requirements.txt" ]; then
        print_step "Installing ComfyUI dependencies..."
        python3 -m pip install -r ComfyUI/requirements.txt
        
        # Install missing dependency for custom nodes
        pip install lpips
        
        print_success "ComfyUI dependencies installed"
    else
        print_warning "ComfyUI/requirements.txt not found"
    fi
    
    # Install additional ML/AI dependencies that might be needed
    print_step "Installing additional ML/AI dependencies..."
    python3 -m pip install --upgrade torch torchvision torchaudio

    print_success "✅ Dependencies installed inside virtual environment: $DLVENV_PATH"
}

# Function to install frontend dependencies
install_frontend_dependencies() {
    print_step "Installing frontend dependencies..."
    
    # Get the directory where this script is located
    local SCRIPT_DIR
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    cd "$SCRIPT_DIR"
    
    if [ -d "dream_layer_frontend" ]; then
        cd dream_layer_frontend
        
        if [ -f "package.json" ]; then
            print_step "Installing Node.js dependencies..."
            npm install
            print_success "Frontend dependencies installed"
        else
            print_warning "package.json not found in dream_layer_frontend"
        fi
        
        cd ..
    else
        print_warning "dream_layer_frontend directory not found"
    fi
}

# Function to setup environment
setup_environment() {
    print_step "Setting up environment..."
    
    # Create necessary directories
    mkdir -p logs
    mkdir -p dream_layer_backend/input
    mkdir -p dream_layer_backend/served_images
    
    # Make startup script executable
    if [ -f "start_dream_layer.sh" ]; then
        chmod +x start_dream_layer.sh
        print_success "Made start_dream_layer.sh executable"
    fi
    
    # Create a simple .env template if it doesn't exist
    if [ ! -f "dream_layer_backend/.env" ]; then
        print_step "Creating .env template..."
        cat > dream_layer_backend/.env << EOF
# Dream Layer Environment Configuration
# Copy this file and update with your actual values

# API Keys (optional - for external services)
# OPENAI_API_KEY=your_openai_key_here
# ANTHROPIC_API_KEY=your_anthropic_key_here

# Server Configuration
FLASK_ENV=development
FLASK_DEBUG=true

# ComfyUI Configuration
COMFYUI_PATH=../ComfyUI
COMFYUI_HOST=127.0.0.1
COMFYUI_PORT=8188
EOF
        print_success "Created .env template"
        print_warning "Please update dream_layer_backend/.env with your actual configuration"
    fi
    
    print_success "Environment setup completed"
}

# Function to run post-installation tests
run_tests() {
    print_step "Running post-installation tests..."
    
    # Activate venv for tests
        if [[ "$VIRTUAL_ENV" != "$DLVENV_PATH" ]]; then
        # shellcheck disable=SC1090
        source "$DLVENV_PATH/bin/activate"
    fi
    
    # Test Python
    if python3 -c "import flask, PIL, requests; print('Python dependencies OK')" 2>/dev/null; then
        print_success "Python dependencies test passed"
    else
        print_error "Python dependencies test failed"
    fi
    
    # Test Node.js
    if node -e "console.log('Node.js test OK')" 2>/dev/null; then
        print_success "Node.js test passed"
    else
        print_error "Node.js test failed"
    fi
    
    # Test npm
    if npm --version >/dev/null 2>&1; then
        print_success "npm test passed"
    else
        print_error "npm test failed"
    fi
    
    if [[ "$IS_CI" == "true" ]]; then
        echo "[CI-SUCCESS] Linux dependencies installation completed successfully"
    fi
}

# Function to display final instructions
display_final_instructions() {
    if [[ "$IS_CI" == "true" ]]; then
        print_success "✅ Installation completed successfully (CI mode)"
        return
    fi

    print_header "INSTALLATION COMPLETE!"
    
    echo -e "${GREEN}✅ All dependencies have been installed successfully!${NC}\n"
    
    echo -e "${CYAN}Next steps:${NC}"
    echo -e "1. ${YELLOW}Configure your environment:${NC}"
    echo -e "   • Edit ${BLUE}dream_layer_backend/.env${NC} with your API keys and preferences"
    echo -e ""
    echo -e "2. ${YELLOW}Start the application:${NC}"
    echo -e "   • Run: ${BLUE}./start_dream_layer.sh${NC}"
    echo -e ""
    echo -e "3. ${YELLOW}Access the application:${NC}"
    echo -e "   • Frontend: ${BLUE}http://localhost:8080${NC}"
    echo -e "   • Main API: ${BLUE}http://localhost:5002${NC}"
    echo -e "   • ComfyUI: ${BLUE}http://localhost:8188${NC}"
    echo -e ""
    echo -e "${CYAN}Virtual Environment:${NC}"
    echo -e "• Activate with: ${BLUE}source ${DLVENV_PATH}/bin/activate${NC}"
    echo -e "• Deactivate with: ${BLUE}deactivate${NC}"
    echo -e ""
    echo -e "${CYAN}Troubleshooting:${NC}"
    echo -e "• Check logs in the ${BLUE}logs/${NC} directory"
    echo -e "• Ensure all ports (8080, 5001-5004, 8188) are available"
    echo -e "• Update Python packages: ${BLUE}source ${DLVENV_PATH}/bin/activate && pip install --upgrade -r requirements.txt${NC}"
    echo -e "• Update Node packages: ${BLUE}cd dream_layer_frontend && npm update${NC}"
    echo -e ""
    echo -e "${GREEN}Happy creating with Dream Layer! 🎨✨${NC}"
}

# Main installation function
main() {
    print_header "DREAM LAYER LINUX INSTALLATION"
    
    echo -e "${CYAN}This script will install all dependencies required for Dream Layer:${NC}"
    echo -e "• Python 3.8+ and pip"
    echo -e "• Node.js 16+ and npm"
    echo -e "• System libraries (ffmpeg, imagemagick, etc.)"
    echo -e "• Python packages (Flask, PyTorch, ComfyUI dependencies)"
    echo -e "• Node.js packages (React, TypeScript, Vite)"
    echo -e ""
    
    if [[ "$IS_CI" == "true" ]]; then
        print_status "Auto-approving installation (CI=$IS_CI)"
    elif [ -t 0 ]; then
        read -p 'Do you want to continue? (y/N): ' -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "Aborted."
            exit 1
        fi
    else
        echo "Non-interactive shell detected — auto-approving install."
    fi

    echo

    print_step "Beginning full installation..."

    # Check linux version
    print_header "SYSTEM CHECK"
    check_linux_version
    
    # Install Python
    print_header "PYTHON INSTALLATION"
    install_python
    
    # Install Node.js
    print_header "NODE.JS INSTALLATION"
    install_nodejs
    
    # Install system dependencies
    print_header "SYSTEM DEPENDENCIES"
    install_system_dependencies
    
    # Install Python dependencies
    print_header "PYTHON DEPENDENCIES"
    install_python_dependencies
    
    # Install frontend dependencies
    print_header "FRONTEND DEPENDENCIES"
    install_frontend_dependencies
    
    # Setup environment
    print_header "ENVIRONMENT SETUP"
    setup_environment
    
    # Run tests
    print_header "POST-INSTALLATION TESTS"
    run_tests
    
    # Display final instructions
    display_final_instructions
}

# Check if script is run directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
