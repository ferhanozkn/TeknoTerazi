from datetime import timedelta

from django.db import IntegrityError, transaction
from django.db.models import Count, Max, Min, Prefetch, Q
from django.shortcuts import get_object_or_404
from django.utils import timezone

from .models import Poll, Product, Vote, VoteAttempt, VoteValue

VOTE_RATE_LIMIT = 60
VOTE_RATE_WINDOW = timedelta(minutes=1)
TRENDING_POLL_LIMIT = 5


class VoteError(Exception):
    def __init__(self, status, message):
        self.status = status
        self.message = message
        super().__init__(message)


def get_poll_with_stats(pk):
    products_qs = Product.objects.annotate(
        worth_count=Count("votes", filter=Q(votes__value=1)),
        not_worth_count=Count("votes", filter=Q(votes__value=-1)),
    ).order_by("position")
    return get_object_or_404(
        Poll.objects.select_related("author").prefetch_related(
            Prefetch("products", queryset=products_qs)
        ),
        pk=pk,
    )


def get_trending_polls(limit=TRENDING_POLL_LIMIT):
    """Bugün (yerel saatle) en çok oy alan açık anketler."""
    start_of_today = timezone.localtime().replace(hour=0, minute=0, second=0, microsecond=0)
    return (
        Poll.objects.filter(is_active=True)
        .select_related("author")
        .prefetch_related("products")
        .annotate(
            today_votes=Count(
                "products__votes",
                filter=Q(products__votes__created_at__gte=start_of_today),
                distinct=True,
            ),
            total_votes=Count("products__votes", distinct=True),
            min_price=Min("products__price"),
            max_price=Max("products__price"),
        )
        .filter(today_votes__gt=0)
        .order_by("-today_votes", "-created_at")[:limit]
    )


def get_favorite_product(products, min_votes=3):
    eligible = [p for p in products if p.total_votes >= min_votes]
    if not eligible:
        return None
    eligible.sort(key=lambda p: (-p.worth_ratio, -p.total_votes))
    best = eligible[0]
    tied = [
        p
        for p in eligible
        if p.worth_ratio == best.worth_ratio and p.total_votes == best.total_votes
    ]
    if len(tied) > 1:
        return None
    return best


def enforce_vote_rate_limit(user, anon_id):
    voter_lookup = {"user": user} if user is not None else {"anon_id": anon_id}
    window_start = timezone.now() - VOTE_RATE_WINDOW
    recent_count = VoteAttempt.objects.filter(created_at__gte=window_start, **voter_lookup).count()
    if recent_count >= VOTE_RATE_LIMIT:
        raise VoteError(429, "Çok fazla oy isteği gönderdin. Lütfen biraz bekle.")
    VoteAttempt.objects.create(**voter_lookup)


def cast_vote(product, user, anon_id, value, ip_hash=""):
    enforce_vote_rate_limit(user, anon_id)

    poll = product.poll

    if not poll.is_active:
        raise VoteError(403, "Bu anket oylamaya kapalı.")

    if user is not None and user.pk == poll.author_id:
        raise VoteError(403, "Kendi anketine oy veremezsin.")

    lookup = {"product": product}
    if user is not None:
        lookup["user"] = user
    else:
        lookup["anon_id"] = anon_id

    def apply_vote():
        with transaction.atomic():
            existing = Vote.objects.select_for_update().filter(**lookup).first()
            if existing is None:
                if user is None and ip_hash:
                    already_voted_from_ip = (
                        Vote.objects.filter(product=product, ip_hash=ip_hash)
                        .exclude(anon_id=anon_id)
                        .exists()
                    )
                    if already_voted_from_ip:
                        raise VoteError(403, "Bu IP adresinden bu ürüne zaten oy verilmiş.")
                Vote.objects.create(value=value, ip_hash=ip_hash, **lookup)
            elif existing.value == value:
                existing.delete()
            else:
                existing.value = value
                existing.save(update_fields=["value"])

    try:
        apply_vote()
    except IntegrityError:
        apply_vote()

    return get_product_vote_stats(product, user, anon_id)


def merge_anon_votes_into_user(anon_id, user):
    """Girişte, o tarayıcının anon_id ile verdiği oyları kullanıcı hesabına taşır.

    Kullanıcının kendi anketine ait anonim oy (bkz. Karar Günlüğü #11) veya
    aynı üründe zaten mevcut bir üye oyu varsa, anonim oy sessizce silinir.
    """
    if anon_id is None:
        return

    anon_votes = Vote.objects.filter(anon_id=anon_id).select_related("product__poll")
    for vote in anon_votes:
        if vote.product.poll.author_id == user.pk:
            vote.delete()
            continue
        with transaction.atomic():
            existing = Vote.objects.select_for_update().filter(
                product=vote.product, user=user
            ).first()
            if existing is None:
                vote.user = user
                vote.anon_id = None
                vote.save(update_fields=["user", "anon_id"])
            else:
                vote.delete()


def get_product_vote_stats(product, user, anon_id):
    stats = (
        Product.objects.filter(pk=product.pk)
        .annotate(
            worth_count=Count("votes", filter=Q(votes__value=1)),
            not_worth_count=Count("votes", filter=Q(votes__value=-1)),
        )
        .get()
    )

    lookup = {"product_id": product.pk}
    if user is not None:
        lookup["user"] = user
    else:
        lookup["anon_id"] = anon_id
    current_vote = Vote.objects.filter(**lookup).first()
    user_vote = None
    if current_vote is not None:
        user_vote = "worth" if current_vote.value == VoteValue.WORTH else "not_worth"

    return {
        "product_id": stats.pk,
        "user_vote": user_vote,
        "worth_count": stats.worth_count,
        "not_worth_count": stats.not_worth_count,
        "total_votes": stats.total_votes,
        "worth_ratio": stats.worth_ratio,
    }
