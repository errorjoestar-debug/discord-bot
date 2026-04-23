import aiohttp
import io
import logging

log = logging.getLogger("muslim_bot")

# Try to import Pillow - optional dependency
try:
    from PIL import Image, ImageDraw, ImageFont
    HAS_PILLOW = True
except ImportError:
    HAS_PILLOW = False

# Dark theme colors
COLORS = {
    "bg": "#1a1a2e",
    "border": "#16213e",
    "title": "#e94560",
    "text": "#ffffff",
    "footer": "#0f3460",
    "accent": "#533483",
}


async def create_text_image(title: str, text: str, footer: str = "MuslimBot", color: str = "#e94560") -> bytes | None:
    """Create a dark-themed image for any Arabic text (azkar, dua, hadith, ayah).
    Uses Pillow if available, otherwise falls back to external API."""
    if HAS_PILLOW:
        return _create_image_pillow(title, text, footer, color)
    else:
        return await _create_image_api(title, text, footer, color)


def _create_image_pillow(title: str, text: str, footer: str, color: str) -> bytes | None:
    """Create image locally using Pillow."""
    try:
        width = 800
        line_height = 40
        padding = 50
        
        # Try to load Arabic font
        from pathlib import Path
        font_dir = Path(__file__).parent.parent / "data" / "fonts"
        font_path = font_dir / "arabic.ttf"
        
        try:
            font = ImageFont.truetype(str(font_path), 28)
            title_font = ImageFont.truetype(str(font_path), 32)
            footer_font = ImageFont.truetype(str(font_path), 20)
        except:
            font = ImageFont.load_default()
            title_font = ImageFont.load_default()
            footer_font = ImageFont.load_default()
        
        # Calculate height based on text
        dummy_img = Image.new('RGB', (width, 100), COLORS["bg"])
        draw = ImageDraw.Draw(dummy_img)
        
        # Wrap text
        wrapped_lines = []
        max_line_width = width - (padding * 2)
        for line in text.split('\n'):
            words = line.split()
            current_line = ""
            for word in words:
                test_line = current_line + " " + word if current_line else word
                bbox = draw.textbbox((0, 0), test_line, font=font)
                if bbox[2] - bbox[0] <= max_line_width:
                    current_line = test_line
                else:
                    if current_line:
                        wrapped_lines.append(current_line)
                    current_line = word
            if current_line:
                wrapped_lines.append(current_line)
        
        # Calculate total height
        text_height = len(wrapped_lines) * line_height
        height = max(300, text_height + 200)
        
        # Create image
        img = Image.new('RGB', (width, height), COLORS["bg"])
        draw = ImageDraw.Draw(img)
        
        # Border
        draw.rectangle([8, 8, width-8, height-8], outline=COLORS["border"], width=2)
        
        # Top accent line
        draw.rectangle([0, 0, width, 4], fill=color)
        
        # Title
        title_bbox = draw.textbbox((0, 0), title, font=title_font)
        title_x = (width - (title_bbox[2] - title_bbox[0])) // 2
        draw.text((title_x, 25), title, fill=color, font=title_font)
        
        # Separator line
        draw.line([(padding, 70), (width - padding, 70)], fill=COLORS["border"], width=1)
        
        # Text
        y = 90
        for line in wrapped_lines:
            draw.text((padding, y), line, fill=COLORS["text"], font=font)
            y += line_height
        
        # Footer
        footer_bbox = draw.textbbox((0, 0), footer, font=footer_font)
        footer_x = (width - (footer_bbox[2] - footer_bbox[0])) // 2
        draw.text((footer_x, height - 45), footer, fill=COLORS["footer"], font=footer_font)
        
        # Bottom accent line
        draw.rectangle([0, height-4, width, height], fill=color)
        
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='PNG')
        img_bytes.seek(0)
        return img_bytes.getvalue()
    except Exception as e:
        log.error(f"Pillow image generation failed: {e}")
        return None


async def _create_image_api(title: str, text: str, footer: str, color: str) -> bytes | None:
    """Try to create image using external API services."""
    # Try multiple free image generation services
    services = [
        _try_quickchart,
    ]
    
    for service in services:
        try:
            result = await service(title, text, footer, color)
            if result:
                return result
        except Exception as e:
            log.debug(f"Image service {service.__name__} failed: {e}")
            continue
    
    return None


async def _try_quickchart(title: str, text: str, footer: str, color: str) -> bytes | None:
    """Use QuickChart API to generate a styled text image."""
    try:
        import urllib.parse
        # Build a simple chart with text overlay
        encoded_text = urllib.parse.quote(text[:500])  # Limit text length
        encoded_title = urllib.parse.quote(title)
        
        url = f"https://quickchart.io/chart?c={{type:'bar',data:{labels:['1'],datasets:[{data:[0]}]}},options:{title:{{display:true,text:'{encoded_title}'}},plugins:{datalabels:{{display:false}}}}}}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=10) as response:
                if response.status == 200:
                    return await response.read()
        return None
    except:
        return None


async def create_ayah_image(text: str, surah_name: str, ayah_number: int, surah_number: int) -> bytes | None:
    """Create image for a Quran ayah."""
    title = f"سورة {surah_name} - آية {ayah_number}"
    footer = "﴿ إِنَّ هَٰذَا الْقُرْآنَ يَهْدِي لِلَّتِي هِيَ أَقْوَمُ ﴾ • MuslimBot"
    return await create_text_image(title, text, footer, "#0984E3")


async def create_azkar_image(title: str, azkar_list: list[dict], footer: str = "MuslimBot", color: str = "#FF8C00") -> list[bytes]:
    """Create images for azkar list. Returns list of image bytes (one per page)."""
    images = []
    
    # Split azkar into pages of 5 items each
    page_size = 5
    pages = [azkar_list[i:i+page_size] for i in range(0, len(azkar_list), page_size)]
    
    for page_num, page in enumerate(pages, 1):
        lines = []
        for i, z in enumerate(page, 1):
            count_str = f" (×{z['count']})" if z.get('count', 1) > 1 else ""
            source_str = f" [{z['source']}]" if z.get('source') else ""
            lines.append(f"{i}. {z['text']}{count_str}{source_str}")
        
        text = "\n".join(lines)
        page_footer = footer
        if len(pages) > 1:
            page_footer = f"الجزء {page_num} من {len(pages)} ─ {footer}"
        
        img = await create_text_image(title, text, page_footer, color)
        if img:
            images.append(img)
    
    return images


async def create_hadith_image(text: str, narrator: str, source: str) -> bytes | None:
    """Create image for a hadith."""
    title = "📖 حديث شريف"
    full_text = f"{text}\n\nالراوي: {narrator}\nالمصدر: {source}"
    footer = "﴿ مَّن يُطِعِ ٱلرَّسُولَ فَقَدْ أَطَاعَ ٱللَّهَ ﴾ • MuslimBot"
    return await create_text_image(title, full_text, footer, "#8E44AD")


async def create_dua_image(text: str, source: str) -> bytes | None:
    """Create image for a dua."""
    title = "🤲 دعاء"
    full_text = f"{text}\n\nالمصدر: {source}"
    footer = "﴿ ادْعُونِي أَسْتَجِبْ لَكُمْ ﴾ • MuslimBot"
    return await create_text_image(title, full_text, footer, "#1ABC9C")
