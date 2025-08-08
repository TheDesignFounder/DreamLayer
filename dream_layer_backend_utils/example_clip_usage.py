#!/usr/bin/env python3
"""
Example usage of the enhanced grid exporter with CLIP auto-labeling
"""

import os
import sys
from labeled_grid_exporter import assemble_grid_enhanced, GridTemplate


def example_basic_clip_usage():
    """Basic example of using CLIP auto-labeling"""

    # Example input directory (replace with your actual directory)
    input_dir = "path/to/your/images"
    output_path = "output_grid_with_clip_labels.png"

    # Create a grid template
    template = GridTemplate(
        name="example", rows=3, cols=3, cell_size=(256, 256), margin=10, font_size=14
    )

    # Generate grid with CLIP auto-labeling
    result = assemble_grid_enhanced(
        input_dir=input_dir,
        output_path=output_path,
        template=template,
        use_clip=True,  # Enable CLIP auto-labeling
        clip_model="openai/clip-vit-base-patch32",
    )

    print("Grid created successfully!")
    print(f"Images processed: {result['images_processed']}")
    print(f"Grid dimensions: {result['grid_dimensions']}")


def example_clip_vs_csv():
    """Example showing CLIP vs CSV labeling"""

    input_dir = "path/to/your/images"

    # Option 1: Use CLIP auto-labeling (when no CSV is available)
    result_clip = assemble_grid_enhanced(
        input_dir=input_dir,
        output_path="grid_clip_labels.png",
        template=GridTemplate("clip", 2, 3, (300, 300)),
        use_clip=True,  # CLIP will generate labels automatically
    )

    # Option 2: Use CSV labels (when you have metadata)
    result_csv = assemble_grid_enhanced(
        input_dir=input_dir,
        output_path="grid_csv_labels.png",
        template=GridTemplate("csv", 2, 3, (300, 300)),
        csv_path="metadata.csv",
        label_columns=["prompt", "model", "seed"],  # CSV columns to use as labels
    )

    print("CLIP labeling result:", result_clip)
    print("CSV labeling result:", result_csv)


def example_different_clip_models():
    """Example using different CLIP models"""

    input_dir = "path/to/your/images"

    # Different CLIP models you can try
    clip_models = [
        "openai/clip-vit-base-patch32",  # Fast, good quality
        "openai/clip-vit-base-patch16",  # Faster, slightly lower quality
        "openai/clip-vit-large-patch14",  # Slower, higher quality
        "openai/clip-vit-large-patch14-336",  # High quality, larger images
    ]

    for i, model_name in enumerate(clip_models):
        output_path = f"grid_clip_{i}.png"

        result = assemble_grid_enhanced(
            input_dir=input_dir,
            output_path=output_path,
            template=GridTemplate("model_test", 2, 2, (256, 256)),
            use_clip=True,
            clip_model=model_name,
        )

        print(f"Model {model_name}: {result}")


if __name__ == "__main__":
    print("Enhanced Grid Exporter with CLIP Auto-labeling Examples")
    print("=" * 60)

    # Check if input directory exists
    if len(sys.argv) > 1:
        input_dir = sys.argv[1]
        if os.path.exists(input_dir):
            print(f"Using input directory: {input_dir}")
            # You can modify the examples to use this input_dir
        else:
            print(f"Input directory not found: {input_dir}")
            print("Please provide a valid directory path as argument")
    else:
        print("Usage: python example_clip_usage.py <input_directory>")
        print("Replace the input_dir paths in the examples with your actual directory")

    print("\nExamples available:")
    print("1. example_basic_clip_usage() - Basic CLIP auto-labeling")
    print("2. example_clip_vs_csv() - Compare CLIP vs CSV labeling")
    print("3. example_different_clip_models() - Test different CLIP models")
