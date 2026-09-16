from django.db.models import Count, Prefetch, Q
from django.shortcuts import get_object_or_404

from .models import Poll, Product


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
