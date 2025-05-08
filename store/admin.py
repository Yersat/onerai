from django.contrib import admin
from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "created_at", "updated_at")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "price",
        "creator",
        "category",
        "is_featured",
        "is_active",
        "created_at",
    )
    list_filter = ("is_featured", "is_active", "category", "created_at")
    search_fields = ("name", "description", "creator__username")
    ordering = ("-created_at",)
