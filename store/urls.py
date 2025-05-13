from django.urls import path
from . import views

app_name = "store"

urlpatterns = [
    path("", views.index, name="index"),
    path("products/", views.product_list, name="products"),
    path("products/<int:product_id>/", views.product_detail, name="product_detail"),
    path("all-creators/", views.creator_list, name="creators"),
    path("all-creators/<str:username>/", views.creator_profile, name="creator_profile"),
    path("category/<slug:slug>/", views.category_products, name="category"),
    path("cart/", views.cart, name="cart"),
    path("cart/remove/<int:item_index>/", views.remove_from_cart, name="remove_from_cart"),
    path("checkout/", views.checkout, name="checkout"),
    path("order-confirmation/<int:order_id>/", views.order_confirmation, name="order_confirmation"),
    path("add-product/", views.add_product, name="add_product"),
    path("my-designs/", views.my_designs, name="my_designs"),
    path("submission-confirmation/<int:product_id>/", views.submission_confirmation, name="submission_confirmation"),
]
