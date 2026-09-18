import uuid

from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import translation

from polls.models import Poll, Product, Vote, VoteValue

User = get_user_model()

EN_HEADERS = {"HTTP_ACCEPT_LANGUAGE": "en"}


def make_poll_with_product(author, title="Hangi telefonu almalıyım?", **overrides):
    poll = Poll.objects.create(author=author, title=title, category="phone", **overrides)
    product = Product.objects.create(poll=poll, name="Telefon A", price=1000, features="x", position=0)
    return poll, product


class LanguageDetectionTests(TestCase):
    def test_default_language_is_turkish(self):
        response = self.client.get(reverse("polls:home"))
        self.assertContains(response, "Almadan önce topluluğa sor.")

    def test_accept_language_header_switches_to_english(self):
        response = self.client.get(reverse("polls:home"), **EN_HEADERS)
        self.assertContains(response, "Ask the community before you buy.")

    def test_set_language_view_persists_via_cookie(self):
        response = self.client.post(
            reverse("set_language"), {"language": "en", "next": "/"}
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.client.cookies["django_language"].value, "en")

        home_response = self.client.get(reverse("polls:home"))
        self.assertContains(home_response, "Ask the community before you buy.")

    def test_language_switcher_lists_both_languages(self):
        response = self.client.get(reverse("polls:home"))
        self.assertContains(response, "Türkçe")
        self.assertContains(response, "English")


class TranslatedContentTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(username="ahmet", email="ahmet@example.com", password="x")

    def test_poll_detail_translates_ui_strings(self):
        poll, product = make_poll_with_product(self.author)
        response = self.client.get(reverse("polls:poll_detail", kwargs={"pk": poll.pk}), **EN_HEADERS)
        self.assertContains(response, "Worth it")
        self.assertContains(response, "Not worth it")
        self.assertContains(response, "Comments (0)")
        self.assertContains(response, "No comments yet. Be the first to write one!")

    def test_category_choice_is_translated(self):
        response = self.client.get(reverse("polls:home"), **EN_HEADERS)
        self.assertContains(response, "Smartphone")
        self.assertNotContains(response, "Akıllı Telefon")

    def test_poll_title_is_never_translated(self):
        poll, product = make_poll_with_product(self.author, title="Hangi telefonu almalıyım?")
        response = self.client.get(reverse("polls:poll_detail", kwargs={"pk": poll.pk}), **EN_HEADERS)
        self.assertContains(response, "Hangi telefonu almalıyım?")

    def test_favorite_badge_is_translated(self):
        poll, product = make_poll_with_product(self.author)
        for _ in range(3):
            Vote.objects.create(product=product, anon_id=uuid.uuid4(), value=VoteValue.WORTH)
        response = self.client.get(reverse("polls:poll_detail", kwargs={"pk": poll.pk}), **EN_HEADERS)
        self.assertContains(response, "Community Favorite")

    def test_form_field_label_is_translated(self):
        self.client.force_login(self.author)
        response = self.client.get(reverse("polls:poll_create"), **EN_HEADERS)
        self.assertContains(response, "Category")
        self.assertContains(response, "Create Poll")


class PluralizationTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(username="ahmet", email="ahmet@example.com", password="x")

    def test_singular_vote_count_in_english(self):
        poll, product = make_poll_with_product(self.author)
        Vote.objects.create(product=product, anon_id=uuid.uuid4(), value=VoteValue.WORTH)
        response = self.client.get(reverse("polls:home"), **EN_HEADERS)
        self.assertContains(response, "1 vote<")

    def test_plural_vote_count_in_english(self):
        poll, product = make_poll_with_product(self.author)
        for _ in range(3):
            Vote.objects.create(product=product, anon_id=uuid.uuid4(), value=VoteValue.WORTH)
        response = self.client.get(reverse("polls:home"), **EN_HEADERS)
        self.assertContains(response, "3 votes<")


class TranslationActivationTests(TestCase):
    def test_gettext_resolves_english_directly(self):
        with translation.override("en"):
            self.assertEqual(translation.gettext("Kaydet"), "Save")

    def test_gettext_resolves_turkish_by_default(self):
        with translation.override("tr"):
            self.assertEqual(translation.gettext("Kaydet"), "Kaydet")


@override_settings(LANGUAGE_CODE="tr")
class ExpiryStringsTranslationTests(TestCase):
    def test_expiry_hint_is_translated(self):
        from datetime import timedelta

        from django.utils import timezone

        author = User.objects.create_user(username="ahmet2", email="ahmet2@example.com", password="x")
        poll, product = make_poll_with_product(
            author, title="Ikinci anket", expires_at=timezone.now() - timedelta(hours=1)
        )
        response = self.client.get(reverse("polls:poll_detail", kwargs={"pk": poll.pk}), **EN_HEADERS)
        self.assertContains(response, "Expired")
