from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from polls.models import Poll, Report

User = get_user_model()


def make_poll(author, **overrides):
    return Poll.objects.create(author=author, title="Hangi telefonu almalıyım?", category="phone", **overrides)


class ReportPollViewTests(TestCase):
    def setUp(self):
        self.author = User.objects.create_user(username="ahmet", email="ahmet@example.com", password="x")
        self.poll = make_poll(self.author)
        self.report_url = reverse("polls:report_poll", kwargs={"pk": self.poll.pk})

    def test_guest_is_redirected_to_login(self):
        response = self.client.get(self.report_url)
        self.assertRedirects(response, f"{reverse('accounts:login')}?next={self.report_url}")
        self.assertEqual(Report.objects.count(), 0)

    def test_member_can_submit_report(self):
        reporter = User.objects.create_user(username="ece", email="ece@example.com", password="x")
        self.client.force_login(reporter)

        response = self.client.post(self.report_url, {"reason": "spam", "detail": "Bu bir reklam gibi duruyor."})

        self.assertRedirects(response, reverse("polls:poll_detail", kwargs={"pk": self.poll.pk}))
        self.assertEqual(Report.objects.count(), 1)
        report = Report.objects.get()
        self.assertEqual(report.reporter, reporter)
        self.assertEqual(report.poll, self.poll)
        self.assertEqual(report.status, "pending")

    def test_detail_is_optional(self):
        reporter = User.objects.create_user(username="ece", email="ece@example.com", password="x")
        self.client.force_login(reporter)
        response = self.client.post(self.report_url, {"reason": "spam", "detail": ""})
        self.assertEqual(Report.objects.count(), 1)
        self.assertEqual(response.status_code, 302)

    def test_missing_reason_is_rejected(self):
        reporter = User.objects.create_user(username="ece", email="ece@example.com", password="x")
        self.client.force_login(reporter)
        self.client.post(self.report_url, {"reason": "", "detail": ""})
        self.assertEqual(Report.objects.count(), 0)

    def test_cannot_report_same_poll_twice(self):
        reporter = User.objects.create_user(username="ece", email="ece@example.com", password="x")
        self.client.force_login(reporter)
        self.client.post(self.report_url, {"reason": "spam", "detail": ""})

        response = self.client.get(self.report_url)

        self.assertRedirects(response, reverse("polls:poll_detail", kwargs={"pk": self.poll.pk}))
        self.assertEqual(Report.objects.count(), 1)

    def test_two_different_users_can_both_report(self):
        reporter1 = User.objects.create_user(username="ece", email="ece@example.com", password="x")
        reporter2 = User.objects.create_user(username="mert", email="mert@example.com", password="x")

        self.client.force_login(reporter1)
        self.client.post(self.report_url, {"reason": "spam", "detail": ""})
        self.client.force_login(reporter2)
        self.client.post(self.report_url, {"reason": "misleading", "detail": ""})

        self.assertEqual(Report.objects.count(), 2)

    def test_author_can_report_own_poll(self):
        self.client.force_login(self.author)
        response = self.client.post(self.report_url, {"reason": "other", "detail": ""})
        self.assertEqual(Report.objects.count(), 1)
        self.assertEqual(response.status_code, 302)
