from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Product, ProductRenderedImage, Order, OrderItem, ShippingAddress


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "created_at", "updated_at")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(ProductRenderedImage)
class ProductRenderedImageAdmin(admin.ModelAdmin):
    list_display = ("product", "color", "created_at")
    list_filter = ("color", "created_at")
    search_fields = ("product__name", "color")
    ordering = ("product", "color")


class ProductRenderedImageInline(admin.TabularInline):
    model = ProductRenderedImage
    extra = 0
    fields = ('color', 'image')


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
    inlines = [ProductRenderedImageInline]

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
        updated = queryset.update(approval_status=Product.STATUS_APPROVED, is_active=True, admin_feedback="")
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


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'size', 'color', 'price', 'created_at')
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_price', 'status_colored', 'tracking_number', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('id', 'user__username', 'user__email', 'tracking_number')
    readonly_fields = ('created_at', 'updated_at', 'user', 'total_price')
    inlines = [OrderItemInline]
    actions = ['mark_as_processing', 'mark_as_shipped', 'mark_as_delivered', 'mark_as_cancelled']

    fieldsets = (
        ('Информация о заказе', {
            'fields': ('user', 'total_price', 'status', 'created_at', 'updated_at')
        }),
        ('Информация о доставке', {
            'fields': ('shipping_address', 'tracking_number')
        }),
        ('Информация об оплате', {
            'fields': ('payment_id',)
        }),
    )

    def status_colored(self, obj):
        colors = {
            Order.STATUS_PENDING: "orange",
            Order.STATUS_PROCESSING: "blue",
            Order.STATUS_SHIPPED: "purple",
            Order.STATUS_DELIVERED: "green",
            Order.STATUS_CANCELLED: "red",
        }
        status_display = dict(Order.STATUS_CHOICES)[obj.status]
        color = colors.get(obj.status, "black")
        return format_html('<span style="color: {};">{}</span>', color, status_display)

    status_colored.short_description = "Статус заказа"

    def mark_as_processing(self, request, queryset):
        updated = queryset.update(status=Order.STATUS_PROCESSING)
        self.message_user(request, f"{updated} заказ(ов) отмечено как 'В обработке'.")

    mark_as_processing.short_description = "Отметить как 'В обработке'"

    def mark_as_shipped(self, request, queryset):
        updated = queryset.update(status=Order.STATUS_SHIPPED)
        self.message_user(request, f"{updated} заказ(ов) отмечено как 'Отправлен'.")

    mark_as_shipped.short_description = "Отметить как 'Отправлен'"

    def mark_as_delivered(self, request, queryset):
        updated = queryset.update(status=Order.STATUS_DELIVERED)
        self.message_user(request, f"{updated} заказ(ов) отмечено как 'Доставлен'.")

    mark_as_delivered.short_description = "Отметить как 'Доставлен'"

    def mark_as_cancelled(self, request, queryset):
        updated = queryset.update(status=Order.STATUS_CANCELLED)
        self.message_user(request, f"{updated} заказ(ов) отмечено как 'Отменен'.")

    mark_as_cancelled.short_description = "Отметить как 'Отменен'"


@admin.register(ShippingAddress)
class ShippingAddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'city', 'phone', 'is_default')
    list_filter = ('city', 'is_default')
    search_fields = ('user__username', 'full_name', 'address', 'city', 'phone')
    readonly_fields = ('created_at', 'updated_at')
