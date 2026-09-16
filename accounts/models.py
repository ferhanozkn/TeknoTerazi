from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

username_validator = RegexValidator(
    regex=r"^[a-zA-Z0-9_]{3,30}$",
    message="Kullanıcı adı 3–30 karakter olmalı ve yalnızca harf, rakam ve alt çizgi içermelidir.",
)


class CustomUser(AbstractUser):
    first_name = None
    last_name = None

    username = models.CharField(
        "kullanıcı adı", max_length=30, unique=True, validators=[username_validator]
    )
    email = models.EmailField("e-posta", unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    def save(self, *args, **kwargs):
        self.email = self.email.lower()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.username
