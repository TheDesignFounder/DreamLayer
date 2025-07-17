#!/usr/bin/env python3
"""
PNG Info metadata parser for DreamLayer AI.
Extracts generation parameters from PNG files created by Stable Diffusion.
"""

import json
import os
from typing import Dict, Optional, Any
from PIL import Image, PngImagePlugin


def parse_png_metadata(file_path: str) -> Optional[Dict[str, Any]]:
    """
    Parse PNG metadata and extract generation parameters.
    
    Args:
        file_path: Path to the PNG file
        
    Returns:
        Dictionary containing parsed metadata, or None if parsing fails
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        IOError: If the file cannot be read or is not a valid PNG
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"PNG file not found: {file_path}")
    
    try:
        # FIXED: Properly handle PNG metadata extraction for all image modes
        with Image.open(file_path) as img:
            # Check if it's a PNG
            if img.format != "PNG":
                raise ValueError(f"File is not a PNG: {file_path}")
            
            # FIXED: Extract text chunks regardless of image mode
            # The image mode (RGB, RGBA, etc.) doesn't affect text chunk extraction
            # Text chunks are stored separately from image data in PNG files
            
            if hasattr(img, 'text') and img.text:
                # Return the text chunks as a dictionary
                # This works for all image modes: RGB, RGBA, L, LA, P, etc.
                return dict(img.text)
            
            return None
            
    except Exception as e:
        raise IOError(f"Failed to parse PNG metadata: {str(e)}") from e

def extract_generation_parameters(metadata: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Extract and parse generation parameters from PNG metadata.
    
    Args:
        metadata: Raw metadata dictionary from PNG
        
    Returns:
        Dictionary containing parsed generation parameters, or None if parsing fails
    """
    if not metadata:
        return None
    
    try:
        # Try to extract parameters from the 'parameters' key
        if 'parameters' in metadata:
            params_str = metadata['parameters']
            if isinstance(params_str, str):
                return json.loads(params_str)
            return params_str
        
        # If no 'parameters' key, try to construct from individual keys
        params = {}
        
        # Standard ComfyUI/A1111 parameter keys
        param_keys = [
            'steps', 'sampler_name', 'cfg_scale', 'width', 'height', 
            'seed', 'model_name', 'model_hash', 'scheduler', 'clip_skip'
        ]
        
        for key in param_keys:
            if key in metadata:
                value = metadata[key]
                # Try to convert numeric strings to numbers
                if isinstance(value, str) and value.replace('.', '').replace('-', '').isdigit():
                    params[key] = float(value) if '.' in value else int(value)
                else:
                    params[key] = value
        
        return params or None
        
    except (json.JSONDecodeError, ValueError) as e:
        print(f"Warning: Failed to parse generation parameters: {e}")
        return None


def get_prompt_from_metadata(metadata: Dict[str, Any]) -> Optional[str]:
    """
    Extract the positive prompt from metadata.
    
    Args:
        metadata: Metadata dictionary from PNG
        
    Returns:
        Positive prompt string, or None if not found
    """
    if not metadata:
        return None
    
    # Check various possible keys for prompt
    prompt_keys = ['prompt', 'positive_prompt', 'text', 'description']
    
    for key in prompt_keys:
        if key in metadata and metadata[key]:
            return str(metadata[key])
    
    return None


def get_negative_prompt_from_metadata(metadata: Dict[str, Any]) -> Optional[str]:
    """
    Extract the negative prompt from metadata.
    
    Args:
        metadata: Metadata dictionary from PNG
        
    Returns:
        Negative prompt string, or None if not found
    """
    if not metadata:
        return None
    
    # Check various possible keys for negative prompt
    negative_keys = ['negative_prompt', 'negative', 'uc', 'unconditional']
    
    for key in negative_keys:
        if key in metadata and metadata[key]:
            return str(metadata[key])
    
    return None


def format_generation_info(metadata: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format metadata into a structured generation info dictionary.
    
    Args:
        metadata: Raw metadata from PNG
        
    Returns:
        Formatted generation info dictionary
    """
    if not metadata:
        return {}
    
    info = {
        'prompt': get_prompt_from_metadata(metadata),
        'negative_prompt': get_negative_prompt_from_metadata(metadata),
        'parameters': extract_generation_parameters(metadata),
        'raw_metadata': metadata
    }
    
    return info


def validate_png_file(file_path: str) -> bool:
    """
    Validate that a file is a valid PNG.
    
    Args:
        file_path: Path to the file to validate
        
    Returns:
        True if the file is a valid PNG, False otherwise
    """
    try:
        with Image.open(file_path) as img:
            return img.format == "PNG"
    except Exception:
        return False


# For testing purposes - create a sample PNG with metadata
def create_sample_png_with_metadata(output_path: str, has_alpha: bool = False, include_metadata: bool = True):
    """
    Create a sample PNG file with metadata for testing.
    
    Args:
        output_path: Path where to save the PNG
        has_alpha: Whether to include alpha channel
        include_metadata: Whether to include generation metadata
    """
    # Create image
    mode = "RGBA" if has_alpha else "RGB"
    size = (512, 512)
    
    if has_alpha:
        img = Image.new(mode, size, (255, 100, 100, 200))  # Semi-transparent red
    else:
        img = Image.new(mode, size, (255, 100, 100))  # Solid red
    
    # Add metadata if requested
    if include_metadata:
        metadata = PngImagePlugin.PngInfo()
        
        # Add sample generation parameters
        metadata.add_text("prompt", "beautiful landscape, highly detailed, 8k")
        metadata.add_text("negative_prompt", "blurry, low quality, deformed")
        metadata.add_text("parameters", json.dumps({
            "steps": 20,
            "sampler_name": "euler",
            "cfg_scale": 7.0,
            "width": 512,
            "height": 512,
            "seed": 12345,
            "model_name": "test_model.safetensors"
        }))
        
        img.save(output_path, "PNG", pnginfo=metadata)
    else:
        img.save(output_path, "PNG")


if __name__ == "__main__":
    # Test the functionality
    import tempfile
    import os
    
    # Create test files
    temp_dir = tempfile.mkdtemp()
    
    try:
        # Test RGB PNG
        rgb_path = os.path.join(temp_dir, "test_rgb.png")
        create_sample_png_with_metadata(rgb_path, has_alpha=False, include_metadata=True)
        
        print("Testing RGB PNG:")
        metadata = parse_png_metadata(rgb_path)
        print(f"Metadata: {metadata}")
        
        # Test RGBA PNG (this will fail due to the bug)
        rgba_path = os.path.join(temp_dir, "test_rgba.png")
        create_sample_png_with_metadata(rgba_path, has_alpha=True, include_metadata=True)
        
        print("\nTesting RGBA PNG (will fail due to bug):")
        metadata = parse_png_metadata(rgba_path)
        print(f"Metadata: {metadata}")
        
    finally:
        # Clean up
        import shutil
        shutil.rmtree(temp_dir)