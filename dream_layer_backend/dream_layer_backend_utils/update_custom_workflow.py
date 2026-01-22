import json
import logging
import copy
import os

logger = logging.getLogger(__name__)

# Debug mode - set DREAMLAYER_DEBUG=1 to enable verbose logging
_DEBUG = os.environ.get("DREAMLAYER_DEBUG", "").lower() in ("1", "true", "yes")

def update_custom_workflow(original_workflow, custom_workflow):
    """
    Update a custom workflow by injecting hardcoded values from the original workflow.
    Only updates specific fields that are normally hardcoded, preserving the custom workflow structure.
    
    Args:
        original_workflow (dict): The original workflow with hardcoded values
        custom_workflow (dict): The uploaded custom workflow JSON
    
    Returns:
        dict: Updated workflow with hardcoded values injected
    """
    try:
        # Create a deep copy of the custom workflow to avoid modifying the original
        updated_workflow = copy.deepcopy(custom_workflow)
        
        # Log the incoming data for debugging
        logger.info("Injecting hardcoded values into custom workflow")
        logger.info(f"Original workflow keys: {list(original_workflow.keys())}")
        logger.info(f"Custom workflow keys: {list(updated_workflow.keys())}")
        
        # Update specific hardcoded fields in the custom workflow
        updated_workflow = inject_hardcoded_values(updated_workflow, original_workflow)
        
        logger.info("Custom workflow updated successfully")
        if _DEBUG:
            # Import here to avoid circular imports
            from dream_layer_backend_utils.api_key_injector import redact_secrets
            logger.info("Updated workflow is:")
            logger.info(json.dumps(redact_secrets(updated_workflow), indent=2))
        
        return updated_workflow
        
    except Exception as e:
        logger.error(f"Error updating custom workflow: {str(e)}")
        raise

