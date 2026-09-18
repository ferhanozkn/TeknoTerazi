from django.urls import path

from . import api

app_name = "polls_api"

urlpatterns = [
    path("csrf/", api.csrf, name="csrf"),
    path("polls/", api.poll_list, name="poll_list"),
    path("polls/trending/", api.trending_polls, name="trending_polls"),
    path("polls/<int:pk>/", api.poll_detail, name="poll_detail"),
    path("products/<int:pk>/vote/", api.vote, name="vote"),
]
