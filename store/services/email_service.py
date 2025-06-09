"""
Email service for sending order notifications.
"""

import logging
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending email notifications."""
    
    def __init__(self):
        self.from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@onerai.kz')
        self.admin_email = getattr(settings, 'ADMIN_EMAIL', 'admin@onerai.kz')
    
    def send_order_notification(self, order):
        """
        Send email notification for a new order.
        
        Args:
            order: Order instance
            
        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        try:
            # Prepare email context
            context = {
                'order': order,
                'order_items': order.items.all(),
                'customer': order.user,
                'shipping_address': order.shipping_address,
                'total_items': sum(item.quantity for item in order.items.all()),
            }
            
            # Render email template
            html_message = render_to_string('emails/new_order_notification.html', context)
            plain_message = strip_tags(html_message)
            
            # Email subject
            subject = f'Новый заказ #{order.id} на onerai.kz'
            
            # Send email
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=self.from_email,
                recipient_list=[self.admin_email],
                html_message=html_message,
                fail_silently=False,
            )
            
            logger.info(f"Order notification email sent successfully for order #{order.id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send order notification email for order #{order.id}: {str(e)}")
            return False
    
    def format_order_details(self, order):
        """
        Format order details for email content.
        
        Args:
            order: Order instance
            
        Returns:
            str: Formatted order details
        """
        details = []
        details.append(f"Номер заказа: #{order.id}")
        details.append(f"Дата заказа: {order.created_at.strftime('%d.%m.%Y %H:%M')}")
        details.append(f"Клиент: {order.user.get_full_name() or order.user.username}")
        details.append(f"Email клиента: {order.user.email}")
        details.append(f"Телефон: {order.shipping_address.phone if order.shipping_address else 'Не указан'}")
        details.append(f"Общая сумма: {order.total_price} ₸")
        details.append(f"Статус: {order.get_status_display()}")
        details.append(f"Статус оплаты: {order.get_payment_status_display()}")
        
        if order.shipping_address:
            details.append(f"Адрес доставки: {order.shipping_address.get_full_address()}")
        
        details.append("\nТовары в заказе:")
        for item in order.items.all():
            details.append(f"- {item.product.name} ({item.size}, {item.color}) x{item.quantity} = {item.get_total_price()} ₸")
        
        return "\n".join(details)
