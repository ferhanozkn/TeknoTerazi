"""Read/vote JSON endpoints for the experimental React frontend (see
.claude/skills/frontend-redesign/SKILL.md). Deliberately plain Django views
(no DRF) — reuses the exact same query/service functions as the Django-
template views in views.py so the two frontends can't drift apart on
business rules.
"""

import json
from urllib.parse import urlencode

from django.core.paginator import Paginator
from django.db import IntegrityError, transaction
from django.db.models import Count, Max, Min, Q
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.translation import gettext as _
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from .forms import CommentForm, PollForm, ProductForm, ProductFormSet, ReportForm
from .models import (
    BudgetTier,
    Category,
    Comment,
    Poll,
    Product,
    Report,
    ReportReason,
    UsagePurpose,
    Vote,
    VoteValue,
)
from .services import (
    VoteError,
    cast_vote,
    get_favorite_product,
    get_poll_with_stats,
    get_trending_polls,
    record_poll_view,
)
from .storage import ImageUploadError, upload_product_image
from .voter import attach_voter_cookie, get_client_ip, get_voter, hash_ip


def _poll_summary(poll):
    products = list(poll.products.all())
    return {
        "id": poll.pk,
        "title": poll.title,
        "category": poll.category,
        "usage_purpose": poll.usage_purpose or None,
        "budget_tier": poll.budget_tier or None,
        "author_username": poll.author.username,
        "created_at": poll.created_at.isoformat(),
        "expires_at": poll.expires_at.isoformat() if poll.expires_at else None,
        "is_active": poll.is_active,
        "is_expired": poll.is_expired,
        "total_votes": poll.total_votes,
        "today_votes": getattr(poll, "today_votes", 0),
        "min_price": float(poll.min_price) if getattr(poll, "min_price", None) is not None else None,
        "max_price": float(poll.max_price) if getattr(poll, "max_price", None) is not None else None,
        "product_names": [p.name for p in products],
        "product_count": len(products),
    }


@require_GET
def poll_list(request):
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

    selected_usage_purpose = request.GET.get("amac", "")
    if selected_usage_purpose:
        polls = polls.filter(usage_purpose=selected_usage_purpose)

    selected_budget_tier = request.GET.get("butce", "")
    if selected_budget_tier:
        polls = polls.filter(budget_tier=selected_budget_tier)

    status = request.GET.get("durum", "")
    if status == "acik":
        polls = polls.filter(is_active=True).exclude(expires_at__lte=timezone.now())

    sort = request.GET.get("sirala", "yeni")
    if sort == "populer":
        polls = polls.order_by("-total_votes", "-created_at")
    else:
        polls = polls.order_by("-created_at")

    paginator = Paginator(polls, 12)
    page_obj = paginator.get_page(request.GET.get("sayfa"))

    querystring_params = request.GET.copy()
    querystring_params.pop("sayfa", None)

    return JsonResponse(
        {
            "results": [_poll_summary(poll) for poll in page_obj],
            "count": paginator.count,
            "num_pages": paginator.num_pages,
            "current_page": page_obj.number,
            "has_next": page_obj.has_next(),
            "has_previous": page_obj.has_previous(),
            "querystring_prefix": urlencode(querystring_params) + "&" if querystring_params else "",
            "filters": {
                "categories": list(Category.choices),
                "usage_purposes": list(UsagePurpose.choices),
                "budget_tiers": list(BudgetTier.choices),
            },
        }
    )


@require_GET
def trending_polls(request):
    return JsonResponse({"results": [_poll_summary(poll) for poll in get_trending_polls()]})


