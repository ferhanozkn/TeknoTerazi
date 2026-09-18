from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from polls.forms import PollForm
from polls.models import Poll, Product
from polls.services import VoteError, cast_vote, get_trending_polls
from polls.tests.test_views import build_post_data

User = get_user_model()


def make_poll_with_product(author, title="Hangi telefonu almalıyım?", **overrides):
    poll = Poll.objects.create(author=author, title=title, category="phone", **overrides)
    product = Product.objects.create(poll=poll, name="Telefon A", price=1000, features="x", position=0)
    return poll, product


class PollExpiryModelTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(username="ahmet", email="ahmet@example.com", password="x")

    def test_no_expiry_is_never_expired(self):
        poll, _ = make_poll_with_product(self.author)
        self.assertFalse(poll.is_expired)

    def test_future_expiry_is_not_expired(self):
        poll, _ = make_poll_with_product(self.author, expires_at=timezone.now() + timedelta(days=1))
        self.assertFalse(poll.is_expired)

    def test_past_expiry_is_expired(self):
        poll, _ = make_poll_with_product(self.author, expires_at=timezone.now() - timedelta(days=1))
        self.assertTrue(poll.is_expired)


class PollFormExpiryValidationTests(TestCase):
    def base_data(self):
        return {"title": "Hangi telefonu almalıyım?", "category": "phone", "description": ""}

    def test_blank_expires_at_is_valid(self):
        form = PollForm(data={**self.base_data(), "expires_at": ""})
        self.assertTrue(form.is_valid())

    def test_future_expires_at_is_valid(self):
        future = (timezone.now() + timedelta(days=1)).strftime("%Y-%m-%dT%H:%M")
        form = PollForm(data={**self.base_data(), "expires_at": future})
        self.assertTrue(form.is_valid())

    def test_past_expires_at_is_rejected(self):
        past = (timezone.now() - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M")
        form = PollForm(data={**self.base_data(), "expires_at": past})
        self.assertFalse(form.is_valid())
        self.assertIn("expires_at", form.errors)


class PollCreateExpiryViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="ahmet", email="ahmet@example.com", password="x")
        self.client.force_login(self.user)

    def test_future_expires_at_is_saved(self):
        future = timezone.now() + timedelta(days=3)
        data = build_post_data(2, poll_overrides={"expires_at": future.strftime("%Y-%m-%dT%H:%M")})

        self.client.post(reverse("polls:poll_create"), data)

        poll = Poll.objects.get()
        self.assertIsNotNone(poll.expires_at)

    def test_past_expires_at_blocks_creation(self):
        past = timezone.now() - timedelta(days=1)
        data = build_post_data(2, poll_overrides={"expires_at": past.strftime("%Y-%m-%dT%H:%M")})

        response = self.client.post(reverse("polls:poll_create"), data)

        self.assertEqual(Poll.objects.count(), 0)
        self.assertContains(response, "Bitiş tarihi gelecekte bir zaman olmalı.")

    def test_no_expires_at_still_works(self):
        data = build_post_data(2)
        response = self.client.post(reverse("polls:poll_create"), data)
        self.assertEqual(Poll.objects.count(), 1)
        self.assertIsNone(Poll.objects.get().expires_at)
        self.assertEqual(response.status_code, 302)


class ExpiredPollBehaviorTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(username="ahmet", email="ahmet@example.com", password="x")
        self.poll, self.product = make_poll_with_product(
            self.author, expires_at=timezone.now() - timedelta(hours=1)
        )
        self.voter = User.objects.create_user(username="ece", email="ece@example.com", password="x")

    def test_voting_on_expired_poll_is_rejected(self):
        with self.assertRaises(VoteError) as ctx:
            cast_vote(self.product, self.voter, None, 1)
        self.assertEqual(ctx.exception.status, 403)
        self.assertEqual(ctx.exception.message, "Bu anketin süresi doldu.")

    def test_expired_poll_shows_badge_and_disables_vote_buttons(self):
        response = self.client.get(reverse("polls:poll_detail", kwargs={"pk": self.poll.pk}))
        self.assertContains(response, "Süresi doldu")
        self.assertContains(response, "disabled")

    def test_owner_does_not_see_toggle_button_when_expired(self):
        self.client.force_login(self.author)
        toggle_url = reverse("polls:poll_toggle_active", kwargs={"pk": self.poll.pk})
        response = self.client.get(reverse("polls:poll_detail", kwargs={"pk": self.poll.pk}))
        self.assertNotContains(response, toggle_url)
        self.assertContains(response, "Sil")

    def test_expired_poll_excluded_from_acik_filter(self):
        response = self.client.get(reverse("polls:home"), {"durum": "acik"})
        self.assertNotContains(response, self.poll.title)

    def test_expired_poll_excluded_from_trending_even_with_votes_today(self):
        from polls.models import Vote, VoteValue

        Vote.objects.create(product=self.product, user=self.voter, value=VoteValue.WORTH)
        trending = list(get_trending_polls())
        self.assertNotIn(self.poll, trending)

    def test_hide_results_reveals_early_once_expired(self):
        poll, product = make_poll_with_product(
            self.author,
            title="Gizli sonuçlu anket",
            hide_results_until_vote=True,
            expires_at=timezone.now() - timedelta(hours=1),
        )
        response = self.client.get(reverse("polls:poll_detail", kwargs={"pk": poll.pk}))
        self.assertNotContains(response, "data-results-block hidden")
