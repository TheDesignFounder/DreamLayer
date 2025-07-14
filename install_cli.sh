#!/bin/bash

# DreamLayer CLI Installation Script
# This script installs the DreamLayer CLI with proper packaging

set -e

echo "🚀 Installing DreamLayer CLI with proper packaging..."

# Check if we're in the right directory
if [ ! -f "setup.py" ]; then
    echo "❌ Error: setup.py not found. Please run this script from the project root."
    exit 1
fi

# Check if ComfyUI exists
if [ ! -d "ComfyUI" ]; then
    echo "❌ Error: ComfyUI directory not found. Please ensure ComfyUI is in the project root."
    exit 1
fi

# Install ComfyUI first (as a local package)
echo "📦 Installing ComfyUI as local package..."
cd ComfyUI
pip install -e .
cd ..

# Install DreamLayer CLI
echo "📦 Installing DreamLayer CLI..."
pip install -e .

echo "✅ Installation complete!"
echo ""
echo "You can now use the CLI with:"
echo "  dreamlayer --help"
echo "  dreamlayer merge-lora --help"
echo ""
echo "Note: The CLI now uses proper packaging - no sys.path hacks needed!"
