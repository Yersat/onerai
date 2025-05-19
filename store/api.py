"""
API endpoints for the onerai store.
"""

import json
import os
import requests
from urllib.parse import urlparse
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from django.conf import settings
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from .models import Product, Category, ProductRenderedImage
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.utils.text import slugify
from .render_utils import create_rendered_product_images

User = get_user_model()

def api_key_required(view_func):
    """
    Decorator to check if the API key is valid.
    """
    def wrapped_view(request, *args, **kwargs):
        # Get the API key from the request headers
        api_key = request.headers.get('Authorization', '').replace('ApiKey ', '')

        # Check if the API key is valid
        if api_key != settings.API_KEY:
            return JsonResponse({
                'success': False,
                'error': 'Invalid API key'
            }, status=401)

        # Call the view function
        return view_func(request, *args, **kwargs)

    return wrapped_view

@csrf_exempt
@require_POST
@api_key_required
def submit_design(request):
    """
    API endpoint to submit a design from partners_onerai.

    Expected JSON payload:
    {
        "name": "Design Name",
        "description": "Design Description",
        "price": "9999.99",
        "tags": "tag1, tag2, tag3",
        "available_colors": "black,white,red",
        "creator_email": "creator@example.com",
        "creator_username": "creator",
        "creator_first_name": "First",
        "creator_last_name": "Last",
        "category_name": "Category Name",
        "design_position": "{\"left\":\"10px\",\"top\":\"10px\",\"width\":\"200px\",\"height\":\"200px\"}",
        "design_image_url": "http://example.com/media/designs/image.png",
        "design_image_path": "products/design_123.png"  # Optional: path to image in shared storage
    }

    Returns:
    {
        "success": true,
        "product_id": 123
    }
    """
    try:
        # Parse the JSON data
        data = json.loads(request.body)

        # Get or create the category
        category, _ = Category.objects.get_or_create(
            name=data.get('category_name', 'Uncategorized'),
            defaults={'slug': slugify(data.get('category_name', 'Uncategorized'))}
        )

        # Get or create the creator
        creator, _ = User.objects.get_or_create(
            email=data.get('creator_email'),
            defaults={
                'username': data.get('creator_username'),
                'first_name': data.get('creator_first_name', ''),
                'last_name': data.get('creator_last_name', '')
            }
        )

        # Create the product without image first
        product = Product.objects.create(
            name=data.get('name'),
            description=data.get('description'),
            price=data.get('price'),
            tags=data.get('tags', ''),
            available_colors=data.get('available_colors', 'black,white'),
            design_position=data.get('design_position', ''),
            creator=creator,
            category=category,
            is_active=False,  # Set to False until approved by admin
            is_featured=False
        )

        # Handle the design image
        design_image_url = data.get('design_image_url')
        design_image_path = data.get('design_image_path')

        if design_image_path:
            # If the image is already in our media storage (shared storage approach)
            # We just need to set the path in the product model
            product.image.name = design_image_path
            product.save(update_fields=['image'])
        elif design_image_url:
            # If we have a URL, download the image
            img_temp = NamedTemporaryFile(delete=True)
            try:
                response = requests.get(design_image_url, stream=True)
                response.raise_for_status()  # Raise exception for HTTP errors

                # Write the image to a temporary file
                for block in response.iter_content(1024 * 8):
                    if not block:
                        break
                    img_temp.write(block)
                img_temp.flush()

                # Get the filename from the URL
                filename = os.path.basename(urlparse(design_image_url).path)
                if not filename:
                    filename = f"design_{product.id}.jpg"

                # Save the image to the product
                product.image.save(filename, File(img_temp), save=True)
            except Exception as e:
                # Log the error but don't fail the request
                print(f"Error downloading image: {str(e)}")
                raise
        else:
            # No image provided
            raise ValueError("No design image provided")

        # Generate rendered images for all colors
        available_colors = data.get('available_colors', 'black,white').split(',')
        create_rendered_product_images(product, available_colors)

        # Return success response
        return JsonResponse({
            'success': True,
            'product_id': product.id
        })
    except Exception as e:
        # Return error response
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)

@require_GET
@api_key_required
def design_status(request, product_id):
    """
    API endpoint to check the status of a design.

    Returns:
    {
        "success": true,
        "status": "approved",
        "feedback": "Feedback from admin"
    }
    """
    try:
        # Get the product
        product = Product.objects.get(id=product_id)

        # Return the status
        return JsonResponse({
            'success': True,
            'status': product.approval_status,
            'feedback': product.admin_feedback or ''
        })
    except Product.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Product not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)
