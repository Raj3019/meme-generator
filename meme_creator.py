"""
Meme Creator module using Pillow.
Handles adding text overlays to images in classic meme format.
"""

from PIL import Image, ImageDraw, ImageFont, ImageFilter
from io import BytesIO
import os


def get_font(size: int) -> ImageFont.FreeTypeFont:
    """
    Get a bold font for meme text.
    Falls back to default font if Impact is not available.
    """
    # Try common font paths
    font_paths = [
        "C:/Windows/Fonts/impact.ttf",
        "C:/Windows/Fonts/IMPACT.TTF",
        "/usr/share/fonts/truetype/msttcorefonts/Impact.ttf",
        "/System/Library/Fonts/Supplemental/Impact.ttf",
        "impact.ttf",
    ]
    
    for font_path in font_paths:
        try:
            if os.path.exists(font_path):
                return ImageFont.truetype(font_path, size)
        except:
            continue
    
    # Try Arial Bold as fallback
    arial_paths = [
        "C:/Windows/Fonts/arialbd.ttf",
        "C:/Windows/Fonts/Arial Bold.ttf",
    ]
    
    for font_path in arial_paths:
        try:
            if os.path.exists(font_path):
                return ImageFont.truetype(font_path, size)
        except:
            continue
    
    # Ultimate fallback - use default
    try:
        return ImageFont.load_default()
    except:
        return None


def wrap_text(text: str, font: ImageFont.FreeTypeFont, max_width: int, draw: ImageDraw.ImageDraw) -> list:
    """
    Wrap text to fit within a maximum width.
    
    Args:
        text: The text to wrap
        font: The font to use
        max_width: Maximum width in pixels
        draw: ImageDraw object for measuring text
    
    Returns:
        List of text lines
    """
    words = text.split()
    lines = []
    current_line = []
    
    for word in words:
        test_line = ' '.join(current_line + [word])
        bbox = draw.textbbox((0, 0), test_line, font=font)
        width = bbox[2] - bbox[0]
        
        if width <= max_width:
            current_line.append(word)
        else:
            if current_line:
                lines.append(' '.join(current_line))
            current_line = [word]
    
    if current_line:
        lines.append(' '.join(current_line))
    
    return lines


def draw_text_with_outline(draw: ImageDraw.ImageDraw, position: tuple, text: str, 
                           font: ImageFont.FreeTypeFont, fill_color: str = "white", 
                           outline_color: str = "black", outline_width: int = 3) -> None:
    """
    Draw text with an outline effect for better readability.
    
    Args:
        draw: ImageDraw object
        position: (x, y) position for the text
        text: The text to draw
        font: The font to use
        fill_color: Main text color
        outline_color: Outline color
        outline_width: Width of the outline
    """
    x, y = position
    
    # Draw outline by drawing text in offset positions
    for dx in range(-outline_width, outline_width + 1):
        for dy in range(-outline_width, outline_width + 1):
            if dx != 0 or dy != 0:
                draw.text((x + dx, y + dy), text, font=font, fill=outline_color)
    
    # Draw the main text
    draw.text(position, text, font=font, fill=fill_color)


def calculate_font_size(text: str, max_width: int, max_height: int, draw: ImageDraw.ImageDraw) -> int:
    """
    Calculate the optimal font size to fit text within bounds.
    
    Args:
        text: The text to fit
        max_width: Maximum width in pixels
        max_height: Maximum height in pixels
        draw: ImageDraw object
    
    Returns:
        Optimal font size
    """
    for size in range(80, 20, -5):
        font = get_font(size)
        if font is None:
            continue
            
        lines = wrap_text(text, font, max_width, draw)
        
        # Calculate total height
        total_height = 0
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            total_height += bbox[3] - bbox[1] + 5  # 5px line spacing
        
        if total_height <= max_height:
            return size
    
    return 25  # Minimum size


def create_meme(image: Image.Image, top_text: str, bottom_text: str) -> Image.Image:
    """
    Create a meme by adding top and bottom text to an image.
    
    Args:
        image: PIL Image object (the background)
        top_text: Text for the top of the meme
        bottom_text: Text for the bottom of the meme
    
    Returns:
        PIL Image with meme text added
    """
    # Ensure image is in RGB mode
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    # Resize image to a standard meme size if needed
    target_size = (800, 800)
    image = image.resize(target_size, Image.Resampling.LANCZOS)
    
    # Create a copy to draw on
    meme = image.copy()
    draw = ImageDraw.Draw(meme)
    
    width, height = meme.size
    padding = 20
    max_text_width = width - (padding * 2)
    max_text_height = height // 4  # Each text area gets 1/4 of image height
    
    # Calculate optimal font sizes
    top_font_size = calculate_font_size(top_text, max_text_width, max_text_height, draw)
    bottom_font_size = calculate_font_size(bottom_text, max_text_width, max_text_height, draw)
    
    # Use the smaller size for consistency
    font_size = min(top_font_size, bottom_font_size)
    font = get_font(font_size)
    
    if font is None:
        # Ultimate fallback
        font = ImageFont.load_default()
    
    # Draw top text
    if top_text:
        top_lines = wrap_text(top_text.upper(), font, max_text_width, draw)
        y_position = padding
        
        for line in top_lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            x_position = (width - text_width) // 2
            
            draw_text_with_outline(draw, (x_position, y_position), line, font)
            y_position += text_height + 5
    
    # Draw bottom text
    if bottom_text:
        bottom_lines = wrap_text(bottom_text.upper(), font, max_text_width, draw)
        
        # Calculate starting y position for bottom text
        total_text_height = 0
        for line in bottom_lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            total_text_height += bbox[3] - bbox[1] + 5
        
        y_position = height - total_text_height - padding
        
        for line in bottom_lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            x_position = (width - text_width) // 2
            
            draw_text_with_outline(draw, (x_position, y_position), line, font)
            y_position += text_height + 5
    
    return meme


def image_to_bytes(image: Image.Image, format: str = "PNG") -> bytes:
    """
    Convert a PIL Image to bytes.
    
    Args:
        image: PIL Image object
        format: Image format (PNG, JPEG, etc.)
    
    Returns:
        Image as bytes
    """
    buffer = BytesIO()
    image.save(buffer, format=format)
    buffer.seek(0)
    return buffer.getvalue()
