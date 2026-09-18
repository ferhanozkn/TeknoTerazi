from allauth.account.adapter import DefaultAccountAdapter
from allauth.core.exceptions import ImmediateHttpResponse
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib import messages
from django.shortcuts import redirect
from django.utils.translation import gettext as _

from .models import CustomUser


class AccountAdapter(DefaultAccountAdapter):
    def generate_unique_username(self, txts, regex=None):
        # CustomUser.username only allows [a-zA-Z0-9_]; allauth's default
        # regex keeps ".", "-", "+" which Google emails often contain.
        return super().generate_unique_username(txts, regex=r"[^\w]")


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        if sociallogin.is_existing:
            return
        email = sociallogin.user.email
        if email and CustomUser.objects.filter(email__iexact=email).exists():
            messages.info(
                request,
                _("Bu e-posta ile zaten bir hesabın var. E-posta ve parolanla giriş yap."),
            )
            raise ImmediateHttpResponse(redirect("accounts:login"))
