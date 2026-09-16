from django import template

register = template.Library()

CATEGORY_ICONS = {
    "phone": "📱",
    "laptop": "💻",
    "tablet": "📟",
    "headphone": "🎧",
    "smartwatch": "⌚",
    "gaming": "🎮",
    "camera": "📷",
    "tv": "🖥️",
    "pc_part": "🧩",
    "other": "✨",
}


@register.filter
def tl(value):
    if value is None:
        return ""
    formatted = f"{value:,.2f}"
    formatted = formatted.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"₺{formatted}"


@register.filter
def percent(value):
    if value is None:
        return "Henüz oy yok"
    return f"%{value:.0f}"


@register.filter
def category_icon(category):
    return CATEGORY_ICONS.get(category, "✨")
