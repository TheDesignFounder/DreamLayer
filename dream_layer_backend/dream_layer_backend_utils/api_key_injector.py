"""
API Key Injector Utility

This module provides utilities to read API keys from environment variables
and inject them into ComfyUI workflows for API nodes.
"""

import os
import re
from dotenv import load_dotenv
from typing import Dict, Any, Union

# Debug mode - set DREAMLAYER_DEBUG=1 to enable verbose logging
_DEBUG = os.environ.get("DREAMLAYER_DEBUG", "").lower() in ("1", "true", "yes")

# Patterns that indicate sensitive values (case-insensitive key matching)
_SENSITIVE_KEY_PATTERNS = re.compile(
    r"(key|token|secret|api|bearer|password|credential|auth)", re.IGNORECASE
)

# Patterns for known API key formats (value matching)
_SENSITIVE_VALUE_PATTERNS = re.compile(
    r"(sk-[a-zA-Z0-9]{20,}|"  # OpenAI
    r"AIza[a-zA-Z0-9_-]{35}|"  # Google
    r"ghp_[a-zA-Z0-9]{36}|"  # GitHub
    r"AKIA[A-Z0-9]{16}|"  # AWS
    r"[a-zA-Z0-9_-]{32,})"  # Generic long tokens
)


def redact_secrets(obj: Union[Dict, list, str, Any], _depth: int = 0) -> Union[Dict, list, str, Any]:
    """
    Recursively walk dict/list/str and mask sensitive values.

    Masks values for keys containing: key, token, secret, api, bearer, password, credential, auth
    Also masks patterns like OpenAI sk-, Google AIza, GitHub ghp_, AWS AKIA

    Args:
        obj: The object to redact (dict, list, str, or any other type)
        _depth: Internal recursion depth tracker

    Returns:
        A copy of the object with sensitive values redacted
    """
    if _depth > 50:  # Prevent infinite recursion
        return "[REDACTED: max depth]"

    if isinstance(obj, dict):
        result = {}
        for key, value in obj.items():
            key_str = str(key).lower()
            if _SENSITIVE_KEY_PATTERNS.search(key_str):
                # This key looks sensitive - redact the value
                if isinstance(value, str) and len(value) > 0:
                    result[key] = f"[REDACTED:{len(value)} chars]"
                else:
                    result[key] = "[REDACTED]"
            else:
                result[key] = redact_secrets(value, _depth + 1)
        return result

    elif isinstance(obj, list):
        return [redact_secrets(item, _depth + 1) for item in obj]

    elif isinstance(obj, str):
        # Check if the string looks like an API key
        if _SENSITIVE_VALUE_PATTERNS.search(obj):
            return f"[REDACTED:{len(obj)} chars]"
        return obj

    else:
        return obj


def _debug_print(msg: str):
    """Print debug message only if DREAMLAYER_DEBUG is enabled."""
    if _DEBUG:
        print(f"[DEBUG] {msg}")

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
    
    # Gemini Nodes
    "GeminiNode": "GEMINI_API_KEY",
    "GeminiInputFiles": "GEMINI_API_KEY",
    "ComfyUI_NanoBanana": "GEMINI_API_KEY",
    
    # Luma Image Node (direct API)
    "LumaImageNode": "LUMA_API_KEY",
    
    # Existing ComfyUI Luma Nodes (use ComfyUI proxy)
    "LumaImageGenerationNode": "LUMA_API_KEY",
    "LumaImageModifyNode": "LUMA_API_KEY",
    "LumaTextToVideoGenerationNode": "LUMA_API_KEY",
    "LumaImageToVideoGenerationNode": "LUMA_API_KEY",
}

