import os
import sys
import threading
import time
import platform
from typing import Optional, Tuple
from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import json
import subprocess
from dream_layer_backend_utils.random_prompt_generator import fetch_positive_prompt, fetch_negative_prompt
from dream_layer_backend_utils.fetch_advanced_models import get_lora_models, get_settings, is_valid_directory, get_upscaler_models, get_controlnet_models
# Add ComfyUI directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
comfyui_dir = os.path.join(parent_dir, "ComfyUI")

# Mapping of API keys to available models
API_KEY_TO_MODELS = {
    "BFL_API_KEY": [
        {"id": "flux-pro", "name": "FLUX Pro", "filename": "flux-pro"},
        {"id": "flux-dev", "name": "FLUX Dev", "filename": "flux-dev"},
        # Add other FLUX variants as needed
    ],
    "OPENAI_API_KEY": [
        {"id": "dall-e-3", "name": "DALL-E 3", "filename": "dall-e-3"},
        {"id": "dall-e-2", "name": "DALL-E 2", "filename": "dall-e-2"},
    ],
    "IDEOGRAM_API_KEY": [
        {"id": "ideogram-v3", "name": "Ideogram V3", "filename": "ideogram-v3"},
    ]
}

def get_directories() -> Tuple[str, Optional[str]]:
    """Get the absolute paths to the output and models directories from settings"""
    settings = get_settings()
    
    # Handle output directory
    output_dir = settings.get('outputDirectory')
    
    # Validate output directory
    if not is_valid_directory(output_dir):
        print("\nWarning: Invalid output directory (starts with '/path')")
        output_dir = os.path.join(parent_dir, 'Dream_Layer_Resources', 'output')
        print(f"Using default output directory: {output_dir}")
    
    # If output directory is not an absolute path, make it relative to parent_dir
    if output_dir and not os.path.isabs(output_dir):
        output_dir = os.path.join(parent_dir, output_dir)
    
    # If no output directory specified, use default
    if not output_dir:
        output_dir = os.path.join(parent_dir, 'Dream_Layer_Resources', 'output')
    
    # Ensure output directory is absolute and exists
    output_dir = os.path.abspath(output_dir)
    os.makedirs(output_dir, exist_ok=True)
    print(f"\nUsing output directory: {output_dir}")

    # Handle models directory
    models_dir = settings.get('modelsDirectory')
    
    # Validate models directory
    if not is_valid_directory(models_dir):
        print("\nWarning: Invalid models directory (starts with '/path')")
        models_dir = None
    elif models_dir:
        models_dir = os.path.abspath(models_dir)
        print(f"Using models directory: {models_dir}")
    
    return output_dir, models_dir

# Set directories before importing ComfyUI
output_dir, models_dir = get_directories()
sys.argv.extend(['--output-directory', output_dir])
if models_dir:
    sys.argv.extend(['--base-directory', models_dir])

# Check for environment variable to force ComfyUI CPU mode
if os.environ.get('DREAMLAYER_COMFYUI_CPU_MODE', 'false').lower() == 'true':
    print("Forcing ComfyUI to run in CPU mode as requested.")
    sys.argv.append('--cpu')

# Allow WebSocket connections from frontend
cors_origin = os.environ.get('COMFYUI_CORS_ORIGIN', 'http://localhost:8080')
sys.argv.extend(['--enable-cors-header', cors_origin])

# Only add ComfyUI to path if it exists and we need to start the server
def import_comfyui_main():
    """Import ComfyUI main module only when needed"""
    if comfyui_dir not in sys.path:
        sys.path.append(comfyui_dir)
    
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location("comfyui_main", os.path.join(comfyui_dir, "main.py"))
        if spec is None or spec.loader is None:
            print("Error: Could not create module spec for ComfyUI main.py")
            return None
        comfyui_main = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(comfyui_main)
        return comfyui_main.start_comfyui
    except ImportError as e:
        print(f"Error importing ComfyUI: {e}")
        print(f"Current Python path: {sys.path}")
        return None

# Create Flask app
app = Flask(__name__)

# Configure CORS to allow requests from frontend
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:8080"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"],
        "expose_headers": ["Content-Type"],
        "supports_credentials": True
    }
})

COMFY_API_URL = "http://127.0.0.1:8188"

def get_available_models():
    """
    Fetch available checkpoint models from ComfyUI and append closed-source models
    """
    from shared_utils import get_model_display_name
    formatted_models = []
    
    # Get ComfyUI models
    try:
        response = requests.get(f"{COMFY_API_URL}/models/checkpoints")
        if response.status_code == 200:
            models = response.json()
            # Convert filenames to more user-friendly names (using display name mapping when available)
            for filename in models:
                name = get_model_display_name(filename)
                formatted_models.append({
                    "id": filename,
                    "name": name,
                    "filename": filename
                })
        else:
            print(f"Error fetching ComfyUI models: {response.status_code}")
    except Exception as e:
        print(f"Error fetching ComfyUI models: {str(e)}")
    
    # Get closed-source models based on available API keys
    try:
        from dream_layer_backend_utils import read_api_keys_from_env
        api_keys = read_api_keys_from_env()
        
        # Append models for each available API key
        for api_key_name, api_key_value in api_keys.items():
            if api_key_name in API_KEY_TO_MODELS:
                formatted_models.extend(API_KEY_TO_MODELS[api_key_name])
                print(f"Added {len(API_KEY_TO_MODELS[api_key_name])} models for {api_key_name}")
                
    except Exception as e:
        print(f"Error fetching closed-source models: {str(e)}")
    
    return formatted_models

