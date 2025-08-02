import os
import requests
from PIL import Image
from io import BytesIO

class RunwayTextToImage:
    """
    Runway Text-to-Image Node for ComfyUI

    Parameters:
        prompt (str): The text prompt for image generation.
        poll_timeout (int): Timeout (in seconds) for the image download. Default is 30.

    Requirements:
        Set the RUNWAY_API_KEY as an environment variable.

    Raises:
        RuntimeError: If API key is not set or any HTTP error occurs.
    """

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {"multiline": True}),
                "poll_timeout": ("INT", {"default": 30}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "generate"
    CATEGORY = "DreamLayer/API"

    def generate(self, prompt, poll_timeout=30):
        api_key = os.getenv("RUNWAY_API_KEY")
        if not api_key:
            raise RuntimeError("RUNWAY_API_KEY not found. Please set it as an environment variable.")

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }
        payload = {"prompt": prompt}

        try:
            response = requests.post(
                "https://api.dev.runwayml.com/v1/text_to_image",
                json=payload,
                headers=headers,
                timeout=10,
            )
            response.raise_for_status()
            image_url = response.json()["image_url"]

            image_response = requests.get(image_url, timeout=poll_timeout)
            image_response.raise_for_status()
            image = Image.open(BytesIO(image_response.content)).convert("RGB")

            return (image,)
        except Exception as e:
            raise RuntimeError(f"Runway API error: {str(e)}")
