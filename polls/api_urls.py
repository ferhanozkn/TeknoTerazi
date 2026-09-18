from django.urls import path

from . import api

app_name = "polls_api"

urlpatterns = [
    path("csrf/", api.csrf, name="csrf"),
    path("polls/", api.poll_list, name="poll_list"),
    path("polls/yeni/", api.poll_create, name="poll_create"),
    path("polls/<int:pk>/duzenle/", api.poll_edit, name="poll_edit"),
    path("polls/trending/", api.trending_polls, name="trending_polls"),
    path("polls/<int:pk>/", api.poll_detail, name="poll_detail"),
    path("polls/<int:pk>/durum/", api.poll_toggle_active, name="poll_toggle_active"),
    path("polls/<int:pk>/sil/", api.poll_delete, name="poll_delete"),
    path("polls/<int:pk>/sikayet/", api.report_poll, name="report_poll"),
    path("anketlerim/", api.my_polls, name="my_polls"),
    path("report-reasons/", api.report_reasons, name="report_reasons"),
    path("products/<int:pk>/vote/", api.vote, name="vote"),
    path("products/<int:pk>/yorum/", api.comment_add, name="comment_add"),
    path("yorum/<int:pk>/sil/", api.comment_delete, name="comment_delete"),
]
