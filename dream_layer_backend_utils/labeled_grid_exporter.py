#!/usr/bin/env python3
"""
Labeled Grid Exporter - Enhanced Version with CLIP Integration

Creates labeled image grids with support for multiple formats, preprocessing,
batch processing, and CLIP-based auto-labeling.

This module provides a comprehensive solution for organizing AI-generated images
into visually appealing grids with metadata labels, supporting both manual CSV
metadata and automatic CLIP-based labeling.

Author: DreamLayer Open Source Challenge
License: MIT
"""

import argparse
import csv
import json
import logging
import os
from pathlib import Path
from typing import Callable, Dict, List, Tuple

import torch
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

# Configure logging with better formatting
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Supported image formats with case-insensitive matching
SUPPORTED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".tiff",
    ".tif",
    ".webp",
    ".gif",
}

# Default configuration constants
DEFAULT_CELL_SIZE = (256, 256)
DEFAULT_MARGIN = 10
DEFAULT_FONT_SIZE = 16
DEFAULT_BACKGROUND_COLOR = (255, 255, 255)
DEFAULT_CLIP_MODEL = "openai/clip-vit-base-patch32"
DEFAULT_EXPORT_FORMAT = "png"

# Font paths for cross-platform compatibility
FONT_PATHS = [
    # Windows
    "C:/Windows/Fonts/arial.ttf",
    "C:/Windows/Fonts/calibri.ttf",
    "C:/Windows/Fonts/tahoma.ttf",
    # macOS
    "/System/Library/Fonts/Arial.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
    # Linux
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "/usr/share/fonts/TTF/arial.ttf",
    "/usr/share/fonts/truetype/arial.ttf",
]


