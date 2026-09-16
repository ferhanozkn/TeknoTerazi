from django.urls import path

from . import views

app_name = "polls"

urlpatterns = [
    path("", views.home, name="home"),
    path("anket/yeni/", views.poll_create, name="poll_create"),
    path("anket/<int:pk>/", views.poll_detail, name="poll_detail"),
    path("anketlerim/", views.my_polls, name="my_polls"),
]
