#!/usr/bin/env python3
"""
Create test tensor files for LoRA merger testing

This script creates dummy .safetensors files that can be used to test the LoRA merger CLI.
"""

import os
import torch
import tempfile
from pathlib import Path
import safetensors.torch

def create_dummy_safetensors_file(file_path: str, num_tensors: int = 10, tensor_size: int = 64):
    """
    Create a dummy safetensors file with random tensors.

    Args:
        file_path: Path where to save the file
        num_tensors: Number of tensors to create
        tensor_size: Size of each tensor (will be tensor_size x tensor_size)
    """
    # Create state dict with dummy tensors
    state_dict = {}

    # Create tensors with different names that might be found in real models
    tensor_names = [
        "model.diffusion_model.input_blocks.0.0.weight",
        "model.diffusion_model.input_blocks.0.0.bias",
        "model.diffusion_model.input_blocks.1.0.weight",
        "model.diffusion_model.input_blocks.1.0.bias",
        "model.diffusion_model.middle_block.0.weight",
        "model.diffusion_model.middle_block.0.bias",
        "model.diffusion_model.output_blocks.0.0.weight",
        "model.diffusion_model.output_blocks.0.0.bias",
        "model.diffusion_model.output_blocks.1.0.weight",
        "model.diffusion_model.output_blocks.1.0.bias"
    ]

    for i in range(min(num_tensors, len(tensor_names))):
        # Create random tensor
        tensor = torch.randn(tensor_size, tensor_size)
        state_dict[tensor_names[i]] = tensor

    # Ensure output directory exists (only if there's a directory path)
    dir_path = os.path.dirname(file_path)
    if dir_path:
        os.makedirs(dir_path, exist_ok=True)

    # Save as safetensors
    safetensors.torch.save_file(state_dict, file_path)
    print(f"✅ Created test file: {file_path} ({len(state_dict)} tensors)")

def create_dummy_lora_file(file_path: str, num_tensors: int = 8, tensor_size: int = 64):
    """
    Create a dummy LoRA safetensors file with LoRA-style tensors.

    Args:
        file_path: Path where to save the file
        num_tensors: Number of tensors to create
        tensor_size: Size of each tensor
    """
    # Create state dict with LoRA-style tensors
    state_dict = {}

    # LoRA tensors typically have specific naming patterns
    lora_names = [
        "lora_unet_input_blocks_0_0_weight",
        "lora_unet_input_blocks_0_0_weight",
        "lora_unet_input_blocks_1_0_weight",
        "lora_unet_input_blocks_1_0_weight",
        "lora_unet_middle_block_0_weight",
        "lora_unet_middle_block_0_weight",
        "lora_unet_output_blocks_0_0_weight",
        "lora_unet_output_blocks_0_0_weight"
    ]

    for i in range(min(num_tensors, len(lora_names))):
        # Create random LoRA tensor (smaller than base model tensors)
        tensor = torch.randn(tensor_size // 2, tensor_size // 2) * 0.1  # Smaller scale for LoRA
        state_dict[lora_names[i]] = tensor

    # Ensure output directory exists (only if there's a directory path)
    dir_path = os.path.dirname(file_path)
    if dir_path:
        os.makedirs(dir_path, exist_ok=True)

    # Save as safetensors
    safetensors.torch.save_file(state_dict, file_path)
    print(f"✅ Created LoRA test file: {file_path} ({len(state_dict)} tensors)")

def main():
    """Create test tensor files."""
    print("🧪 Creating test tensor files for LoRA merger testing...")

    # Create test files in current directory
    base_file = "test_base.safetensors"
    lora_file = "test_lora.safetensors"
    output_file = "test_merged.safetensors"

    # Create base model file
    create_dummy_safetensors_file(base_file, num_tensors=10, tensor_size=128)

    # Create LoRA file
    create_dummy_lora_file(lora_file, num_tensors=8, tensor_size=128)

    print(f"\n📁 Test files created:")
    print(f"   Base model: {base_file}")
    print(f"   LoRA model: {lora_file}")
    print(f"   Output file: {output_file}")

    print(f"\n🧪 You can now test the CLI with:")
    print(f"   python -m dream_layer_backend.cli merge-lora {base_file} {lora_file} {output_file}")

    # Check file sizes
    if os.path.exists(base_file):
        size = os.path.getsize(base_file)
        print(f"\n📊 File sizes:")
        print(f"   {base_file}: {size:,} bytes")

    if os.path.exists(lora_file):
        size = os.path.getsize(lora_file)
        print(f"   {lora_file}: {size:,} bytes")

if __name__ == "__main__":
    main()