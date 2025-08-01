from __future__ import annotations
from inspect import cleandoc
from typing import Optional
from comfy.comfy_types.node_typing import IO, ComfyNodeABC, InputTypeDict
from comfy_api.input_impl.video_types import VideoFromFile
from comfy_api_nodes.apis.luma_api import (
    LumaImageModel,
    LumaVideoModel,
    LumaVideoOutputResolution,
    LumaVideoModelOutputDuration,
    LumaAspectRatio,
    LumaState,
    LumaImageGenerationRequest,
    LumaGenerationRequest,
    LumaGeneration,
    LumaCharacterRef,
    LumaModifyImageRef,
    LumaImageIdentity,
    LumaReference,
    LumaReferenceChain,
    LumaImageReference,
    LumaKeyframes,
    LumaConceptChain,
    LumaIO,
    get_luma_concepts,
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
    process_image_response,
    validate_string,
)
from server import PromptServer

import requests
import torch
from io import BytesIO
import os
import time
from typing import Optional, Dict, List, Union

# Constants for API interaction
LUMA_T2V_AVERAGE_DURATION = 105  # Average duration in seconds for text-to-video generation
LUMA_I2V_AVERAGE_DURATION = 100  # Average duration in seconds for image-to-video generation
MAX_RETRIES = 3  # Maximum number of retries for API requests
INITIAL_RETRY_DELAY = 2  # Initial retry delay in seconds

def image_result_url_extractor(response: LumaGeneration) -> str:
    """Extract image URL from Luma API response.
    
    Args:
        response: The Luma API response object
        
    Returns:
        str: The URL of the generated image
        
    Raises:
        RuntimeError: If the image URL is missing from the response
    """
    url = getattr(getattr(response, "assets", None), "image", None)
    if not url:
        raise RuntimeError(
            "No image URL found in response.assets.image. "
            "This may indicate an API error or incomplete generation."
        )
    return url

def video_result_url_extractor(response: LumaGeneration) -> str:
    """Extract video URL from Luma API response.
    
    Args:
        response: The Luma API response object
        
    Returns:
        str: The URL of the generated video
        
    Raises:
        RuntimeError: If the video URL is missing from the response
    """
    url = getattr(getattr(response, "assets", None), "video", None)
    if not url:
        raise RuntimeError(
            "No video URL found in response.assets.video. "
            "This may indicate an API error or incomplete generation."
        )
    return url

class LumaReferenceNode(ComfyNodeABC):
    """
    Holds an image and weight for use with Luma Generate Image node.
    """

    RETURN_TYPES = (IO.STRING,)
    RETURN_NAMES = ("luma_ref",)
    DESCRIPTION = cleandoc(__doc__ or "")  # Handle potential None value
    FUNCTION = "create_luma_reference"
    CATEGORY = "api node/image/Luma"

    @classmethod
    def INPUT_TYPES(cls) -> InputTypeDict:
        return {
            "required": {
                "image": (
                    IO.IMAGE,
                    {
                        "tooltip": "Image to use as reference.",
                    },
                ),
                "weight": (
                    IO.FLOAT,
                    {
                        "default": 1.0,
                        "min": 0.0,
                        "max": 1.0,
                        "step": 0.01,
                        "tooltip": "Weight of image reference.",
                    },
                ),
            },
            "optional": {
                "luma_ref": (
                    IO.STRING,
                    {
                        "tooltip": "Serialized Luma Reference Chain (string).",
                    },
                ),
            },
        }

    def create_luma_reference(
        self,
        image: torch.Tensor,
        weight: float,
        luma_ref: Optional[LumaReferenceChain] = None
    ) -> tuple[LumaReferenceChain]:
        if luma_ref is not None:
            luma_ref = luma_ref.clone()
        else:
            luma_ref = LumaReferenceChain()
        luma_ref.add(LumaReference(image=image, weight=round(weight, 2)))
        return (luma_ref,)


