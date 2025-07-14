from PIL import Image

class PixVerseStylize:
    NAME = "PixVerseStylize"

    def __init__(self):
        self.allowed_styles = [
            "watercolor", "oil painting", "sketch", "manga", "cartoon",
            "cyberpunk", "pixel art", "charcoal", "realism", "pop art",
            "comic", "vintage", "pastel", "gothic", "anime", "steampunk",
            "neon", "3d render", "graffiti", "low poly"
        ]

    def process(self, image: Image.Image, style: str) -> Image.Image:
        if style not in self.allowed_styles:
            raise ValueError(
                f"Unsupported style '{style}'. Supported styles: {', '.join(self.allowed_styles)}"
            )
        return image  # Currently, it just returns the original image

NODE_CLASS_MAPPINGS = {
    "PixVerseStylize": PixVerseStylize
}
