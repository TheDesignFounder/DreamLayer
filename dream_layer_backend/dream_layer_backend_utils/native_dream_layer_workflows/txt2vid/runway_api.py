import os
import requests
import time
import logging
from dotenv import load_dotenv

def generate_runway_video(prompt, output_dir, model="veo3.1", ratio="1280:720", duration=6, seed=None, audio=False, mode="text2vid", input_image=None):
    """Generate video using Runway API

    Args:
        prompt: Text prompt or description
        output_dir: Directory to save the video
        model: Model to use (veo3.1, veo3.1_fast, veo3, gen4_turbo, gen3a_turbo, gen4_aleph)
        ratio: Video aspect ratio
        duration: Video duration in seconds (4, 6, or 8)
        seed: Random seed (-1 for random)
        audio: Whether to generate audio (only for veo models)
               - With audio: 40 credits/sec for veo3.1, 15 credits/sec for veo3.1_fast
               - Without audio: 20 credits/sec for veo3.1, 10 credits/sec for veo3.1_fast
        mode: Generation mode ('text2vid' or 'img2vid')
        input_image: Base64 encoded image (required for img2vid mode)
    """
    load_dotenv()
    api_key = os.getenv("RUNWAY_API_KEY")
    if not api_key:
        return {"error": "RUNWAY_API_KEY not found in .env"}

    # Ensure duration is an integer (not array or string)
    duration_int = int(duration) if duration else 6

    # Choose endpoint and build payload based on mode
    if mode == "img2vid" and input_image:
        # Step 1: Upload image to Runway and get runway:// URL
        logging.info("Uploading image to Runway...")

        # Extract base64 data if it includes data URI prefix
        image_data = input_image
        if 'base64,' in input_image:
            image_data = input_image.split('base64,')[1]

        # Upload to Runway's upload endpoint
        upload_response = requests.post(
            "https://api.dev.runwayml.com/v1/uploads",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "X-Runway-Version": "2024-11-06"
            },
            json={
                "filename": "input_image.png",
                "type": "ephemeral"
            }
        )

        upload_data = upload_response.json()
        if "runwayUri" not in upload_data or "uploadUrl" not in upload_data:
            return {"error": f"Failed to initiate upload: {upload_data}"}

        runway_image_url = upload_data["runwayUri"]
        upload_url = upload_data["uploadUrl"]
        upload_fields = upload_data.get("fields", {})

        # Upload the actual image data using multipart form
        import base64
        image_bytes = base64.b64decode(image_data)

        # Prepare multipart form data with fields from response
        files = {'file': ('input_image.png', image_bytes, 'image/png')}

        upload_file_response = requests.post(
            upload_url,
            data=upload_fields,
            files=files
        )

        if upload_file_response.status_code not in [200, 201, 204]:
            return {"error": f"Failed to upload image: {upload_file_response.status_code} - {upload_file_response.text}"}

        logging.info(f"Image uploaded successfully: {runway_image_url}")

        # Step 2: Create video generation request with runway:// URL
        endpoint = "https://api.dev.runwayml.com/v1/image_to_video"
        payload = {
            "promptImage": runway_image_url,
            "model": model,
            "ratio": ratio,
            "duration": duration_int,
            "position": "first"
        }
        # Add promptText if provided for img2vid
        if prompt:
            payload["promptText"] = prompt
    else:
        # text2vid mode
        endpoint = "https://api.dev.runwayml.com/v1/text_to_video"
        payload = {"promptText": prompt, "model": model, "ratio": ratio, "duration": duration_int}
        # Only add audio for veo models in text2vid mode
        if model in ['veo3.1', 'veo3.1_fast', 'veo3']:
            payload["audio"] = audio

    if seed and seed != -1:
        payload["seed"] = int(seed)

    logging.info(f"Runway API payload: {payload}")

    response = requests.post(endpoint,
                           headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json",
                                   "X-Runway-Version": "2024-11-06"}, json=payload)

    response_data = response.json()
    if "id" not in response_data:
        return {"error": f"API Error: {response_data}"}

    task_id = response_data["id"]

    while True:
        status = requests.get(f"https://api.dev.runwayml.com/v1/tasks/{task_id}",
                            headers={"Authorization": f"Bearer {api_key}", "X-Runway-Version": "2024-11-06"}).json()
        logging.info(f"Polling Runway task {task_id[:8]}... Status: {status.get('status', 'unknown')}")
        if status["status"] == "SUCCEEDED":
            video_url = status["output"][0]
            video_data = requests.get(video_url).content
            filename = f"RUNWAY_VIDEO_{task_id[:8].upper()}.mp4"
            file_path = os.path.join(output_dir, filename)
            with open(file_path, "wb") as f:
                f.write(video_data)
            return {"success": True, "file": file_path, "filename": filename}
        elif status["status"] == "FAILED":
            return {"error": f"Generation failed: {status.get('failure', 'Unknown error')}"}
        time.sleep(10)
