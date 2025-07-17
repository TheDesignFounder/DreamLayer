#!/usr/bin/env python3
"""
Create test tensor files for LoRA merger testing

This script creates dummy .safetensors files that can be used to test the LoRA merger CLI.
"""

import os
import torch
import safetensors.torch
import logging
import argparse


def create_dummy_safetensors_file(file_path: str, num_tensors: int = 10, tensor_size: int = 64, tensor_names=None):
    """
    Create a dummy safetensors file with random tensors.

    Args:
        file_path: Path where to save the file
        num_tensors: Number of tensors to create
        tensor_size: Size of each tensor (will be tensor_size x tensor_size)
        tensor_names: Optional list of tensor names to use
    """
    # Parameter validation
    if num_tensors <= 0:
        raise ValueError("num_tensors must be positive")
    if tensor_size <= 0:
        raise ValueError("tensor_size must be positive")
    if not file_path or not isinstance(file_path, str):
        raise ValueError("file_path must be a valid string")

    # Create state dict with dummy tensors
    state_dict = {}

    # Default tensor names
    default_tensor_names = [
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
    names = tensor_names if tensor_names is not None else default_tensor_names
    if num_tensors > len(names):
        raise ValueError(f"num_tensors ({num_tensors}) exceeds available tensor names ({len(names)})")

    for i in range(num_tensors):
        tensor = torch.randn(tensor_size, tensor_size)
        state_dict[names[i]] = tensor

    dir_path = os.path.dirname(file_path)
    if dir_path:
        os.makedirs(dir_path, exist_ok=True)

    safetensors.torch.save_file(state_dict, file_path)
    logging.info(f"✅ Created test file: {file_path} ({len(state_dict)} tensors)")


def create_dummy_lora_file(file_path: str, num_tensors: int = 8, tensor_size: int = 64, lora_names=None):
    """
    Create a dummy LoRA safetensors file with LoRA-style tensors.

    Args:
        file_path: Path where to save the file
        num_tensors: Number of tensors to create
        tensor_size: Size of each tensor
        lora_names: Optional list of LoRA tensor names to use
    """
    # Parameter validation
    if num_tensors <= 0:
        raise ValueError("num_tensors must be positive")
    if tensor_size <= 0:
        raise ValueError("tensor_size must be positive")
    if not file_path or not isinstance(file_path, str):
        raise ValueError("file_path must be a valid string")

    state_dict = {}

    default_lora_names = [
        "lora_unet_input_blocks_0_0_weight",
        "lora_unet_input_blocks_0_0_bias",
        "lora_unet_input_blocks_1_0_weight",
        "lora_unet_input_blocks_1_0_bias",
        "lora_unet_middle_block_0_weight",
        "lora_unet_middle_block_0_bias",
        "lora_unet_output_blocks_0_0_weight",
        "lora_unet_output_blocks_0_0_bias"
    ]
    names = lora_names if lora_names is not None else default_lora_names
    if num_tensors > len(names):
        raise ValueError(f"num_tensors ({num_tensors}) exceeds available LoRA tensor names ({len(names)})")

    for i in range(num_tensors):
        tensor = torch.randn(tensor_size // 2, tensor_size // 2) * 0.1
        state_dict[names[i]] = tensor

    dir_path = os.path.dirname(file_path)
    if dir_path:
        os.makedirs(dir_path, exist_ok=True)

    safetensors.torch.save_file(state_dict, file_path)
    logging.info(f"✅ Created LoRA test file: {file_path} ({len(state_dict)} tensors)")


def main():
    """Create test tensor files."""
    logging.basicConfig(level=logging.INFO)
    logging.info("🧪 Creating test tensor files for LoRA merger testing...")

    parser = argparse.ArgumentParser(description="Create dummy .safetensors files for LoRA merger testing.")
    parser.add_argument('--base-file', type=str, default="test_base.safetensors", help="Base model output file name")
    parser.add_argument('--lora-file', type=str, default="test_lora.safetensors", help="LoRA model output file name")
    parser.add_argument('--output-file', type=str, default="test_merged.safetensors", help="Merged output file name (not created by this script)")
    parser.add_argument('--num-base-tensors', type=int, default=10, help="Number of base model tensors (max 10 unless custom names)")
    parser.add_argument('--num-lora-tensors', type=int, default=8, help="Number of LoRA tensors (max 8 unless custom names)")
    parser.add_argument('--tensor-size', type=int, default=128, help="Size of each tensor (square)")
    parser.add_argument('--base-names', type=str, help="Comma-separated list of base tensor names")
    parser.add_argument('--lora-names', type=str, help="Comma-separated list of LoRA tensor names")
    args = parser.parse_args()

    base_names = args.base_names.split(',') if args.base_names else None
    lora_names = args.lora_names.split(',') if args.lora_names else None

    # Create base model file
    create_dummy_safetensors_file(args.base_file, num_tensors=args.num_base_tensors, tensor_size=args.tensor_size, tensor_names=base_names)

    # Create LoRA file
    create_dummy_lora_file(args.lora_file, num_tensors=args.num_lora_tensors, tensor_size=args.tensor_size, lora_names=lora_names)

    logging.info("\n📁 Test files created:")
    logging.info(f"   Base model: {args.base_file}")
    logging.info(f"   LoRA model: {args.lora_file}")
    logging.info(f"   Output file: {args.output_file}")

    logging.info("\n🧪 You can now test the CLI with:")
    logging.info(f"   dreamlayer merge-lora {args.base_file} {args.lora_file} {args.output_file}")

    # Check file sizes
    if os.path.exists(args.base_file):
        size = os.path.getsize(args.base_file)
        logging.info("\n📊 File sizes:")
        logging.info(f"   {args.base_file}: {size:,} bytes")

    if os.path.exists(args.lora_file):
        size = os.path.getsize(args.lora_file)
        logging.info(f"   {args.lora_file}: {size:,} bytes")

if __name__ == "__main__":
    main()
