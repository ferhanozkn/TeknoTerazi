from django.contrib import admin

from .models import Comment, Poll, Product, Vote


class ProductInline(admin.TabularInline):
    model = Product
    extra = 0


@admin.register(Poll)
class PollAdmin(admin.ModelAdmin):
    inlines = [ProductInline]
    list_display = ("title", "author", "category", "is_active", "created_at")
    list_filter = ("category", "is_active", "created_at")
    search_fields = ("title", "author__username")


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ("product", "user", "anon_id", "value", "created_at")
    list_filter = ("value",)
    readonly_fields = [f.name for f in Vote._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("product", "author", "body", "created_at")
    list_filter = ("created_at",)
    search_fields = ("body", "author__username", "product__name")
    readonly_fields = [f.name for f in Comment._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
