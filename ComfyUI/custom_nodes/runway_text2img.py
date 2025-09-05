import os
import requests
from io import BytesIO
from PIL import Image
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))


from nodes import CLIPTextEncode

class RunwayText2Image(CLIPTextEncode):
    """
    RunwayText2Image Node

    Description:
        This node sends a prompt to Runway’s /v1/text_to_image endpoint to generate an image.
        It can be used in a ComfyUI graph after text-encoding nodes like CLIPTextEncode.

    Parameters:
        - prompt (str): Text prompt for image generation (default: "").
        - poll_timeout (int): Max time to wait for response in seconds (default: 60, min: 5, max: 300).

    Returns:
        - (IMAGE,): A tuple containing a PIL.Image in RGB format.

    Requirements:
        - Requires the RUNWAY_API_KEY environment variable to be set.
        If absent, a RuntimeError is raised with a clear message.

    Notes:
        - You can adjust the poll_timeout parameter to shorten or extend how long the node waits for a response from Runway’s API.

    API:
    - POST https://api.dev.runwayml.com/v1/text_to_image
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {"default": ""}),
                "poll_timeout": ("INT", {"default": 60, "min": 5, "max": 300}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "generate_image"

    def generate_image(self, prompt, poll_timeout):
        api_key = os.getenv("RUNWAY_API_KEY")
        if not api_key:
            raise RuntimeError("Missing environment variable: RUNWAY_API_KEY")

        headers = {"Authorization": f"Bearer {api_key}"}
        payload = {"prompt": prompt}

        try:
            response = requests.post(
                "https://api.dev.runwayml.com/v1/text_to_image",
                json=payload,
                headers=headers,
                timeout=poll_timeout
            )
            response.raise_for_status()
            image_url = response.json().get("image_url")
            if not image_url:
                raise ValueError("No image URL returned from Runway API")

            image_data = requests.get(image_url).content
            image = Image.open(BytesIO(image_data)).convert("RGB")

            return (image,)

        except Exception as e:
            raise RuntimeError(f"RunwayText2Image generation failed: {e}")

NODE_CLASS_MAPPINGS = {
    "RunwayText2Image": RunwayText2Image,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "RunwayText2Image": "Runway Text-to-Image",
}
