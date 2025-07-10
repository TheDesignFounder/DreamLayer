"""
ControlNet Processor Utility

This module provides utilities to process ControlNet data from frontend requests
and inject them into ComfyUI workflows.
"""

import os
import base64
import logging
import time
from PIL import Image
import io
from typing import Dict, Any

logger = logging.getLogger(__name__)

def process_controlnet_images(controlnet_data: Dict[str, Any], comfy_input_dir: str) -> Dict[str, Any]:
    """
    Process ControlNet images from the frontend request and save them to ComfyUI input directory.
    
    Args:
        controlnet_data: ControlNet configuration from frontend
        comfy_input_dir: Path to ComfyUI input directory
    
    Returns:
        Dict: Updated ControlNet data with processed image paths
    """
    if not controlnet_data or not controlnet_data.get('enabled'):
        return controlnet_data
    
    processed_controlnet = controlnet_data.copy()
    units = processed_controlnet.get('units', [])
    
    for i, unit in enumerate(units):
        if unit.get('input_image') and unit.get('enabled'):
            try:
                # Process the ControlNet image
                image_path = process_controlnet_image(unit['input_image'], comfy_input_dir, f"controlnet_{i}")
                units[i]['input_image_path'] = image_path
                logger.info(f"Processed ControlNet image for unit {i}: {image_path}")
            except Exception as e:
                logger.error(f"Error processing ControlNet image for unit {i}: {str(e)}")
                # Disable the unit if image processing fails
                units[i]['enabled'] = False
    
    return processed_controlnet

def process_controlnet_image(image_data: Any, comfy_input_dir: str, prefix: str) -> str:
    """
    Process a single ControlNet image and save it to the ComfyUI input directory.
    
    Args:
        image_data: Image data (could be File object, base64 string, or data URL)
        comfy_input_dir: Path to ComfyUI input directory
        prefix: Prefix for the filename
    
    Returns:
        str: Filename of the saved image
    """
    try:
        # Handle different image data formats
        if hasattr(image_data, 'read'):  # File object
            image_bytes = image_data.read()
            image = Image.open(io.BytesIO(image_bytes))
        elif isinstance(image_data, str):
            if image_data.startswith('data:'):  # Data URL
                # Extract base64 part
                if ',' in image_data:
                    image_data = image_data.split(',')[1]
                image_bytes = base64.b64decode(image_data)
                image = Image.open(io.BytesIO(image_bytes))
            else:  # Assume base64 string
                image_bytes = base64.b64decode(image_data)
                image = Image.open(io.BytesIO(image_bytes))
        else:
            raise ValueError(f"Unsupported image data type: {type(image_data)}")
        
        # Convert image to RGB if needed
        if image.mode == 'RGBA':
            image = image.convert('RGB')
        elif image.mode not in ['RGB', 'L']:
            image = image.convert('RGB')
        
        # Generate filename
        timestamp = int(time.time())
        filename = f"{prefix}_{timestamp}.png"
        filepath = os.path.join(comfy_input_dir, filename)
        
        # Save image
        image.save(filepath, format='PNG')
        
        # Verify the saved image
        with Image.open(filepath) as verify_img:
            verify_img.verify()
        
        logger.info(f"Saved ControlNet image: {filepath}")
        return filename
        
    except Exception as e:
        logger.error(f"Error processing ControlNet image: {str(e)}")
        raise

