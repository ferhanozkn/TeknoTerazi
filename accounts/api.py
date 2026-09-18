"""Auth JSON endpoints for the experimental React frontend (see
.claude/skills/frontend-redesign/SKILL.md). Reuses the same forms Django's
own login/signup views use, so validation and the turnstile/username-email
rules never drift between the two frontends.
"""

import json

from django.contrib.auth import login, logout
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST

from .forms import EmailLoginForm, SignUpForm, UsernameChangeForm
from .turnstile import verify_turnstile_token


def _unauthenticated():
    return JsonResponse({"error": "Bu işlem için giriş yapmalısın."}, status=401)


def _user_payload(request):
    if request.user.is_authenticated:
        return {"authenticated": True, "username": request.user.username}
    return {"authenticated": False, "username": None}


@require_GET
def me(request):
    return JsonResponse(_user_payload(request))


def _form_errors(form):
    return {field: [str(e) for e in errors] for field, errors in form.errors.items()}


@require_POST
def signup(request):
    body = json.loads(request.body or b"{}")
    form = SignUpForm(
        {
            "username": body.get("username", ""),
            "email": body.get("email", ""),
            "password1": body.get("password1", ""),
            "password2": body.get("password2", ""),
        }
    )
    form_valid = form.is_valid()
    turnstile_ok = verify_turnstile_token(body.get("turnstile_token"))
    if not turnstile_ok:
        form.add_error(None, "Bot koruması doğrulanamadı. Lütfen tekrar dene.")

    if not (form_valid and turnstile_ok):
        return JsonResponse({"errors": _form_errors(form)}, status=400)

    user = form.save()
    login(request, user, backend="django.contrib.auth.backends.ModelBackend")
    return JsonResponse(_user_payload(request), status=201)


@require_POST
def login_view(request):
    body = json.loads(request.body or b"{}")
    form = EmailLoginForm(
        request, data={"username": body.get("email", ""), "password": body.get("password", "")}
    )
    if not form.is_valid():
        return JsonResponse({"errors": _form_errors(form)}, status=400)

    login(request, form.get_user())
    return JsonResponse(_user_payload(request))


@require_POST
def logout_view(request):
    logout(request)
    return JsonResponse(_user_payload(request))


@require_GET
def profile(request):
    if not request.user.is_authenticated:
        return _unauthenticated()
    user = request.user
    return JsonResponse(
        {
            "username": user.username,
            "email": user.email,
            "date_joined": user.date_joined.isoformat(),
            "poll_count": user.polls.count(),
        }
    )


@require_POST
def update_username(request):
    if not request.user.is_authenticated:
        return _unauthenticated()
    body = json.loads(request.body or b"{}")
    form = UsernameChangeForm({"username": body.get("username", "")}, instance=request.user)
    if not form.is_valid():
        return JsonResponse({"errors": _form_errors(form)}, status=400)
    form.save()
    return JsonResponse({"username": request.user.username})
