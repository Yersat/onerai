from django.contrib import admin
from django.utils.html import format_html
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
        "approval_status_colored",
        "is_featured",
        "is_active",
        "created_at",
    )
    list_filter = ("approval_status", "is_featured", "is_active", "category", "created_at")
    search_fields = ("name", "description", "creator__username")
    ordering = ("-created_at",)
    readonly_fields = ("created_at", "updated_at")
    actions = ["approve_products", "reject_products"]

    fieldsets = (
        ("Основная информация", {
            "fields": ("name", "description", "price", "image", "tags", "available_colors", "creator", "category")
        }),
        ("Статус проверки", {
            "fields": ("approval_status", "admin_feedback")
        }),
        ("Настройки отображения", {
            "fields": ("is_featured", "is_active")
        }),
        ("Информация о создании", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )

    def approval_status_colored(self, obj):
        colors = {
            Product.STATUS_PENDING: "orange",
            Product.STATUS_APPROVED: "green",
            Product.STATUS_REJECTED: "red",
        }
        status_display = dict(Product.STATUS_CHOICES)[obj.approval_status]
        color = colors.get(obj.approval_status, "black")
        return format_html('<span style="color: {};">{}</span>', color, status_display)

    approval_status_colored.short_description = "Статус проверки"

    def approve_products(self, request, queryset):
        updated = queryset.update(approval_status=Product.STATUS_APPROVED, admin_feedback="")
        self.message_user(request, f"{updated} дизайн(ов) успешно одобрено.")

    approve_products.short_description = "Одобрить выбранные дизайны"

    def reject_products(self, request, queryset):
        # This is a simplified version. In a real application, you might want to
        # add a form to collect feedback for each rejected product.
        updated = queryset.update(
            approval_status=Product.STATUS_REJECTED,
            admin_feedback="Дизайн не соответствует требованиям платформы."
        )
        self.message_user(request, f"{updated} дизайн(ов) отклонено.")

    reject_products.short_description = "Отклонить выбранные дизайны"
