"""
Simple script to create a basic Open Graph image placeholder.
Run with: python create_og_image.py
Requires: pip install pillow
"""

from PIL import Image, ImageDraw, ImageFont
import os

# Image dimensions (Facebook/LinkedIn recommended)
WIDTH = 1200
HEIGHT = 630

# Colors
BACKGROUND = "#0d6efd"  # Bootstrap primary blue
TEXT_COLOR = "#ffffff"
ACCENT_COLOR = "#ffc107"  # Bootstrap warning yellow

# Create image
img = Image.new('RGB', (WIDTH, HEIGHT), color=BACKGROUND)
draw = ImageDraw.Draw(img)

# Try to use a nice font, fallback to default
try:
    title_font = ImageFont.truetype("arial.ttf", 80)
    subtitle_font = ImageFont.truetype("arial.ttf", 40)
    small_font = ImageFont.truetype("arial.ttf", 30)
except:
    # Fallback to default font
    title_font = ImageFont.load_default()
    subtitle_font = ImageFont.load_default()
    small_font = ImageFont.load_default()

# Add gradient effect (simple darkening at bottom)
for y in range(HEIGHT):
    darkness = int(30 * (y / HEIGHT))
    for x in range(WIDTH):
        r, g, b = img.getpixel((x, y))
        img.putpixel((x, y), (max(0, r - darkness), max(0, g - darkness), max(0, b - darkness)))

# Add text with shadow effect
def draw_text_with_shadow(text, font, y_position, color=TEXT_COLOR):
    # Get text size
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    x_position = (WIDTH - text_width) // 2
    
    # Draw shadow
    draw.text((x_position + 3, y_position + 3), text, fill="#000000", font=font)
    # Draw main text
    draw.text((x_position, y_position), text, fill=color, font=font)

# Main content
draw_text_with_shadow("🤖 Marketing Agent", title_font, 150)
draw_text_with_shadow("KI-gestützte Marketing Automation", subtitle_font, 270)

# Features
features_y = 380
draw_text_with_shadow("✓ Telegram  ✓ LinkedIn  ✓ Facebook  ✓ Instagram", small_font, features_y, ACCENT_COLOR)

# Branding
draw_text_with_shadow("Andrii-IT", subtitle_font, 500)

# Save image
output_path = os.path.join("app", "static", "img", "og-default.jpg")
os.makedirs(os.path.dirname(output_path), exist_ok=True)
img.save(output_path, "JPEG", quality=90)
print(f"✅ Open Graph image created: {output_path}")
print(f"📏 Size: {WIDTH}x{HEIGHT}px")
print(f"📦 File size: {os.path.getsize(output_path) / 1024:.2f} KB")
