import os
import base64
import uuid
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.utils.text import slugify
from django.core.files.base import ContentFile
from django.urls import reverse
from .models import Product, Category, ShippingAddress, Order, OrderItem
from .forms import ShippingAddressForm

User = get_user_model()

# Create your views here.


def index(request):
    # Get featured products (only approved ones)
    featured_products = Product.objects.filter(
        is_featured=True,
        is_active=True,
        approval_status=Product.STATUS_APPROVED
    )[:8]

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
    # Get category filter from query parameters
    category_name = request.GET.get('category')

    # Base query for approved and active products
    products_query = Product.objects.filter(
        is_active=True,
        approval_status=Product.STATUS_APPROVED
    )

    # Apply category filter if provided
    if category_name:
        products_query = products_query.filter(category__name=category_name)

    # Get all categories for the filter buttons
    categories = Category.objects.all()

    # Get the products
    products = products_query.order_by('-created_at')

    context = {
        "products": products,
        "categories": categories
    }

    return render(request, "store/product_list.html", context)


def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)

    # If the product is not approved, only the creator or admin can view it
    if product.approval_status != Product.STATUS_APPROVED:
        if not request.user.is_authenticated or (
            request.user != product.creator and not request.user.is_staff
        ):
            messages.error(request, "Этот дизайн еще не одобрен администратором.")
            return redirect("store:products")

    return render(request, "store/product_detail.html", {"product": product})


def creator_list(request):
    creators = User.objects.filter(is_creator=True).order_by("-designs_count")
    return render(request, "store/creator_list.html", {"creators": creators})


def creator_profile(request, username):
    creator = get_object_or_404(User, username=username, is_creator=True)

    # If viewing own profile or admin, show all products including pending/rejected
    if request.user.is_authenticated and (request.user.username == username or request.user.is_staff):
        products = creator.products.filter(is_active=True)
        is_own_profile = True
    else:
        # For other users, only show approved products
        products = creator.products.filter(
            is_active=True,
            approval_status=Product.STATUS_APPROVED
        )
        is_own_profile = False

    return render(
        request,
        "store/creator_profile.html",
        {
            "creator": creator,
            "products": products,
            "is_own_profile": is_own_profile
        },
    )


