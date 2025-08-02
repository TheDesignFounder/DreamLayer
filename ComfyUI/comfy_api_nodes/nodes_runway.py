"""Runway API Nodes

API Docs:
  - https://docs.dev.runwayml.com/api/#tag/Task-management/paths/~1v1~1tasks~1%7Bid%7D/delete

User Guides:
  - https://help.runwayml.com/hc/en-us/sections/30265301423635-Gen-3-Alpha
  - https://help.runwayml.com/hc/en-us/articles/37327109429011-Creating-with-Gen-4-Video
  - https://help.runwayml.com/hc/en-us/articles/33927968552339-Creating-with-Act-One-on-Gen-3-Alpha-and-Turbo
  - https://help.runwayml.com/hc/en-us/articles/34170748696595-Creating-with-Keyframes-on-Gen-3

"""

from typing import Union, Optional, Any
from enum import Enum
import os
import requests
import base64
import io
import time
import numpy as np
import torch
from PIL import Image

from typing import Optional

import nodes
import torch
import time

from comfy.comfy_types.node_typing import ComfyNodeABC, IO

import torch

from comfy_api_nodes.apis import (
    RunwayImageToVideoRequest,
    RunwayImageToVideoResponse,
    RunwayTaskStatusResponse as TaskStatusResponse,
    RunwayTaskStatusEnum as TaskStatus,
    RunwayModelEnum as Model,
    RunwayDurationEnum as Duration,
    RunwayAspectRatioEnum as AspectRatio,
    RunwayPromptImageObject,
    RunwayPromptImageDetailedObject,
    RunwayTextToImageRequest,
    RunwayTextToImageResponse,
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
    upload_images_to_comfyapi,
    download_url_to_video_output,
    image_tensor_pair_to_batch,
    validate_string,
    download_url_to_image_tensor,
)
from comfy_api_nodes.mapper_utils import model_field_to_node_input
from comfy_api.input_impl import VideoFromFile
from comfy.comfy_types.node_typing import IO, ComfyNodeABC

PATH_IMAGE_TO_VIDEO = "/proxy/runway/image_to_video"
PATH_TEXT_TO_IMAGE = "/proxy/runway/text_to_image"
PATH_GET_TASK_STATUS = "/proxy/runway/tasks"

AVERAGE_DURATION_I2V_SECONDS = 64
AVERAGE_DURATION_FLF_SECONDS = 256
AVERAGE_DURATION_T2I_SECONDS = 41


class RunwayApiError(Exception):
    """Base exception for Runway API errors."""

    pass


class RunwayGen4TurboAspectRatio(str, Enum):
    """Aspect ratios supported for Image to Video API when using gen4_turbo model."""

    field_1280_720 = "1280:720"
    field_720_1280 = "720:1280"
    field_1104_832 = "1104:832"
    field_832_1104 = "832:1104"
    field_960_960 = "960:960"
    field_1584_672 = "1584:672"


class RunwayGen3aAspectRatio(str, Enum):
    """Aspect ratios supported for Image to Video API when using gen3a_turbo model."""

    field_768_1280 = "768:1280"
    field_1280_768 = "1280:768"


def get_video_url_from_task_status(response: TaskStatusResponse) -> Union[str, None]:
    """Returns the video URL from the task status response if it exists."""
    if response.output and len(response.output) > 0:
        return response.output[0]
    return None


# TODO: replace with updated image validation utils (upstream)
def validate_input_image(image: torch.Tensor) -> bool:
    """
    Validate the input image is within the size limits for the Runway API.
    See: https://docs.dev.runwayml.com/assets/inputs/#common-error-reasons
    """
    return image.shape[2] < 8000 and image.shape[1] < 8000


def poll_until_finished(
    auth_kwargs: dict[str, str],
    api_endpoint: ApiEndpoint[Any, TaskStatusResponse],
    estimated_duration: Optional[int] = None,
    node_id: Optional[str] = None,
) -> TaskStatusResponse:
    """Polls the Runway API endpoint until the task reaches a terminal state, then returns the response."""
    return PollingOperation(
        poll_endpoint=api_endpoint,
        completed_statuses=[
            TaskStatus.SUCCEEDED.value,
        ],
        failed_statuses=[
            TaskStatus.FAILED.value,
            TaskStatus.CANCELLED.value,
        ],
        status_extractor=lambda response: (response.status.value),
        auth_kwargs=auth_kwargs,
        result_url_extractor=get_video_url_from_task_status,
        estimated_duration=estimated_duration,
        node_id=node_id,
        progress_extractor=extract_progress_from_task_status,
    ).execute()


