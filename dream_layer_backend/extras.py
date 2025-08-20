import os
import sys
import json
import time
import requests
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import tempfile
import shutil
from dream_layer import get_directories

# Create Flask app
app = Flask(__name__)

# Configure CORS to allow requests from frontend
CORS(app, resources={
    r"/*": {  # Allow CORS for all routes including /images
        "origins": ["http://localhost:8080", "http://127.0.0.1:8080"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})

# ComfyUI API URL
COMFY_API_URL = "http://127.0.0.1:8188"

# Get the absolute path to the ComfyUI root directory (parent of our backend directory)
COMFY_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ComfyUI's input directory should be inside the ComfyUI directory
COMFY_UI_DIR = os.path.join(COMFY_ROOT, "ComfyUI")
COMFY_INPUT_DIR = os.path.join(COMFY_UI_DIR, "input")

# Create a directory to store our served images
SERVED_IMAGES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "served_images")
os.makedirs(SERVED_IMAGES_DIR, exist_ok=True)

# Server URL for image serving
SERVER_URL = "http://localhost:5003"

def verify_input_directory():
    """Verify that the input directory exists and is writable"""
    if not os.path.exists(COMFY_INPUT_DIR):
        raise RuntimeError(f"Input directory does not exist: {COMFY_INPUT_DIR}")
    if not os.access(COMFY_INPUT_DIR, os.W_OK):
        raise RuntimeError(f"Input directory is not writable: {COMFY_INPUT_DIR}")
    print(f"Verified input directory: {COMFY_INPUT_DIR}")

# Verify input directory on startup
verify_input_directory()

def wait_for_upscaled_image(image_file, params: dict) -> dict:
    """
    Handle the entire upscaling process from workflow construction to waiting for result.
    
    Args:
        image_file: The uploaded image file
        params (dict): Dictionary containing upscaling parameters
        
    Returns:
        dict: The final upscaled image data
    """
    input_path = None
    try:
        # Get output directory using the shared function
        output_dir, _ = get_directories()
        print(f"\nUsing output directory: {output_dir}")
        
        # Generate a unique filename for the input image
        timestamp = int(time.time())
        input_filename = f"upscale_input_{timestamp}{os.path.splitext(image_file.filename)[1]}"
        input_path = os.path.join(COMFY_INPUT_DIR, input_filename)
        
        print(f"\nSaving image to: {input_path}")
        print(f"Input directory exists: {os.path.exists(COMFY_INPUT_DIR)}")
        print(f"Input directory is writable: {os.access(COMFY_INPUT_DIR, os.W_OK)}")
        
        # Save the uploaded image to ComfyUI's input directory
        image_file.save(input_path)
        
        # Verify the file was saved
        print(f"File exists after save: {os.path.exists(input_path)}")
        print(f"File size: {os.path.getsize(input_path) if os.path.exists(input_path) else 'N/A'}")
        
        # Construct the workflow
        workflow = construct_upscale_workflow(input_path, params)
        
        # Send the workflow to ComfyUI
        response = requests.post(
            f"{COMFY_API_URL}/prompt",
            json={"prompt": workflow}
        )
        response.raise_for_status()
        prompt_data = response.json()
        
        # Get the prompt ID
        prompt_id = prompt_data.get('prompt_id')
        if not prompt_id:
            raise Exception("No prompt ID received from ComfyUI")
        
        # Wait for the result
        max_attempts = 60  # 60 seconds timeout
        attempt = 0
        while attempt < max_attempts:
            # Check history for the result
            history_response = requests.get(f"{COMFY_API_URL}/history/{prompt_id}")
            history_response.raise_for_status()
            history_data = history_response.json()
            
            if prompt_id in history_data:
                # Get the output image path from the history
                output_data = history_data[prompt_id]
                print("\nComfyUI History Data:")
                print(json.dumps(output_data, indent=2))
                
                if 'outputs' in output_data:
                    # Find the SaveImage node output
                    for node_id, node_output in output_data['outputs'].items():
                        if 'images' in node_output:
                            image_data = node_output['images'][0]
                            image_path = image_data['filename']
                            print(f"\nFound image in history:")
                            print(f"Image path from history: {image_path}")
                            
                            # Construct absolute path to the output image
                            absolute_image_path = os.path.join(output_dir, image_path)
                            print(f"Absolute image path: {absolute_image_path}")
                            print(f"Output image exists: {os.path.exists(absolute_image_path)}")
                            
                            # Copy the output image to served_images directory
                            output_filename = f"upscaled_{timestamp}.png"
                            output_path = os.path.join(SERVED_IMAGES_DIR, output_filename)
                            print(f"Copying to: {output_path}")
                            print(f"Served images dir exists: {os.path.exists(SERVED_IMAGES_DIR)}")
                            print(f"Served images dir is writable: {os.access(SERVED_IMAGES_DIR, os.W_OK)}")
                            
                            shutil.copy2(absolute_image_path, output_path)
                            print(f"Copy complete. Output exists: {os.path.exists(output_path)}")
                            
                            # Clean up the temporary input image
                            if input_path and os.path.exists(input_path):
                                try:
                                    os.remove(input_path)
                                    print(f"Cleaned up temporary input image: {input_path}")
                                except Exception as e:
                                    print(f"Warning: Failed to clean up temporary input image: {e}")
                            
                            return {
                                "status": "success",
                                "data": {
                                    "output_image": f"{SERVER_URL}/images/{output_filename}",
                                    "processing_time": output_data.get('execution_time', 0),
                                    "original_size": {
                                        "width": image_data.get('width', 0),
                                        "height": image_data.get('height', 0)
                                    },
                                    "new_size": {
                                        "width": image_data.get('width', 0),
                                        "height": image_data.get('height', 0)
                                    }
                                }
                            }
            
            # Wait before next attempt
            time.sleep(1)
            attempt += 1
        
        raise Exception("Timeout waiting for upscaling result")
            
    except Exception as e:
        print(f"Error in upscaling process: {str(e)}")
        # Clean up the temporary input image in case of error
        if input_path and os.path.exists(input_path):
            try:
                os.remove(input_path)
                print(f"Cleaned up temporary input image after error: {input_path}")
            except Exception as cleanup_error:
                print(f"Warning: Failed to clean up temporary input image after error: {cleanup_error}")
        raise

def map_model_name(frontend_model_id: str) -> str:
    """
    Map frontend model IDs to ComfyUI model names.
    
    Args:
        frontend_model_id (str): The model ID from the frontend
        
    Returns:
        str: The corresponding ComfyUI model name
    """
    model_mapping = {
        "r-esrgan-4x-plus": "RealESRGAN_x4plus.pth",
        "esrgan-4x": "ESRGAN_x4.pth",
        "swinir-4x": "swinir_4x.pth",
        # Add more mappings as needed
    }
    return model_mapping.get(frontend_model_id, frontend_model_id)

def construct_upscale_workflow(image_path: str, params: dict) -> dict:
    """
    Construct a ComfyUI workflow for image upscaling.
    
    Args:
        image_path (str): Path to the input image
        params (dict): Dictionary containing upscaling parameters:
            - upscaler_model: Primary upscaler model name
            - output_format: Output image format (PNG/JPG)
    
    Returns:
        dict: ComfyUI workflow JSON
    """
    # Create a unique filename prefix
    filename_prefix = f"upscaled_{int(time.time())}"
    
    # Map the frontend model ID to ComfyUI model name
    comfy_model_name = map_model_name(params["upscaler_model"])
    
    # Construct the workflow
    workflow = {
        "3": {  # Load Image
            "class_type": "LoadImage",
            "inputs": {
                "image": image_path
            }
        },
        "resize": {  # Resize Image
            "class_type": "ImageScale",
            "inputs": {
                "image": ["3", 0],
                "width": 512,
                "height": 512,
                "upscale": "disabled",
                "crop": "center",
                "upscale_method": "lanczos"
            }
        },
        "4": {  # Upscaler Model Loader
            "class_type": "UpscaleModelLoader",
            "inputs": {
                "model_name": comfy_model_name
            }
        },
        "5": {  # Image Upscale
            "class_type": "ImageUpscaleWithModel",
            "inputs": {
                "upscale_model": ["4", 0],
                "image": ["resize", 0]
            }
        },
        "6": {  # Save Image
            "class_type": "SaveImage",
            "inputs": {
                "images": ["5", 0],
                "filename_prefix": filename_prefix
            }
        }
    }
    
    # Print the workflow
    print("\nConstructed Workflow:")
    print(json.dumps(workflow, indent=2))
    
    return workflow

@app.route('/api/extras/upscale', methods=['POST'])
def upscale_image():
    """Handle image upscaling request"""
    try:
        # Get the uploaded image
        if 'image' not in request.files:
            return jsonify({
                "status": "error",
                "message": "No image file provided"
            }), 400

        image_file = request.files['image']
        
        # Get and parse the parameters
        params_str = request.form.get('params')
        if not params_str:
            return jsonify({
                "status": "error",
                "message": "No parameters provided"
            }), 400

        try:
            params = json.loads(params_str)
        except json.JSONDecodeError:
            return jsonify({
                "status": "error",
                "message": "Invalid parameters format"
            }), 400

        # Print the request data
        print("\nReceived Request Data:")
        print(json.dumps({
            'image': image_file.filename,
            'params': params
        }, indent=2))

        # Process the image using wait_for_upscaled_image
        result = wait_for_upscaled_image(image_file, params)
        
        return jsonify(result)

    except Exception as e:
        print(f"Error processing request: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

# This endpoint is now handled by dream_layer.py

def start_extras_server():
    """Start the Extras API server"""
    print("\nStarting Extras API server on http://localhost:5003")
    app.run(host='0.0.0.0', port=5003, debug=True, use_reloader=True)

if __name__ == "__main__":
    print("Starting Extras server...")
    start_extras_server() 