def inject_controlnet_into_workflow(workflow: Dict[str, Any], controlnet_data: Dict[str, Any], comfy_input_dir: str) -> Dict[str, Any]:
    """
    Inject ControlNet configuration into a ComfyUI workflow.
    
    Args:
        workflow: The ComfyUI workflow to modify
        controlnet_data: ControlNet configuration with processed images
        comfy_input_dir: Path to ComfyUI input directory
    
    Returns:
        Dict: Modified workflow with ControlNet nodes
    """
    if not controlnet_data or not controlnet_data.get('enabled'):
        return workflow
    
    units = controlnet_data.get('units', [])
    if not units:
        return workflow
    
    # For now, we'll handle the first enabled unit
    # TODO: Support multiple ControlNet units
    enabled_units = [unit for unit in units if unit.get('enabled')]
    if not enabled_units:
        return workflow
    
    unit = enabled_units[0]  # Use first enabled unit
    
    # Find the KSampler node to modify its connections
    ksampler_node = None
    for node_id, node_data in workflow.get('prompt', {}).items():
        if node_data.get('class_type') == 'KSampler':
            ksampler_node = node_id
            break
    
    if not ksampler_node:
        logger.warning("No KSampler node found in workflow")
        return workflow
    
    # Find positive and negative prompt nodes
    positive_node = None
    negative_node = None
    ksampler_inputs = workflow['prompt'][ksampler_node].get('inputs', {})
    
    positive_input = ksampler_inputs.get('positive')
    negative_input = ksampler_inputs.get('negative')
    
    if positive_input and isinstance(positive_input, list) and len(positive_input) > 0:
        positive_node = str(positive_input[0])
    if negative_input and isinstance(negative_input, list) and len(negative_input) > 0:
        negative_node = str(negative_input[0])
    
    # Add ControlNet nodes to the workflow
    next_node_id = str(max([int(k) for k in workflow['prompt'].keys() if k.isdigit()]) + 1)
    
    # Add ControlNet Loader
    controlnet_loader_id = next_node_id
    workflow['prompt'][controlnet_loader_id] = {
        "class_type": "ControlNetLoader",
        "inputs": {
            "control_net_name": unit.get('model', 'diffusion_pytorch_model.safetensors')
        }
    }
    
    # Add ControlNet Load Image node for the ControlNet input image
    next_node_id = str(int(next_node_id) + 1)
    controlnet_load_image_id = next_node_id
    workflow['prompt'][controlnet_load_image_id] = {
        "class_type": "LoadImage",
        "inputs": {
            "image": os.path.join(comfy_input_dir, unit.get('input_image_path', ''))
        }
    }
    
    # Add ControlNet Apply Advanced
    next_node_id = str(int(next_node_id) + 1)
    controlnet_apply_id = next_node_id
    workflow['prompt'][controlnet_apply_id] = {
        "class_type": "ControlNetApplyAdvanced",
        "inputs": {
            "positive": [positive_node, 0] if positive_node else ["6", 0],
            "negative": [negative_node, 0] if negative_node else ["7", 0],
            "control_net": [controlnet_loader_id, 0],
            "image": [controlnet_load_image_id, 0],  # Use the ControlNet image
            "strength": unit.get('weight', 1.0),
            "start_percent": unit.get('guidance_start', 0.0),
            "end_percent": unit.get('guidance_end', 1.0)
        }
    }
    
    # Update KSampler to use ControlNet output
    workflow['prompt'][ksampler_node]['inputs']['positive'] = [controlnet_apply_id, 0]
    workflow['prompt'][ksampler_node]['inputs']['negative'] = [controlnet_apply_id, 1]
    
    logger.info(f"Injected ControlNet into workflow with unit: {unit.get('control_type', 'unknown')}")
    return workflow

def validate_controlnet_config(controlnet_data: Dict[str, Any]) -> bool:
    """
    Validate ControlNet configuration from frontend.
    
    Args:
        controlnet_data: ControlNet configuration to validate
    
    Returns:
        bool: True if valid, False otherwise
    """
    if not controlnet_data:
        return False
    
    if not controlnet_data.get('enabled'):
        return False
    
    units = controlnet_data.get('units', [])
    if not units:
        return False
    
    # Check if at least one unit is enabled and has required fields
    for unit in units:
        if unit.get('enabled'):
            # Check required fields
            if not unit.get('control_type'):
                logger.warning("ControlNet unit missing control_type")
                return False
            
            if not unit.get('model'):
                logger.warning("ControlNet unit missing model")
                return False
            
            # Image is optional for some use cases
            if not unit.get('input_image'):
                logger.warning("ControlNet unit missing input_image")
                return False
    
    return True 