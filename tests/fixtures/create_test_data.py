#!/usr/bin/env python3
"""
Create test fixtures for labeled grid exporter smoke test.
"""

import csv
import os
from PIL import Image, ImageDraw, ImageFont

def create_test_images():
    """Create 4 test images with different colors and patterns."""
    colors = [
        (255, 100, 100, "Red"),    # Red
        (100, 255, 100, "Green"),  # Green  
        (100, 100, 255, "Blue"),   # Blue
        (255, 255, 100, "Yellow")  # Yellow
    ]
    
    os.makedirs("tests/fixtures/images", exist_ok=True)
    
    for i, (r, g, b, name) in enumerate(colors):
        # Create a 512x512 image
        img = Image.new('RGB', (512, 512), color=(r, g, b))
        draw = ImageDraw.Draw(img)
        
        # Add some pattern
        for x in range(0, 512, 50):
            draw.line([(x, 0), (x, 512)], fill=(255, 255, 255), width=2)
        for y in range(0, 512, 50):
            draw.line([(0, y), (512, y)], fill=(255, 255, 255), width=2)
            
        # Add text
        try:
            font = ImageFont.truetype("arial.ttf", 36)
        except:
            font = ImageFont.load_default()
            
        draw.text((50, 50), f"Test {i+1}", fill=(255, 255, 255), font=font)
        draw.text((50, 100), name, fill=(255, 255, 255), font=font)
        
        filename = f"test_image_{i+1:02d}.png"
        img.save(f"tests/fixtures/images/{filename}")
        print(f"Created {filename}")

def create_test_csv():
    """Create test CSV metadata."""
    metadata = [
        {"filename": "test_image_01.png", "seed": "12345", "sampler": "euler_a", "steps": "20", "cfg": "7.0", "preset": "Standard"},
        {"filename": "test_image_02.png", "seed": "67890", "sampler": "dpm++", "steps": "25", "cfg": "8.5", "preset": "Quality"},
        {"filename": "test_image_03.png", "seed": "11111", "sampler": "heun", "steps": "30", "cfg": "6.0", "preset": "Fast"},
        {"filename": "test_image_04.png", "seed": "22222", "sampler": "lms", "steps": "15", "cfg": "9.0", "preset": "Creative"},
    ]
    
    with open("tests/fixtures/metadata.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["filename", "seed", "sampler", "steps", "cfg", "preset"])
        writer.writeheader()
        writer.writerows(metadata)
    
    print("Created metadata.csv")

if __name__ == "__main__":
    create_test_images()
    create_test_csv()
    print("Test fixtures created successfully!")