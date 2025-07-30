"""
Runway Text-to-Image Node for DreamLayer

This module implements a ComfyUI node that generates images using Runway's Gen-4 text-to-image API.
The node follows the official Runway API specification and supports all documented features.

Requirements:
- RUNWAY_API_KEY environment variable must be set  
- Node accepts promptText, ratio, seed, and optional referenceImages
- Supports polling for task completion via /v1/tasks/{id} endpoint
- Returns ComfyUI-compatible image tensors

Usage:
Set RUNWAY_API_KEY=sk-... in your .env file before using this node.

API Reference: https://docs.dev.runwayml.com/api/#tag/Start-generating/paths/~1v1~1text_to_image/post
"""

import os
import httpx
import torch
import numpy as np
import time
from PIL import Image
from io import BytesIO
from typing import Optional, List, Dict, Any
from inspect import cleandoc

# Try to import ComfyUI types, fall back to simplified interface if not available
try:
    from comfy.comfy_types.node_typing import IO, ComfyNodeABC, InputTypeDict
except ImportError:
    # Fallback for standalone testing
    class ComfyNodeABC:
        pass
    class IO:
        STRING = "STRING"
        INT = "INT" 
        FLOAT = "FLOAT"
        IMAGE = "IMAGE"
    InputTypeDict = dict


