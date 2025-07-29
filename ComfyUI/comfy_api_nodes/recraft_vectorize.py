from __future__ import annotations
from inspect import cleandoc
import hashlib
import os
import logging
import torch
import numpy as np
from PIL import Image
from comfy.comfy_types.node_typing import IO
from comfy.utils import ProgressBar
from .nodes_recraft import handle_recraft_file_request

logger = logging.getLogger(__name__)

class RecraftVectorizeNode:
    """
    Vectorizes a batch of raster images using the Recraft API and saves them as pure-vector SVG files.
    """
    DESCRIPTION = cleandoc(__doc__ or "")
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("svg_file_paths",)
    FUNCTION = "execute"
    CATEGORY = "api node/image/Recraft"
    API_NODE = True

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": (IO.IMAGE,),
                "resolution_limit": (
                    IO.INT, {
                        "default": 2048, "min": 128, "max": 4096, "step": 64,
                        "tooltip": "Warns if an input image's resolution exceeds this limit. High-resolution images can impact performance."
                    }
                ),
                 "output_path": (
                    IO.STRING, {
                        "default": "output/vectorized_svgs",
                        "tooltip": "The directory where the output SVG files will be saved."
                    }
                ),
            },
            "hidden": {
                "auth_token": "AUTH_TOKEN_COMFY_ORG",
                "comfy_api_key": "API_KEY_COMFY_ORG",
            },
        }

    def execute(self, image: torch.Tensor, resolution_limit: int, output_path: str, **kwargs) -> tuple[str]:
        if image.shape[0] == 0:
            return ("",)

        # Create the output directory once
        if not os.path.exists(output_path):
            os.makedirs(output_path, exist_ok=True)

        pbar = ProgressBar(image.shape[0])
        all_file_paths = []

        # Loop through each image in the batch for processing
        for i in range(image.shape[0]):
            img_tensor_single = image[i].unsqueeze(0)
            pbar.update(1)
            image_hash = hashlib.sha256(img_tensor_single.cpu().numpy().tobytes()).hexdigest()
            img_array = np.clip(255. * img_tensor_single.cpu().numpy().squeeze(), 0, 255).astype(np.uint8)
            pil_image = Image.fromarray(img_array)

            if pil_image.width > resolution_limit or pil_image.height > resolution_limit:
                logger.warning(f"Image {i+1} resolution ({pil_image.width}x{pil_image.height}) exceeds the recommended limit of {resolution_limit}px.")

            try:
                svg_bytes_list = handle_recraft_file_request(
                    image=img_tensor_single,
                    path="/proxy/recraft/images/vectorize",
                    auth_kwargs=kwargs,
                )
                if not svg_bytes_list:
                    raise ConnectionError(f"Recraft API did not return any data for image {i+1}.")

                svg_content = svg_bytes_list[0].getvalue().decode('utf-8')

            except Exception as e:
                raise ConnectionError(f"Failed to vectorize image {i+1}. Reason: {e}") from e

            # Save the SVG content to a file
            filename = f"vectorized_{image_hash[:16]}.svg"
            svg_file_path = os.path.join(output_path, filename)

            with open(svg_file_path, "w", encoding="utf-8") as f:
                f.write(svg_content)

            all_file_paths.append(svg_file_path)

        # Join all generated file paths into a single string for the output
        return ("\n".join(all_file_paths),)


# Node class mappings
NODE_CLASS_MAPPINGS = {
    "RecraftVectorizeNode": RecraftVectorizeNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "RecraftVectorizeNode": "Recraft Vectorize Image to File",
}
