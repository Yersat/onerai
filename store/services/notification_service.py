"""
Main notification service that coordinates email and Telegram notifications.
"""

import logging
from django.conf import settings
from .email_service import EmailService
from .telegram_service import TelegramService

logger = logging.getLogger(__name__)


class NotificationService:
    """Main service for handling all order notifications."""
    
    def __init__(self):
        self.email_service = EmailService()
        self.telegram_service = TelegramService()
    
    def send_order_notifications(self, order):
        """
        Send all configured notifications for a new order.
        
        Args:
            order: Order instance
            
        Returns:
            dict: Results of notification attempts
        """
        results = {
            'email': False,
            'telegram': False,
            'errors': []
        }
        
        logger.info(f"Sending notifications for order #{order.id}")
        
        # Send email notification
        try:
            results['email'] = self.email_service.send_order_notification(order)
            if not results['email']:
                results['errors'].append("Email notification failed")
        except Exception as e:
            results['errors'].append(f"Email notification error: {str(e)}")
            logger.error(f"Email notification error for order #{order.id}: {str(e)}")
        
        # Send Telegram notification
        try:
            results['telegram'] = self.telegram_service.send_order_notification(order)
            if not results['telegram'] and self.telegram_service.is_configured():
                results['errors'].append("Telegram notification failed")
        except Exception as e:
            results['errors'].append(f"Telegram notification error: {str(e)}")
            logger.error(f"Telegram notification error for order #{order.id}: {str(e)}")
        
        # Log summary - prioritize Telegram notifications
        telegram_configured = self.telegram_service.is_configured()
        email_enabled = getattr(settings, 'EMAIL_BACKEND', '').endswith('smtp.EmailBackend')

        if telegram_configured and results['telegram']:
            logger.info(f"Telegram notification sent successfully for order #{order.id}")
        elif telegram_configured and not results['telegram']:
            logger.error(f"Telegram notification failed for order #{order.id}")

        if email_enabled and results['email']:
            logger.info(f"Email notification sent successfully for order #{order.id}")
        elif email_enabled and not results['email']:
            logger.warning(f"Email notification failed for order #{order.id}")

        # Overall success if at least one notification method works
        if results['telegram'] or results['email']:
            logger.info(f"Order #{order.id} notifications completed")
        else:
            logger.error(f"All notifications failed for order #{order.id}")
        
        return results
    
    def test_all_services(self):
        """
        Test all notification services.
        
        Returns:
            dict: Test results for each service
        """
        results = {
            'email': True,  # Email service doesn't have a specific test method
            'telegram': self.telegram_service.test_connection() if self.telegram_service.is_configured() else None
        }
        
        return results
