from allauth.core.exceptions import ImmediateHttpResponse
from allauth.socialaccount.models import SocialLogin
from django.contrib.messages.storage.fallback import FallbackStorage
from django.core.exceptions import ValidationError
from django.test import RequestFactory, TestCase
from django.urls import reverse

from accounts.adapters import AccountAdapter, SocialAccountAdapter
from accounts.models import CustomUser


class CustomUserTests(TestCase):
    def test_email_is_stored_lowercase(self):
        user = CustomUser.objects.create_user(
            username="ahmet", email="Ahmet@Example.COM", password="x"
        )
        self.assertEqual(user.email, "ahmet@example.com")

    def test_invalid_username_is_rejected(self):
        user = CustomUser(username="a b!", email="a@example.com")
        with self.assertRaises(ValidationError):
            user.full_clean()


VALID_SIGNUP_DATA = {
    "username": "ahmet",
    "email": "ahmet@example.com",
    "password1": "cok-guclu-parola-1",
    "password2": "cok-guclu-parola-1",
}


class SignUpViewTests(TestCase):
    def test_successful_signup_logs_user_in_and_redirects_home(self):
        response = self.client.post(reverse("accounts:signup"), VALID_SIGNUP_DATA)
        self.assertRedirects(response, reverse("polls:home"))
        self.assertIn("_auth_user_id", self.client.session)

    def test_duplicate_username_case_insensitive_is_rejected(self):
        CustomUser.objects.create_user(username="Ahmet", email="other@example.com", password="x")
        response = self.client.post(reverse("accounts:signup"), VALID_SIGNUP_DATA)
        self.assertContains(response, "Bu kullanıcı adı zaten kullanılıyor.")

    def test_duplicate_email_case_insensitive_is_rejected(self):
        CustomUser.objects.create_user(username="baska", email="Ahmet@Example.com", password="x")
        response = self.client.post(reverse("accounts:signup"), VALID_SIGNUP_DATA)
        self.assertContains(response, "Bu e-posta adresiyle zaten bir hesap var.")

    def test_password_mismatch_shows_turkish_message(self):
        data = {**VALID_SIGNUP_DATA, "password2": "farkli-bir-parola-2"}
        response = self.client.post(reverse("accounts:signup"), data)
        self.assertContains(response, "Parolalar eşleşmiyor.")

    def test_authenticated_user_redirected_away_from_signup(self):
        user = CustomUser.objects.create_user(username="ayse", email="ayse@example.com", password="x")
        self.client.force_login(user)
        response = self.client.get(reverse("accounts:signup"))
        self.assertRedirects(response, reverse("polls:home"))


class LoginViewTests(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="ahmet", email="ahmet@example.com", password="dogru-parola-1"
        )

    def test_successful_login_with_email(self):
        response = self.client.post(
            reverse("accounts:login"),
            {"username": "ahmet@example.com", "password": "dogru-parola-1"},
        )
        self.assertRedirects(response, reverse("polls:home"))

    def test_login_with_different_case_email_still_works(self):
        response = self.client.post(
            reverse("accounts:login"),
            {"username": "Ahmet@Example.com", "password": "dogru-parola-1"},
        )
        self.assertRedirects(response, reverse("polls:home"))

    def test_wrong_password_shows_generic_message(self):
        response = self.client.post(
            reverse("accounts:login"),
            {"username": "ahmet@example.com", "password": "yanlis-parola"},
        )
        self.assertContains(response, "E-posta veya parola hatalı.")

    def test_authenticated_user_redirected_away_from_login(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("accounts:login"))
        self.assertRedirects(response, reverse("polls:home"))


class ProfileViewTests(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="ahmet", email="ahmet@example.com", password="x"
        )

    def test_anonymous_user_redirected_to_login(self):
        response = self.client.get(reverse("accounts:profile"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("accounts:login"), response.url)

    def test_profile_shows_current_username_and_email(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("accounts:profile"))
        self.assertContains(response, "ahmet")
        self.assertContains(response, "ahmet@example.com")

    def test_username_can_be_changed(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse("accounts:profile"), {"username": "mehmet"})
        self.assertRedirects(response, reverse("accounts:profile"))
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, "mehmet")

    def test_duplicate_username_case_insensitive_is_rejected(self):
        CustomUser.objects.create_user(username="Mehmet", email="mehmet@example.com", password="x")
        self.client.force_login(self.user)
        response = self.client.post(reverse("accounts:profile"), {"username": "mehmet"})
        self.assertContains(response, "Bu kullanıcı adı zaten kullanılıyor.")
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, "ahmet")

    def test_keeping_same_username_is_not_rejected_as_duplicate(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse("accounts:profile"), {"username": "ahmet"})
        self.assertRedirects(response, reverse("accounts:profile"))


class GoogleLoginButtonTests(TestCase):
    def test_login_page_has_google_button(self):
        response = self.client.get(reverse("accounts:login"))
        self.assertContains(response, "Google ile giriş yap")

    def test_signup_page_has_google_button(self):
        response = self.client.get(reverse("accounts:signup"))
        self.assertContains(response, "Google ile kayıt ol")


class SocialAccountAdapterTests(TestCase):
    def _request(self):
        request = RequestFactory().get("/hesap/giris/")
        request.session = {}
        request._messages = FallbackStorage(request)
        return request

    def test_generate_unique_username_strips_disallowed_characters(self):
        adapter = AccountAdapter()
        username = adapter.generate_unique_username(["ahmet.yilmaz+test@example.com"])
        self.assertRegex(username, r"^[a-zA-Z0-9_]{3,30}$")

    def test_pre_social_login_redirects_when_email_already_registered(self):
        CustomUser.objects.create_user(username="ahmet", email="ahmet@example.com", password="x")
        adapter = SocialAccountAdapter()
        sociallogin = SocialLogin(user=CustomUser(email="Ahmet@Example.com"))
        request = self._request()
        with self.assertRaises(ImmediateHttpResponse) as ctx:
            adapter.pre_social_login(request, sociallogin)
        self.assertEqual(ctx.exception.response.status_code, 302)
        self.assertIn(reverse("accounts:login"), ctx.exception.response.url)

    def test_pre_social_login_allows_new_email(self):
        adapter = SocialAccountAdapter()
        sociallogin = SocialLogin(user=CustomUser(email="yeni@example.com"))
        request = self._request()
        adapter.pre_social_login(request, sociallogin)  # raises nothing


class LogoutViewTests(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(username="ahmet", email="ahmet@example.com", password="x")

    def test_logout_requires_post(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("accounts:logout"))
        self.assertEqual(response.status_code, 405)

    def test_logout_via_post_clears_session(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse("accounts:logout"))
        self.assertRedirects(response, reverse("polls:home"))
        self.assertNotIn("_auth_user_id", self.client.session)
