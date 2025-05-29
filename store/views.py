import os
import base64
import uuid
import json
import os.path
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import get_user_model, login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.utils.text import slugify
from django.core.files.base import ContentFile
from django.urls import reverse
from django.http import JsonResponse, Http404, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.conf import settings
from .models import Product, Category, ShippingAddress, Order, OrderItem, ProductRenderedImage
from .forms import ShippingAddressForm, StoreUserRegistrationForm
from .render_utils import create_rendered_product_images, render_design_on_tshirt
from .freedompay_service import FreedomPayService

User = get_user_model()

# Create your views here.


def index(request):
    # Get featured products (only approved ones)
    featured_products = Product.objects.filter(
        is_featured=True,
        is_active=True,
        approval_status=Product.STATUS_APPROVED
    )[:8]

    # Get recent products (only approved ones)
    recent_products = Product.objects.filter(
        is_active=True,
        approval_status=Product.STATUS_APPROVED
    ).order_by('-created_at')[:8]  # Limit to 8 most recent products

    # Get all categories
    categories = Category.objects.all()[:6]

    context = {
        "featured_products": featured_products,
        "recent_products": recent_products,
        "categories": categories,
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
        quantity = int(request.POST.get('quantity', 1))  # Default to 1 if not provided

        if product_id and selected_size and selected_color:
            try:
                # Get the product
                product = get_object_or_404(Product, id=product_id, is_active=True, approval_status=Product.STATUS_APPROVED)

                # Initialize session cart if it doesn't exist
                if 'cart' not in request.session:
                    request.session['cart'] = []

                # Check if the same product with same size and color already exists in cart
                found = False
                for item in request.session['cart']:
                    if (item['product_id'] == product_id and
                        item['size'] == selected_size and
                        item['color'] == selected_color):
                        # Update quantity instead of adding a new item
                        item['quantity'] = item.get('quantity', 1) + quantity
                        found = True
                        break

                if not found:
                    # Add new item to cart
                    cart_item = {
                        'product_id': product_id,
                        'size': selected_size,
                        'color': selected_color,
                        'quantity': quantity
                    }
                    request.session['cart'].append(cart_item)

                request.session.modified = True
                messages.success(request, f"{product.name} добавлен в корзину")
            except Exception as e:
                messages.error(request, f"Ошибка при добавлении товара в корзину: {str(e)}")

    # Handle quantity updates
    elif request.method == "GET" and request.GET.get('action') == 'update_quantity':
        item_index = int(request.GET.get('item_index', -1))
        new_quantity = int(request.GET.get('quantity', 1))

        if item_index >= 0 and 'cart' in request.session and item_index < len(request.session['cart']):
            if new_quantity > 0:
                # Update quantity
                request.session['cart'][item_index]['quantity'] = new_quantity
                request.session.modified = True
                messages.success(request, "Количество товара обновлено")
            else:
                # Remove item if quantity is 0
                product_id = request.session['cart'][item_index]['product_id']
                try:
                    product = Product.objects.get(id=product_id)
                    product_name = product.name
                except Product.DoesNotExist:
                    product_name = "Товар"

                request.session['cart'].pop(item_index)
                request.session.modified = True
                messages.success(request, f"{product_name} удален из корзины")

        # Redirect back to cart to prevent form resubmission
        return redirect('store:cart')

    # Get cart items from session
    if 'cart' in request.session and request.session['cart']:
        for index, item in enumerate(request.session['cart']):
            try:
                product = Product.objects.get(id=item['product_id'], is_active=True, approval_status=Product.STATUS_APPROVED)
                quantity = item.get('quantity', 1)  # Default to 1 for backward compatibility

                cart_item = {
                    'product': product,
                    'size': item['size'],
                    'color': item['color'],
                    'quantity': quantity,
                    'index': index  # Add index for removal
                }
                cart_items.append(cart_item)
                total_price += float(product.price) * quantity
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

            # Use server-side rendering to generate images for all colors
            available_colors_list = available_colors.split(',')

            # Perform server-side rendering for all selected colors
            create_rendered_product_images(product, available_colors_list)

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
            quantity = item.get('quantity', 1)  # Default to 1 for backward compatibility
            cart_item = {
                'product': product,
                'size': item['size'],
                'color': item['color'],
                'quantity': quantity,
                'index': index
            }
            cart_items.append(cart_item)
            total_price += float(product.price) * quantity
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
                quantity=item['quantity'],
                price=item['product'].price
            )

        # Clear cart
        request.session['cart'] = []
        request.session.modified = True

        # Initialize payment with Freedom Pay
        try:
            freedompay_service = FreedomPayService()
            payment_result = freedompay_service.init_payment(order, request)

            if payment_result['success']:
                payment_data = payment_result['data']

                # Store payment ID in order
                order.payment_id = payment_data.get('pg_payment_id')
                order.save()

                # Redirect to Freedom Pay payment page
                redirect_url = payment_data.get('pg_redirect_url')
                if redirect_url:
                    return redirect(redirect_url)
                else:
                    messages.error(request, "Ошибка при инициализации платежа. Попробуйте еще раз.")
                    return redirect("store:checkout")
            else:
                messages.error(request, f"Ошибка платежной системы: {payment_result.get('error', 'Неизвестная ошибка')}")
                return redirect("store:checkout")

        except Exception as e:
            messages.error(request, f"Ошибка при обработке платежа: {str(e)}")
            return redirect("store:checkout")

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


