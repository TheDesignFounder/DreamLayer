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



@app.route('/debug/reproduce', methods=['POST', 'OPTIONS'])
def handle_txt2img():
    """Handle text-to-image generation requests"""
    pass