class CLIPLabeler:
    """
    CLIP-based image labeling for automatic caption generation.

    This class provides automatic image labeling using OpenAI's CLIP model,
    supporting zero-shot classification and caption generation for images
    without requiring explicit training data.
    """

    def __init__(self, model_name: str = DEFAULT_CLIP_MODEL, device: str = None):
        """
        Initialize CLIP model for image labeling.

        Args:
            model_name: CLIP model to use (default: openai/clip-vit-base-patch32)
            device: Device to run model on (default: auto-detect CUDA/CPU)
        """
        self.model_name = model_name
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.model = None
        self.processor = None
        self.tokenizer = None
        self._is_loaded = False
        # Defer model loading until first use for better performance

    def _load_model(self):
        """Load CLIP model and processor"""
        try:
            from transformers import CLIPProcessor, CLIPModel

            logger.info(f"Loading CLIP model: {self.model_name}")
            self.model = CLIPModel.from_pretrained(self.model_name)
            self.processor = CLIPProcessor.from_pretrained(self.model_name)
            self.tokenizer = self.processor.tokenizer

            self.model.to(self.device)
            self.model.eval()
            logger.info(f"CLIP model loaded successfully on {self.device}")

        except ImportError:
            logger.error(
                "transformers library not found. Please install: pip install transformers"
            )
            raise
        except Exception as e:
            logger.error(f"Failed to load CLIP model: {str(e)}")
            raise

    def _get_caption_candidates(self) -> List[str]:
        """
        Get a comprehensive list of caption candidates for zero-shot classification.

        Returns:
            List of descriptive caption candidates covering various image types
        """
        return [
            # Nature and landscapes
            "a beautiful landscape",
            "a mountain view",
            "an ocean scene",
            "a forest",
            "a sunset",
            "a beach",
            "a garden",
            "a park",
            "a flower",
            "a tree",
            # People and portraits
            "a portrait of a person",
            "a group of people",
            "a child",
            "an adult",
            "a professional portrait",
            "a candid photo",
            # Animals
            "an animal",
            "a bird",
            "a cat",
            "a dog",
            "a horse",
            "a fish",
            "a wild animal",
            "a domestic pet",
            # Buildings and architecture
            "a building",
            "a house",
            "an apartment",
            "a skyscraper",
            "a bridge",
            "a monument",
            "a statue",
            "a church",
            "a castle",
            # Transportation
            "a vehicle",
            "a car",
            "a train",
            "an airplane",
            "a boat",
            "a bicycle",
            "a motorcycle",
            "a bus",
            "a truck",
            # Urban scenes
            "an urban scene",
            "a city skyline",
            "a street",
            "a road",
            "a cityscape",
            "a downtown area",
            # Objects and items
            "a product",
            "furniture",
            "clothing",
            "electronics",
            "a computer",
            "a phone",
            "a camera",
            "a book",
            "food and drinks",
            # Art and media
            "a painting",
            "a photograph",
            "a cartoon",
            "a logo",
            "abstract art",
            "a sculpture",
            "a drawing",
            "digital art",
            # Activities and concepts
            "sports",
            "music",
            "text or writing",
            "a celebration",
            "work",
            "leisure",
            "technology",
            "nature",
            "architecture",
        ]

    def generate_label(self, image: Image.Image, max_length: int = 50) -> str:
        """
        Generate a descriptive label for an image using CLIP zero-shot classification.

        Args:
            image: PIL Image to label
            max_length: Maximum length of generated label (default: 50)

        Returns:
            Generated label string, or "unlabeled" if generation fails

        Raises:
            RuntimeError: If model loading fails and no fallback is available
        """
        # Ensure model is loaded
        if not self._is_loaded:
            try:
                self._load_model()
            except Exception as e:
                logger.warning(f"Failed to load CLIP model: {str(e)}")
                return "unlabeled"

        try:
            # Prepare image
            if image.mode != "RGB":
                image = image.convert("RGB")

            # Get caption candidates
            candidates = self._get_caption_candidates()

            # Process image and text
            inputs = self.processor(
                images=image,
                text=candidates,
                return_tensors="pt",
                padding=True,
                truncation=True,
            )

            # Move to device
            inputs = {k: v.to(self.device) for k, v in inputs.items()}

            # Get predictions
            with torch.no_grad():
                outputs = self.model(**inputs)
                logits_per_image = outputs.logits_per_image
                probs = logits_per_image.softmax(dim=-1)

            # Get top prediction
            top_idx = probs.argmax().item()
            confidence = probs[0][top_idx].item()

            # Get the best caption
            best_caption = candidates[top_idx]

            # If confidence is low, try to generate a more specific caption
            if confidence < 0.3:
                # Try with more specific prompts
                specific_prompts = [
                    "a detailed photograph of",
                    "an artistic image of",
                    "a professional photo of",
                    "a creative artwork of",
                ]

                best_specific = best_caption
                best_conf = confidence

                for prefix in specific_prompts:
                    full_prompt = f"{prefix} {best_caption}"
                    inputs = self.processor(
                        images=image,
                        text=[full_prompt],
                        return_tensors="pt",
                        padding=True,
                        truncation=True,
                    )
                    inputs = {k: v.to(self.device) for k, v in inputs.items()}

                    with torch.no_grad():
                        outputs = self.model(**inputs)
                        logits = outputs.logits_per_image
                        prob = logits.softmax(dim=-1)[0][0].item()

                        if prob > best_conf:
                            best_conf = prob
                            best_specific = full_prompt

                best_caption = best_specific

            # Truncate if too long
            if len(best_caption) > max_length:
                best_caption = best_caption[: max_length - 3] + "..."

            return best_caption

        except Exception as e:
            logger.warning(f"Failed to generate CLIP label: {str(e)}")
            return "unlabeled"

    def batch_generate_labels(
        self, images: List[Image.Image], max_length: int = 50
    ) -> List[str]:
        """
        Generate labels for multiple images efficiently

        Args:
            images: List of PIL Images
            max_length: Maximum length of generated labels

        Returns:
            List of generated labels
        """
        labels = []
        for i, image in enumerate(images):
            logger.info(f"Generating label for image {i+1}/{len(images)}")
            label = self.generate_label(image, max_length)
            labels.append(label)
        return labels