def inject_hardcoded_values(custom_workflow, original_workflow):
    """
    Inject specific hardcoded values from original workflow into custom workflow.
    Uses a generic approach that works with any node type by looking for specific field names.
    
    Args:
        custom_workflow (dict): The custom workflow to update
        original_workflow (dict): The original workflow with hardcoded values
    
    Returns:
        dict: Updated custom workflow
    """
    try:
        custom_prompt = custom_workflow.get('prompt', {})
        original_prompt = original_workflow.get('prompt', {})
        
        # Extract hardcoded values from original workflow
        hardcoded_values = extract_hardcoded_values(original_prompt)
        logger.info(f"Extracted hardcoded values: {hardcoded_values}")
        
        # Find KSampler node to determine positive/negative prompt connections (for text field mapping)
        ksampler_node = None
        for node_id, node_data in custom_prompt.items():
            if node_data.get('class_type') == 'KSampler':
                ksampler_node = node_id
                break
        
        # Map positive and negative prompt nodes based on KSampler connections
        positive_prompt_node = None
        negative_prompt_node = None
        
        if ksampler_node:
            ksampler_inputs = custom_prompt[ksampler_node].get('inputs', {})
            positive_input = ksampler_inputs.get('positive')
            negative_input = ksampler_inputs.get('negative')
            
            if positive_input and isinstance(positive_input, list) and len(positive_input) > 0:
                positive_prompt_node = str(positive_input[0])
            if negative_input and isinstance(negative_input, list) and len(negative_input) > 0:
                negative_prompt_node = str(negative_input[0])
        
        logger.info(f"Positive prompt node: {positive_prompt_node}")
        logger.info(f"Negative prompt node: {negative_prompt_node}")
        
        # Generic field matching - works with any node type
        for node_id, node_data in custom_prompt.items():
            if not isinstance(node_data, dict):
                continue
                
            class_type = node_data.get('class_type')
            inputs = node_data.get('inputs', {})
            
            # Update prompt fields (could be 'prompt' or 'text')
            if 'prompt' in inputs and 'prompt' in hardcoded_values:
                inputs['prompt'] = hardcoded_values['prompt']
                logger.info(f"Updated prompt in node {node_id} ({class_type}): {hardcoded_values['prompt']}")
                
            # Handle text fields (for CLIPTextEncode nodes and similar)
            if 'text' in inputs and 'prompt' in hardcoded_values:
                # Determine if this is positive or negative prompt based on KSampler connections
                if node_id == positive_prompt_node:
                    inputs['text'] = hardcoded_values['prompt']
                    logger.info(f"Updated positive text in node {node_id} ({class_type}): {hardcoded_values['prompt']}")
                elif node_id == negative_prompt_node:
                    inputs['text'] = hardcoded_values.get('negative_prompt', inputs['text'])
                    logger.info(f"Updated negative text in node {node_id} ({class_type}): {hardcoded_values.get('negative_prompt', '')}")
                else:
                    # Fallback: determine based on content or node naming
                    current_text = inputs.get('text', '')
                    if 'negative' in current_text.lower() or 'ugly' in current_text.lower() or node_id.endswith('_negative'):
                        inputs['text'] = hardcoded_values.get('negative_prompt', current_text)
                        logger.info(f"Updated negative text in node {node_id} ({class_type}) (fallback): {hardcoded_values.get('negative_prompt', current_text)}")
                    else:
                        inputs['text'] = hardcoded_values.get('prompt', current_text)
                        logger.info(f"Updated positive text in node {node_id} ({class_type}) (fallback): {hardcoded_values.get('prompt', current_text)}")
            
            # Update common sampling parameters
            if 'steps' in inputs and 'steps' in hardcoded_values:
                inputs['steps'] = hardcoded_values['steps']
                logger.info(f"Updated steps in node {node_id} ({class_type}): {hardcoded_values['steps']}")
                
            if 'cfg' in inputs and 'cfg_scale' in hardcoded_values:
                inputs['cfg'] = hardcoded_values['cfg_scale']
                logger.info(f"Updated cfg in node {node_id} ({class_type}): {hardcoded_values['cfg_scale']}")
                
            if 'seed' in inputs and 'seed' in hardcoded_values:
                inputs['seed'] = hardcoded_values['seed']
                logger.info(f"Updated seed in node {node_id} ({class_type}): {hardcoded_values['seed']}")
                
            if 'sampler_name' in inputs and 'sampler_name' in hardcoded_values:
                inputs['sampler_name'] = hardcoded_values['sampler_name']
                logger.info(f"Updated sampler_name in node {node_id} ({class_type}): {hardcoded_values['sampler_name']}")
                
            if 'scheduler' in inputs and 'scheduler' in hardcoded_values:
                inputs['scheduler'] = hardcoded_values['scheduler']
                logger.info(f"Updated scheduler in node {node_id} ({class_type}): {hardcoded_values['scheduler']}")
                
            if 'denoise' in inputs and 'denoising_strength' in hardcoded_values:
                inputs['denoise'] = hardcoded_values['denoising_strength']
                logger.info(f"Updated denoise in node {node_id} ({class_type}): {hardcoded_values['denoising_strength']}")
                
            # Update image dimensions
            if 'width' in inputs and 'width' in hardcoded_values:
                inputs['width'] = hardcoded_values['width']
                logger.info(f"Updated width in node {node_id} ({class_type}): {hardcoded_values['width']}")
                
            if 'height' in inputs and 'height' in hardcoded_values:
                inputs['height'] = hardcoded_values['height']
                logger.info(f"Updated height in node {node_id} ({class_type}): {hardcoded_values['height']}")
                
            # Update model/checkpoint names
            if 'ckpt_name' in inputs and 'ckpt_name' in hardcoded_values:
                inputs['ckpt_name'] = hardcoded_values['ckpt_name']
                logger.info(f"Updated ckpt_name in node {node_id} ({class_type}): {hardcoded_values['ckpt_name']}")
                
            # Update image paths
            if 'image' in inputs and 'input_image_path' in hardcoded_values:
                inputs['image'] = hardcoded_values['input_image_path']
                logger.info(f"Updated image in node {node_id} ({class_type}): {hardcoded_values['input_image_path']}")
        
        return custom_workflow
        
    except Exception as e:
        logger.error(f"Error injecting hardcoded values: {str(e)}")
        return custom_workflow

