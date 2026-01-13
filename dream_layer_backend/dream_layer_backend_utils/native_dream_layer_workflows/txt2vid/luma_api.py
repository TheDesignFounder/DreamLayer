import os
import requests
import time
import logging
from dotenv import load_dotenv

def generate_luma_video(prompt, output_dir, model="ray-2", aspect_ratio="16:9", loop=True,
                       resolution=None, duration=None):
    """Generate video using Luma API"""
    load_dotenv()
    api_key = os.getenv("LUMA_API_KEY")
    if not api_key:
        return {"error": "LUMA_API_KEY not found in .env"}

    payload = {"model": model, "prompt": prompt, "aspect_ratio": aspect_ratio, "loop": loop}
    if resolution: payload["resolution"] = resolution
    if duration: payload["duration"] = duration

    response = requests.post("https://api.lumalabs.ai/dream-machine/v1/generations/video",
                           headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                           json=payload)

    response_data = response.json()
    if "id" not in response_data:
        return {"error": f"API Error: {response_data}"}

    gen_id = response_data["id"]

    while True:
        status = requests.get(f"https://api.lumalabs.ai/dream-machine/v1/generations/{gen_id}",
                            headers={"Authorization": f"Bearer {api_key}"}).json()
        logging.info(f"Polling Luma generation {gen_id[:8]}... Status: {status.get('state', 'unknown')}")
        if status["state"] == "completed":
            video_url = status["assets"]["video"]
            video_data = requests.get(video_url).content
            filename = f"LUMA_VIDEO_{gen_id[:8].upper()}.mp4"
            file_path = os.path.join(output_dir, filename)
            with open(file_path, "wb") as f:
                f.write(video_data)
            return {"success": True, "file": file_path, "filename": filename}
        elif status["state"] == "failed":
            return {"error": f"Generation failed: {status.get('failure_reason', 'Unknown error')}"}
        time.sleep(10)
