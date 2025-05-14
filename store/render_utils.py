"""
Utility functions for server-side rendering of t-shirt designs
"""
import os
import json
import uuid
from io import BytesIO
from PIL import Image
from django.conf import settings
from django.core.files.base import ContentFile


def get_tshirt_image_path(color):
    """Get the file path for a t-shirt mockup image"""
    # Try STATIC_ROOT first
    static_root_path = os.path.join(settings.STATIC_ROOT, f"img/tshirt-mockups/tshirt-{color}.png")
    if os.path.exists(static_root_path):
        return static_root_path

    # If not found, try the static directory directly
    base_dir = settings.BASE_DIR
    static_path = os.path.join(base_dir, 'static', f"img/tshirt-mockups/tshirt-{color}.png")
    if os.path.exists(static_path):
        return static_path

    # If still not found, try the media directory
    media_path = os.path.join(settings.MEDIA_ROOT, f"tshirt-mockups/tshirt-{color}.png")
    if os.path.exists(media_path):
        return media_path

    # Fallback to a hardcoded path for testing
    fallback_path = os.path.join(base_dir, 'static', 'img', 'tshirt-mockups', f"tshirt-{color}.png")
    return fallback_path


def render_design_on_tshirt(design_image_path, tshirt_color, design_position_data):
    """
    Render a design on a t-shirt image

    Args:
        design_image_path: Path to the design image file
        tshirt_color: Color of the t-shirt (e.g., 'black', 'white')
        design_position_data: JSON string with position and size data

    Returns:
        BytesIO object containing the rendered image
    """
    # Debug log to help diagnose position data issues
    print(f"Design position data for {tshirt_color}: {design_position_data}")
    try:
        # Parse design position data
        position_data = json.loads(design_position_data)

        # Get t-shirt image path
        tshirt_path = get_tshirt_image_path(tshirt_color)

        # Open images
        tshirt_img = Image.open(tshirt_path).convert('RGBA')
        design_img = Image.open(design_image_path).convert('RGBA')

        # Get dimensions
        tshirt_width, tshirt_height = tshirt_img.size

        # Parse position data from CSS pixels to percentages
        # The position data is stored as "123px" format, so we need to extract the numeric part
        try:
            # Try to parse values with 'px' suffix first
            if 'px' in position_data.get('left', ''):
                left_px = float(position_data.get('left', '0').replace('px', ''))
                top_px = float(position_data.get('top', '0').replace('px', ''))
                width_px = float(position_data.get('width', '0').replace('px', ''))
                height_px = float(position_data.get('height', '0').replace('px', ''))

                # Get the parent container dimensions from the position data if available
                # Otherwise use standard reference size
                parent_width = float(position_data.get('parent_width', 450))
                parent_height = float(position_data.get('parent_height', 450))

                # Convert to percentages based on the parent container size
                left_percent = left_px / parent_width
                top_percent = top_px / parent_height
                width_percent = width_px / parent_width
                height_percent = height_px / parent_height
            else:
                # If no 'px' suffix, assume it's already a percentage (with or without % sign)
                left_percent = float(position_data.get('left', '25%').replace('%', '')) / 100
                top_percent = float(position_data.get('top', '25%').replace('%', '')) / 100
                width_percent = float(position_data.get('width', '25%').replace('%', '')) / 100
                height_percent = float(position_data.get('height', '25%').replace('%', '')) / 100
        except (ValueError, TypeError):
            # Fallback to default values if parsing fails
            print(f"Error parsing position data: {position_data}")
            # Use the values from the design creation page's positionDesign function
            left_percent = 0.35  # Center horizontally
            top_percent = 0.35   # Position on chest area (matches the 0.35 value in JS)
            width_percent = 0.3  # 30% of t-shirt width
            height_percent = 0.3 # 30% of t-shirt height

        # Calculate pixel values for the actual t-shirt image
        design_width = int(tshirt_width * width_percent)
        design_height = int(tshirt_height * height_percent)
        left_pos = int(tshirt_width * left_percent)
        top_pos = int(tshirt_height * top_percent)

        # Resize design
        design_img = design_img.resize((design_width, design_height), Image.LANCZOS)

        # Create a new transparent image for the design
        design_layer = Image.new('RGBA', tshirt_img.size, (0, 0, 0, 0))

        # Paste design onto the transparent layer
        design_layer.paste(design_img, (left_pos, top_pos), design_img)

        # Composite the images
        result = Image.alpha_composite(tshirt_img, design_layer)

        # Convert to RGB for JPEG saving
        result = result.convert('RGB')

        # Save to BytesIO
        output = BytesIO()
        result.save(output, format='JPEG', quality=85)
        output.seek(0)

        return output
    except Exception as e:
        print(f"Error rendering design: {str(e)}")
        raise


def create_rendered_product_images(product, colors):
    """
    Create rendered images for a product in multiple colors

    Args:
        product: Product instance
        colors: List of color strings

    Returns:
        Boolean indicating success
    """
    try:
        # Get the design image path
        design_image_path = product.image.path

        # Get design position data
        design_position = product.design_position

        # Process each color
        for color in colors:
            # Render the design on the t-shirt
            rendered_image = render_design_on_tshirt(
                design_image_path,
                color,
                design_position
            )

            # Generate a unique filename
            filename = f"rendered_{color}_{uuid.uuid4().hex}.jpg"

            # Create a ContentFile from the BytesIO
            rendered_file = ContentFile(rendered_image.getvalue(), name=filename)

            # Create or update the ProductRenderedImage
            from .models import ProductRenderedImage
            ProductRenderedImage.objects.update_or_create(
                product=product,
                color=color,
                defaults={'image': rendered_file}
            )

            # Set the default rendered image if it doesn't exist
            if not product.rendered_image:
                product.rendered_image = rendered_file
                product.save()

        return True
    except Exception as e:
        print(f"Error creating rendered product images: {str(e)}")
        return False
