from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
import csv
import time
import pynvml
from shared_utils import  send_to_comfyui
import requests
from dream_layer import get_directories
from dream_layer_backend_utils import interrupt_workflow
from dream_layer_backend_utils.fetch_advanced_models import get_controlnet_models
from PIL import Image, ImageDraw
from txt2img_workflow import transform_to_txt2img_workflow
from run_registry import create_run_config_from_generation_data
from dataclasses import asdict

app = Flask(__name__)
CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:*", "http://127.0.0.1:*"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# Get served images directory
output_dir, _ = get_directories()
SERVED_IMAGES_DIR = os.path.join(os.path.dirname(__file__), 'served_images')
os.makedirs(SERVED_IMAGES_DIR, exist_ok=True)

# Get inference CSV directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INFERENCE_TRACES_DIR = os.path.join(BASE_DIR, "inference_traces")
os.makedirs(INFERENCE_TRACES_DIR, exist_ok=True)  # create folder if it doesn't exist
TRACE_CSV = os.path.join(INFERENCE_TRACES_DIR, "inference_trace_txt2img.csv")

# Trace headers
TRACE_HEADERS = ["timestamp", "total_time_s", "images_generated", "time_per_image_s", "gpu_name", "driver_version","ckpt_name"]

# Helper Function to Check CSV File Path
def ensure_csv_exists():
    """Ensure the inference trace CSV exists with headers."""
    if not os.path.exists(TRACE_CSV):
        with open(TRACE_CSV, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(TRACE_HEADERS)

# Helper Function to Log Inference Trace
def log_inference_trace(total_time, images_generated, gpu_name, driver_version,ckpt_name):
    """Log inference details to CSV and console."""
    # Checking to see if images were generated, finding the time per image
    time_per_image = None if images_generated == 0 else total_time / images_generated
    
    # Converting to string format
    time_per_image_str = "N/A" if time_per_image is None else f"{time_per_image:.2f}"

    # Console logging 
    print(f"⏱ {total_time:.2f}s total · {time_per_image_str}s/img · {gpu_name} · Driver {driver_version}")

    # CSV logging
    ensure_csv_exists()
    with open(TRACE_CSV, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            time.time(),
            round(total_time, 4),
            images_generated,
            round(time_per_image, 4) if time_per_image is not None else "",
            gpu_name,
            driver_version,
            ckpt_name
        ])

