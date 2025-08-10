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
import base64
import io
import time
import platform
import subprocess
import traceback
from shared_utils import SERVED_IMAGES_DIR, serve_image, MATRIX_GRIDS_DIR
from shared_utils import upload_controlnet_image as upload_cn_image

app = Flask(__name__)
CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:*", "http://127.0.0.1:*"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

@app.route('/api/txt2img', methods=['POST', 'OPTIONS'])
def handle_txt2img():
    """Handle text-to-image generation requests"""
    if request.method == 'OPTIONS':
        return jsonify({"status": "ok"})
    
    try:
        data = request.json
        if data:
            print("Data:", json.dumps(data, indent=2))
            
            print("\nKey Parameters:")
            print("-"*20)
            print(f"Prompt: {data.get('prompt', 'Not provided')}")
            print(f"Negative Prompt: {data.get('negative_prompt', 'Not provided')}")
            print(f"Batch Size: {data.get('batch_size', 'Not provided')}")
            
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
            
            workflow = transform_to_txt2img_workflow(data)
            print("\nGenerated ComfyUI Workflow:")
            print("-"*20)
            print(json.dumps(workflow, indent=2))
            
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
        
        result = upload_cn_image(file, unit_index)
        
        if isinstance(result, tuple):
            return jsonify(result[0]), result[1]
        else:
            return jsonify(result)
            
    except Exception as e:
        print(f"❌ Error uploading ControlNet image: {str(e)}")
        traceback.print_exc()
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/save-matrix-grid', methods=['POST'])
def save_matrix_grid():
    """
    Save Matrix grid image to server storage (permanent directory)
    """
    try:
        print(f"🔄 Matrix grid save request received")
        data = request.json
        
        if not data or 'imageData' not in data:
            print("❌ No image data in request")
            return jsonify({
                "status": "error",
                "message": "No image data provided"
            }), 400
        
        image_data = data['imageData']
        if image_data.startswith('data:'):
            image_data = image_data.split(',')[1]
        
        print(f"📊 Received base64 data length: {len(image_data)}")
        
        # Decode base64 image
        image_bytes = base64.b64decode(image_data)
        print(f"📊 Decoded image bytes: {len(image_bytes)}")
        
        image = Image.open(io.BytesIO(image_bytes))
        print(f"📊 Image dimensions: {image.size}")
        
        timestamp = int(time.time() * 1000)
        matrix_id = data.get('matrixId', 'matrix')
        filename = f"{matrix_id}_{timestamp}.png"
        print(f"📁 Generated filename: {filename}")
        
        os.makedirs(MATRIX_GRIDS_DIR, exist_ok=True)
        print(f"📁 MATRIX_GRIDS_DIR: {MATRIX_GRIDS_DIR}")
        print(f"📁 Directory exists: {os.path.exists(MATRIX_GRIDS_DIR)}")
        print(f"📁 Directory is writable: {os.access(MATRIX_GRIDS_DIR, os.W_OK)}")
        
        filepath = os.path.join(MATRIX_GRIDS_DIR, filename)
        print(f"📁 Full save path: {filepath}")
        
        image.save(filepath, format='PNG')
        print(f"💾 Matrix grid saved to permanent storage")
        
        if os.path.exists(filepath):
            file_size = os.path.getsize(filepath)
            print(f"✅ Successfully saved Matrix grid to permanent storage: {filename}")
            print(f"📏 File size: {file_size} bytes")
            print(f"📁 Full path: {filepath}")
            
            dir_contents = os.listdir(MATRIX_GRIDS_DIR)
            print(f"📁 Matrix grids directory contents: {dir_contents}")
            
            return jsonify({
                "status": "success",
                "filename": filename,
                "url": f"http://localhost:5001/api/images/{filename}",
                "filesize": file_size,
                "storage": "permanent"
            })
        else:
            print(f"❌ File was not created: {filepath}")
            return jsonify({
                "status": "error",
                "message": "Failed to save Matrix grid to permanent storage"
            }), 500
            
    except Exception as e:
        print(f"❌ Error saving Matrix grid: {str(e)}")
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