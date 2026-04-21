from PIL import Image, ImageDraw, ImageFont
import io
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
FONT_PATH = DATA_DIR / "fonts" / "arabic.ttf"


def create_ayah_image(text: str, surah_name: str, ayah_number: int) -> bytes:
    """Create a dark-themed image for an ayah."""
    # Image dimensions
    width = 800
    height = 400
    
    # Create image with dark background
    img = Image.new('RGB', (width, height), color='#1a1a2e')
    draw = ImageDraw.Draw(img)
    
    # Try to load Arabic font, fallback to default
    try:
        font = ImageFont.truetype(str(FONT_PATH), 32)
        title_font = ImageFont.truetype(str(FONT_PATH), 24)
    except:
        font = ImageFont.load_default()
        title_font = ImageFont.load_default()
    
    # Add decorative border
    border_color = '#16213e'
    draw.rectangle([10, 10, width-10, height-10], outline=border_color, width=3)
    
    # Add title (surah name)
    title_text = f"سورة {surah_name} - آية {ayah_number}"
    title_bbox = draw.textbbox((0, 0), title_text, font=title_font)
    title_width = title_bbox[2] - title_bbox[0]
    title_x = (width - title_width) // 2
    draw.text((title_x, 30), title_text, fill='#e94560', font=title_font)
    
    # Add ayah text (wrapped)
    y_position = 100
    line_height = 45
    max_line_width = width - 100
    
    # Simple text wrapping
    words = text.split()
    current_line = ""
    
    for word in words:
        test_line = current_line + " " + word if current_line else word
        bbox = draw.textbbox((0, 0), test_line, font=font)
        line_width = bbox[2] - bbox[0]
        
        if line_width <= max_line_width:
            current_line = test_line
        else:
            if current_line:
                draw.text((50, y_position), current_line, fill='#ffffff', font=font)
                y_position += line_height
            current_line = word
    
    if current_line:
        draw.text((50, y_position), current_line, fill='#ffffff', font=font)
    
    # Add footer
    footer_text = "﴿ إِنَّ هَٰذَا الْقُرْآنَ يَهْدِي لِلَّتِي هِيَ أَقْوَمُ ﴾"
    footer_bbox = draw.textbbox((0, 0), footer_text, font=title_font)
    footer_width = footer_bbox[2] - footer_bbox[0]
    footer_x = (width - footer_width) // 2
    draw.text((footer_x, height - 50), footer_text, fill='#0f3460', font=title_font)
    
    # Save to bytes
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    
    return img_bytes.getvalue()
