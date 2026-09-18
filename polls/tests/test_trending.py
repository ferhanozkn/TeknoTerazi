import uuid
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from polls.models import Poll, Product, Vote, VoteValue
from polls.services import get_trending_polls

User = get_user_model()


def make_poll_with_product(author, title="Hangi telefonu almalıyım?", **overrides):
    poll = Poll.objects.create(author=author, title=title, category="phone", **overrides)
    product = Product.objects.create(poll=poll, name="Telefon A", price=1000, features="x", position=0)
    return poll, product


def vote_at(product, when, **overrides):
    vote = Vote.objects.create(product=product, anon_id=uuid.uuid4(), value=VoteValue.WORTH, **overrides)
    Vote.objects.filter(pk=vote.pk).update(created_at=when)
    return vote


class TrendingPollsTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(username="ahmet", email="ahmet@example.com", password="x")
        self.now = timezone.localtime()
        self.yesterday = self.now - timedelta(days=1)

    def test_poll_with_votes_today_appears_in_trending(self):
        poll, product = make_poll_with_product(self.author)
        vote_at(product, self.now)

        trending = list(get_trending_polls())

        self.assertIn(poll, trending)

    def test_poll_with_only_yesterdays_votes_is_excluded(self):
        poll, product = make_poll_with_product(self.author)
        vote_at(product, self.yesterday)

        trending = list(get_trending_polls())

        self.assertNotIn(poll, trending)

    def test_poll_with_no_votes_is_excluded(self):
        poll, _ = make_poll_with_product(self.author)
        self.assertNotIn(poll, list(get_trending_polls()))

    def test_closed_poll_is_excluded_even_with_votes_today(self):
        poll, product = make_poll_with_product(self.author, is_active=False)
        vote_at(product, self.now)

        self.assertNotIn(poll, list(get_trending_polls()))

    def test_ordered_by_todays_vote_count_descending(self):
        quiet_poll, quiet_product = make_poll_with_product(self.author, title="Az oylu anket")
        busy_poll, busy_product = make_poll_with_product(self.author, title="Çok oylu anket")
        vote_at(quiet_product, self.now)
        for _ in range(3):
            Vote.objects.create(product=busy_product, anon_id=uuid.uuid4(), value=VoteValue.WORTH)

        trending = list(get_trending_polls())

        self.assertEqual(trending[0], busy_poll)
        self.assertEqual(trending[1], quiet_poll)

    def test_limited_to_five(self):
        for i in range(6):
            poll, product = make_poll_with_product(self.author, title=f"Anket {i}")
            vote_at(product, self.now)

        self.assertEqual(len(list(get_trending_polls())), 5)

    def test_home_view_shows_trending_section(self):
        poll, product = make_poll_with_product(self.author, title="Trend olan anket")
        vote_at(product, self.now)

        response = self.client.get(reverse("polls:home"))

        self.assertContains(response, "Bugün trend olanlar")
        self.assertContains(response, "Trend olan anket")

    def test_home_view_hides_trending_section_when_nothing_trending(self):
        response = self.client.get(reverse("polls:home"))
        self.assertNotContains(response, "Bugün trend olanlar")