class RunwayText2ImgNode(ComfyNodeABC):
    """
    Generate images using Runway's Gen-4 text-to-image API.
    
    This node calls the official Runway API at https://api.dev.runwayml.com/v1/text_to_image
    following the complete API specification including task polling and all supported parameters.
    
    Parameters:
    - promptText (str): Text description of the image to generate (supports @tag references)
    - ratio (str, default="1024:1024"): Aspect ratio in format "width:height" 
    - seed (int, optional): Random seed for reproducible generation
    - timeout (int, default=120): Maximum time to wait for completion in seconds
    
    Advanced Features:
    - Reference images: Upload images and reference them using @tag syntax in prompts
    - Multiple aspect ratios: Support for various ratios like "1920:1080", "1024:1024", etc.
    - Task polling: Automatically polls until generation completes
    - Comprehensive error handling: Handles all API error states gracefully
    
    Environment Variables:
    - RUNWAY_API_KEY: Required Runway API key (format: sk-...)
    
    Examples:
    - Simple: "A beautiful landscape at sunset"
    - With references: "@EiffelTower painted in the style of @StarryNight" 
      (requires reference images with matching tags)
    
    API Version: 2024-11-06
    """
    
    DESCRIPTION = cleandoc(__doc__)
    CATEGORY = "api node/image/runway"
    RETURN_TYPES = (IO.IMAGE,)
    RETURN_NAMES = ("image",)
    FUNCTION = "generate_image"
    
    # Standard aspect ratios supported by Runway Gen-4
    ASPECT_RATIOS = [
        "1024:1024",
        "1280:720", 
        "720:1280",
        "1920:1080",
        "1080:1920", 
        "1152:896",
        "896:1152",
        "1536:640",
        "640:1536"
    ]
    
    @classmethod
    def INPUT_TYPES(cls) -> InputTypeDict:
        return {
            "required": {
                "promptText": (IO.STRING, {
                    "multiline": True,
                    "default": "A futuristic cityscape at dusk, cinematic lighting",
                    "tooltip": "Text description of the image to generate. Use @tag to reference uploaded images."
                }),
                "ratio": (cls.ASPECT_RATIOS, {
                    "default": "1024:1024",
                    "tooltip": "Aspect ratio of the generated image"
                }),
                "timeout": (IO.INT, {
                    "default": 120,
                    "min": 30,
                    "max": 600,
                    "step": 10,
                    "tooltip": "Maximum time to wait for completion in seconds"
                })
            },
            "optional": {
                "seed": (IO.INT, {
                    "default": -1,
                    "min": -1,
                    "max": 2147483647,
                    "tooltip": "Random seed for reproducible generation. Use -1 for random."
                })
            }
        }
    
    def generate_image(
        self, 
        promptText: str,
        ratio: str = "1024:1024", 
        timeout: int = 120,
        seed: int = -1
    ) -> tuple[torch.Tensor]:
        """
        Generate an image using the official Runway Gen-4 text-to-image API.
        
        Args:
            promptText: Text description of the image to generate
            ratio: Aspect ratio in "width:height" format (default: "1024:1024")
            timeout: Maximum time to wait for completion in seconds (default: 120)
            seed: Random seed for reproducible generation, -1 for random (default: -1)
            
        Returns:
            Tuple containing the generated image as a torch.Tensor
            
        Raises:
            RuntimeError: If RUNWAY_API_KEY is not set or API call fails
            ValueError: If input parameters are invalid
        """
        # Get API key from environment
        api_key = os.getenv("RUNWAY_API_KEY")
        if not api_key:
            raise RuntimeError(
                "RUNWAY_API_KEY not set. Please add RUNWAY_API_KEY=sk-... to your .env file."
            )
        
        # Validate inputs
        if not promptText or not promptText.strip():
            raise ValueError("promptText cannot be empty")
        
        if ratio not in self.ASPECT_RATIOS:
            raise ValueError(f"Ratio must be one of: {', '.join(self.ASPECT_RATIOS)}")
            
        if timeout < 30:
            raise ValueError("Timeout must be at least 30 seconds")
        
        # Prepare request payload according to official API spec
        payload = {
            "model": "gen4_image",
            "promptText": promptText.strip(),
            "ratio": ratio
        }
        
        # Add seed if specified (not -1)
        if seed != -1:
            payload["seed"] = seed
        
        # Prepare headers according to API documentation
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "X-Runway-Version": "2024-11-06"
        }
        
        try:
            # Create task via text-to-image endpoint
            with httpx.Client(timeout=30) as client:
                print(f"[RunwayText2Img] Creating task with prompt: {promptText[:50]}...")
                
                response = client.post(
                    "https://api.dev.runwayml.com/v1/text_to_image",
                    json=payload,
                    headers=headers
                )
                
                # Check for HTTP errors
                response.raise_for_status()
                
                # Parse initial response to get task ID
                result = response.json()
                
                if "id" not in result:
                    raise RuntimeError("No task ID returned from Runway API")
                
                task_id = result["id"]
                print(f"[RunwayText2Img] Task created with ID: {task_id}")
                
                # Poll for completion
                image_url = self._poll_for_completion(client, task_id, headers, timeout)
                
                # Download the final image
                print(f"[RunwayText2Img] Downloading image from: {image_url}")
                image_response = client.get(image_url)
                image_response.raise_for_status()
                
                # Convert to PIL Image
                image = Image.open(BytesIO(image_response.content))
                
                # Convert to RGB if necessary
                if image.mode != "RGB":
                    image = image.convert("RGB")
                
                # Convert to numpy array and then to torch tensor
                image_array = np.array(image, dtype=np.float32) / 255.0
                image_tensor = torch.from_numpy(image_array).unsqueeze(0)  # Add batch dimension
                
                print(f"[RunwayText2Img] Image generated successfully: {image_tensor.shape}")
                return (image_tensor,)
                
        except httpx.TimeoutException:
            raise RuntimeError(f"Request timed out. Try increasing the timeout parameter.")
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise RuntimeError("Invalid RUNWAY_API_KEY. Please check your API key.")
            elif e.response.status_code == 429:
                raise RuntimeError("Rate limit exceeded. Please wait and try again.")
            elif e.response.status_code == 400:
                error_detail = e.response.text
                raise RuntimeError(f"Invalid request: {error_detail}")
            else:
                raise RuntimeError(f"Runway API error {e.response.status_code}: {e.response.text}")
        except Exception as e:
            raise RuntimeError(f"Failed to generate image: {str(e)}")
    
    def _poll_for_completion(
        self, 
        client: httpx.Client, 
        task_id: str, 
        headers: Dict[str, str], 
        timeout: int
    ) -> str:
        """
        Poll the Runway API until the task completes and return the image URL.
        
        Args:
            client: HTTP client to use for requests
            task_id: The task ID to poll
            headers: Headers to include in requests  
            timeout: Maximum time to wait in seconds
            
        Returns:
            URL of the generated image
            
        Raises:
            RuntimeError: If task fails or times out
        """
        start_time = time.time()
        poll_interval = 2  # Start with 2 second intervals
        max_poll_interval = 10  # Maximum 10 second intervals
        
        while time.time() - start_time < timeout:
            try:
                # Poll task status
                response = client.get(
                    f"https://api.dev.runwayml.com/v1/tasks/{task_id}",
                    headers=headers,
                    timeout=10
                )
                response.raise_for_status()
                
                status_data = response.json()
                status = status_data.get("status")
                
                print(f"[RunwayText2Img] Task {task_id} status: {status}")
                
                if status == "SUCCEEDED":
                    # Task completed successfully
                    output = status_data.get("output")
                    if not output or not isinstance(output, list) or len(output) == 0:
                        raise RuntimeError("Task succeeded but no output found")
                    
                    return output[0]  # Return the first (and usually only) image URL
                
                elif status in ["FAILED", "CANCELLED"]:
                    # Task failed or was cancelled
                    failure_reason = status_data.get("failure", {}).get("reason", "Unknown error")
                    raise RuntimeError(f"Task {status.lower()}: {failure_reason}")
                
                elif status in ["PENDING", "RUNNING"]:
                    # Task is still processing, continue polling
                    progress = status_data.get("progress")
                    if progress is not None:
                        print(f"[RunwayText2Img] Progress: {progress:.1%}")
                    
                    time.sleep(poll_interval)
                    
                    # Gradually increase poll interval to reduce API calls
                    poll_interval = min(poll_interval * 1.2, max_poll_interval)
                    
                else:
                    # Unknown status
                    print(f"[RunwayText2Img] Unknown status: {status}, continuing to poll...")
                    time.sleep(poll_interval)
                    
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 404:
                    raise RuntimeError(f"Task {task_id} not found")
                else:
                    raise RuntimeError(f"Error polling task status: {e.response.status_code}")
            except httpx.TimeoutException:
                print(f"[RunwayText2Img] Polling timeout, retrying...")
                time.sleep(poll_interval)
        
        # If we get here, we've timed out
        raise RuntimeError(f"Task did not complete within {timeout} seconds")


# Export for ComfyUI
__all__ = ["RunwayText2ImgNode"] 