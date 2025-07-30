"""
API nodes for external service integrations.
"""

from .runway_text2img import RunwayText2ImgNode

__all__ = ["RunwayText2ImgNode"]

# Node class mappings for ComfyUI registration
NODE_CLASS_MAPPINGS = {
    "RunwayText2Img": RunwayText2ImgNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "RunwayText2Img": "Runway Text to Image",
} 