class LumaConceptsNode(ComfyNodeABC):
    """
    Holds one or more Camera Concepts for use with Luma Text to Video and Luma Image to Video nodes.
    """

    RETURN_TYPES = (IO.STRING,)
    RETURN_NAMES = ("luma_concepts",)
    DESCRIPTION = cleandoc(__doc__ or "")  # Handle potential None value
    FUNCTION = "create_concepts"
    CATEGORY = "api node/video/Luma"

    @classmethod
    def INPUT_TYPES(cls) -> InputTypeDict:
        concept_options = get_luma_concepts(include_none=True)
        return {
            "required": {
                "concept1": (
                    IO.STRING,
                    {
                        "options": concept_options,
                        "tooltip": "Camera concept 1.",
                    },
                ),
                "concept2": (
                    IO.STRING,
                    {
                        "options": concept_options,
                        "tooltip": "Camera concept 2.",
                    },
                ),
                "concept3": (
                    IO.STRING,
                    {
                        "options": concept_options,
                        "tooltip": "Camera concept 3.",
                    },
                ),
                "concept4": (
                    IO.STRING,
                    {
                        "options": concept_options,
                        "tooltip": "Camera concept 4.",
                    },
                ),
            },
            "optional": {
                "luma_concepts": (
                    IO.STRING,
                    {
                        "tooltip": "Serialized Luma Concept Chain (string).",
                    },
                ),
            },
        }

    def create_concepts(
        self,
        concept1: str,
        concept2: str,
        concept3: str,
        concept4: str,
        luma_concepts: Optional[LumaConceptChain] = None,
    ) -> tuple[LumaConceptChain]:
        chain = LumaConceptChain(str_list=[concept1, concept2, concept3, concept4])
        if luma_concepts is not None:
            chain = luma_concepts.clone_and_merge(chain)
        return (chain,)


