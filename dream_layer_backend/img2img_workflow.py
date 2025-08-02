from dream_layer_backend_utils.update_custom_workflow import override_workflow
from dream_layer_backend_utils.update_custom_workflow import update_custom_workflow
from dream_layer_backend_utils.update_custom_workflow import update_image_paths_in_workflow
from dream_layer_backend_utils.update_custom_workflow import validate_custom_workflow
from dream_layer_backend_utils.img2img_controlnet_processor import process_controlnet_images, inject_controlnet_into_workflow, validate_controlnet_config
from dream_layer_backend_utils.api_key_injector import inject_api_keys_into_workflow, read_api_keys_from_env
from dream_layer_backend_utils.workflow_loader import load_workflow
from dream_layer_backend_utils.shared_workflow_parameters import (
    inject_face_restoration_parameters,
    inject_tiling_parameters,
    inject_hires_fix_parameters,
    inject_refiner_parameters
)
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

    # Determine model type and features
    model_name = data.get('model_name', 'v1-6-pruned-emaonly-fp16.safetensors')
    use_controlnet = bool(data.get('controlnet'))
    use_lora = bool(data.get('lora'))

    # Select the correct workflow template path
    workflow_template_path = get_img2img_workflow_template(
        model_name, use_controlnet, use_lora)

    # Load the workflow from the template file
    with open(workflow_template_path, 'r') as f:
        workflow = json.load(f)

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
            controlnet_data = process_controlnet_images(
                controlnet_data, COMFY_INPUT_DIR)
            logger.info("ControlNet images processed successfully")
        except Exception as e:
            logger.error(f"Error processing ControlNet images: {str(e)}")
            controlnet_data = None
    else:
        if controlnet_data:
            logger.warning(
                "Invalid ControlNet configuration, ignoring ControlNet")
        controlnet_data = None

    # Extract parameters with validation and type conversion
    prompt = data.get('prompt', '')
    negative_prompt = data.get('negative_prompt', '')
    width = max(64, min(2048, int(data.get('width', 512))))
    height = max(64, min(2048, int(data.get('height', 512))))
    batch_size = max(1, min(8, int(data.get('batch_size', 1))))
    steps = max(1, min(150, int(data.get('steps', 20))))
    cfg_scale = max(1.0, min(20.0, float(data.get('cfg_scale', 7.0))))
    denoising_strength = max(
        0.0, min(1.0, float(data.get('denoising_strength', 0.75))))
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
        # Using 2^31-1 as max to ensure it's well within safe integer range
        seed = random.randint(1, 2**31 - 1)
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
    # The old hardcoded workflow dict is removed, so this block is now empty.
    # The workflow object is now loaded directly from the template.

    # Add VAE loader if custom VAE is specified
    if vae_name:
        workflow["prompt"]["11"] = {
            "class_type": "VAELoader",
            "inputs": {
                "vae_name": vae_name
            }
        }

    # The original workflow loading logic using load_workflow is removed.
    # The workflow object is now directly loaded from the template.

    # Check if custom workflow is provided and use it instead of the default workflow
    custom_workflow = data.get('custom_workflow')
    if custom_workflow and validate_custom_workflow(custom_workflow):
        logger.info(
            "Custom workflow detected, updating with current parameters...")
        try:
            # Update the custom workflow with the current parameters
            workflow = update_custom_workflow(workflow, custom_workflow)
            logger.info(
                "Successfully updated custom workflow with current parameters")
        except Exception as e:
            logger.error(f"Error updating custom workflow: {str(e)}")
            logger.info("Falling back to default workflow")
    else:
        # Update the default workflow with the current parameters
        workflow = override_workflow(workflow, core_generation_settings)
        # Update image paths in the workflow
        workflow = update_image_paths_in_workflow(
            workflow, os.path.join(COMFY_INPUT_DIR, input_image))
        logger.info("No valid custom workflow provided, using default workflow")

    # Log the generated workflow
    logger.info("Generated workflow:")
    logger.info(json.dumps(workflow, indent=2))

    # Inject ControlNet into the workflow if present
    if controlnet_data:
        logger.info("Injecting ControlNet into workflow...")
        try:
            workflow = inject_controlnet_into_workflow(
                workflow, controlnet_data, COMFY_INPUT_DIR)
            logger.info("ControlNet successfully injected into workflow")

        except Exception as e:
            logger.error(f"Error injecting ControlNet into workflow: {str(e)}")
    else:
        logger.info(
            "No ControlNet data provided - skipping ControlNet injection")

    # Inject API keys from environment variables into the workflow
    all_api_keys = read_api_keys_from_env()
    workflow = inject_api_keys_into_workflow(workflow, all_api_keys)

    # Process mask file if present (for inpainting)
    mask_image = data.get('mask_image')
    if mask_image:
        logger.info(f"Processing mask for inpainting: {mask_image}")
        try:
            workflow = inject_mask_into_workflow(
                workflow, mask_image, COMFY_INPUT_DIR)
            logger.info(
                "Mask successfully injected into workflow for inpainting")
        except Exception as e:
            logger.error(f"Error injecting mask into workflow: {str(e)}")
            logger.info("Continuing without mask (regular img2img)")
    else:
        logger.info("No mask provided - using regular img2img")

    # Extract advanced option data (mirroring txt2img)
    face_restoration_data = {
        'restore_faces': data.get('restore_faces', False),
        'face_restoration_model': data.get('face_restoration_model', 'codeformer'),
        'codeformer_weight': data.get('codeformer_weight', 0.5),
        'gfpgan_weight': data.get('gfpgan_weight', 0.5)
    }
    tiling_data = {
        'tiling': data.get('tiling', False),
        'tile_size': data.get('tile_size', 512),
        'tile_overlap': data.get('tile_overlap', 64)
    }
    hires_fix_data = {
        'hires_fix': data.get('hires_fix', False),
        'hires_fix_upscale_method': data.get('hires_fix_upscale_method', 'upscale-by'),
        'hires_fix_upscale_factor': data.get('hires_fix_upscale_factor', 2.5),
        'hires_fix_hires_steps': data.get('hires_fix_hires_steps', 1),
        'hires_fix_denoising_strength': data.get('hires_fix_denoising_strength', 0.5),
        'hires_fix_resize_width': data.get('hires_fix_resize_width', 4000),
        'hires_fix_resize_height': data.get('hires_fix_resize_height', 4000),
        'hires_fix_upscaler': data.get('hires_fix_upscaler', '4x-ultrasharp')
    }
    refiner_data = {
        'refiner_enabled': data.get('refiner_enabled', False),
        'refiner_model': data.get('refiner_model', 'none'),
        'refiner_switch_at': data.get('refiner_switch_at', 0.8)
    }
    # Inject advanced options if enabled
    if face_restoration_data['restore_faces']:
        logger.info("Injecting Face Restoration parameters...")
        workflow = inject_face_restoration_parameters(
            workflow, face_restoration_data)
    if tiling_data['tiling']:
        logger.info("Injecting Tiling parameters...")
        workflow = inject_tiling_parameters(workflow, tiling_data)
    if hires_fix_data['hires_fix']:
        logger.info("Injecting Hires.fix parameters...")
        workflow = inject_hires_fix_parameters(workflow, hires_fix_data)
    if refiner_data['refiner_enabled']:
        logger.info("Injecting Refiner parameters...")
        workflow = inject_refiner_parameters(workflow, refiner_data)

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


