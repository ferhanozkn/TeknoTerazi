import uuid

from django.contrib.auth import get_user_model
from django.db import connection
from django.test import TestCase
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from polls.models import Poll, Product, Vote, VoteValue

User = get_user_model()


def product_fields(index, **overrides):
    data = {
        f"products-{index}-id": "",
        f"products-{index}-name": f"Ürün {index}",
        f"products-{index}-price": "1000",
        f"products-{index}-features": "Özellik A",
        f"products-{index}-product_url": "",
        f"products-{index}-image_url": "",
    }
    for key, value in overrides.items():
        data[f"products-{index}-{key}"] = value
    return data


def build_post_data(product_count, poll_overrides=None, product_overrides=None):
    data = {
        "title": "Hangi telefonu almalıyım?",
        "category": "phone",
        "description": "",
        "products-TOTAL_FORMS": str(product_count),
        "products-INITIAL_FORMS": "0",
        "products-MIN_NUM_FORMS": "0",
        "products-MAX_NUM_FORMS": "1000",
    }
    data.update(poll_overrides or {})
    product_overrides = product_overrides or {}
    for i in range(product_count):
        data.update(product_fields(i, **product_overrides.get(i, {})))
    return data


class PollCreateViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="ahmet", email="ahmet@example.com", password="x")
        self.client.force_login(self.user)

    def test_guest_is_redirected_to_login(self):
        self.client.logout()
        create_url = reverse("polls:poll_create")
        response = self.client.get(create_url)
        self.assertRedirects(response, f"{reverse('accounts:login')}?next={create_url}")

    def test_one_product_is_rejected(self):
        response = self.client.post(reverse("polls:poll_create"), build_post_data(1))
        self.assertContains(response, "Bir ankete en az 2 ürün eklemelisin.")
        self.assertEqual(Poll.objects.count(), 0)

    def test_six_products_is_rejected(self):
        response = self.client.post(reverse("polls:poll_create"), build_post_data(6))
        self.assertContains(response, "Bir ankete en fazla 5 ürün ekleyebilirsin.")
        self.assertEqual(Poll.objects.count(), 0)

    def test_product_without_price_is_rejected(self):
        data = build_post_data(2, product_overrides={0: {"price": ""}})
        response = self.client.post(reverse("polls:poll_create"), data)
        self.assertContains(response, "Geçerli bir fiyat gir.")
        self.assertEqual(Poll.objects.count(), 0)

    def test_product_without_features_is_rejected(self):
        data = build_post_data(2, product_overrides={0: {"features": ""}})
        response = self.client.post(reverse("polls:poll_create"), data)
        self.assertContains(response, "Ürünün en az bir özelliğini yazmalısın.")
        self.assertEqual(Poll.objects.count(), 0)

    def test_duplicate_product_name_is_rejected(self):
        data = build_post_data(2, product_overrides={1: {"name": "Ürün 0"}})
        response = self.client.post(reverse("polls:poll_create"), data)
        self.assertContains(response, "Aynı ürünü iki kez ekleyemezsin.")
        self.assertEqual(Poll.objects.count(), 0)

    def test_two_products_succeeds(self):
        response = self.client.post(reverse("polls:poll_create"), build_post_data(2))
        poll = Poll.objects.get()
        self.assertRedirects(response, reverse("polls:poll_detail", kwargs={"pk": poll.pk}))
        self.assertEqual(poll.author, self.user)
        self.assertEqual(list(poll.products.order_by("position").values_list("position", flat=True)), [0, 1])

    def test_five_products_succeeds(self):
        self.client.post(reverse("polls:poll_create"), build_post_data(5))
        poll = Poll.objects.get()
        self.assertEqual(poll.products.count(), 5)

    def test_invalid_submission_preserves_entered_data(self):
        data = build_post_data(1, poll_overrides={"title": "Kaybolmamalı başlık"})
        response = self.client.post(reverse("polls:poll_create"), data)
        self.assertContains(response, "Kaybolmamalı başlık")


def make_poll_with_products(author, title="Anket", category="phone", product_count=2, **overrides):
    poll = Poll.objects.create(author=author, title=title, category=category, **overrides)
    for i in range(product_count):
        Product.objects.create(
            poll=poll,
            name=f"{title} Ürün {i}",
            price=100 * (i + 1),
            features="Özellik",
            position=i,
        )
    return poll


class HomeViewTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(username="ahmet", email="ahmet@example.com", password="x")

    def test_guest_can_view_home(self):
        make_poll_with_products(self.author, title="Hangi telefonu almalıyım?")
        response = self.client.get(reverse("polls:home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Hangi telefonu almalıyım?")

    def test_empty_state_when_no_polls(self):
        response = self.client.get(reverse("polls:home"))
        self.assertContains(response, "Henüz anket yok.")

    def test_search_matches_poll_title(self):
        make_poll_with_products(self.author, title="Hangi telefonu almalıyım?")
        make_poll_with_products(self.author, title="Hangi laptopu almalıyım?")
        response = self.client.get(reverse("polls:home"), {"q": "telefon"})
        self.assertContains(response, "Hangi telefonu almalıyım?")
        self.assertNotContains(response, "Hangi laptopu almalıyım?")

    def test_search_matches_product_name(self):
        poll = make_poll_with_products(self.author, title="Anket A", product_count=0)
        Product.objects.create(poll=poll, name="iPhone 15", price=100, features="x", position=0)
        make_poll_with_products(self.author, title="Anket B")
        response = self.client.get(reverse("polls:home"), {"q": "iphone"})
        self.assertContains(response, "Anket A")
        self.assertNotContains(response, "Anket B")

    def test_category_filter(self):
        make_poll_with_products(self.author, title="Telefon anketi", category="phone")
        make_poll_with_products(self.author, title="Laptop anketi", category="laptop")
        response = self.client.get(reverse("polls:home"), {"kategori": "laptop"})
        self.assertContains(response, "Laptop anketi")
        self.assertNotContains(response, "Telefon anketi")

    def test_status_filter_only_active(self):
        make_poll_with_products(self.author, title="Açık anket", is_active=True)
        make_poll_with_products(self.author, title="Kapalı anket", is_active=False)
        response = self.client.get(reverse("polls:home"), {"durum": "acik"})
        self.assertContains(response, "Açık anket")
        self.assertNotContains(response, "Kapalı anket")

    def test_pagination_splits_across_pages(self):
        for i in range(13):
            make_poll_with_products(self.author, title=f"Anket {i}")
        page1 = self.client.get(reverse("polls:home"))
        self.assertEqual(len(page1.context["page_obj"]), 12)
        page2 = self.client.get(reverse("polls:home"), {"sayfa": 2})
        self.assertEqual(len(page2.context["page_obj"]), 1)

    def test_query_count_is_constant_regardless_of_poll_count(self):
        for i in range(3):
            make_poll_with_products(self.author, title=f"Küçük {i}")
        with CaptureQueriesContext(connection) as small:
            self.client.get(reverse("polls:home"))

        for i in range(15):
            make_poll_with_products(self.author, title=f"Büyük {i}")
        with CaptureQueriesContext(connection) as large:
            self.client.get(reverse("polls:home"))

        self.assertEqual(len(small.captured_queries), len(large.captured_queries))


class PollDetailViewTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(username="ahmet", email="ahmet@example.com", password="x")

    def test_guest_can_view_detail(self):
        poll = make_poll_with_products(self.author, title="Hangi telefonu almalıyım?")
        response = self.client.get(reverse("polls:poll_detail", kwargs={"pk": poll.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Hangi telefonu almalıyım?")

    def test_nonexistent_poll_returns_404(self):
        response = self.client.get(reverse("polls:poll_detail", kwargs={"pk": 9999}))
        self.assertEqual(response.status_code, 404)

    def test_favorite_badge_shown_for_eligible_top_product(self):
        poll = make_poll_with_products(self.author, product_count=0)
        strong = Product.objects.create(poll=poll, name="Güçlü", price=100, features="x", position=0)
        weak = Product.objects.create(poll=poll, name="Zayıf", price=100, features="x", position=1)
        for _ in range(4):
            Vote.objects.create(product=strong, anon_id=uuid.uuid4(), value=VoteValue.WORTH)
        Vote.objects.create(product=strong, anon_id=uuid.uuid4(), value=VoteValue.NOT_WORTH)
        Vote.objects.create(product=weak, anon_id=uuid.uuid4(), value=VoteValue.WORTH)

        response = self.client.get(reverse("polls:poll_detail", kwargs={"pk": poll.pk}))
        self.assertContains(response, "Topluluğun Favorisi")

    def test_no_favorite_badge_below_minimum_votes(self):
        poll = make_poll_with_products(self.author, product_count=0)
        Product.objects.create(poll=poll, name="Tek", price=100, features="x", position=0)
        response = self.client.get(reverse("polls:poll_detail", kwargs={"pk": poll.pk}))
        self.assertNotContains(response, "Topluluğun Favorisi")

    def test_owner_sees_manage_actions(self):
        poll = make_poll_with_products(self.author)
        self.client.force_login(self.author)
        response = self.client.get(reverse("polls:poll_detail", kwargs={"pk": poll.pk}))
        self.assertContains(response, 'id="share-button"')
        self.assertContains(response, "poll-detail__owner-actions")

    def test_non_owner_does_not_see_manage_actions(self):
        poll = make_poll_with_products(self.author)
        other = User.objects.create_user(username="ece", email="ece@example.com", password="x")
        self.client.force_login(other)
        response = self.client.get(reverse("polls:poll_detail", kwargs={"pk": poll.pk}))
        self.assertNotContains(response, "poll-detail__owner-actions")


class PollToggleActiveViewTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(username="ahmet", email="ahmet@example.com", password="x")
        self.poll = make_poll_with_products(self.author)

    def test_owner_can_toggle(self):
        self.client.force_login(self.author)
        url = reverse("polls:poll_toggle_active", kwargs={"pk": self.poll.pk})
        response = self.client.post(url)
        self.assertRedirects(response, reverse("polls:my_polls"))
        self.poll.refresh_from_db()
        self.assertFalse(self.poll.is_active)

    def test_non_owner_gets_404(self):
        other = User.objects.create_user(username="ece", email="ece@example.com", password="x")
        self.client.force_login(other)
        url = reverse("polls:poll_toggle_active", kwargs={"pk": self.poll.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)
        self.poll.refresh_from_db()
        self.assertTrue(self.poll.is_active)

    def test_guest_is_redirected_to_login(self):
        url = reverse("polls:poll_toggle_active", kwargs={"pk": self.poll.pk})
        response = self.client.post(url)
        self.assertRedirects(response, f"{reverse('accounts:login')}?next={url}")

    def test_get_is_not_allowed(self):
        self.client.force_login(self.author)
        url = reverse("polls:poll_toggle_active", kwargs={"pk": self.poll.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 405)


class PollDeleteViewTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(username="ahmet", email="ahmet@example.com", password="x")
        self.poll = make_poll_with_products(self.author)

    def test_get_shows_confirmation_page(self):
        self.client.force_login(self.author)
        url = reverse("polls:poll_delete", kwargs={"pk": self.poll.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.poll.title)

    def test_owner_can_delete(self):
        self.client.force_login(self.author)
        url = reverse("polls:poll_delete", kwargs={"pk": self.poll.pk})
        response = self.client.post(url)
        self.assertRedirects(response, reverse("polls:my_polls"))
        self.assertFalse(Poll.objects.filter(pk=self.poll.pk).exists())

    def test_non_owner_gets_404(self):
        other = User.objects.create_user(username="ece", email="ece@example.com", password="x")
        self.client.force_login(other)
        url = reverse("polls:poll_delete", kwargs={"pk": self.poll.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)
        self.assertTrue(Poll.objects.filter(pk=self.poll.pk).exists())


class MyPollsViewTests(TestCase):
    def test_shows_only_own_polls(self):
        author = User.objects.create_user(username="ahmet", email="ahmet@example.com", password="x")
        other = User.objects.create_user(username="ece", email="ece@example.com", password="x")
        make_poll_with_products(author, title="Benim anketim")
        make_poll_with_products(other, title="Başkasının anketi")

        self.client.force_login(author)
        response = self.client.get(reverse("polls:my_polls"))
        self.assertContains(response, "Benim anketim")
        self.assertNotContains(response, "Başkasının anketi")

    def test_guest_is_redirected_to_login(self):
        url = reverse("polls:my_polls")
        response = self.client.get(url)
        self.assertRedirects(response, f"{reverse('accounts:login')}?next={url}")


class ErrorPageTests(TestCase):
    def test_404_uses_custom_template(self):
        with self.settings(DEBUG=False, ALLOWED_HOSTS=["testserver"]):
            response = self.client.get("/olmayan-bir-sayfa/")
        self.assertEqual(response.status_code, 404)
        self.assertContains(response, "Bu sayfa terazide yok", status_code=404)
