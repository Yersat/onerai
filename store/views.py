import os
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from .models import Product, Category

User = get_user_model()

# Create your views here.


def index(request):
    # Get featured products (you can adjust the logic based on your needs)
    featured_products = Product.objects.filter(is_featured=True)[:8]

    # Get all categories
    categories = Category.objects.all()[:6]

    # Get featured creators (users with most designs)
    featured_creators = User.objects.filter(is_creator=True).order_by("-designs_count")[
        :4
    ]

    context = {
        "featured_products": featured_products,
        "categories": categories,
        "featured_creators": featured_creators,
    }

    return render(request, "store/index.html", context)


def product_list(request):
    products = Product.objects.filter(is_active=True)
    return render(request, "store/product_list.html", {"products": products})


def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)
    return render(request, "store/product_detail.html", {"product": product})


def creator_list(request):
    creators = User.objects.filter(is_creator=True).order_by("-designs_count")
    return render(request, "store/creator_list.html", {"creators": creators})


def creator_profile(request, username):
    creator = get_object_or_404(User, username=username, is_creator=True)
    products = creator.products.filter(is_active=True)
    return render(
        request,
        "store/creator_profile.html",
        {"creator": creator, "products": products},
    )


def category_products(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = category.products.filter(is_active=True)
    return render(
        request,
        "store/category_products.html",
        {"category": category, "products": products},
    )


def cart(request):
    # This is a placeholder - we'll implement cart functionality later
    return render(request, "store/cart.html")


@login_required
def add_product(request):
    # Since we're using the Creator model as our user model,
    # all authenticated users are creators
    if request.method == "POST":
        # Handle product creation (to be implemented)
        pass
    return render(request, "store/add_product.html")