@require_GET
def poll_detail(request, pk):
    poll = get_poll_with_stats(pk)
    record_poll_view(poll)
    products = list(poll.products.all())

    favorite_product = get_favorite_product(products)
    cheapest_product = min(products, key=lambda p: p.price) if products else None

    user, anon_id, is_new_anon = get_voter(request)
    user_votes = {}
    if products:
        vote_lookup = {"product__poll_id": poll.pk}
        vote_lookup.update({"user": user} if user is not None else {"anon_id": anon_id})
        user_votes = {
            v.product_id: "worth" if v.value == VoteValue.WORTH else "not_worth"
            for v in Vote.objects.filter(**vote_lookup).only("product_id", "value")
        }

    is_owner = user is not None and user.pk == poll.author_id
    can_vote = poll.is_active and not poll.is_expired and not is_owner
    hide_until_vote_active = poll.hide_results_until_vote and can_vote

    attribute_keys = []
    seen_keys = set()
    product_payloads = []
    for product in products:
        user_vote = user_votes.get(product.pk)
        show_results = user_vote is not None if hide_until_vote_active else True
        for key in product.attributes_dict:
            if key not in seen_keys:
                seen_keys.add(key)
                attribute_keys.append(key)
        product_payloads.append(
            {
                "id": product.pk,
                "name": product.name,
                "price": float(product.price),
                "currency": product.currency,
                "image_url": product.image_url or None,
                "product_url": product.product_url or None,
                "features": product.features_list,
                "attributes": product.attributes_dict,
                "worth_count": product.worth_count,
                "not_worth_count": product.not_worth_count,
                "worth_ratio": product.worth_ratio,
                "user_vote": user_vote,
                "show_results": show_results,
                "is_cheapest": product == cheapest_product,
                "is_favorite": product == favorite_product,
                "comments": [
                    {
                        "id": comment.pk,
                        "body": comment.body,
                        "author_username": comment.author.username,
                        "created_at": comment.created_at.isoformat(),
                        "can_delete": user is not None and comment.author_id == user.pk,
                    }
                    for comment in product.comments.select_related("author").order_by("-created_at")
                ],
            }
        )

    # response must reflect a signed anon-voter cookie for a first-time visitor
    response = JsonResponse(
        {
            "id": poll.pk,
            "title": poll.title,
            "description": poll.description or None,
            "category": poll.category,
            "usage_purpose": poll.usage_purpose or None,
            "budget_tier": poll.budget_tier or None,
            "author_username": poll.author.username,
            "is_owner": is_owner,
            "created_at": poll.created_at.isoformat(),
            "expires_at": poll.expires_at.isoformat() if poll.expires_at else None,
            "is_active": poll.is_active,
            "is_expired": poll.is_expired,
            "hide_results_until_vote": poll.hide_results_until_vote,
            "view_count": poll.view_count,
            "total_votes": poll.total_votes,
            "can_vote": can_vote,
            "poll_has_votes": poll.total_votes > 0,
            "attribute_keys": attribute_keys,
            "products": product_payloads,
        }
    )
    if user is None and is_new_anon:
        attach_voter_cookie(response, anon_id)
    return response


@require_GET
def csrf(request):
    """Forces Django to set the csrftoken cookie so the Next.js app can read it
    before its first POST (mirrors what a rendered {% csrf_token %} form does).
    """
    return JsonResponse({"csrf_token": get_token(request)})


@require_POST
def vote(request, pk):
    product = get_object_or_404(Product.objects.select_related("poll"), pk=pk)

    value_map = {"worth": VoteValue.WORTH, "not_worth": VoteValue.NOT_WORTH}
    value = value_map.get(request.POST.get("value"))
    if value is None:
        try:
            body = json.loads(request.body or b"{}")
        except ValueError:
            body = {}
        value = value_map.get(body.get("value"))
    if value is None:
        return JsonResponse({"error": _("Geçersiz oy değeri.")}, status=400)

    user, anon_id, is_new_anon = get_voter(request)
    ip_hash = hash_ip(get_client_ip(request)) if user is None else ""

    try:
        result = cast_vote(product, user, anon_id, value, ip_hash=ip_hash)
    except VoteError as exc:
        return JsonResponse({"error": exc.message}, status=exc.status)

    response = JsonResponse(result)
    if user is None and is_new_anon:
        attach_voter_cookie(response, anon_id)
    return response


