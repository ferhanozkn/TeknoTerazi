from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from polls.models import Poll, Product, Vote
from polls.services import merge_anon_votes_into_user

User = get_user_model()

AJAX_HEADERS = {"HTTP_X_REQUESTED_WITH": "XMLHttpRequest"}


def make_poll_with_product(author, **overrides):
    poll = Poll.objects.create(author=author, title="Hangi telefonu almalıyım?", category="phone", **overrides)
    product = Product.objects.create(poll=poll, name="Telefon A", price=1000, features="x", position=0)
    return poll, product


class MergeAnonVotesServiceTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(username="ahmet", email="ahmet@example.com", password="x")
        self.poll, self.product = make_poll_with_product(self.author)
        self.voter = User.objects.create_user(username="ece", email="ece@example.com", password="x")

    def test_noop_when_anon_id_is_none(self):
        merge_anon_votes_into_user(None, self.voter)  # raises nothing

    def test_anon_vote_is_reassigned_to_user(self):
        vote = Vote.objects.create(product=self.product, anon_id="11111111-1111-1111-1111-111111111111", value=1)
        merge_anon_votes_into_user(vote.anon_id, self.voter)
        vote.refresh_from_db()
        self.assertEqual(vote.user, self.voter)
        self.assertIsNone(vote.anon_id)

    def test_anon_vote_on_own_poll_is_discarded(self):
        vote = Vote.objects.create(product=self.product, anon_id="22222222-2222-2222-2222-222222222222", value=1)
        merge_anon_votes_into_user(vote.anon_id, self.author)
        self.assertFalse(Vote.objects.filter(pk=vote.pk).exists())

    def test_anon_vote_is_discarded_when_user_already_voted_on_same_product(self):
        Vote.objects.create(product=self.product, user=self.voter, value=-1)
        anon_vote = Vote.objects.create(
            product=self.product, anon_id="33333333-3333-3333-3333-333333333333", value=1
        )
        merge_anon_votes_into_user(anon_vote.anon_id, self.voter)
        self.assertFalse(Vote.objects.filter(pk=anon_vote.pk).exists())
        remaining = Vote.objects.get(product=self.product)
        self.assertEqual(remaining.user, self.voter)
        self.assertEqual(remaining.value, -1)


class MergeOnLoginIntegrationTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(username="ahmet", email="ahmet@example.com", password="x")
        self.poll, self.product = make_poll_with_product(self.author)
        self.vote_url = reverse("polls:vote", kwargs={"pk": self.product.pk})

    def _vote_anonymously(self):
        response = self.client.post(self.vote_url, {"value": "worth"}, **AJAX_HEADERS)
        self.client.cookies["tt_voter"] = response.cookies["tt_voter"].value
        return Vote.objects.get()

    def test_login_merges_anon_vote(self):
        anon_vote = self._vote_anonymously()
        voter = User.objects.create_user(username="ece", email="ece@example.com", password="dogru-parola-1")

        self.client.post(
            reverse("accounts:login"),
            {"username": "ece@example.com", "password": "dogru-parola-1"},
        )

        anon_vote.refresh_from_db()
        self.assertEqual(anon_vote.user, voter)
        self.assertIsNone(anon_vote.anon_id)

    def test_signup_merges_anon_vote(self):
        anon_vote = self._vote_anonymously()

        self.client.post(
            reverse("accounts:signup"),
            {
                "username": "ece",
                "email": "ece@example.com",
                "password1": "cok-guclu-parola-1",
                "password2": "cok-guclu-parola-1",
            },
        )

        anon_vote.refresh_from_db()
        self.assertEqual(anon_vote.user.username, "ece")
        self.assertIsNone(anon_vote.anon_id)
