#!/usr/bin/env python3
import os
import sys
from PIL import Image, ImageDraw, ImageFont
import argparse
import textwrap

def get_jarvis_path():
    """Get the path to the jarvis.png file."""
    # Look in the same directory as this module
    module_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(module_dir, "static", "jarvis.png")

def wrap_text(text, font, max_width, draw):
    """Wrap text to fit within the specified width."""
    words = text.split()
    lines = []
    current_line = ""
    
    for word in words:
        test_line = current_line + " " + word if current_line else word
        bbox = draw.textbbox((0, 0), test_line, font=font)
        test_width = bbox[2] - bbox[0]
        
        if test_width <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
                current_line = word
            else:
                # Single word is too long, force it on its own line
                lines.append(word)
    
    if current_line:
        lines.append(current_line)
    
    return lines

def get_text_dimensions(lines, font, draw, line_spacing=1.2):
    """Calculate total dimensions of multi-line text."""
    if not lines:
        return 0, 0
    
    max_width = 0
    total_height = 0
    
    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=font)
        line_width = bbox[2] - bbox[0]
        line_height = bbox[3] - bbox[1]
        
        max_width = max(max_width, line_width)
        total_height += line_height
        
        if i < len(lines) - 1:  # Add spacing between lines
            total_height += int(line_height * (line_spacing - 1))
    
    return max_width, total_height

def create_jarvis_image(text, output_dir="~/jarvis"):
    """Create a Jarvis image with text overlay in the white area."""
    
    # Get the path to the jarvis.png file
    jarvis_path = get_jarvis_path()
    
    if not os.path.exists(jarvis_path):
        raise FileNotFoundError(f"Jarvis image not found at {jarvis_path}")
    
    # Open the base image
    img = Image.open(jarvis_path)
    draw = ImageDraw.Draw(img)
    
    # Get image dimensions
    img_width, img_height = img.size
    
    # Define the white area bounds (approximately the top portion)
    # Based on the image, the white area appears to be roughly the top 25% of the image
    white_area_height = int(img_height * 0.25)
    
    # Add padding to the text area
    padding = 20
    text_area_width = img_width - (2 * padding)
    text_area_height = white_area_height - (2 * padding)
    
    # Try to use bold system fonts, fallback to default if not available
    try:
        # Try bold system fonts first
        font_size = 48
        bold_font_paths = [
            "/System/Library/Fonts/Helvetica.ttc",  # macOS - try to get bold variant
            "/System/Library/Fonts/Arial Black.ttf",  # macOS
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",  # Linux
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",  # Linux
            "C:\\Windows\\Fonts\\arialbd.ttf",  # Windows Bold
            "C:\\Windows\\Fonts\\arial.ttf",  # Windows fallback
        ]
        
        font = None
        for font_path in bold_font_paths:
            if os.path.exists(font_path):
                try:
                    font = ImageFont.truetype(font_path, font_size)
                    break
                except:
                    continue
        
        if font is None:
            font = ImageFont.load_default()
    except:
        font = ImageFont.load_default()
    
    # Auto-adjust font size and wrap text to fit in the white area
    max_font_size = 72
    min_font_size = 12
    current_font_size = max_font_size
    
    while current_font_size >= min_font_size:
        # Update font size
        try:
            if font.path:  # TrueType font
                font = ImageFont.truetype(font.path, current_font_size)
            else:  # Default font - can't resize easily
                break
        except:
            break
        
        # Wrap text for current font size
        lines = wrap_text(text, font, text_area_width, draw)
        
        # Check if text fits in the available height
        text_width, text_height = get_text_dimensions(lines, font, draw)
        
        if text_height <= text_area_height and text_width <= text_area_width:
            break
        
        current_font_size -= 4
    
    # If we're using default font and text is too long, try simple line breaking
    if current_font_size < min_font_size or not hasattr(font, 'path'):
        # Simple word wrapping for default font
        wrapped_lines = textwrap.wrap(text, width=50)  # Rough character limit
        lines = wrapped_lines[:6]  # Limit to 6 lines maximum
    
    # Calculate starting position to center the text block
    total_text_width, total_text_height = get_text_dimensions(lines, font, draw)
    
    start_x = padding + (text_area_width - total_text_width) // 2
    start_y = padding + (text_area_height - total_text_height) // 2
    
    # Draw each line
    current_y = start_y
    line_spacing = 1.2
    
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        line_width = bbox[2] - bbox[0]
        line_height = bbox[3] - bbox[1]
        
        # Center each line horizontally
        line_x = start_x + (total_text_width - line_width) // 2
        
        # Draw text with bold effect (draw multiple times with slight offset)
        offsets = [(0, 0), (1, 0), (0, 1), (1, 1)]  # Creates bold effect
        for offset_x, offset_y in offsets:
            draw.text((line_x + offset_x, current_y + offset_y), line, fill="black", font=font)
        
        current_y += int(line_height * line_spacing)
    
    # Create output filename
    safe_text = "".join(c for c in text if c.isalnum() or c in (' ', '-', '_')).rstrip()
    safe_text = safe_text.replace(' ', '_')
    filename = f"jarvis_{safe_text}.png"
    
    # Expand the output directory path
    output_dir = os.path.expanduser(output_dir)
    os.makedirs(output_dir, exist_ok=True)
    
    output_path = os.path.join(output_dir, filename)
    img.save(output_path)
    
    return output_path

def main():
    parser = argparse.ArgumentParser(description="Generate Jarvis images with text overlay")
    parser.add_argument("text", help="Text to overlay on the image")
    parser.add_argument("-o", "--output", default="~/jarvis", 
                       help="Output directory (default: ~/jarvis)")
    
    args = parser.parse_args()
    
    try:
        output_path = create_jarvis_image(args.text, args.output)
        print(f"Generated: {output_path}")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()