#!/usr/bin/env python3
"""
Demo script showing how to use the Runway Text-to-Image node

This script demonstrates the complete API flow as documented at:
https://docs.dev.runwayml.com/api/#tag/Start-generating/paths/~1v1~1text_to_image/post

Requirements:
- Set RUNWAY_API_KEY=sk-... in your .env file
- Run: python demo_runway_api.py
"""

import os
from dotenv import load_dotenv
from dream_layer_backend.comfy_nodes.api_nodes.runway_text2img import RunwayText2ImgNode

def main():
    # Load environment variables
    load_dotenv()
    
    # Check API key
    if not os.getenv("RUNWAY_API_KEY"):
        print("❌ RUNWAY_API_KEY not found in environment")
        print("Please add RUNWAY_API_KEY=sk-... to your .env file")
        return
    
    print("🚀 Runway Gen-4 Text-to-Image Demo")
    print("=" * 50)
    
    # Create node instance
    node = RunwayText2ImgNode()
    
    # Show supported aspect ratios
    print(f"📐 Supported aspect ratios:")
    for ratio in node.ASPECT_RATIOS:
        print(f"   - {ratio}")
    print()
    
    # Test prompts to try
    test_prompts = [
        {
            "promptText": "A futuristic cityscape at dusk, cinematic lighting, cyberpunk style",
            "ratio": "1920:1080",
            "seed": 12345
        },
        {
            "promptText": "A serene mountain lake reflection, photorealistic, golden hour",
            "ratio": "1024:1024",
            "seed": -1  # Random seed
        }
    ]
    
    for i, params in enumerate(test_prompts, 1):
        print(f"🎨 Test {i}: Generating image...")
        print(f"   Prompt: {params['promptText'][:50]}...")
        print(f"   Ratio: {params['ratio']}")
        print(f"   Seed: {params['seed'] if params['seed'] != -1 else 'Random'}")
        
        try:
            # Generate image using official API
            result = node.generate_image(**params)
            
            # Verify result
            if result and len(result) > 0:
                tensor = result[0]
                print(f"   ✅ Success! Generated {tensor.shape} tensor")
                print(f"   📊 Shape: [batch={tensor.shape[0]}, height={tensor.shape[1]}, width={tensor.shape[2]}, channels={tensor.shape[3]}]")
            else:
                print(f"   ❌ No result returned")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        print()
    
    print("📚 API Documentation:")
    print("   https://docs.dev.runwayml.com/guides/using-the-api/")
    print()
    
    print("🔧 To integrate with ComfyUI:")
    print("   1. The node appears as 'Runway Text to Image' in category 'api node/image/runway'")
    print("   2. Connect text input to promptText")
    print("   3. Set desired aspect ratio")
    print("   4. Connect output to SaveImage or other image processing nodes")
    print()

if __name__ == "__main__":
    main()