#!/usr/bin/env python3
"""
Quick script to create test images for demonstrating the reports module
"""

import os
import json
import shutil
from PIL import Image, ImageDraw, ImageFont
import random

def create_test_image(filename, text, width=512, height=512):
    """Create a simple test image with text"""
    # Create a new image with a random background color
    colors = [(255, 200, 200), (200, 255, 200), (200, 200, 255), (255, 255, 200), (255, 200, 255), (200, 255, 255)]
    bg_color = random.choice(colors)
    
    image = Image.new('RGB', (width, height), bg_color)
    draw = ImageDraw.Draw(image)
    
    # Try to use a default font, fallback to basic if not available
    try:
        font_size = 24
        font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", font_size)
    except:
        font = ImageFont.load_default()
    
    # Calculate text position for center alignment
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x = (width - text_width) // 2
    y = (height - text_height) // 2
    
    # Draw the text
    draw.text((x, y), text, fill=(0, 0, 0), font=font)
    
    # Add some decorative elements
    draw.rectangle([10, 10, width-10, height-10], outline=(0, 0, 0), width=3)
    
    return image

def main():
    print("🎨 Creating test images for DreamLayer Reports demo...")
    
    # Ensure served_images directory exists
    served_images_dir = "served_images"
    os.makedirs(served_images_dir, exist_ok=True)
    
    # Create test images
    test_images = [
        ("txt2img_landscape_demo.png", "Beautiful Mountain\nLandscape", 512, 512),
        ("txt2img_portrait_demo.png", "Professional\nPortrait", 512, 768),
        ("txt2img_fantasy_demo.png", "Fantasy Castle\nScene", 768, 512),
        ("img2img_enhanced_demo.png", "Enhanced Photo\nResult", 512, 512),
        ("img2img_style_demo.png", "Style Transfer\nArt", 512, 512)
    ]
    
    for filename, text, width, height in test_images:
        filepath = os.path.join(served_images_dir, filename)
        image = create_test_image(filename.replace('.png', '').replace('_', ' ').title(), text, width, height)
        image.save(filepath, 'PNG')
        print(f"✅ Created: {filename}")
    
    # Create sample gallery data
    gallery_data = {
        "txt2img": [
            {
                "id": "demo_txt2img_001",
                "filename": "txt2img_landscape_demo.png",
                "url": "http://localhost:5001/api/images/txt2img_landscape_demo.png",
                "prompt": "Epic mountain landscape at sunset, dramatic clouds, golden hour lighting, photorealistic",
                "negativePrompt": "blurry, low quality, watermark, text",
                "timestamp": "2024-08-09T18:00:00.000Z",
                "settings": {
                    "model_name": "v15PrunedEmaonly_v15PrunedEmaonly.safetensors",
                    "sampler_name": "euler",
                    "steps": 15,
                    "cfg_scale": 7.0,
                    "width": 512,
                    "height": 512,
                    "seed": 123456,
                    "batch_size": 1
                }
            },
            {
                "id": "demo_txt2img_002", 
                "filename": "txt2img_portrait_demo.png",
                "url": "http://localhost:5001/api/images/txt2img_portrait_demo.png",
                "prompt": "Professional portrait of a person, studio lighting, high quality photography",
                "negativePrompt": "cartoon, anime, low resolution, distorted",
                "timestamp": "2024-08-09T18:05:00.000Z",
                "settings": {
                    "model_name": "v15PrunedEmaonly_v15PrunedEmaonly.safetensors",
                    "sampler_name": "dpmpp_2m",
                    "steps": 20,
                    "cfg_scale": 8.0,
                    "width": 512,
                    "height": 768,
                    "seed": 789012,
                    "batch_size": 1
                }
            },
            {
                "id": "demo_txt2img_003",
                "filename": "txt2img_fantasy_demo.png", 
                "url": "http://localhost:5001/api/images/txt2img_fantasy_demo.png",
                "prompt": "Medieval fantasy castle on hilltop, magical atmosphere, epic scene",
                "negativePrompt": "modern, contemporary, realistic",
                "timestamp": "2024-08-09T18:10:00.000Z",
                "settings": {
                    "model_name": "v15PrunedEmaonly_v15PrunedEmaonly.safetensors",
                    "sampler_name": "euler",
                    "steps": 25,
                    "cfg_scale": 7.5,
                    "width": 768,
                    "height": 512,
                    "seed": 345678,
                    "batch_size": 1
                }
            }
        ],
        "img2img": [
            {
                "id": "demo_img2img_001",
                "filename": "img2img_enhanced_demo.png",
                "url": "http://localhost:5001/api/images/img2img_enhanced_demo.png", 
                "prompt": "Enhanced version with better lighting and details, photorealistic",
                "negativePrompt": "artificial, over-processed, cartoon",
                "timestamp": "2024-08-09T18:15:00.000Z",
                "settings": {
                    "model_name": "v15PrunedEmaonly_v15PrunedEmaonly.safetensors",
                    "sampler_name": "euler",
                    "steps": 20,
                    "cfg_scale": 7.5,
                    "width": 512,
                    "height": 512,
                    "seed": 456789,
                    "denoising_strength": 0.65,
                    "input_image": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
                }
            },
            {
                "id": "demo_img2img_002",
                "filename": "img2img_style_demo.png",
                "url": "http://localhost:5001/api/images/img2img_style_demo.png",
                "prompt": "Apply artistic painting style, creative interpretation",
                "negativePrompt": "photorealistic, digital, sharp edges", 
                "timestamp": "2024-08-09T18:20:00.000Z",
                "settings": {
                    "model_name": "v15PrunedEmaonly_v15PrunedEmaonly.safetensors",
                    "sampler_name": "dpmpp_2m",
                    "steps": 30,
                    "cfg_scale": 8.5,
                    "width": 512,
                    "height": 512,
                    "seed": 567890,
                    "denoising_strength": 0.75
                }
            }
        ]
    }
    
    # Save gallery data
    with open('temp_gallery_data.json', 'w', encoding='utf-8') as f:
        json.dump(gallery_data, f, indent=2, ensure_ascii=False)
    
    print("\n🎯 Test images and gallery data created successfully!")
    print(f"📁 Images saved to: {os.path.abspath(served_images_dir)}")
    print(f"📄 Gallery data saved to: temp_gallery_data.json")
    print(f"\n📊 Created {len(gallery_data['txt2img'])} txt2img and {len(gallery_data['img2img'])} img2img samples")
    
    return gallery_data

if __name__ == "__main__":
    main()