@app.route('/api/models', methods=['GET'])
def handle_get_models():
    """
    Endpoint to get available checkpoint models
    """
    try:
        models = get_available_models()
        return jsonify({
            "status": "success",
            "models": models
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

def save_settings(settings):
    """Save path settings to a file"""
    try:
        settings_file = os.path.join(os.path.dirname(__file__), 'settings.json')
        with open(settings_file, 'w') as f:
            json.dump(settings, f, indent=2)
        print("Settings saved successfully")
        return True
    except Exception as e:
        print(f"Error saving settings: {e}")
        return False

@app.route('/api/settings/paths', methods=['POST'])
def handle_path_settings():
    """Endpoint to handle path configuration settings"""
    try:
        settings = request.json
        if settings is None:
            return jsonify({
                "status": "error",
                "message": "No JSON data received"
            }), 400
            
        print("\n=== Received Path Configuration Settings ===")
        print("Output Directory:", settings.get('outputDirectory'))
        print("Models Directory:", settings.get('modelsDirectory'))
        print("ControlNet Models Path:", settings.get('controlNetModelsPath'))
        print("Upscaler Models Path:", settings.get('upscalerModelsPath'))
        print("VAE Models Path:", settings.get('vaeModelsPath'))
        print("LoRA/Embeddings Path:", settings.get('loraEmbeddingsPath'))
        print("Filename Format:", settings.get('filenameFormat'))
        print("Save Metadata:", settings.get('saveMetadata'))
        print("==========================================\n")

        if save_settings(settings):
            # Execute the restart script
            script_path = os.path.join(os.path.dirname(__file__), 'restart_server.sh')
            subprocess.Popen([script_path])
            return jsonify({
                "status": "success",
                "message": "Settings saved. Server restart initiated."
            })
        else:
            raise Exception("Failed to save settings")

    except Exception as e:
        print(f"Error handling path settings: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

def start_comfy_server():
    """Start the ComfyUI server"""
    try:
        # Import ComfyUI main module
        start_comfyui = import_comfyui_main()
        if start_comfyui is None:
            print("Error: Could not import ComfyUI start_comfyui function")
            return False
        
        # Change to ComfyUI directory
        os.chdir(comfyui_dir)
        
        # Start ComfyUI in a thread
        def run_comfyui():
            loop, server, start_func = start_comfyui()
            x = start_func()
            loop.run_until_complete(x)
        
        comfy_thread = threading.Thread(target=run_comfyui, daemon=True)
        comfy_thread.start()
        
        # Wait for server to be ready
        start_time = time.time()
        while time.time() - start_time < 60:  # 60 second timeout
            try:
                response = requests.get(COMFY_API_URL)
                if response.status_code == 200:
                    print("\nComfyUI server is ready!")
                    return True
            except requests.exceptions.ConnectionError:
                time.sleep(1)
        
        print("Error: ComfyUI server failed to start within the timeout period")
        return False
        
    except Exception as e:
        print(f"Error starting ComfyUI server: {e}")
        return False

def start_flask_server():
    """Start the Flask API server"""
    print("\nStarting Flask API server on http://localhost:5002")
    app.run(host='0.0.0.0', port=5002, debug=True, use_reloader=False)

def get_available_lora_models():
    """
    Fetch available LoRA models from ComfyUI
    """
    from shared_utils import get_model_display_name
    formatted_models = []
    
    try:
        models = get_lora_models()
        
        # Convert filenames to more user-friendly names (using display name mapping when available)
        for filename in models:
            name = get_model_display_name(filename)
            formatted_models.append({
                "id": filename,
                "name": name,
                "filename": filename
            })
    except Exception as e:
        print(f"Error fetching LoRA models: {str(e)}")
    
    return formatted_models

@app.route('/', methods=['GET'])
def is_server_running():
    return jsonify({
        "status": "success"
        })

@app.route('/api/lora-models', methods=['GET'])
def handle_get_lora_models():
    """
    Endpoint to get available LoRA models
    """
    try:
        models = get_available_lora_models()
        return jsonify({
            "status": "success",
            "models": models
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500
        
@app.route('/api/add-api-key', methods=['POST'])
def add_api_key():
    """
    Update or add an API key in the .env file.
    Expects JSON: { "alias": "OPENAI_API_KEY", "api-key": "sk-..." }
    """
    try:
        data = request.get_json()
        alias = data.get('alias')
        api_key = data.get('api-key')

        if not alias or not api_key:
            return jsonify({"status": "error", "message": "Missing alias or api_key"}), 400

        env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
        lines = []
        found = False
        
        if os.path.exists(env_path):
            with open(env_path, 'r') as f:
                lines = f.readlines()

        new_lines = []
        for line in lines:
            if line.strip().startswith(f"{alias}="):
                new_lines.append(f"{alias}={api_key}\n")
                found = True
            else:
                new_lines.append(line)
        if not found:
            new_lines.append(f"\n{alias}={api_key}")

        with open(env_path, 'w') as f:
            f.writelines(new_lines)

        return jsonify({"status": "success", "message": f"{alias} updated in .env"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/fetch-prompt', methods=['GET'])
def fetch_prompt():
    """
    Endpoint to fetch random prompts
    """
    
    prompt_type = request.args.get('type')
    print(f"🎯 FETCH PROMPT CALLED - Type: {prompt_type}")
    
    prompt = fetch_positive_prompt() if prompt_type == 'positive' else fetch_negative_prompt()
    return jsonify({"status": "success", "prompt": prompt})

@app.route('/api/upscaler-models', methods=['GET'])
def get_upscaler_models_endpoint():

    models = get_upscaler_models()
    formatted = [{"id": m, "name": m.replace('.pth', ''), "filename": m} for m in models]
    return jsonify({"status": "success", "models": formatted})

@app.route('/api/show-in-folder', methods=['POST'])
def show_in_folder():
    """Show image file in system file manager (cross-platform)"""
    try:
        filename = request.json.get('filename')
        if not filename:
            return jsonify({"status": "error", "message": "No filename provided"}), 400
        
        output_dir, _ = get_directories()
        print(f"DEBUG: output_dir='{output_dir}', filename='{filename}'")
        image_path = os.path.join(output_dir, filename)
        
        if not os.path.exists(image_path):
            return jsonify({"status": "error", "message": "File not found"}), 404
        
        # Detect operating system and use appropriate command
        system = platform.system()
        
        if system == "Darwin":  # macOS
            subprocess.run(['open', '-R', image_path])
            return jsonify({"status": "success", "message": f"Opened {filename} in Finder"})
        elif system == "Windows":  # Windows
            subprocess.run(['explorer', '/select,', image_path])
            return jsonify({"status": "success", "message": f"Opened {filename} in File Explorer"})
        elif system == "Linux":  # Linux
            # Open the directory containing the file (can't highlight specific file reliably)
            subprocess.run(['xdg-open', output_dir])
            return jsonify({"status": "success", "message": f"Opened directory containing {filename}"})
        else:
            return jsonify({"status": "error", "message": f"Unsupported operating system: {system}"}), 400
            
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/send-to-img2img', methods=['POST'])
def send_to_img2img():
    """Send image to img2img tab"""
    try:
        filename = request.json.get('filename')
        if not filename:
            return jsonify({"status": "error", "message": "No filename provided"}), 400
        
        output_dir, _ = get_directories()
        image_path = os.path.join(output_dir, filename)
        
        if not os.path.exists(image_path):
            return jsonify({"status": "error", "message": "File not found"}), 404
            
        return jsonify({"status": "success", "message": "Image sent to img2img"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/send-to-extras', methods=['POST', 'OPTIONS'])
def send_to_extras():
    """Send image to extras tab"""
    if request.method == 'OPTIONS':
        # Respond to preflight request
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        return response
        
    try:
        filename = request.json.get('filename')
        if not filename:
            return jsonify({"status": "error", "message": "No filename provided"}), 400
        
        output_dir, _ = get_directories()
        image_path = os.path.join(output_dir, filename)
        
        if not os.path.exists(image_path):
            return jsonify({"status": "error", "message": "File not found"}), 404
            
        return jsonify({"status": "success", "message": "Image sent to extras"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
@app.route('/api/upload-controlnet-image', methods=['POST'])
def upload_controlnet_image():
    """
    Endpoint to upload ControlNet images directly to ComfyUI input directory
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

@app.route('/api/upload-model', methods=['POST'])
def upload_model():
    """
    Endpoint to upload model files to ComfyUI models directory
    Supports formats: .safetensors, .ckpt, .pth, .pt, .bin
    Supports types: checkpoints, loras, controlnet, upscale_models, vae, embeddings, hypernetworks
    """
    try:
        from shared_utils import upload_model_file

        if 'file' not in request.files:
            return jsonify({
                "status": "error",
                "message": "No file provided in request"
            }), 400

        file = request.files['file']
        model_type = request.form.get('model_type', 'checkpoints')

        result = upload_model_file(file, model_type)

        if not isinstance(result, tuple):
            return jsonify(result)

        response_data, status_code = result
        return jsonify(response_data), status_code

    except Exception as e:
        print(f"❌ Error in model upload endpoint: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/api/images/<filename>', methods=['GET'])
def serve_image(filename):
    """
    Serve images from multiple possible directories
    """
    try:
        # Use shared function
        from shared_utils import serve_image as serve_img
        return serve_img(filename)
            
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

if __name__ == "__main__":
    print("Starting Dream Layer backend services...")
    if start_comfy_server():
        start_flask_server()
    else:
        print("Failed to start ComfyUI server. Exiting...")
        sys.exit(1) 