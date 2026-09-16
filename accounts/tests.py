from django.core.exceptions import ValidationError
from django.test import TestCase

from accounts.models import CustomUser


class CustomUserTests(TestCase):
    def test_email_is_stored_lowercase(self):
        user = CustomUser.objects.create_user(
            username="ahmet", email="Ahmet@Example.COM", password="x"
        )
        self.assertEqual(user.email, "ahmet@example.com")

    def test_invalid_username_is_rejected(self):
        user = CustomUser(username="a b!", email="a@example.com")
        with self.assertRaises(ValidationError):
            user.full_clean()
