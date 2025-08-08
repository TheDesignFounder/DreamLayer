#!/usr/bin/env python3
"""
Create a sample grid image for PR submission.

This script generates a sample grid to demonstrate the labeled grid exporter functionality.
"""

import os
import csv
import tempfile
from PIL import Image, ImageDraw, ImageFont

from dream_layer_backend_utils.labeled_grid_exporter import (
    validate_inputs, read_metadata, collect_images, assemble_grid
)

def create_sample_images():
    """Create sample images for demonstration."""
    temp_dir = tempfile.mkdtemp()
    images_dir = os.path.join(temp_dir, "sample_images")
    os.makedirs(images_dir, exist_ok=True)
    
    # Create sample images with different colors and patterns
    sample_images = [
        ("sample_001.png", (512, 512), (255, 100, 100), "Red Landscape"),  # Red
        ("sample_002.png", (512, 512), (100, 255, 100), "Green Portrait"),  # Green
        ("sample_003.png", (512, 512), (100, 100, 255), "Blue Abstract"),   # Blue
        ("sample_004.png", (512, 512), (255, 255, 100), "Yellow Still Life"), # Yellow
    ]
    
    for filename, size, color, title in sample_images:
        img = Image.new("RGB", size, color)
        draw = ImageDraw.Draw(img)
        
        # Add some artistic elements
        try:
            font = ImageFont.truetype("arial.ttf", 32)
        except:
            font = ImageFont.load_default()
        
        # Add title
        draw.text((50, 50), title, fill="white", font=font)
        
        # Add decorative elements
        for i in range(0, size[0], 80):
            for j in range(0, size[1], 80):
                if (i + j) % 160 == 0:
                    draw.ellipse([i, j, i+40, j+40], fill="white", outline="black", width=2)
        
        # Add some lines for visual interest
        for i in range(0, size[0], 100):
            draw.line([(i, 0), (i, size[1])], fill="white", width=3)
        
        img.save(os.path.join(images_dir, filename))
    
    return images_dir, temp_dir

def create_sample_csv(images_dir):
    """Create sample CSV metadata."""
    csv_path = os.path.join(images_dir, "sample_metadata.csv")
    
    sample_data = [
        {
            "filename": "sample_001.png",
            "seed": "12345",
            "sampler": "euler_a",
            "steps": "20",
            "cfg": "7.5",
            "model": "stable-diffusion-v1-5",
            "prompt": "a beautiful red landscape with mountains"
        },
        {
            "filename": "sample_002.png",
            "seed": "67890",
            "sampler": "dpm++_2m",
            "steps": "30",
            "cfg": "8.0",
            "model": "stable-diffusion-v2-1",
            "prompt": "portrait of a person in green lighting"
        },
        {
            "filename": "sample_003.png",
            "seed": "11111",
            "sampler": "ddim",
            "steps": "25",
            "cfg": "6.5",
            "model": "stable-diffusion-v1-5",
            "prompt": "abstract blue geometric patterns"
        },
        {
            "filename": "sample_004.png",
            "seed": "22222",
            "sampler": "euler",
            "steps": "15",
            "cfg": "9.0",
            "model": "stable-diffusion-v2-1",
            "prompt": "still life with yellow flowers"
        }
    ]
    
    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ["filename", "seed", "sampler", "steps", "cfg", "model", "prompt"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(sample_data)
    
    return csv_path

def main():
    """Create a sample grid for PR submission."""
    print("🎨 Creating sample grid for PR submission...")
    
    # Create sample images
    images_dir, temp_dir = create_sample_images()
    print(f"✅ Created sample images in: {images_dir}")
    
    # Create sample CSV
    csv_path = create_sample_csv(images_dir)
    print(f"✅ Created sample metadata: {csv_path}")
    
    # Create output directory
    output_dir = os.path.join(os.getcwd(), "sample_output")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "sample_grid.png")
    
    try:
        # Validate inputs
        validate_inputs(images_dir, output_path, csv_path)
        
        # Read metadata
        csv_records = read_metadata(csv_path)
        
        # Collect images
        images_info = collect_images(images_dir, csv_records)
        print(f"✅ Collected {len(images_info)} images with metadata")
        
        # Assemble grid
        assemble_grid(
            images_info=images_info,
            label_keys=["seed", "sampler", "steps", "cfg"],
            output_path=output_path,
            rows=2,
            cols=2,
            font_size=18,
            margin=15
        )
        
        print(f"✅ Sample grid created: {output_path}")
        
        # Get file info
        file_size = os.path.getsize(output_path)
        with Image.open(output_path) as img:
            print(f"📊 Grid dimensions: {img.width}×{img.height}")
            print(f"📁 File size: {file_size} bytes ({file_size/1024:.1f} KB)")
        
        print("\n🎉 Sample grid ready for PR submission!")
        print(f"📁 Location: {output_path}")
        
    except Exception as e:
        print(f"❌ Error creating sample grid: {e}")
        return 1
    finally:
        # Clean up temporary files
        import shutil
        shutil.rmtree(temp_dir)
    
    return 0

if __name__ == "__main__":
    exit(main()) 