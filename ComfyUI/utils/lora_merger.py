#!/usr/bin/env python3
"""
LoRA Merger Utility for ComfyUI

This module provides LoRA merging functionality using ComfyUI's existing LoRA infrastructure.
It can be used as a standalone utility or imported by other tools.
"""

import logging
import torch
from typing import Dict

import comfy.utils
import comfy.lora

logger = logging.getLogger(__name__)

# Import shared utilities (if available)
try:
    from dream_layer_backend.dream_layer_backend_utils.shared_lora_utils import (
        validate_safetensors_file,
        load_safetensors_file,
        save_safetensors_file,
        create_lora_key_mapping,
        apply_lora_patches
    )
except ImportError:
    # Fallback to local implementations if shared utils not available
    import os

    def validate_safetensors_file(file_path: str) -> bool:
        """Validate that a file exists and is a valid .safetensors file."""
        if not os.path.exists(file_path):
            logger.error(f"File does not exist: {file_path}")
            return False

        if not file_path.endswith('.safetensors'):
            logger.error(f"File is not a .safetensors file: {file_path}")
            return False

        try:
            stat = os.stat(file_path)
            if stat.st_size == 0:
                logger.error(f"File is empty: {file_path}")
                return False
            return True
        except OSError as e:
            logger.error(f"Error reading file {file_path}: {e}")
            return False

    def load_safetensors_file(file_path: str) -> Dict[str, torch.Tensor]:
        """Load a .safetensors file using ComfyUI's utilities."""
        try:
            state_dict = comfy.utils.load_torch_file(file_path, safe_load=True)
            logger.info(f"Successfully loaded {file_path} with {len(state_dict)} keys")
            return state_dict
        except Exception as e:
            logger.error(f"Error loading {file_path}: {e}")
            raise

    def save_safetensors_file(state_dict: Dict[str, torch.Tensor], output_path: str) -> None:
        """Save a state dict to a .safetensors file using ComfyUI's utilities."""
        try:
            dir_path = os.path.dirname(output_path)
            if dir_path:
                os.makedirs(dir_path, exist_ok=True)
            comfy.utils.save_torch_file(state_dict, output_path, metadata={})
            logger.info(f"Successfully saved merged model to {output_path}")
        except Exception as e:
            logger.error(f"Error saving {output_path}: {e}")
            raise

    def create_lora_key_mapping(base_state_dict: Dict[str, torch.Tensor], lora_state_dict: Dict[str, torch.Tensor]) -> Dict[str, str]:
        """Create a key mapping between base model and LoRA keys."""
        key_map = {}
        for key in base_state_dict.keys():
            if key.startswith("model.diffusion_model."):
                lora_key = key.replace("model.diffusion_model.", "").replace(".", "_")
                lora_key = f"lora_unet_{lora_key}"
                if lora_key in lora_state_dict:
                    key_map[lora_key] = key
        return key_map

    def apply_lora_patches(base_state_dict: Dict[str, torch.Tensor], loaded_patches: Dict, strength_model: float = 1.0) -> Dict[str, torch.Tensor]:
        """Apply LoRA patches to the base state dict."""
        merged_state_dict = base_state_dict.copy()
        for key, patch_info in loaded_patches.items():
            if key in merged_state_dict:
                patch_type = patch_info[0]
                patch_data = patch_info[1]
                if patch_type == "diff":
                    diff = patch_data[0]
                    if diff.shape == merged_state_dict[key].shape:
                        merged_state_dict[key] = merged_state_dict[key] + (diff * strength_model)
                    else:
                        logger.warning(f"Shape mismatch for key {key}: {diff.shape} vs {merged_state_dict[key].shape}")
                elif patch_type == "set":
                    merged_state_dict[key] = patch_data[0] * strength_model
        return merged_state_dict


def merge_lora_using_comfyui(
    base_path: str,
    lora_path: str,
    output_path: str,
    strength_model: float = 1.0,
    strength_clip: float = 1.0
) -> bool:
    """
    Merge LoRA weights with a base model using ComfyUI's LoRA infrastructure.

    Args:
        base_path: Path to the base model .safetensors file
        lora_path: Path to the LoRA .safetensors file
        output_path: Path where to save the merged model
        strength_model: Strength for model weights (default: 1.0)
        strength_clip: Strength for CLIP weights (default: 1.0)

    Returns:
        bool: True if merge was successful, False otherwise
    """
    try:
        # Validate input files using shared utilities
        if not validate_safetensors_file(base_path):
            return False
        if not validate_safetensors_file(lora_path):
            return False

        logger.info("Starting LoRA merge using ComfyUI infrastructure:")
        logger.info(f"  Base model: {base_path}")
        logger.info(f"  LoRA model: {lora_path}")
        logger.info(f"  Output: {output_path}")
        logger.info(f"  Model strength: {strength_model}")
        logger.info(f"  CLIP strength: {strength_clip}")

        # Load state dicts using shared utilities
        base_state_dict = load_safetensors_file(base_path)
        lora_state_dict = load_safetensors_file(lora_path)

        # Create key mapping using shared utilities
        key_map = create_lora_key_mapping(base_state_dict, lora_state_dict)

        # Use ComfyUI's LoRA loading logic
        loaded_patches = comfy.lora.load_lora(lora_state_dict, key_map)

        # Apply patches using shared utilities
        merged_state_dict = apply_lora_patches(base_state_dict, loaded_patches, strength_model)

        # Save the merged model using shared utilities
        save_safetensors_file(merged_state_dict, output_path)

        logger.info("LoRA merge completed successfully using ComfyUI infrastructure!")
        return True

    except Exception as e:
        logger.error(f"Error during LoRA merge: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
