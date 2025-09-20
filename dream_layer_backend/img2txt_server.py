from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import os
import base64
import tempfile
import requests
from io import BytesIO
from PIL import Image
from dream_layer import get_directories
from dream_layer_backend_utils import interrupt_workflow
from dream_layer_backend_utils.api_key_injector import inject_api_keys_into_workflow
from shared_utils import send_to_comfyui

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

def load_img2txt_workflow():
    """Load the Gemini multimodal workflow for img2txt analysis"""
    workflow_path = os.path.join(os.path.dirname(__file__), 'workflows', 'img2img', 'gemini_multimodal_workflow.json')
    try:
        with open(workflow_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading Gemini multimodal workflow: {e}")
        return None

def transform_to_img2txt_workflow(data):
    """Transform frontend data to ComfyUI img2txt workflow using full Gemini multimodal workflow"""
    workflow = load_img2txt_workflow()
    if not workflow:
        raise Exception("Could not load Gemini multimodal workflow")
    
    # Use the full workflow - we'll extract just the text from GeminiNode later
    workflow_copy = json.loads(json.dumps(workflow))
    
    # Process and save the input image
    if 'input_image' in data and data['input_image']:
        try:
            # Decode base64 image
            image_data = data['input_image'].split(',')[1] if ',' in data['input_image'] else data['input_image']
            image_bytes = base64.b64decode(image_data)
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png', dir=SERVED_IMAGES_DIR) as temp_file:
                temp_file.write(image_bytes)
                temp_filename = os.path.basename(temp_file.name)
            
            # Update workflow with the uploaded image
            workflow_copy['prompt']['1']['inputs']['image'] = temp_filename
            
        except Exception as e:
            print(f"Error processing input image: {e}")
            raise Exception(f"Failed to process input image: {str(e)}")
    else:
        raise Exception("No input image provided")
    
    # Update Gemini prompt if provided
    if 'prompt' in data and data['prompt']:
        custom_prompt = data['prompt']
    else:
        custom_prompt = "Analyze this image and provide a detailed description. Include: what objects/people you see, the scene setting, colors, mood, style, composition, and any notable details. Be descriptive and thorough."
    
    workflow_copy['prompt']['2']['inputs']['prompt'] = custom_prompt
    
    # Update model if provided
    if 'model' in data and data['model']:
        workflow_copy['prompt']['2']['inputs']['model'] = data['model']
    
    # Update seed if provided
    if 'seed' in data and data['seed'] is not None:
        workflow_copy['prompt']['2']['inputs']['seed'] = int(data['seed'])
    
    return workflow_copy

def call_gemini_api_directly(data):
    """Call Gemini API directly bypassing ComfyUI"""
    from dream_layer_backend_utils.api_key_injector import read_api_keys_from_env
    
    # Get API key
    api_keys = read_api_keys_from_env()
    gemini_key = api_keys.get('GEMINI_API_KEY')
    if not gemini_key:
        raise Exception("GEMINI_API_KEY not found in environment")
    
    # Convert image to base64 for Gemini
    image_b64 = data['input_image'].split(',')[1] if ',' in data['input_image'] else data['input_image']
    
    # Prepare prompt
    prompt_text = data.get('prompt', "Analyze this image and provide a detailed description. Include: what objects/people you see, the scene setting, colors, mood, style, composition, and any notable details. Be descriptive and thorough.")
    
    # Gemini API request
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
    headers = {'Content-Type': 'application/json', 'X-goog-api-key': gemini_key}
    payload = {
        "contents": [{
            "parts": [
                {"text": prompt_text},
                {"inline_data": {"mime_type": "image/png", "data": image_b64}}
            ]
        }]
    }
    
    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        result = response.json()
        return result['candidates'][0]['content']['parts'][0]['text']
    else:
        raise Exception(f"Gemini API error: {response.status_code} - {response.text}")

@app.route('/api/img2txt', methods=['POST', 'OPTIONS'])
def handle_img2txt():
    """Handle image-to-text generation requests"""
    if request.method == 'OPTIONS':
        return jsonify({"status": "ok"})
    
    try:
        data = request.json
        if data:
            print("Img2Txt Data:", json.dumps({
                **data,
                'input_image': 'BASE64_IMAGE_DATA' if 'input_image' in data else None
            }, indent=2))
            
            # Validate required fields
            if 'input_image' not in data or not data['input_image']:
                return jsonify({
                    "status": "error",
                    "message": "Missing required field: input_image"
                }), 400
            
            # Direct Gemini API call (bypass ComfyUI)
            gemini_response = call_gemini_api_directly(data)
            print(f"✅ Direct Gemini API response received: {len(gemini_response)} chars")
            
            # Format response to match expected structure
            comfy_response = {
                "status": "success",
                "text_output": gemini_response,
                "all_images": []
            }
            
            if "error" in comfy_response:
                return jsonify({
                    "status": "error",
                    "message": comfy_response["error"]
                }), 500
            
            response = jsonify({
                "status": "success",
                "message": "Image analysis completed successfully",
                "comfy_response": comfy_response,
                "generated_text": comfy_response.get("text_output", "No text output received")
            })
            
            return response
            
        else:
            return jsonify({
                "status": "error",
                "message": "No data received"
            }), 400
            
    except Exception as e:
        print(f"Error in handle_img2txt: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/img2txt/interrupt', methods=['POST'])
def handle_img2txt_interrupt():
    """Handle interruption of img2txt generation"""
    print("Interrupting img2txt generation...")
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
        print(f"Error serving image {filename}: {str(e)}")
        return jsonify({"error": str(e)}), 404

if __name__ == '__main__':
    print("Starting Img2Txt server on port 5007...")
    app.run(debug=True, host='0.0.0.0', port=5007)
