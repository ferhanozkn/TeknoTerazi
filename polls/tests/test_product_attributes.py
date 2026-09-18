from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from polls.forms import ProductForm
from polls.models import Poll, Product
from polls.tests.test_views import build_post_data

User = get_user_model()


class ProductAttributesDictTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(username="ahmet", email="ahmet@example.com", password="x")
        self.poll = Poll.objects.create(author=self.author, title="Hangi telefonu almalıyım?", category="phone")

    def test_blank_attributes_gives_empty_dict(self):
        product = Product.objects.create(poll=self.poll, name="A", price=100, features="x", position=0)
        self.assertEqual(product.attributes_dict, {})

    def test_parses_key_value_lines(self):
        product = Product.objects.create(
            poll=self.poll,
            name="A",
            price=100,
            features="x",
            position=0,
            attributes="RAM: 8 GB\nDepolama: 128 GB",
        )
        self.assertEqual(product.attributes_dict, {"RAM": "8 GB", "Depolama": "128 GB"})

    def test_lines_without_colon_are_ignored(self):
        product = Product.objects.create(
            poll=self.poll, name="A", price=100, features="x", position=0, attributes="RAM 8 GB\nEkran: 6.1 inç"
        )
        self.assertEqual(product.attributes_dict, {"Ekran": "6.1 inç"})


class ProductFormAttributesValidationTests(TestCase):
    def base_data(self):
        return {
            "name": "Telefon A",
            "price": "1000",
            "features": "Özellik A",
            "product_url": "",
            "image_url": "",
        }

    def test_blank_attributes_is_valid(self):
        form = ProductForm(data={**self.base_data(), "attributes": ""})
        self.assertTrue(form.is_valid())

    def test_valid_lines_are_normalized(self):
        form = ProductForm(data={**self.base_data(), "attributes": "RAM :  8 GB \nDepolama:128 GB"})
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data["attributes"], "RAM: 8 GB\nDepolama: 128 GB")

    def test_line_without_colon_is_rejected(self):
        form = ProductForm(data={**self.base_data(), "attributes": "8 GB RAM"})
        self.assertFalse(form.is_valid())
        self.assertIn("attributes", form.errors)

    def test_too_many_lines_rejected(self):
        lines = "\n".join(f"Özellik{i}: Değer{i}" for i in range(9))
        form = ProductForm(data={**self.base_data(), "attributes": lines})
        self.assertFalse(form.is_valid())
        self.assertIn("attributes", form.errors)

    def test_key_too_long_is_rejected(self):
        form = ProductForm(data={**self.base_data(), "attributes": f"{'a' * 41}: değer"})
        self.assertFalse(form.is_valid())
        self.assertIn("attributes", form.errors)

    def test_value_too_long_is_rejected(self):
        form = ProductForm(data={**self.base_data(), "attributes": f"RAM: {'a' * 81}"})
        self.assertFalse(form.is_valid())
        self.assertIn("attributes", form.errors)


class ComparisonTableViewTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(username="ahmet", email="ahmet@example.com", password="x")

    def test_table_hidden_when_no_attributes_set(self):
        poll = Poll.objects.create(author=self.author, title="Hangi telefonu almalıyım?", category="phone")
        Product.objects.create(poll=poll, name="A", price=100, features="x", position=0)
        Product.objects.create(poll=poll, name="B", price=200, features="x", position=1)

        response = self.client.get(reverse("polls:poll_detail", kwargs={"pk": poll.pk}))

        self.assertNotContains(response, "Karşılaştırma tablosu")

    def test_table_shown_and_fills_missing_values_with_dash(self):
        poll = Poll.objects.create(author=self.author, title="Hangi telefonu almalıyım?", category="phone")
        Product.objects.create(
            poll=poll, name="Telefon A", price=100, features="x", position=0, attributes="RAM: 8 GB"
        )
        Product.objects.create(poll=poll, name="Telefon B", price=200, features="x", position=1)

        response = self.client.get(reverse("polls:poll_detail", kwargs={"pk": poll.pk}))

        self.assertContains(response, "Karşılaştırma tablosu")
        self.assertContains(response, "RAM")
        self.assertContains(response, "8 GB")
        self.assertContains(response, "—")

    def test_poll_create_saves_attributes(self):
        self.client.force_login(self.author)
        data = build_post_data(2, product_overrides={0: {"attributes": "RAM: 8 GB\nDepolama: 128 GB"}})

        self.client.post(reverse("polls:poll_create"), data)

        product = Product.objects.get(position=0)
        self.assertEqual(product.attributes_dict, {"RAM": "8 GB", "Depolama": "128 GB"})
