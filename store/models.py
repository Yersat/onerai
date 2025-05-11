from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify

User = get_user_model()


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="categories/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Categories"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Product(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_APPROVED = 'approved'
    STATUS_REJECTED = 'rejected'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'На проверке'),
        (STATUS_APPROVED, 'Одобрен'),
        (STATUS_REJECTED, 'Отклонен'),
    ]

    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to="products/", help_text="Original design image")
    rendered_image = models.ImageField(upload_to="products/rendered/", blank=True, null=True, help_text="T-shirt with design applied")
    tags = models.CharField(max_length=255, blank=True, help_text="Comma-separated hashtags")
    available_colors = models.CharField(max_length=255, default="black,white", help_text="Comma-separated available colors")
    design_position = models.TextField(blank=True, help_text="JSON data for design position and size")
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="products")
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, related_name="products"
    )
    approval_status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
        help_text="Статус проверки дизайна администратором"
    )
    admin_feedback = models.TextField(blank=True, help_text="Комментарий администратора (причина отклонения)")
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    @property
    def is_approved(self):
        return self.approval_status == self.STATUS_APPROVED


# Add is_creator and designs_count to User model
User.add_to_class("is_creator", models.BooleanField(default=False))
User.add_to_class("designs_count", models.IntegerField(default=0))
User.add_to_class(
    "profile_image", models.ImageField(upload_to="profiles/", blank=True, null=True)
)
