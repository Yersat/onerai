"""
Models for the designs app in the partners_onerai project.
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify

User = get_user_model()

class Category(models.Model):
    """Category model for designs"""
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    
    class Meta:
        verbose_name_plural = "Categories"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name

class Design(models.Model):
    """Design model for partners_onerai"""
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
    image = models.ImageField(upload_to="designs/")
    tags = models.CharField(max_length=255, blank=True, help_text="Comma-separated hashtags")
    available_colors = models.CharField(max_length=255, default="black,white", help_text="Comma-separated available colors")
    design_position = models.TextField(blank=True, help_text="JSON data for design position and size")
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="designs")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name="designs")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    feedback = models.TextField(blank=True, help_text="Feedback from admin")
    onerai_product_id = models.IntegerField(null=True, blank=True, help_text="Product ID in the onerai service")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    @property
    def is_approved(self):
        return self.status == self.STATUS_APPROVED
