"""
Freedom Pay payment service integration for onerai.kz marketplace.
Handles payment initialization, signature generation, and callback processing.
"""

import hashlib
import secrets
import string
import requests
import xmltodict
from decimal import Decimal
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class FreedomPayService:
    """Service class for Freedom Pay payment integration."""

    def __init__(self):
        self.merchant_id = settings.FREEDOM_PAY_MERCHANT_ID
        self.secret_key = settings.FREEDOM_PAY_SECRET_KEY
        self.api_url = settings.FREEDOM_PAY_API_URL
        self.testing_mode = settings.FREEDOM_PAY_TESTING_MODE

        if not self.merchant_id or not self.secret_key:
            raise ValueError("Freedom Pay credentials not configured in settings")

    def generate_salt(self, length: int = 16) -> str:
        """Generate random salt for signature."""
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(length))

    def generate_signature(self, script_name: str, params: Dict[str, Any]) -> str:
        """
        Generate MD5 signature for Freedom Pay API request.

        Args:
            script_name: Name of the API endpoint script
            params: Dictionary of parameters to sign

        Returns:
            MD5 signature string
        """
        # Create a copy of params and add salt if not present
        sign_params = params.copy()
        if 'pg_salt' not in sign_params:
            sign_params['pg_salt'] = self.generate_salt()

        # Sort parameters alphabetically by key
        sorted_params = sorted(sign_params.items())

        # Create signature string: script_name;param1;param2;...;secret_key
        signature_parts = [script_name] if script_name else ['']
        signature_parts.extend([str(value) for key, value in sorted_params])
        signature_parts.append(self.secret_key)

        signature_string = ';'.join(signature_parts)

        # Generate MD5 hash
        signature = hashlib.md5(signature_string.encode('utf-8')).hexdigest()

        logger.debug(f"Signature generation:")
        logger.debug(f"  Script name: '{script_name}'")
        logger.debug(f"  Parameters: {dict(sorted_params)}")
        logger.debug(f"  Signature string: {signature_string}")
        logger.debug(f"  Generated signature: {signature}")

        return signature

    def init_payment(self, order, request) -> Dict[str, Any]:
        """
        Initialize payment with Freedom Pay.

        Args:
            order: Order instance
            request: Django request object

        Returns:
            Dictionary with payment initialization response
        """
        # Note: Using real Freedom Pay credentials now

        # Build callback URLs
        result_url = request.build_absolute_uri(reverse('store:freedompay_result'))
        success_url = request.build_absolute_uri(reverse('store:freedompay_success'))
        failure_url = request.build_absolute_uri(reverse('store:freedompay_failure'))

        # Prepare payment parameters
        params = {
            'pg_order_id': str(order.id),
            'pg_merchant_id': self.merchant_id,
            'pg_amount': str(order.total_price),
            'pg_description': f'Заказ #{order.id} на onerai.kz',
            'pg_currency': 'KZT',
            'pg_result_url': result_url,
            'pg_success_url': success_url,
            'pg_failure_url': failure_url,
            'pg_request_method': 'POST',
            'pg_success_url_method': 'GET',
            'pg_failure_url_method': 'GET',
            'pg_testing_mode': self.testing_mode,
            'pg_user_phone': order.shipping_address.phone,
            'pg_user_contact_email': order.user.email,
            'pg_user_ip': self.get_client_ip(request),
            'pg_language': 'ru',
            'pg_lifetime': '3600',  # 1 hour
        }

        # Generate salt and signature
        params['pg_salt'] = self.generate_salt()
        params['pg_sig'] = self.generate_signature('init_payment.php', params)

        try:
            # Make API request
            response = requests.post(
                f"{self.api_url}/init_payment.php",
                data=params,
                timeout=30
            )
            response.raise_for_status()

            # Parse XML response
            response_data = xmltodict.parse(response.text)

            if 'response' in response_data:
                result = response_data['response']

                # Verify response signature
                if self.verify_response_signature(result):
                    return {
                        'success': True,
                        'data': result
                    }
                else:
                    logger.error("Invalid response signature from Freedom Pay")
                    return {
                        'success': False,
                        'error': 'Invalid response signature'
                    }
            else:
                logger.error(f"Invalid response format: {response.text}")
                return {
                    'success': False,
                    'error': 'Invalid response format'
                }

        except requests.RequestException as e:
            logger.error(f"Freedom Pay API request failed: {e}")
            return {
                'success': False,
                'error': f'Payment service unavailable: {e}'
            }
        except Exception as e:
            logger.error(f"Payment initialization failed: {e}")
            return {
                'success': False,
                'error': f'Payment initialization failed: {e}'
            }

    def _mock_payment_init(self, order, request) -> Dict[str, Any]:
        """
        Mock payment initialization for testing with test credentials.

        Args:
            order: Order instance
            request: Django request object

        Returns:
            Dictionary with mock payment response
        """
        # Build callback URLs
        success_url = request.build_absolute_uri(reverse('store:freedompay_success'))

        # Generate a mock payment ID
        mock_payment_id = f"test_payment_{order.id}_{self.generate_salt(8)}"

        # Create a mock redirect URL that will simulate the payment page
        mock_redirect_url = f"{success_url}?pg_order_id={order.id}&pg_payment_id={mock_payment_id}&test_mode=1"

        logger.info(f"Mock payment initialized for order {order.id}")

        return {
            'success': True,
            'data': {
                'pg_payment_id': mock_payment_id,
                'pg_redirect_url': mock_redirect_url,
                'pg_status': 'ok'
            }
        }

    def verify_response_signature(self, response_data: Dict[str, Any]) -> bool:
        """
        Verify signature in Freedom Pay response.

        Args:
            response_data: Response data from Freedom Pay

        Returns:
            True if signature is valid, False otherwise
        """
        logger.debug(f"Verifying response signature for data: {response_data}")

        if 'pg_sig' not in response_data:
            logger.error("Missing pg_sig in response data")
            return False

        if 'pg_salt' not in response_data:
            logger.error("Missing pg_salt in response data")
            return False

        received_signature = response_data['pg_sig']
        logger.debug(f"Received signature: {received_signature}")

        # Remove signature from params for verification
        verify_params = response_data.copy()
        del verify_params['pg_sig']

        # Generate expected signature (use 'init_payment.php' script name for responses)
        expected_signature = self.generate_signature('init_payment.php', verify_params)

        logger.debug(f"Expected signature: {expected_signature}")
        signature_matches = received_signature.lower() == expected_signature.lower()
        logger.debug(f"Signatures match: {signature_matches}")

        if not signature_matches:
            logger.error(f"Response signature mismatch: received={received_signature}, expected={expected_signature}")

        # If signatures don't match, run debug to find the correct script name (only in debug mode)
        if not signature_matches and settings.DEBUG:
            self.debug_signature_mismatch(received_signature, verify_params)

        return signature_matches

    def debug_signature_mismatch(self, received_sig: str, response_data: Dict[str, Any]) -> None:
        """
        Debug signature mismatch by trying different script names.

        Args:
            received_sig: The signature received from Freedom Pay
            response_data: The response data without pg_sig
        """
        logger.error("=== SIGNATURE MISMATCH DEBUG ===")
        logger.error(f"Received signature: {received_sig}")

        # Try different script names that might be used by Freedom Pay
        script_names_to_try = [
            '',  # Empty (current approach)
            'init_payment.php',  # Request script name
            'result',  # Result callback
            'check',   # Check callback
        ]

        for script_name in script_names_to_try:
            try:
                test_signature = self.generate_signature(script_name, response_data)
                matches = received_sig.lower() == test_signature.lower()
                logger.error(f"Script name '{script_name}': {test_signature} - {'MATCH' if matches else 'NO MATCH'}")
                if matches:
                    logger.error(f"*** FOUND MATCHING SCRIPT NAME: '{script_name}' ***")
            except Exception as e:
                logger.error(f"Error testing script name '{script_name}': {e}")

        logger.error("=== END SIGNATURE DEBUG ===")

    def get_client_ip(self, request) -> str:
        """Get client IP address from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip or '127.0.0.1'

    def process_payment_result(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process payment result callback from Freedom Pay.

        Args:
            request_data: POST data from Freedom Pay callback

        Returns:
            Dictionary with processing result
        """
        try:
            # Verify signature
            if not self.verify_callback_signature(request_data):
                logger.error("Invalid callback signature")
                return {
                    'status': 'error',
                    'description': 'Invalid signature'
                }

            order_id = request_data.get('pg_order_id')
            payment_id = request_data.get('pg_payment_id')
            result = request_data.get('pg_result')

            if not order_id:
                logger.error("Missing order ID in callback")
                return {
                    'status': 'error',
                    'description': 'Missing order ID'
                }

            # Process payment result
            if result == '1':  # Success
                return {
                    'status': 'ok',
                    'description': 'Payment accepted',
                    'order_id': order_id,
                    'payment_id': payment_id
                }
            else:  # Failure
                return {
                    'status': 'rejected',
                    'description': 'Payment failed',
                    'order_id': order_id,
                    'payment_id': payment_id
                }

        except Exception as e:
            logger.error(f"Payment result processing failed: {e}")
            return {
                'status': 'error',
                'description': f'Processing failed: {e}'
            }

    def verify_callback_signature(self, request_data: Dict[str, Any]) -> bool:
        """
        Verify signature in Freedom Pay callback.

        Args:
            request_data: POST data from Freedom Pay

        Returns:
            True if signature is valid, False otherwise
        """
        logger.debug(f"Verifying callback signature for data: {request_data}")

        if 'pg_sig' not in request_data:
            logger.error("Missing pg_sig in callback data")
            return False

        if 'pg_salt' not in request_data:
            logger.error("Missing pg_salt in callback data")
            return False

        received_signature = request_data['pg_sig']
        logger.debug(f"Received callback signature: {received_signature}")

        # Remove signature from params for verification
        verify_params = request_data.copy()
        del verify_params['pg_sig']

        # Generate expected signature (empty script name for callbacks)
        # Note: Callbacks use empty script name, unlike init_payment responses
        expected_signature = self.generate_signature('', verify_params)

        logger.debug(f"Expected callback signature: {expected_signature}")
        signature_matches = received_signature.lower() == expected_signature.lower()
        logger.debug(f"Callback signatures match: {signature_matches}")

        if not signature_matches:
            logger.error(f"Callback signature mismatch: received={received_signature}, expected={expected_signature}")

        # If signatures don't match, run debug to find the correct script name (only in debug mode)
        if not signature_matches and settings.DEBUG:
            self.debug_signature_mismatch(received_signature, verify_params)

        return signature_matches
