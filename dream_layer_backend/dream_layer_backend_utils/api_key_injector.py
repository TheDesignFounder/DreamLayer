"""
API Key Injector Utility

This module provides utilities to read API keys from environment variables
and inject them into ComfyUI workflows for API nodes.
"""

import os
import json
import logging
from typing import Dict, List, Optional

# Set up logging
logger = logging.getLogger(__name__)

# Global mapping of node classes to their required API keys
NODE_TO_API_KEY_MAPPING = {
    # BFL Nodes (use direct API, but still need api_key_comfy_org for compatibility)
    "FluxProUltraImageNode": "BFL_API_KEY",
    "FluxKontextProImageNode": "BFL_API_KEY", 
    "FluxKontextMaxImageNode": "BFL_API_KEY",
    "FluxProImageNode": "BFL_API_KEY",
    "FluxProExpandNode": "BFL_API_KEY",
    "FluxProFillNode": "BFL_API_KEY", 
    "FluxProCannyNode": "BFL_API_KEY",
    "FluxProDepthNode": "BFL_API_KEY",
    
    # OpenAI Nodes (use ComfyUI proxy, need api_key_comfy_org)
    "OpenAIDalle2": "OPENAI_API_KEY",
    "OpenAIDalle3": "OPENAI_API_KEY", 
    "OpenAIGPTImage1": "OPENAI_API_KEY",
    "OpenAITextNode": "OPENAI_API_KEY",
    "OpenAIChatNode": "OPENAI_API_KEY",
    "OpenAIInputFiles": "OPENAI_API_KEY",  # Utility node, might not need key
    "OpenAIChatConfig": "OPENAI_API_KEY",  # Config node, might not need key

    # Ideogram Nodes
    "IdeogramV1": "IDEOGRAM_API_KEY",
    "IdeogramV2": "IDEOGRAM_API_KEY",
    "IdeogramV3": "IDEOGRAM_API_KEY",
}

# Mapping of environment variable names to ComfyUI extra_data keys
ENV_KEY_TO_EXTRA_DATA_MAPPING = {
    "BFL_API_KEY": "api_key_comfy_org",
    "OPENAI_API_KEY": "api_key_comfy_org",
    "IDEOGRAM_API_KEY": "api_key_comfy_org",
    # Future additions:
    # "GEMINI_API_KEY": "api_key_gemini",
    # "ANTHROPIC_API_KEY": "api_key_anthropic",
}

def load_api_keys_from_env() -> Dict[str, str]:
    """
    Load API keys from environment variables.
    
    Returns:
        Dict[str, str]: Dictionary mapping service names to API keys
    """
    api_keys = {}
    
    # Define environment variable mappings
    env_mappings = {
        'BFL_API_KEY': 'bfl',
        'OPENAI_API_KEY': 'openai', 
        'IDEOGRAM_API_KEY': 'ideogram',
        'LUMA_API_KEY': 'luma'
    }
    
    for env_key, service_name in env_mappings.items():
        api_key = os.environ.get(env_key)
        if api_key:
            api_keys[service_name] = api_key
            logger.debug(f"Found {env_key}: {display_key}")
        else:
            logger.debug(f"No {env_key} found in environment")
    
    logger.debug(f"Total API keys loaded: {len(api_keys)}")
    return api_keys

def inject_api_keys_into_workflow(workflow: Dict, api_keys: Dict[str, str]) -> Dict:
    """
    Inject API keys into workflow's extra_data section.
    
    Args:
        workflow (Dict): The workflow dictionary
        api_keys (Dict[str, str]): Available API keys
        
    Returns:
        Dict: Updated workflow with API keys injected
    """
    workflow_with_keys = workflow.copy()
    
    # Ensure extra_data section exists
    if 'extra_data' not in workflow_with_keys:
        workflow_with_keys['extra_data'] = {}
        logger.debug("Created new extra_data section")
    else:
        logger.debug("Using existing extra_data section")
    
    # Scan workflow for API nodes that need keys
    needed_env_keys = set()
    
    logger.debug("Scanning workflow for API nodes...")
    for node_id, node_data in workflow_with_keys.get('nodes', {}).items():
        class_type = node_data.get('class_type', '')
        
        # Map node types to required API keys
        if 'BFL' in class_type:
            needed_env_keys.add('BFL_API_KEY')
            logger.debug(f"Found {class_type} node - needs {needed_env_keys}")
        elif 'OpenAI' in class_type or 'DALL' in class_type:
            needed_env_keys.add('OPENAI_API_KEY')
            logger.debug(f"Found {class_type} node - needs {needed_env_keys}")
        elif 'Ideogram' in class_type:
            needed_env_keys.add('IDEOGRAM_API_KEY')
            logger.debug(f"Found {class_type} node - needs {needed_env_keys}")
        elif 'Luma' in class_type:
            needed_env_keys.add('LUMA_API_KEY')
            logger.debug(f"Found {class_type} node - needs {needed_env_keys}")
    
    logger.debug(f"needed_env_keys: {needed_env_keys}")
    logger.debug(f"all_api_keys keys: {all_api_keys.keys()}")
    
    # Check if we have the required API keys
    all_api_keys = load_api_keys_from_env()
    
    if 'BFL_API_KEY' in needed_env_keys and 'bfl' in all_api_keys:
        workflow_with_keys['extra_data']['api_key_comfy_org'] = all_api_keys['bfl']
        logger.debug(f"Using BFL_API_KEY for api_key_comfy_org")
    elif 'OPENAI_API_KEY' in needed_env_keys and 'openai' in all_api_keys:
        workflow_with_keys['extra_data']['api_key_comfy_org'] = all_api_keys['openai']
        logger.debug(f"Using OPENAI_API_KEY for api_key_comfy_org")
    elif 'IDEOGRAM_API_KEY' in needed_env_keys and 'ideogram' in all_api_keys:
        workflow_with_keys['extra_data']['api_key_comfy_org'] = all_api_keys['ideogram']
        logger.debug(f"Using IDEOGRAM_API_KEY for api_key_comfy_org")
    elif 'LUMA_API_KEY' in needed_env_keys and 'luma' in all_api_keys:
        workflow_with_keys['extra_data']['api_key_comfy_org'] = all_api_keys['luma']
        logger.debug(f"Using LUMA_API_KEY for api_key_comfy_org")
    else:
        logger.warning(f"No available API keys for needed services: {needed_env_keys}")
    
    if 'api_key_comfy_org' in workflow_with_keys['extra_data']:
        logger.debug(f"Injected api_key_comfy_org into workflow")
    else:
        logger.debug("No API keys needed for this workflow")
    
    logger.debug(f"Final extra_data: {workflow_with_keys['extra_data']}")
    return workflow_with_keys 