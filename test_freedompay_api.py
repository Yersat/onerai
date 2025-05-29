#!/usr/bin/env python
"""
Test script to make a real Freedom Pay API call and debug signature issues.
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

from django.test import RequestFactory
from store.freedompay_service import FreedomPayService
from store.models import Order, ShippingAddress
from django.contrib.auth import get_user_model

User = get_user_model()


def create_test_order():
    """Create a test order for payment testing."""

    # Create a test user
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User'
        }
    )

    # Create shipping address
    shipping_address, created = ShippingAddress.objects.get_or_create(
        user=user,
        defaults={
            'full_name': 'Test User',
            'phone': '77777777777',
            'address': 'Test Address',
            'city': 'Almaty',
            'postal_code': '050000'
        }
    )

    # Create test order
    order = Order.objects.create(
        user=user,
        shipping_address=shipping_address,
        total_price=1000.00,
        status=Order.STATUS_PENDING,
        payment_status=Order.PAYMENT_STATUS_PENDING
    )

    return order


def test_freedom_pay_api():
    """Test actual Freedom Pay API call."""

    print("=== Testing Freedom Pay API Call ===")

    # Create test order
    order = create_test_order()
    print(f"Created test order: {order.id}")

    # Create mock request
    factory = RequestFactory()
    request = factory.post('/checkout/', HTTP_HOST='127.0.0.1:8000')
    request.META['REMOTE_ADDR'] = '127.0.0.1'

    # Initialize Freedom Pay service
    service = FreedomPayService()

    print(f"Using credentials:")
    print(f"  Merchant ID: {service.merchant_id}")
    print(f"  Secret Key: {service.secret_key}")
    print(f"  API URL: {service.api_url}")
    print(f"  Testing Mode: {service.testing_mode}")
    print()

    # Test payment initialization
    print("Initializing payment...")
    try:
        result = service.init_payment(order, request)

        print(f"Payment initialization result:")
        print(f"  Success: {result.get('success')}")
        print(f"  Data: {result.get('data')}")
        print(f"  Error: {result.get('error')}")

        if result.get('success'):
            print("✅ Payment initialization successful!")
            payment_data = result.get('data', {})
            print(f"  Payment ID: {payment_data.get('pg_payment_id')}")
            print(f"  Redirect URL: {payment_data.get('pg_redirect_url')}")
        else:
            print("❌ Payment initialization failed!")
            print(f"  Error: {result.get('error')}")

    except Exception as e:
        print(f"❌ Exception during payment initialization: {e}")
        import traceback
        traceback.print_exc()

    # Clean up
    order.delete()
    print(f"\nCleaned up test order {order.id}")


if __name__ == '__main__':
    test_freedom_pay_api()
