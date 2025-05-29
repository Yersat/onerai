#!/usr/bin/env python
"""
Test script to verify Freedom Pay signature generation against documentation examples.
"""

import hashlib
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

from store.freedompay_service import FreedomPayService


def test_signature_generation():
    """Test signature generation against Freedom Pay documentation examples."""
    
    print("=== Testing Freedom Pay Signature Generation ===")
    
    # Initialize service with test credentials
    service = FreedomPayService()
    
    print(f"Merchant ID: {service.merchant_id}")
    print(f"Secret Key: {service.secret_key}")
    print()
    
    # Test case 1: Basic init_payment.php signature from documentation
    print("Test 1: Basic init_payment.php signature")
    test_params = {
        'pg_order_id': '23',
        'pg_merchant_id': service.merchant_id,
        'pg_amount': '25',
        'pg_description': 'test',
        'pg_salt': 'molbulak',
    }
    
    signature = service.generate_signature('init_payment.php', test_params)
    print(f"Generated signature: {signature}")
    
    # Manual calculation for verification
    sorted_params = sorted(test_params.items())
    signature_parts = ['init_payment.php']
    signature_parts.extend([str(value) for key, value in sorted_params])
    signature_parts.append(service.secret_key)
    signature_string = ';'.join(signature_parts)
    manual_signature = hashlib.md5(signature_string.encode('utf-8')).hexdigest()
    
    print(f"Manual signature string: {signature_string}")
    print(f"Manual signature: {manual_signature}")
    print(f"Signatures match: {signature == manual_signature}")
    print()
    
    # Test case 2: Response signature verification (empty script name)
    print("Test 2: Response signature verification")
    response_data = {
        'pg_status': 'ok',
        'pg_payment_id': '4567788',
        'pg_redirect_url': 'https://api.freedompay.kg/pay.html?customer=test',
        'pg_salt': 'bdwLavL9lg6It91b',
    }
    
    # Generate signature for this response
    response_signature = service.generate_signature('', response_data)
    print(f"Response signature: {response_signature}")
    
    # Test verification
    response_data_with_sig = response_data.copy()
    response_data_with_sig['pg_sig'] = response_signature
    
    verification_result = service.verify_response_signature(response_data_with_sig)
    print(f"Verification result: {verification_result}")
    print()
    
    # Test case 3: Test with actual credentials format
    print("Test 3: Test with actual project credentials")
    actual_params = {
        'pg_order_id': '1',
        'pg_merchant_id': '561533',
        'pg_amount': '1000',
        'pg_description': 'Test order',
        'pg_currency': 'KZT',
        'pg_salt': 'test123',
    }
    
    actual_signature = service.generate_signature('init_payment.php', actual_params)
    print(f"Actual signature: {actual_signature}")
    print()


if __name__ == '__main__':
    test_signature_generation()
