from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import CustomUser


class SignUpForm(UserCreationForm):
    error_messages = {
        **UserCreationForm.error_messages,
        "password_mismatch": "Parolalar eşleşmiyor.",
    }

    class Meta:
        model = CustomUser
        fields = ["username", "email"]

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if username and CustomUser.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError("Bu kullanıcı adı zaten kullanılıyor.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get("email", "").lower()
        if CustomUser.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Bu e-posta adresiyle zaten bir hesap var.")
        return email


class UsernameChangeForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ["username"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "Kullanıcı adı"

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if (
            username
            and CustomUser.objects.filter(username__iexact=username)
            .exclude(pk=self.instance.pk)
            .exists()
        ):
            raise forms.ValidationError("Bu kullanıcı adı zaten kullanılıyor.")
        return username


class EmailLoginForm(AuthenticationForm):
    error_messages = {
        **AuthenticationForm.error_messages,
        "invalid_login": "E-posta veya parola hatalı.",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "E-posta"

    def clean_username(self):
        return self.cleaned_data.get("username", "").lower()
