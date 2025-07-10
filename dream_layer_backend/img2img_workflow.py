from dream_layer_backend_utils.update_custom_workflow import override_workflow
from dream_layer_backend_utils.update_custom_workflow import update_custom_workflow
from dream_layer_backend_utils.update_custom_workflow import update_image_paths_in_workflow
from dream_layer_backend_utils.update_custom_workflow import validate_custom_workflow
from dream_layer_backend_utils.img2img_controlnet_processor import process_controlnet_images, inject_controlnet_into_workflow, validate_controlnet_config
from dream_layer_backend_utils.api_key_injector import inject_api_keys_into_workflow
from dream_layer_backend_utils.workflow_loader import load_workflow
import json
import os
import random
import re
import logging
from dream_layer import get_directories 
from extras import COMFY_INPUT_DIR

logger = logging.getLogger(__name__)


def transform_to_img2img_workflow(data):
    """
    Transform frontend request data into ComfyUI workflow format for img2img
    """

    # Create workflow_request dictionary with the 4 keys expected by load_workflow
    workflow_request = {
        'generation_flow': 'img2img',
        'model_name': 'local',  # Default to local, will be updated based on actual model
        'controlnet': 'controlnet' in data,  # True if controlnet exists in data, False otherwise
        'lora': data.get('lora') is not None  # True if lora exists and is not None, False otherwise
    }
    
    # Determine model type based on model_name
    model_name = data.get('model_name', 'v1-6-pruned-emaonly-fp16.safetensors')
    if 'bfl' in model_name.lower() or 'flux' in model_name.lower():
        workflow_request['model_name'] = 'bfl'
    elif 'ideogram' in model_name.lower():  # Added check for ideogram models
        workflow_request['model_name'] = 'ideogram'
    else:
        workflow_request['model_name'] = 'local'
    
    print(f"\nWorkflow request dictionary:")
    print("-"*30)
    print(json.dumps(workflow_request, indent=2))
    print("-"*30)

    # Log the raw incoming data
    logger.info("Raw data received in transform_to_img2img_workflow:")
    logger.info(json.dumps({
        **data,
        'input_image': 'BASE64_IMAGE_DATA' if 'input_image' in data else None,
        'controlnet': 'CONTROLNET_DATA' if 'controlnet' in data else None
    }, indent=2))
    # Get output directory using the shared function
    output_dir, _ = get_directories()
    logger.info(f"\nUsing output directory: {output_dir}")

        # Process ControlNet data if present
    controlnet_data = data.get('controlnet')
    if controlnet_data and validate_controlnet_config(controlnet_data):
        logger.info("Processing ControlNet configuration...")
        try:
            controlnet_data = process_controlnet_images(controlnet_data, COMFY_INPUT_DIR)
            logger.info("ControlNet images processed successfully")
        except Exception as e:
            logger.error(f"Error processing ControlNet images: {str(e)}")
            controlnet_data = None
    else:
        if controlnet_data:
            logger.warning("Invalid ControlNet configuration, ignoring ControlNet")
        controlnet_data = None
    
    # Extract parameters with validation and type conversion
    prompt = data.get('prompt', '')
    negative_prompt = data.get('negative_prompt', '')
    width = max(64, min(2048, int(data.get('width', 512))))
    height = max(64, min(2048, int(data.get('height', 512))))
    batch_size = max(1, min(8, int(data.get('batch_size', 1))))
    steps = max(1, min(150, int(data.get('steps', 20))))
    cfg_scale = max(1.0, min(20.0, float(data.get('cfg_scale', 7.0))))
    denoising_strength = max(0.0, min(1.0, float(data.get('denoising_strength', 0.75))))
    input_image = data.get('input_image', '')
    model_name = data.get('model_name', 'v1-6-pruned-emaonly-fp16.safetensors')
    sampler_name = data.get('sampler_name', 'euler')
    scheduler = data.get('scheduler', 'normal')
    
    # Advanced settings
    vae_name = data.get('vae_name')
    clip_skip = data.get('clip_skip', 1)
    tiling = data.get('tiling', False)
    hires_fix = data.get('hires_fix', False)
    karras_sigmas = data.get('karras_sigmas', False)
    
    # Handle seed - ensure it's a positive integer
    try:
        seed = int(data.get('seed', 0))
    except (ValueError, TypeError):
        seed = 0
        
    # Generate a random positive seed if seed is 0 or negative
    if seed <= 0:
        seed = random.randint(1, 2**31 - 1)  # Using 2^31-1 as max to ensure it's well within safe integer range
        logger.info(f"Generated random seed: {seed}")
    
    # Update the data with the actual seed used
    data['seed'] = seed

    # Create core generation settings dictionary with all hardcoded values
    core_generation_settings = {
        'prompt': prompt,
        'negative_prompt': negative_prompt,
        'width': width,
        'height': height,
        'batch_size': batch_size,
        'steps': steps,
        'cfg': cfg_scale,
        'sampler_name': sampler_name,
        'scheduler': scheduler,
        'seed': seed,
        'ckpt_name': model_name,
        'denoise': 1.0,
        "image": os.path.join(COMFY_INPUT_DIR, input_image)
    }

    # Log the processed parameters
    logger.info("Core Generation Settings")
    logger.info(json.dumps(core_generation_settings, indent=4))
    
    # Create the ComfyUI workflow
    workflow = {
        "prompt": {
            "3": {
                "class_type": "KSampler",
                "inputs": {
                    "cfg": cfg_scale,
                    "denoise": denoising_strength,
                    "latent_image": ["5", 0],
                    "model": ["4", 0],
                    "negative": ["7", 0],
                    "positive": ["6", 0],
                    "sampler_name": sampler_name,
                    "scheduler": scheduler,
                    "seed": seed,
                    "steps": steps
                }
            },
            "4": {
                "class_type": "CheckpointLoaderSimple",
                "inputs": {
                    "ckpt_name": model_name
                }
            },
            "5": {
                "class_type": "VAEEncode",
                "inputs": {
                    "pixels": ["resize", 0],
                    "vae": ["4", 2] if not vae_name else ["11", 0]
                }
            },
            "6": {
                "class_type": "CLIPTextEncode",
                "inputs": {
                    "clip": ["4", 1],
                    "text": prompt
                }
            },
            "7": {
                "class_type": "CLIPTextEncode",
                "inputs": {
                    "clip": ["4", 1],
                    "text": negative_prompt
                }
            },
            "8": {
                "class_type": "VAEDecode",
                "inputs": {
                    "samples": ["3", 0],
                    "vae": ["4", 2] if not vae_name else ["11", 0]
                }
            },
            "9": {
                "class_type": "SaveImage",
                "inputs": {
                    "filename_prefix": "ComfyUI",
                    "images": ["8", 0]
                }
            },
            "10": {
                "class_type": "LoadImage",
                "inputs": {
                    "image": os.path.join(COMFY_INPUT_DIR, input_image)
                }
            },
            "resize": {
                "class_type": "ImageScale",
                "inputs": {
                    "image": ["10", 0],
                    "width": width,
                    "height": height,
                    "upscale": "disabled",
                    "crop": "center",
                    "upscale_method": "lanczos"
                }
            }
        }
    }

    # Add VAE loader if custom VAE is specified
    if vae_name:
        workflow["prompt"]["11"] = {
            "class_type": "VAELoader",
            "inputs": {
                "vae_name": vae_name
            }
        }
    
    loaded_workflow = load_workflow(workflow_request)
    print("\nLoaded workflow:")
    print("-"*50)
    print(json.dumps(loaded_workflow, indent=2))
    print("-"*50)
    
    # Check if custom workflow is provided and use it instead of the default workflow
    custom_workflow = data.get('custom_workflow')
    if custom_workflow and validate_custom_workflow(custom_workflow):
        logger.info("Custom workflow detected, updating with current parameters...")
        try:
            # Update the custom workflow with the current parameters
            workflow = update_custom_workflow(workflow, custom_workflow)
            logger.info("Successfully updated custom workflow with current parameters")
        except Exception as e:
            logger.error(f"Error updating custom workflow: {str(e)}")
            logger.info("Falling back to default workflow")
    else:
        # Update the default workflow with the current parameters
        workflow = override_workflow(loaded_workflow, core_generation_settings)
        # Update image paths in the workflow
        workflow = update_image_paths_in_workflow(workflow, os.path.join(COMFY_INPUT_DIR, input_image))
        logger.info("No valid custom workflow provided, using default workflow")
    
    # Log the generated workflow
    logger.info("Generated workflow:")
    logger.info(json.dumps(workflow, indent=2))

        # Inject ControlNet into the workflow if present
    if controlnet_data:
        logger.info("Injecting ControlNet into workflow...")
        try:
            workflow = inject_controlnet_into_workflow(workflow, controlnet_data, COMFY_INPUT_DIR)
            logger.info("ControlNet successfully injected into workflow")
            
            
        except Exception as e:
            logger.error(f"Error injecting ControlNet into workflow: {str(e)}")
    else:
        logger.info("No ControlNet data provided - skipping ControlNet injection")
    
    # Inject API keys from environment variables into the workflow
    workflow = inject_api_keys_into_workflow(workflow)
    
    return workflow

def extract_filename_from_data_url(data_url):
    """Extract filename from data URL if present in the format data:image/...;name=filename.ext;base64,..."""
    if not data_url:
        return None
    
    # Try to find name parameter in the data URL
    name_match = re.search(r';name=(.*?);', data_url)
    if name_match:
        return name_match.group(1)
    return None