def _unauthenticated():
    return JsonResponse({"error": _("Bu işlem için giriş yapmalısın.")}, status=401)


def _conversion_rate(poll):
    if not poll.view_count:
        return None
    return round(poll.total_votes / poll.view_count * 100)


def _form_errors(form):
    return {field: [str(e) for e in errors] for field, errors in form.errors.items()}


@require_POST
def poll_create(request):
    if not request.user.is_authenticated:
        return _unauthenticated()

    poll_form = PollForm(request.POST)
    product_formset = ProductFormSet(request.POST, request.FILES, prefix="products")

    if not (poll_form.is_valid() and product_formset.is_valid()):
        return JsonResponse(
            {
                "poll_errors": _form_errors(poll_form),
                "product_errors": [_form_errors(form) for form in product_formset.forms],
                "non_form_errors": list(product_formset.non_form_errors()),
            },
            status=400,
        )

    image_urls = []
    upload_errors = {}
    for index, form in enumerate(product_formset.forms):
        image_file = form.cleaned_data.get("image")
        if not image_file:
            image_urls.append(None)
            continue
        try:
            image_urls.append(upload_product_image(image_file))
        except ImageUploadError as exc:
            upload_errors[index] = exc.message
            image_urls.append(None)

    if upload_errors:
        return JsonResponse({"product_upload_errors": upload_errors}, status=400)

    with transaction.atomic():
        poll = poll_form.save(commit=False)
        poll.author = request.user
        poll.save()
        products = product_formset.save(commit=False)
        for position, (product, image_url) in enumerate(zip(products, image_urls)):
            product.poll = poll
            product.position = position
            if image_url:
                product.image_url = image_url
            product.save()

    return JsonResponse({"id": poll.pk}, status=201)


@require_http_methods(["GET", "POST"])
def poll_edit(request, pk):
    if not request.user.is_authenticated:
        return _unauthenticated()

    poll = get_object_or_404(
        Poll.objects.annotate(vote_count=Count("products__votes")),
        pk=pk,
        author=request.user,
    )
    if poll.vote_count > 0:
        return JsonResponse({"error": _("Bu anket oy almış, artık düzenlenemez.")}, status=403)

    products = list(poll.products.all())

    if request.method == "GET":
        return JsonResponse(
            {
                "id": poll.pk,
                "title": poll.title,
                "category": poll.category,
                "description": poll.description,
                "usage_purpose": poll.usage_purpose or None,
                "budget_tier": poll.budget_tier or None,
                "hide_results_until_vote": poll.hide_results_until_vote,
                "expires_at": poll.expires_at.isoformat() if poll.expires_at else None,
                "products": [
                    {
                        "id": product.pk,
                        "name": product.name,
                        "price": float(product.price),
                        "features": product.features,
                        "attributes": product.attributes,
                        "product_url": product.product_url,
                        "image_url": product.image_url,
                    }
                    for product in products
                ],
            }
        )

    poll_form = PollForm(request.POST, instance=poll)
    product_forms = [
        ProductForm(request.POST, request.FILES, instance=product, prefix=f"products-{product.pk}")
        for product in products
    ]
    forms_valid = poll_form.is_valid()
    for form in product_forms:
        forms_valid = form.is_valid() and forms_valid

    non_form_errors = []
    if forms_valid:
        names = [form.cleaned_data["name"].strip().lower() for form in product_forms]
        if len(names) != len(set(names)):
            forms_valid = False
            non_form_errors.append(_("Aynı ürünü iki kez ekleyemezsin."))

    if not forms_valid:
        return JsonResponse(
            {
                "poll_errors": _form_errors(poll_form),
                "product_errors": {form.instance.pk: _form_errors(form) for form in product_forms},
                "non_form_errors": non_form_errors,
            },
            status=400,
        )

    image_urls = {}
    upload_errors = {}
    for form in product_forms:
        image_file = form.cleaned_data.get("image")
        if not image_file:
            continue
        try:
            image_urls[form.instance.pk] = upload_product_image(image_file)
        except ImageUploadError as exc:
            upload_errors[form.instance.pk] = exc.message

    if upload_errors:
        return JsonResponse({"product_upload_errors": upload_errors}, status=400)

    with transaction.atomic():
        poll_form.save()
        for form in product_forms:
            product = form.save(commit=False)
            if product.pk in image_urls:
                product.image_url = image_urls[product.pk]
            product.save()

    return JsonResponse({"id": poll.pk})


