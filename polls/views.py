from urllib.parse import urlencode

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import transaction
from django.db.models import Count, Max, Min, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from .forms import CommentForm, PollForm, ProductFormSet
from .models import Category, Comment, Poll, Product, Vote, VoteValue
from .services import VoteError, cast_vote, get_favorite_product, get_poll_with_stats
from .voter import attach_voter_cookie, get_client_ip, get_voter, hash_ip


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
    for product in products:
        product.comment_list = list(
            product.comments.select_related("author").order_by("-created_at")
        )
    favorite_product = get_favorite_product(products)
    cheapest_product = min(products, key=lambda p: p.price) if products else None

    user, anon_id, _ = get_voter(request)
    if products:
        vote_lookup = {"product__poll_id": poll.pk}
        vote_lookup.update({"user": user} if user is not None else {"anon_id": anon_id})
        user_votes = {
            v.product_id: "worth" if v.value == VoteValue.WORTH else "not_worth"
            for v in Vote.objects.filter(**vote_lookup).only("product_id", "value")
        }
        for product in products:
            product.user_vote = user_votes.get(product.pk)

    can_vote = poll.is_active and not (user is not None and user.pk == poll.author_id)

    return render(
        request,
        "polls/poll_detail.html",
        {
            "poll": poll,
            "products": products,
            "favorite_product": favorite_product,
            "cheapest_product": cheapest_product,
            "can_vote": can_vote,
            "comment_form": CommentForm(auto_id=False),
        },
    )


@login_required
@require_POST
def comment_add(request, pk):
    product = get_object_or_404(Product.objects.select_related("poll"), pk=pk)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.product = product
        comment.author = request.user
        comment.save()
        messages.success(request, "Yorumun eklendi.")
    else:
        for error in form.errors.get("body", []):
            messages.error(request, error)
    return redirect(f"{reverse('polls:poll_detail', args=[product.poll_id])}#urun-{product.pk}")


@login_required
@require_POST
def comment_delete(request, pk):
    comment = get_object_or_404(Comment, pk=pk, author=request.user)
    product_id = comment.product_id
    poll_id = comment.product.poll_id
    comment.delete()
    messages.success(request, "Yorumun silindi.")
    return redirect(f"{reverse('polls:poll_detail', args=[poll_id])}#urun-{product_id}")


@require_POST
def vote(request, pk):
    product = get_object_or_404(Product.objects.select_related("poll"), pk=pk)
    is_ajax = request.headers.get("x-requested-with") == "XMLHttpRequest"

    value_map = {"worth": VoteValue.WORTH, "not_worth": VoteValue.NOT_WORTH}
    value = value_map.get(request.POST.get("value"))
    if value is None:
        if is_ajax:
            return JsonResponse({"error": "Geçersiz oy değeri."}, status=400)
        messages.error(request, "Geçersiz oy değeri.")
        return redirect("polls:poll_detail", pk=product.poll_id)

    user, anon_id, is_new_anon = get_voter(request)
    ip_hash = hash_ip(get_client_ip(request)) if user is None else ""

    try:
        result = cast_vote(product, user, anon_id, value, ip_hash=ip_hash)
    except VoteError as exc:
        if is_ajax:
            return JsonResponse({"error": exc.message}, status=exc.status)
        messages.error(request, exc.message)
        return redirect("polls:poll_detail", pk=product.poll_id)

    if is_ajax:
        response = JsonResponse(result)
    else:
        response = redirect("polls:poll_detail", pk=product.poll_id)

    if user is None and is_new_anon:
        attach_voter_cookie(response, anon_id)

    return response


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
