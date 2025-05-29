from django.urls import path
from . import views
from . import api

app_name = "store"

urlpatterns = [
    # Frontend routes
    path("", views.index, name="index"),
    path("products/", views.product_list, name="products"),
    path("products/<int:product_id>/", views.product_detail, name="product_detail"),

    path("category/<slug:slug>/", views.category_products, name="category"),
    path("cart/", views.cart, name="cart"),
    path("cart/remove/<int:item_index>/", views.remove_from_cart, name="remove_from_cart"),
    path("checkout/", views.checkout, name="checkout"),
    path("order-confirmation/<int:order_id>/", views.order_confirmation, name="order_confirmation"),
    path("add-product/", views.add_product, name="add_product"),
    path("submission-confirmation/<int:product_id>/", views.submission_confirmation, name="submission_confirmation"),
    path("profile/", views.customer_profile, name="customer_profile"),

    # Legal document routes
    path("legal/<slug:document_name>/", views.legal_document, name="legal_document"),

    # Authentication routes
    path("login/", views.login_store_user, name="login"),
    path("register/", views.register_store_user, name="register"),
    path("logout/", views.logout_view, name="logout"),

    # API routes
    path("api/designs/submit/", api.submit_design, name="api_submit_design"),
    path("api/designs/status/<int:product_id>/", api.design_status, name="api_design_status"),

    # Freedom Pay payment routes
    path("payment/freedompay/result/", views.freedompay_result, name="freedompay_result"),
    path("payment/freedompay/success/", views.freedompay_success, name="freedompay_success"),
    path("payment/freedompay/failure/", views.freedompay_failure, name="freedompay_failure"),
]
