from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from polls.models import Poll, Product

User = get_user_model()


def make_poll_with_products(author, title="Hangi telefonu almalıyım?", product_count=2, **overrides):
    poll = Poll.objects.create(author=author, title=title, category="phone", **overrides)
    for i in range(product_count):
        Product.objects.create(
            poll=poll, name=f"Ürün {i}", price=100 * (i + 1), features="Özellik", position=i
        )
    return poll


class PollOgImageViewTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(username="ahmet", email="ahmet@example.com", password="x")

    def test_returns_png_image(self):
        poll = make_poll_with_products(self.author)
        response = self.client.get(reverse("polls:poll_og_image", kwargs={"pk": poll.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "image/png")
        self.assertEqual(response.content[:8], b"\x89PNG\r\n\x1a\n")

    def test_nonexistent_poll_returns_404(self):
        response = self.client.get(reverse("polls:poll_og_image", kwargs={"pk": 9999}))
        self.assertEqual(response.status_code, 404)

    def test_works_with_very_long_title(self):
        long_title = ("Bu gerçekten uzun bir başlık mı yoksa değil mi çok emin " * 2)[:120].strip()
        poll = make_poll_with_products(self.author, title=long_title)
        response = self.client.get(reverse("polls:poll_og_image", kwargs={"pk": poll.pk}))
        self.assertEqual(response.status_code, 200)

    def test_works_with_no_products(self):
        poll = make_poll_with_products(self.author, product_count=0)
        response = self.client.get(reverse("polls:poll_og_image", kwargs={"pk": poll.pk}))
        self.assertEqual(response.status_code, 200)


class PollDetailOgTagsTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(username="ahmet", email="ahmet@example.com", password="x")

    def test_og_title_and_image_present(self):
        poll = make_poll_with_products(self.author, title="Hangi telefonu almalıyım?")
        response = self.client.get(reverse("polls:poll_detail", kwargs={"pk": poll.pk}))
        self.assertContains(response, 'property="og:title" content="Hangi telefonu almalıyım? · TeknoTerazi"')
        self.assertContains(response, "og-goruntu.png")
        self.assertContains(response, 'property="og:image:width" content="1200"')