class ImagePreprocessor:
    """Handles image preprocessing operations"""

    @staticmethod
    def resize_image(
        image: Image.Image, target_size: Tuple[int, int], mode: str = "fit"
    ) -> Image.Image:
        """Resize image with different modes"""
        if mode == "fit":
            # Fit within target size, maintaining aspect ratio
            image.thumbnail(target_size, Image.Resampling.LANCZOS)
        elif mode == "fill":
            # Fill target size, cropping if necessary
            image = image.resize(target_size, Image.Resampling.LANCZOS)
        elif mode == "stretch":
            # Stretch to exact target size
            image = image.resize(target_size, Image.Resampling.LANCZOS)
        return image

    @staticmethod
    def crop_image(
        image: Image.Image, crop_box: Tuple[int, int, int, int]
    ) -> Image.Image:
        """Crop image to specified box (left, top, right, bottom)"""
        return image.crop(crop_box)

    @staticmethod
    def apply_filter(
        image: Image.Image, filter_type: str, strength: float = 1.0
    ) -> Image.Image:
        """Apply various filters to image"""
        if filter_type == "blur":
            return image.filter(ImageFilter.GaussianBlur(radius=strength))
        elif filter_type == "sharpen":
            return image.filter(ImageFilter.UnsharpMask(radius=strength, percent=150))
        elif filter_type == "emboss":
            return image.filter(ImageFilter.EMBOSS)
        elif filter_type == "edge_enhance":
            return image.filter(ImageFilter.EDGE_ENHANCE)
        return image

    @staticmethod
    def adjust_brightness(image: Image.Image, factor: float) -> Image.Image:
        """Adjust image brightness"""
        enhancer = ImageEnhance.Brightness(image)
        return enhancer.enhance(factor)

    @staticmethod
    def adjust_contrast(image: Image.Image, factor: float) -> Image.Image:
        """Adjust image contrast"""
        enhancer = ImageEnhance.Contrast(image)
        return enhancer.enhance(factor)

    @staticmethod
    def adjust_saturation(image: Image.Image, factor: float) -> Image.Image:
        """Adjust image saturation"""
        enhancer = ImageEnhance.Color(image)
        return enhancer.enhance(factor)


class GridTemplate:
    """Manages grid layout templates"""

    def __init__(
        self,
        name: str,
        rows: int,
        cols: int,
        cell_size: Tuple[int, int],
        margin: int = 10,
        font_size: int = 16,
    ):
        self.name = name
        self.rows = rows
        self.cols = cols
        self.cell_size = cell_size
        self.margin = margin
        self.font_size = font_size

    def to_dict(self) -> Dict:
        """Convert template to dictionary"""
        return {
            "name": self.name,
            "rows": self.rows,
            "cols": self.cols,
            "cell_size": self.cell_size,
            "margin": self.margin,
            "font_size": self.font_size,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "GridTemplate":
        """Create template from dictionary"""
        return cls(
            name=data["name"],
            rows=data["rows"],
            cols=data["cols"],
            cell_size=tuple(data["cell_size"]),
            margin=data.get("margin", 10),
            font_size=data.get("font_size", 16),
        )


class BatchProcessor:
    """Handles batch processing of multiple directories"""

    def __init__(self, output_base_dir: str):
        self.output_base_dir = output_base_dir
        os.makedirs(output_base_dir, exist_ok=True)

    def process_batch(
        self,
        input_dirs: List[str],
        template: GridTemplate,
        label_columns: List[str] = None,
        csv_path: str = None,
        export_format: str = "png",
        preprocessing: Dict = None,
        use_clip: bool = False,
        clip_model: str = "openai/clip-vit-base-patch32",
    ) -> List[Dict]:
        """Process multiple input directories with optional CLIP auto-labeling"""
        results = []

        for input_dir in input_dirs:
            if not os.path.exists(input_dir):
                logger.warning(f"Input directory not found: {input_dir}")
                continue

            # Create output filename based on input directory name
            dir_name = os.path.basename(input_dir)
            output_filename = f"{dir_name}_grid.{export_format}"
            output_path = os.path.join(self.output_base_dir, output_filename)

            try:
                # Process single directory
                result = assemble_grid_enhanced(
                    input_dir=input_dir,
                    output_path=output_path,
                    template=template,
                    label_columns=label_columns or [],
                    csv_path=csv_path,
                    export_format=export_format,
                    preprocessing=preprocessing,
                    use_clip=use_clip,
                    clip_model=clip_model,
                )
                result["input_dir"] = input_dir
                result["output_path"] = output_path
                results.append(result)

            except Exception as e:
                logger.error(f"Error processing {input_dir}: {str(e)}")
                results.append(
                    {"input_dir": input_dir, "status": "error", "error": str(e)}
                )

        return results


def validate_inputs(input_dir: str, output_path: str, csv_path: str = None) -> bool:
    """
    Validate input parameters for grid generation.

    Args:
        input_dir: Path to directory containing images
        output_path: Path where output grid will be saved
        csv_path: Optional path to CSV metadata file

    Returns:
        True if all inputs are valid, False otherwise

    Raises:
        ValueError: If critical validation fails
    """
    # Validate input directory
    if not input_dir:
        logger.error("Input directory path is required")
        return False

    if not os.path.exists(input_dir):
        logger.error(f"Input directory does not exist: {input_dir}")
        return False

    if not os.path.isdir(input_dir):
        logger.error(f"Input path is not a directory: {input_dir}")
        return False

    # Validate output path
    if not output_path:
        logger.error("Output path is required")
        return False

    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir, exist_ok=True)
            logger.info(f"Created output directory: {output_dir}")
        except (OSError, PermissionError) as e:
            logger.error(f"Failed to create output directory {output_dir}: {str(e)}")
            return False

    # Validate CSV file if provided
    if csv_path and not os.path.exists(csv_path):
        logger.warning(f"CSV file not found: {csv_path}")
        # Don't return False here as CSV is optional

    return True


