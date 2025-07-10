from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
from dream_layer import get_directories
from dream_layer_backend_utils import interrupt_workflow
from shared_utils import  send_to_comfyui
from dream_layer_backend_utils.fetch_advanced_models import get_controlnet_models
from PIL import Image, ImageDraw
from txt2img_workflow import transform_to_txt2img_workflow

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
            
            # Transform to ComfyUI workflow

            workflow = transform_to_txt2img_workflow(data)
            print("\nGenerated ComfyUI Workflow:")
            print("-"*20)
            print(json.dumps(workflow, indent=2))
            
            # Send to ComfyUI server
            comfy_response = send_to_comfyui(workflow)
            
            if "error" in comfy_response:
                return jsonify({
                    "status": "error",
                    "message": comfy_response["error"]
                }), 500
            
            response = jsonify({
                "status": "success",
                "message": "Workflow sent to ComfyUI successfully",
                "comfy_response": comfy_response,
                "generated_images": comfy_response.get("all_images", [])
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