class LumaImageGenerationNode(ComfyNodeABC):
    """
    Generates images synchronously based on prompt and aspect ratio.
    """

    RETURN_TYPES = (IO.IMAGE,)
    DESCRIPTION = cleandoc(__doc__ or "")  # Handle potential None value
    FUNCTION = "api_call"
    API_NODE = True
    CATEGORY = "api node/image/Luma"

    @classmethod
    def INPUT_TYPES(cls) -> InputTypeDict:
        return {
            "required": {
                "prompt": (
                    IO.STRING,
                    {
                        "multiline": True,
                        "default": "",
                        "tooltip": "Prompt for the image generation",
                    },
                ),
                "model": (
                    IO.STRING,
                    {
                        "options": [model.value for model in LumaImageModel],
                        "default": LumaImageModel.photon_1.value,
                        "tooltip": "Luma model to use.",
                    },
                ),
                "aspect_ratio": (
                    IO.STRING,
                    {
                        "options": [ratio.value for ratio in LumaAspectRatio],
                        "default": LumaAspectRatio.ratio_16_9.value,
                        "tooltip": "Aspect ratio of the generated image.",
                    },
                ),
                "seed": (
                    IO.INT,
                    {
                        "default": 0,
                        "min": 0,
                        "max": 0xFFFFFFFFFFFFFFFF,
                        "control_after_generate": True,
                        "tooltip": "Seed to determine if node should re-run; actual results are nondeterministic regardless of seed.",
                    },
                ),
                "style_image_weight": (
                    IO.FLOAT,
                    {
                        "default": 1.0,
                        "min": 0.0,
                        "max": 1.0,
                        "step": 0.01,
                        "tooltip": "Weight of style image. Ignored if no style_image provided.",
                    },
                ),
            },
            "optional": {
                "image_luma_ref": (
                    IO.STRING,
                    {
                        "tooltip": "Serialized Luma Reference Chain (string).",
                    },
                ),
                "style_image": (
                    IO.IMAGE,
                    {"tooltip": "Style reference image; only 1 image will be used."},
                ),
                "character_image": (
                    IO.IMAGE,
                    {
                        "tooltip": "Character reference images; can be a batch of multiple, up to 4 images can be considered."
                    },
                ),
            },
        }

    def api_call(
        self,
        prompt: str,
        model: str,
        aspect_ratio: str,
        seed: int,
        style_image_weight: float,
        image_luma_ref: Optional[LumaReferenceChain] = None,
        style_image: Optional[torch.Tensor] = None,
        character_image: Optional[torch.Tensor] = None,
        unique_id: Optional[str] = None,
        **kwargs,
    ) -> tuple[torch.Tensor]:
        validate_string(prompt, strip_whitespace=True, min_length=3)
        # handle image_luma_ref
        api_image_ref = None
        if image_luma_ref is not None:
            api_image_ref = self._convert_luma_refs(
                image_luma_ref, max_refs=4, auth_kwargs=kwargs,
            )
        # handle style_luma_ref
        api_style_ref = None
        if style_image is not None:
            api_style_ref = self._convert_style_image(
                style_image, weight=style_image_weight, auth_kwargs=kwargs,
            )
        # handle character_ref images
        character_ref = None
        if character_image is not None:
            download_urls = upload_images_to_comfyapi(
                character_image, max_images=4, auth_kwargs=kwargs,
            )
            character_ref = LumaCharacterRef(
                identity0=LumaImageIdentity(images=download_urls)
            )

        operation = SynchronousOperation(
            endpoint=ApiEndpoint(
                path="/proxy/luma/generations/image",
                method=HttpMethod.POST,
                request_model=LumaImageGenerationRequest,
                response_model=LumaGeneration,
            ),
            request=LumaImageGenerationRequest(
                prompt=prompt,
                model=LumaImageModel(model),
                aspect_ratio=LumaAspectRatio(aspect_ratio),
                image_ref=api_image_ref,
                style_ref=api_style_ref,
                character_ref=character_ref,
                modify_image_ref=None,
            ),
            auth_kwargs=kwargs,
        )
        response_api: LumaGeneration = operation.execute()

        operation = PollingOperation(
            poll_endpoint=ApiEndpoint(
                path=f"/proxy/luma/generations/{response_api.id}",
                method=HttpMethod.GET,
                request_model=EmptyRequest,
                response_model=LumaGeneration,
            ),
            completed_statuses=[LumaState.completed],
            failed_statuses=[LumaState.failed],
            status_extractor=lambda x: x.state,
            result_url_extractor=image_result_url_extractor,
            node_id=unique_id,
            progress_extractor=lambda x: 1.0 if getattr(x, "state", None) == LumaState.completed else 0.0,
            auth_kwargs=kwargs,
        )
        response_poll = operation.execute()

        image_url = getattr(getattr(response_poll, "assets", None), "image", None)
        if not image_url:
            raise RuntimeError("No image URL found in response_poll.assets.image")
        try:
            img_response = requests.get(image_url)
            img_response.raise_for_status()
            img = process_image_response(img_response)
            return (img,)
        except requests.RequestException as e:
            raise RuntimeError(f"Failed to download generated image: {e}")
        except Exception as e:
            raise RuntimeError(f"Failed to process generated image: {e}")

    def _convert_luma_refs(
        self, luma_ref: LumaReferenceChain, max_refs: int, auth_kwargs: Optional[dict[str,str]] = None
    ):
        luma_urls = []
        ref_count = 0
        for ref in luma_ref.refs:
            download_urls = upload_images_to_comfyapi(
                ref.image, max_images=1, auth_kwargs=auth_kwargs
            )
            luma_urls.append(download_urls[0])
            ref_count += 1
            if ref_count >= max_refs:
                break
        return luma_ref.create_api_model(download_urls=luma_urls, max_refs=max_refs)

    def _convert_style_image(
        self, style_image: torch.Tensor, weight: float, auth_kwargs: Optional[dict[str,str]] = None
    ):
        chain = LumaReferenceChain(
            first_ref=LumaReference(image=style_image, weight=weight)
        )
        return self._convert_luma_refs(chain, max_refs=1, auth_kwargs=auth_kwargs)


