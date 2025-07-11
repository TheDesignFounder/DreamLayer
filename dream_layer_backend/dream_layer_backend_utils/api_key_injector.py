"""
API Key Injector Utility

This module provides utilities to read API keys from environment variables
and inject them into ComfyUI workflows for API nodes.
"""

import os
from dotenv import load_dotenv
from typing import Dict, Any

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
    
    # Gemini Nodes
    "GeminiImageNode": "GEMINI_API_KEY",
    "GeminiTextNode": "GEMINI_API_KEY",
    "GeminiVisionNode": "GEMINI_API_KEY",
    "GeminiProNode": "GEMINI_API_KEY",
    "GeminiFlashNode": "GEMINI_API_KEY",
    
    # Anthropic Nodes  
    "AnthropicClaudeNode": "ANTHROPIC_API_KEY",
    "AnthropicSonnetNode": "ANTHROPIC_API_KEY",
    "AnthropicHaikuNode": "ANTHROPIC_API_KEY",
    "AnthropicOpusNode": "ANTHROPIC_API_KEY",
    "ClaudeImageNode": "ANTHROPIC_API_KEY",
}

# Mapping of environment variable names to ComfyUI extra_data keys
ENV_KEY_TO_EXTRA_DATA_MAPPING = {
    "BFL_API_KEY": "api_key_comfy_org",
    "OPENAI_API_KEY": "api_key_comfy_org",
    "IDEOGRAM_API_KEY": "api_key_comfy_org",
    # New API integrations:
    "GEMINI_API_KEY": "api_key_gemini",
    "ANTHROPIC_API_KEY": "api_key_anthropic",
}

def read_api_keys_from_env() -> Dict[str, str]:
    """
    Read all API keys from environment variables.
    
    Returns:
        Dict containing environment variable names mapped to their values.
        Example: {"BFL_API_KEY": "sk-bfl-...", "OPENAI_API_KEY": "sk-openai-..."}
    """
    # Get the path to the project's root directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_dir))
    
    # Construct the path to the .env file in the root directory
    dotenv_path = os.path.join(project_root, '.env')
    
    # Load environment variables from the .env file in the project root
    load_dotenv(dotenv_path=dotenv_path)
    
    api_keys = {}
    
    # Read all API keys defined in the mapping
    for env_key in ENV_KEY_TO_EXTRA_DATA_MAPPING.keys():
        api_key = os.getenv(env_key)
        if api_key:
            api_keys[env_key] = api_key
            # Safely truncate for display without assuming length
            display_key = api_key[:8] + "..." + api_key[-4:] if len(api_key) > 12 else api_key
            print(f"[DEBUG] Found {env_key}: {display_key}")
        else:
            print(f"[DEBUG] No {env_key} found in environment")
    
    print(f"[DEBUG] Total API keys loaded: {len(api_keys)}")
    return api_keys


def inject_api_keys_into_workflow(workflow: Dict[str, Any]) -> Dict[str, Any]:
    """
    Inject API keys from environment variables into workflow extra_data based on nodes present.
    
    Args:
        workflow: The workflow dictionary to inject keys into
        
    Returns:
        Workflow with appropriate API keys added to extra_data
    """
    # Read all available API keys from environment
    all_api_keys = read_api_keys_from_env()
    
    # Create a copy to avoid modifying the original
    workflow_with_keys = workflow.copy()
    
    # Ensure extra_data exists
    if "extra_data" not in workflow_with_keys:
        workflow_with_keys["extra_data"] = {}
        print("[DEBUG] Created new extra_data section")
    else:
        print("[DEBUG] Using existing extra_data section")
    
    # Scan workflow for node types and determine which API keys are needed
    needed_env_keys = set()
    workflow_prompt = workflow.get('prompt', {})
    
    print("[DEBUG] Scanning workflow for API nodes...")
    for node_id, node_data in workflow_prompt.items():
        if isinstance(node_data, dict):
            class_type = node_data.get('class_type')
            if class_type in NODE_TO_API_KEY_MAPPING:
                required_env_key = NODE_TO_API_KEY_MAPPING[class_type]
                needed_env_keys.add(required_env_key)
                print(f"[DEBUG] Found {class_type} node - needs {required_env_key}")
    # Inject all needed API keys into extra_data
    print(f"[DEBUG] needed_env_keys: {needed_env_keys}")
    print(f"[DEBUG] all_api_keys keys: {all_api_keys.keys()}")
    
    keys_injected = 0
    
    if needed_env_keys:
        # Group keys by their destination in extra_data
        comfy_org_keys = []
        other_keys = []
        
        for env_key in needed_env_keys:
            if env_key in all_api_keys:
                extra_data_key = ENV_KEY_TO_EXTRA_DATA_MAPPING[env_key]
                if extra_data_key == "api_key_comfy_org":
                    comfy_org_keys.append(env_key)
                else:
                    other_keys.append((env_key, extra_data_key))
        
        # Handle api_key_comfy_org (choose one with priority)
        if comfy_org_keys:
            # Priority: BFL_API_KEY first, then OPENAI_API_KEY, then IDEOGRAM_API_KEY
            chosen_key = None
            if "BFL_API_KEY" in comfy_org_keys:
                chosen_key = "BFL_API_KEY"
            elif "OPENAI_API_KEY" in comfy_org_keys:
                chosen_key = "OPENAI_API_KEY"
            elif "IDEOGRAM_API_KEY" in comfy_org_keys:
                chosen_key = "IDEOGRAM_API_KEY"
            
            if chosen_key:
                workflow_with_keys["extra_data"]["api_key_comfy_org"] = all_api_keys[chosen_key]
                print(f"[DEBUG] Using {chosen_key} for api_key_comfy_org")
                keys_injected += 1
        
        # Handle dedicated API keys (Gemini, Anthropic, etc.)
        for env_key, extra_data_key in other_keys:
            workflow_with_keys["extra_data"][extra_data_key] = all_api_keys[env_key]
            print(f"[DEBUG] Injected {env_key} as {extra_data_key}")
            keys_injected += 1
    
    # Summary
    if keys_injected > 0:
        print(f"[DEBUG] Successfully injected {keys_injected} API key(s) into workflow")
    else:
        print("[DEBUG] No API keys needed for this workflow")
    
    print(f"[DEBUG] Final extra_data: {workflow_with_keys['extra_data']}")
    
    return workflow_with_keys 