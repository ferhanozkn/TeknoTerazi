import requests
from django.conf import settings

VERIFY_URL = "https://challenges.cloudflare.com/turnstile/v0/siteverify"


def verify_turnstile_token(token):
    """Cloudflare Turnstile token'ını doğrular.

    TURNSTILE_SECRET_KEY tanımlı değilse (yerel geliştirme) hep True döner —
    widget zaten şablonda gösterilmiyor.
    """
    if not settings.TURNSTILE_SECRET_KEY:
        return True
    if not token:
        return False
    try:
        response = requests.post(
            VERIFY_URL,
            data={"secret": settings.TURNSTILE_SECRET_KEY, "response": token},
            timeout=5,
        )
        response.raise_for_status()
        return bool(response.json().get("success"))
    except requests.RequestException:
        return False
