from django.contrib.auth.decorators import login_required
from django.shortcuts import render


def home(request):
    return render(request, "polls/home.html")


@login_required
def poll_create(request):
    return render(request, "polls/poll_create.html")


@login_required
def my_polls(request):
    return render(request, "polls/my_polls.html")
