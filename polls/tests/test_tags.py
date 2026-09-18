from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from polls.models import Poll
from polls.tests.test_views import build_post_data

User = get_user_model()


class PollCreateTagsTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="ahmet", email="ahmet@example.com", password="x")
        self.client.force_login(self.user)

    def test_tags_are_optional(self):
        data = build_post_data(2)
        response = self.client.post(reverse("polls:poll_create"), data)
        self.assertEqual(response.status_code, 302)
        poll = Poll.objects.get()
        self.assertEqual(poll.usage_purpose, "")
        self.assertEqual(poll.budget_tier, "")

    def test_tags_are_saved_when_provided(self):
        data = build_post_data(2, poll_overrides={"usage_purpose": "gaming", "budget_tier": "premium"})
        self.client.post(reverse("polls:poll_create"), data)
        poll = Poll.objects.get()
        self.assertEqual(poll.usage_purpose, "gaming")
        self.assertEqual(poll.budget_tier, "premium")


def make_poll(author, title="Anket", **overrides):
    poll = Poll.objects.create(author=author, title=title, category="phone", **overrides)
    return poll


class TagBadgesAndFilterTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(username="ahmet", email="ahmet@example.com", password="x")

    def test_badges_shown_on_home_and_detail(self):
        poll = make_poll(self.author, usage_purpose="school", budget_tier="economic")
        home_response = self.client.get(reverse("polls:home"))
        self.assertContains(home_response, "Okul")
        self.assertContains(home_response, "Ekonomik")

        detail_response = self.client.get(reverse("polls:poll_detail", kwargs={"pk": poll.pk}))
        self.assertContains(detail_response, "Okul")
        self.assertContains(detail_response, "Ekonomik")

    def test_no_badges_when_tags_unset(self):
        make_poll(self.author, title="Etiketsiz anket")
        response = self.client.get(reverse("polls:home"))
        self.assertNotContains(response, "badge--tag")

    def test_filter_by_usage_purpose(self):
        make_poll(self.author, title="Oyun anketi", usage_purpose="gaming")
        make_poll(self.author, title="Okul anketi", usage_purpose="school")

        response = self.client.get(reverse("polls:home"), {"amac": "gaming"})

        self.assertContains(response, "Oyun anketi")
        self.assertNotContains(response, "Okul anketi")

    def test_filter_by_budget_tier(self):
        make_poll(self.author, title="Ucuz anket", budget_tier="economic")
        make_poll(self.author, title="Pahalı anket", budget_tier="premium")

        response = self.client.get(reverse("polls:home"), {"butce": "premium"})

        self.assertContains(response, "Pahalı anket")
        self.assertNotContains(response, "Ucuz anket")
