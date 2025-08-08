#!/usr/bin/env python3
"""
ComfyUI Custom Node: Labeled Grid Exporter

This custom node integrates the labeled grid exporter directly into ComfyUI workflows,
allowing users to create labeled image grids with metadata overlays directly from
the ComfyUI interface.

Usage:
1. Add this node to your ComfyUI custom_nodes directory
2. Connect image outputs to this node
3. Optionally provide metadata (seeds, prompts, etc.)
4. Get a labeled grid output

Features:
- Automatic grid layout based on number of images
- Metadata overlay (seed, sampler, steps, cfg, etc.)
- CLIP auto-labeling support
- Customizable styling and formatting
- Batch processing support
"""

import os
import json
import csv
import tempfile
from typing import Dict, List

# ComfyUI node imports
import comfy.utils

# Import our labeled grid exporter
from labeled_grid_exporter import GridTemplate, assemble_grid_enhanced


class LabeledGridExporterNode:
    """ComfyUI custom node for creating labeled image grids"""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "images": ("IMAGE",),
                "grid_rows": ("INT", {"default": 3, "min": 1, "max": 10}),
                "grid_cols": ("INT", {"default": 3, "min": 1, "max": 10}),
                "cell_width": ("INT", {"default": 512, "min": 64, "max": 2048}),
                "cell_height": ("INT", {"default": 704, "min": 64, "max": 2048}),
                "margin": ("INT", {"default": 10, "min": 0, "max": 100}),
                "font_size": ("INT", {"default": 16, "min": 8, "max": 48}),
                "background_color": ("STRING", {"default": "255,255,255"}),
                "export_format": (["png", "jpg", "jpeg"], {"default": "png"}),
                "use_clip_labeling": ("BOOLEAN", {"default": False}),
                "clip_model": ("STRING", {"default": "openai/clip-vit-base-patch32"}),
            },
            "optional": {
                "metadata": ("STRING", {"default": "", "multiline": True}),
                "label_columns": ("STRING", {"default": "seed,sampler,steps,cfg"}),
                "template_name": ("STRING", {"default": "comfyui_grid"}),
            },
        }

    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("grid_image", "grid_info")
    FUNCTION = "create_labeled_grid"
    CATEGORY = "image/postprocessing"

    def create_labeled_grid(
        self,
        images,
        grid_rows,
        grid_cols,
        cell_width,
        cell_height,
        margin,
        font_size,
        background_color,
        export_format,
        use_clip_labeling,
        clip_model,
        metadata="",
        label_columns="seed,sampler,steps,cfg",
        template_name="comfyui_grid",
    ):
        """Create a labeled grid from input images"""

        # Parse background color
        try:
            bg_color = tuple(map(int, background_color.split(",")))
        except (ValueError, AttributeError):
            bg_color = (255, 255, 255)

        # Parse label columns
        label_cols = [col.strip() for col in label_columns.split(",") if col.strip()]

        # Create temporary directory for processing
        with tempfile.TemporaryDirectory() as temp_dir:
            # Save images to temporary directory
            image_files = []
            for i, image in enumerate(images):
                # Convert tensor to PIL image
                pil_image = comfy.utils.tensor_to_pil(image)[0]

                # Save image
                filename = f"ComfyUI_{i:04d}.png"
                filepath = os.path.join(temp_dir, filename)
                pil_image.save(filepath)
                image_files.append(filename)

            # Create CSV metadata if provided
            csv_path = None
            if metadata.strip():
                csv_path = os.path.join(temp_dir, "metadata.csv")
                self._create_metadata_csv(csv_path, image_files, metadata, label_cols)

            # Create grid template
            template = GridTemplate(
                name=template_name,
                rows=grid_rows,
                cols=grid_cols,
                cell_size=(cell_width, cell_height),
                margin=margin,
                font_size=font_size,
            )

            # Create output path
            output_path = os.path.join(temp_dir, f"grid_output.{export_format}")

            # Generate labeled grid
            result = assemble_grid_enhanced(
                input_dir=temp_dir,
                output_path=output_path,
                template=template,
                label_columns=label_cols,
                csv_path=csv_path,
                export_format=export_format,
                background_color=bg_color,
                use_clip=use_clip_labeling,
                clip_model=clip_model,
            )

            # Load the output image back to tensor
            output_image = comfy.utils.load_image(output_path)

            # Create info string
            info = json.dumps(
                {
                    "status": result.get("status", "unknown"),
                    "images_processed": result.get("images_processed", 0),
                    "grid_dimensions": result.get("grid_dimensions", "unknown"),
                    "canvas_size": result.get("canvas_size", "unknown"),
                    "export_format": export_format,
                    "template": template_name,
                },
                indent=2,
            )

            return (output_image, info)

    def _create_metadata_csv(
        self,
        csv_path: str,
        image_files: List[str],
        metadata: str,
        label_columns: List[str],
    ):
        """Create CSV metadata file from provided metadata string"""
        try:
            # Parse metadata (assuming JSON format)
            metadata_dict = json.loads(metadata)

            with open(csv_path, "w", newline="", encoding="utf-8") as csvfile:
                fieldnames = ["filename"] + label_columns
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()

                for i, filename in enumerate(image_files):
                    row = {"filename": filename}

                    # Add metadata for each column
                    for col in label_columns:
                        if col in metadata_dict:
                            if isinstance(metadata_dict[col], list) and i < len(
                                metadata_dict[col]
                            ):
                                row[col] = str(metadata_dict[col][i])
                            else:
                                row[col] = str(metadata_dict[col])
                        else:
                            row[col] = f"value_{i}"  # Default value

                    writer.writerow(row)

        except json.JSONDecodeError:
            # Fallback: create simple metadata
            with open(csv_path, "w", newline="", encoding="utf-8") as csvfile:
                fieldnames = ["filename"] + label_columns
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()

                for i, filename in enumerate(image_files):
                    row = {"filename": filename}
                    for col in label_columns:
                        row[col] = f"{col}_{i}"
                    writer.writerow(row)


