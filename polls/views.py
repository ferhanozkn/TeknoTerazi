from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PollForm, ProductFormSet
from .models import Poll


def home(request):
    return render(request, "polls/home.html")


@login_required
def poll_create(request):
    if request.method == "POST":
        poll_form = PollForm(request.POST)
        product_formset = ProductFormSet(request.POST, prefix="products")
        if poll_form.is_valid() and product_formset.is_valid():
            with transaction.atomic():
                poll = poll_form.save(commit=False)
                poll.author = request.user
                poll.save()
                products = product_formset.save(commit=False)
                for position, product in enumerate(products):
                    product.poll = poll
                    product.position = position
                    product.save()
            messages.success(
                request,
                "Anketin yayında! 🎉 Linki paylaşarak daha çok oy toplayabilirsin.",
            )
            return redirect("polls:poll_detail", pk=poll.pk)
    else:
        poll_form = PollForm()
        product_formset = ProductFormSet(prefix="products")

    return render(
        request,
        "polls/poll_create.html",
        {"poll_form": poll_form, "product_formset": product_formset},
    )


def poll_detail(request, pk):
    poll = get_object_or_404(Poll, pk=pk)
    return render(request, "polls/poll_detail.html", {"poll": poll})


@login_required
def my_polls(request):
    return render(request, "polls/my_polls.html")