@login_required
def customer_profile(request):
    """View for customer profile page"""
    # Get user's orders
    orders = Order.objects.filter(user=request.user).order_by('-created_at')

    # Get user's shipping addresses
    shipping_addresses = ShippingAddress.objects.filter(user=request.user).order_by('-is_default')

    context = {
        'user': request.user,
        'orders': orders,
        'shipping_addresses': shipping_addresses,
    }

    return render(request, "store/customer_profile.html", context)


def login_store_user(request):
    """View for store user login"""
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Добро пожаловать, {user.get_full_name()}!")
                # Get the next parameter or default to home
                next_url = request.POST.get("next") or request.GET.get("next")
                if next_url:
                    return redirect(next_url)
                return redirect("store:index")
    else:
        form = AuthenticationForm()
    return render(request, "store/login.html", {"form": form, "next": request.GET.get("next", "")})


def register_store_user(request):
    """View for store user registration"""
    if request.method == "POST":
        form = StoreUserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Регистрация успешна! Добро пожаловать в onerai.")
            next_url = request.POST.get("next") or request.GET.get("next")
            if next_url:
                return redirect(next_url)
            return redirect("store:index")
    else:
        form = StoreUserRegistrationForm()
    return render(request, "store/register.html", {"form": form})


def legal_document(request, document_name):
    """View for displaying legal documents"""
    # Map URL slugs to actual filenames
    document_map = {
        'terms-of-service': 'terms_of_service.html',
        'privacy-policy': 'privacy_policy.html',
        'cookie-policy': 'cookie_policy.html',
        'return-policy': 'return_policy.html',
        'shipping-policy': 'shipping_policy.html',
        'payment-terms': 'payment_terms.html',
        'content-guidelines': 'content_guidelines.html',
        'creator-agreement': 'creator_agreement.html',
        'intellectual-property-policy': 'intellectual_property_policy.html',
        'dispute-resolution-policy': 'dispute_resolution_policy.html',
        'age-restrictions-policy': 'age_restrictions_policy.html',
    }

    # Check if the requested document exists in our map
    if document_name not in document_map:
        raise Http404("Запрашиваемый документ не найден")

    # Get the actual filename
    filename = document_map[document_name]
    file_path = os.path.join(settings.BASE_DIR, 'legal', filename)

    # Check if the file exists
    if not os.path.exists(file_path):
        raise Http404(f"Документ {filename} не найден")

    # Read the file content
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Return the content as a response
    return render(request, 'store/legal_document.html', {
        'content': content,
        'document_name': document_name,
        'document_title': document_name.replace('-', ' ').title()
    })


@csrf_exempt
@require_POST
def render_design_api(request):
    """API endpoint for server-side rendering of designs on t-shirts"""
    try:
        # Extract data from request
        data = json.loads(request.body)
        product_id = data.get('product_id')
        colors = data.get('colors', [])
        design_position = data.get('design_position', None)  # Allow passing custom position data

        # Validate input
        if not product_id:
            return JsonResponse({'error': 'Product ID is required'}, status=400)

        if not colors:
            return JsonResponse({'error': 'At least one color must be specified'}, status=400)

        # Get the product
        try:
            product = Product.objects.get(id=product_id)

            # Update design position if provided
            if design_position:
                # Ensure parent container dimensions are included
                try:
                    position_data = json.loads(design_position)
                    if 'parent_width' not in position_data or 'parent_height' not in position_data:
                        # Add default parent dimensions if not provided
                        position_data['parent_width'] = 450
                        position_data['parent_height'] = 450
                        design_position = json.dumps(position_data)
                except json.JSONDecodeError:
                    # If position data is invalid, just use it as is
                    pass

                product.design_position = design_position
                product.save(update_fields=['design_position'])

        except Product.DoesNotExist:
            return JsonResponse({'error': 'Product not found'}, status=404)

        # Check permissions - only the creator or admin can render designs
        if request.user != product.creator and not request.user.is_staff:
            return JsonResponse({'error': 'Permission denied'}, status=403)

        # Perform the rendering
        success = create_rendered_product_images(product, colors)

        if success:
            # Get the URLs of the rendered images
            rendered_images = {}
            for color in colors:
                try:
                    rendered_image = ProductRenderedImage.objects.get(product=product, color=color)
                    rendered_images[color] = rendered_image.image.url
                except ProductRenderedImage.DoesNotExist:
                    rendered_images[color] = None

            return JsonResponse({
                'success': True,
                'message': 'Images rendered successfully',
                'rendered_images': rendered_images
            })
        else:
            return JsonResponse({
                'error': 'Failed to render images'
            }, status=500)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def logout_view(request):
    """Custom view for handling user logout that accepts GET requests"""
    logout(request)
    messages.success(request, "Вы успешно вышли из аккаунта.")
    return redirect("store:index")


