"""
URL patterns for the designs app in the partners_onerai project.
"""
from django.urls import path
from . import views

app_name = "designs"

urlpatterns = [
    path("add/", views.add_design, name="add_design"),
    path("my-designs/", views.my_designs, name="my_designs"),
    path("design/<int:design_id>/", views.design_detail, name="design_detail"),
    path("submission-confirmation/<int:design_id>/", views.submission_confirmation, name="submission_confirmation"),
    path("api/check-status/<int:design_id>/", views.check_design_status, name="check_design_status"),
]
