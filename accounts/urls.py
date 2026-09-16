from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from . import views
from .forms import EmailLoginForm

app_name = "accounts"

urlpatterns = [
    path("kayit/", views.signup, name="signup"),
    path(
        "giris/",
        LoginView.as_view(
            template_name="accounts/login.html",
            authentication_form=EmailLoginForm,
            redirect_authenticated_user=True,
        ),
        name="login",
    ),
    path("cikis/", LogoutView.as_view(), name="logout"),
]
