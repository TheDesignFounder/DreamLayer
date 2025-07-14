"""
Shared LoRA Utilities

This module contains common utilities shared between ComfyUI utils and DreamLayer bridge
to avoid code duplication and ensure consistency.
"""

import os
import logging
from typing import Dict, Optional
import torch

logger = logging.getLogger(__name__)


def validate_safetensors_file(file_path: str) -> bool:
    """
    Validate that a file exists and is a valid .safetensors file.

    Args:
        file_path: Path to the file to validate

    Returns:
        bool: True if file is valid, False otherwise
    """
    if not os.path.exists(file_path):
        logger.error(f"File does not exist: {file_path}")
        return False

    if not file_path.endswith('.safetensors'):
        logger.error(f"File is not a .safetensors file: {file_path}")
        return False

    # Check if file is readable and has content
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
    """
    Load a .safetensors file using ComfyUI's utilities.

    Args:
        file_path: Path to the .safetensors file

    Returns:
        Dict[str, torch.Tensor]: State dict from the file
    """
    try:
        import comfy.utils
        state_dict = comfy.utils.load_torch_file(file_path, safe_load=True)
        logger.info(f"Successfully loaded {file_path} with {len(state_dict)} keys")
        return state_dict
    except ImportError as e:
        logger.error(f"ComfyUI not available: {e}")
        raise ImportError("ComfyUI is required for loading safetensors files") from e
    except Exception as e:
        logger.error(f"Error loading {file_path}: {e}")
        raise


def save_safetensors_file(state_dict: Dict[str, torch.Tensor], output_path: str) -> None:
    """
    Save a state dict to a .safetensors file using ComfyUI's utilities.

    Args:
        state_dict: State dict to save
        output_path: Path where to save the file
    """
    try:
        import comfy.utils

        # Ensure output directory exists (only if there's a directory path)
        dir_path = os.path.dirname(output_path)
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)

        # Save using ComfyUI's safe save
        comfy.utils.save_torch_file(state_dict, output_path, metadata={})
        logger.info(f"Successfully saved merged model to {output_path}")
    except ImportError as e:
        logger.error(f"ComfyUI not available: {e}")
        raise ImportError("ComfyUI is required for saving safetensors files") from e
    except Exception as e:
        logger.error(f"Error saving {output_path}: {e}")
        raise


def check_comfyui_availability() -> bool:
    """
    Check if ComfyUI is available and properly configured.

    Returns:
        bool: True if ComfyUI is available
    """
    try:
        import comfy.utils
        import comfy.lora
        return True
    except ImportError:
        return False


def get_comfyui_version() -> Optional[str]:
    """
    Get the ComfyUI version if available.

    Returns:
        Optional[str]: ComfyUI version string or None
    """
    try:
        import comfy.comfyui_version
        return getattr(comfy.comfyui_version, 'version', None)
    except (ImportError, AttributeError):
        return None


def create_lora_key_mapping(base_state_dict: Dict[str, torch.Tensor], lora_state_dict: Dict[str, torch.Tensor]) -> Dict[str, str]:
    """
    Create a key mapping between base model and LoRA keys.

    Args:
        base_state_dict: Base model state dict
        lora_state_dict: LoRA state dict

    Returns:
        Dict[str, str]: Mapping from LoRA keys to base model keys
    """
    key_map = {}
    for key in base_state_dict.keys():
        if key.startswith("model.diffusion_model."):
            # Map base model keys to LoRA keys
            lora_key = key.replace("model.diffusion_model.", "").replace(".", "_")
            lora_key = f"lora_unet_{lora_key}"
            if lora_key in lora_state_dict:
                key_map[lora_key] = key
    return key_map


def apply_lora_patches(
    base_state_dict: Dict[str, torch.Tensor],
    loaded_patches: Dict,
    strength_model: float = 1.0
) -> Dict[str, torch.Tensor]:
    """
    Apply LoRA patches to the base state dict.

    Args:
        base_state_dict: Base model state dict
        loaded_patches: Patches loaded from LoRA
        strength_model: Strength for model weights

    Returns:
        Dict[str, torch.Tensor]: Merged state dict
    """
    merged_state_dict = base_state_dict.copy()

    for key, patch_info in loaded_patches.items():
        if key in merged_state_dict:
            patch_type = patch_info[0]
            patch_data = patch_info[1]

            if patch_type == "diff":
                # Apply difference patch
                diff = patch_data[0]
                if diff.shape == merged_state_dict[key].shape:
                    merged_state_dict[key] = merged_state_dict[key] + (diff * strength_model)
                else:
                    logger.warning(f"Shape mismatch for key {key}: {diff.shape} vs {merged_state_dict[key].shape}")
            elif patch_type == "set":
                # Set the weight directly
                merged_state_dict[key] = patch_data[0] * strength_model

    return merged_state_dict