from flask import Flask, request, jsonify
from flask_cors import CORS
import base64
import json
import logging
import os
import csv
import pynvml
import requests
from PIL import Image
import io
import time
from shared_utils import send_to_comfyui
from img2img_workflow import transform_to_img2img_workflow
from shared_utils import COMFY_API_URL
from dream_layer_backend_utils.fetch_advanced_models import get_controlnet_models
from run_registry import create_run_config_from_generation_data
from dataclasses import asdict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
# Configure CORS to allow requests from frontend
CORS(app, resources={
    r"/*": {  # Allow CORS for all routes
        "origins": ["http://localhost:8080"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})


# Get the absolute path to the ComfyUI root directory (parent of our backend directory)
COMFY_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# ComfyUI's input directory should be inside the ComfyUI directory
COMFY_UI_DIR = os.path.join(COMFY_ROOT, "ComfyUI")
COMFY_INPUT_DIR = os.path.join(COMFY_UI_DIR, "input")
COMFY_OUTPUT_DIR = os.path.join(COMFY_UI_DIR, "output")

# Create a directory to store our served images
SERVED_IMAGES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "served_images")
os.makedirs(SERVED_IMAGES_DIR, exist_ok=True)

logger.info(f"ComfyUI root directory: {COMFY_ROOT}")
logger.info(f"ComfyUI directory: {COMFY_UI_DIR}")
logger.info(f"ComfyUI input directory: {COMFY_INPUT_DIR}")
logger.info(f"ComfyUI output directory: {COMFY_OUTPUT_DIR}")

def verify_input_directory():
    """Verify that the input directory exists and is writable"""
    if not os.path.exists(COMFY_INPUT_DIR):
        raise RuntimeError(f"Input directory does not exist: {COMFY_INPUT_DIR}")
    if not os.access(COMFY_INPUT_DIR, os.W_OK):
        raise RuntimeError(f"Input directory is not writable: {COMFY_INPUT_DIR}")
    logger.info(f"Verified input directory: {COMFY_INPUT_DIR}")

# Verify input directory on startup
verify_input_directory()


# Using shared functions from shared_utils.py

@app.route('/api/img2img', methods=['POST', 'OPTIONS'])
def handle_img2img():
    if request.method == 'OPTIONS':
        # Handle preflight request
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin', 'http://localhost:8080')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        return response

    try:
        # Verify input directory before processing
        verify_input_directory()
        
        data = request.json
        logger.info("Received img2img request with data: %s", {
            **data,
            'input_image': 'BASE64_IMAGE_DATA' if 'input_image' in data else None
        })

        # Validate required fields
        required_fields = ['prompt', 'input_image', 'denoising_strength']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    'status': 'error',
                    'message': f'Missing required field: {field}'
                }), 400

        # Process the input image
        try:
            # Get the input image from the request
            input_image = data['input_image']
            
            # Check if it's a data URL
            if input_image.startswith('data:'):
                # Extract the base64 part
                if ',' in input_image:
                    input_image = input_image.split(',')[1]
                
                # Decode base64 image
                image_bytes = base64.b64decode(input_image)
                image = Image.open(io.BytesIO(image_bytes))
            else:
                # If it's not a data URL, assume it's already base64 encoded
                image_bytes = base64.b64decode(input_image)
                image = Image.open(io.BytesIO(image_bytes))
            
            # Save the image temporarily in ComfyUI's input directory
            temp_filename = f"input_{int(time.time())}.png"
            temp_filepath = os.path.join(COMFY_INPUT_DIR, temp_filename)
            
            # Convert image to RGB if it's in RGBA mode
            if image.mode == 'RGBA':
                image = image.convert('RGB')
            elif image.mode not in ['RGB', 'L']:
                image = image.convert('RGB')
            
            # Save image and verify it was saved correctly
            image.save(temp_filepath, format='PNG')
            if not os.path.exists(temp_filepath):
                raise RuntimeError(f"Failed to save image to {temp_filepath}")
            
            # Verify the saved image can be opened
            try:
                with Image.open(temp_filepath) as verify_img:
                    verify_img.verify()
                logger.info(f"Verified saved image: {temp_filepath}")
            except Exception as e:
                raise RuntimeError(f"Saved image verification failed: {str(e)}")
            
            # Update the data with just the filename for the workflow
            data['input_image'] = temp_filename
            
            # Log image details
            logger.info("Input image saved as: %s, format=%s, size=%s, mode=%s", 
                       temp_filename, image.format, image.size, image.mode)
            
            # List directory contents for debugging
            logger.info("Input directory contents:")
            for filename in os.listdir(COMFY_INPUT_DIR):
                logger.info(f"  {filename}")
            
        except Exception as e:
            logger.error("Error processing input image: %s", str(e))
            return jsonify({
                'status': 'error',
                'message': f'Invalid input image: {str(e)}'
            }), 400
        
        
        # Get checkpoint 
        ckpt_name = data.get("ckpt_name", "unknown")
        
        # List of allowed checkpoints
        CHECKPOINTS_DIR = os.path.join(COMFY_ROOT, "ComfyUI", "models", "checkpoints")

        # Inline function to list allowed checkpoints dynamically
        def get_allowed_checkpoints():
            try:
                return [
                    fname for fname in os.listdir(CHECKPOINTS_DIR)
                    if fname.endswith(('.safetensors', '.ckpt'))
                ]
            except Exception as e:
                logger.error(f"Failed to list checkpoints: {e}")
                return []
            
        ALLOWED_CKPTS = get_allowed_checkpoints()

        # Validate checkpoint 
        if not ckpt_name or ckpt_name not in ALLOWED_CKPTS:
            if ALLOWED_CKPTS:
                chosen_ckpt = ALLOWED_CKPTS[0]
                print(f"Checkpoint '{ckpt_name}' invalid or missing, falling back to '{chosen_ckpt}'")
                ckpt_name = chosen_ckpt
            else:
                 return jsonify({"error": "No checkpoints available on server"}), 500

        # Insert ckpt_name into data
        data['ckpt_name'] = ckpt_name

        # Transform data to ComfyUI workflow
        workflow = transform_to_img2img_workflow(data)
        # workflow = transform_to_img2img_workflow(data, ckpt_name=ckpt_name)

        # Log the workflow for debugging
        logger.info("Generated workflow:")
        logger.info(json.dumps(workflow, indent=2))
        
        try:
            pynvml.nvmlInit()
            gpu_handle = pynvml.nvmlDeviceGetHandleByIndex(0)
            gpu_name = pynvml.nvmlDeviceGetName(gpu_handle).decode()
            driver_version = pynvml.nvmlSystemGetDriverVersion().decode()
        except Exception:
            gpu_name = "CPU"
            driver_version = "N/A"

        # Start Time
        start_time = time.perf_counter()

        # Send to ComfyUI
        comfy_response = send_to_comfyui(workflow)

        # End Time
        elapsed = time.perf_counter() - start_time

        # Calculate images generated
        images_generated = len(comfy_response.get("all_images", []))
        time_per_image = elapsed / images_generated if images_generated > 0 else None

        # Log info to console and logger
        time_per_image_str = f"{time_per_image:.2f}s/img" if time_per_image else "N/A"
        logger.info(f"⏱ {elapsed:.2f}s total · {time_per_image_str} · GPU: {gpu_name} · Driver: {driver_version}")
        print(f"⏱ {elapsed:.2f}s total · {time_per_image_str} · GPU: {gpu_name} · Driver: {driver_version}")

        # Log info into CSV
        
        # Path for CSV log file
        BASE_DIR = os.path.dirname(os.path.abspath(__file__))
        INFERENCE_TRACES_DIR = os.path.join(BASE_DIR, "inference_traces")
        os.makedirs(INFERENCE_TRACES_DIR, exist_ok=True)  # create folder if it doesn't exist
        TRACE_CSV = os.path.join(INFERENCE_TRACES_DIR, "inference_trace_img2img.csv")

        # Ensure CSV file exists and has header
        if not os.path.exists(TRACE_CSV):
            with open(TRACE_CSV, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["timestamp", "total_time_s", "images_generated", "time_per_image_s", "gpu_name", "driver_version","ckpt_name"])

        # Append new row to CSV
        with open(TRACE_CSV, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                time.time(),
                round(elapsed, 4),
                images_generated,
                round(time_per_image, 4) if time_per_image is not None else "",
                gpu_name,
                driver_version,
                ckpt_name
            ])

        # Include information into JSON response
        comfy_response["metrics"] = {
            "elapsed_time_sec": elapsed,
            "time_per_image_sec": time_per_image,
            "gpu": gpu_name,
            "driver_version": driver_version
        }
        
        if "error" in comfy_response:
            return jsonify({
                "status": "error",
                "message": comfy_response["error"]
            }), 500
        
        # Log generated images if present
        if "generated_images" in comfy_response:
            images = comfy_response["generated_images"]
            logger.info("Generated Images Details:")
            for i, img in enumerate(images):
                logger.info(f"Image {i + 1}:")
                logger.info(f"  Filename: {img.get('filename')}")
                logger.info(f"  Type: {img.get('type')}")
                logger.info(f"  Subfolder: {img.get('subfolder', 'None')}")
                logger.info(f"  URL: {img.get('url')}")
        
        # Extract generated image filenames
        generated_images = []
        if comfy_response.get("generated_images"):
            for img_data in comfy_response["generated_images"]:
                if isinstance(img_data, dict) and "filename" in img_data:
                    generated_images.append(img_data["filename"])
        
        # Register the completed run
        try:
            run_config = create_run_config_from_generation_data(
                data, generated_images, "img2img"
            )
            
            # Send to run registry
            registry_response = requests.post(
                "http://localhost:5005/api/runs",
                json=asdict(run_config),
                timeout=5
            )
            
            if registry_response.status_code == 200:
                logger.info(f"✅ Run registered successfully: {run_config.run_id}")
            else:
                logger.warning(f"⚠️ Failed to register run: {registry_response.text}")
                
        except Exception as e:
            logger.warning(f"⚠️ Error registering run: {str(e)}")
        
        response = jsonify({
            "status": "success",
            "message": "Workflow sent to ComfyUI successfully",
            "comfy_response": comfy_response,
            "workflow": workflow,
            "run_id": run_config.run_id if 'run_config' in locals() else None
        })
        
        # Clean up the temporary image file
        try:
            os.remove(temp_filepath)
            logger.info(f"Cleaned up temporary file: {temp_filepath}")
        except Exception as e:
            logger.warning(f"Failed to remove temporary file {temp_filepath}: {str(e)}")
        
        return response

    except Exception as e:
        logger.error("Error processing request: %s", str(e))
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/img2img/interrupt', methods=['POST'])
def handle_img2img_interrupt():
    print("=== IMG2IMG INTERRUPT REQUEST ===")
    print(request.json)
    return jsonify({"status": "received"})

@app.route('/images/<filename>')
def serve_image_endpoint(filename):
    """Serve images from the served_images directory"""
    try:
        # Use shared function
        from shared_utils import serve_image
        return serve_image(filename)
    except Exception as e:
        logger.error(f"Error serving image {filename}: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5004, debug=True) 