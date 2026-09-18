import json

from django.conf import settings
from django.test import TestCase
from django.urls import reverse


class PwaManifestTests(TestCase):
    def test_home_page_links_manifest_and_icons(self):
        response = self.client.get(reverse("polls:home"))
        self.assertContains(response, "manifest.webmanifest")
        self.assertContains(response, "apple-touch-icon.png")
        self.assertContains(response, 'name="theme-color"')

    def test_home_page_registers_service_worker(self):
        response = self.client.get(reverse("polls:home"))
        self.assertContains(response, "register_sw.js")

    def test_manifest_file_is_valid_json_with_required_fields(self):
        manifest_path = settings.BASE_DIR / "static" / "manifest.webmanifest"
        with open(manifest_path, encoding="utf-8") as f:
            data = json.load(f)
        self.assertEqual(data["name"], "TeknoTerazi")
        self.assertEqual(data["display"], "standalone")
        self.assertEqual(len(data["icons"]), 2)
