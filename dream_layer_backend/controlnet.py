import os
import base64
import traceback
import time
from PIL import Image, ImageDraw

def save_controlnet_image(image_data, unit_index):
    """
    Save uploaded ControlNet image to ComfyUI input directory.
    
    Args:
        image_data: Base64 encoded image data or file data
        unit_index: Index of the ControlNet unit
    
    Returns:
        str: Filename of the saved image
    """
    try:
        print(f"🖼️ Saving ControlNet image for unit {unit_index}")
        print(f"📊 Image data type: {type(image_data)}")
        if isinstance(image_data, str):
            print(f"📏 Image data length: {len(image_data)}")
            print(f"🔍 Image data starts with: {image_data[:50]}...")
        
        # Get ComfyUI input directory - use absolute path
        input_dir = os.path.join("DreamLayer", "ComfyUI", "input")
        print(f"📁 Target directory: {input_dir}")
        
        # Create input directory if it doesn't exist
        os.makedirs(input_dir, exist_ok=True)
        print(f"✅ Directory exists: {os.path.exists(input_dir)}")
        
        # Create a unique filename based on timestamp and unit index
        timestamp = int(time.time() * 1000)
        filename = f"controlnet_unit_{unit_index}_{timestamp}.png"
        filepath = os.path.join(input_dir, filename)
        print(f"📄 Target filepath: {filepath}")
        
        # Handle base64 encoded image data
        if isinstance(image_data, str) and image_data.startswith('data:image'):
            print("🔄 Processing base64 image data")
            # Extract base64 data
            try:
                header, encoded = image_data.split(",", 1)
                print(f"📋 Image header: {header}")
                image_bytes = base64.b64decode(encoded)
                print(f"💾 Decoded image size: {len(image_bytes)} bytes")
                
                # Write the image file
                with open(filepath, 'wb') as f:
                    f.write(image_bytes)
                
                # Verify the file was created
                if os.path.exists(filepath):
                    file_size = os.path.getsize(filepath)
                    print(f"✅ Successfully saved ControlNet image: {filename}")
                    print(f"📁 Full path: {filepath}")
                    print(f"📏 File size: {file_size} bytes")
                    return filename
                else:
                    print(f"❌ File was not created: {filepath}")
                    return None
                
            except Exception as decode_error:
                print(f"❌ Error decoding base64 image: {decode_error}")
                traceback.print_exc()
                return None
        else:
            print(f"❌ Unsupported image data format for unit {unit_index}")
            print(f"🔍 Expected: base64 string starting with 'data:image'")
            print(f"🔍 Got: {type(image_data)}")
            if isinstance(image_data, str):
                print(f"🔍 String starts with: {image_data[:100]}...")
            return None
        
    except Exception as e:
        print(f"❌ Error saving ControlNet image: {str(e)}")
        traceback.print_exc()
        return None

def create_test_controlnet_image():
    """
    Create a simple test image for ControlNet if no image is uploaded.
    This creates a basic 512x512 white image with a simple pattern.
    """
    try:
        # Get ComfyUI input directory - use absolute path
        input_dir = os.path.join("DreamLayer", "ComfyUI", "input")
        print(f"📁 Creating test image in: {input_dir}")
        
        # Create input directory if it doesn't exist
        os.makedirs(input_dir, exist_ok=True)
        
        # Create a simple test image
        img = Image.new('RGB', (512, 512), color='white')
        draw = ImageDraw.Draw(img)
        
        # Draw a simple pattern (a circle in the center)
        draw.ellipse([156, 156, 356, 356], outline='black', width=3)
        
        # Save the test image
        test_image_path = os.path.join(input_dir, 'controlnet_input.png')
        img.save(test_image_path)
        
        print(f"✅ Created test ControlNet image: {test_image_path}")
        print(f"📏 File size: {os.path.getsize(test_image_path)} bytes")
        return True
        
    except Exception as e:
        print(f"❌ Error creating test ControlNet image: {str(e)}")
        traceback.print_exc()
        return False