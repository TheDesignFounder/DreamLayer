from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import json
import os
import logging
import base64
import uuid
from dream_layer import get_directories
from dream_layer_backend_utils.native_dream_layer_workflows.txt2vid.luma_api import generate_luma_video
from dream_layer_backend_utils.native_dream_layer_workflows.txt2vid.runway_api import generate_runway_video
import generation_history as gh

app = Flask(__name__)
CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:*", "http://127.0.0.1:*"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# Setup logging
logs_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
os.makedirs(logs_dir, exist_ok=True)
logging.basicConfig(
    filename=os.path.join(logs_dir, 'txt2vid_server.log'),
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filemode='a'
)

output_dir, _ = get_directories()
VIDEO_OUTPUT_DIR = os.path.join(output_dir, 'videos')
os.makedirs(VIDEO_OUTPUT_DIR, exist_ok=True)

# Create temp directory for image-to-video input images
TEMP_IMAGES_DIR = os.path.join(output_dir, 'temp_images')
os.makedirs(TEMP_IMAGES_DIR, exist_ok=True)

@app.route('/api/txt2vid', methods=['POST', 'OPTIONS'])
def handle_txt2vid():
    if request.method == 'OPTIONS':
        return jsonify({"status": "ok"})

    try:
        data = request.json
        logging.info(f"Received txt2vid request: {json.dumps(data, indent=2)}")

        if not data or 'prompt' not in data:
            logging.error("Missing prompt in request")
            return jsonify({"status": "error", "message": "Missing prompt"}), 400

        provider = data.get('provider', data.get('model', 'luma')).lower()
        logging.info(f"Using provider: {provider}")

        if provider == 'luma':
            luma_model = data.get('luma_model', 'ray-2')
            logging.info(f"Using Luma model: {luma_model}")

            # Luma doesn't support img2vid (requires publicly accessible CDN URL)
            if data.get('input_image'):
                logging.error("Luma AI does not support image-to-video (requires CDN URL)")
                return jsonify({
                    "status": "error",
                    "message": "Luma AI does not support image-to-video. Please use Runway ML for img2vid generation."
                }), 400

            result = generate_luma_video(
                prompt=data['prompt'],
                output_dir=VIDEO_OUTPUT_DIR,
                model=luma_model,
                aspect_ratio=data.get('aspect_ratio', '16:9'),
                loop=data.get('loop', True),
                resolution=data.get('resolution'),
                duration=data.get('duration')
            )
        elif provider == 'runway':
            runway_model = data.get('runway_model', 'veo3')
            runway_mode = data.get('runway_mode', 'text2vid')
            logging.info(f"Using Runway model: {runway_model}, mode: {runway_mode}")
            result = generate_runway_video(
                prompt=data.get('prompt', ''),
                output_dir=VIDEO_OUTPUT_DIR,
                model=runway_model,
                ratio=data.get('ratio', '1280:720'),
                duration=data.get('duration', 4),
                seed=data.get('seed'),
                audio=data.get('audio', False),  # Default to False to save credits
                mode=runway_mode,
                input_image=data.get('input_image')  # Base64 image for img2vid
            )
        else:
            logging.error(f"Unsupported provider: {provider}")
            return jsonify({"status": "error", "message": f"Unsupported provider: {provider}"}), 400

        logging.info(f"Generation result: {result}")

        if "error" in result:
            logging.error(f"Generation failed: {result['error']}")
            return jsonify({"status": "error", "message": result["error"]}), 500

        # Save to history database
        # Determine generation type based on provider and input image
        if provider == 'runway':
            generation_type = data.get('runway_mode', 'text2vid')
        elif provider == 'luma':
            # Luma: img2vid if input_image present, otherwise txt2vid
            generation_type = 'img2vid' if data.get('input_image') else 'txt2vid'
        else:
            generation_type = 'txt2vid'

        if generation_type not in ['txt2vid', 'img2vid']:
            generation_type = 'txt2vid'  # Default to txt2vid

        video_url = f"http://localhost:5008/api/videos/{result['filename']}"
        history_data = {
            'id': result['filename'],
            'type': generation_type,
            'filename': result['filename'],
            'file_path': result['file'],
            'url': video_url,
            'prompt': data.get('prompt', ''),
            'settings': data  # Save all request settings
        }

        try:
            gh.save_generation(history_data)
            logging.info(f"Saved to history: {result['filename']}")
        except Exception as e:
            logging.error(f"Failed to save to history: {str(e)}")
            # Don't fail the request if history save fails

        response = {
            "status": "success",
            "message": "Video generated successfully",
            "filename": result["filename"]
        }
        logging.info(f"Returning success response: {response}")
        return jsonify(response)

    except Exception as e:
        logging.error(f"Error in handle_txt2vid: {str(e)}", exc_info=True)
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/videos/<filename>', methods=['GET'])
def serve_video(filename):
    try:
        logging.info(f"Serving video: {filename}")
        file_path = os.path.join(VIDEO_OUTPUT_DIR, filename)
        if os.path.exists(file_path):
            return send_file(file_path, mimetype='video/mp4')
        logging.error(f"Video not found: {filename}")
        return jsonify({"error": "Video not found"}), 404
    except Exception as e:
        logging.error(f"Error serving video {filename}: {str(e)}")
        return jsonify({"error": str(e)}), 404

@app.route('/api/temp-images/<filename>', methods=['GET'])
def serve_temp_image(filename):
    """Serve temporary images for Luma img2vid (CDN URL requirement)"""
    try:
        logging.info(f"Serving temp image: {filename}")
        file_path = os.path.join(TEMP_IMAGES_DIR, filename)
        if os.path.exists(file_path):
            return send_file(file_path, mimetype='image/png')
        logging.error(f"Temp image not found: {filename}")
        return jsonify({"error": "Image not found"}), 404
    except Exception as e:
        logging.error(f"Error serving temp image {filename}: {str(e)}")
        return jsonify({"error": str(e)}), 404

@app.route('/api/open-videos-folder', methods=['POST', 'OPTIONS'])
def open_videos_folder():
    if request.method == 'OPTIONS':
        return jsonify({"status": "ok"})

    try:
        import platform
        import subprocess

        logging.info(f"Opening videos folder: {VIDEO_OUTPUT_DIR}")

        system = platform.system()
        if system == 'Darwin':  # macOS
            subprocess.run(['open', VIDEO_OUTPUT_DIR])
        elif system == 'Windows':
            subprocess.run(['explorer', VIDEO_OUTPUT_DIR])
        elif system == 'Linux':
            subprocess.run(['xdg-open', VIDEO_OUTPUT_DIR])

        return jsonify({"status": "success", "message": f"Opened folder: {VIDEO_OUTPUT_DIR}"})
    except Exception as e:
        logging.error(f"Error opening videos folder: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/available-providers', methods=['GET'])
def get_available_providers():
    """Check which video providers have API keys configured"""
    try:
        from dotenv import load_dotenv
        load_dotenv()

        providers = {
            'luma': bool(os.getenv('LUMA_API_KEY')),
            'runway': bool(os.getenv('RUNWAY_API_KEY'))
        }

        logging.info(f"Available providers: {providers}")
        return jsonify({
            "status": "success",
            "providers": providers
        })
    except Exception as e:
        logging.error(f"Error checking available providers: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    logging.info("Starting Txt2Vid server on port 5008...")
    print("Starting Txt2Vid server on port 5008...")
    app.run(debug=True, host='0.0.0.0', port=5008)