class LumaImageModifyNode(ComfyNodeABC):
    """
    Modifies images synchronously based on prompt and aspect ratio.
    """

    RETURN_TYPES = (IO.IMAGE,)
    DESCRIPTION = cleandoc(__doc__ or "")  # Handle potential None value
    FUNCTION = "api_call"
    API_NODE = True
    CATEGORY = "api node/image/Luma"

    @classmethod
    def INPUT_TYPES(cls) -> InputTypeDict:
        return {
            "required": {
                "image": (
                    IO.IMAGE,
                    {
                        "tooltip": "Image to modify.",
                    },
                ),
                "prompt": (
                    IO.STRING,
                    {
                        "multiline": True,
                        "default": "",
                        "tooltip": "Prompt for the image generation",
                    },
                ),
                "image_weight": (
                    IO.FLOAT,
                    {
                        "default": 0.1,
                        "min": 0.0,
                        "max": 0.98,
                        "step": 0.01,
                        "tooltip": "Weight of the image; the closer to 1.0, the less the image will be modified.",
                    },
                ),
                "model": (
                    IO.STRING,
                    {
                        "options": [model.value for model in LumaImageModel],
                        "default": LumaImageModel.photon_1.value,
                        "tooltip": "Luma model to use.",
                    },
                ),
                "seed": (
                    IO.INT,
                    {
                        "default": 0,
                        "min": 0,
                        "max": 0xFFFFFFFFFFFFFFFF,
                        "control_after_generate": True,
                        "tooltip": "Seed to determine if node should re-run; actual results are nondeterministic regardless of seed.",
                    },
                ),
            },
            "optional": {},
        }

    def api_call(
        self,
        prompt: str,
        model: str,
        image: torch.Tensor,
        image_weight: float,
        seed: int,
        unique_id: Optional[str] = None,
        **kwargs,
    ) -> tuple[torch.Tensor]:
        # first, upload image
        download_urls = upload_images_to_comfyapi(
            image, max_images=1, auth_kwargs=kwargs,
        )
        image_url = download_urls[0]
        # next, make Luma call with download url provided
        operation = SynchronousOperation(
            endpoint=ApiEndpoint(
                path="/proxy/luma/generations/image",
                method=HttpMethod.POST,
                request_model=LumaImageGenerationRequest,
                response_model=LumaGeneration,
            ),
            request=LumaImageGenerationRequest(
                prompt=prompt,
                model=LumaImageModel(model),
                aspect_ratio=None,
                image_ref=None,
                style_ref=None,
                character_ref=None,
                modify_image_ref=LumaModifyImageRef(
                    url=image_url, weight=round(max(min(1.0-image_weight, 0.98), 0.0), 2)
                ),
            ),
            auth_kwargs=kwargs,
        )
        response_api: LumaGeneration = operation.execute()

        operation = PollingOperation(
            poll_endpoint=ApiEndpoint(
                path=f"/proxy/luma/generations/{response_api.id}",
                method=HttpMethod.GET,
                request_model=EmptyRequest,
                response_model=LumaGeneration,
            ),
            completed_statuses=[LumaState.completed],
            failed_statuses=[LumaState.failed],
            status_extractor=lambda x: x.state,
            result_url_extractor=image_result_url_extractor,
            node_id=unique_id,
            progress_extractor=lambda x: 1.0 if getattr(x, "state", None) == LumaState.completed else 0.0,
            auth_kwargs=kwargs,
        )
        response_poll = operation.execute()

        image_url = getattr(getattr(response_poll, "assets", None), "image", None)
        if not image_url:
            raise RuntimeError("No image URL found in response_poll.assets.image")
        img_response = requests.get(image_url)
        img_response.raise_for_status()
        img = process_image_response(img_response)
        return (img,)


