from django.urls import path

from . import views

app_name = "polls"

urlpatterns = [
    path("", views.home, name="home"),
    path("anket/yeni/", views.poll_create, name="poll_create"),
    path("anket/<int:pk>/", views.poll_detail, name="poll_detail"),
    path("anket/<int:pk>/durum/", views.poll_toggle_active, name="poll_toggle_active"),
    path("anket/<int:pk>/sil/", views.poll_delete, name="poll_delete"),
    path("anket/<int:pk>/sikayet/", views.report_poll, name="report_poll"),
    path("urun/<int:pk>/oy/", views.vote, name="vote"),
    path("urun/<int:pk>/yorum/", views.comment_add, name="comment_add"),
    path("yorum/<int:pk>/sil/", views.comment_delete, name="comment_delete"),
    path("anketlerim/", views.my_polls, name="my_polls"),
]
