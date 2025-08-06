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
    # Stability AI Nodes - Use direct API key
    "StabilityStableImageUltraNode": "STABILITY_API_KEY",
    "StabilityStableImageSD_3_5Node": "STABILITY_API_KEY",
    "StabilityUpscaleConservativeNode": "STABILITY_API_KEY",
    "StabilityUpscaleCreativeNode": "STABILITY_API_KEY",
    "StabilityUpscaleFastNode": "STABILITY_API_KEY",
}

# Mapping of environment variable names to ComfyUI extra_data keys
ENV_KEY_TO_EXTRA_DATA_MAPPING = {
    "BFL_API_KEY": "api_key_comfy_org",
    "OPENAI_API_KEY": "api_key_comfy_org",
    "IDEOGRAM_API_KEY": "api_key_comfy_org",
    "STABILITY_API_KEY": "stability_api_key",  # Changed from COMFY_API_KEY
    "COMFY_API_KEY": "api_key_comfy_org",
    "COMFY_AUTH_TOKEN": "auth_token_comfy_org",
    # Future additions:
    # "GEMINI_API_KEY": "api_key_gemini",
    # "ANTHROPIC_API_KEY": "api_key_anthropic",
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
            display_key = api_key[:8] + "..." + \
                api_key[-4:] if len(api_key) > 12 else api_key
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
                print(
                    f"[DEBUG] Found {class_type} node - needs {required_env_key}")
    # Decide which key to use for api_key_comfy_org
    api_key_comfy_org = None
    print(f"[DEBUG] needed_env_keys: {needed_env_keys}")
    print(f"[DEBUG] all_api_keys keys: {all_api_keys.keys()}")
    if needed_env_keys:
        # If we have multiple keys that map to api_key_comfy_org, choose one
        # Priority: BFL_API_KEY first, then OPENAI_API_KEY, then IDEOGRAM_API_KEY
        if "BFL_API_KEY" in needed_env_keys and "BFL_API_KEY" in all_api_keys:
            api_key_comfy_org = all_api_keys["BFL_API_KEY"]
            print(f"[DEBUG] Using BFL_API_KEY for api_key_comfy_org")
        elif "OPENAI_API_KEY" in needed_env_keys and "OPENAI_API_KEY" in all_api_keys:
            api_key_comfy_org = all_api_keys["OPENAI_API_KEY"]
            print(f"[DEBUG] Using OPENAI_API_KEY for api_key_comfy_org")
        elif "IDEOGRAM_API_KEY" in needed_env_keys and "IDEOGRAM_API_KEY" in all_api_keys:
            api_key_comfy_org = all_api_keys["IDEOGRAM_API_KEY"]
            print(f"[DEBUG] Using IDEOGRAM_API_KEY for api_key_comfy_org")
        else:
            print(
                f"[DEBUG] No available API keys for needed services: {needed_env_keys}")

    # Add the chosen key to extra_data
    if api_key_comfy_org:
        workflow_with_keys["extra_data"]["api_key_comfy_org"] = api_key_comfy_org
        print(f"[DEBUG] Injected api_key_comfy_org into workflow")

    # Special handling for Stability AI nodes - inject stability_api_key directly
    has_stability_nodes = False
    for node_id, node_data in workflow.get("prompt", {}).items():
        class_type = node_data.get("class_type", "")
        if class_type.startswith("Stability"):
            has_stability_nodes = True
            # For Stability nodes, inject the stability API key directly
            if "STABILITY_API_KEY" in all_api_keys:
                stability_key = all_api_keys["STABILITY_API_KEY"]
                if "extra_data" not in workflow_with_keys:
                    workflow_with_keys["extra_data"] = {}
                workflow_with_keys["extra_data"]["stability_api_key"] = stability_key
                print(f"[DEBUG] Injected stability_api_key for {class_type}")
            else:
                print(f"[DEBUG] STABILITY_API_KEY not found for {class_type}")

    if not has_stability_nodes:
        print("[DEBUG] No Stability AI nodes found in workflow")

    print(f"[DEBUG] Final extra_data: {workflow_with_keys['extra_data']}")

    return workflow_with_keys
