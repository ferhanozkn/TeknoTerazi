from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from polls.models import Poll, Product, Vote, VoteValue

User = get_user_model()


def make_poll_with_product(author, title="Hangi telefonu almalıyım?", **overrides):
    poll = Poll.objects.create(author=author, title=title, category="phone", **overrides)
    product = Product.objects.create(poll=poll, name="Telefon A", price=1000, features="x", position=0)
    return poll, product


class ViewCountTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(username="ahmet", email="ahmet@example.com", password="x")

    def test_view_count_starts_at_zero(self):
        poll, _product = make_poll_with_product(self.author)
        self.assertEqual(poll.view_count, 0)

    def test_view_count_increments_on_poll_detail_view(self):
        poll, _product = make_poll_with_product(self.author)
        self.client.get(reverse("polls:poll_detail", kwargs={"pk": poll.pk}))
        poll.refresh_from_db()
        self.assertEqual(poll.view_count, 1)

    def test_view_count_increments_on_each_visit(self):
        poll, _product = make_poll_with_product(self.author)
        for _ in range(3):
            self.client.get(reverse("polls:poll_detail", kwargs={"pk": poll.pk}))
        poll.refresh_from_db()
        self.assertEqual(poll.view_count, 3)

    def test_view_count_increments_for_owner_too(self):
        poll, _product = make_poll_with_product(self.author)
        self.client.force_login(self.author)
        self.client.get(reverse("polls:poll_detail", kwargs={"pk": poll.pk}))
        poll.refresh_from_db()
        self.assertEqual(poll.view_count, 1)


class AnalyticsDisplayTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(username="ahmet", email="ahmet@example.com", password="x")
        self.other = User.objects.create_user(username="mehmet", email="mehmet@example.com", password="x")

    def test_owner_sees_analytics_block(self):
        poll, product = make_poll_with_product(self.author)
        self.client.force_login(self.author)
        response = self.client.get(reverse("polls:poll_detail", kwargs={"pk": poll.pk}))
        self.assertContains(response, "poll-detail__analytics")
        self.assertContains(response, "yalnızca sana görünür")

    def test_non_owner_does_not_see_analytics_block(self):
        poll, product = make_poll_with_product(self.author)
        self.client.force_login(self.other)
        response = self.client.get(reverse("polls:poll_detail", kwargs={"pk": poll.pk}))
        self.assertNotContains(response, "poll-detail__analytics")

    def test_anonymous_visitor_does_not_see_analytics_block(self):
        poll, product = make_poll_with_product(self.author)
        response = self.client.get(reverse("polls:poll_detail", kwargs={"pk": poll.pk}))
        self.assertNotContains(response, "poll-detail__analytics")

    def test_conversion_rate_shown_after_votes(self):
        poll, product = make_poll_with_product(self.author)
        for i in range(2):
            self.client.get(reverse("polls:poll_detail", kwargs={"pk": poll.pk}))
        Vote.objects.create(product=product, anon_id="a1111111-1111-1111-1111-111111111111", value=VoteValue.WORTH)
        self.client.force_login(self.author)
        response = self.client.get(reverse("polls:poll_detail", kwargs={"pk": poll.pk}))
        # 3 views by now (2 anonymous + this one), 1 vote -> %33
        self.assertContains(response, "dönüşüm")

    def test_conversion_rate_is_zero_percent_with_no_votes_yet(self):
        poll, product = make_poll_with_product(self.author)
        self.client.force_login(self.author)
        response = self.client.get(reverse("polls:poll_detail", kwargs={"pk": poll.pk}))
        # This request itself counts as the first view, with no votes yet -> %0.
        self.assertContains(response, "%0")
        self.assertContains(response, "dönüşüm")

    def test_my_polls_shows_view_count(self):
        poll, product = make_poll_with_product(self.author)
        self.client.get(reverse("polls:poll_detail", kwargs={"pk": poll.pk}))
        self.client.force_login(self.author)
        response = self.client.get(reverse("polls:my_polls"))
        self.assertContains(response, "görüntülenme")
