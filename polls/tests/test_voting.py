from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from polls.models import Poll, Product, Vote, VoteAttempt

User = get_user_model()

AJAX_HEADERS = {"HTTP_X_REQUESTED_WITH": "XMLHttpRequest"}


def make_poll_with_product(author, **overrides):
    poll = Poll.objects.create(author=author, title="Hangi telefonu almalıyım?", category="phone", **overrides)
    product = Product.objects.create(poll=poll, name="Telefon A", price=1000, features="x", position=0)
    return poll, product


class VoteViewTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(username="ahmet", email="ahmet@example.com", password="x")
        self.poll, self.product = make_poll_with_product(self.author)
        self.vote_url = reverse("polls:vote", kwargs={"pk": self.product.pk})

    def test_guest_votes_cookie_is_set_and_toggling_same_value_removes_vote(self):
        response = self.client.post(self.vote_url, {"value": "worth"}, **AJAX_HEADERS)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["worth_count"], 1)
        self.assertEqual(response.json()["user_vote"], "worth")
        self.assertIn("tt_voter", response.cookies)
        self.assertEqual(Vote.objects.count(), 1)

        response2 = self.client.post(self.vote_url, {"value": "worth"}, **AJAX_HEADERS)
        self.assertEqual(response2.json()["worth_count"], 0)
        self.assertIsNone(response2.json()["user_vote"])
        self.assertEqual(Vote.objects.count(), 0)

    def test_member_changes_vote_keeps_single_record(self):
        voter = User.objects.create_user(username="ece", email="ece@example.com", password="x")
        self.client.force_login(voter)

        self.client.post(self.vote_url, {"value": "worth"}, **AJAX_HEADERS)
        response = self.client.post(self.vote_url, {"value": "not_worth"}, **AJAX_HEADERS)

        self.assertEqual(Vote.objects.count(), 1)
        self.assertEqual(Vote.objects.get().value, -1)
        self.assertEqual(response.json()["user_vote"], "not_worth")
        self.assertEqual(response.json()["worth_count"], 0)
        self.assertEqual(response.json()["not_worth_count"], 1)

    def test_closed_poll_returns_403(self):
        self.poll.is_active = False
        self.poll.save(update_fields=["is_active"])
        response = self.client.post(self.vote_url, {"value": "worth"}, **AJAX_HEADERS)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["error"], "Bu anket oylamaya kapalı.")
        self.assertEqual(Vote.objects.count(), 0)

    def test_owner_cannot_vote_on_own_poll(self):
        self.client.force_login(self.author)
        response = self.client.post(self.vote_url, {"value": "worth"}, **AJAX_HEADERS)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["error"], "Kendi anketine oy veremezsin.")
        self.assertEqual(Vote.objects.count(), 0)

    def test_tampered_cookie_gets_new_identity_without_error(self):
        self.client.cookies["tt_voter"] = "not-a-valid-signed-value"
        response = self.client.post(self.vote_url, {"value": "worth"}, **AJAX_HEADERS)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Vote.objects.count(), 1)
        self.assertIn("tt_voter", response.cookies)
        self.assertNotEqual(response.cookies["tt_voter"].value, "not-a-valid-signed-value")

    def test_get_is_not_allowed(self):
        response = self.client.get(self.vote_url)
        self.assertEqual(response.status_code, 405)

    def test_request_without_csrf_token_is_rejected(self):
        csrf_client = Client(enforce_csrf_checks=True)
        response = csrf_client.post(self.vote_url, {"value": "worth"}, **AJAX_HEADERS)
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Vote.objects.count(), 0)

    def test_non_ajax_request_redirects_to_poll_detail(self):
        response = self.client.post(self.vote_url, {"value": "worth"})
        self.assertRedirects(response, reverse("polls:poll_detail", kwargs={"pk": self.poll.pk}))
        self.assertEqual(Vote.objects.count(), 1)

    def test_invalid_value_is_rejected(self):
        response = self.client.post(self.vote_url, {"value": "garbage"}, **AJAX_HEADERS)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Vote.objects.count(), 0)

    def test_nonexistent_product_returns_404(self):
        url = reverse("polls:vote", kwargs={"pk": 9999})
        response = self.client.post(url, {"value": "worth"}, **AJAX_HEADERS)
        self.assertEqual(response.status_code, 404)


class PollDetailUserVoteTests(TestCase):
    def test_existing_vote_is_reflected_as_pressed(self):
        author = User.objects.create_user(username="ahmet", email="ahmet@example.com", password="x")
        poll, product = make_poll_with_product(author)
        voter = User.objects.create_user(username="ece", email="ece@example.com", password="x")
        self.client.force_login(voter)

        vote_url = reverse("polls:vote", kwargs={"pk": product.pk})
        self.client.post(vote_url, {"value": "worth"}, **AJAX_HEADERS)

        response = self.client.get(reverse("polls:poll_detail", kwargs={"pk": poll.pk}))
        self.assertContains(response, 'aria-pressed="true"', count=1)
        self.assertContains(response, 'aria-pressed="false"', count=1)


