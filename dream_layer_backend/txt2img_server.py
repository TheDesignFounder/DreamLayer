from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import uuid
import requests

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
    try:
        data = request.get_json()
        prompt = data.get("prompt", "a beautiful landscape")
        negative_prompt = data.get("negative_prompt", "")
        model_name = data.get("model", "v1-5-pruned-emaonly.safetensors")

        prompt_id = str(uuid.uuid4())[:8]

        workflow = {
            "prompt": {
                "1": {
                    "class_type": "LoadCheckpoint",
                    "inputs": {
                        "ckpt_name": model_name
                    }
                },
                "2": {
                    "class_type": "CLIPTextEncode",
                    "inputs": {
                        "text": prompt,
                        "clip": ["1", 0]
                    }
                },
                "3": {
                    "class_type": "CLIPTextEncode",
                    "inputs": {
                        "text": negative_prompt,
                        "clip": ["1", 0]
                    }
                },
                "4": {
                    "class_type": "EmptyLatentImage",
                    "inputs": {
                        "width": 512,
                        "height": 512,
                        "batch_size": 1
                    }
                },
                "5": {
                    "class_type": "KSampler",
                    "inputs": {
                        "model": ["1", 0],
                        "positive": ["2", 0],
                        "negative": ["3", 0],
                        "latent_image": ["4", 0],
                        "seed": 123456,
                        "steps": 20,
                        "cfg": 7,
                        "sampler_name": "euler",
                        "scheduler": "normal",
                        "denoise": 1.0
                    }
                },
                "6": {
                    "class_type": "VAEDecode",
                    "inputs": {
                        "samples": ["5", 0],
                        "vae": ["1", 2]
                    }
                },
                "7": {
                    "class_type": "SaveImage",
                    "inputs": {
                        "images": ["6", 0]
                    }
                }
            },
            "client_id": f"{prompt_id}_client"
        }

        # Send request to ComfyUI
        res = requests.post("http://localhost:8188/prompt", json=workflow)
        res.raise_for_status()

        return jsonify({"status": "success", "message": "Prompt submitted successfully"}), 200

    except Exception as e:
        print("[ERROR] Txt2Img:", e)
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    print("Starting Flask API server on http://localhost:5002")
    app.run(host='0.0.0.0', port=5002, debug=True)
