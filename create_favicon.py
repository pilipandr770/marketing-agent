"""
Simple script to create a basic favicon.
Run with: python create_favicon.py
Requires: pip install pillow
"""

from PIL import Image, ImageDraw, ImageFont
import os

# Favicon dimensions
SIZE = 64

# Colors
BACKGROUND = "#0d6efd"  # Bootstrap primary blue
TEXT_COLOR = "#ffffff"

# Create image
img = Image.new('RGB', (SIZE, SIZE), color=BACKGROUND)
draw = ImageDraw.Draw(img)

# Try to use a nice font, fallback to default
try:
    font = ImageFont.truetype("arial.ttf", 40)
except:
    # Fallback to default font
    font = ImageFont.load_default()

# Draw robot emoji or letter "M"
text = "🤖"
try:
    # Try emoji first
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (SIZE - text_width) // 2
    y = (SIZE - text_height) // 2 - 5
    draw.text((x, y), text, fill=TEXT_COLOR, font=font)
except:
    # Fallback to letter "M"
    text = "M"
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (SIZE - text_width) // 2
    y = (SIZE - text_height) // 2 - 5
    draw.text((x, y), text, fill=TEXT_COLOR, font=font)

# Save image
output_path = os.path.join("app", "static", "img", "favicon.png")
os.makedirs(os.path.dirname(output_path), exist_ok=True)
img.save(output_path, "PNG")
print(f"✅ Favicon created: {output_path}")
print(f"📏 Size: {SIZE}x{SIZE}px")