@app.route('/api/txt2img', methods=['POST', 'OPTIONS'])
def handle_txt2img():
    """Handle text-to-image generation requests"""
    if request.method == 'OPTIONS':
        return jsonify({"status": "ok"})
    
    try:
        data = request.json
        if data:
            print("Data:", json.dumps(data, indent=2))
            
            # Print specific fields of interest
            print("\nKey Parameters:")
            print("-"*20)
            print(f"Prompt: {data.get('prompt', 'Not provided')}")
            print(f"Negative Prompt: {data.get('negative_prompt', 'Not provided')}")
            print(f"Batch Size: {data.get('batch_size', 'Not provided')}")
            
            # Check ControlNet data specifically
            controlnet_data = data.get('controlnet', {})
            print(f"\n🎮 ControlNet Data:")
            print("-"*20)
            print(f"ControlNet enabled: {controlnet_data.get('enabled', False)}")
            if controlnet_data.get('units'):
                for i, unit in enumerate(controlnet_data['units']):
                    print(f"Unit {i}:")
                    print(f"  Enabled: {unit.get('enabled', False)}")
                    print(f"  Has input_image: {unit.get('input_image') is not None}")
                    print(f"  Input image type: {type(unit.get('input_image'))}")
                    if unit.get('input_image'):
                        print(f"  Input image length: {len(unit['input_image']) if isinstance(unit['input_image'], str) else 'N/A'}")
                        print(f"  Input image preview: {unit['input_image'][:50] if isinstance(unit['input_image'], str) else 'N/A'}...")
            else:
                print("No ControlNet units found")

            # Get the absolute path to the ComfyUI root directory 
            COMFY_ROOT = os.path.dirname(os.path.abspath(__file__))
            
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
                    print(f"Failed to list checkpoints: {e}")
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

            # Transform to ComfyUI workflow
            workflow = transform_to_txt2img_workflow(data)
            #workflow = transform_to_txt2img_workflow(data, ckpt_name=ckpt_name)
            print("\nGenerated ComfyUI Workflow:")
            print("-"*20)
            print(json.dumps(workflow, indent=2))
            
            # Init NVML once at startup
            try:
                pynvml.nvmlInit()
                gpu_handle = pynvml.nvmlDeviceGetHandleByIndex(0)
                gpu_name = pynvml.nvmlDeviceGetName(gpu_handle).decode()
                driver_version = pynvml.nvmlSystemGetDriverVersion().decode()
            except Exception:
                gpu_name = "CPU"
                driver_version = "N/A"

            # Start timing 
            start = time.perf_counter()
            
            # Send to ComfyUI server
            comfy_response = send_to_comfyui(workflow)
            
            # Stop timing
            elapsed = time.perf_counter() - start

            # Determine number of images generated and time per image
            images_generated = len(comfy_response.get("all_images", []))
            time_per_image = None if images_generated == 0 else total_time / images_generated
    
            # Converting to string format
            time_per_image_str = "N/A" if time_per_image is None else f"{time_per_image:.2f}"
                    
            # Log the result
            log_inference_trace(elapsed, images_generated, gpu_name, driver_version,ckpt_name)

            # Add metrics into API response
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
            
            comfy_response["generated_images"] = comfy_response.get("all_images", [])
            # Extract generated image filenames
            generated_images = []
            if comfy_response.get("all_images"):
                for img_data in comfy_response["all_images"]:
                    if isinstance(img_data, dict) and "filename" in img_data:
                        generated_images.append(img_data["filename"])
            
            print("Start register process")
            # Register the completed run
            try:
                run_config = create_run_config_from_generation_data(
                    data, generated_images, "txt2img"
                )
                
                # Send to run registry
                registry_response = requests.post(
                    "http://localhost:5005/api/runs",
                    json=asdict(run_config),
                    timeout=5
                )
                
                if registry_response.status_code == 200:
                    print(f"✅ Run registered successfully: {run_config.run_id}")
                else:
                    print(f"⚠️ Failed to register run: {registry_response.text}")
                    
            except Exception as e:
                print(f"⚠️ Error registering run: {str(e)}")
            
            response = jsonify({
                "status": "success",
                "message": "Workflow sent to ComfyUI successfully",
                "comfy_response": comfy_response,
                "generated_images": comfy_response.get("all_images", []),
                "run_id": run_config.run_id if 'run_config' in locals() else None
            })
            
            return response
            
        else:
            return jsonify({
                "status": "error",
                "message": "No data received"
            }), 400
            
    except Exception as e:
        print(f"Error in handle_txt2img: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/txt2img/interrupt', methods=['POST'])
def handle_txt2img_interrupt():
    """Handle interruption of txt2img generation"""
    print("Interrupting txt2img generation...")
    success = interrupt_workflow()
    return jsonify({"status": "received", "interrupted": success})

@app.route('/api/images/<filename>', methods=['GET'])
def serve_image_endpoint(filename):
    """
    Serve images from multiple possible directories
    This endpoint is needed here because the frontend expects it on this port
    """
    try:
        # Use shared function
        from shared_utils import serve_image
        return serve_image(filename)
            
    except Exception as e:
        print(f"❌ Error serving image {filename}: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/controlnet/models', methods=['GET'])
def get_controlnet_models_endpoint():
    """Get available ControlNet models"""
    try:
        models = get_controlnet_models()
        return jsonify({
            "status": "success",
            "models": models
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Failed to fetch ControlNet models: {str(e)}"
        }), 500

@app.route('/api/upload-controlnet-image', methods=['POST'])
def upload_controlnet_image_endpoint():
    """
    Endpoint to upload ControlNet images directly to ComfyUI input directory
    This endpoint is needed here because the frontend expects it on this port
    """
    try:
        if 'file' not in request.files:
            return jsonify({
                "status": "error",
                "message": "No file provided"
            }), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({
                "status": "error",
                "message": "No file selected"
            }), 400
        
        unit_index = request.form.get('unit_index', '0')
        try:
            unit_index = int(unit_index)
        except ValueError:
            unit_index = 0
        
        # Use shared function
        from shared_utils import upload_controlnet_image as upload_cn_image
        result = upload_cn_image(file, unit_index)
        
        if isinstance(result, tuple):
            return jsonify(result[0]), result[1]
        else:
            return jsonify(result)
            
    except Exception as e:
        print(f"❌ Error uploading ControlNet image: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

if __name__ == "__main__":
    print("\nStarting Text2Image Handler Server...")
    print("Listening for requests at http://localhost:5001/api/txt2img")
    print("ControlNet endpoints available:")
    print("  - GET /api/controlnet/models")
    print("  - POST /api/upload-controlnet-image")
    print("  - GET /api/images/<filename>")
    app.run(host='127.0.0.1', port=5001, debug=True) 