# Mapping of environment variable names to ComfyUI extra_data keys
ENV_KEY_TO_EXTRA_DATA_MAPPING = {
    "BFL_API_KEY": "api_key_comfy_org",
    "OPENAI_API_KEY": "api_key_comfy_org",
    "IDEOGRAM_API_KEY": "api_key_comfy_org",
    "STABILITY_API_KEY": "stability_api_key",  # Changed from COMFY_API_KEY
    "COMFY_API_KEY": "api_key_comfy_org",
    "COMFY_AUTH_TOKEN": "auth_token_comfy_org",
    "GEMINI_API_KEY": "api_key_comfy_org",
    "LUMA_API_KEY": "luma_api_key",  # Direct API key for Luma
    "RUNWAY_API_KEY": "api_key_comfy_org",
    # Future additions:
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
            _debug_print(f"Found {env_key}: [REDACTED]")
        else:
            _debug_print(f"No {env_key} found in environment")

    _debug_print(f"Total API keys loaded: {len(api_keys)}")
    return api_keys


def inject_api_keys_into_workflow(workflow: Dict[str, Any], all_api_keys: Dict[str, str] = None) -> Dict[str, Any]:
    """
    Inject API keys from environment variables into workflow extra_data based on nodes present.

    Args:
        workflow: The workflow dictionary to inject keys into
        all_api_keys: Optional dictionary of API keys. If None, reads from environment.

    Returns:
        Workflow with appropriate API keys added to extra_data
    """
    # Use passed API keys or read from environment if not provided
    if all_api_keys is None:
        all_api_keys = read_api_keys_from_env()

    # Create a copy to avoid modifying the original
    workflow_with_keys = workflow.copy()

    # Ensure extra_data exists
    if "extra_data" not in workflow_with_keys:
        workflow_with_keys["extra_data"] = {}
        _debug_print("Created new extra_data section")
    else:
        _debug_print("Using existing extra_data section")

    # Scan workflow for node types and determine which API keys are needed
    needed_env_keys = set()
    workflow_prompt = workflow.get('prompt', {})

    _debug_print("Scanning workflow for API nodes...")
    for node_id, node_data in workflow_prompt.items():
        if isinstance(node_data, dict):
            class_type = node_data.get('class_type')
            if class_type in NODE_TO_API_KEY_MAPPING:
                required_env_key = NODE_TO_API_KEY_MAPPING[class_type]
                needed_env_keys.add(required_env_key)
                _debug_print(f"Found {class_type} node - needs {required_env_key}")
    # Decide which key to use for api_key_comfy_org
    api_key_comfy_org = None
    _debug_print(f"needed_env_keys: {needed_env_keys}")
    _debug_print(f"all_api_keys keys: {list(all_api_keys.keys())}")
    if needed_env_keys:
        # If we have multiple keys that map to api_key_comfy_org, choose one
        # Priority: BFL_API_KEY first, then OPENAI_API_KEY, then IDEOGRAM_API_KEY, then GEMINI_API_KEY
        if "BFL_API_KEY" in needed_env_keys and "BFL_API_KEY" in all_api_keys:
            api_key_comfy_org = all_api_keys["BFL_API_KEY"]
            _debug_print("Using BFL_API_KEY for api_key_comfy_org")
        elif "OPENAI_API_KEY" in needed_env_keys and "OPENAI_API_KEY" in all_api_keys:
            api_key_comfy_org = all_api_keys["OPENAI_API_KEY"]
            _debug_print("Using OPENAI_API_KEY for api_key_comfy_org")
        elif "IDEOGRAM_API_KEY" in needed_env_keys and "IDEOGRAM_API_KEY" in all_api_keys:
            api_key_comfy_org = all_api_keys["IDEOGRAM_API_KEY"]
            _debug_print("Using IDEOGRAM_API_KEY for api_key_comfy_org")
        elif "GEMINI_API_KEY" in needed_env_keys and "GEMINI_API_KEY" in all_api_keys:
            api_key_comfy_org = all_api_keys["GEMINI_API_KEY"]
            _debug_print("Using GEMINI_API_KEY for api_key_comfy_org")
        else:
            _debug_print(f"No available API keys for needed services: {needed_env_keys}")

    # Add the chosen key to extra_data
    if api_key_comfy_org:
        workflow_with_keys["extra_data"]["api_key_comfy_org"] = api_key_comfy_org
        _debug_print("Injected api_key_comfy_org into workflow")

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
                _debug_print(f"Injected stability_api_key for {class_type}")
            else:
                _debug_print(f"STABILITY_API_KEY not found for {class_type}")

    if not has_stability_nodes:
        _debug_print("No Stability AI nodes found in workflow")

    # Special handling for Luma nodes - inject luma_api_key as hidden input
    has_luma_nodes = False
    for node_id, node_data in workflow.get("prompt", {}).items():
        class_type = node_data.get("class_type", "")
        if class_type.startswith("Luma"):
            has_luma_nodes = True
            # For Luma nodes, inject the luma API key as hidden input
            if "LUMA_API_KEY" in all_api_keys:
                luma_key = all_api_keys["LUMA_API_KEY"]
                # Ensure inputs section exists
                if "inputs" not in workflow_with_keys["prompt"][node_id]:
                    workflow_with_keys["prompt"][node_id]["inputs"] = {}
                # Add luma_api_key as hidden input
                workflow_with_keys["prompt"][node_id]["inputs"]["luma_api_key"] = luma_key
                _debug_print(f"Injected luma_api_key as hidden input for {class_type}")
            else:
                _debug_print(f"LUMA_API_KEY not found for {class_type}")

    if not has_luma_nodes:
        _debug_print("No Luma nodes found in workflow")

    # Log extra_data keys only (never log values which contain secrets)
    _debug_print(f"Final extra_data keys: {list(workflow_with_keys.get('extra_data', {}).keys())}")

    return workflow_with_keys
