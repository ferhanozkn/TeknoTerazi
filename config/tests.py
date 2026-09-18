from django.test import TestCase
from django.urls import reverse


class ServiceWorkerViewTests(TestCase):
    def test_service_worker_is_served_with_correct_headers(self):
        response = self.client.get(reverse("service_worker"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/javascript")
        self.assertEqual(response["Service-Worker-Allowed"], "/")
        self.assertIn(b"addEventListener", response.content)
