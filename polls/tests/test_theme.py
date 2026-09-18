from django.test import TestCase
from django.urls import reverse


class ThemeToggleTests(TestCase):
    def test_home_page_includes_theme_toggle_button(self):
        response = self.client.get(reverse("polls:home"))
        self.assertContains(response, 'id="theme-toggle"')

    def test_home_page_loads_theme_script(self):
        response = self.client.get(reverse("polls:home"))
        self.assertContains(response, "js/theme.js")

    def test_home_page_has_fouc_prevention_script(self):
        response = self.client.get(reverse("polls:home"))
        self.assertContains(response, "tt_theme")
