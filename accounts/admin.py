from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Kişisel bilgiler", {"fields": ("username",)}),
        (
            "İzinler",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Önemli tarihler", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "username", "password1", "password2"),
            },
        ),
    )
    list_display = ("email", "username", "is_staff", "is_active", "date_joined")
    ordering = ("-date_joined",)
    search_fields = ("email", "username")
