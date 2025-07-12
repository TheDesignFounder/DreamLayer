from flask import Flask, request, jsonify
from flask_cors import CORS
import base64
import json
import logging
import os
from PIL import Image
import io
import time
from shared_utils import send_to_comfyui
from img2img_workflow import transform_to_img2img_workflow
from shared_utils import COMFY_API_URL
from dream_layer_backend_utils.fetch_advanced_models import get_controlnet_models

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
COMFY_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ComfyUI's input directory should be inside the ComfyUI directory
COMFY_UI_DIR = os.path.join(COMFY_ROOT, "ComfyUI")
COMFY_INPUT_DIR = os.path.join(COMFY_UI_DIR, "input")
COMFY_OUTPUT_DIR = os.path.join(COMFY_UI_DIR, "output")

# Create a directory to store our served images
SERVED_IMAGES_DIR = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), "served_images")
os.makedirs(SERVED_IMAGES_DIR, exist_ok=True)

logger.info(f"ComfyUI root directory: {COMFY_ROOT}")
logger.info(f"ComfyUI directory: {COMFY_UI_DIR}")
logger.info(f"ComfyUI input directory: {COMFY_INPUT_DIR}")
logger.info(f"ComfyUI output directory: {COMFY_OUTPUT_DIR}")


def verify_input_directory():
    """Verify that the input directory exists and is writable"""
    if not os.path.exists(COMFY_INPUT_DIR):
        raise RuntimeError(
            f"Input directory does not exist: {COMFY_INPUT_DIR}")
    if not os.access(COMFY_INPUT_DIR, os.W_OK):
        raise RuntimeError(
            f"Input directory is not writable: {COMFY_INPUT_DIR}")
    logger.info(f"Verified input directory: {COMFY_INPUT_DIR}")


# Verify input directory on startup
verify_input_directory()


def process_uploaded_file(file, file_type="image"):
    """
    Process an uploaded file and save it to ComfyUI input directory

    Args:
        file: Flask file object
        file_type: Type of file ("image" or "mask")

    Returns:
        str: Filename of the saved file
    """
    if not file or file.filename == '':
        raise ValueError(f"No {file_type} file provided")

    # Validate file type for mask
    if file_type == "mask":
        if file.content_type != "image/png":
            raise ValueError("Mask file must be PNG format")
        if file.content_length and file.content_length > 10 * 1024 * 1024:  # 10MB
            raise ValueError("Mask file size must be 10 MB or less")

    # Generate unique filename
    timestamp = int(time.time())
    filename = f"{file_type}_{timestamp}.png"
    filepath = os.path.join(COMFY_INPUT_DIR, filename)

    # Save the file
    file.save(filepath)

    # Verify the file was saved
    if not os.path.exists(filepath):
        raise RuntimeError(f"Failed to save {file_type} file to {filepath}")

    # Verify the saved file can be opened as an image
    try:
        with Image.open(filepath) as verify_img:
            verify_img.verify()
        logger.info(f"Verified saved {file_type}: {filepath}")
    except Exception as e:
        raise RuntimeError(f"Saved {file_type} verification failed: {str(e)}")

    logger.info(f"{file_type.capitalize()} saved as: {filename}")
    return filename


# Using shared functions from shared_utils.py

@app.route('/api/img2img', methods=['POST', 'OPTIONS'])
def handle_img2img():
    if request.method == 'OPTIONS':
        # Handle preflight request
        response = jsonify({'status': 'ok'})
        response.headers.add('Access-Control-Allow-Origin',
                             'http://localhost:8080')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST, OPTIONS')
        return response

    try:
        # Verify input directory before processing
        verify_input_directory()

        # Check if this is multipart form data (new format) or JSON (old format)
        if request.content_type and 'multipart/form-data' in request.content_type:
            # Handle multipart form data with files
            logger.info("Processing multipart form data request")

            # Get files from multipart form data
            image_file = request.files.get('image')
            mask_file = request.files.get('mask')
            params_json = request.form.get('params')

            logger.info(
                f"Received image: {image_file.filename if image_file else None}")
            logger.info(
                f"Received mask: {mask_file.filename if mask_file else None}")
            logger.info(f"Received params: {params_json}")

            if not image_file:
                return jsonify({
                    'status': 'error',
                    'message': 'No image file provided'
                }), 400

            if not params_json:
                return jsonify({
                    'status': 'error',
                    'message': 'No parameters provided'
                }), 400

            try:
                data = json.loads(params_json)
            except json.JSONDecodeError:
                return jsonify({
                    'status': 'error',
                    'message': 'Invalid parameters format'
                }), 400

            # Process the uploaded image file
            try:
                input_filename = process_uploaded_file(image_file, "image")
                data['input_image'] = input_filename
            except Exception as e:
                logger.error(f"Error processing input image: {str(e)}")
                return jsonify({
                    'status': 'error',
                    'message': f'Invalid input image: {str(e)}'
                }), 400

            # Process the uploaded mask file if present
            if mask_file:
                try:
                    mask_filename = process_uploaded_file(mask_file, "mask")
                    data['mask_image'] = mask_filename
                    logger.info(f"Mask file processed: {mask_filename}")
                except Exception as e:
                    logger.error(f"Error processing mask file: {str(e)}")
                    return jsonify({
                        'status': 'error',
                        'message': f'Invalid mask file: {str(e)}'
                    }), 400

            # Validate required fields
            required_fields = ['prompt', 'denoising_strength']
            for field in required_fields:
                if field not in data:
                    return jsonify({
                        'status': 'error',
                        'message': f'Missing required field: {field}'
                    }), 400

        else:
            # Handle JSON request (existing format)
            logger.info("Processing JSON request")
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

            # Process the input image (base64 format)
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
                    raise RuntimeError(
                        f"Failed to save image to {temp_filepath}")

                # Verify the saved image can be opened
                try:
                    with Image.open(temp_filepath) as verify_img:
                        verify_img.verify()
                    logger.info(f"Verified saved image: {temp_filepath}")
                except Exception as e:
                    raise RuntimeError(
                        f"Saved image verification failed: {str(e)}")

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

        # Transform data to ComfyUI workflow
        workflow = transform_to_img2img_workflow(data)

        # Log the workflow for debugging
        logger.info("Generated workflow:")
        logger.info(json.dumps(workflow, indent=2))

        # Send to ComfyUI
        comfy_response = send_to_comfyui(workflow)

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

        response = jsonify({
            "status": "success",
            "message": "Workflow sent to ComfyUI successfully",
            "comfy_response": comfy_response,
            "workflow": workflow
        })

        # Clean up temporary files if they were created in this request
        if 'temp_filepath' in locals():
            try:
                os.remove(temp_filepath)
                logger.info(f"Cleaned up temporary file: {temp_filepath}")
            except Exception as e:
                logger.warning(
                    f"Failed to remove temporary file {temp_filepath}: {str(e)}")

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
