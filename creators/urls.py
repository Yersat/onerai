from django.urls import path
from . import views

app_name = "creators"

urlpatterns = [
    path("register/", views.register_creator, name="register"),
    path("login/", views.login_creator, name="login"),
    path("profile/", views.creator_profile, name="profile"),
]