class IpHashDuplicateVoteTests(TestCase):
    def setUp(self):
        author = User.objects.create_user(username="ahmet", email="ahmet@example.com", password="x")
        self.poll, self.product = make_poll_with_product(author)
        self.vote_url = reverse("polls:vote", kwargs={"pk": self.product.pk})

    def test_second_anon_identity_from_same_ip_is_rejected(self):
        response1 = self.client.post(self.vote_url, {"value": "worth"}, **AJAX_HEADERS)
        self.assertEqual(response1.status_code, 200)

        other_client = Client()
        response2 = other_client.post(self.vote_url, {"value": "worth"}, **AJAX_HEADERS)
        self.assertEqual(response2.status_code, 403)
        self.assertEqual(response2.json()["error"], "Bu IP adresinden bu ürüne zaten oy verilmiş.")
        self.assertEqual(Vote.objects.count(), 1)

    def test_same_anon_identity_can_still_change_or_remove_own_vote(self):
        response1 = self.client.post(self.vote_url, {"value": "worth"}, **AJAX_HEADERS)
        self.client.cookies["tt_voter"] = response1.cookies["tt_voter"].value

        response2 = self.client.post(self.vote_url, {"value": "not_worth"}, **AJAX_HEADERS)
        self.assertEqual(response2.status_code, 200)
        self.assertEqual(Vote.objects.get().value, -1)

    def test_different_ip_is_not_blocked(self):
        self.client.post(self.vote_url, {"value": "worth"}, **AJAX_HEADERS, REMOTE_ADDR="1.2.3.4")

        other_client = Client()
        response = other_client.post(
            self.vote_url, {"value": "worth"}, **AJAX_HEADERS, REMOTE_ADDR="5.6.7.8"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Vote.objects.count(), 2)

    def test_x_forwarded_for_is_preferred_over_remote_addr(self):
        self.client.post(
            self.vote_url,
            {"value": "worth"},
            **AJAX_HEADERS,
            REMOTE_ADDR="10.0.0.1",
            HTTP_X_FORWARDED_FOR="9.9.9.9, 10.0.0.1",
        )
        other_client = Client()
        response = other_client.post(
            self.vote_url,
            {"value": "worth"},
            **AJAX_HEADERS,
            REMOTE_ADDR="10.0.0.2",
            HTTP_X_FORWARDED_FOR="9.9.9.9, 10.0.0.2",
        )
        self.assertEqual(response.status_code, 403)

    def test_member_votes_are_not_ip_restricted(self):
        voter1 = User.objects.create_user(username="ece", email="ece@example.com", password="x")
        voter2 = User.objects.create_user(username="can", email="can@example.com", password="x")

        self.client.force_login(voter1)
        response1 = self.client.post(self.vote_url, {"value": "worth"}, **AJAX_HEADERS)
        self.assertEqual(response1.status_code, 200)
        self.client.logout()

        self.client.force_login(voter2)
        response2 = self.client.post(self.vote_url, {"value": "worth"}, **AJAX_HEADERS)
        self.assertEqual(response2.status_code, 200)
        self.assertEqual(Vote.objects.count(), 2)


class VoteRateLimitTests(TestCase):
    def setUp(self):
        author = User.objects.create_user(username="ahmet", email="ahmet@example.com", password="x")
        self.poll, self.product = make_poll_with_product(author)
        self.vote_url = reverse("polls:vote", kwargs={"pk": self.product.pk})

    def _sign_anon_cookie(self):
        response = self.client.post(self.vote_url, {"value": "worth"}, **AJAX_HEADERS)
        return response.cookies["tt_voter"].value

    def test_over_limit_requests_are_rejected_with_429(self):
        signed = self._sign_anon_cookie()
        self.client.cookies["tt_voter"] = signed
        anon_id = Vote.objects.get().anon_id

        VoteAttempt.objects.bulk_create(
            [VoteAttempt(anon_id=anon_id) for _ in range(59)]
        )

        response = self.client.post(self.vote_url, {"value": "not_worth"}, **AJAX_HEADERS)
        self.assertEqual(response.status_code, 429)
        self.assertEqual(response.json()["error"], "Çok fazla oy isteği gönderdin. Lütfen biraz bekle.")

    def test_different_voters_have_independent_limits(self):
        signed = self._sign_anon_cookie()
        self.client.cookies["tt_voter"] = signed
        anon_id = Vote.objects.get().anon_id
        VoteAttempt.objects.bulk_create([VoteAttempt(anon_id=anon_id) for _ in range(60)])

        other_client = Client()
        response = other_client.post(
            self.vote_url, {"value": "worth"}, **AJAX_HEADERS, REMOTE_ADDR="8.8.8.8"
        )
        self.assertEqual(response.status_code, 200)
