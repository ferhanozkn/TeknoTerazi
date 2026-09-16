from urllib.parse import urlencode

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Count, Max, Min, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import PollForm, ProductFormSet
from .models import Category, Poll
from .services import get_favorite_product, get_poll_with_stats


def home(request):
    polls = (
        Poll.objects.select_related("author")
        .prefetch_related("products")
        .annotate(
            total_votes=Count("products__votes", distinct=True),
            min_price=Min("products__price"),
            max_price=Max("products__price"),
        )
    )

    query = request.GET.get("q", "").strip()
    if query:
        polls = polls.filter(Q(title__icontains=query) | Q(products__name__icontains=query)).distinct()

    selected_category = request.GET.get("kategori", "")
    if selected_category:
        polls = polls.filter(category=selected_category)

    status = request.GET.get("durum", "")
    if status == "acik":
        polls = polls.filter(is_active=True)

    sort = request.GET.get("sirala", "yeni")
    if sort == "populer":
        polls = polls.order_by("-total_votes", "-created_at")
    else:
        polls = polls.order_by("-created_at")

    paginator = Paginator(polls, 12)
    page_obj = paginator.get_page(request.GET.get("sayfa"))

    querystring_params = request.GET.copy()
    querystring_params.pop("sayfa", None)
    querystring_prefix = urlencode(querystring_params) + "&" if querystring_params else ""

    context = {
        "page_obj": page_obj,
        "categories": Category.choices,
        "query": query,
        "selected_category": selected_category,
        "sort": sort,
        "status": status,
        "querystring_prefix": querystring_prefix,
    }
    return render(request, "polls/home.html", context)


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
    poll = get_poll_with_stats(pk)
    products = list(poll.products.all())
    favorite_product = get_favorite_product(products)
    cheapest_product = min(products, key=lambda p: p.price) if products else None
    return render(
        request,
        "polls/poll_detail.html",
        {
            "poll": poll,
            "products": products,
            "favorite_product": favorite_product,
            "cheapest_product": cheapest_product,
        },
    )


@login_required
@require_POST
def poll_toggle_active(request, pk):
    poll = get_object_or_404(Poll, pk=pk, author=request.user)
    poll.is_active = not poll.is_active
    poll.save(update_fields=["is_active"])
    return redirect("polls:my_polls")


@login_required
def poll_delete(request, pk):
    poll = get_object_or_404(Poll, pk=pk, author=request.user)
    if request.method == "POST":
        poll.delete()
        messages.success(request, "Anket silindi.")
        return redirect("polls:my_polls")
    return render(request, "polls/poll_confirm_delete.html", {"poll": poll})


@login_required
def my_polls(request):
    polls = (
        request.user.polls.prefetch_related("products")
        .annotate(total_votes=Count("products__votes", distinct=True))
        .order_by("-created_at")
    )
    return render(request, "polls/my_polls.html", {"polls": polls})
