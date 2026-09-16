from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from polls.models import Poll

User = get_user_model()


def product_fields(index, **overrides):
    data = {
        f"products-{index}-id": "",
        f"products-{index}-name": f"Ürün {index}",
        f"products-{index}-price": "1000",
        f"products-{index}-features": "Özellik A",
        f"products-{index}-product_url": "",
        f"products-{index}-image_url": "",
    }
    for key, value in overrides.items():
        data[f"products-{index}-{key}"] = value
    return data


def build_post_data(product_count, poll_overrides=None, product_overrides=None):
    data = {
        "title": "Hangi telefonu almalıyım?",
        "category": "phone",
        "description": "",
        "products-TOTAL_FORMS": str(product_count),
        "products-INITIAL_FORMS": "0",
        "products-MIN_NUM_FORMS": "0",
        "products-MAX_NUM_FORMS": "1000",
    }
    data.update(poll_overrides or {})
    product_overrides = product_overrides or {}
    for i in range(product_count):
        data.update(product_fields(i, **product_overrides.get(i, {})))
    return data


class PollCreateViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="ahmet", email="ahmet@example.com", password="x")
        self.client.force_login(self.user)

    def test_guest_is_redirected_to_login(self):
        self.client.logout()
        create_url = reverse("polls:poll_create")
        response = self.client.get(create_url)
        self.assertRedirects(response, f"{reverse('accounts:login')}?next={create_url}")

    def test_one_product_is_rejected(self):
        response = self.client.post(reverse("polls:poll_create"), build_post_data(1))
        self.assertContains(response, "Bir ankete en az 2 ürün eklemelisin.")
        self.assertEqual(Poll.objects.count(), 0)

    def test_six_products_is_rejected(self):
        response = self.client.post(reverse("polls:poll_create"), build_post_data(6))
        self.assertContains(response, "Bir ankete en fazla 5 ürün ekleyebilirsin.")
        self.assertEqual(Poll.objects.count(), 0)

    def test_product_without_price_is_rejected(self):
        data = build_post_data(2, product_overrides={0: {"price": ""}})
        response = self.client.post(reverse("polls:poll_create"), data)
        self.assertContains(response, "Geçerli bir fiyat gir.")
        self.assertEqual(Poll.objects.count(), 0)

    def test_product_without_features_is_rejected(self):
        data = build_post_data(2, product_overrides={0: {"features": ""}})
        response = self.client.post(reverse("polls:poll_create"), data)
        self.assertContains(response, "Ürünün en az bir özelliğini yazmalısın.")
        self.assertEqual(Poll.objects.count(), 0)

    def test_duplicate_product_name_is_rejected(self):
        data = build_post_data(2, product_overrides={1: {"name": "Ürün 0"}})
        response = self.client.post(reverse("polls:poll_create"), data)
        self.assertContains(response, "Aynı ürünü iki kez ekleyemezsin.")
        self.assertEqual(Poll.objects.count(), 0)

    def test_two_products_succeeds(self):
        response = self.client.post(reverse("polls:poll_create"), build_post_data(2))
        poll = Poll.objects.get()
        self.assertRedirects(response, reverse("polls:poll_detail", kwargs={"pk": poll.pk}))
        self.assertEqual(poll.author, self.user)
        self.assertEqual(list(poll.products.order_by("position").values_list("position", flat=True)), [0, 1])

    def test_five_products_succeeds(self):
        self.client.post(reverse("polls:poll_create"), build_post_data(5))
        poll = Poll.objects.get()
        self.assertEqual(poll.products.count(), 5)

    def test_invalid_submission_preserves_entered_data(self):
        data = build_post_data(1, poll_overrides={"title": "Kaybolmamalı başlık"})
        response = self.client.post(reverse("polls:poll_create"), data)
        self.assertContains(response, "Kaybolmamalı başlık")