def extract_hardcoded_values(original_prompt):
    """
    Extract hardcoded values from the original workflow.
    
    Args:
        original_prompt (dict): The prompt section of the original workflow
    
    Returns:
        dict: Dictionary of hardcoded values
    """
    hardcoded_values = {}
    
    try:
        # Find KSampler node to determine positive/negative prompt connections
        ksampler_node = None
        for node_id, node_data in original_prompt.items():
            if node_data.get('class_type') == 'KSampler':
                ksampler_node = node_id
                break
        
        # Map positive and negative prompt nodes based on KSampler connections
        positive_prompt_node = None
        negative_prompt_node = None
        
        if ksampler_node:
            ksampler_inputs = original_prompt[ksampler_node].get('inputs', {})
            positive_input = ksampler_inputs.get('positive')
            negative_input = ksampler_inputs.get('negative')
            
            if positive_input and isinstance(positive_input, list) and len(positive_input) > 0:
                positive_prompt_node = str(positive_input[0])
            if negative_input and isinstance(negative_input, list) and len(negative_input) > 0:
                negative_prompt_node = str(negative_input[0])
        
        logger.info(f"Extracting - Positive prompt node: {positive_prompt_node}")
        logger.info(f"Extracting - Negative prompt node: {negative_prompt_node}")
        
        for node_id, node_data in original_prompt.items():
            if not isinstance(node_data, dict):
                continue
                
            class_type = node_data.get('class_type')
            inputs = node_data.get('inputs', {})
            
            if class_type == 'CheckpointLoaderSimple':
                hardcoded_values['ckpt_name'] = inputs.get('ckpt_name')
                
            elif class_type == 'CLIPTextEncode':
                text = inputs.get('text', '')
                # Determine if this is positive or negative prompt based on KSampler connections
                if node_id == positive_prompt_node:
                    hardcoded_values['prompt'] = text
                    logger.info(f"Extracted positive prompt from node {node_id}: {text}")
                elif node_id == negative_prompt_node:
                    hardcoded_values['negative_prompt'] = text
                    logger.info(f"Extracted negative prompt from node {node_id}: {text}")
                else:
                    # Fallback to old logic for edge cases
                    if 'negative' in text.lower() or 'ugly' in text.lower():
                        hardcoded_values['negative_prompt'] = text
                        logger.info(f"Extracted negative prompt from node {node_id} (fallback): {text}")
                    else:
                        hardcoded_values['prompt'] = text
                        logger.info(f"Extracted positive prompt from node {node_id} (fallback): {text}")
                    
            elif class_type == 'KSampler':
                hardcoded_values['steps'] = inputs.get('steps')
                hardcoded_values['cfg_scale'] = inputs.get('cfg')
                hardcoded_values['seed'] = inputs.get('seed')
                hardcoded_values['sampler_name'] = inputs.get('sampler_name')
                hardcoded_values['scheduler'] = inputs.get('scheduler')
                hardcoded_values['denoising_strength'] = inputs.get('denoise')
                
            elif class_type == 'ImageScale':
                hardcoded_values['width'] = inputs.get('width')
                hardcoded_values['height'] = inputs.get('height')
                
            elif class_type == 'EmptyLatentImage':
                hardcoded_values['width'] = inputs.get('width')
                hardcoded_values['height'] = inputs.get('height')
                
            elif class_type == 'LoadImage':
                hardcoded_values['input_image_path'] = inputs.get('image')
                
    except Exception as e:
        logger.error(f"Error extracting hardcoded values: {str(e)}")
        
    return hardcoded_values