def extract_progress_from_task_status(
    response: TaskStatusResponse,
) -> Union[float, None]:
    if hasattr(response, "progress") and response.progress is not None:
        return response.progress * 100
    return None


def get_image_url_from_task_status(response: TaskStatusResponse) -> Union[str, None]:
    """Returns the image URL from the task status response if it exists."""
    if response.output and len(response.output) > 0:
        return response.output[0]
    return None


class RunwayVideoGenNode(ComfyNodeABC):
    """Runway Video Node Base."""

    RETURN_TYPES = ("VIDEO",)
    FUNCTION = "api_call"
    CATEGORY = "api node/video/Runway"
    API_NODE = True

    def validate_task_created(self, response: RunwayImageToVideoResponse) -> bool:
        """
        Validate the task creation response from the Runway API matches
        expected format.
        """
        if not bool(response.id):
            raise RunwayApiError("Invalid initial response from Runway API.")
        return True

    def validate_response(self, response: RunwayImageToVideoResponse) -> bool:
        """
        Validate the successful task status response from the Runway API
        matches expected format.
        """
        if not response.output or len(response.output) == 0:
            raise RunwayApiError(
                "Runway task succeeded but no video data found in response."
            )
        return True

    def get_response(
        self, task_id: str, auth_kwargs: dict[str, str], node_id: Optional[str] = None
    ) -> RunwayImageToVideoResponse:
        """Poll the task status until it is finished then get the response."""
        return poll_until_finished(
            auth_kwargs,
            ApiEndpoint(
                path=f"{PATH_GET_TASK_STATUS}/{task_id}",
                method=HttpMethod.GET,
                request_model=EmptyRequest,
                response_model=TaskStatusResponse,
            ),
            estimated_duration=AVERAGE_DURATION_FLF_SECONDS,
            node_id=node_id,
        )

    def generate_video(
        self,
        request: RunwayImageToVideoRequest,
        auth_kwargs: dict[str, str],
        node_id: Optional[str] = None,
    ) -> tuple[VideoFromFile]:
        initial_operation = SynchronousOperation(
            endpoint=ApiEndpoint(
                path=PATH_IMAGE_TO_VIDEO,
                method=HttpMethod.POST,
                request_model=RunwayImageToVideoRequest,
                response_model=RunwayImageToVideoResponse,
            ),
            request=request,
            auth_kwargs=auth_kwargs,
        )

        initial_response = initial_operation.execute()
        self.validate_task_created(initial_response)
        task_id = initial_response.id

        final_response = self.get_response(task_id, auth_kwargs, node_id)
        self.validate_response(final_response)

        video_url = get_video_url_from_task_status(final_response)
        return (download_url_to_video_output(video_url),)


