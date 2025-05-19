"""
URL configuration for partners_onerai project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from . import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", TemplateView.as_view(template_name="index.html"), name="index"),
    path("designs/", include("designs.urls")),
    path("accounts/", include("django.contrib.auth.urls")),

    # Legal document routes
    path("legal/<slug:document_name>/", views.legal_document, name="legal_document"),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
