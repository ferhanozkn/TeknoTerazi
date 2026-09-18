from decimal import Decimal

from django import forms
from django.core.exceptions import ValidationError
from django.forms import BaseInlineFormSet, inlineformset_factory
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .models import BudgetTier, Category, Comment, Poll, Product, Report, ReportReason, UsagePurpose


class PollForm(forms.ModelForm):
    hide_results_until_vote = forms.BooleanField(
        label=_("Sonuçları oy vermeden gizle"),
        required=False,
        help_text=_("Önyargıyı azaltmak için: bir ürüne oy verene kadar o ürünün oy sayıları gizli kalır."),
    )
    expires_at = forms.DateTimeField(
        required=False,
        label=_("Bitiş tarihi (opsiyonel)"),
        widget=forms.DateTimeInput(attrs={"type": "datetime-local"}),
        help_text=_("Belirlersen bu tarihten sonra anket otomatik olarak kapanır."),
        error_messages={"invalid": _("Geçerli bir tarih ve saat gir.")},
    )

    class Meta:
        model = Poll
        fields = [
            "title",
            "category",
            "description",
            "usage_purpose",
            "budget_tier",
            "hide_results_until_vote",
            "expires_at",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["category"].choices = [("", _("Kategori seç"))] + list(Category.choices)
        self.fields["usage_purpose"].required = False
        self.fields["usage_purpose"].choices = [("", _("Kullanım amacı seç (opsiyonel)"))] + list(
            UsagePurpose.choices
        )
        self.fields["budget_tier"].required = False
        self.fields["budget_tier"].choices = [("", _("Bütçe seç (opsiyonel)"))] + list(BudgetTier.choices)

    def clean_expires_at(self):
        value = self.cleaned_data.get("expires_at")
        if value and value <= timezone.now():
            raise ValidationError(_("Bitiş tarihi gelecekte bir zaman olmalı."))
        return value


class CommaDecimalField(forms.DecimalField):
    def to_python(self, value):
        if isinstance(value, str):
            value = value.strip().replace(",", ".")
        return super().to_python(value)


ALLOWED_IMAGE_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
MAX_IMAGE_SIZE = 5 * 1024 * 1024


class ProductForm(forms.ModelForm):
    image = forms.FileField(
        required=False,
        label=_("Görsel yükle (opsiyonel)"),
        help_text=_("jpg, png, webp veya gif — en fazla 5 MB. Yüklersen aşağıdaki link yok sayılır."),
    )
    price = CommaDecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=Decimal("0.01"),
        max_value=Decimal("10000000"),
        widget=forms.TextInput(attrs={"inputmode": "decimal", "placeholder": "0,00"}),
        error_messages={
            "invalid": _("Geçerli bir fiyat gir."),
            "required": _("Geçerli bir fiyat gir."),
            "min_value": _("Geçerli bir fiyat gir."),
            "max_value": _("Geçerli bir fiyat gir."),
        },
    )
    features = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={
                "rows": 4,
                "placeholder": _("Her satıra bir özellik yaz\n8 GB RAM\n120 Hz ekran"),
            }
        ),
    )
    attributes = forms.CharField(
        required=False,
        label=_("Karşılaştırma özellikleri (opsiyonel)"),
        widget=forms.Textarea(
            attrs={
                "rows": 3,
                "placeholder": _("Diğer ürünlerle yan yana karşılaştırmak için\nRAM: 8 GB\nDepolama: 128 GB"),
            }
        ),
        help_text=_('Her satırı "Anahtar: Değer" biçiminde yaz — anket sayfasında bir karşılaştırma tablosu oluşturur.'),
    )

    class Meta:
        model = Product
        fields = ["name", "price", "features", "product_url", "image_url", "attributes"]

    def clean_image(self):
        file = self.cleaned_data.get("image")
        if not file:
            return file
        if file.content_type not in ALLOWED_IMAGE_CONTENT_TYPES:
            raise ValidationError(_("Yalnızca JPG, PNG, WEBP veya GIF dosyası yükleyebilirsin."))
        if file.size > MAX_IMAGE_SIZE:
            raise ValidationError(_("Görsel en fazla 5 MB olabilir."))
        return file

    def clean_features(self):
        raw = self.cleaned_data.get("features", "")
        lines = [line.strip() for line in raw.splitlines() if line.strip()]
        if not lines:
            raise ValidationError(_("Ürünün en az bir özelliğini yazmalısın."))
        if len(lines) > 15:
            raise ValidationError(_("En fazla 15 özellik ekleyebilirsin."))
        for line in lines:
            if len(line) > 120:
                raise ValidationError(_("Her özellik satırı en fazla 120 karakter olabilir."))
        return "\n".join(lines)

    def clean_attributes(self):
        raw = self.cleaned_data.get("attributes", "")
        lines = [line.strip() for line in raw.splitlines() if line.strip()]
        if len(lines) > 8:
            raise ValidationError(_("En fazla 8 karşılaştırma özelliği ekleyebilirsin."))
        parsed = []
        for line in lines:
            if ":" not in line:
                raise ValidationError(_('Her satırı "Anahtar: Değer" biçiminde yaz (örn. "RAM: 8 GB").'))
            key, separator, value = line.partition(":")
            key, value = key.strip(), value.strip()
            if not key or not value:
                raise ValidationError(_('Her satırı "Anahtar: Değer" biçiminde yaz (örn. "RAM: 8 GB").'))
            if len(key) > 40:
                raise ValidationError(_("Özellik adı en fazla 40 karakter olabilir."))
            if len(value) > 80:
                raise ValidationError(_("Özellik değeri en fazla 80 karakter olabilir."))
            parsed.append(f"{key}: {value}")
        return "\n".join(parsed)