class RunwayImageToVideoNodeGen3a(RunwayVideoGenNode):
    """Runway Image to Video Node using Gen3a Turbo model."""

    DESCRIPTION = "Generate a video from a single starting frame using Gen3a Turbo model. Before diving in, review these best practices to ensure that your input selections will set your generation up for success: https://help.runwayml.com/hc/en-us/articles/33927968552339-Creating-with-Act-One-on-Gen-3-Alpha-and-Turbo."

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "prompt": model_field_to_node_input(
                    IO.STRING, RunwayImageToVideoRequest, "promptText", multiline=True
                ),
                "start_frame": (
                    IO.IMAGE,
                    {"tooltip": "Start frame to be used for the video"},
                ),
                "duration": model_field_to_node_input(
                    IO.COMBO, RunwayImageToVideoRequest, "duration", enum_type=Duration
                ),
                "ratio": model_field_to_node_input(
                    IO.COMBO,
                    RunwayImageToVideoRequest,
                    "ratio",
                    enum_type=RunwayGen3aAspectRatio,
                ),
                "seed": model_field_to_node_input(
                    IO.INT,
                    RunwayImageToVideoRequest,
                    "seed",
                    control_after_generate=True,
                ),
            },
            "hidden": {
                "auth_token": "AUTH_TOKEN_COMFY_ORG",
                "comfy_api_key": "API_KEY_COMFY_ORG",
                "unique_id": "UNIQUE_ID",
            },
        }

    def api_call(
        self,
        prompt: str,
        start_frame: torch.Tensor,
        duration: str,
        ratio: str,
        seed: int,
        unique_id: Optional[str] = None,
        **kwargs,
    ) -> tuple[VideoFromFile]:
        # Validate inputs
        validate_string(prompt, min_length=1)
        validate_input_image(start_frame)

        # Upload image
        download_urls = upload_images_to_comfyapi(
            start_frame,
            max_images=1,
            mime_type="image/png",
            auth_kwargs=kwargs,
        )
        if len(download_urls) != 1:
            raise RunwayApiError("Failed to upload one or more images to comfy api.")

        return self.generate_video(
            RunwayImageToVideoRequest(
                promptText=prompt,
                seed=seed,
                model=Model("gen3a_turbo"),
                duration=Duration(duration),
                ratio=AspectRatio(ratio),
                promptImage=RunwayPromptImageObject(
                    root=[
                        RunwayPromptImageDetailedObject(
                            uri=str(download_urls[0]), position="first"
                        )
                    ]
                ),
            ),
            auth_kwargs=kwargs,
            node_id=unique_id,
        )


class RunwayImageToVideoNodeGen4(RunwayVideoGenNode):
    """Runway Image to Video Node using Gen4 Turbo model."""

    DESCRIPTION = "Generate a video from a single starting frame using Gen4 Turbo model. Before diving in, review these best practices to ensure that your input selections will set your generation up for success: https://help.runwayml.com/hc/en-us/articles/37327109429011-Creating-with-Gen-4-Video."

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "prompt": model_field_to_node_input(
                    IO.STRING, RunwayImageToVideoRequest, "promptText", multiline=True
                ),
                "start_frame": (
                    IO.IMAGE,
                    {"tooltip": "Start frame to be used for the video"},
                ),
                "duration": model_field_to_node_input(
                    IO.COMBO, RunwayImageToVideoRequest, "duration", enum_type=Duration
                ),
                "ratio": model_field_to_node_input(
                    IO.COMBO,
                    RunwayImageToVideoRequest,
                    "ratio",
                    enum_type=RunwayGen4TurboAspectRatio,
                ),
                "seed": model_field_to_node_input(
                    IO.INT,
                    RunwayImageToVideoRequest,
                    "seed",
                    control_after_generate=True,
                ),
            },
            "hidden": {
                "auth_token": "AUTH_TOKEN_COMFY_ORG",
                "comfy_api_key": "API_KEY_COMFY_ORG",
                "unique_id": "UNIQUE_ID",
            },
        }

    def api_call(
        self,
        prompt: str,
        start_frame: torch.Tensor,
        duration: str,
        ratio: str,
        seed: int,
        unique_id: Optional[str] = None,
        **kwargs,
    ) -> tuple[VideoFromFile]:
        # Validate inputs
        validate_string(prompt, min_length=1)
        validate_input_image(start_frame)

        # Upload image
        download_urls = upload_images_to_comfyapi(
            start_frame,
            max_images=1,
            mime_type="image/png",
            auth_kwargs=kwargs,
        )
        if len(download_urls) != 1:
            raise RunwayApiError("Failed to upload one or more images to comfy api.")

        return self.generate_video(
            RunwayImageToVideoRequest(
                promptText=prompt,
                seed=seed,
                model=Model("gen4_turbo"),
                duration=Duration(duration),
                ratio=AspectRatio(ratio),
                promptImage=RunwayPromptImageObject(
                    root=[
                        RunwayPromptImageDetailedObject(
                            uri=str(download_urls[0]), position="first"
                        )
                    ]
                ),
            ),
            auth_kwargs=kwargs,
            node_id=unique_id,
        )


