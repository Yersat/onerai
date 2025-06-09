"""
Django signals for the store app.
Handles notifications when orders are created.
"""

import logging
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order
from .services.notification_service import NotificationService

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Order)
def order_created_notification(sender, instance, created, **kwargs):
    """
    Signal handler that triggers notifications when a new order is created.
    
    Args:
        sender: The model class (Order)
        instance: The actual instance being saved
        created: Boolean indicating if this is a new instance
        **kwargs: Additional keyword arguments
    """
    if created:  # Only trigger for new orders, not updates
        logger.info(f"New order created: #{instance.id}")
        
        try:
            # Initialize notification service
            notification_service = NotificationService()
            
            # Send notifications
            notification_service.send_order_notifications(instance)
            
            logger.info(f"Notifications sent successfully for order #{instance.id}")
            
        except Exception as e:
            logger.error(f"Failed to send notifications for order #{instance.id}: {str(e)}")
            # Don't raise the exception to avoid breaking the order creation process
