import uuid

import requests
from django.conf import settings

UPLOAD_TIMEOUT = 15


class ImageUploadError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(message)


def upload_product_image(uploaded_file):
    """Verilen dosyayı Supabase Storage'a yükler, herkese açık URL'ini döndürür."""
    if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_ROLE_KEY:
        raise ImageUploadError(
            "Görsel yükleme şu anda yapılandırılmamış. Bunun yerine \"Görsel linki\" alanını kullanabilirsin."
        )

    extension = uploaded_file.name.rsplit(".", 1)[-1].lower()
    object_path = f"{uuid.uuid4().hex}.{extension}"
    upload_url = (
        f"{settings.SUPABASE_URL}/storage/v1/object/"
        f"{settings.SUPABASE_STORAGE_BUCKET}/{object_path}"
    )

    try:
        response = requests.post(
            upload_url,
            headers={
                "Authorization": f"Bearer {settings.SUPABASE_SERVICE_ROLE_KEY}",
                "apikey": settings.SUPABASE_SERVICE_ROLE_KEY,
                "Content-Type": uploaded_file.content_type or "application/octet-stream",
            },
            data=uploaded_file.read(),
            timeout=UPLOAD_TIMEOUT,
        )
    except requests.RequestException:
        raise ImageUploadError("Görsel yüklenemedi, lütfen tekrar dene.")

    if not response.ok:
        raise ImageUploadError("Görsel yüklenemedi, lütfen tekrar dene.")

    return (
        f"{settings.SUPABASE_URL}/storage/v1/object/public/"
        f"{settings.SUPABASE_STORAGE_BUCKET}/{object_path}"
    )