class RunwayFirstLastFrameNode(RunwayVideoGenNode):
    """Runway First-Last Frame Node."""

    DESCRIPTION = "Upload first and last keyframes, draft a prompt, and generate a video. More complex transitions, such as cases where the Last frame is completely different from the First frame, may benefit from the longer 10s duration. This would give the generation more time to smoothly transition between the two inputs. Before diving in, review these best practices to ensure that your input selections will set your generation up for success: https://help.runwayml.com/hc/en-us/articles/34170748696595-Creating-with-Keyframes-on-Gen-3."

    def get_response(
        self, task_id: str, auth_kwargs: dict[str, str], node_id: Optional[str] = None
    ) -> RunwayImageToVideoResponse:
        return poll_until_finished(
            auth_kwargs,
            ApiEndpoint(
                path=f"{PATH_GET_TASK_STATUS}/{task_id}",
                method=HttpMethod.GET,
                request_model=EmptyRequest,
                response_model=TaskStatusResponse,
            ),
            estimated_duration=AVERAGE_DURATION_FLF_SECONDS,
            node_id=node_id,
        )

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "prompt": model_field_to_node_input(
                    IO.STRING, RunwayImageToVideoRequest, "promptText", multiline=True
                ),
                "start_frame": (
                    IO.IMAGE,
                    {"tooltip": "Start frame to be used for the video"},
                ),
                "end_frame": (
                    IO.IMAGE,
                    {
                        "tooltip": "End frame to be used for the video. Supported for gen3a_turbo only."
                    },
                ),
                "duration": model_field_to_node_input(
                    IO.COMBO, RunwayImageToVideoRequest, "duration", enum_type=Duration
                ),
                "ratio": model_field_to_node_input(
                    IO.COMBO,
                    RunwayImageToVideoRequest,
                    "ratio",
                    enum_type=RunwayGen3aAspectRatio,
                ),
                "seed": model_field_to_node_input(
                    IO.INT,
                    RunwayImageToVideoRequest,
                    "seed",
                    control_after_generate=True,
                ),
            },
            "hidden": {
                "auth_token": "AUTH_TOKEN_COMFY_ORG",
                "unique_id": "UNIQUE_ID",
                "comfy_api_key": "API_KEY_COMFY_ORG",
            },
        }

    def api_call(
        self,
        prompt: str,
        start_frame: torch.Tensor,
        end_frame: torch.Tensor,
        duration: str,
        ratio: str,
        seed: int,
        unique_id: Optional[str] = None,
        **kwargs,
    ) -> tuple[VideoFromFile]:
        # Validate inputs
        validate_string(prompt, min_length=1)
        validate_input_image(start_frame)
        validate_input_image(end_frame)

        # Upload images
        stacked_input_images = image_tensor_pair_to_batch(start_frame, end_frame)
        download_urls = upload_images_to_comfyapi(
            stacked_input_images,
            max_images=2,
            mime_type="image/png",
            auth_kwargs=kwargs,
        )
        if len(download_urls) != 2:
            raise RunwayApiError("Failed to upload one or more images to comfy api.")

        return self.generate_video(
            RunwayImageToVideoRequest(
                promptText=prompt,
                seed=seed,
                model=Model("gen3a_turbo"),
                duration=Duration(duration),
                ratio=AspectRatio(ratio),
                promptImage=RunwayPromptImageObject(
                    root=[
                        RunwayPromptImageDetailedObject(
                            uri=str(download_urls[0]), position="first"
                        ),
                        RunwayPromptImageDetailedObject(
                            uri=str(download_urls[1]), position="last"
                        ),
                    ]
                ),
            ),
            auth_kwargs=kwargs,
            node_id=unique_id,
        )


