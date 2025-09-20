#!/bin/bash

# Dream Layer Startup Script
# This script starts all the necessary services for the Dream Layer application

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

IS_CI="${CI:-false}"

# Function to print colored output
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

# Function to check if port is in use
check_port() {
    local port=$1
    if lsof -i:$port > /dev/null 2>&1; then
        return 0 # Port is in use
    else
        return 1 # Port is free
    fi
}

# Function to kill process using specific port
kill_port() {
    local port=$1
    print_warning "Killing process on port $port..."
    lsof -ti:$port | xargs kill -9 2>/dev/null || true
}

# Function to wait for port to be available
wait_for_port() {
    local port=$1
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if check_port $port; then
            print_success "Port $port is now available"
            return 0
        fi
        print_status "Waiting for port $port to be available... (attempt $attempt/$max_attempts)"
        sleep 1
        attempt=$((attempt + 1))
    done
    
    print_error "Port $port did not become available within $max_attempts seconds"
    return 1
}

# Function to start a Python server
start_python_server() {
    local server_name=$1
    local server_file=$2
    local port=$3
    local log_file="logs/${server_name}.log"
    local timeout=${4:-30}  # Default timeout of 30 seconds
    
    print_status "Starting $server_name on port $port..."
    
    # Create logs directory if it doesn't exist
    mkdir -p logs
    
    # Start the server in background
    cd dream_layer_backend
    python3 "$server_file" > "../$log_file" 2>&1 &
    local pid=$!
    cd ..
    
    # Store PID for cleanup
    echo $pid > "logs/${server_name}.pid"
    
    # Wait for server to start with increased timeout for dream_layer
    print_status "Waiting for $server_name to start (timeout: ${timeout}s)..."
    local attempt=1
    while [ $attempt -le $timeout ]; do
        if check_port $port; then
            print_success "$server_name started successfully (PID: $pid)"
            return 0
        fi
        sleep 1
        attempt=$((attempt + 1))
    done
    
    print_error "$server_name failed to start on port $port within ${timeout} seconds"
    print_status "Check the log file: $log_file"
    return 1
}

# Function to cleanup on exit
cleanup() {
    print_status "Cleaning up processes..."
    
    # Kill all background processes
    if [ -d "logs" ]; then
        for pid_file in logs/*.pid; do
            if [ -f "$pid_file" ]; then
                local pid=$(cat "$pid_file")
                if kill -0 $pid 2>/dev/null; then
                    print_status "Killing process $pid"
                    kill $pid 2>/dev/null || true
                fi
                rm -f "$pid_file"
            fi
        done
    fi
    
    # Kill processes on known ports
    kill_port 8188  # ComfyUI
    kill_port 5001  # txt2img server
    kill_port 5002  # Flask (dream_layer)
    kill_port 5003  # Extras server
    kill_port 5004  # img2img server
    kill_port 8080  # Vite dev server
    
    print_success "Cleanup completed"
}

# Set up trap to cleanup on script exit
trap cleanup EXIT INT TERM

# Main execution
main() {
    print_status "Starting Dream Layer services..."
    
    # Get the directory where this script is located
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    cd "$SCRIPT_DIR"
    
    if [[ "$(uname)" == "Linux" && -f "/tmp/dlvenv/bin/activate" ]]; then
        print_status "Activating Python virtual environment..."
        # shellcheck disable=SC1091
        source "/tmp/dlvenv/bin/activate"
    fi

    # Check if Python is available
    if ! command -v python3 &> /dev/null; then
        print_error "Python3 is not installed or not in PATH"
        exit 1
    fi
    
    # Check if Node.js is available
    if ! command -v node &> /dev/null; then
        print_error "Node.js is not installed or not in PATH"
        exit 1
    fi
    
    # Check if npm is available
    if ! command -v npm &> /dev/null; then
        print_error "npm is not installed or not in PATH"
        exit 1
    fi
    
    # Delete settings.json if it exists to prevent ComfyUI path interference
    if [ -f "dream_layer_backend/settings.json" ]; then
        print_warning "Removing existing settings.json to prevent ComfyUI path interference..."
        rm -f "dream_layer_backend/settings.json"
        print_success "settings.json removed"
    fi
    
    # Clean up served_images directory
    [ -d "dream_layer_backend/served_images" ] && rm -f dream_layer_backend/served_images/* && print_success "Cleaned up served_images directory"
    
    # Kill any existing processes on our ports
    print_status "Cleaning up existing processes..."
    kill_port 8188  # ComfyUI
    kill_port 5001  # txt2img server
    kill_port 5002  # Flask (dream_layer)
    kill_port 5003  # Extras server
    kill_port 5004  # img2img server
    kill_port 8080  # Vite dev server
    
    # Wait for ports to be freed
    sleep 2

    # Start Python servers
    print_status "Starting Python servers..."
    
    # Tell ComfyUI to use only CPU mode if we are in a container
    if [[ "$IS_CI" == "true" ]]; then
        export DREAMLAYER_COMFYUI_CPU_MODE=true
    fi

    # Start dream_layer.py (main server) - needs longer timeout as it starts ComfyUI first
    start_python_server "dream_layer" "dream_layer.py" 5002 120

    # Start txt2img_server.py
    start_python_server "txt2img_server" "txt2img_server.py" 5001
    
    # Start img2img_server.py
    start_python_server "img2img_server" "img2img_server.py" 5004
    
    # Start extras.py
    start_python_server "extras" "extras.py" 5003
    
    # Start frontend
    print_status "Starting frontend development server..."
    cd dream_layer_frontend
    
    # Check if node_modules exists, if not install dependencies
    if [ ! -d "node_modules" ]; then
        print_status "Installing frontend dependencies..."
        npm install
    fi
    
    # Start the development server
    npm run dev > "../logs/frontend.log" 2>&1 &
    local frontend_pid=$!
    cd ..
    
    # Store frontend PID
    echo $frontend_pid > "logs/frontend.pid"
    
    # Wait for frontend to start
    sleep 3
    
    if check_port 8080; then
        print_success "Frontend started successfully (PID: $frontend_pid)"
    else
        print_error "Frontend failed to start on port 8080"
        exit 1
    fi
    
    print_success "All Dream Layer services started successfully!"
    print_status "Services running:"
    print_status "  - Dream Layer (main): http://localhost:5002"
    print_status "  - txt2img server: http://localhost:5001"
    print_status "  - img2img server: http://localhost:5004"
    print_status "  - Extras server: http://localhost:5003"
    print_status "  - Frontend: http://localhost:8080"
    print_status "  - ComfyUI: http://localhost:8188"
    
    print_status "Log files are available in the 'logs' directory"
    print_status "Press Ctrl+C to stop all services"
    
    if [[ "$IS_CI" == "true" ]]; then
        print_success "CI mode: skipping wait, services launched"
        echo "[CI-SUCCESS] Dream Layer started successfully in CI mode"
    else
    # Keep the script running interactively
        wait
    fi
}

# Run main function
main "$@"