def _load_font(font_size: int) -> ImageFont.FreeTypeFont:
    """Enhanced font loading with multiple fallback options"""
    for font_path in FONT_PATHS:
        if os.path.exists(font_path):
            try:
                return ImageFont.truetype(font_path, font_size)
            except Exception as e:
                logger.debug(f"Failed to load font {font_path}: {str(e)}")
                continue

    logger.warning("No system fonts found, using default font")
    return ImageFont.load_default()


def read_metadata(csv_path: str) -> Dict[str, Dict]:
    """Enhanced CSV metadata reading with better error handling"""
    records = {}
    try:
        with open(csv_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                filename = row.get("filename", "")
                if filename:
                    records[filename] = row
    except UnicodeDecodeError:
        try:
            with open(csv_path, "r", encoding="latin-1") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    filename = row.get("filename", "")
                    if filename:
                        records[filename] = row
        except Exception as e:
            logger.error(f"Failed to read CSV file {csv_path}: {str(e)}")
            return {}
    except Exception as e:
        logger.error(f"Error reading CSV file {csv_path}: {str(e)}")
        return {}

    return records


def determine_grid(
    images_info: List[Dict], rows: int = None, cols: int = None
) -> Tuple[int, int]:
    """Determine optimal grid dimensions"""
    num_images = len(images_info)

    if rows and cols:
        if rows * cols < num_images:
            logger.warning(
                f"Specified grid ({rows}x{cols}={rows*cols}) is smaller than number of images ({num_images})"
            )
        return rows, cols

    # Auto-determine grid
    if rows:
        cols = (num_images + rows - 1) // rows
    elif cols:
        rows = (num_images + cols - 1) // cols
    else:
        # Find closest square-ish grid
        sqrt = int(num_images**0.5)
        if sqrt * sqrt >= num_images:
            rows = cols = sqrt
        else:
            rows = sqrt
            cols = (num_images + rows - 1) // rows

    return rows, cols


def collect_images(
    input_dir: str,
    csv_records: Dict[str, Dict] = None,
    clip_labeler: CLIPLabeler = None,
) -> List[Dict]:
    """
    Collect and process images from directory with optional metadata and CLIP labeling.

    Args:
        input_dir: Directory containing images
        csv_records: Optional dictionary of CSV metadata keyed by filename
        clip_labeler: Optional CLIP labeler for automatic labeling

    Returns:
        List of image information dictionaries

    Raises:
        OSError: If directory cannot be read
        ValueError: If no valid images are found
    """
    images_info = []
    supported_count = 0
    processed_count = 0

    try:
        # Get sorted list of files for consistent ordering
        file_list = sorted(os.listdir(input_dir))

        for filename in file_list:
            # Check if file has supported extension (case-insensitive)
            file_ext = Path(filename).suffix.lower()
            if file_ext not in SUPPORTED_EXTENSIONS:
                continue

            supported_count += 1
            file_path = os.path.join(input_dir, filename)

            try:
                # Open and validate image
                with Image.open(file_path) as img:
                    # Verify image can be loaded and converted
                    if img.mode not in ("RGB", "RGBA", "L", "P"):
                        img = img.convert("RGB")
                    elif img.mode == "RGBA":
                        # Convert RGBA to RGB with white background
                        background = Image.new("RGB", img.size, (255, 255, 255))
                        background.paste(
                            img, mask=img.split()[-1] if img.mode == "RGBA" else None
                        )
                        img = background

                    # Get metadata from CSV or generate with CLIP
                    metadata = csv_records.get(filename, {}) if csv_records else {}

                    # Generate CLIP label if no CSV metadata and CLIP is available
                    if not metadata and clip_labeler:
                        try:
                            auto_label = clip_labeler.generate_label(img)
                            metadata = {"auto_label": auto_label}
                            logger.debug(
                                f"Generated CLIP label for {filename}: {auto_label}"
                            )
                        except Exception as e:
                            logger.warning(
                                f"Failed to generate CLIP label for {filename}: {str(e)}"
                            )
                            metadata = {"auto_label": filename}  # Fallback to filename

                    # Store image information
                    images_info.append(
                        {
                            "path": file_path,
                            "filename": filename,
                            "image": img.copy(),
                            "metadata": metadata,
                        }
                    )
                    processed_count += 1

            except (OSError, IOError) as e:
                logger.warning(f"Failed to load image {filename}: {str(e)}")
                continue
            except Exception as e:
                logger.warning(f"Unexpected error loading {filename}: {str(e)}")
                continue

    except OSError as e:
        logger.error(f"Error reading directory {input_dir}: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error processing directory {input_dir}: {str(e)}")
        return []

    logger.info(
        f"Processed {processed_count}/{supported_count} supported images from {input_dir}"
    )

    if not images_info:
        raise ValueError(f"No valid images found in directory: {input_dir}")

    return images_info


def preprocess_images(images_info: List[Dict], preprocessing: Dict) -> List[Dict]:
    """Apply preprocessing to images"""
    if not preprocessing:
        return images_info

    preprocessor = ImagePreprocessor()
    processed_images = []

    for img_info in images_info:
        img = img_info["image"]

        # Apply resize
        if "resize" in preprocessing:
            resize_config = preprocessing["resize"]
            target_size = resize_config.get("size", (256, 256))
            mode = resize_config.get("mode", "fit")
            img = preprocessor.resize_image(img, target_size, mode)

        # Apply crop
        if "crop" in preprocessing:
            crop_box = preprocessing["crop"]
            img = preprocessor.crop_image(img, crop_box)

        # Apply filters
        if "filters" in preprocessing:
            for filter_config in preprocessing["filters"]:
                filter_type = filter_config.get("type")
                strength = filter_config.get("strength", 1.0)
                img = preprocessor.apply_filter(img, filter_type, strength)

        # Apply adjustments
        if "brightness" in preprocessing:
            img = preprocessor.adjust_brightness(img, preprocessing["brightness"])

        if "contrast" in preprocessing:
            img = preprocessor.adjust_contrast(img, preprocessing["contrast"])

        if "saturation" in preprocessing:
            img = preprocessor.adjust_saturation(img, preprocessing["saturation"])

        # Update image info
        img_info["image"] = img
        processed_images.append(img_info)

    return processed_images


def assemble_grid_enhanced(
    input_dir: str,
    output_path: str,
    template: GridTemplate,
    label_columns: List[str] = None,
    csv_path: str = None,
    export_format: str = "png",
    preprocessing: Dict = None,
    background_color: Tuple[int, int, int] = (255, 255, 255),
    progress_callback: Callable = None,
    use_clip: bool = False,
    clip_model: str = "openai/clip-vit-base-patch32",
) -> Dict:
    """Enhanced grid assembly with multiple export formats, preprocessing, and CLIP auto-labeling"""

    if not validate_inputs(input_dir, output_path, csv_path):
        raise ValueError(f"Invalid inputs: {input_dir}")

    # Initialize CLIP labeler if requested and no CSV provided
    clip_labeler = None
    if use_clip and not csv_path:
        try:
            clip_labeler = CLIPLabeler(model_name=clip_model)
            logger.info("CLIP auto-labeling enabled")
        except Exception as e:
            logger.warning(f"Failed to initialize CLIP labeler: {str(e)}")
            logger.info("Falling back to filename-based labels")

    # Read CSV metadata if provided
    csv_records = None
    if csv_path and os.path.exists(csv_path):
        csv_records = read_metadata(csv_path)

    # Collect images with CLIP labeling if enabled
    images_info = collect_images(input_dir, csv_records, clip_labeler)

    if not images_info:
        raise ValueError(f"No supported image files found in '{input_dir}'")

    # Apply preprocessing
    if preprocessing:
        images_info = preprocess_images(images_info, preprocessing)

    # Determine grid dimensions
    rows, cols = determine_grid(images_info, template.rows, template.cols)

    # Calculate cell size based on template
    cell_width, cell_height = template.cell_size

    # Calculate canvas size
    canvas_width = cols * cell_width + (cols + 1) * template.margin
    canvas_height = rows * cell_height + (rows + 1) * template.margin

    # Create canvas with background
    canvas = Image.new("RGB", (canvas_width, canvas_height), background_color)
    draw = ImageDraw.Draw(canvas)

    # Load font
    font = _load_font(template.font_size)

    # Place images in grid
    for i, img_info in enumerate(images_info):
        if i >= rows * cols:
            break

        row = i // cols
        col = i % cols

        # Calculate position
        x = template.margin + col * (cell_width + template.margin)
        y = template.margin + row * (cell_height + template.margin)

        # Resize image to fit cell
        img = img_info["image"]
        img.thumbnail((cell_width, cell_height), Image.Resampling.LANCZOS)

        # Center image in cell
        img_x = x + (cell_width - img.width) // 2
        img_y = y + (cell_height - img.height) // 2

        # Paste image
        canvas.paste(img, (img_x, img_y))

        # Add labels
        label_text = None
        if label_columns and img_info["metadata"]:
            # Use CSV labels if available
            try:
                labels = []
                for col_name in label_columns:
                    if col_name in img_info["metadata"]:
                        labels.append(f"{col_name}: {img_info['metadata'][col_name]}")

                if labels:
                    label_text = "\n".join(labels)
            except Exception as e:
                logger.warning(
                    f"Failed to process CSV labels for {img_info['filename']}: {str(e)}"
                )

        elif img_info["metadata"] and "auto_label" in img_info["metadata"]:
            # Use CLIP-generated label
            label_text = img_info["metadata"]["auto_label"]

        # Draw label if available
        if label_text:
            try:
                # Calculate text dimensions
                bbox = draw.textbbox((0, 0), label_text, font=font)
                text_width = bbox[2] - bbox[0]
                text_height = bbox[3] - bbox[1]

                # Position text at bottom of cell with padding
                text_x = x + (cell_width - text_width) // 2
                text_y = y + cell_height - text_height - 8

                # Ensure text doesn't go outside cell bounds
                text_x = max(x + 2, min(text_x, x + cell_width - text_width - 2))
                text_y = max(y + 2, min(text_y, y + cell_height - text_height - 2))

                # Draw text with enhanced visibility
                outline_color = (0, 0, 0)
                text_color = (255, 255, 255)

                # Draw outline for better contrast
                for dx in [-2, -1, 0, 1, 2]:
                    for dy in [-2, -1, 0, 1, 2]:
                        if dx != 0 or dy != 0:
                            draw.text(
                                (text_x + dx, text_y + dy),
                                label_text,
                                font=font,
                                fill=outline_color,
                            )

                # Draw main text
                draw.text((text_x, text_y), label_text, font=font, fill=text_color)

            except Exception as e:
                logger.warning(
                    f"Failed to draw label for {img_info['filename']}: {str(e)}"
                )
                # Fallback: draw simple text without outline
                try:
                    draw.text(
                        (x + 5, y + cell_height - 20),
                        label_text[:30],
                        font=font,
                        fill=(255, 255, 255),
                    )
                except (OSError, TypeError, AttributeError):
                    pass  # Skip label if all drawing methods fail

        # Update progress
        if progress_callback:
            progress_callback((i + 1) / len(images_info))

    # Save with specified format and quality
    save_kwargs = {}
    if export_format.lower() in ["jpg", "jpeg"]:
        save_kwargs["quality"] = 95
        save_kwargs["optimize"] = True
    elif export_format.lower() == "png":
        save_kwargs["optimize"] = True

    canvas.save(output_path, format=export_format.upper(), **save_kwargs)

    # Return result information
    return {
        "status": "success",
        "images_processed": len(images_info),
        "grid_dimensions": f"{rows}x{cols}",
        "canvas_size": f"{canvas_width}x{canvas_height}",
        "export_format": export_format,
    }


def assemble_grid(
    images_info: List[Dict],
    label_columns: List[str],
    output_path: str,
    rows: int = None,
    cols: int = None,
    font_size: int = 16,
    margin: int = 10,
    progress_callback: Callable = None,
) -> None:
    """Legacy function for backward compatibility"""
    template = GridTemplate(
        name="legacy",
        rows=rows or 3,
        cols=cols or 3,
        cell_size=(256, 256),
        margin=margin,
        font_size=font_size,
    )

    # Extract input_dir from first image
    input_dir = os.path.dirname(images_info[0]["path"]) if images_info else ""

    result = assemble_grid_enhanced(
        input_dir=input_dir,
        output_path=output_path,
        template=template,
        label_columns=label_columns,
    )

    return result


def save_template(template: GridTemplate, filepath: str) -> None:
    """Save grid template to file"""
    with open(filepath, "w") as f:
        json.dump(template.to_dict(), f, indent=2)


def load_template(filepath: str) -> GridTemplate:
    """Load grid template from file"""
    with open(filepath, "r") as f:
        data = json.load(f)
    return GridTemplate.from_dict(data)


def create_animated_grid(
    images_info: List[Dict],
    output_path: str,
    template: GridTemplate,
    label_columns: List[str] = None,
    duration: int = 500,
) -> None:
    """Create animated GIF grid"""
    # This is a placeholder for animation support
    # Would require more complex implementation with PIL's ImageSequence
    logger.info("Animation support coming soon!")


def main():
    """
    Enhanced command line interface for labeled grid generation with CLIP auto-labeling.

    This function provides a comprehensive CLI for creating labeled image grids,
    supporting both manual CSV metadata and automatic CLIP-based labeling.
    """
    parser = argparse.ArgumentParser(
        description="Create labeled image grids with enhanced features and CLIP auto-labeling",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic grid with CSV metadata
  python labeled_grid_exporter.py images/ output.png --csv metadata.csv --labels seed steps

  # Auto-labeling with CLIP (no CSV needed)
  python labeled_grid_exporter.py images/ output.png --use-clip --rows 3 --cols 3

  # Batch processing multiple directories
  python labeled_grid_exporter.py --batch dir1/ dir2/ dir3/ output/ --use-clip

  # Custom grid with specific settings
  python labeled_grid_exporter.py images/ output.png --cell-size 512 512 --margin 20 --font-size 24
        """,
    )

    # Required arguments
    parser.add_argument(
        "input_dir", nargs="?", help="Input directory containing images"
    )
    parser.add_argument("output_path", nargs="?", help="Output path for the grid image")

    # Metadata options
    parser.add_argument("--csv", help="CSV file with metadata")
    parser.add_argument("--labels", nargs="+", help="Column names to use as labels")

    # Grid layout options
    parser.add_argument("--rows", type=int, help="Number of rows in grid")
    parser.add_argument("--cols", type=int, help="Number of columns in grid")
    parser.add_argument(
        "--cell-size",
        nargs=2,
        type=int,
        default=DEFAULT_CELL_SIZE,
        help=f"Cell size (width height) (default: {DEFAULT_CELL_SIZE[0]} {DEFAULT_CELL_SIZE[1]})",
    )
    parser.add_argument(
        "--margin",
        type=int,
        default=DEFAULT_MARGIN,
        help=f"Margin between images (default: {DEFAULT_MARGIN})",
    )

    # Styling options
    parser.add_argument(
        "--font-size",
        type=int,
        default=DEFAULT_FONT_SIZE,
        help=f"Font size for labels (default: {DEFAULT_FONT_SIZE})",
    )
    parser.add_argument(
        "--background",
        nargs=3,
        type=int,
        default=DEFAULT_BACKGROUND_COLOR,
        help=f"Background color (R G B) (default: {DEFAULT_BACKGROUND_COLOR[0]} {DEFAULT_BACKGROUND_COLOR[1]} {DEFAULT_BACKGROUND_COLOR[2]})",
    )

    # Output options
    parser.add_argument(
        "--format",
        choices=["png", "jpg", "jpeg", "webp", "tiff"],
        default=DEFAULT_EXPORT_FORMAT,
        help=f"Output format (default: {DEFAULT_EXPORT_FORMAT})",
    )

    # Preprocessing options
    parser.add_argument(
        "--resize", nargs=2, type=int, help="Resize images (width height)"
    )
    parser.add_argument(
        "--resize-mode",
        choices=["fit", "fill", "stretch"],
        default="fit",
        help="Resize mode (default: fit)",
    )

    # Batch processing
    parser.add_argument("--batch", nargs="+", help="Process multiple directories")

    # Template options
    parser.add_argument("--template", help="Load template from file")
    parser.add_argument("--save-template", help="Save current settings as template")

    # CLIP auto-labeling options
    parser.add_argument(
        "--use-clip",
        action="store_true",
        help="Use CLIP to auto-generate labels when no CSV is provided",
    )
    parser.add_argument(
        "--clip-model",
        default=DEFAULT_CLIP_MODEL,
        help=f"CLIP model to use for auto-labeling (default: {DEFAULT_CLIP_MODEL})",
    )

    # Debug options
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    parser.add_argument(
        "--version", action="version", version="Labeled Grid Exporter 2.0"
    )

    args = parser.parse_args()

    # Set up logging
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Verbose logging enabled")

    # Validate arguments
    if args.batch:
        # Batch processing mode
        if len(args.batch) < 2:
            parser.error(
                "Batch processing requires at least 2 arguments: input directories and output directory"
            )
        input_dirs = args.batch[:-1]
        output_dir = args.batch[-1]
        logger.info(f"Batch processing {len(input_dirs)} directories to {output_dir}")
    else:
        # Single directory processing
        if not args.input_dir or not args.output_path:
            parser.error(
                "Both input_dir and output_path are required for single directory processing"
            )
        input_dirs = [args.input_dir]
        output_dir = os.path.dirname(args.output_path) or "."

    # Validate cell size
    if args.cell_size[0] <= 0 or args.cell_size[1] <= 0:
        parser.error("Cell size must be positive integers")

    # Validate background color
    if not all(0 <= c <= 255 for c in args.background):
        parser.error("Background color values must be between 0 and 255")

    # Validate font size
    if args.font_size <= 0:
        parser.error("Font size must be positive")

    # Validate margin
    if args.margin < 0:
        parser.error("Margin must be non-negative")

    try:
        # Handle batch processing
        if args.batch:
            processor = BatchProcessor(os.path.dirname(args.output_path))
            template = GridTemplate(
                name="batch",
                rows=args.rows or 3,
                cols=args.cols or 3,
                cell_size=tuple(args.cell_size),
                margin=args.margin,
                font_size=args.font_size,
            )

            preprocessing = None
            if args.resize:
                preprocessing = {
                    "resize": {"size": tuple(args.resize), "mode": args.resize_mode}
                }

            results = processor.process_batch(
                input_dirs=args.batch,
                template=template,
                label_columns=args.labels or [],
                csv_path=args.csv,
                export_format=args.format,
                preprocessing=preprocessing,
                use_clip=args.use_clip,
                clip_model=args.clip_model,
            )

            for result in results:
                if result.get("status") == "success":
                    print(f"✅ {result['input_dir']} -> {result['output_path']}")
                else:
                    print(
                        f"❌ {result['input_dir']}: {result.get('error', 'Unknown error')}"
                    )

            return

        # Load template if specified
        template = None
        if args.template:
            template = load_template(args.template)
        else:
            template = GridTemplate(
                name="cli",
                rows=args.rows or 3,
                cols=args.cols or 3,
                cell_size=tuple(args.cell_size),
                margin=args.margin,
                font_size=args.font_size,
            )

        # Save template if requested
        if args.save_template:
            save_template(template, args.save_template)
            print(f"Template saved to {args.save_template}")

        # Prepare preprocessing
        preprocessing = None
        if args.resize:
            preprocessing = {
                "resize": {"size": tuple(args.resize), "mode": args.resize_mode}
            }

        # Process single directory
        result = assemble_grid_enhanced(
            input_dir=args.input_dir,
            output_path=args.output_path,
            template=template,
            label_columns=args.labels or [],
            csv_path=args.csv,
            export_format=args.format,
            preprocessing=preprocessing,
            background_color=tuple(args.background),
            use_clip=args.use_clip,
            clip_model=args.clip_model,
        )

        print("✅ Grid created successfully!")
        print(f"   Images processed: {result['images_processed']}")
        print(f"   Grid dimensions: {result['grid_dimensions']}")
        print(f"   Canvas size: {result['canvas_size']}")
        print(f"   Output format: {result['export_format']}")

    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
