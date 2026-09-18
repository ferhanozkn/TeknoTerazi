from django.urls import path

from . import api

app_name = "polls_api"

urlpatterns = [
    path("csrf/", api.csrf, name="csrf"),
    path("polls/", api.poll_list, name="poll_list"),
    path("polls/trending/", api.trending_polls, name="trending_polls"),
    path("polls/<int:pk>/", api.poll_detail, name="poll_detail"),
    path("polls/<int:pk>/durum/", api.poll_toggle_active, name="poll_toggle_active"),
    path("polls/<int:pk>/sil/", api.poll_delete, name="poll_delete"),
    path("anketlerim/", api.my_polls, name="my_polls"),
    path("products/<int:pk>/vote/", api.vote, name="vote"),
]
