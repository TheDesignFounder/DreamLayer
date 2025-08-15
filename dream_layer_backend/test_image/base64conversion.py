import base64
from pathlib import Path

# Folder containing images
folder = Path(__file__).parent  # assuming this script is inside test_image folder

# Supported image extensions
img_extensions = {".png", ".jpg", ".jpeg", ".bmp", ".gif"}

# Find first image file in folder
image_files = [f for f in folder.iterdir() if f.suffix.lower() in img_extensions]

if not image_files:
    raise FileNotFoundError(f"No image files found in {folder}")

input_img_path = image_files[0]
base64_txt_path = folder / "base64_txt_test_image.txt"
output_img_path = folder / "test_image.png"

print(f"Using input image: {input_img_path.name}")

# Read image bytes
with open(input_img_path, "rb") as f:
    img_bytes = f.read()

# Encode to base64 string
base64_img = base64.b64encode(img_bytes).decode("utf-8")

# Save base64 string to 4.txt
with open(base64_txt_path, "w") as f:
    f.write(base64_img)

print(f"Saved base64 string to {base64_txt_path}")

# Decode base64 string back to bytes
decoded_bytes = base64.b64decode(base64_img)

# Save decoded bytes as new PNG file
with open(output_img_path, "wb") as f:
    f.write(decoded_bytes)

print(f"Saved decoded image as {output_img_path}")
