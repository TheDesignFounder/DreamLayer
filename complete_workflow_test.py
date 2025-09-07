#!/usr/bin/env python3
"""
Complete workflow test: Simulate frontend generating image and syncing to backend
"""

import requests
import json
from datetime import datetime, timezone

def simulate_complete_workflow():
    """Simulate the complete frontend workflow"""
    
    print("🧪 Testing Complete Image Generation → Reports Workflow")
    print("=" * 60)
    
    # Step 1: Simulate frontend creating ImageResult after generation
    print("📷 Step 1: Simulating frontend image generation result...")
    
    # This simulates what the frontend does after receiving a successful generation response
    frontend_image_result = {
        "id": f"frontend_sim_{datetime.now().timestamp()}",
        "url": "http://localhost:5001/api/images/DreamLayer_00029_.png",
        "prompt": "debug test image for reports workflow",
        "negativePrompt": "blurry, low quality",
        "timestamp": int(datetime.now().timestamp() * 1000),  # Frontend uses milliseconds
        "settings": {
            "model_name": "v15PrunedEmaonly_v15PrunedEmaonly.safetensors",
            "sampler_name": "euler",
            "steps": 10,
            "cfg_scale": 7.0,
            "width": 256,
            "height": 256,
            "seed": 987654321,
            "batch_size": 1,
            "negative_prompt": "blurry, low quality"
        }
    }
    
    print(f"✅ Created frontend image result: {frontend_image_result['id']}")
    
    # Step 2: Simulate frontend syncing gallery data to backend (auto-sync)
    print("\n🔄 Step 2: Simulating frontend auto-sync to backend...")
    
    gallery_data = {
        "txt2img": [frontend_image_result],
        "img2img": []
    }
    
    try:
        response = requests.post(
            'http://localhost:5002/api/gallery-data',
            json=gallery_data,
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Gallery sync successful: {result}")
        else:
            print(f"❌ Gallery sync failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Gallery sync error: {e}")
        return False
    
    # Step 3: Test Reports tab behavior (what happens when user clicks Reports)
    print("\n📋 Step 3: Testing Reports tab functionality...")
    
    # The Reports tab should now show 1 image and allow report generation
    try:
        response = requests.post(
            'http://localhost:5002/api/reports/generate',
            json={'filename': 'complete_workflow_test.zip'},
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Report generation successful!")
            print(f"   Total images: {result.get('total_images')}")
            print(f"   Generation types: {result.get('generation_types')}")
            print(f"   CSV valid: {result.get('csv_validation', {}).get('valid')}")
            print(f"   Paths valid: {result.get('path_validation', {}).get('valid')}")
            print(f"   Bundle size: {result.get('bundle_size_bytes')} bytes")
            
            # Step 4: Test download
            print("\n📥 Step 4: Testing report download...")
            download_response = requests.get(f"http://localhost:5002/api/reports/download/{result.get('report_filename')}")
            
            if download_response.status_code == 200:
                print(f"✅ Download successful: {len(download_response.content)} bytes")
                return True
            else:
                print(f"❌ Download failed: {download_response.status_code}")
                return False
                
        else:
            print(f"❌ Report generation failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Report generation error: {e}")
        return False

def test_backend_state():
    """Check current backend state"""
    print("\n🔍 Checking backend state...")
    
    # Check if temp_gallery_data.json exists
    try:
        with open('/Users/Ayushi/Desktop/DreamLayer/DreamLayer/dream_layer_backend/temp_gallery_data.json', 'r') as f:
            data = json.load(f)
            print(f"📁 Backend has gallery data: {len(data.get('txt2img', []))} txt2img, {len(data.get('img2img', []))} img2img")
    except FileNotFoundError:
        print("📁 No temp_gallery_data.json found")
    
    # Check served images
    import os
    served_dir = '/Users/Ayushi/Desktop/DreamLayer/DreamLayer/dream_layer_backend/served_images'
    if os.path.exists(served_dir):
        images = [f for f in os.listdir(served_dir) if f.endswith('.png')]
        print(f"🖼️ Served images directory has: {len(images)} images")
        if images:
            print(f"   Latest: {max(images)}")
    else:
        print("🖼️ No served_images directory found")

def main():
    # First check backend state
    test_backend_state()
    
    # Then run complete workflow test
    if simulate_complete_workflow():
        print("\n🎉 COMPLETE WORKFLOW TEST PASSED!")
        print("The Reports tab should now work correctly in the frontend.")
    else:
        print("\n❌ WORKFLOW TEST FAILED!")
        print("There are still issues with the integration.")

if __name__ == "__main__":
    main()
