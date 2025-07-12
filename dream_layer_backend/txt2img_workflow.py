import json
import random
import os
import json
import re
from pathlib import Path
from constants import (
    DIMENSION_LIMITS, BATCH_SIZE_LIMITS, SAMPLING_LIMITS, 
    SEED_LIMITS, BASE64_DETECTION, DEFAULT_PATHS, 
    CONTROLNET_TYPE_MAPPING
)
from dream_layer_backend_utils.workflow_loader import load_workflow
from dream_layer_backend_utils.api_key_injector import inject_api_keys_into_workflow
from dream_layer_backend_utils.update_custom_workflow import override_workflow 
from dream_layer_backend_utils.update_custom_workflow import update_custom_workflow, validate_custom_workflow
from shared_utils import SAMPLER_NAME_MAP
from controlnet import save_controlnet_image, create_test_controlnet_image


def increment_seed_in_workflow(workflow, increment):
    """Increment seed in workflow for batch generation - handles both ComfyUI and closed-source workflows"""
    try:
        # First try to find KSampler node (for ComfyUI workflows)
        for node_id, node_data in workflow.get('prompt', {}).items():
            if node_data.get('class_type') == 'KSampler':
                current_seed = node_data.get('inputs', {}).get('seed', 0)
                node_data['inputs']['seed'] = current_seed + increment
                print(f"🎲 Incremented KSampler seed: {current_seed} -> {current_seed + increment}")
                return workflow
        
        # If no KSampler found, try closed-source model nodes (DALL-E, BFL, Ideogram)
        closed_source_nodes = ['OpenAIDalle3', 'OpenAIDalle2', 'FluxProImageNode', 'FluxProUltraImageNode', 'FluxDevImageNode', 'IdeogramV3']
        for node_id, node_data in workflow.get('prompt', {}).items():
            if node_data.get('class_type') in closed_source_nodes:
                current_seed = node_data.get('inputs', {}).get('seed', 0)
                new_seed = current_seed + increment
                node_data['inputs']['seed'] = new_seed
                print(f"🎲 Incremented {node_data.get('class_type')} seed: {current_seed} -> {new_seed}")
                return workflow
        
        print("⚠️ No seed node found to increment")
        
    except Exception as e:
        print(f"Error incrementing seed: {e}")
    return workflow


