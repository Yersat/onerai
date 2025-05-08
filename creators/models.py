from django.db import models
from django.contrib.auth.models import User


class CreatorProfile(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="creator_profile"
    )
    bio = models.TextField(max_length=500, blank=True)
    portfolio_url = models.URLField(blank=True)
    instagram_handle = models.CharField(max_length=30, blank=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"CreatorProfile for {self.user.username}"