class BaseProductFormSet(BaseInlineFormSet):
    default_error_messages = {
        "too_few_forms": _("Bir ankete en az %(num)d ürün eklemelisin."),
        "too_many_forms": _("Bir ankete en fazla %(num)d ürün ekleyebilirsin."),
    }

    def clean(self):
        super().clean()
        if any(self.errors):
            return
        names = []
        for form in self.forms:
            name = form.cleaned_data.get("name", "").strip().lower()
            if not name:
                continue
            if name in names:
                raise ValidationError(_("Aynı ürünü iki kez ekleyemezsin."))
            names.append(name)


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["body"]
        widgets = {
            "body": forms.Textarea(
                attrs={
                    "rows": 3,
                    "maxlength": 500,
                    "placeholder": _("Neden buna değer ya da değmez? Kısa bir not bırak…"),
                }
            )
        }
        error_messages = {
            "body": {
                "required": _("Yorum yazmadan gönderemezsin."),
                "min_length": _("Yorumun en az 3 karakter olmalı."),
                "max_length": _("Yorumun en fazla 500 karakter olabilir."),
            }
        }


class ReportForm(forms.ModelForm):
    reason = forms.ChoiceField(
        label=_("Şikayet nedeni"),
        choices=ReportReason.choices,
        error_messages={"required": _("Bir şikayet nedeni seçmelisin.")},
    )
    detail = forms.CharField(
        label=_("Detay (opsiyonel)"),
        required=False,
        max_length=500,
        widget=forms.Textarea(
            attrs={"rows": 3, "placeholder": _("İstersen kısaca açıkla (opsiyonel)…")}
        ),
    )

    class Meta:
        model = Report
        fields = ["reason", "detail"]


ProductFormSet = inlineformset_factory(
    Poll,
    Product,
    form=ProductForm,
    formset=BaseProductFormSet,
    fields=["name", "price", "features", "product_url", "image_url", "attributes"],
    extra=0,
    min_num=2,
    max_num=5,
    validate_min=True,
    validate_max=True,
    can_delete=False,
)
