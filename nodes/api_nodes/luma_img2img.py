import os
import requests
from PIL import Image
from io import BytesIO
from typing import Optional

import numpy as np

def tensor_to_image(tensor: np.ndarray) -> Image.Image:
    """Converts a 3xHxW tensor to a PIL image (RGB)."""
    tensor = np.clip(tensor * 255, 0, 255).astype(np.uint8)
    return Image.fromarray(np.transpose(tensor, (1, 2, 0)))

def image_to_tensor(image: Image.Image) -> np.ndarray:
    """Converts a PIL image to a 3xHxW float32 tensor scaled [0, 1]."""
    image = image.convert("RGB")
    arr = np.array(image).astype(np.float32) / 255.0
    return np.transpose(arr, (2, 0, 1))

class ComfyUIWarning(Exception):
    pass

class LumaImg2Img:
    """
    Luma Image-to-Image Node

    This node modifies an input image using the Luma API.

    Required env:
        LUMA_API_KEY (str) — your API key from Luma

    Inputs:
        image (Tensor) — input image tensor
        prompt (str) — prompt to guide the image generation

    Optional:
        image_weight (float) — [0.02, 1.0], default=0.5
        model (str) — default="luma-v3"
        aspect_ratio (str) — "1:1", "16:9", etc. Default: "1:1"
        seed (int) — random seed for reproducibility
        timeout (float) — request timeout in seconds

    Output:
        modified_image (Tensor) — the returned image
    """
    def run(
        self,
        image,
        prompt: str,
        image_weight: float = 0.5,
        model: str = "luma-v3",
        aspect_ratio: str = "1:1",
        seed: Optional[int] = None,
        timeout: float = 30.0,
    ):
        api_key = os.getenv("LUMA_API_KEY")
        if not api_key:
            raise ComfyUIWarning("Missing $LUMA_API_KEY — set this in your environment or ~/.dreamlayer/keys.toml")

        # Convert image tensor to PNG byte stream
        pil_img = tensor_to_image(image)
        buffer = BytesIO()
        pil_img.save(buffer, format="PNG")
        buffer.seek(0)

        payload = {
            "prompt": prompt,
            "image_weight": image_weight,
            "model": model,
            "aspect_ratio": aspect_ratio,
        }

        if seed is not None:
            payload["seed"] = seed

        files = {"image": ("image.png", buffer, "image/png")}
        headers = {"Authorization": f"Bearer {api_key}"}

        response = requests.post(
            "https://api.luma.ai/proxy/luma/generations/image",
            headers=headers,
            data=payload,
            files=files,
            timeout=timeout
        )

        if not response.ok:
            raise RuntimeError(f"Luma API failed: {response.status_code} {response.text}")

        result_image = Image.open(BytesIO(response.content)).convert("RGB")
        return {"image": image_to_tensor(result_image)}