@require_GET
def my_polls(request):
    if not request.user.is_authenticated:
        return _unauthenticated()

    polls = (
        request.user.polls.prefetch_related("products")
        .annotate(total_votes=Count("products__votes", distinct=True))
        .order_by("-created_at")
    )
    return JsonResponse(
        {
            "results": [
                {
                    "id": poll.pk,
                    "title": poll.title,
                    "total_votes": poll.total_votes,
                    "view_count": poll.view_count,
                    "conversion_rate": _conversion_rate(poll),
                    "is_active": poll.is_active,
                }
                for poll in polls
            ]
        }
    )


@require_POST
def poll_toggle_active(request, pk):
    if not request.user.is_authenticated:
        return _unauthenticated()
    poll = get_object_or_404(Poll, pk=pk, author=request.user)
    poll.is_active = not poll.is_active
    poll.save(update_fields=["is_active"])
    return JsonResponse({"id": poll.pk, "is_active": poll.is_active})


@require_POST
def poll_delete(request, pk):
    if not request.user.is_authenticated:
        return _unauthenticated()
    poll = get_object_or_404(Poll, pk=pk, author=request.user)
    poll.delete()
    return JsonResponse({"ok": True})


@require_POST
def comment_add(request, pk):
    if not request.user.is_authenticated:
        return _unauthenticated()
    product = get_object_or_404(Product.objects.select_related("poll"), pk=pk)
    body = json.loads(request.body or b"{}")
    form = CommentForm(body)
    if not form.is_valid():
        return JsonResponse({"errors": _form_errors(form)}, status=400)
    comment = form.save(commit=False)
    comment.product = product
    comment.author = request.user
    comment.save()
    return JsonResponse(
        {
            "id": comment.pk,
            "body": comment.body,
            "author_username": comment.author.username,
            "created_at": comment.created_at.isoformat(),
            "can_delete": True,
        },
        status=201,
    )


@require_POST
def comment_delete(request, pk):
    if not request.user.is_authenticated:
        return _unauthenticated()
    comment = get_object_or_404(Comment, pk=pk, author=request.user)
    comment.delete()
    return JsonResponse({"ok": True})


@require_GET
def report_reasons(request):
    return JsonResponse({"reasons": list(ReportReason.choices)})


@require_POST
def report_poll(request, pk):
    if not request.user.is_authenticated:
        return _unauthenticated()
    poll = get_object_or_404(Poll, pk=pk)

    if Report.objects.filter(poll=poll, reporter=request.user).exists():
        return JsonResponse({"error": _("Bu anketi zaten şikayet ettin.")}, status=400)

    body = json.loads(request.body or b"{}")
    form = ReportForm(body)
    if not form.is_valid():
        return JsonResponse({"errors": _form_errors(form)}, status=400)

    try:
        with transaction.atomic():
            report = form.save(commit=False)
            report.poll = poll
            report.reporter = request.user
            report.save()
    except IntegrityError:
        return JsonResponse({"error": _("Bu anketi zaten şikayet ettin.")}, status=400)

    return JsonResponse({"ok": True}, status=201)
