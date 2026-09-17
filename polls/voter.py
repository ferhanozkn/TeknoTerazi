import uuid

from django.conf import settings

COOKIE_NAME = "tt_voter"
COOKIE_SALT = "tt-voter"
COOKIE_MAX_AGE = 60 * 60 * 24 * 365  # 365 gün


def read_anon_id(request):
    """İstekteki imzalı anon_id çerezini, oturum durumundan bağımsız okur."""
    raw = request.get_signed_cookie(COOKIE_NAME, salt=COOKIE_SALT, default=None)
    if raw:
        try:
            return uuid.UUID(raw)
        except ValueError:
            pass
    return None


def get_voter(request):
    """(user, anon_id, is_new_anon) döndürür. Üye ise anon_id None'dır."""
    if request.user.is_authenticated:
        return request.user, None, False

    anon_id = read_anon_id(request)
    if anon_id is not None:
        return None, anon_id, False

    return None, uuid.uuid4(), True


def attach_voter_cookie(response, anon_id):
    response.set_signed_cookie(
        COOKIE_NAME,
        str(anon_id),
        salt=COOKIE_SALT,
        max_age=COOKIE_MAX_AGE,
        httponly=True,
        samesite="Lax",
        secure=not settings.DEBUG,
    )
