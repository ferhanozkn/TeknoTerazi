import uuid

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from polls.models import Poll, Product, Vote, VoteValue

User = get_user_model()


def make_poll_with_product(author, title="Hangi telefonu almalıyım?", **overrides):
    poll = Poll.objects.create(author=author, title=title, category="phone", **overrides)
    product = Product.objects.create(poll=poll, name="Telefon A", price=1000, features="x", position=0)
    return poll, product


class HideResultsUntilVoteTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(username="ahmet", email="ahmet@example.com", password="x")
        self.poll, self.product = make_poll_with_product(self.author, hide_results_until_vote=True)
        Vote.objects.create(product=self.product, user=self.author, value=VoteValue.WORTH)
        self.detail_url = reverse("polls:poll_detail", kwargs={"pk": self.poll.pk})

    def test_guest_does_not_see_results_before_voting(self):
        response = self.client.get(self.detail_url)
        self.assertContains(response, "data-results-block hidden")
        self.assertContains(response, "data-results-hint")
        self.assertNotContains(response, "data-results-hint hidden")

    def test_voter_sees_results_after_voting(self):
        voter = User.objects.create_user(username="ece", email="ece@example.com", password="x")
        self.client.force_login(voter)
        self.client.post(reverse("polls:vote", kwargs={"pk": self.product.pk}), {"value": "worth"})

        response = self.client.get(self.detail_url)

        self.assertNotContains(response, "data-results-block hidden")
        self.assertContains(response, "data-results-hint hidden")

    def test_owner_always_sees_results(self):
        self.client.force_login(self.author)
        response = self.client.get(self.detail_url)
        self.assertNotContains(response, "data-results-block hidden")

    def test_results_visible_regardless_once_poll_is_closed(self):
        self.poll.is_active = False
        self.poll.save(update_fields=["is_active"])
        response = self.client.get(self.detail_url)
        self.assertNotContains(response, "data-results-block hidden")

    def test_favorite_badge_hidden_before_voting(self):
        for _ in range(3):
            Vote.objects.create(product=self.product, anon_id=uuid.uuid4(), value=VoteValue.WORTH)
        response = self.client.get(self.detail_url)
        self.assertNotContains(response, "Topluluğun Favorisi")

    def test_favorite_badge_shown_after_voting(self):
        for _ in range(3):
            Vote.objects.create(product=self.product, anon_id=uuid.uuid4(), value=VoteValue.WORTH)
        self.client.force_login(self.author)
        response = self.client.get(self.detail_url)
        self.assertContains(response, "Topluluğun Favorisi")

    def test_no_hint_markup_when_setting_is_off(self):
        poll, product = make_poll_with_product(self.author, title="Varsayılan anket", hide_results_until_vote=False)
        response = self.client.get(reverse("polls:poll_detail", kwargs={"pk": poll.pk}))
        self.assertNotContains(response, "data-results-hint")
        self.assertNotContains(response, "data-results-block hidden")
