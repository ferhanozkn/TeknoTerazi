import uuid
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from polls.models import Poll, Product, Vote, VoteValue

User = get_user_model()


def make_poll_with_products(author, product_count=2, **overrides):
    poll = Poll.objects.create(author=author, title="Hangi telefonu almalıyım?", category="phone", **overrides)
    products = []
    for i in range(product_count):
        products.append(
            Product.objects.create(
                poll=poll, name=f"Ürün {i}", price=100 * (i + 1), features="Özellik", position=i
            )
        )
    return poll, products


def build_edit_data(poll, products, poll_overrides=None, product_overrides=None):
    data = {"title": poll.title, "category": poll.category, "description": poll.description}
    data.update(poll_overrides or {})
    product_overrides = product_overrides or {}
    for product in products:
        prefix = f"products-{product.pk}"
        entry = {
            "name": product.name,
            "price": str(product.price),
            "features": product.features,
            "product_url": product.product_url,
            "image_url": product.image_url,
        }
        entry.update(product_overrides.get(product.pk, {}))
        for key, value in entry.items():
            data[f"{prefix}-{key}"] = value
    return data


class PollEditViewTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(username="ahmet", email="ahmet@example.com", password="x")
        self.poll, self.products = make_poll_with_products(self.author)
        self.edit_url = reverse("polls:poll_edit", kwargs={"pk": self.poll.pk})

    def test_guest_is_redirected_to_login(self):
        response = self.client.get(self.edit_url)
        self.assertRedirects(response, f"{reverse('accounts:login')}?next={self.edit_url}")

    def test_non_owner_gets_404(self):
        other = User.objects.create_user(username="ece", email="ece@example.com", password="x")
        self.client.force_login(other)
        response = self.client.get(self.edit_url)
        self.assertEqual(response.status_code, 404)

    def test_owner_sees_prefilled_form(self):
        self.client.force_login(self.author)
        response = self.client.get(self.edit_url)
        self.assertContains(response, self.poll.title)
        self.assertContains(response, self.products[0].name)

    def test_poll_with_votes_cannot_be_edited(self):
        Vote.objects.create(product=self.products[0], anon_id=uuid.uuid4(), value=VoteValue.WORTH)
        self.client.force_login(self.author)

        response = self.client.get(self.edit_url)

        self.assertRedirects(response, reverse("polls:poll_detail", kwargs={"pk": self.poll.pk}))
        self.assertEqual(Poll.objects.get(pk=self.poll.pk).title, self.poll.title)

    def test_owner_can_update_title_and_product_price(self):
        self.client.force_login(self.author)
        data = build_edit_data(
            self.poll,
            self.products,
            poll_overrides={"title": "Güncellenmiş başlık"},
            product_overrides={self.products[0].pk: {"price": "999"}},
        )

        response = self.client.post(self.edit_url, data)

        self.assertRedirects(response, reverse("polls:poll_detail", kwargs={"pk": self.poll.pk}))
        self.poll.refresh_from_db()
        self.assertEqual(self.poll.title, "Güncellenmiş başlık")
        self.products[0].refresh_from_db()
        self.assertEqual(str(self.products[0].price), "999.00")

    def test_duplicate_product_names_are_rejected(self):
        self.client.force_login(self.author)
        data = build_edit_data(
            self.poll,
            self.products,
            product_overrides={self.products[1].pk: {"name": self.products[0].name}},
        )

        self.client.post(self.edit_url, data)

        self.products[1].refresh_from_db()
        self.assertNotEqual(self.products[1].name, self.products[0].name)

    @patch("polls.views.upload_product_image")
    def test_uploaded_image_updates_product(self, mock_upload):
        mock_upload.return_value = "https://example.supabase.co/x.jpg"
        self.client.force_login(self.author)
        data = build_edit_data(self.poll, self.products)
        data[f"products-{self.products[0].pk}-image"] = SimpleUploadedFile(
            "a.jpg", b"x", content_type="image/jpeg"
        )

        response = self.client.post(self.edit_url, data)

        self.assertEqual(response.status_code, 302)
        self.products[0].refresh_from_db()
        self.assertEqual(self.products[0].image_url, "https://example.supabase.co/x.jpg")


class PollDetailEditLinkTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(username="ahmet", email="ahmet@example.com", password="x")
        self.poll, self.products = make_poll_with_products(self.author)

    def test_edit_link_shown_when_no_votes(self):
        self.client.force_login(self.author)
        response = self.client.get(reverse("polls:poll_detail", kwargs={"pk": self.poll.pk}))
        self.assertContains(response, reverse("polls:poll_edit", kwargs={"pk": self.poll.pk}))

    def test_edit_link_hidden_once_voted(self):
        Vote.objects.create(product=self.products[0], anon_id=uuid.uuid4(), value=VoteValue.WORTH)
        self.client.force_login(self.author)
        response = self.client.get(reverse("polls:poll_detail", kwargs={"pk": self.poll.pk}))
        self.assertNotContains(response, reverse("polls:poll_edit", kwargs={"pk": self.poll.pk}))
