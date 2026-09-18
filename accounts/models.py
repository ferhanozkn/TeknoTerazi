from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

username_validator = RegexValidator(
    regex=r"^[a-zA-Z0-9_]{3,30}$",
    message=_("Kullanıcı adı 3–30 karakter olmalı ve yalnızca harf, rakam ve alt çizgi içermelidir."),
)


class CustomUser(AbstractUser):
    first_name = None
    last_name = None

    username = models.CharField(
        _("kullanıcı adı"), max_length=30, unique=True, validators=[username_validator]
    )
    email = models.EmailField(_("e-posta"), unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def save(self, *args, **kwargs):
        self.email = self.email.lower()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username
