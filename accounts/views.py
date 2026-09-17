from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import SignUpForm, UsernameChangeForm


def signup(request):
    if request.user.is_authenticated:
        return redirect("polls:home")

    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Aramıza hoş geldin, @{user.username}! 🎉")
            return redirect("polls:home")
    else:
        form = SignUpForm()

    return render(request, "accounts/signup.html", {"form": form})


@login_required
def profile(request):
    if request.method == "POST":
        form = UsernameChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Kullanıcı adın güncellendi.")
            return redirect("accounts:profile")
    else:
        form = UsernameChangeForm(instance=request.user)

    poll_count = request.user.polls.count()
    return render(request, "accounts/profile.html", {"form": form, "poll_count": poll_count})
