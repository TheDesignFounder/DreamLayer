#!/usr/bin/env python3
"""
Create a before/after comparison image for Task 3 demo.
"""

from PIL import Image, ImageDraw, ImageFont

def create_comparison():
    """Create a side-by-side comparison of before and after grids."""
    
    # Load the before and after images
    before_img = Image.open("docs/task3_before.png")
    after_img = Image.open("docs/task3_after.png")
    
    # Create a new image with both side by side
    total_width = before_img.width + after_img.width + 100  # 100px gap
    max_height = max(before_img.height, after_img.height) + 150  # 150px for labels
    
    comparison = Image.new('RGB', (total_width, max_height), color=(248, 249, 250))
    draw = ImageDraw.Draw(comparison)
    
    # Try to load a nice font
    try:
        title_font = ImageFont.truetype("arial.ttf", 24)
        subtitle_font = ImageFont.truetype("arial.ttf", 16)
    except:
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()
    
    # Add title
    title_text = "Task 3: CLIP AI-powered Auto-labeling"
    title_bbox = draw.textbbox((0, 0), title_text, font=title_font)
    title_width = title_bbox[2] - title_bbox[0]
    title_x = (total_width - title_width) // 2
    draw.text((title_x, 20), title_text, fill=(51, 51, 51), font=title_font)
    
    # Position images
    y_offset = 80
    before_x = 20
    after_x = before_img.width + 80
    
    # Paste images
    comparison.paste(before_img, (before_x, y_offset))
    comparison.paste(after_img, (after_x, y_offset))
    
    # Add "Before" and "After" labels
    before_text = "BEFORE: CSV Metadata Labels"
    after_text = "AFTER: CLIP AI-Generated Labels"
    
    # Before label
    before_bbox = draw.textbbox((0, 0), before_text, font=subtitle_font)
    before_width = before_bbox[2] - before_bbox[0]
    before_label_x = before_x + (before_img.width - before_width) // 2
    draw.text((before_label_x, y_offset + before_img.height + 20), before_text, fill=(220, 53, 69), font=subtitle_font)
    
    # After label  
    after_bbox = draw.textbbox((0, 0), after_text, font=subtitle_font)
    after_width = after_bbox[2] - after_bbox[0]
    after_label_x = after_x + (after_img.width - after_width) // 2
    draw.text((after_label_x, y_offset + after_img.height + 20), after_text, fill=(25, 135, 84), font=subtitle_font)
    
    # Add description
    desc_text = "CLIP automatically understands image content and generates meaningful descriptions"
    desc_bbox = draw.textbbox((0, 0), desc_text, font=subtitle_font)
    desc_width = desc_bbox[2] - desc_bbox[0]
    desc_x = (total_width - desc_width) // 2
    draw.text((desc_x, y_offset + before_img.height + 60), desc_text, fill=(108, 117, 125), font=subtitle_font)
    
    # Save the comparison
    comparison.save("docs/task3_demo.png", optimize=True, quality=95)
    print("✅ Demo comparison created: docs/task3_demo.png")
    print(f"   Size: {comparison.width}x{comparison.height}")
    
    # Also create a smaller version for README
    small_comparison = comparison.resize((800, int(800 * comparison.height / comparison.width)), Image.Resampling.LANCZOS)
    small_comparison.save("docs/task3_demo_small.png", optimize=True, quality=90)
    print("✅ Small demo created: docs/task3_demo_small.png")
    print(f"   Size: {small_comparison.width}x{small_comparison.height}")

if __name__ == "__main__":
    create_comparison()