"""
Test script to verify design position consistency
"""
import os
import json
import sys
import shutil
from PIL import Image, ImageDraw
from io import BytesIO

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('.'))

# Import Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'onerai.settings')
import django
django.setup()

from store.render_utils import render_design_on_tshirt, get_tshirt_image_path
from store.models import Product
from django.conf import settings

def ensure_test_mockups_exist():
    """
    Create test t-shirt mockup images if they don't exist
    """
    colors = ['black', 'white', 'red', 'blue', 'yellow', 'green', 'grey']

    # Create a test directory for mockups if it doesn't exist
    test_dir = os.path.join(settings.BASE_DIR, 'static', 'img', 'tshirt-mockups')
    os.makedirs(test_dir, exist_ok=True)

    for color in colors:
        mockup_path = os.path.join(test_dir, f"tshirt-{color}.png")

        # Skip if the file already exists
        if os.path.exists(mockup_path):
            continue

        # Create a simple colored rectangle as a mockup
        width, height = 800, 1000
        img = Image.new('RGBA', (width, height), color=color)

        # Add a border to make it look like a t-shirt
        draw = ImageDraw.Draw(img)
        draw.rectangle([(10, 10), (width-10, height-10)], outline='white', width=2)

        # Save the mockup
        img.save(mockup_path)
        print(f"Created test mockup for {color} t-shirt at {mockup_path}")

def test_design_position_consistency():
    """
    Test that design positions are consistent between creation and rendering
    """
    print("Testing design position consistency...")

    # Get a product with design position data
    products = Product.objects.filter(design_position__isnull=False).order_by('-id')

    if not products:
        print("No products with design position data found.")
        return

    product = products[0]
    print(f"Testing product: {product.name} (ID: {product.id})")

    # Get the design position data
    design_position_data = product.design_position
    print(f"Design position data: {design_position_data}")

    # Parse the position data
    try:
        position_data = json.loads(design_position_data)
        print("Position data parsed successfully:")
        for key, value in position_data.items():
            print(f"  {key}: {value}")
    except json.JSONDecodeError:
        print("Error parsing position data")
        return

    # Get the design image path
    design_image_path = product.image.path
    print(f"Design image path: {design_image_path}")

    # Get available colors
    available_colors = product.available_colors.split(',')
    print(f"Available colors: {available_colors}")

    # Render the design on each available color
    for color in available_colors:
        print(f"\nRendering design on {color} t-shirt...")
        try:
            rendered_image = render_design_on_tshirt(
                design_image_path,
                color,
                design_position_data
            )

            # Save the rendered image to a temporary file for inspection
            temp_file = f"temp_rendered_{color}.jpg"
            with open(temp_file, 'wb') as f:
                f.write(rendered_image.getvalue())

            print(f"Rendered image saved to {temp_file}")

            # Open the rendered image and draw a red rectangle around the design area
            # This helps visualize where the design is positioned
            img = Image.open(temp_file)
            draw = ImageDraw.Draw(img)

            # Calculate the design position based on the position data
            try:
                if 'px' in position_data.get('left', ''):
                    left_px = float(position_data.get('left', '0').replace('px', ''))
                    top_px = float(position_data.get('top', '0').replace('px', ''))
                    width_px = float(position_data.get('width', '0').replace('px', ''))
                    height_px = float(position_data.get('height', '0').replace('px', ''))

                    # Get parent dimensions
                    parent_width = float(position_data.get('parent_width', 450))
                    parent_height = float(position_data.get('parent_height', 450))

                    # Convert to percentages
                    left_percent = left_px / parent_width
                    top_percent = top_px / parent_height
                    width_percent = width_px / parent_width
                    height_percent = height_px / parent_height
                else:
                    left_percent = float(position_data.get('left', '25%').replace('%', '')) / 100
                    top_percent = float(position_data.get('top', '25%').replace('%', '')) / 100
                    width_percent = float(position_data.get('width', '25%').replace('%', '')) / 100
                    height_percent = float(position_data.get('height', '25%').replace('%', '')) / 100

                # Calculate pixel values for the actual t-shirt image
                img_width, img_height = img.size
                design_width = int(img_width * width_percent)
                design_height = int(img_height * height_percent)
                left_pos = int(img_width * left_percent)
                top_pos = int(img_height * top_percent)

                # Draw a red rectangle around the design area
                draw.rectangle(
                    [(left_pos, top_pos), (left_pos + design_width, top_pos + design_height)],
                    outline="red",
                    width=3
                )

                # Save the image with the rectangle
                img.save(f"temp_rendered_{color}_with_rect.jpg")
                print(f"Image with position rectangle saved to temp_rendered_{color}_with_rect.jpg")

            except Exception as e:
                print(f"Error calculating design position: {str(e)}")

        except Exception as e:
            print(f"Error rendering design: {str(e)}")

    print("\nTest completed. Check the generated images to verify position consistency.")

if __name__ == "__main__":
    # Ensure test mockups exist
    ensure_test_mockups_exist()

    # Run the test
    test_design_position_consistency()
