from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from polls.forms import ProductForm
from polls.models import Poll, Product
from polls.storage import ImageUploadError
from polls.tests.test_views import build_post_data

User = get_user_model()


def make_image_file(name="foto.jpg", content_type="image/jpeg", size=100):
    return SimpleUploadedFile(name, b"x" * size, content_type=content_type)


class ProductFormImageValidationTests(TestCase):
    def base_data(self):
        return {
            "name": "Telefon A",
            "price": "1000",
            "features": "Özellik A",
            "product_url": "",
            "image_url": "",
        }

    def test_no_image_is_valid(self):
        form = ProductForm(data=self.base_data(), files={})
        self.assertTrue(form.is_valid())

    def test_valid_jpeg_is_accepted(self):
        form = ProductForm(data=self.base_data(), files={"image": make_image_file()})
        self.assertTrue(form.is_valid())

    def test_invalid_content_type_is_rejected(self):
        file = make_image_file(name="dosya.txt", content_type="text/plain")
        form = ProductForm(data=self.base_data(), files={"image": file})
        self.assertFalse(form.is_valid())
        self.assertIn("image", form.errors)

    def test_oversized_image_is_rejected(self):
        file = make_image_file(size=5 * 1024 * 1024 + 1)
        form = ProductForm(data=self.base_data(), files={"image": file})
        self.assertFalse(form.is_valid())
        self.assertIn("image", form.errors)


class PollCreateImageUploadViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="ahmet", email="ahmet@example.com", password="x")
        self.client.force_login(self.user)

    @patch("polls.views.upload_product_image")
    def test_uploaded_image_is_stored_as_product_image_url(self, mock_upload):
        mock_upload.return_value = "https://example.supabase.co/storage/v1/object/public/product-images/x.jpg"
        data = build_post_data(2, product_overrides={0: {"image": make_image_file()}})

        self.client.post(reverse("polls:poll_create"), data)

        product = Product.objects.get(position=0)
        self.assertEqual(product.image_url, "https://example.supabase.co/storage/v1/object/public/product-images/x.jpg")
        mock_upload.assert_called_once()

    @patch("polls.views.upload_product_image")
    def test_uploaded_image_takes_priority_over_url_field(self, mock_upload):
        mock_upload.return_value = "https://example.supabase.co/storage/v1/object/public/product-images/x.jpg"
        data = build_post_data(
            2,
            product_overrides={0: {"image": make_image_file(), "image_url": "https://harici.com/foto.jpg"}},
        )

        self.client.post(reverse("polls:poll_create"), data)

        product = Product.objects.get(position=0)
        self.assertEqual(product.image_url, "https://example.supabase.co/storage/v1/object/public/product-images/x.jpg")

    @patch("polls.views.upload_product_image")
    def test_upload_failure_blocks_poll_creation_and_shows_error(self, mock_upload):
        mock_upload.side_effect = ImageUploadError("Görsel yüklenemedi, lütfen tekrar dene.")
        data = build_post_data(2, product_overrides={0: {"image": make_image_file()}})

        response = self.client.post(reverse("polls:poll_create"), data)

        self.assertEqual(Poll.objects.count(), 0)
        self.assertContains(response, "Görsel yüklenemedi, lütfen tekrar dene.")

    @override_settings(SUPABASE_URL="", SUPABASE_SERVICE_ROLE_KEY="")
    def test_no_supabase_config_gives_turkish_error(self):
        data = build_post_data(2, product_overrides={0: {"image": make_image_file()}})

        response = self.client.post(reverse("polls:poll_create"), data)

        self.assertEqual(Poll.objects.count(), 0)
        self.assertContains(response, "Görsel yükleme şu anda yapılandırılmamış")

    def test_poll_without_any_image_still_works(self):
        data = build_post_data(2)
        response = self.client.post(reverse("polls:poll_create"), data)
        self.assertEqual(Poll.objects.count(), 1)
        self.assertRedirects(response, reverse("polls:poll_detail", kwargs={"pk": Poll.objects.get().pk}))