def override_workflow(original_workflow, core_generation_settings):
    """
    Override values in the original workflow with those from core_generation_settings.
    Recursively searches through the entire workflow structure and replaces matching field names.
    Uses standardized template values ("beautiful"/"ugly") for prompt identification.
    
    Args:
        original_workflow (dict): The workflow to update
        core_generation_settings (dict): Dictionary containing values to override
    
    Returns:
        dict: Updated workflow with overridden values
    """
    try:
        # Create a deep copy to avoid modifying the original
        updated_workflow = copy.deepcopy(original_workflow)
        
        logger.info("Overriding workflow with core generation settings")
        logger.info(f"Core generation settings: {core_generation_settings}")
        
        def recursive_override(obj, path=""):
            """Recursively search and replace values in nested dictionaries/lists"""
            if isinstance(obj, dict):
                for key, value in obj.items():
                    current_path = f"{path}.{key}" if path else key
                    
                    # Handle prompt fields (for DALL-E/BFL workflows)
                    if key == 'prompt' and isinstance(value, str):
                        if value == 'beautiful' and 'prompt' in core_generation_settings:
                            obj[key] = core_generation_settings['prompt']
                            logger.info(f"Updated prompt at {current_path}: {core_generation_settings['prompt']}")
                    
                    # Handle text fields (for local ComfyUI workflows)
                    elif key == 'text' and isinstance(value, str):
                        if value == 'beautiful' and 'prompt' in core_generation_settings:
                            obj[key] = core_generation_settings['prompt']
                            logger.info(f"Updated positive text at {current_path}: {core_generation_settings['prompt']}")
                        elif value == 'ugly' and 'negative_prompt' in core_generation_settings:
                            obj[key] = core_generation_settings['negative_prompt']
                            logger.info(f"Updated negative text at {current_path}: {core_generation_settings['negative_prompt']}")
                    
                    # Handle other direct field mappings
                    elif key in core_generation_settings:
                        # Map cfg_scale to cfg
                        if key == 'cfg' and 'cfg' in core_generation_settings:
                            obj[key] = core_generation_settings['cfg']
                            logger.info(f"Updated {key} at {current_path}: {core_generation_settings['cfg']}")
                        # Direct field matches
                        elif key in ['steps', 'seed', 'sampler_name', 'scheduler', 'denoise', 'ckpt_name', 'batch_size', 'height', 'width']:
                            obj[key] = core_generation_settings[key]
                            logger.info(f"Updated {key} at {current_path}: {core_generation_settings[key]}")
                    
                    # Continue recursing
                    recursive_override(value, current_path)
                    
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    recursive_override(item, f"{path}[{i}]")
        
        # Start the recursive override
        recursive_override(updated_workflow)
        
        logger.info("Workflow override completed successfully")
        return updated_workflow
        
    except Exception as e:
        logger.error(f"Error overriding workflow: {str(e)}")
        return original_workflow

def validate_custom_workflow(workflow):
    """
    Validate that the custom workflow has the required structure.
    
    Args:
        workflow (dict): The workflow to validate
    
    Returns:
        bool: True if valid, False otherwise
    """
    try:
        if not isinstance(workflow, dict):
            return False
            
        if 'prompt' not in workflow:
            return False
            
        if not isinstance(workflow['prompt'], dict):
            return False
            
        # Check if there are any nodes in the workflow
        if len(workflow['prompt']) == 0:
            return False
            
        return True
        
    except Exception as e:
        logger.error(f"Error validating custom workflow: {str(e)}")
        return False

def find_save_node(workflow):
    """
    Find the SaveImage node ID in the workflow.
    
    Args:
        workflow (dict): The workflow to search
    
    Returns:
        str: Node ID of the SaveImage node, or None if not found
    """
    try:
        prompt = workflow.get('prompt', {})
        
        for node_id, node_data in prompt.items():
            if isinstance(node_data, dict) and node_data.get('class_type') == 'SaveImage':
                logger.info(f"Found SaveImage node at ID: {node_id}")
                return node_id
        
        logger.warning("No SaveImage node found in workflow")
        return None
        
    except Exception as e:
        logger.error(f"Error finding SaveImage node: {str(e)}")
        return None

def update_image_paths_in_workflow(workflow, image_path):
    """
    Specifically handle updating image paths in LoadImage nodes.
    This function searches for all LoadImage nodes and updates their image input.
    
    Args:
        workflow (dict): The workflow to update
        image_path (str): The path to the input image (filename only for ComfyUI)
    
    Returns:
        dict: Updated workflow with correct image paths
    """
    try:
        logger.info(f"Updating image paths in workflow with: {image_path}")
        
        # Create a deep copy to avoid modifying the original
        updated_workflow = copy.deepcopy(workflow)
        prompt = updated_workflow.get('prompt', {})
        
        # Find all LoadImage nodes and update their image input
        updated_count = 0
        for node_id, node_data in prompt.items():
            if isinstance(node_data, dict) and node_data.get('class_type') == 'LoadImage':
                inputs = node_data.get('inputs', {})
                if 'image' in inputs:
                    old_image = inputs['image']
                    inputs['image'] = image_path
                    logger.info(f"Updated LoadImage node {node_id}: '{old_image}' -> '{image_path}'")
                    updated_count += 1
        
        if updated_count == 0:
            logger.warning("No LoadImage nodes found in workflow to update")
        else:
            logger.info(f"Successfully updated {updated_count} LoadImage node(s)")
        
        return updated_workflow
        
    except Exception as e:
        logger.error(f"Error updating image paths in workflow: {str(e)}")
        return workflow 