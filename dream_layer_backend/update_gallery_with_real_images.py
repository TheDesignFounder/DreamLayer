#!/usr/bin/env python3
"""
Create gallery data from the recently generated images
"""

import json
import os
import requests
from datetime import datetime, timezone

def create_gallery_data_from_served_images():
    """Create gallery data from actual served images"""
    served_images_dir = "served_images"
    
    # Get all PNG files from served_images
    image_files = [f for f in os.listdir(served_images_dir) if f.endswith('.png')]
    image_files.sort()  # Sort by filename
    
    print(f"Found {len(image_files)} images: {image_files}")
    
    # Create realistic gallery data for these images
    gallery_data = {
        "txt2img": [],
        "img2img": []
    }
    
    # Sample prompts for the generated images
    prompts = [
        "simple red apple on table, photorealistic",
        "cute kitten playing with ball",
        "epic mountain landscape at sunset, dramatic clouds, golden hour lighting",
        "professional portrait photography, studio lighting, high quality"
    ]
    
    for i, filename in enumerate(image_files):
        prompt = prompts[i] if i < len(prompts) else f"Generated image {i+1}"
        
        # Create realistic metadata
        image_data = {
            "id": f"real_gen_{i+1:03d}",
            "filename": filename,
            "url": f"http://localhost:5001/api/images/{filename}",
            "prompt": prompt,
            "negativePrompt": "blurry, low quality, watermark, distorted",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "settings": {
                "model_name": "v15PrunedEmaonly_v15PrunedEmaonly.safetensors",
                "sampler_name": "euler",
                "steps": 15,
                "cfg_scale": 7.0,
                "width": 512,
                "height": 512 if i % 2 == 0 else 256,  # Mix of sizes
                "seed": 1000000 + i * 12345,
                "batch_size": 1
            }
        }
        
        # Alternate between txt2img and img2img for variety
        if i % 3 == 0:
            # Add img2img specific settings
            image_data["settings"]["denoising_strength"] = 0.75
            gallery_data["img2img"].append(image_data)
        else:
            gallery_data["txt2img"].append(image_data)
    
    return gallery_data

def send_gallery_data_to_backend(gallery_data):
    """Send gallery data to the backend"""
    try:
        response = requests.post(
            'http://localhost:5002/api/gallery-data',
            json=gallery_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            print("✅ Gallery data sent successfully!")
            print(f"Response: {response.json()}")
            return True
        else:
            print(f"❌ Failed to send gallery data: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error sending gallery data: {e}")
        return False

def test_report_generation():
    """Test report generation with the real gallery data"""
    try:
        response = requests.post(
            'http://localhost:5002/api/reports/generate',
            json={'filename': 'test_real_images_report.zip'},
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Report generated successfully!")
            print(f"Total images: {result.get('total_images')}")
            print(f"File size: {result.get('bundle_size_bytes')} bytes")
            print(f"CSV valid: {result.get('csv_validation', {}).get('valid')}")
            print(f"Paths valid: {result.get('path_validation', {}).get('valid')}")
            return result.get('report_filename')
        else:
            print(f"❌ Failed to generate report: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error generating report: {e}")
        return None

def main():
    print("🔄 Creating gallery data from real images...")
    
    gallery_data = create_gallery_data_from_served_images()
    
    print(f"📊 Created gallery data:")
    print(f"  - txt2img: {len(gallery_data['txt2img'])} images")
    print(f"  - img2img: {len(gallery_data['img2img'])} images")
    print(f"  - Total: {len(gallery_data['txt2img']) + len(gallery_data['img2img'])} images")
    
    print("\n🚀 Sending gallery data to backend...")
    if send_gallery_data_to_backend(gallery_data):
        print("\n📋 Testing report generation...")
        report_filename = test_report_generation()
        
        if report_filename:
            print(f"\n🎉 Success! Report created: {report_filename}")
            print("You can now test the Reports tab in the frontend!")
        else:
            print("\n❌ Report generation failed")
    else:
        print("\n❌ Failed to send gallery data")

if __name__ == "__main__":
    main()
