#!/usr/bin/env python3
"""
Test script for mask upload functionality
This script tests the img2img server with mask upload to verify the implementation works.
"""

import requests
import json
import os
from PIL import Image
import io
import base64


def create_test_mask():
    """Create a simple test mask image"""
    # Create a 512x512 black image with a white circle in the center
    mask = Image.new('L', (512, 512), 0)  # Black background

    # Create a white circle in the center (this will be the area to inpaint)
    from PIL import ImageDraw
    draw = ImageDraw.Draw(mask)
    draw.ellipse([156, 156, 356, 356], fill=255)  # White circle

    return mask


def create_test_image():
    """Create a simple test image"""
    # Create a 512x512 image with a solid color
    image = Image.new('RGB', (512, 512), (100, 150, 200))  # Blue-gray color

    # Add some text or pattern
    from PIL import ImageDraw, ImageFont
    draw = ImageDraw.Draw(image)
    try:
        # Try to use a default font
        font = ImageFont.load_default()
    except:
        # Fallback to basic text
        font = None

    draw.text((50, 50), "Test Image", fill=(255, 255, 255), font=font)

    return image


def test_mask_upload():
    """Test the mask upload functionality"""
    print("🧪 Testing Mask Upload Functionality")
    print("=" * 50)

    # Create test files
    print("📝 Creating test files...")
    test_image = create_test_image()
    test_mask = create_test_mask()

    # Save test files temporarily
    image_path = "test_image.png"
    mask_path = "test_mask.png"
    test_image.save(image_path)
    test_mask.save(mask_path)

    try:
        # Prepare the multipart form data
        print("📤 Preparing request data...")

        # Test parameters
        params = {
            "prompt": "A beautiful landscape with mountains",
            "negative_prompt": "blurry, low quality",
            "denoising_strength": 0.75,
            "steps": 20,
            "cfg_scale": 7.0,
            "sampler_name": "euler",
            "scheduler": "normal",
            "width": 512,
            "height": 512,
            "batch_size": 1,
            "seed": 42
        }

        # Create multipart form data
        files = {
            'image': ('test_image.png', open(image_path, 'rb'), 'image/png'),
            'mask': ('test_mask.png', open(mask_path, 'rb'), 'image/png')
        }

        data = {
            'params': json.dumps(params)
        }

        print("🚀 Sending request to img2img server...")
        print(f"   URL: http://localhost:5004/api/img2img")
        print(f"   Image: {image_path}")
        print(f"   Mask: {mask_path}")
        print(f"   Params: {json.dumps(params, indent=2)}")

        # Send request
        response = requests.post(
            'http://localhost:5004/api/img2img',
            files=files,
            data=data,
            timeout=60  # 60 second timeout for image generation
        )

        print(f"\n📥 Response Status: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print("✅ Request successful!")
            print(f"   Status: {result.get('status')}")
            print(f"   Message: {result.get('message')}")

            if 'comfy_response' in result and 'generated_images' in result['comfy_response']:
                images = result['comfy_response']['generated_images']
                print(f"   Generated {len(images)} image(s)")
                for i, img in enumerate(images):
                    print(f"   Image {i+1}: {img.get('url', 'No URL')}")
            else:
                print("   ⚠️  No generated images in response")
                print(f"   Full response: {json.dumps(result, indent=2)}")
        else:
            print("❌ Request failed!")
            print(f"   Error: {response.text}")

    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Could not connect to img2img server")
        print("   Make sure the server is running on port 5004")
        print("   Run: python dream_layer_backend/img2img_server.py")
    except requests.exceptions.Timeout:
        print("❌ Timeout Error: Request took too long")
        print("   This might be normal for the first image generation")
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")

    finally:
        # Clean up test files
        print("\n🧹 Cleaning up test files...")
        if os.path.exists(image_path):
            os.remove(image_path)
        if os.path.exists(mask_path):
            os.remove(mask_path)
        print("✅ Cleanup complete")


if __name__ == "__main__":
    test_mask_upload()