class LumaTextToVideoGenerationNode(ComfyNodeABC):
    """Generates videos synchronously based on prompt and output_size.
    
    This node uses the Luma API to generate videos from text prompts.
    It supports various models, resolutions, and durations.
    
    Attributes:
        RETURN_TYPES: Tuple of (IO.VIDEO,) indicating video output
        API_NODE: True to mark this as an API-dependent node
        CATEGORY: UI category for the node
        
    Notes:
        - The ray_1_6 model has specific resolution and duration constraints
        - Generation time varies based on video length and complexity
        - Progress is reported via the PromptServer if unique_id is provided
    """

    RETURN_TYPES = (IO.VIDEO,)
    DESCRIPTION = cleandoc(__doc__ or "")  # Handle potential None value
    FUNCTION = "api_call"
    API_NODE = True
    CATEGORY = "api node/video/Luma"

    @classmethod
    def INPUT_TYPES(cls) -> InputTypeDict:
        return {
            "required": {
                "prompt": (
                    IO.STRING,
                    {
                        "multiline": True,
                        "default": "",
                        "tooltip": "Prompt for the video generation",
                    },
                ),
                "model": (
                    IO.STRING,
                    {
                        "options": [model.value for model in LumaVideoModel],
                        "default": LumaVideoModel.ray_1_6.value,
                        "tooltip": "Luma video model to use.",
                    },
                ),
                "aspect_ratio": (
                    IO.STRING,
                    {
                        "options": [ratio.value for ratio in LumaAspectRatio],
                        "default": LumaAspectRatio.ratio_16_9.value,
                        "tooltip": "Aspect ratio of the generated video.",
                    },
                ),
                "resolution": (
                    IO.STRING,
                    {
                        "options": [resolution.value for resolution in LumaVideoOutputResolution],
                        "default": LumaVideoOutputResolution.res_540p.value,
                        "tooltip": "Output resolution.",
                    },
                ),
                "duration": (
                    IO.STRING,
                    {
                        "options": [dur.value for dur in LumaVideoModelOutputDuration],
                        "default": list(LumaVideoModelOutputDuration)[0].value,
                        "tooltip": "Video duration.",
                    },
                ),
                "loop": (
                    IO.BOOLEAN,
                    {
                        "default": False,
                        "tooltip": "Loop video output.",
                    },
                ),
                "seed": (
                    IO.INT,
                    {
                        "default": 0,
                        "min": 0,
                        "max": 0xFFFFFFFFFFFFFFFF,
                        "control_after_generate": True,
                        "tooltip": "Seed to determine if node should re-run; actual results are nondeterministic regardless of seed.",
                    },
                ),
            },
            "optional": {
                "luma_concepts": (
                    IO.STRING,
                    {
                        "tooltip": "Serialized Luma Concept Chain (string).",
                    },
                ),
            },
        }

    def api_call(
        self,
        prompt: str,
        model: str,
        aspect_ratio: str,
        resolution: str,
        duration: str,
        loop: bool,
        seed: int,
        luma_concepts: Optional[LumaConceptChain] = None,
        unique_id: Optional[str] = None,
        **kwargs,
    ) -> tuple[VideoFromFile]:
        """Generate a video using the Luma API.
        
        Args:
            prompt: Text description of the video to generate
            model: Luma video model to use
            aspect_ratio: Desired aspect ratio (e.g., "16:9")
            resolution: Output resolution (e.g., "540p")
            duration: Video length (e.g., "2_seconds")
            loop: Whether to create a seamlessly looping video
            seed: Random seed (affects node execution only)
            luma_concepts: Optional chain of camera movement concepts
            unique_id: Optional ID for progress tracking
            **kwargs: Additional arguments passed to API calls
            
        Returns:
            tuple[VideoFromFile]: Generated video as a single-element tuple
            
        Raises:
            ValueError: If prompt is invalid or enum options are missing
            RuntimeError: If API calls fail or response is invalid
        """
        validate_string(prompt, strip_whitespace=False, min_length=3)

        # Cache and validate enum options
        duration_options = list(LumaVideoModelOutputDuration)
        resolution_options = list(LumaVideoOutputResolution)

        # Comprehensive validation of enum values
        if not duration_options:
            raise ValueError(
                "No valid duration options available for video generation. "
                "LumaVideoModelOutputDuration enum must have at least one value defined."
            )
        if not resolution_options:
            raise ValueError(
                "No valid resolution options available for video generation. "
                "LumaVideoOutputResolution enum must have at least one value defined."
            )

        # Handle ray_1_6 model constraints with safe list access
        try:
            default_duration = duration_options[0].value
            default_resolution = resolution_options[0].value
        except (IndexError, AttributeError) as e:
            raise ValueError(
                "Failed to access default enum values. This should not happen as we already "
                "checked for empty lists. Please report this as a bug."
            ) from e

        duration_val = duration if model != LumaVideoModel.ray_1_6.value else default_duration
        resolution_val = resolution if model != LumaVideoModel.ray_1_6.value else default_resolution

        # Validate selected options
        if duration_val not in [opt.value for opt in duration_options]:
            raise ValueError(f"Invalid duration '{duration_val}'. Must be one of: {[opt.value for opt in duration_options]}")
        if resolution_val not in [opt.value for opt in resolution_options]:
            raise ValueError(f"Invalid resolution '{resolution_val}'. Must be one of: {[opt.value for opt in resolution_options]}")
        if aspect_ratio not in [ratio.value for ratio in LumaAspectRatio]:
            raise ValueError(f"Invalid aspect ratio '{aspect_ratio}'. Must be one of: {[ratio.value for ratio in LumaAspectRatio]}")

        operation = SynchronousOperation(
            endpoint=ApiEndpoint(
                path="/proxy/luma/generations",
                method=HttpMethod.POST,
                request_model=LumaGenerationRequest,
                response_model=LumaGeneration,
            ),
            request=LumaGenerationRequest(
                prompt=prompt,
                model=LumaVideoModel(model),
                resolution=LumaVideoOutputResolution(resolution_val),
                aspect_ratio=LumaAspectRatio(aspect_ratio),
                duration=LumaVideoModelOutputDuration(duration_val),
                loop=loop,
                concepts=luma_concepts.create_api_model() if luma_concepts else None,
                keyframes=None,
            ),
            auth_kwargs=kwargs,
        )
        response_api: LumaGeneration = operation.execute()

        if unique_id:
            PromptServer.instance.send_progress_text(f"Luma video generation started: {response_api.id}", unique_id)

        operation = PollingOperation(
            poll_endpoint=ApiEndpoint(
                path=f"/proxy/luma/generations/{response_api.id}",
                method=HttpMethod.GET,
                request_model=EmptyRequest,
                response_model=LumaGeneration,
            ),
            completed_statuses=[LumaState.completed],
            failed_statuses=[LumaState.failed],
            status_extractor=lambda x: x.state,
            result_url_extractor=video_result_url_extractor,
            node_id=unique_id,
            estimated_duration=LUMA_T2V_AVERAGE_DURATION,
            progress_extractor=lambda x: 1.0 if getattr(x, "state", None) == LumaState.completed else 0.0,
            auth_kwargs=kwargs,
        )
        response_poll = operation.execute()

        video_url = getattr(getattr(response_poll, "assets", None), "video", None)
        if not video_url:
            raise RuntimeError("No video URL found in response_poll.assets.video")
        vid_response = requests.get(video_url)
        vid_response.raise_for_status()
        return (VideoFromFile(BytesIO(vid_response.content)),)