def transform_to_txt2img_workflow(data):
    """
    Transform frontend data to ComfyUI txt2img workflow
    Combines advanced ControlNet functionality with smallFeatures improvements
    """
    try:
        print("\n🔄 Transforming txt2img workflow:")
        print("-" * 40)
        print(f"📊 Data keys: {list(data.keys())}")
        
        # Extract and validate core parameters with smallFeatures improvements
        prompt = data.get('prompt', '')
        negative_prompt = data.get('negative_prompt', '')
        
        # Dimension validation
        width = max(DIMENSION_LIMITS['MIN'], min(DIMENSION_LIMITS['MAX'], int(data.get('width', DIMENSION_LIMITS['DEFAULT']))))
        height = max(DIMENSION_LIMITS['MIN'], min(DIMENSION_LIMITS['MAX'], int(data.get('height', DIMENSION_LIMITS['DEFAULT']))))
        
        # Batch parameters with validation (from smallFeatures)
        batch_size = max(BATCH_SIZE_LIMITS['MIN'], min(BATCH_SIZE_LIMITS['MAX'], int(data.get('batch_size', BATCH_SIZE_LIMITS['DEFAULT']))))
        print(f"\nBatch size: {batch_size}")
        
        # Sampling parameters with validation
        steps = max(SAMPLING_LIMITS['STEPS']['MIN'], min(SAMPLING_LIMITS['STEPS']['MAX'], int(data.get('steps', SAMPLING_LIMITS['STEPS']['DEFAULT']))))
        cfg_scale = max(SAMPLING_LIMITS['CFG_SCALE']['MIN'], min(SAMPLING_LIMITS['CFG_SCALE']['MAX'], float(data.get('cfg_scale', SAMPLING_LIMITS['CFG_SCALE']['DEFAULT']))))
        
        # Get sampler name and map it to ComfyUI format (from smallFeatures)
        frontend_sampler = data.get('sampler_name', 'euler')
        sampler_name = SAMPLER_NAME_MAP.get(frontend_sampler, 'euler')
        print(f"\nMapping sampler name: {frontend_sampler} -> {sampler_name}")
        
        scheduler = data.get('scheduler', 'normal')
        
        # Handle seed - enhanced from smallFeatures for -1 values
        try:
            seed = int(data.get('seed', 0))
            if seed < SEED_LIMITS['MIN_VALUE']:
                seed = random.randint(SEED_LIMITS['MIN_VALUE'], SEED_LIMITS['MAX_VALUE'])
        except (ValueError, TypeError):
            seed = random.randint(SEED_LIMITS['MIN_VALUE'], SEED_LIMITS['MAX_VALUE'])
        
        # Handle model name validation
        model_name = data.get('model_name', 'juggernautXL_v8Rundiffusion.safetensors')
        
        # Check if it's a closed-source model (DALL-E, FLUX, Ideogram, etc.)
        closed_source_models = ['dall-e-3', 'dall-e-2', 'flux-pro', 'flux-dev', 'ideogram-v3']
        
        if model_name in closed_source_models:
            print(f"🎨 Using closed-source model: {model_name}")
        
        print(f"\nUsing model: {model_name}")
        
        core_generation_settings = {
            'prompt': prompt,
            'negative_prompt': negative_prompt,
            'width': width,
            'height': height,
            'batch_size': batch_size,
            'steps': steps,
            'cfg_scale': cfg_scale,
            'sampler_name': sampler_name,
            'scheduler': scheduler,
            'seed': seed,
            'ckpt_name': model_name,
            'denoise': 1.0
        }
        print(f"🎯 Core settings: {core_generation_settings}")
        
        # Extract ControlNet data
        controlnet_data = data.get('controlnet', {})
        print(f"🎮 ControlNet data: {controlnet_data}")
        
        # Extract Face Restoration data
        face_restoration_data = {
            'restore_faces': data.get('restore_faces', False),
            'face_restoration_model': data.get('face_restoration_model', 'codeformer'),
            'codeformer_weight': data.get('codeformer_weight', 0.5),
            'gfpgan_weight': data.get('gfpgan_weight', 0.5)
        }
        print(f"👤 Face Restoration data: {face_restoration_data}")
        
        # Extract Tiling data
        tiling_data = {
            'tiling': data.get('tiling', False),
            'tile_size': data.get('tile_size', 512),
            'tile_overlap': data.get('tile_overlap', 64)
        }
        print(f"🧩 Tiling data: {tiling_data}")
        
        # Extract Hires.fix data
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
        print(f"🖼️ Hires.fix data: {hires_fix_data}")
        
        # Extract Refiner data
        refiner_data = {
            'refiner_enabled': data.get('refiner_enabled', False),
            'refiner_model': data.get('refiner_model', 'none'),
            'refiner_switch_at': data.get('refiner_switch_at', 0.8)
        }
        print(f"🖌️ Refiner data: {refiner_data}")
        
        # Determine workflow template based on features
        use_controlnet = controlnet_data.get('enabled', False) and controlnet_data.get('units')
        use_lora = data.get('lora') and data.get('lora').get('enabled', False)
        use_face_restoration = face_restoration_data.get('restore_faces', False)
        use_tiling = tiling_data.get('tiling', False)
        
        print(f"🔧 Use ControlNet: {use_controlnet}")
        print(f"🔧 Use LoRA: {use_lora}")
        print(f"🔧 Use Face Restoration: {use_face_restoration}")
        print(f"🔧 Use Tiling: {use_tiling}")
        
        # Create workflow request for the loader
        if model_name in ['dall-e-3', 'dall-e-2']:
            workflow_model_type = 'dalle'
        elif model_name in ['flux-pro', 'flux-dev']:
            workflow_model_type = 'bfl'
        elif 'ideogram' in model_name.lower():  # Added check for ideogram models
            workflow_model_type = 'ideogram'
        else:
            workflow_model_type = 'local'
        
        workflow_request = {
            'generation_flow': 'txt2img',
            'model_name': workflow_model_type,
            'controlnet': use_controlnet,
            'lora': use_lora
        }
        
        print(f"📄 Workflow request: {workflow_request}")
        
        # Load workflow using the workflow loader
        workflow = load_workflow(workflow_request)
        print(f"✅ Workflow loaded successfully")
        
        # Inject API keys if needed (for DALL-E, FLUX, etc.)
        workflow = inject_api_keys_into_workflow(workflow)
        print(f"✅ API keys injected")
        
        # Custom workflow support from smallFeatures
        custom_workflow = data.get('custom_workflow')
        if custom_workflow and validate_custom_workflow(custom_workflow):
            print("Custom workflow detected, updating with current parameters...")
            try:
                workflow = update_custom_workflow(workflow, custom_workflow)
                print("Successfully updated custom workflow with current parameters")
            except Exception as e:
                print(f"Error updating custom workflow: {str(e)}")
                print("Falling back to default workflow override")
                workflow = override_workflow(workflow, core_generation_settings)
        else:
            # Apply overrides to loaded workflow
            workflow = override_workflow(workflow, core_generation_settings)
            print("No valid custom workflow provided, using default workflow with overrides")
        
        print(f"✅ Core settings applied")
        
        # Apply LoRA parameters if enabled
        if use_lora:
            print(f"🎨 Applying LoRA parameters...")
            workflow = inject_lora_parameters(workflow, data.get('lora', {}))
        
        # Apply ControlNet parameters if enabled
        if use_controlnet:
            print(f"🎮 Applying ControlNet parameters...")
            workflow = inject_controlnet_parameters(workflow, controlnet_data)
        
        # Apply Face Restoration parameters if enabled
        if use_face_restoration:
            print(f"👤 Applying Face Restoration parameters...")
            workflow = inject_face_restoration_parameters(workflow, face_restoration_data)
        
        # Apply Tiling parameters if enabled
        if use_tiling:
            print(f"🧩 Applying Tiling parameters...")
            workflow = inject_tiling_parameters(workflow, tiling_data)
        
        # Apply Hires.fix parameters if enabled
        if hires_fix_data.get('hires_fix', False):
            print(f"✨ Applying Hires.fix parameters...")
            workflow = inject_hires_fix_parameters(workflow, hires_fix_data)
        
        # Apply Refiner parameters if enabled
        if refiner_data.get('refiner_enabled', False):
            print(f"✨ Applying Refiner parameters...")
            workflow = inject_refiner_parameters(workflow, refiner_data)
        
        print(f"✅ Workflow transformation complete")
        print(f"📋 Generated workflow: {json.dumps(workflow, indent=2)}")
        return workflow
        
    except Exception as e:
        print(f"❌ Error transforming workflow: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


def inject_lora_parameters(workflow, lora_data):
    """
    Inject LoRA parameters into the workflow.
    
    Args:
        workflow (dict): The ComfyUI workflow
        lora_data (dict): LoRA configuration from frontend
    
    Returns:
        dict: Updated workflow with LoRA parameters
    """
    try:
        print("\nInjecting LoRA parameters:")
        print("-"*30)
        print(json.dumps(lora_data, indent=2))
        print("-"*30)
        
        if not lora_data.get('enabled', False):
            print("LoRA not enabled")
            return workflow
        
        lora_name = lora_data.get('lora_name')
        strength_model = lora_data.get('strength_model', 1.0)
        strength_clip = lora_data.get('strength_clip', 1.0)
        
        if not lora_name:
            print("No LoRA name provided")
            return workflow
        
        # Find LoraLoader node in the workflow
        prompt = workflow.get('prompt', {})
        
        for node_id, node_data in prompt.items():
            if node_data.get('class_type') == 'LoraLoader':
                node_data['inputs']['lora_name'] = lora_name
                node_data['inputs']['strength_model'] = strength_model
                node_data['inputs']['strength_clip'] = strength_clip
                print(f"Updated LoRA: {lora_name} (model: {strength_model}, clip: {strength_clip})")
                break
        
        print("LoRA parameters injected successfully")
        return workflow
        
    except Exception as e:
        print(f"Error injecting LoRA parameters: {str(e)}")
        return workflow

def inject_controlnet_parameters(workflow, controlnet_data):
    """
    Inject ControlNet parameters into the workflow.
    
    Args:
        workflow (dict): The ComfyUI workflow
        controlnet_data (dict): ControlNet configuration from frontend
    
    Returns:
        dict: Updated workflow with ControlNet parameters
    """
    try:
        print("\nInjecting ControlNet parameters:")
        print("-"*30)
        print(json.dumps(controlnet_data, indent=2))
        print("-"*30)
        
        if not controlnet_data.get('enabled', False) or not controlnet_data.get('units'):
            print("ControlNet not enabled or no units provided")
            return workflow
        
        units = controlnet_data['units']
        if not units:
            print("No ControlNet units provided")
            return workflow
        
        # Handle multiple ControlNet units - filter enabled units
        enabled_units = [unit for unit in units if unit.get('enabled', False)]
        if not enabled_units:
            print("No enabled ControlNet units found")
            return workflow
        
        print(f"Processing {len(enabled_units)} enabled ControlNet units")
        
        # Find ControlNet nodes in the workflow  
        prompt = workflow.get('prompt', {})
        
        # If only one unit, use the template-based approach
        if len(enabled_units) == 1:
            unit = enabled_units[0]
            
            # Update ControlNetLoader node
            for node_id, node_data in prompt.items():
                if node_data.get('class_type') == 'ControlNetLoader':
                    if unit.get('model'):
                        node_data['inputs']['control_net_name'] = unit['model']
                        print(f"Updated ControlNet model: {unit['model']}")
                    break
            
            # Update SetUnionControlNetType node if it exists
            for node_id, node_data in prompt.items():
                if node_data.get('class_type') == 'SetUnionControlNetType':
                    if unit.get('control_type'):
                        # Map frontend control types to Union ControlNet types
                        union_type = CONTROLNET_TYPE_MAPPING.get(unit['control_type'], 'openpose')
                        node_data['inputs']['type'] = union_type
                        print(f"Updated Union ControlNet type: {union_type}")
                    break
            
            # Update ControlNetApplyAdvanced node
            for node_id, node_data in prompt.items():
                if node_data.get('class_type') == 'ControlNetApplyAdvanced':
                    inputs = node_data.get('inputs', {})
                    
                    # Update strength (weight)
                    if unit.get('weight') is not None:
                        inputs['strength'] = unit['weight']
                        print(f"Updated ControlNet strength: {unit['weight']}")
                    
                    # Update guidance start/end
                    if unit.get('guidance_start') is not None:
                        inputs['start_percent'] = unit['guidance_start']
                        print(f"Updated guidance start: {unit['guidance_start']}")
                    
                    if unit.get('guidance_end') is not None:
                        inputs['end_percent'] = unit['guidance_end']
                        print(f"Updated guidance end: {unit['guidance_end']}")
                    
                    break
        
        # For multiple units, build a chain dynamically
        else:
            print("Multiple ControlNet units detected - building dynamic chain")
            
            # Find original positive/negative conditioning nodes
            original_positive = None
            original_negative = None
            for node_id, node_data in prompt.items():
                if node_data.get('class_type') == 'CLIPTextEncode':
                    inputs = node_data.get('inputs', {})
                    if 'positive' in inputs.get('text', '').lower():
                        original_positive = node_id
                    elif 'negative' in inputs.get('text', '').lower():
                        original_negative = node_id
            
            # Fallback: find any CLIPTextEncode nodes if not found by text content
            if not original_positive or not original_negative:
                clip_nodes = [node_id for node_id, node_data in prompt.items() 
                             if node_data.get('class_type') == 'CLIPTextEncode']
                if len(clip_nodes) >= 2:
                    if not original_positive:
                        original_positive = clip_nodes[0]
                    if not original_negative:
                        original_negative = clip_nodes[1]
            
            # Final fallback: use default node IDs if still not found
            if not original_positive:
                original_positive = "6"  # Default positive conditioning node
            if not original_negative:
                original_negative = "7"  # Default negative conditioning node
            
            # Get next available node ID
            numeric_ids = []
            for k in prompt.keys():
                try:
                    numeric_ids.append(float(k))
                except ValueError:
                    continue
            max_node_id = max(numeric_ids) if numeric_ids else 0
            next_node_id = int(max_node_id) + 1
            
            # Build ControlNet chain
            current_positive = original_positive
            current_negative = original_negative
            
            for i, unit in enumerate(enabled_units):
                print(f"Adding ControlNet unit {i+1}/{len(enabled_units)}: {unit.get('control_type', 'unknown')}")
                
                # Add ControlNet Loader
                loader_id = str(next_node_id)
                prompt[loader_id] = {
                    "class_type": "ControlNetLoader", 
                    "inputs": {
                        "control_net_name": unit.get('model', 'diffusion_pytorch_model.safetensors')
                    }
                }
                next_node_id += 1
                
                # Add SetUnionControlNetType
                union_id = str(next_node_id) + '.5'
                union_type = CONTROLNET_TYPE_MAPPING.get(unit.get('control_type'), 'openpose')
                prompt[union_id] = {
                    "class_type": "SetUnionControlNetType",
                    "inputs": {
                        "control_net": [loader_id, 0],
                        "type": union_type
                    }
                }
                next_node_id += 1
                
                # Add LoadImage for this unit
                load_image_id = str(next_node_id)
                prompt[load_image_id] = {
                    "class_type": "LoadImage",
                    "inputs": {
                        "image": "controlnet_input.png"  # Will be updated later with actual image
                    }
                }
                next_node_id += 1
                
                # Add ControlNetApplyAdvanced
                apply_id = str(next_node_id)
                prompt[apply_id] = {
                    "class_type": "ControlNetApplyAdvanced",
                    "inputs": {
                        "positive": [current_positive, 0] if current_positive else [original_positive, 0],
                        "negative": [current_negative, 0] if current_negative else [original_negative, 0],
                        "control_net": [union_id, 0],
                        "image": [load_image_id, 0],
                        "strength": unit.get('weight', 0.8),
                        "start_percent": unit.get('guidance_start', 0.0),
                        "end_percent": unit.get('guidance_end', 1.0)
                    }
                }
                next_node_id += 1
                
                # Chain for next unit
                current_positive = apply_id
                current_negative = apply_id
                
                print(f"Added ControlNet unit {i+1} with model {unit.get('model', 'default')}")
            
            # Update KSampler to use final ControlNet output
            for node_id, node_data in prompt.items():
                if node_data.get('class_type') == 'KSampler':
                    node_data['inputs']['positive'] = [current_positive, 0]
                    node_data['inputs']['negative'] = [current_negative, 1] 
                    print(f"Updated KSampler to use final ControlNet output from node {current_positive}")
                    break
            
            print(f"Successfully built ControlNet chain with {len(enabled_units)} units")
        
        # Handle input images for all enabled units
        print(f"🎯 Processing images for {len(enabled_units)} ControlNet units")
        
        # Collect all LoadImage nodes to update them
        load_image_nodes = []
        for node_id, node_data in prompt.items():
            if node_data.get('class_type') == 'LoadImage':
                load_image_nodes.append(node_id)
        
        print(f"🔍 Found {len(load_image_nodes)} LoadImage nodes: {load_image_nodes}")
        
        # Process each enabled unit's image
        for i, unit in enumerate(enabled_units):
            print(f"🎯 Processing image for unit {i+1}: {unit.get('control_type', 'unknown')}")
            
            input_image_value = unit.get('input_image')
            if input_image_value is not None and input_image_value != '':
                print(f"📊 Unit {i+1} input image type: {type(input_image_value)}")
                
                # Check if it's a filename (already uploaded) or base64 data
                input_image = unit['input_image']
                
                if isinstance(input_image, str):
                    # Check if it looks like a filename (not base64)
                    # More robust check: filenames typically have extensions and don't contain base64 characters
                    is_base64 = (any(input_image.startswith(prefix) for prefix in BASE64_DETECTION['PREFIXES']) or
                                (re.match(BASE64_DETECTION['PATTERN'], input_image) and len(input_image) > BASE64_DETECTION['MIN_LENGTH']))
                    if not is_base64:
                        # It's likely a filename
                        print(f"📁 Unit {i+1} using filename: {input_image}")
                        saved_filename = input_image
                    else:
                        # It's base64 data, save it
                        print(f"🔄 Unit {i+1} converting base64 to file...")
                        saved_filename = save_controlnet_image(input_image, unit.get('unit_index', i))
                        print(f"✅ Unit {i+1} saved as: {saved_filename}")
                else:
                    print(f"❌ Unit {i+1} unsupported image type: {type(input_image)}")
                    saved_filename = None
                
                # Update the corresponding LoadImage node
                if saved_filename and i < len(load_image_nodes):
                    node_id = load_image_nodes[i]
                    old_image = prompt[node_id]['inputs'].get('image', 'None')
                    prompt[node_id]['inputs']['image'] = saved_filename
                    print(f"🔄 Updated LoadImage node {node_id}: {old_image} -> {saved_filename}")
                else:
                    print(f"❌ Warning: Could not find LoadImage node for unit {i+1}")
            else:
                print(f"ℹ️ Unit {i+1} has no input image - will use default")
        
        # Ensure at least one image exists for ControlNet
        if not any(unit.get('input_image') for unit in enabled_units):
            print("📁 No ControlNet images provided, checking for default test image...")
            # Create test image if none exists
            test_image_path = Path(__file__).parent.parent.parent / DEFAULT_PATHS['COMFYUI_INPUT_DIR'] / DEFAULT_PATHS['CONTROLNET_INPUT']
            if not test_image_path.exists():
                print("📁 Creating default test image...")
                create_test_controlnet_image()
            else:
                print(f"✅ Default test image exists: {test_image_path}")
        
        print("ControlNet parameters injected successfully")
        return workflow
        
    except Exception as e:
        print(f"Error injecting ControlNet parameters: {str(e)}")
        return workflow

def inject_face_restoration_parameters(workflow, face_restoration_data):
    """
    Inject face restoration parameters into the workflow.
    
    Uses the FaceRestoreCFWithModel node from the facerestore_cf package.
    This node supports CodeFormer and GFPGAN models for face restoration.
    
    Args:
        workflow (dict): The ComfyUI workflow
        face_restoration_data (dict): Face restoration configuration from frontend
    
    Returns:
        dict: Updated workflow with face restoration parameters
    """
    try:
        print("\nInjecting Face Restoration parameters:")
        print("-"*40)
        print(json.dumps(face_restoration_data, indent=2))
        print("-"*40)
        
        if not face_restoration_data.get('restore_faces', False):
            print("Face restoration is disabled, skipping...")
            return workflow
        
        # Extract parameters
        model_type = face_restoration_data.get('face_restoration_model', 'codeformer')
        codeformer_weight = face_restoration_data.get('codeformer_weight', 0.5)
        gfpgan_weight = face_restoration_data.get('gfpgan_weight', 0.5)
        
        print(f"Model type: {model_type}")
        print(f"CodeFormer weight: {codeformer_weight}")
        print(f"GFPGAN weight: {gfpgan_weight}")
        
        # Get workflow components
        prompt = workflow.get('prompt', {})
        
        # Find SaveImage node
        save_node_id = None
        for node_id, node_data in prompt.items():
            if node_data.get('class_type') == 'SaveImage':
                save_node_id = node_id
                break
        
        if not save_node_id:
            print("SaveImage node not found, cannot inject face restoration")
            return workflow
        
        # Find the VAEDecode node that feeds into SaveImage
        vae_decode_node_id = None
        save_node_inputs = prompt[save_node_id].get('inputs', {})
        
        # Look for the VAEDecode node that feeds into SaveImage
        for node_id, node_data in prompt.items():
            if node_data.get('class_type') == 'VAEDecode':
                # Check if this VAEDecode's output is used by SaveImage
                for input_key, input_value in save_node_inputs.items():
                    if isinstance(input_value, list) and len(input_value) == 2:
                        if input_value[0] == node_id:
                            vae_decode_node_id = node_id
                            break
                if vae_decode_node_id:
                    break
        
        if not vae_decode_node_id:
            print("VAEDecode node not found, cannot inject face restoration")
            return workflow
        
        print(f"Found VAEDecode node: {vae_decode_node_id}")
        print(f"Found SaveImage node: {save_node_id}")
        
        # Generate unique node IDs
        model_loader_node_id = f"facerestore_model_loader_{len(prompt) + 1}"
        face_restore_node_id = f"face_restore_{len(prompt) + 2}"
        
        # Add FaceRestoreModelLoader node
        # Determine model name based on model type
        if model_type == 'codeformer':
            model_name = 'codeformer.pth'  # Default CodeFormer model
        elif model_type == 'gfpgan':
            model_name = 'GFPGANv1.4.pth'  # Default GFPGAN model
        else:
            model_name = 'codeformer.pth'  # Default to CodeFormer
        
        prompt[model_loader_node_id] = {
            "class_type": "FaceRestoreModelLoader",
            "inputs": {
                "model_name": model_name
            }
        }
        
        # Add FaceRestoreCFWithModel node
        # Use the appropriate weight based on model type
        fidelity_weight = codeformer_weight if model_type == 'codeformer' else gfpgan_weight
        
        prompt[face_restore_node_id] = {
            "class_type": "FaceRestoreCFWithModel",
            "inputs": {
                "facerestore_model": [model_loader_node_id, 0],
                "image": [vae_decode_node_id, 0],
                "facedetection": "retinaface_resnet50",
                "codeformer_fidelity": fidelity_weight
            }
        }
        
        # Update SaveImage to use the face restoration node output
        prompt[save_node_id]["inputs"]["images"] = [face_restore_node_id, 0]
        
        print(f"Added FaceRestoreModelLoader node: {model_loader_node_id}")
        print(f"Added FaceRestoreCFWithModel node: {face_restore_node_id}")
        print(f"Model: {model_name}")
        print(f"Fidelity weight: {fidelity_weight}")
        print("Face restoration parameters injected successfully!")
        return workflow
        
    except Exception as e:
        print(f"Error injecting face restoration parameters: {str(e)}")
        import traceback
        traceback.print_exc()
        return workflow

def inject_tiling_parameters(workflow, tiling_data):
    """
    Inject tiling parameters into the workflow by replacing VAEEncode and VAEDecode nodes
    with their tiled versions.
    
    Args:
        workflow (dict): The ComfyUI workflow
        tiling_data (dict): Tiling configuration from frontend
    
    Returns:
        dict: Updated workflow with tiling parameters
    """
    try:
        print("\nInjecting Tiling parameters:")
        print("-"*30)
        print(json.dumps(tiling_data, indent=2))
        print("-"*30)
        
        if not tiling_data.get('tiling', False):
            print("Tiling is disabled, skipping...")
            return workflow
        
        tile_size = tiling_data.get('tile_size', 512)
        tile_overlap = tiling_data.get('tile_overlap', 64)
        
        print(f"Tile size: {tile_size}")
        print(f"Tile overlap: {tile_overlap}")
        
        # Get workflow components
        prompt = workflow.get('prompt', {})
        
        # Find VAEEncode and VAEDecode nodes in a single iteration
        vae_encode_node_id = None
        vae_decode_node_id = None
        
        for node_id, node_data in prompt.items():
            class_type = node_data.get('class_type')
            if class_type == 'VAEEncode' and not vae_encode_node_id:
                vae_encode_node_id = node_id
            elif class_type == 'VAEDecode' and not vae_decode_node_id:
                vae_decode_node_id = node_id
            
            # Break early if both nodes found
            if vae_encode_node_id and vae_decode_node_id:
                break
        
        if not vae_encode_node_id:
            print("VAEEncode node not found, cannot inject tiling")
            return workflow
        
        if not vae_decode_node_id:
            print("VAEDecode node not found, cannot inject tiling")
            return workflow
        
        print(f"Found VAEEncode node: {vae_encode_node_id}")
        print(f"Found VAEDecode node: {vae_decode_node_id}")
        
        # Replace VAEEncode with VAEEncodeTiled
        vae_encode_inputs = prompt[vae_encode_node_id]["inputs"]
        prompt[vae_encode_node_id] = {
            "class_type": "VAEEncodeTiled",
            "inputs": {
                "pixels": vae_encode_inputs.get("pixels"),
                "vae": vae_encode_inputs.get("vae"),
                "tile_size": tile_size,
                "overlap": tile_overlap
            }
        }
        
        # Replace VAEDecode with VAEDecodeTiled
        vae_decode_inputs = prompt[vae_decode_node_id]["inputs"]
        prompt[vae_decode_node_id] = {
            "class_type": "VAEDecodeTiled",
            "inputs": {
                "samples": vae_decode_inputs.get("samples"),
                "vae": vae_decode_inputs.get("vae"),
                "tile_size": tile_size,
                "overlap": tile_overlap
            }
        }
        
        print(f"Replaced VAEEncode with VAEEncodeTiled: {vae_encode_node_id}")
        print(f"Replaced VAEDecode with VAEDecodeTiled: {vae_decode_node_id}")
        print(f"Tile size: {tile_size}")
        print(f"Tile overlap: {tile_overlap}")
        
        print("Tiling parameters injected successfully!")
        return workflow
        
    except Exception as e:
        print(f"Error injecting tiling parameters: {str(e)}")
        import traceback
        traceback.print_exc()
        return workflow

def inject_hires_fix_parameters(workflow, hires_fix_data):
    """
    Inject hires.fix (high-resolution) upscaling/refinement nodes into the workflow.
    Args:
        workflow (dict): The ComfyUI workflow
        hires_fix_data (dict): hires.fix configuration from frontend
    Returns:
        dict: Updated workflow with hires.fix nodes
    """
    try:
        print("\nInjecting Hires.fix parameters:")
        print("-"*40)
        print(json.dumps(hires_fix_data, indent=2))
        print("-"*40)
        if not hires_fix_data.get('hires_fix', False):
            print("Hires.fix is disabled, skipping...")
            return workflow

        # Add upscaler model mapping
        upscaler_model_map = {
            '4x-ultrasharp': '4x-UltraSharp.pth',
            # Add more mappings as needed
        }

        # Extract parameters
        upscale_method = hires_fix_data.get('hires_fix_upscale_method', 'upscale-by')
        upscale_factor = hires_fix_data.get('hires_fix_upscale_factor', 2.5)
        hires_steps = hires_fix_data.get('hires_fix_hires_steps', 1)
        denoising_strength = hires_fix_data.get('hires_fix_denoising_strength', 0.5)
        resize_width = hires_fix_data.get('hires_fix_resize_width', 4000)
        resize_height = hires_fix_data.get('hires_fix_resize_height', 4000)
        upscaler = hires_fix_data.get('hires_fix_upscaler', '4x-ultrasharp')
        upscaler = upscaler_model_map.get(upscaler, upscaler)

        prompt = workflow.get('prompt', {})

        # Find SaveImage node
        save_node_id = None
        for node_id, node_data in prompt.items():
            if node_data.get('class_type') == 'SaveImage':
                save_node_id = node_id
                break
        if not save_node_id:
            print("SaveImage node not found, cannot inject hires.fix")
            return workflow

        # Find the VAEDecode node that feeds into SaveImage
        vae_decode_node_id = None
        save_node_inputs = prompt[save_node_id].get('inputs', {})
        for node_id, node_data in prompt.items():
            if node_data.get('class_type') == 'VAEDecode':
                for input_key, input_value in save_node_inputs.items():
                    if isinstance(input_value, list) and len(input_value) == 2:
                        if input_value[0] == node_id:
                            vae_decode_node_id = node_id
                            break
                if vae_decode_node_id:
                    break
        if not vae_decode_node_id:
            print("VAEDecode node not found, cannot inject hires.fix")
            return workflow

        # Generate unique node IDs
        upscaler_loader_node_id = f"upscaler_model_loader_{len(prompt) + 1}"
        upscaler_node_id = f"upscale_with_model_{len(prompt) + 2}"
        hires_vae_encode_node_id = f"hires_vaeencode_{len(prompt) + 3}"
        hires_ksampler_node_id = f"hires_ksampler_{len(prompt) + 4}"
        hires_vae_decode_node_id = f"hires_vaedecode_{len(prompt) + 5}"

        # Add UpscaleModelLoader node
        prompt[upscaler_loader_node_id] = {
            "class_type": "UpscaleModelLoader",
            "inputs": {
                "model_name": upscaler
            }
        }
        # Add ImageUpscaleWithModel node
        prompt[upscaler_node_id] = {
            "class_type": "ImageUpscaleWithModel",
            "inputs": {
                "upscale_model": [upscaler_loader_node_id, 0],
                "image": [vae_decode_node_id, 0],
                # If using 'upscale-by', set factor; if 'resize-to', set width/height
                **({"upscale_by": upscale_factor} if upscale_method == "upscale-by" else {"width": resize_width, "height": resize_height})
            }
        }
        # Find required nodes in a single iteration for efficiency
        checkpoint_loader_node = None
        positive_conditioning_node = None
        negative_conditioning_node = None
        
        for node_id, node_data in prompt.items():
            class_type = node_data.get('class_type')
            
            if class_type == 'CheckpointLoaderSimple' and not checkpoint_loader_node:
                checkpoint_loader_node = node_id
            elif class_type == 'CLIPTextEncode':
                inputs = node_data.get('inputs', {})
                text_content = inputs.get('text', '').lower()
                if 'positive' in text_content and not positive_conditioning_node:
                    positive_conditioning_node = node_id
                elif 'negative' in text_content and not negative_conditioning_node:
                    negative_conditioning_node = node_id
            
            # Break early if all nodes found
            if checkpoint_loader_node and positive_conditioning_node and negative_conditioning_node:
                break
        
        # Add VAEEncode node (to convert upscaled image to latent)
        prompt[hires_vae_encode_node_id] = {
            "class_type": "VAEEncode",
            "inputs": {
                "pixels": [upscaler_node_id, 0],
                "vae": [checkpoint_loader_node or "4", 2]  # Use found node or fallback to "4"
            }
        }
        
        # Add a new KSampler for hires steps/denoising
        prompt[hires_ksampler_node_id] = {
            "class_type": "KSampler",
            "inputs": {
                "model": [checkpoint_loader_node or "4", 0],  # Use found checkpoint loader
                "positive": [positive_conditioning_node or "6", 0],
                "negative": [negative_conditioning_node or "7", 0],
                "latent_image": [hires_vae_encode_node_id, 0],
                "seed": 0,  # Could use a new random seed or reuse
                "steps": hires_steps,
                "cfg": 7.0,  # Could be parameterized
                "sampler_name": "euler",
                "scheduler": "normal",
                "denoise": denoising_strength
            }
        }
        # Add a new VAEDecode for the hires output
        prompt[hires_vae_decode_node_id] = {
            "class_type": "VAEDecode",
            "inputs": {
                "samples": [hires_ksampler_node_id, 0],
                "vae": [checkpoint_loader_node or "4", 2]
            }
        }
        # Update SaveImage to use the hires VAEDecode output
        prompt[save_node_id]["inputs"]["images"] = [hires_vae_decode_node_id, 0]

        print(f"Added UpscaleModelLoader node: {upscaler_loader_node_id}")
        print(f"Added ImageUpscaleWithModel node: {upscaler_node_id}")
        print(f"Added VAEEncode node: {hires_vae_encode_node_id}")
        print(f"Added hires KSampler node: {hires_ksampler_node_id}")
        print(f"Added hires VAEDecode node: {hires_vae_decode_node_id}")
        print("Hires.fix parameters injected successfully!")
        return workflow
    except Exception as e:
        print(f"Error injecting hires.fix parameters: {str(e)}")
        import traceback
        traceback.print_exc()
        return workflow

def inject_refiner_parameters(workflow, refiner_data):
    """
    Inject SDXL Refiner nodes into the workflow.
    Args:
        workflow (dict): The ComfyUI workflow
        refiner_data (dict): refiner configuration from frontend
    Returns:
        dict: Updated workflow with refiner nodes
    """
    try:
        print("\nInjecting Refiner parameters:")
        print("-"*40)
        print(json.dumps(refiner_data, indent=2))
        print("-"*40)
        if not refiner_data.get('refiner_enabled', False):
            print("Refiner is disabled, skipping...")
            return workflow

        refiner_model_map = {
            'sdxl-1.0': 'sd_xl_refiner_1.0.safetensors',
            'sdxl-0.9': 'sdxl_refiner_0.9.safetensors',
            'flux': 'flux_refiner.safetensors',
            'sdxl-turbo': 'sdxl_turbo_refiner.safetensors',
            'none': None
        }
        refiner_model = refiner_data.get('refiner_model', 'none')
        refiner_ckpt = refiner_model_map.get(refiner_model, None)
        switch_at = refiner_data.get('refiner_switch_at', 0.8)
        if not refiner_ckpt:
            print("No valid refiner model selected, skipping...")
            return workflow

        prompt = workflow.get('prompt', {})

        # Find SaveImage node
        save_node_id = None
        for node_id, node_data in prompt.items():
            if node_data.get('class_type') == 'SaveImage':
                save_node_id = node_id
                break
        if not save_node_id:
            print("SaveImage node not found, cannot inject refiner")
            return workflow

        # Find the VAEDecode node that feeds into SaveImage
        vae_decode_node_id = None
        save_node_inputs = prompt[save_node_id].get('inputs', {})
        for node_id, node_data in prompt.items():
            if node_data.get('class_type') == 'VAEDecode':
                for input_key, input_value in save_node_inputs.items():
                    if isinstance(input_value, list) and len(input_value) == 2:
                        if input_value[0] == node_id:
                            vae_decode_node_id = node_id
                            break
                if vae_decode_node_id:
                    break
        if not vae_decode_node_id:
            print("VAEDecode node not found, cannot inject refiner")
            return workflow

        # Generate unique node IDs
        refiner_loader_node_id = f"refiner_loader_{len(prompt) + 1}"
        refiner_vae_encode_node_id = f"refiner_vaeencode_{len(prompt) + 2}"
        refiner_ksampler_node_id = f"refiner_ksampler_{len(prompt) + 3}"
        refiner_vae_decode_node_id = f"refiner_vaedecode_{len(prompt) + 4}"

        # Add CheckpointLoaderSimple for refiner
        prompt[refiner_loader_node_id] = {
            "class_type": "CheckpointLoaderSimple",
            "inputs": {
                "ckpt_name": refiner_ckpt
            }
        }
        # Add VAEEncode node (to convert image to latent for refiner)
        prompt[refiner_vae_encode_node_id] = {
            "class_type": "VAEEncode",
            "inputs": {
                "pixels": [vae_decode_node_id, 0],
                "vae": [refiner_loader_node_id, 2]
            }
        }
        # Find conditioning nodes for refiner in a single iteration
        positive_conditioning_node = None
        negative_conditioning_node = None
        for node_id, node_data in prompt.items():
            if node_data.get('class_type') == 'CLIPTextEncode':
                inputs = node_data.get('inputs', {})
                text_content = inputs.get('text', '').lower()
                if 'positive' in text_content and not positive_conditioning_node:
                    positive_conditioning_node = node_id
                elif 'negative' in text_content and not negative_conditioning_node:
                    negative_conditioning_node = node_id
                
                # Break early if both nodes found
                if positive_conditioning_node and negative_conditioning_node:
                    break
        
        # Add KSampler for refiner
        prompt[refiner_ksampler_node_id] = {
            "class_type": "KSampler",
            "inputs": {
                "model": [refiner_loader_node_id, 0],
                "positive": [positive_conditioning_node or "6", 0],
                "negative": [negative_conditioning_node or "7", 0],
                "latent_image": [refiner_vae_encode_node_id, 0],
                "seed": 0,
                "steps": 10,  # You may want to parameterize this
                "cfg": 7.0,
                "sampler_name": "euler",
                "scheduler": "normal",
                "denoise": 1.0,
                "refiner_switch_at": switch_at
            }
        }
        # Add VAEDecode for refiner output
        prompt[refiner_vae_decode_node_id] = {
            "class_type": "VAEDecode",
            "inputs": {
                "samples": [refiner_ksampler_node_id, 0],
                "vae": [refiner_loader_node_id, 2]
            }
        }
        # Update SaveImage to use the refiner VAEDecode output
        prompt[save_node_id]["inputs"]["images"] = [refiner_vae_decode_node_id, 0]

        print(f"Added CheckpointLoaderSimple node: {refiner_loader_node_id}")
        print(f"Added VAEEncode node: {refiner_vae_encode_node_id}")
        print(f"Added refiner KSampler node: {refiner_ksampler_node_id}")
        print(f"Added refiner VAEDecode node: {refiner_vae_decode_node_id}")
        print("Refiner parameters injected successfully!")
        return workflow
    except Exception as e:
        print(f"Error injecting refiner parameters: {str(e)}")
        import traceback
        traceback.print_exc()
        return workflow