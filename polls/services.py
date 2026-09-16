from django.db import IntegrityError, transaction
from django.db.models import Count, Prefetch, Q
from django.shortcuts import get_object_or_404

from .models import Poll, Product, Vote, VoteValue


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


def cast_vote(product, user, anon_id, value):
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
                Vote.objects.create(value=value, **lookup)
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