class LumaImageToVideoGenerationNode(ComfyNodeABC):
    """
    Generates videos synchronously based on prompt, input images, and output_size.
    """

    RETURN_TYPES = (IO.VIDEO,)
    DESCRIPTION = cleandoc(__doc__ or "")  # Handle potential None value
    FUNCTION = "api_call"
    API_NODE = True
    CATEGORY = "api node/video/Luma"

    @classmethod
    def INPUT_TYPES(cls) -> InputTypeDict:
        return {
            "required": {
                "prompt": (
                    IO.STRING,
                    {
                        "multiline": True,
                        "default": "",
                        "tooltip": "Prompt for the video generation",
                    },
                ),
                "model": (
                    IO.STRING,
                    {
                        "options": [model.value for model in LumaVideoModel],
                        "default": LumaVideoModel.ray_1_6.value,
                        "tooltip": "Luma video model to use.",
                    },
                ),
                "resolution": (
                    IO.STRING,
                    {
                        "options": [resolution.value for resolution in LumaVideoOutputResolution],
                        "default": LumaVideoOutputResolution.res_540p.value,
                        "tooltip": "Output resolution.",
                    },
                ),
                "duration": (
                    IO.STRING,
                    {
                        "options": [dur.value for dur in LumaVideoModelOutputDuration],
                        "default": list(LumaVideoModelOutputDuration)[0].value,
                        "tooltip": "Video duration.",
                    },
                ),
                "loop": (
                    IO.BOOLEAN,
                    {
                        "default": False,
                        "tooltip": "Loop video output.",
                    },
                ),
                "seed": (
                    IO.INT,
                    {
                        "default": 0,
                        "min": 0,
                        "max": 0xFFFFFFFFFFFFFFFF,
                        "control_after_generate": True,
                        "tooltip": "Seed to determine if node should re-run; actual results are nondeterministic regardless of seed.",
                    },
                ),
            },
            "optional": {
                "first_image": (
                    IO.IMAGE,
                    {"tooltip": "First frame of generated video."},
                ),
                "last_image": (
                    IO.IMAGE,
                    {"tooltip": "Last frame of generated video."},
                ),
                "luma_concepts": (
                    IO.STRING,
                    {
                        "tooltip": "Serialized Luma Concept Chain (string).",
                    },
                ),
            },
        }

    def api_call(
        self,
        prompt: str,
        model: str,
        resolution: str,
        duration: str,
        loop: bool,
        seed: int,
        first_image: Optional[torch.Tensor] = None,
        last_image: Optional[torch.Tensor] = None,
        luma_concepts: Optional[LumaConceptChain] = None,
        unique_id: Optional[str] = None,
        **kwargs,
    ) -> tuple[VideoFromFile]:
        if first_image is None and last_image is None:
            raise ValueError("At least one of first_image and last_image requires an input.")
        keyframes = self._convert_to_keyframes(first_image, last_image, auth_kwargs=kwargs)

        # Cache and validate enum options
        duration_options = list(LumaVideoModelOutputDuration)
        resolution_options = list(LumaVideoOutputResolution)

        # Comprehensive validation of enum values
        if not duration_options:
            raise ValueError(
                "No valid duration options available for image-to-video generation. "
                "LumaVideoModelOutputDuration enum must have at least one value defined."
            )
        if not resolution_options:
            raise ValueError(
                "No valid resolution options available for image-to-video generation. "
                "LumaVideoOutputResolution enum must have at least one value defined."
            )

        # Get default values safely
        try:
            default_duration = next((opt.value for opt in duration_options), None)
            default_resolution = next((opt.value for opt in resolution_options), None)
            if default_duration is None or default_resolution is None:
                raise ValueError("Failed to get default values from enums")
        except Exception as e:
            raise ValueError(
                "Failed to access default enum values. This should not happen as we already "
                f"checked for empty lists. Original error: {str(e)}"
            ) from e

        # Handle ray_1_6 model constraints
        duration_val = duration if model != LumaVideoModel.ray_1_6 else default_duration
        resolution_val = resolution if model != LumaVideoModel.ray_1_6 else default_resolution

        operation = SynchronousOperation(
            endpoint=ApiEndpoint(
                path="/proxy/luma/generations",
                method=HttpMethod.POST,
                request_model=LumaGenerationRequest,
                response_model=LumaGeneration,
            ),
            request=LumaGenerationRequest(
                prompt=prompt,
                model=LumaVideoModel(model),
                aspect_ratio=LumaAspectRatio.ratio_16_9,  # ignored, but still needed by the API for some reason
                resolution=LumaVideoOutputResolution(resolution_val),
                duration=LumaVideoModelOutputDuration(duration_val),
                loop=loop,
                keyframes=keyframes,
                concepts=luma_concepts.create_api_model() if luma_concepts else None,
            ),
            auth_kwargs=kwargs,
        )
        response_api: LumaGeneration = operation.execute()

        if unique_id:
            PromptServer.instance.send_progress_text(f"Luma video generation started: {response_api.id}", unique_id)

        operation = PollingOperation(
            poll_endpoint=ApiEndpoint(
                path=f"/proxy/luma/generations/{response_api.id}",
                method=HttpMethod.GET,
                request_model=EmptyRequest,
                response_model=LumaGeneration,
            ),
            completed_statuses=[LumaState.completed],
            failed_statuses=[LumaState.failed],
            status_extractor=lambda x: x.state,
            result_url_extractor=video_result_url_extractor,
            node_id=unique_id,
            estimated_duration=LUMA_I2V_AVERAGE_DURATION,
            progress_extractor=lambda x: 1.0 if getattr(x, "state", None) == LumaState.completed else 0.0,
            auth_kwargs=kwargs,
        )
        response_poll = operation.execute()

        video_url = getattr(getattr(response_poll, "assets", None), "video", None)
        if not video_url:
            raise RuntimeError("No video URL found in response_poll.assets.video")
        vid_response = requests.get(video_url)
        vid_response.raise_for_status()
        return (VideoFromFile(BytesIO(vid_response.content)),)

    def _convert_to_keyframes(
        self,
        first_image: Optional[torch.Tensor] = None,
        last_image: Optional[torch.Tensor] = None,
        auth_kwargs: Optional[dict[str,str]] = None,
    ):
        if first_image is None and last_image is None:
            return None
        frame0 = None
        frame1 = None
        if first_image is not None:
            download_urls = upload_images_to_comfyapi(
                first_image, max_images=1, auth_kwargs=auth_kwargs,
            )
            frame0 = LumaImageReference(type="image", url=download_urls[0])
        if last_image is not None:
            download_urls = upload_images_to_comfyapi(
                last_image, max_images=1, auth_kwargs=auth_kwargs,
            )
            frame1 = LumaImageReference(type="image", url=download_urls[0])
        return LumaKeyframes(frame0=frame0, frame1=frame1)


