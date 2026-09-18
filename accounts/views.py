from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils.translation import gettext as _

from .forms import SignUpForm, UsernameChangeForm
from .turnstile import verify_turnstile_token


def signup(request):
    if request.user.is_authenticated:
        return redirect("polls:home")

    if request.method == "POST":
        form = SignUpForm(request.POST)
        form_valid = form.is_valid()
        turnstile_ok = verify_turnstile_token(request.POST.get("cf-turnstile-response"))
        if not turnstile_ok:
            form.add_error(None, _("Bot koruması doğrulanamadı. Lütfen tekrar dene."))
        if form_valid and turnstile_ok:
            user = form.save()
            login(request, user, backend="django.contrib.auth.backends.ModelBackend")
            messages.success(request, _("Aramıza hoş geldin, @%(username)s! 🎉") % {"username": user.username})
            return redirect("polls:home")
    else:
        form = SignUpForm()

    return render(
        request,
        "accounts/signup.html",
        {"form": form, "turnstile_site_key": settings.TURNSTILE_SITE_KEY},
    )


@login_required
def profile(request):
    if request.method == "POST":
        form = UsernameChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, _("Kullanıcı adın güncellendi."))
            return redirect("accounts:profile")
    else:
        form = UsernameChangeForm(instance=request.user)

    poll_count = request.user.polls.count()
    return render(request, "accounts/profile.html", {"form": form, "poll_count": poll_count})
