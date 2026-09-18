from decimal import Decimal

from django.conf import settings
from django.core.validators import (
    MaxValueValidator,
    MinLengthValidator,
    MinValueValidator,
    URLValidator,
)
from django.db import models
from django.utils import timezone


class Category(models.TextChoices):
    PHONE = "phone", "Akıllı Telefon"
    LAPTOP = "laptop", "Dizüstü Bilgisayar"
    TABLET = "tablet", "Tablet"
    HEADPHONE = "headphone", "Kulaklık"
    SMARTWATCH = "smartwatch", "Akıllı Saat"
    GAMING = "gaming", "Oyun & Konsol"
    CAMERA = "camera", "Kamera"
    TV = "tv", "TV & Monitör"
    PC_PART = "pc_part", "Bilgisayar Parçası"
    OTHER = "other", "Diğer"


class VoteValue(models.IntegerChoices):
    WORTH = 1, "Buna değer"
    NOT_WORTH = -1, "Buna değmez"


class Poll(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="polls"
    )
    title = models.CharField(max_length=120, validators=[MinLengthValidator(5)])
    description = models.TextField(max_length=1000, blank=True)
    category = models.CharField(max_length=20, choices=Category.choices)
    is_active = models.BooleanField(default=True)
    hide_results_until_vote = models.BooleanField(default=False)
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    @property
    def is_expired(self):
        return self.expires_at is not None and self.expires_at <= timezone.now()


class Product(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name="products")
    name = models.CharField(max_length=100)
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[
            MinValueValidator(Decimal("0.01")),
            MaxValueValidator(Decimal("10000000")),
        ],
    )
    currency = models.CharField(max_length=3, default="TRY")
    features = models.TextField()
    product_url = models.URLField(blank=True, validators=[URLValidator(schemes=["http", "https"])])
    image_url = models.URLField(blank=True, validators=[URLValidator(schemes=["https"])])
    position = models.PositiveSmallIntegerField()

    class Meta:
        ordering = ["position"]
        constraints = [
            models.UniqueConstraint(fields=["poll", "position"], name="unique_position_per_poll"),
        ]

    def __str__(self):
        return self.name

    @property
    def features_list(self):
        return [line.strip() for line in self.features.splitlines() if line.strip()]

    @property
    def total_votes(self):
        return getattr(self, "worth_count", 0) + getattr(self, "not_worth_count", 0)

    @property
    def worth_ratio(self):
        total = self.total_votes
        if total == 0:
            return None
        return round(self.worth_count / total * 100, 1)


class Vote(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="votes")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    anon_id = models.UUIDField(null=True, blank=True, db_index=True)
    ip_hash = models.CharField(max_length=64, blank=True, default="", db_index=True)
    value = models.SmallIntegerField(choices=VoteValue.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["product", "user"],
                condition=models.Q(user__isnull=False),
                name="unique_vote_per_user",
            ),
            models.UniqueConstraint(
                fields=["product", "anon_id"],
                condition=models.Q(anon_id__isnull=False),
                name="unique_vote_per_anon",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(user__isnull=False, anon_id__isnull=True)
                    | models.Q(user__isnull=True, anon_id__isnull=False)
                ),
                name="vote_has_exactly_one_voter",
            ),
        ]

    def __str__(self):
        return f"{self.product} — {self.get_value_display()}"


class Comment(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="comments"
    )
    body = models.TextField(max_length=500, validators=[MinLengthValidator(3)])
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.author} → {self.product}"


class ReportReason(models.TextChoices):
    INAPPROPRIATE = "inappropriate", "Uygunsuz içerik"
    SPAM = "spam", "Spam veya tanıtım"
    MISLEADING = "misleading", "Yanıltıcı bilgi"
    OTHER = "other", "Diğer"


class ReportStatus(models.TextChoices):
    PENDING = "pending", "Bekliyor"
    RESOLVED = "resolved", "İncelendi"
    DISMISSED = "dismissed", "Reddedildi"


class Report(models.Model):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name="reports")
    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reports"
    )
    reason = models.CharField(max_length=20, choices=ReportReason.choices)
    detail = models.TextField(max_length=500, blank=True)
    status = models.CharField(
        max_length=20, choices=ReportStatus.choices, default=ReportStatus.PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(fields=["poll", "reporter"], name="unique_report_per_user"),
        ]

    def __str__(self):
        return f"{self.poll} — {self.get_reason_display()}"


class VoteAttempt(models.Model):
    """Hız sınırlama için oy isteklerinin (başarılı/başarısız) kaydı."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True
    )
    anon_id = models.UUIDField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
