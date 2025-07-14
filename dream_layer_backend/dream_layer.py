from flask import Flask, request, jsonify
from flask_cors import CORS
import uuid
import json
import os
import requests

app = Flask(__name__)
CORS(app)

# Update this path to wherever your model files are located
CHECKPOINTS_DIR = "../../Dream_Layer_Resources/models/checkpoints"
OUTPUT_DIR = "../../Dream_Layer_Resources/output"
COMFY_API_URL = "http://localhost:8188/prompt"

@app.route("/api/models", methods=["GET"])
def get_models():
    try:
        models = []
        for file in os.listdir(CHECKPOINTS_DIR):
            if file.endswith(".safetensors"):
                model_id = str(uuid.uuid4())
                models.append({
                    "id": model_id,
                    "name": os.path.splitext(file)[0],
                    "filename": file
                })
        return jsonify({"status": "success", "models": models})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route("/api/fetch-prompt", methods=["GET"])
def fetch_prompt():
    prompt_type = request.args.get("type", "positive")
    try:
        # For now, return static sample prompts
        if prompt_type == "positive":
            prompt = "a futuristic city at night, cyberpunk, high detail"
        else:
            prompt = "blurry, low-res, distorted"

        return jsonify({
            "status": "success",
            "prompt": prompt,
            "type": prompt_type,
            "message": "Prompt fetched successfully"
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.route("/api/upscaler-models", methods=["GET"])
def get_upscaler_models():
    # Placeholder for real upscaler models
    return jsonify({"models": ["ESRGAN", "R-ESRGAN 4x"]})

@app.route("/api/txt2img", methods=["POST"])
def txt2img():
    try:
        data = request.json
        prompt = data.get("prompt", "")
        negative_prompt = data.get("negative_prompt", "")
        model_name = data.get("model_name")

        # Load and update base graph
        with open("JSON.json", "r") as f:
            graph = json.load(f)

        # Dynamically update graph
        graph["prompt"]["1"]["inputs"]["ckpt_name"] = model_name
        graph["prompt"]["4"]["inputs"]["text"] = prompt
        graph["prompt"]["5"]["inputs"]["text"] = negative_prompt
        graph["client_id"] = str(uuid.uuid4())

        # Send to ComfyUI
        response = requests.post(COMFY_API_URL, json=graph)
        response.raise_for_status()

        return jsonify({"status": "success", "message": "Prompt submitted to ComfyUI"})
    except Exception as e:
        print(f"[ERROR] Txt2Img: Failed to submit prompt to ComfyUI", str(e))
        return jsonify({"status": "error", "message": str(e)})

if __name__ == "__main__":
    print("Starting Flask API server on http://localhost:5002")
    app.run(host="0.0.0.0", port=5100, debug=True)
