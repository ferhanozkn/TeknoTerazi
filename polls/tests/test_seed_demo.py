from django.core.management import call_command
from django.test import TestCase

from accounts.models import CustomUser
from polls.models import Poll


class SeedDemoCommandTests(TestCase):
    def test_seed_creates_demo_users_and_polls(self):
        call_command("seed_demo")
        self.assertEqual(CustomUser.objects.filter(username__startswith="demo_").count(), 3)
        demo_polls = Poll.objects.filter(author__username__startswith="demo_")
        self.assertGreaterEqual(demo_polls.count(), 8)
        for poll in demo_polls:
            self.assertGreaterEqual(poll.products.count(), 2)

    def test_seed_is_idempotent(self):
        call_command("seed_demo")
        first_count = Poll.objects.filter(author__username__startswith="demo_").count()
        call_command("seed_demo")
        second_count = Poll.objects.filter(author__username__startswith="demo_").count()
        self.assertEqual(first_count, second_count)

    def test_flush_removes_only_demo_data(self):
        real_author = CustomUser.objects.create_user(
            username="gercek", email="gercek@example.com", password="x"
        )
        real_poll = Poll.objects.create(title="Gerçek anket", author=real_author, category="phone")

        call_command("seed_demo")
        call_command("seed_demo", "--flush")

        self.assertEqual(CustomUser.objects.filter(username__startswith="demo_").count(), 0)
        self.assertEqual(Poll.objects.filter(author__username__startswith="demo_").count(), 0)
        self.assertTrue(Poll.objects.filter(pk=real_poll.pk).exists())