def get_img2img_workflow_template(model_name, use_controlnet=False, use_lora=False):
    model_name_lower = model_name.lower()

    # Check for BFL/Flux models first (they have their own workflow)
    if "bfl" in model_name_lower or "flux" in model_name_lower:
        return "workflows/img2img/bfl_core_generation_workflow.json"

    # Check for Ideogram models
    elif "ideogram" in model_name_lower:
        return "workflows/img2img/ideogram_core_generation_workflow.json"

    # For all other models (SD1.5, SDXL, etc.), use the appropriate workflow based on features
    else:
        if use_controlnet and use_lora:
            return "workflows/img2img/local_controlnet_lora.json"
        elif use_controlnet:
            return "workflows/img2img/local_controlnet.json"
        elif use_lora:
            return "workflows/img2img/local_lora.json"
        else:
            return "workflows/img2img/core_generation_workflow.json"


def inject_mask_into_workflow(workflow, mask_filename, comfy_input_dir):
    """
    Inject mask file into ComfyUI workflow for inpainting using VAEEncodeForInpaint.
    Args:
        workflow: ComfyUI workflow dictionary
        mask_filename: Filename of the mask file in ComfyUI input directory
        comfy_input_dir: Path to ComfyUI input directory
    Returns:
        dict: Updated workflow with mask nodes
    """
    mask_path = os.path.join(comfy_input_dir, mask_filename)

    # Verify the mask file exists and is accessible
    if not os.path.exists(mask_path):
        raise FileNotFoundError(f"Mask file not found at: {mask_path}")

    # Find the next available node ID
    max_node_id = max(int(k) for k in workflow["prompt"].keys()
                      if k.replace('.', '').isdigit())
    next_id = str(max_node_id + 1)

    # Find the input image node (LoadImage or similar)
    input_image_node_id = None
    vae_node_id = None
    for node_id, node_data in workflow["prompt"].items():
        if node_data.get("class_type", "").startswith("LoadImage"):
            input_image_node_id = node_id
        if node_data.get("class_type") in ("VAELoader", "CheckpointLoaderSimple"):
            vae_node_id = node_id

    if not input_image_node_id:
        raise RuntimeError(
            "Could not find input image node for inpainting workflow.")
    if not vae_node_id:
        raise RuntimeError("Could not find VAE node for inpainting workflow.")

    # Add LoadImageMask node for the mask
    mask_node_id = next_id
    workflow["prompt"][mask_node_id] = {
        "class_type": "LoadImageMask",
        "inputs": {
            "image": mask_filename,  # Just the filename, not full path
            "channel": "alpha"
        }
    }
    next_id = str(int(next_id) + 1)

    # Add VAEEncodeForInpaint node
    vae_encode_inpaint_node_id = next_id
    workflow["prompt"][vae_encode_inpaint_node_id] = {
        "class_type": "VAEEncodeForInpaint",
        "inputs": {
            "pixels": [input_image_node_id, 0],
            "vae": [vae_node_id, 0] if workflow["prompt"][vae_node_id].get("class_type") == "VAELoader" else [vae_node_id, 2],
            "mask": [mask_node_id, 0],
            "grow_mask_by": 6
        }
    }

    # Find the KSampler node and update its latent_image input
    ksampler_node_id = None
    for node_id, node_data in workflow["prompt"].items():
        if node_data.get("class_type") == "KSampler":
            ksampler_node_id = node_id
            break

    if ksampler_node_id:
        # Remove any mask input from KSampler (we're using VAEEncodeForInpaint instead)
        workflow["prompt"][ksampler_node_id]["inputs"].pop("mask", None)
        # Set latent_image to output of VAEEncodeForInpaint
        workflow["prompt"][ksampler_node_id]["inputs"]["latent_image"] = [
            vae_encode_inpaint_node_id, 0]
        logger.info(
            f"Updated KSampler node {ksampler_node_id} to use latent from VAEEncodeForInpaint node {vae_encode_inpaint_node_id}")
    else:
        logger.warning("Could not find KSampler node in workflow")

    return workflow