def category_products(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = category.products.filter(
        is_active=True,
        approval_status=Product.STATUS_APPROVED
    )
    return render(
        request,
        "store/category_products.html",
        {"category": category, "products": products},
    )


def cart(request):
    # Initialize cart items and total price
    cart_items = []
    total_price = 0

    # Handle adding product to cart
    if request.method == "POST":
        product_id = request.POST.get('product_id')
        selected_size = request.POST.get('selected_size')
        selected_color = request.POST.get('selected_color')

        if product_id and selected_size and selected_color:
            try:
                # Get the product
                product = get_object_or_404(Product, id=product_id, is_active=True, approval_status=Product.STATUS_APPROVED)

                # Initialize session cart if it doesn't exist
                if 'cart' not in request.session:
                    request.session['cart'] = []

                # Add item to cart
                cart_item = {
                    'product_id': product_id,
                    'size': selected_size,
                    'color': selected_color
                }

                request.session['cart'].append(cart_item)
                request.session.modified = True

                messages.success(request, f"{product.name} добавлен в корзину")
            except Exception as e:
                messages.error(request, f"Ошибка при добавлении товара в корзину: {str(e)}")

    # Get cart items from session
    if 'cart' in request.session and request.session['cart']:
        for index, item in enumerate(request.session['cart']):
            try:
                product = Product.objects.get(id=item['product_id'], is_active=True, approval_status=Product.STATUS_APPROVED)
                cart_item = {
                    'product': product,
                    'size': item['size'],
                    'color': item['color'],
                    'index': index  # Add index for removal
                }
                cart_items.append(cart_item)
                total_price += float(product.price)
            except Product.DoesNotExist:
                # Remove invalid products from cart
                request.session['cart'].remove(item)
                request.session.modified = True

    context = {
        'cart_items': cart_items,
        'total_price': total_price
    }

    return render(request, "store/cart.html", context)


@login_required
def my_designs(request):
    """View for creators to see all their designs with approval status"""
    products = Product.objects.filter(creator=request.user).order_by('-created_at')

    # Count products by status
    pending_count = products.filter(approval_status=Product.STATUS_PENDING).count()
    approved_count = products.filter(approval_status=Product.STATUS_APPROVED).count()
    rejected_count = products.filter(approval_status=Product.STATUS_REJECTED).count()

    context = {
        'products': products,
        'pending_count': pending_count,
        'approved_count': approved_count,
        'rejected_count': rejected_count,
    }

    return render(request, "store/my_designs.html", context)


@login_required
def submission_confirmation(request, product_id):
    """View for showing confirmation after design submission"""
    product = get_object_or_404(Product, id=product_id, creator=request.user)
    return render(request, "store/submission_confirmation.html", {"product": product})


@login_required
def add_product(request):
    # Since we're using the Creator model as our user model,
    # all authenticated users are creators
    if request.method == "POST":
        # Extract form data
        name = request.POST.get('name')
        description = request.POST.get('description')
        price = request.POST.get('price')
        category_name = request.POST.get('category')
        tags = request.POST.get('tags', '')  # Get tags with empty string as default
        available_colors = request.POST.get('available_colors', 'black,white')  # Get available colors
        image = request.FILES.get('image')
        design_position = request.POST.get('design_position')
        rendered_image_data = request.POST.get('rendered_image_data')

        # Basic validation
        if not all([name, description, price, category_name, image]):
            messages.error(request, 'Пожалуйста, заполните все обязательные поля')
            return render(request, "store/add_product.html")

        try:
            # Get or create category
            category, created = Category.objects.get_or_create(
                name=category_name,
                defaults={'slug': slugify(category_name)}
            )

            # Create product with pending approval status
            product = Product.objects.create(
                name=name,
                description=description,
                price=price,
                image=image,
                tags=tags,  # Save tags
                available_colors=available_colors,  # Save available colors
                design_position=design_position,  # Save design position data
                creator=request.user,
                category=category,
                approval_status=Product.STATUS_PENDING  # Set as pending approval
            )

            # Process the rendered image if available
            if rendered_image_data and rendered_image_data.startswith('data:image'):
                # Extract the base64 encoded image data
                format, imgstr = rendered_image_data.split(';base64,')
                ext = format.split('/')[-1]

                # Generate a unique filename
                filename = f"rendered_{uuid.uuid4().hex}.{ext}"

                # Convert base64 to file and save
                rendered_image = ContentFile(base64.b64decode(imgstr), name=filename)
                product.rendered_image = rendered_image
                product.save()

            # Update user's designs count
            request.user.designs_count += 1
            request.user.is_creator = True
            request.user.save()

            # Success message is now shown on the confirmation page
            return redirect('store:submission_confirmation', product_id=product.id)

        except Exception as e:
            messages.error(request, f'Произошла ошибка: {str(e)}')

    return render(request, "store/add_product.html")


@login_required
def checkout(request):
    """View for checkout process"""
    # Initialize cart items and total price
    cart_items = []
    total_price = 0

    # Check if cart is empty
    if 'cart' not in request.session or not request.session['cart']:
        messages.warning(request, "Ваша корзина пуста. Добавьте товары перед оформлением заказа.")
        return redirect("store:cart")

    # Get cart items from session
    for index, item in enumerate(request.session['cart']):
        try:
            product = Product.objects.get(id=item['product_id'], is_active=True, approval_status=Product.STATUS_APPROVED)
            cart_item = {
                'product': product,
                'size': item['size'],
                'color': item['color'],
                'index': index
            }
            cart_items.append(cart_item)
            total_price += float(product.price)
        except Product.DoesNotExist:
            # Remove invalid products from cart
            request.session['cart'].remove(item)
            request.session.modified = True

    # Get user's shipping addresses
    shipping_addresses = ShippingAddress.objects.filter(user=request.user).order_by('-is_default')

    # Initialize form for new shipping address
    form = ShippingAddressForm()

    if request.method == "POST":
        # Check if user is submitting a new address or using an existing one
        address_choice = request.POST.get('address_choice')

        # Validate that an address choice was provided
        if not address_choice:
            messages.error(request, "Пожалуйста, выберите адрес доставки или добавьте новый.")
            context = {
                'cart_items': cart_items,
                'total_price': total_price,
                'shipping_addresses': shipping_addresses,
                'form': form
            }
            return render(request, "store/checkout.html", context)

        if address_choice == 'new':
            # Process new address form
            form = ShippingAddressForm(request.POST)
            if form.is_valid():
                shipping_address = form.save(commit=False)
                shipping_address.user = request.user
                shipping_address.save()
            else:
                # If form is invalid, render the page again with form errors
                context = {
                    'cart_items': cart_items,
                    'total_price': total_price,
                    'shipping_addresses': shipping_addresses,
                    'form': form
                }
                return render(request, "store/checkout.html", context)
        else:
            # Get existing address
            try:
                shipping_address = ShippingAddress.objects.get(id=address_choice, user=request.user)
            except ShippingAddress.DoesNotExist:
                messages.error(request, "Выбранный адрес не найден.")
                return redirect("store:checkout")

        # Create order
        order = Order.objects.create(
            user=request.user,
            shipping_address=shipping_address,
            total_price=total_price,
            status=Order.STATUS_PENDING
        )

        # Create order items
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item['product'],
                size=item['size'],
                color=item['color'],
                price=item['product'].price
            )

        # Clear cart
        request.session['cart'] = []
        request.session.modified = True

        # Redirect to order confirmation page
        messages.success(request, "Заказ успешно оформлен! Мы свяжемся с вами для подтверждения и оплаты.")
        return redirect("store:order_confirmation", order_id=order.id)

    context = {
        'cart_items': cart_items,
        'total_price': total_price,
        'shipping_addresses': shipping_addresses,
        'form': form
    }

    return render(request, "store/checkout.html", context)


@login_required
def order_confirmation(request, order_id):
    """View for showing order confirmation after checkout"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, "store/order_confirmation.html", {"order": order})


def remove_from_cart(request, item_index):
    """View for removing an item from the cart"""
    if 'cart' in request.session and request.session['cart']:
        try:
            # Get the item that's being removed to show in the success message
            if 0 <= item_index < len(request.session['cart']):
                item = request.session['cart'][item_index]
                try:
                    product = Product.objects.get(id=item['product_id'])
                    product_name = product.name
                except Product.DoesNotExist:
                    product_name = "Товар"

                # Remove the item from the cart
                request.session['cart'].pop(item_index)
                request.session.modified = True

                messages.success(request, f"{product_name} удален из корзины")
            else:
                messages.error(request, "Товар не найден в корзине")
        except Exception as e:
            messages.error(request, f"Ошибка при удалении товара из корзины: {str(e)}")

    # Redirect back to cart
    return redirect("store:cart")