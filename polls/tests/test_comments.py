from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from polls.models import Comment, Poll, Product

User = get_user_model()


def make_poll_with_product(author, **overrides):
    poll = Poll.objects.create(author=author, title="Hangi telefonu almalıyım?", category="phone", **overrides)
    product = Product.objects.create(poll=poll, name="Telefon A", price=1000, features="x", position=0)
    return poll, product


class CommentAddViewTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(username="ahmet", email="ahmet@example.com", password="x")
        self.poll, self.product = make_poll_with_product(self.author)
        self.comment_add_url = reverse("polls:comment_add", kwargs={"pk": self.product.pk})

    def test_guest_is_redirected_to_login(self):
        response = self.client.post(self.comment_add_url, {"body": "Kamerası harika."})
        self.assertRedirects(response, f"{reverse('accounts:login')}?next={self.comment_add_url}")
        self.assertEqual(Comment.objects.count(), 0)

    def test_member_can_add_comment(self):
        voter = User.objects.create_user(username="ece", email="ece@example.com", password="x")
        self.client.force_login(voter)

        response = self.client.post(self.comment_add_url, {"body": "Kamerası harika, fiyatına göre çok iyi."})

        self.assertRedirects(
            response,
            f"{reverse('polls:poll_detail', kwargs={'pk': self.poll.pk})}#urun-{self.product.pk}",
            fetch_redirect_response=False,
        )
        self.assertEqual(Comment.objects.count(), 1)
        comment = Comment.objects.get()
        self.assertEqual(comment.author, voter)
        self.assertEqual(comment.product, self.product)

    def test_poll_author_can_also_comment(self):
        self.client.force_login(self.author)
        response = self.client.post(self.comment_add_url, {"body": "Kendi anketime not düşüyorum."})
        self.assertEqual(Comment.objects.count(), 1)
        self.assertEqual(response.status_code, 302)

    def test_empty_comment_is_rejected(self):
        voter = User.objects.create_user(username="ece", email="ece@example.com", password="x")
        self.client.force_login(voter)
        self.client.post(self.comment_add_url, {"body": ""})
        self.assertEqual(Comment.objects.count(), 0)

    def test_too_long_comment_is_rejected(self):
        voter = User.objects.create_user(username="ece", email="ece@example.com", password="x")
        self.client.force_login(voter)
        self.client.post(self.comment_add_url, {"body": "a" * 501})
        self.assertEqual(Comment.objects.count(), 0)

    def test_comment_appears_on_poll_detail_page(self):
        voter = User.objects.create_user(username="ece", email="ece@example.com", password="x")
        self.client.force_login(voter)
        self.client.post(self.comment_add_url, {"body": "Kamerası harika, fiyatına göre çok iyi."})

        response = self.client.get(reverse("polls:poll_detail", kwargs={"pk": self.poll.pk}))

        self.assertContains(response, "Kamerası harika, fiyatına göre çok iyi.")
        self.assertContains(response, "@ece")


class CommentDeleteViewTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(username="ahmet", email="ahmet@example.com", password="x")
        self.poll, self.product = make_poll_with_product(self.author)
        self.voter = User.objects.create_user(username="ece", email="ece@example.com", password="x")
        self.comment = Comment.objects.create(product=self.product, author=self.voter, body="Kamerası harika.")
        self.delete_url = reverse("polls:comment_delete", kwargs={"pk": self.comment.pk})

    def test_guest_is_redirected_to_login(self):
        response = self.client.post(self.delete_url)
        self.assertRedirects(response, f"{reverse('accounts:login')}?next={self.delete_url}")
        self.assertEqual(Comment.objects.count(), 1)

    def test_author_can_delete_own_comment(self):
        self.client.force_login(self.voter)
        response = self.client.post(self.delete_url)
        self.assertRedirects(
            response,
            f"{reverse('polls:poll_detail', kwargs={'pk': self.poll.pk})}#urun-{self.product.pk}",
            fetch_redirect_response=False,
        )
        self.assertEqual(Comment.objects.count(), 0)

    def test_other_user_cannot_delete_comment(self):
        other = User.objects.create_user(username="mert", email="mert@example.com", password="x")
        self.client.force_login(other)
        response = self.client.post(self.delete_url)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(Comment.objects.count(), 1)