class RunwayTextToImageNode(ComfyNodeABC):
    """Runway Text to Image Node."""

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "api_call"
    CATEGORY = "api node/image/Runway"
    API_NODE = True
    DESCRIPTION = "Generate an image from a text prompt using Runway's Gen 4 model. You can also include reference images to guide the generation."

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "prompt": model_field_to_node_input(
                    IO.STRING, RunwayTextToImageRequest, "promptText", multiline=True
                ),
                "ratio": model_field_to_node_input(
                    IO.COMBO,
                    RunwayTextToImageRequest,
                    "ratio",
                    enum_type=RunwayTextToImageAspectRatioEnum,
                ),
            },
            "optional": {
                "reference_image": (
                    IO.IMAGE,
                    {"tooltip": "Optional reference image to guide the generation"},
                )
            },
            "hidden": {
                "auth_token": "AUTH_TOKEN_COMFY_ORG",
                "comfy_api_key": "API_KEY_COMFY_ORG",
                "unique_id": "UNIQUE_ID",
            },
        }

    def validate_task_created(self, response: RunwayTextToImageResponse) -> bool:
        """
        Validate the task creation response from the Runway API matches
        expected format.
        """
        if not bool(response.id):
            raise RunwayApiError("Invalid initial response from Runway API.")
        return True

    def validate_response(self, response: TaskStatusResponse) -> bool:
        """
        Validate the successful task status response from the Runway API
        matches expected format.
        """
        if not response.output or len(response.output) == 0:
            raise RunwayApiError(
                "Runway task succeeded but no image data found in response."
            )
        return True

    def get_response(
        self, task_id: str, auth_kwargs: dict[str, str], node_id: Optional[str] = None
    ) -> TaskStatusResponse:
        """Poll the task status until it is finished then get the response."""
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
        )

    def api_call(
        self,
        prompt: str,
        ratio: str,
        reference_image: Optional[torch.Tensor] = None,
        unique_id: Optional[str] = None,
        **kwargs,
    ) -> tuple[torch.Tensor]:
        # Validate inputs
        validate_string(prompt, min_length=1)

        # Prepare reference images if provided
        reference_images = None
        if reference_image is not None:
            validate_input_image(reference_image)
            download_urls = upload_images_to_comfyapi(
                reference_image,
                max_images=1,
                mime_type="image/png",
                auth_kwargs=kwargs,
            )
            if len(download_urls) != 1:
                raise RunwayApiError("Failed to upload reference image to comfy api.")

            reference_images = [ReferenceImage(uri=str(download_urls[0]))]

        # Create request
        request = RunwayTextToImageRequest(
            promptText=prompt,
            model=Model4.gen4_image,
            ratio=ratio,
            referenceImages=reference_images,
        )

        # Execute initial request
        initial_operation = SynchronousOperation(
            endpoint=ApiEndpoint(
                path=PATH_TEXT_TO_IMAGE,
                method=HttpMethod.POST,
                request_model=RunwayTextToImageRequest,
                response_model=RunwayTextToImageResponse,
            ),
            request=request,
            auth_kwargs=kwargs,
        )

        initial_response = initial_operation.execute()
        self.validate_task_created(initial_response)
        task_id = initial_response.id

        # Poll for completion
        final_response = self.get_response(
            task_id, auth_kwargs=kwargs, node_id=unique_id
        )
        self.validate_response(final_response)

        # Download and return image
        image_url = get_image_url_from_task_status(final_response)
        if not image_url:
            raise RunwayApiError("No image URL found in successful response.")
        return (download_url_to_image_tensor(image_url),)

"""
Runway Text-to-Image Node

A simple node that accepts a prompt string and generates an image using Runway's API.
"""