class BatchLabeledGridExporterNode:
    """ComfyUI custom node for batch processing multiple image sets"""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image_batches": ("IMAGE",),  # Multiple batches of images
                "batch_names": ("STRING", {"default": "batch1,batch2,batch3"}),
                "grid_rows": ("INT", {"default": 3, "min": 1, "max": 10}),
                "grid_cols": ("INT", {"default": 3, "min": 1, "max": 10}),
                "cell_width": ("INT", {"default": 512, "min": 64, "max": 2048}),
                "cell_height": ("INT", {"default": 704, "min": 64, "max": 2048}),
                "margin": ("INT", {"default": 10, "min": 0, "max": 100}),
                "font_size": ("INT", {"default": 16, "min": 8, "max": 48}),
                "export_format": (["png", "jpg", "jpeg"], {"default": "png"}),
            },
            "optional": {
                "batch_metadata": ("STRING", {"default": "", "multiline": True}),
                "label_columns": ("STRING", {"default": "seed,sampler,steps,cfg"}),
            },
        }

    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("batch_grids", "batch_info")
    FUNCTION = "create_batch_grids"
    CATEGORY = "image/postprocessing"

    def create_batch_grids(
        self,
        image_batches,
        batch_names,
        grid_rows,
        grid_cols,
        cell_width,
        cell_height,
        margin,
        font_size,
        export_format,
        batch_metadata="",
        label_columns="seed,sampler,steps,cfg",
    ):
        """Create labeled grids for multiple batches of images"""

        # Parse batch names
        batch_name_list = [
            name.strip() for name in batch_names.split(",") if name.strip()
        ]

        # Parse label columns
        label_cols = [col.strip() for col in label_columns.split(",") if col.strip()]

        # Create temporary directory for processing
        with tempfile.TemporaryDirectory() as temp_dir:
            batch_results = []

            # Process each batch
            for batch_idx, (batch_images, batch_name) in enumerate(
                zip(image_batches, batch_name_list)
            ):
                # Create batch directory
                batch_dir = os.path.join(temp_dir, batch_name)
                os.makedirs(batch_dir, exist_ok=True)

                # Save batch images
                image_files = []
                for i, image in enumerate(batch_images):
                    pil_image = comfy.utils.tensor_to_pil(image)[0]
                    filename = f"{batch_name}_{i:04d}.png"
                    filepath = os.path.join(batch_dir, filename)
                    pil_image.save(filepath)
                    image_files.append(filename)

                # Create metadata for this batch
                csv_path = None
                if batch_metadata.strip():
                    csv_path = os.path.join(batch_dir, "metadata.csv")
                    self._create_batch_metadata_csv(
                        csv_path, image_files, batch_metadata, label_cols, batch_idx
                    )

                # Create grid template
                template = GridTemplate(
                    name=f"{batch_name}_grid",
                    rows=grid_rows,
                    cols=grid_cols,
                    cell_size=(cell_width, cell_height),
                    margin=margin,
                    font_size=font_size,
                )

                # Create output path
                output_path = os.path.join(
                    temp_dir, f"{batch_name}_grid.{export_format}"
                )

                # Generate labeled grid
                result = assemble_grid_enhanced(
                    input_dir=batch_dir,
                    output_path=output_path,
                    template=template,
                    label_columns=label_cols,
                    csv_path=csv_path,
                    export_format=export_format,
                )

                batch_results.append(
                    {
                        "batch_name": batch_name,
                        "output_path": output_path,
                        "result": result,
                    }
                )

            # Combine all batch grids into a single image
            combined_image = self._combine_batch_grids(batch_results)

            # Create info string
            info = json.dumps(
                {
                    "batches_processed": len(batch_results),
                    "batch_names": batch_name_list,
                    "results": [r["result"] for r in batch_results],
                },
                indent=2,
            )

            return (combined_image, info)

    def _create_batch_metadata_csv(
        self,
        csv_path: str,
        image_files: List[str],
        batch_metadata: str,
        label_columns: List[str],
        batch_idx: int,
    ):
        """Create CSV metadata for a batch"""
        try:
            metadata_dict = json.loads(batch_metadata)

            with open(csv_path, "w", newline="", encoding="utf-8") as csvfile:
                fieldnames = ["filename"] + label_columns
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()

                for i, filename in enumerate(image_files):
                    row = {"filename": filename}

                    for col in label_columns:
                        if col in metadata_dict:
                            if isinstance(metadata_dict[col], list) and batch_idx < len(
                                metadata_dict[col]
                            ):
                                batch_data = metadata_dict[col][batch_idx]
                                if isinstance(batch_data, list) and i < len(batch_data):
                                    row[col] = str(batch_data[i])
                                else:
                                    row[col] = str(batch_data)
                            else:
                                row[col] = str(metadata_dict[col])
                        else:
                            row[col] = f"{col}_{batch_idx}_{i}"

                    writer.writerow(row)

        except json.JSONDecodeError:
            # Fallback metadata
            with open(csv_path, "w", newline="", encoding="utf-8") as csvfile:
                fieldnames = ["filename"] + label_columns
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()

                for i, filename in enumerate(image_files):
                    row = {"filename": filename}
                    for col in label_columns:
                        row[col] = f"{col}_{batch_idx}_{i}"
                    writer.writerow(row)

    def _combine_batch_grids(self, batch_results: List[Dict]) -> Dict:
        """Combine multiple batch grids into a single image"""
        # Load all batch grid images
        grid_images = []
        for result in batch_results:
            grid_image = comfy.utils.load_image(result["output_path"])
            grid_images.append(grid_image)

        # For now, return the first grid image
        # In a full implementation, you might want to combine them vertically or horizontally
        return grid_images[0] if grid_images else None


# Node class mappings for ComfyUI
NODE_CLASS_MAPPINGS = {
    "LabeledGridExporter": LabeledGridExporterNode,
    "BatchLabeledGridExporter": BatchLabeledGridExporterNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "LabeledGridExporter": "Labeled Grid Exporter",
    "BatchLabeledGridExporter": "Batch Labeled Grid Exporter",
}
