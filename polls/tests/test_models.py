import uuid

from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.test import TestCase

from polls.models import Category, Poll, Product, Vote, VoteValue

User = get_user_model()


def make_poll(author, **kwargs):
    defaults = {
        "title": "Hangi telefonu almalıyım?",
        "category": Category.PHONE,
    }
    defaults.update(kwargs)
    return Poll.objects.create(author=author, **defaults)


def make_product(poll, **kwargs):
    defaults = {
        "name": "Telefon A",
        "price": "19999.90",
        "features": "128 GB\n8 GB RAM",
        "position": 0,
    }
    defaults.update(kwargs)
    return Product.objects.create(poll=poll, **defaults)


class ProductFeaturesListTests(TestCase):
    def test_blank_lines_are_dropped(self):
        product = make_product(
            make_poll(User.objects.create_user(username="ahmet", email="a@example.com", password="x")),
            features="128 GB\n\n  8 GB RAM  \n",
        )
        self.assertEqual(product.features_list, ["128 GB", "8 GB RAM"])


class ProductPositionConstraintTests(TestCase):
    def test_same_position_twice_in_same_poll_is_rejected(self):
        author = User.objects.create_user(username="ahmet", email="a@example.com", password="x")
        poll = make_poll(author)
        make_product(poll, position=0)
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                make_product(poll, name="Telefon B", position=0)


class VoteConstraintTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(username="ahmet", email="a@example.com", password="x")
        self.voter = User.objects.create_user(username="ece", email="e@example.com", password="x")
        self.poll = make_poll(self.author)
        self.product = make_product(self.poll)

    def test_user_cannot_vote_twice_on_same_product(self):
        Vote.objects.create(product=self.product, user=self.voter, value=VoteValue.WORTH)
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Vote.objects.create(product=self.product, user=self.voter, value=VoteValue.NOT_WORTH)

    def test_anon_voter_cannot_vote_twice_on_same_product(self):
        anon_id = uuid.uuid4()
        Vote.objects.create(product=self.product, anon_id=anon_id, value=VoteValue.WORTH)
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Vote.objects.create(product=self.product, anon_id=anon_id, value=VoteValue.NOT_WORTH)

    def test_vote_requires_exactly_one_voter_not_none(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Vote.objects.create(product=self.product, value=VoteValue.WORTH)

    def test_vote_requires_exactly_one_voter_not_both(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                Vote.objects.create(
                    product=self.product,
                    user=self.voter,
                    anon_id=uuid.uuid4(),
                    value=VoteValue.WORTH,
                )
