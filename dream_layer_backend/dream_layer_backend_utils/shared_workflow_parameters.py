import json
import os   


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
        
        # For now, handle the first unit (can be extended for multiple units)
        unit = units[0]
        
        # Find ControlNet nodes in the workflow
        prompt = workflow.get('prompt', {})
        
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
                    control_type_mapping = {
                        'openpose': 'openpose',
                        'canny': 'canny/lineart/anime_lineart/mlsd',
                        'depth': 'depth',
                        'normal': 'normal',
                        'segment': 'segment',
                        'tile': 'tile',
                        'repaint': 'repaint'
                    }
                    union_type = control_type_mapping.get(unit['control_type'], 'openpose')
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
        
        # Handle input image if provided
        print(f"🎯 Checking ControlNet image for unit {unit.get('unit_index', 0)}")
        print(f"🔍 Unit keys: {list(unit.keys())}")
        print(f"🔍 Unit input_image value: {unit.get('input_image')}")
        print(f"🔍 Unit input_image type: {type(unit.get('input_image'))}")
        print(f"🔍 Unit input_image is None: {unit.get('input_image') is None}")
        print(f"🔍 Unit input_image is empty string: {unit.get('input_image') == ''}")
        print(f"🔍 Unit input_image truthy: {bool(unit.get('input_image'))}")
        
        input_image_value = unit.get('input_image')
        if input_image_value is not None and input_image_value != '':
            print(f"🎯 Processing ControlNet image for unit {unit.get('unit_index', 0)}")
            print(f"📊 Input image data type: {type(unit['input_image'])}")
            
            # Check if it's a filename (already uploaded) or base64 data
            input_image = unit['input_image']
            
            if isinstance(input_image, str):
                # Check if it looks like a filename (not base64)
                if not input_image.startswith('data:image') and not input_image.startswith('/9j/') and len(input_image) < 1000:
                    # It's likely a filename
                    print(f"📁 Using provided filename: {input_image}")
                    saved_filename = input_image
                else:
                    # It's base64 data, save it
                    print(f"📏 Input image data length: {len(input_image)}")
                    print(f"🔍 Input image starts with: {input_image[:100]}...")
                    print("🔄 Converting base64 to file...")
                    saved_filename = save_controlnet_image(input_image, unit.get('unit_index', 0))
                    print(f"🔍 Save function returned: {saved_filename}")
            else:
                print(f"❌ Unsupported input image type: {type(input_image)}")
                saved_filename = None
            
            if saved_filename:
                print(f"✅ Image filename: {saved_filename}")
                # Find LoadImage node and update it
                print(f"🔍 Looking for LoadImage node in workflow...")
                print(f"🔍 Available nodes:")
                for node_id, node_data in prompt.items():
                    print(f"   Node {node_id}: {node_data.get('class_type', 'Unknown')}")
                
                for node_id, node_data in prompt.items():
                    if node_data.get('class_type') == 'LoadImage':
                        old_image = node_data['inputs'].get('image', 'None')
                        node_data['inputs']['image'] = saved_filename
                        print(f"🔄 Updated LoadImage node {node_id}:")
                        print(f"   Old image: {old_image}")
                        print(f"   New image: {saved_filename}")
                        break
                else:
                    print("❌ Warning: No LoadImage node found in workflow")
            else:
                print("❌ Failed to process ControlNet input image, creating test image")
                create_test_controlnet_image()
        else:
            print("ℹ️ No ControlNet input image provided - using existing test image")
            print("🔍 Unit keys:", list(unit.keys()))
            print("🔍 Unit input_image value:", unit.get('input_image'))
            # Don't create a new test image if one already exists
            test_image_path = "/Users/najeebkhan/dreamLayer/dream_layer_v1/ComfyUI/input/controlnet_input.png"
            if not os.path.exists(test_image_path):
                print("📁 Test image not found, creating one...")
                create_test_controlnet_image()
            else:
                print(f"✅ Test image exists: {test_image_path}")
        
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
    with their tiled versions. Always set temporal_overlap=4 and temporal_size=8 for images (minimum allowed).
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
        
        # Find VAEEncode and VAEDecode nodes (support both normal and tiled)
        vae_encode_node_id = None
        vae_decode_node_id = None
        
        for node_id, node_data in prompt.items():
            if node_data.get('class_type') in ['VAEEncode', 'VAEEncodeTiled']:
                vae_encode_node_id = node_id
            elif node_data.get('class_type') in ['VAEDecode', 'VAEDecodeTiled']:
                vae_decode_node_id = node_id
        
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
                "overlap": tile_overlap,
                "temporal_overlap": 4,  # minimum allowed
                "temporal_size": 8      # minimum allowed
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
                "overlap": tile_overlap,
                "temporal_overlap": 4,  # minimum allowed
                "temporal_size": 8      # minimum allowed
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
    Support both normal and tiled VAEDecode nodes.
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

        # Find the VAEDecode or VAEDecodeTiled node that feeds into SaveImage
        vae_decode_node_id = None
        save_node_inputs = prompt[save_node_id].get('inputs', {})
        for node_id, node_data in prompt.items():
            if node_data.get('class_type') in ['VAEDecode', 'VAEDecodeTiled']:
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
        # Add VAEEncode node (to convert upscaled image to latent)
        prompt[hires_vae_encode_node_id] = {
            "class_type": "VAEEncode",
            "inputs": {
                "pixels": [upscaler_node_id, 0],
                "vae": ["4", 2]  # Assumes CheckpointLoaderSimple is node 4
            }
        }
        # Add a new KSampler for hires steps/denoising
        prompt[hires_ksampler_node_id] = {
            "class_type": "KSampler",
            "inputs": {
                "model": ["4", 0],  # Assumes CheckpointLoaderSimple is node 4
                "positive": ["6", 0],
                "negative": ["7", 0],
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
                "vae": ["4", 2]
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
    Support both normal and tiled VAEDecode nodes.
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

        # Find the VAEDecode or VAEDecodeTiled node that feeds into SaveImage
        vae_decode_node_id = None
        save_node_inputs = prompt[save_node_id].get('inputs', {})
        for node_id, node_data in prompt.items():
            if node_data.get('class_type') in ['VAEDecode', 'VAEDecodeTiled']:
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
        # Add KSampler for refiner
        prompt[refiner_ksampler_node_id] = {
            "class_type": "KSampler",
            "inputs": {
                "model": [refiner_loader_node_id, 0],
                "positive": ["6", 0],
                "negative": ["7", 0],
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