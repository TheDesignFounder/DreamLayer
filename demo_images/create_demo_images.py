#!/usr/bin/env python3
"""
Create demo images showing before/after functionality of CLIP integration.
"""

import os
import tempfile
import csv
from PIL import Image, ImageDraw, ImageFont

def create_demo_images():
    """Create demo images for before/after comparison."""
    # Create temporary demo directory
    demo_dir = tempfile.mkdtemp(prefix="task3_demo_")
    images_dir = os.path.join(demo_dir, "images")
    os.makedirs(images_dir, exist_ok=True)
    
    # Create 4 themed demo images
    scenes = [
        {"color": (135, 206, 235), "name": "Sky", "description": "Clear blue sky with white clouds"},
        {"color": (34, 139, 34), "name": "Forest", "description": "Dense green forest landscape"},
        {"color": (255, 140, 0), "name": "Sunset", "description": "Golden sunset over mountains"},
        {"color": (147, 112, 219), "name": "Lavender", "description": "Purple lavender field in bloom"}
    ]
    
    image_files = []
    for i, scene in enumerate(scenes):
        # Create a 512x512 image
        img = Image.new('RGB', (512, 512), color=scene["color"])
        draw = ImageDraw.Draw(img)
        
        # Add some artistic elements
        # Gradient effect
        for y in range(512):
            alpha = int(255 * (1 - y / 512) * 0.3)
            overlay = Image.new('RGBA', (512, 1), (255, 255, 255, alpha))
            img.paste(overlay, (0, y), overlay)
        
        # Add decorative pattern
        for x in range(0, 512, 100):
            for y in range(0, 512, 100):
                draw.ellipse([x+20, y+20, x+80, y+80], outline=(255, 255, 255, 100), width=2)
        
        # Add scene text
        try:
            font = ImageFont.truetype("arial.ttf", 48)
        except:
            font = ImageFont.load_default()
            
        draw.text((50, 200), scene["name"], fill=(255, 255, 255), font=font)
        draw.text((50, 260), f"Demo {i+1}", fill=(255, 255, 255), font=font)
        
        filename = f"scene_{i+1:02d}.png"
        filepath = os.path.join(images_dir, filename)
        img.save(filepath)
        image_files.append({"filename": filename, "description": scene["description"]})
        print(f"Created {filename}")
    
    return demo_dir, images_dir, image_files

def create_demo_csv(demo_dir, image_files):
    """Create basic CSV metadata."""
    csv_path = os.path.join(demo_dir, "metadata.csv")
    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['filename', 'seed', 'sampler', 'steps', 'cfg']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        
        for i, img_info in enumerate(image_files):
            writer.writerow({
                'filename': img_info['filename'],
                'seed': str(42000 + i),
                'sampler': 'euler_a',
                'steps': '20',
                'cfg': '7.5'
            })
    
    print(f"Created metadata.csv")
    return csv_path

if __name__ == "__main__":
    demo_dir, images_dir, image_files = create_demo_images()
    csv_path = create_demo_csv(demo_dir, image_files)
    
    print(f"\nDemo data created in: {demo_dir}")
    print(f"Images directory: {images_dir}")
    print(f"CSV file: {csv_path}")
    print(f"Image files: {[img['filename'] for img in image_files]}")