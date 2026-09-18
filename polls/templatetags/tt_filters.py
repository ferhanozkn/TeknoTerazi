from django import template
from django.utils.translation import gettext as _

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

USAGE_PURPOSE_ICONS = {
    "gaming": "🎮",
    "school": "📚",
    "work": "💼",
    "daily": "☀️",
    "other": "✨",
}

BUDGET_TIER_ICONS = {
    "economic": "💵",
    "mid": "💰",
    "premium": "💎",
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
        return _("Henüz oy yok")
    return f"%{value:.0f}"


@register.filter
def category_icon(category):
    return CATEGORY_ICONS.get(category, "✨")


@register.filter
def usage_purpose_icon(usage_purpose):
    return USAGE_PURPOSE_ICONS.get(usage_purpose, "")


@register.filter
def budget_tier_icon(budget_tier):
    return BUDGET_TIER_ICONS.get(budget_tier, "")


@register.filter
def dict_get(mapping, key):
    return mapping.get(key, "")


@register.filter
def conversion_rate(poll):
    if not poll.view_count:
        return None
    return round(poll.total_votes / poll.view_count * 100)
