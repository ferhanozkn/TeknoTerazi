import os
from io import BytesIO

from PIL import Image, ImageDraw, ImageFont

WIDTH, HEIGHT = 1200, 630
BG_COLOR = (15, 16, 36)
ACCENT_COLOR = (30, 20, 80)
TEXT_COLOR = (241, 242, 250)
MUTED_COLOR = (163, 168, 201)
BRAND_COLOR = (140, 110, 255)
MARGIN = 80

FONT_DIR = os.path.join(os.path.dirname(__file__), "fonts")


def _font(name, size, variation=None):
    font = ImageFont.truetype(os.path.join(FONT_DIR, name), size)
    if variation:
        try:
            font.set_variation_by_name(variation)
        except OSError:
            pass
    return font


def _wrap_and_truncate(draw, text, font, max_width, max_lines):
    words = text.split()
    lines = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        width = draw.textbbox((0, 0), candidate, font=font)[2]
        if width > max_width and current:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)

    if len(lines) <= max_lines:
        return lines

    lines = lines[:max_lines]
    last = lines[-1]
    while last and draw.textbbox((0, 0), last + "…", font=font)[2] > max_width:
        last = last[:-1].rstrip()
    lines[-1] = last + "…"
    return lines


def render_poll_og_image(poll, products):
    """Anket linki paylaşıldığında sosyal medya önizlemesinde görünen görsel."""
    image = Image.new("RGB", (WIDTH, HEIGHT), color=BG_COLOR)
    draw = ImageDraw.Draw(image)
    draw.ellipse([-120, -120, 320, 320], fill=ACCENT_COLOR)

    title_font = _font("SpaceGrotesk.ttf", 60, "Bold")
    sub_font = _font("Inter.ttf", 34, "Regular")
    meta_font = _font("Inter.ttf", 28, "Medium")
    brand_font = _font("SpaceGrotesk.ttf", 30, "Bold")

    max_width = WIDTH - MARGIN * 2
    lines = _wrap_and_truncate(draw, poll.title, title_font, max_width, 3)
    y = 190
    for line in lines:
        draw.text((MARGIN, y), line, font=title_font, fill=TEXT_COLOR)
        y += 74

    product_names = " vs ".join(product.name for product in products[:3])
    if product_names:
        product_line = _wrap_and_truncate(draw, product_names, sub_font, max_width, 1)[0]
        draw.text((MARGIN, y + 24), product_line, font=sub_font, fill=MUTED_COLOR)

    total_votes = sum(product.total_votes for product in products)
    meta_text = f"{len(products)} ürün · {total_votes} oy"
    draw.text((MARGIN, HEIGHT - 160), meta_text, font=meta_font, fill=MUTED_COLOR)
    draw.text((MARGIN, HEIGHT - 100), "TeknoTerazi", font=brand_font, fill=BRAND_COLOR)

    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()
