#!/usr/bin/env python
"""
Test script to verify the complete Freedom Pay payment flow.
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
from django.http import HttpRequest
from store.freedompay_service import FreedomPayService
from store.models import Order, ShippingAddress
from store.views import freedompay_result
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


def test_payment_initialization():
    """Test payment initialization."""
    
    print("=== Testing Payment Initialization ===")
    
    # Create test order
    order = create_test_order()
    print(f"Created test order: {order.id}")
    
    # Create mock request
    factory = RequestFactory()
    request = factory.post('/checkout/', HTTP_HOST='127.0.0.1:8000')
    request.META['REMOTE_ADDR'] = '127.0.0.1'
    
    # Initialize Freedom Pay service
    service = FreedomPayService()
    
    # Test payment initialization
    result = service.init_payment(order, request)
    
    if result.get('success'):
        print("✅ Payment initialization successful!")
        payment_data = result.get('data', {})
        print(f"  Payment ID: {payment_data.get('pg_payment_id')}")
        print(f"  Redirect URL: {payment_data.get('pg_redirect_url')}")
        
        # Store payment ID in order for callback testing
        order.payment_id = payment_data.get('pg_payment_id')
        order.save()
        
        return order, payment_data
    else:
        print("❌ Payment initialization failed!")
        print(f"  Error: {result.get('error')}")
        order.delete()
        return None, None


def test_callback_processing(order, payment_id):
    """Test callback processing."""
    
    print("\n=== Testing Callback Processing ===")
    
    if not order or not payment_id:
        print("❌ No order or payment ID to test callback")
        return
    
    # Initialize Freedom Pay service
    service = FreedomPayService()
    
    # Create mock callback data (successful payment)
    callback_data = {
        'pg_order_id': str(order.id),
        'pg_payment_id': payment_id,
        'pg_result': '1',  # Success
        'pg_amount': str(order.total_price),
        'pg_currency': 'KZT',
        'pg_salt': service.generate_salt(),
    }
    
    # Generate signature for callback (empty script name)
    callback_data['pg_sig'] = service.generate_signature('', callback_data)
    
    print(f"Testing callback with data: {callback_data}")
    
    # Test callback processing
    result = service.process_payment_result(callback_data)
    
    print(f"Callback processing result:")
    print(f"  Status: {result.get('status')}")
    print(f"  Description: {result.get('description')}")
    print(f"  Order ID: {result.get('order_id')}")
    print(f"  Payment ID: {result.get('payment_id')}")
    
    if result.get('status') == 'ok':
        print("✅ Callback processing successful!")
        
        # Check if order was updated
        order.refresh_from_db()
        print(f"  Order payment status: {order.payment_status}")
        print(f"  Order status: {order.status}")
        
        return True
    else:
        print("❌ Callback processing failed!")
        return False


def main():
    """Run the complete payment flow test."""
    
    print("=== Complete Freedom Pay Payment Flow Test ===")
    print(f"Using Freedom Pay test environment")
    print()
    
    try:
        # Test 1: Payment initialization
        order, payment_data = test_payment_initialization()
        
        if order and payment_data:
            payment_id = payment_data.get('pg_payment_id')
            
            # Test 2: Callback processing
            callback_success = test_callback_processing(order, payment_id)
            
            if callback_success:
                print("\n✅ Complete payment flow test PASSED!")
            else:
                print("\n❌ Callback processing test FAILED!")
            
            # Clean up
            order.delete()
            print(f"\nCleaned up test order {order.id}")
        else:
            print("\n❌ Payment initialization test FAILED!")
            
    except Exception as e:
        print(f"\n❌ Test failed with exception: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
