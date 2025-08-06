import os
from typing import Optional, Any

import torch

from comfy.comfy_types.node_typing import IO, ComfyNodeABC
from comfy_api_nodes.apis import (
    RunwayTextToImageRequest,
    RunwayTextToImageResponse,
    RunwayTaskStatusResponse as TaskStatusResponse,
    RunwayTaskStatusEnum as TaskStatus,
    Model4,
    ReferenceImage,
    RunwayTextToImageAspectRatioEnum,
)
from comfy_api_nodes.apis.client import (
    ApiEndpoint,
    HttpMethod,
    SynchronousOperation,
    PollingOperation,
    EmptyRequest,
)
from comfy_api_nodes.apinode_utils import (
    validate_string,
    download_url_to_image_tensor,
    upload_images_to_comfyapi,
)
from comfy_api_nodes.mapper_utils import model_field_to_node_input

# API endpoints
PATH_TEXT_TO_IMAGE = "/proxy/runway/text_to_image"
PATH_GET_TASK_STATUS = "/proxy/runway/tasks"

# Estimated time for text-to-image generation (in seconds)
AVERAGE_DURATION_T2I_SECONDS = 30


class RunwayText2ImgNode(ComfyNodeABC):

    @classmethod
    def INPUT_TYPES(cls):
        
        return {
            "required": {
                "prompt": model_field_to_node_input(
                    IO.STRING, 
                    RunwayTextToImageRequest, 
                    "promptText", 
                    multiline=True,
                    tooltip="Text description of the image to generate"
                ),
                "aspect_ratio": model_field_to_node_input(
                    IO.COMBO,
                    RunwayTextToImageRequest,
                    "ratio",
                    enum_type=RunwayTextToImageAspectRatioEnum,
                    default="16:9",
                    tooltip="Aspect ratio of the generated image"
                ),
                "seed": model_field_to_node_input(
                    IO.INT,
                    RunwayTextToImageRequest,
                    "seed",
                    default=0,
                    tooltip="Random seed for reproducibility (0 for random)"
                ),
            },
            "optional": {
                "reference_image": (
                    "IMAGE",
                    {"tooltip": "Optional reference image to guide the generation"}
                ),
                "poll_timeout": (
                    "INT",
                    {
                        "default": 300,
                        "min": 10,
                        "max": 3600,
                        "step": 5,
                        "tooltip": "Maximum time (seconds) to wait for generation to complete"
                    },
                ),
            },
            "hidden": {
                "unique_id": "UNIQUE_ID",
            },
        }

    def validate_environment(self):
        """Validate that required environment variables are set."""
        if not os.environ.get("RUNWAY_API_KEY"):
            raise ValueError("Missing required environment variable: RUNWAY_API_KEY. Please set this variable to use the Runway text-to-image node.")

    def validate_task_created(self, response: RunwayTextToImageResponse) -> bool:
        
        if not bool(response.id):
            raise ValueError("Invalid response from Runway API: No task ID received")
        return True

    def validate_response(self, response: TaskStatusResponse) -> bool:
        
        if not response.output or len(response.output) == 0:
            raise ValueError("Runway task succeeded but no image data found in response")
        return True

    def get_response(
        self, 
        task_id: str, 
        auth_kwargs: dict[str, str], 
        node_id: Optional[str] = None,
        poll_timeout: int = 300
    ) -> TaskStatusResponse:
       
        return poll_until_finished(
            auth_kwargs,
            ApiEndpoint(
                path=f"{PATH_GET_TASK_STATUS}/{task_id}",
                method=HttpMethod.GET,
                request_model=EmptyRequest,
                response_model=TaskStatusResponse,
            ),
            estimated_duration=AVERAGE_DURATION_T2I_SECONDS,
            node_id=node_id,
            timeout=poll_timeout,
        )

    def generate_image(
        self,
        prompt: str,
        aspect_ratio: str,
        seed: int = 0,
        reference_image: Optional[torch.Tensor] = None,
        poll_timeout: int = 300,
        unique_id: Optional[str] = None,
        **kwargs,
    ) -> tuple[torch.Tensor]:
       
        # Validate environment and inputs
        self.validate_environment()
        validate_string(prompt, min_length=1, field_name="prompt")
        
        # Prepare reference images if provided
        reference_images = None
        if reference_image is not None:
            # Validate reference image dimensions
            if len(reference_image.shape) != 4 or reference_image.shape[1] not in {1, 3, 4}:
                raise ValueError()
                
            # Upload reference image to ComfyAPI
            download_urls = upload_images_to_comfyapi(
                reference_image,
                max_images=1,
                mime_type="image/png",
                auth_kwargs={"api_key": os.environ["RUNWAY_API_KEY"]},
            )
            
            if not download_urls:
                raise RuntimeError("Failed to upload reference image to ComfyAPI")
                
            reference_images = [ReferenceImage(uri=str(download_urls[0]))]

        # Create API request
        request = RunwayTextToImageRequest(
            promptText=prompt,
            model=Model4.gen4_image,
            ratio=aspect_ratio,
            referenceImages=reference_images,
            seed=seed if seed != 0 else None,  # Use None for random seed
        )

        # Execute the request
        try:
            operation = SynchronousOperation(
                endpoint=ApiEndpoint(
                    path=PATH_TEXT_TO_IMAGE,
                    method=HttpMethod.POST,
                    request_model=RunwayTextToImageRequest,
                    response_model=RunwayTextToImageResponse,
                ),
                request=request,
                auth_kwargs={"api_key": os.environ["RUNWAY_API_KEY"]},
            )
            
            # Get initial response
            initial_response = operation.execute()
            self.validate_task_created(initial_response)
            
            # Poll for completion
            final_response = self.get_response(
                task_id=initial_response.id,
                auth_kwargs={"api_key": os.environ["RUNWAY_API_KEY"]},
                node_id=unique_id,
                poll_timeout=poll_timeout,
            )
            self.validate_response(final_response)
            
            # Download and return the generated image
            image_url = final_response.output[0]  # Get first output URL
            image_tensor = download_url_to_image_tensor(image_url)
            
            return (image_tensor,)
            
        except Exception as e:
            raise RuntimeError(f"Failed to generate image: {str(e)}") from e