# Freedom Pay payment views
@csrf_exempt
@require_POST
def freedompay_result(request):
    """Handle Freedom Pay payment result callback"""
    try:
        freedompay_service = FreedomPayService()
        result = freedompay_service.process_payment_result(request.POST.dict())

        order_id = result.get('order_id')
        payment_id = result.get('payment_id')

        if order_id:
            try:
                order = Order.objects.get(id=order_id)

                if result['status'] == 'ok':
                    # Payment successful
                    order.payment_status = Order.PAYMENT_STATUS_PAID
                    order.payment_id = payment_id
                    order.status = Order.STATUS_PROCESSING
                    order.save()

                elif result['status'] == 'rejected':
                    # Payment failed
                    order.payment_status = Order.PAYMENT_STATUS_FAILED
                    order.save()

            except Order.DoesNotExist:
                pass

        # Return XML response to Freedom Pay
        response_data = {
            'pg_status': result['status'],
            'pg_description': result['description'],
            'pg_salt': freedompay_service.generate_salt()
        }

        # Generate signature for response
        response_data['pg_sig'] = freedompay_service.generate_signature('', response_data)

        # Build XML response
        xml_response = f'''<?xml version="1.0" encoding="utf-8"?>
<response>
    <pg_status>{response_data['pg_status']}</pg_status>
    <pg_description>{response_data['pg_description']}</pg_description>
    <pg_salt>{response_data['pg_salt']}</pg_salt>
    <pg_sig>{response_data['pg_sig']}</pg_sig>
</response>'''

        return HttpResponse(xml_response, content_type='application/xml')

    except Exception as e:
        # Return error response
        xml_response = f'''<?xml version="1.0" encoding="utf-8"?>
<response>
    <pg_status>error</pg_status>
    <pg_description>Processing error: {str(e)}</pg_description>
</response>'''

        return HttpResponse(xml_response, content_type='application/xml')


def freedompay_success(request):
    """Handle successful payment redirect from Freedom Pay"""
    order_id = request.GET.get('pg_order_id')
    payment_id = request.GET.get('pg_payment_id')
    test_mode = request.GET.get('test_mode')

    if order_id:
        try:
            order = Order.objects.get(id=order_id, user=request.user)

            # If this is a test mode payment, update the order status
            if test_mode == '1':
                order.payment_status = Order.PAYMENT_STATUS_PAID
                order.payment_id = payment_id
                order.status = Order.STATUS_PROCESSING
                order.save()
                messages.success(request, "Тестовый платеж успешно обработан! Ваш заказ принят в обработку.")
            else:
                messages.success(request, "Платеж успешно обработан! Ваш заказ принят в обработку.")

            return redirect("store:order_confirmation", order_id=order.id)
        except Order.DoesNotExist:
            messages.error(request, "Заказ не найден.")
            return redirect("store:index")
    else:
        messages.success(request, "Платеж успешно обработан!")
        return redirect("store:index")


def freedompay_failure(request):
    """Handle failed payment redirect from Freedom Pay"""
    order_id = request.GET.get('pg_order_id')

    if order_id:
        try:
            order = Order.objects.get(id=order_id, user=request.user)
            messages.error(request, "Ошибка при обработке платежа. Попробуйте еще раз или выберите другой способ оплаты.")
            return redirect("store:checkout")
        except Order.DoesNotExist:
            messages.error(request, "Заказ не найден.")
            return redirect("store:index")
    else:
        messages.error(request, "Ошибка при обработке платежа.")
        return redirect("store:index")