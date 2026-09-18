from decimal import Decimal

from django import forms
from django.core.exceptions import ValidationError
from django.forms import BaseInlineFormSet, inlineformset_factory

from .models import Category, Comment, Poll, Product


class PollForm(forms.ModelForm):
    class Meta:
        model = Poll
        fields = ["title", "category", "description"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["category"].choices = [("", "Kategori seç")] + list(Category.choices)


class CommaDecimalField(forms.DecimalField):
    def to_python(self, value):
        if isinstance(value, str):
            value = value.strip().replace(",", ".")
        return super().to_python(value)


class ProductForm(forms.ModelForm):
    price = CommaDecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=Decimal("0.01"),
        max_value=Decimal("10000000"),
        widget=forms.TextInput(attrs={"inputmode": "decimal", "placeholder": "0,00"}),
        error_messages={
            "invalid": "Geçerli bir fiyat gir.",
            "required": "Geçerli bir fiyat gir.",
            "min_value": "Geçerli bir fiyat gir.",
            "max_value": "Geçerli bir fiyat gir.",
        },
    )
    features = forms.CharField(
        required=False,
        widget=forms.Textarea(
            attrs={
                "rows": 4,
                "placeholder": "Her satıra bir özellik yaz\n8 GB RAM\n120 Hz ekran",
            }
        ),
    )

    class Meta:
        model = Product
        fields = ["name", "price", "features", "product_url", "image_url"]

    def clean_features(self):
        raw = self.cleaned_data.get("features", "")
        lines = [line.strip() for line in raw.splitlines() if line.strip()]
        if not lines:
            raise ValidationError("Ürünün en az bir özelliğini yazmalısın.")
        if len(lines) > 15:
            raise ValidationError("En fazla 15 özellik ekleyebilirsin.")
        for line in lines:
            if len(line) > 120:
                raise ValidationError("Her özellik satırı en fazla 120 karakter olabilir.")
        return "\n".join(lines)


class BaseProductFormSet(BaseInlineFormSet):
    default_error_messages = {
        "too_few_forms": "Bir ankete en az %(num)d ürün eklemelisin.",
        "too_many_forms": "Bir ankete en fazla %(num)d ürün ekleyebilirsin.",
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
                raise ValidationError("Aynı ürünü iki kez ekleyemezsin.")
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
                    "placeholder": "Neden buna değer ya da değmez? Kısa bir not bırak…",
                }
            )
        }
        error_messages = {
            "body": {
                "required": "Yorum yazmadan gönderemezsin.",
                "min_length": "Yorumun en az 3 karakter olmalı.",
                "max_length": "Yorumun en fazla 500 karakter olabilir.",
            }
        }


ProductFormSet = inlineformset_factory(
    Poll,
    Product,
    form=ProductForm,
    formset=BaseProductFormSet,
    fields=["name", "price", "features", "product_url", "image_url"],
    extra=0,
    min_num=2,
    max_num=5,
    validate_min=True,
    validate_max=True,
    can_delete=False,
)