def poll_until_finished(
    auth_kwargs: dict[str, str],
    api_endpoint: ApiEndpoint[Any, TaskStatusResponse],
    estimated_duration: int = 30,
    node_id: Optional[str] = None,
    timeout: int = 300,
) -> TaskStatusResponse:
    """Poll until the task is finished using PollingOperation.
    
    Args:
        auth_kwargs: Authentication parameters for the API
        api_endpoint: The API endpoint to poll
        estimated_duration: Estimated duration in seconds (used for progress reporting)
        node_id: Optional node ID for progress reporting
        timeout: Maximum time to wait in seconds
        
    Returns:
        The final task status response
        
    Raises:
        TimeoutError: If the task doesn't complete within the timeout
        RuntimeError: If the task fails or is cancelled
    """
    from datetime import datetime, timedelta
    
    def check_status() -> tuple[bool, TaskStatusResponse]:
        response = SynchronousOperation(
            endpoint=api_endpoint,
            auth_kwargs=auth_kwargs,
        ).execute()
        
        if response.status == TaskStatus.SUCCEEDED:
            return True, response
        elif response.status in {TaskStatus.FAILED, TaskStatus.CANCELLED}:
            raise RuntimeError(f"Task failed with status: {response.status}")
        return False, response
    
    start_time = datetime.now()
    timeout_time = start_time + timedelta(seconds=timeout)
    
    poller = PollingOperation(
        operation=check_status,
        check_interval_seconds=1.0,
        timeout_seconds=timeout,
        initial_delay_seconds=0.5,
        max_interval_seconds=5.0,
        backoff_factor=1.5,
    )
    
    try:
        return poller.run()
    except TimeoutError:
        raise TimeoutError(f"Task did not complete within {timeout} seconds")


# Node mapping for ComfyUI
NODE_CLASS_MAPPINGS = {
    "RunwayText2ImgNode": RunwayText2ImgNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "RunwayText2ImgNode": "Runway Text to Image (Gen-4)",
}
