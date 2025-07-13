"""
LoRA Merger Bridge

This module provides a bridge between DreamLayer's CLI interface and ComfyUI's LoRA merging functionality.
It allows DreamLayer to leverage ComfyUI's robust LoRA infrastructure while maintaining its own interface.
"""

import os
import sys
import logging
from typing import Optional, Tuple

# Add ComfyUI to path
current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
comfyui_dir = os.path.join(current_dir, "ComfyUI")
if comfyui_dir not in sys.path:
    sys.path.append(comfyui_dir)

logger = logging.getLogger(__name__)


def get_comfyui_lora_merger():
    """
    Import and return the ComfyUI LoRA merger module.

    Returns:
        Module: The ComfyUI lora_merger module
    """
    try:
        # Import the ComfyUI lora_merger utility
        import utils.lora_merger as comfyui_lora_merger
        return comfyui_lora_merger
    except ImportError as e:
        logger.error(f"Failed to import ComfyUI lora_merger: {e}")
        raise ImportError("ComfyUI lora_merger not found. Make sure ComfyUI is properly installed.")


def merge_lora_weights(
    base_path: str,
    lora_path: str,
    output_path: str,
    lora_scale: float = 1.0,
    alpha: float = 1.0
) -> bool:
    """
    Bridge function to merge LoRA weights using ComfyUI's infrastructure.

    Args:
        base_path: Path to the base model .safetensors file
        lora_path: Path to the LoRA .safetensors file
        output_path: Path where to save the merged model
        lora_scale: Scaling factor for LoRA weights (default: 1.0)
        alpha: Alpha parameter for LoRA merging (default: 1.0)

    Returns:
        bool: True if merge was successful, False otherwise
    """
    try:
        # Get the ComfyUI lora_merger module
        comfyui_lora_merger = get_comfyui_lora_merger()

        # Use ComfyUI's merge function
        success = comfyui_lora_merger.merge_lora_using_comfyui(
            base_path=base_path,
            lora_path=lora_path,
            output_path=output_path,
            strength_model=lora_scale,
            strength_clip=alpha
        )

        return success

    except Exception as e:
        logger.error(f"Error in LoRA merge bridge: {e}")
        return False


def validate_safetensors_file(file_path: str) -> bool:
    """
    Bridge function to validate safetensors files using ComfyUI's validation.

    Args:
        file_path: Path to the file to validate

    Returns:
        bool: True if file is valid, False otherwise
    """
    try:
        comfyui_lora_merger = get_comfyui_lora_merger()
        return comfyui_lora_merger.validate_safetensors_file(file_path)
    except Exception as e:
        logger.error(f"Error in validation bridge: {e}")
        return False


def check_comfyui_availability() -> bool:
    """
    Check if ComfyUI and its LoRA merger are available.

    Returns:
        bool: True if ComfyUI is available, False otherwise
    """
    try:
        get_comfyui_lora_merger()
        return True
    except ImportError:
        return False


def get_comfyui_version() -> Optional[str]:
    """
    Get the ComfyUI version if available.

    Returns:
        Optional[str]: ComfyUI version string or None if not available
    """
    try:
        import comfy.comfyui_version
        return comfy.comfyui_version.version
    except ImportError:
        return None
