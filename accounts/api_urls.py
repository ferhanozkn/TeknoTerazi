from django.urls import path

from . import api

app_name = "accounts_api"

urlpatterns = [
    path("me/", api.me, name="me"),
    path("signup/", api.signup, name="signup"),
    path("login/", api.login_view, name="login"),
    path("logout/", api.logout_view, name="logout"),
    path("profile/", api.profile, name="profile"),
    path("profile/username/", api.update_username, name="update_username"),
]
