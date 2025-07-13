#!/bin/bash
# Installation script for DreamLayer CLI

set -e

echo "🚀 Installing DreamLayer CLI..."

# Check if we're in the right directory
if [ ! -f "setup.py" ]; then
    echo "❌ Error: setup.py not found. Please run this script from the dream_layer_backend directory."
    exit 1
fi

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: Python 3 is required but not installed."
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Install the CLI in development mode
echo "🔧 Installing CLI..."
pip install -e .

echo "✅ DreamLayer CLI installed successfully!"
echo ""
echo "Usage examples:"
echo "  dreamlayer merge-lora base.safetensors lora.safetensors merged.safetensors"
echo "  dreamlayer merge-lora base.safetensors lora.safetensors merged.safetensors --scale 0.8"
echo "  dreamlayer test"
echo ""
echo "For help: dreamlayer --help"