class LumaText2ImgNode(ComfyNodeABC):
    """
    Generates images using Luma's text-to-image API.

    This node chains after a CLIPTextEncode block and outputs a valid image.
    Requires LUMA_API_KEY environment variable to be set.

    Parameters:
    - prompt: Text prompt for image generation
    - model: Luma model to use (photon-1, photon-flash-1)
    - aspect_ratio: Aspect ratio of the generated image
    - seed: Random seed for generation (affects node re-execution, not actual results)

    API Key Setup:
    Set the LUMA_API_KEY environment variable with your Luma API key.
    Example: export LUMA_API_KEY="your_api_key_here"
    """

    RETURN_TYPES = (IO.IMAGE,)
    DESCRIPTION = cleandoc(__doc__ or "")
    FUNCTION = "api_call"
    API_NODE = True
    CATEGORY = "api node/image/Luma"

    @classmethod
    def INPUT_TYPES(cls) -> InputTypeDict:
        return {
            "required": {
                "prompt": (
                    IO.STRING,
                    {
                        "multiline": True,
                        "default": "",
                        "tooltip": "Prompt for the image generation",
                    },
                ),
                "model": (
                    IO.STRING,
                    {
                        "options": [model.value for model in LumaImageModel],
                        "default": LumaImageModel.photon_1.value,
                        "tooltip": "Luma model to use.",
                    },
                ),
                "aspect_ratio": (
                    IO.STRING,
                    {
                        "options": [ratio.value for ratio in LumaAspectRatio],
                        "default": LumaAspectRatio.ratio_16_9.value,
                        "tooltip": "Aspect ratio of the generated image.",
                    },
                ),
                "seed": (
                    IO.INT,
                    {
                        "default": 0,
                        "min": 0,
                        "max": 0xFFFFFFFFFFFFFFFF,
                        "control_after_generate": True,
                        "tooltip": "Seed to determine if node should re-run; actual results are nondeterministic regardless of seed.",
                    },
                ),
            },
            "optional": {},
        }

    def api_call(
        self,
        prompt: str,
        model: str,
        aspect_ratio: str,
        seed: int,
        unique_id: Optional[str] = None,
        **kwargs,
    ) -> tuple[torch.Tensor]:
        validate_string(prompt, strip_whitespace=True, min_length=3)
        
        operation = SynchronousOperation(
            endpoint=ApiEndpoint(
                path="/proxy/luma/generations/image",
                method=HttpMethod.POST,
                request_model=LumaImageGenerationRequest,
                response_model=LumaGeneration,
            ),
            request=LumaImageGenerationRequest(
                prompt=prompt,
                model=LumaImageModel(model),
                aspect_ratio=LumaAspectRatio(aspect_ratio),
                image_ref=None,
                style_ref=None,
                character_ref=None,
                modify_image_ref=None,
            ),
            auth_kwargs=kwargs,
        )
        response_api: LumaGeneration = operation.execute()

        operation = PollingOperation(
            poll_endpoint=ApiEndpoint(
                path=f"/proxy/luma/generations/{response_api.id}",
                method=HttpMethod.GET,
                request_model=EmptyRequest,
                response_model=LumaGeneration,
            ),
            completed_statuses=[LumaState.completed],
            failed_statuses=[LumaState.failed],
            status_extractor=lambda x: x.state,
            result_url_extractor=image_result_url_extractor,
            node_id=unique_id,
            progress_extractor=lambda x: 1.0 if getattr(x, "state", None) == LumaState.completed else 0.0,
            auth_kwargs={"luma_api_key": api_key},
        )

        response_poll = operation.execute()

        # Download and return image
        image_url = getattr(getattr(response_poll, "assets", None), "image", None)
        if not image_url:
            raise RuntimeError("No image URL found in response_poll.assets.image")
        img_response = requests.get(image_url)
        img_response.raise_for_status()
        img = process_image_response(img_response)
        return (img,)


# A dictionary that contains all nodes you want to export with their names
# NOTE: names should be globally unique
NODE_CLASS_MAPPINGS = {
    "LumaImageNode": LumaImageGenerationNode,
    "LumaImageModifyNode": LumaImageModifyNode,
    "LumaVideoNode": LumaTextToVideoGenerationNode,
    "LumaImageToVideoNode": LumaImageToVideoGenerationNode,
    "LumaReferenceNode": LumaReferenceNode,
    "LumaConceptsNode": LumaConceptsNode,
    "LumaText2ImgNode": LumaText2ImgNode,
}

# A dictionary that contains the friendly/humanly readable titles for the nodes
NODE_DISPLAY_NAME_MAPPINGS = {
    "LumaImageNode": "Luma Text to Image",
    "LumaImageModifyNode": "Luma Image to Image",
    "LumaVideoNode": "Luma Text to Video",
    "LumaImageToVideoNode": "Luma Image to Video",
    "LumaReferenceNode": "Luma Reference",
    "LumaConceptsNode": "Luma Concepts",
    "LumaText2ImgNode": "Luma Text to Image (Direct)",
}
