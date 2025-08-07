"""
Workflow Loader Utility

This module provides utilities to dynamically load workflows from the workflows directory
and inject user parameters into them.
"""

import os
import json
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


def _determine_workflow_path(workflow_request: Dict[str, Any]) -> str:
    """Determine the workflow file path based on request parameters."""
    generation_flow = workflow_request.get('generation_flow')
    # Convert to lowercase for case-insensitive comparison
    model_name = workflow_request.get('model_name', '').lower()
    controlnet = workflow_request.get('controlnet', False)
    lora = workflow_request.get('lora', False)

    # Determine workflow filename based on parameters
    if 'bfl' in model_name or 'flux' in model_name:
        filename = "bfl_core_generation_workflow.json"
    elif 'dalle' in model_name:
        filename = "dalle_core_generation_workflow.json"
    elif 'ideogram' in model_name:  # Changed to check if 'ideogram' is in model_name
        filename = "ideogram_core_generation_workflow.json"
    elif 'stability' in model_name:
        filename = "stability_core_generation_workflow.json"
    elif controlnet and lora:
        filename = "local_controlnet_lora.json"
    elif controlnet:
        filename = "local_controlnet.json"
    elif lora:
        filename = "local_lora.json"
    else:
        filename = "core_generation_workflow.json"

    # Build full path
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    workflow_path = os.path.join(
        current_dir, 'workflows', generation_flow, filename)

    if not os.path.exists(workflow_path):
        raise FileNotFoundError(f"Workflow file not found: {workflow_path}")

    return workflow_path


def _load_workflow_json(workflow_path: str) -> Dict[str, Any]:
    """Load and parse workflow JSON file."""
    with open(workflow_path, 'r') as file:
        return json.load(file)


def load_workflow(workflow_request: Dict[str, Any]) -> Dict[str, Any]:
    """
    Load and configure a workflow based on the request parameters.

    Args:
        workflow_request: Dictionary containing:
            - generation_flow: txt2img/img2img
            - model_name: bfl/dalle/other
            - controlnet: true/false
            - lora: true/false

    Returns:
        Dict: Loaded workflow configuration
    """
    try:
        workflow_path = _determine_workflow_path(workflow_request)
        workflow = _load_workflow_json(workflow_path)
        logger.info(f"Successfully loaded workflow: {workflow_path}")
        return workflow
    except Exception as e:
        logger.error(f"Error loading workflow: {str(e)}")
        raise


def analyze_workflow(workflow: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze workflow to determine batch size and if it uses API nodes."""
    is_api = bool(workflow.get('extra_data'))
    batch_size = next((node['inputs'].get('batch_size', 1) for node in workflow.get(
        'prompt', {}).values() if 'batch_size' in node.get('inputs', {})), 1)
    return {'batch_size': batch_size, 'is_api': is_api}
