#!/usr/bin/env python
"""
Check the status of order #13 from the payment transaction.
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).resolve().parent
sys.path.insert(0, str(project_root))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'onerai.settings')

import django
django.setup()

from store.models import Order

def check_order_status():
    """Check the status of order #13."""

    try:
        order = Order.objects.get(id=13)

        print("=== Order #13 Status ===")
        print(f"Order ID: {order.id}")
        print(f"User: {order.user.username}")
        print(f"Total Price: {order.total_price}")
        print(f"Order Status: {order.status}")
        print(f"Payment Status: {order.payment_status}")
        print(f"Payment ID: {order.payment_id}")
        print(f"Created: {order.created_at}")
        print(f"Updated: {order.updated_at}")

        # Check shipping address
        if order.shipping_address:
            print(f"\nShipping Address:")
            print(f"  Name: {order.shipping_address.full_name}")
            print(f"  Phone: {order.shipping_address.phone}")
            print(f"  Address: {order.shipping_address.address}")
            print(f"  City: {order.shipping_address.city}")

        # Check order items
        items = order.items.all()
        print(f"\nOrder Items ({items.count()}):")
        for item in items:
            print(f"  - {item.product.name}: {item.quantity} x {item.price} = {item.get_total_price()}")

        return order

    except Order.DoesNotExist:
        print("❌ Order #13 not found")
        return None
    except Exception as e:
        print(f"❌ Error checking order: {e}")
        return None

if __name__ == '__main__':
    check_order_status()
