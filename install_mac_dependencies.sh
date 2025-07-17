#!/bin/bash

# Dream Layer macOS Dependencies Installation Script
# This script installs all the necessary dependencies for running Dream Layer on macOS

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

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

# Function to check macOS version
check_macos_version() {
    local version=$(sw_vers -productVersion)
    local major_version=$(echo "$version" | cut -d. -f1)
    local minor_version=$(echo "$version" | cut -d. -f2)
    
    print_status "Detected macOS version: $version"
    
    # Check if macOS is 10.15 or newer (required for most modern dependencies)
    if [ "$major_version" -lt 10 ] || ([ "$major_version" -eq 10 ] && [ "$minor_version" -lt 15 ]); then
        print_warning "macOS 10.15 (Catalina) or newer is recommended for best compatibility"
    else
        print_success "macOS version is compatible"
    fi
}

# Function to install Homebrew
install_homebrew() {
    if command_exists brew; then
        print_success "Homebrew is already installed"
        # Update Homebrew
        print_step "Updating Homebrew..."
        brew update
    else
        print_step "Installing Homebrew..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        
        # Add Homebrew to PATH for Apple Silicon Macs
        if [[ $(uname -m) == "arm64" ]]; then
            echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
            eval "$(/opt/homebrew/bin/brew shellenv)"
        fi
        
        print_success "Homebrew installed successfully"
    fi
}

# Function to install Python
install_python() {
    if command_exists python3; then
        local python_version=$(python3 --version | cut -d' ' -f2)
        print_status "Python is already installed: $python_version"
        
        # Check if version is 3.8 or newer
        local major=$(echo "$python_version" | cut -d. -f1)
        local minor=$(echo "$python_version" | cut -d. -f2)
        
        if [ "$major" -eq 3 ] && [ "$minor" -ge 8 ]; then
            print_success "Python version is compatible (3.8+)"
        else
            print_warning "Python 3.8+ is recommended. Installing latest Python..."
            brew install python@3.11
        fi
    else
        print_step "Installing Python..."
        brew install python@3.11
        print_success "Python installed successfully"
    fi
    
    # Ensure pip is available
    if ! command_exists pip3; then
        print_step "Installing pip..."
        python3 -m ensurepip --upgrade
    fi
    
    # Upgrade pip
    print_step "Upgrading pip..."
    python3 -m pip install --upgrade pip
}

# Function to install Node.js
install_nodejs() {
    if command_exists node; then
        local node_version=$(node --version)
        print_status "Node.js is already installed: $node_version"
        
        # Check if version is 16 or newer
        local version_number=$(echo "$node_version" | sed 's/v//' | cut -d. -f1)
        if [ "$version_number" -ge 16 ]; then
            print_success "Node.js version is compatible (16+)"
        else
            print_warning "Node.js 16+ is recommended. Installing latest Node.js..."
            brew install node
        fi
    else
        print_step "Installing Node.js..."
        brew install node
        print_success "Node.js installed successfully"
    fi
    
    # Ensure npm is available and up to date
    if command_exists npm; then
        print_step "Updating npm..."
        npm install -g npm@latest
    fi
}

# Function to install system dependencies
install_system_dependencies() {
    print_step "Installing system dependencies..."
    
    # Essential tools for development
    local packages=(
        "git"           # Version control
        "wget"          # Download utility
        "curl"          # Transfer utility
        "ffmpeg"        # Video/audio processing (useful for AI/media projects)
        "imagemagick"   # Image processing
        "pkg-config"    # Package configuration
        "libjpeg"       # JPEG library
        "libpng"        # PNG library
        "freetype"      # Font rendering
        "lsof"          # Process monitoring (used in startup script)
    )
    
    for package in "${packages[@]}"; do
        if brew list "$package" &>/dev/null; then
            print_status "$package is already installed"
        else
            print_step "Installing $package..."
            brew install "$package"
        fi
    done
    
    print_success "System dependencies installed"
}

# Function to install Python dependencies
install_python_dependencies() {
    print_step "Installing Python dependencies..."
    
    # Get the directory where this script is located
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    cd "$SCRIPT_DIR"
    
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
        print_success "ComfyUI dependencies installed"
    else
        print_warning "ComfyUI/requirements.txt not found"
    fi
    
    # Install additional ML/AI dependencies that might be needed
    print_step "Installing additional ML/AI dependencies..."
    python3 -m pip install --upgrade torch torchvision torchaudio
}

# Function to install frontend dependencies
install_frontend_dependencies() {
    print_step "Installing frontend dependencies..."
    
    # Get the directory where this script is located
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
    if [ ! -f ".env" ]; then
        print_step "Creating .env template..."
        cat > .env << EOF
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
        print_warning "Please update .env with your actual configuration"
    fi
    
    print_success "Environment setup completed"
}

# Function to run post-installation tests
run_tests() {
    print_step "Running post-installation tests..."
    
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
}

# Function to display final instructions
display_final_instructions() {
    print_header "INSTALLATION COMPLETE!"
    
    echo -e "${GREEN}✅ All dependencies have been installed successfully!${NC}\n"
    
    echo -e "${CYAN}Next steps:${NC}"
    echo -e "1. ${YELLOW}Configure your environment:${NC}"
    echo -e "   • Edit ${BLUE}.env${NC} with your API keys and preferences"
    echo -e ""
    echo -e "2. ${YELLOW}Start the application:${NC}"
    echo -e "   • Run: ${BLUE}./start_dream_layer.sh${NC}"
    echo -e ""
    echo -e "3. ${YELLOW}Access the application:${NC}"
    echo -e "   • Frontend: ${BLUE}http://localhost:8080${NC}"
    echo -e "   • Main API: ${BLUE}http://localhost:5002${NC}"
    echo -e "   • ComfyUI: ${BLUE}http://localhost:8188${NC}"
    echo -e ""
    echo -e "${CYAN}Troubleshooting:${NC}"
    echo -e "• Check logs in the ${BLUE}logs/${NC} directory"
    echo -e "• Ensure all ports (8080, 5001-5004, 8188) are available"
    echo -e "• Update Python packages: ${BLUE}python3 -m pip install --upgrade -r requirements.txt${NC}"
    echo -e "• Update Node packages: ${BLUE}cd dream_layer_frontend && npm update${NC}"
    echo -e ""
    echo -e "${GREEN}Happy creating with Dream Layer! 🎨✨${NC}"
}

# Main installation function
main() {
    print_header "DREAM LAYER macOS INSTALLATION"
    
    echo -e "${CYAN}This script will install all dependencies required for Dream Layer:${NC}"
    echo -e "• Homebrew (package manager)"
    echo -e "• Python 3.8+ and pip"
    echo -e "• Node.js 16+ and npm"
    echo -e "• System libraries (ffmpeg, imagemagick, etc.)"
    echo -e "• Python packages (Flask, PyTorch, ComfyUI dependencies)"
    echo -e "• Node.js packages (React, TypeScript, Vite)"
    echo -e ""
    
    read -p "Do you want to continue? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_status "Installation cancelled"
        exit 0
    fi
    
    # Check macOS version
    print_header "SYSTEM CHECK"
    check_macos_version
    
    # Install Homebrew
    print_header "HOMEBREW INSTALLATION"
    install_homebrew
    
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