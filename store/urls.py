from django.urls import path
from . import views

app_name = "store"

urlpatterns = [
    path("", views.index, name="index"),
    path("products/", views.product_list, name="products"),
    path("products/<int:product_id>/", views.product_detail, name="product_detail"),
    path("creators/", views.creator_list, name="creators"),
    path("creators/<str:username>/", views.creator_profile, name="creator_profile"),
    path("category/<slug:slug>/", views.category_products, name="category"),
    path("cart/", views.cart, name="cart"),
    path("add-product/", views.add_product, name="add_product"),
]
