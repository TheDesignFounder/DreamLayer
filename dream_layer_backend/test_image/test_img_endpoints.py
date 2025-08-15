"""
Test file validation logic for testing model endpoint communication
"""


import base64
import json
import requests
from pathlib import Path

# Config
TXT2IMG_API_HOST = "http://127.0.0.1:5001"
IMG2IMG_API_HOST = "http://127.0.0.1:5004"

TEST_IMAGE_DIR = Path(__file__).parent / "test_image"
PNG_PATH = TEST_IMAGE_DIR / "test_image.png"
BASE64_PATH = TEST_IMAGE_DIR / "base64_txt_test_image.txt"  

# Paths for ComfyUI checkpoints 
COMFYUI_ROOT = Path(__file__).parent.parent.parent / "ComfyUI"
CHECKPOINTS_DIR = COMFYUI_ROOT / "models" / "checkpoints"

def get_checkpoints():
    if not CHECKPOINTS_DIR.exists():
        print(f"Checkpoints directory not found: {CHECKPOINTS_DIR}")
        return []
    return [f.name for f in CHECKPOINTS_DIR.iterdir() if f.suffix in {".safetensors", ".ckpt"}]

def get_base64_image() -> str:
    """Return base64 string from .txt if available, else generate from PNG."""
    if BASE64_PATH.exists():
        print(f"Reading existing Base64 from {BASE64_PATH}")
        return BASE64_PATH.read_text().strip()
    elif PNG_PATH.exists():
        print(f"Encoding {PNG_PATH} to Base64...")
        encoded = base64.b64encode(PNG_PATH.read_bytes()).decode("utf-8")
        BASE64_PATH.write_text(encoded)
        print(f"Saved Base64 to {BASE64_PATH}")
        return encoded
    else:
        raise FileNotFoundError(f"Neither {PNG_PATH} nor {BASE64_PATH} found.")

def pretty_print_response(title: str, resp: requests.Response):
    print(f"\n--- {title} ---")
    print(f"Status: {resp.status_code}")
    try:
        data = resp.json()
        print(json.dumps(data, indent=2)[:1500])  # truncated preview
    except Exception as e:
        print("Failed to parse JSON:", e)
        print(resp.text[:1500])

if __name__ == "__main__":
    print("Running DreamLayer API Tests")

    checkpoints = get_checkpoints()
    if checkpoints:
        print(f"Available checkpoints: {checkpoints}")
        ckpt_name = checkpoints[0]
    else:
        print("No checkpoints found, proceeding without ckpt_name")
        ckpt_name = None

    base64_img = get_base64_image()

    # TXT2IMG Request payload based on your curl details
    txt2img_payload = {
        "prompt": "a red fox in a snowy forest",
        "negative_prompt": "",
        "width": 512,
        "height": 512,
        "batch_size": 1,
        "steps": 20,
        "cfg_scale": 7.0,
        "sampler_name": "euler",
        "scheduler": "normal",
        "seed": 42,
        "ckpt_name": ckpt_name,
        "denoise": 1.0
    }

    r1 = requests.post(f"{TXT2IMG_API_HOST}/api/txt2img", json=txt2img_payload)
    pretty_print_response("TXT2IMG Response", r1)

    # IMG2IMG Request payload
    img2img_payload = {
        "prompt": "Translate this image into an impressionist style",
        "negative_prompt": "",
        "width": 512,
        "height": 512,
        "batch_size": 1,
        "steps": 20,
        "cfg_scale": 7.0,
        "sampler_name": "euler",
        "scheduler": "normal",
        "seed": 42,
        "input_image": base64_img,
        "denoising_strength": 0.6,
        "ckpt_name": ckpt_name
    }

    r2 = requests.post(f"{IMG2IMG_API_HOST}/api/img2img", json=img2img_payload)
    pretty_print_response("IMG2IMG Response", r2)

    print("\nTest completed!")