class RunwayText2ImgNode(ComfyNodeABC):
    """Runway Text-to-Image Node - Simple direct API implementation."""
    
    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "generate_image"
    CATEGORY = "api node/image/Runway"
    API_NODE = True
    DESCRIPTION = "Generate an image from a text prompt using Runway's API directly."
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "prompt": model_field_to_node_input(
                    IO.STRING, RunwayTextToImageRequest, "promptText", multiline=True),
                "ratio": model_field_to_node_input(
                    IO.COMBO,
                    RunwayTextToImageRequest,
                    "ratio",
                    enum_type=RunwayTextToImageAspectRatioEnum,
                )
            },
            "hidden": {
                "unique_id": "UNIQUE_ID"
            },
        }
    
    def generate_image(self, prompt: str, ratio: str, unique_id: Optional[str] = None, **kwargs):
        """
        Generate an image from a text prompt using Runway's API.
        
        Args:
            prompt: The text prompt for image generation
            unique_id: Optional unique identifier for the node
            
        Returns:
            tuple[torch.Tensor]: Generated image as a tensor
            
        Raises:
            ValueError: If RUNWAY_API_KEY is missing
            Exception: If API call fails
        """

        # Check for API key
        api_key = os.getenv('RUNWAY_API_KEY')
        if not api_key:
            raise ValueError(
                "RUNWAY_API_KEY environment variable is required but not set. "
                "Please set your Runway API key in the .env file or environment variables."
            )
        
        # Validate prompt
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty")
        
        # Prepare the request
        url = "https://api.dev.runwayml.com/v1/text_to_image"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "X-Runway-Version": "2024-11-06"
        }
        
        payload = {
            "promptText": prompt.strip(),
            "model": "gen4_image",
            "ratio": ratio 
        }
        
        try:
            # Make the API request
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            # print("Response status:", response.status_code)
            # print("Response text:", response.text)
            response.raise_for_status()
            
            # Parse the response
            result_id = response.json().get("id")
            if not result_id:
                raise Exception("No result ID received from Runway API")

            # Poll for result
            status_url = f"https://api.dev.runwayml.com/v1/tasks/{result_id}"
            max_attempts = 30
            image_url = None

            for attempt in range(max_attempts):
                time.sleep(2)
                status_response = requests.get(status_url, headers=headers)
                status_response.raise_for_status()
                status_data = status_response.json()

                if status_data.get("status") == "SUCCEEDED":
                    output_list = status_data.get("output", [])
                    if output_list:
                       image_url = output_list[0]
                       break
                elif status_data.get("status") in ["FAILED", "CANCELLED"]:
                   raise Exception(f"Task failed: {status_data.get('status')}")

            if not image_url:
               raise Exception("Timeout waiting for image generation.")

            # Download and convert image
            image_response = requests.get(image_url)
            image_response.raise_for_status()
            image_bytes = image_response.content
            image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
            image_array = np.array(image).astype(np.float32) / 255.0

            if image_array.ndim == 2:
                image_array = np.stack([image_array] * 3, axis=-1)
            elif image_array.shape[2] == 4:
                image_array = image_array[:, :, :3]
            elif image_array.shape[2] == 1:
                image_array = np.repeat(image_array, 3, axis=-1)

            image_tensor = torch.from_numpy(image_array).permute(2, 0, 1).unsqueeze(0).contiguous()
           
            # print(f"✅ Runway output tensor shape: {image_tensor.shape}, dtype: {image_tensor.dtype}")

            if image_tensor.ndim != 4 or image_tensor.shape[1] != 3:
                raise ValueError(f"Unexpected image tensor shape: {image_tensor.shape}. Must be [1, 3, H, W]")

            if image_tensor.dtype != torch.float32:
                image_tensor = image_tensor.float()

            return (image_tensor,)
            

        except requests.exceptions.HTTPError as e:
            print("Runway API error response:", response.text)
            if response.status_code == 401:
                raise Exception("Invalid Runway API key. Please check your RUNWAY_API_KEY.")
            elif response.status_code == 400:
                raise Exception(f"Bad request to Runway API: {response.text}")
            else:
                raise Exception(f"Runway API error (HTTP {response.status_code}): {response.text}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to connect to Runway API: {str(e)}")
        except Exception as e:
            raise Exception(f"Error generating image with Runway API: {str(e)}")


# Node mappings
NODE_CLASS_MAPPINGS = {
    "RunwayFirstLastFrameNode": RunwayFirstLastFrameNode,
    "RunwayImageToVideoNodeGen3a": RunwayImageToVideoNodeGen3a,
    "RunwayImageToVideoNodeGen4": RunwayImageToVideoNodeGen4,
    "RunwayTextToImageNode": RunwayTextToImageNode,
    "RunwayText2ImgNode": RunwayText2ImgNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "RunwayFirstLastFrameNode": "Runway First-Last-Frame to Video",
    "RunwayImageToVideoNodeGen3a": "Runway Image to Video (Gen3a Turbo)",
    "RunwayImageToVideoNodeGen4": "Runway Image to Video (Gen4 Turbo)",
    "RunwayTextToImageNode": "Runway Text to Image",
    "RunwayText2ImgNode": "Runway Text to Image (Simple)",
} 