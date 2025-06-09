"""
Telegram service for sending order notifications.
"""

import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class TelegramService:
    """Service for sending Telegram notifications."""
    
    def __init__(self):
        self.bot_token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
        self.chat_id = getattr(settings, 'TELEGRAM_CHAT_ID', None)
        self.api_url = f"https://api.telegram.org/bot{self.bot_token}"
    
    def is_configured(self):
        """Check if Telegram service is properly configured."""
        return bool(self.bot_token and self.chat_id)
    
    def send_order_notification(self, order):
        """
        Send Telegram notification for a new order.
        
        Args:
            order: Order instance
            
        Returns:
            bool: True if message was sent successfully, False otherwise
        """
        if not self.is_configured():
            logger.warning("Telegram service not configured. Skipping Telegram notification.")
            return False
        
        try:
            # Format message
            message = self.format_order_message(order)
            
            # Send message
            response = requests.post(
                f"{self.api_url}/sendMessage",
                data={
                    'chat_id': self.chat_id,
                    'text': message,
                    'parse_mode': 'HTML'
                },
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info(f"Telegram notification sent successfully for order #{order.id}")
                return True
            else:
                logger.error(f"Failed to send Telegram notification for order #{order.id}. Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to send Telegram notification for order #{order.id}: {str(e)}")
            return False
    
    def format_order_message(self, order):
        """
        Format order details for Telegram message.
        
        Args:
            order: Order instance
            
        Returns:
            str: Formatted message for Telegram
        """
        # Calculate total items
        total_items = sum(item.quantity for item in order.items.all())
        
        message_parts = [
            "🛍️ <b>Новый заказ на onerai.kz!</b>",
            "",
            f"📋 <b>Заказ:</b> #{order.id}",
            f"📅 <b>Дата:</b> {order.created_at.strftime('%d.%m.%Y %H:%M')}",
            f"👤 <b>Клиент:</b> {order.user.get_full_name() or order.user.username}",
            f"📧 <b>Email:</b> {order.user.email}",
        ]
        
        if order.shipping_address:
            message_parts.extend([
                f"📞 <b>Телефон:</b> {order.shipping_address.phone}",
                f"📍 <b>Адрес:</b> {order.shipping_address.get_full_address()}",
            ])
        
        message_parts.extend([
            f"💰 <b>Сумма:</b> {order.total_price} ₸",
            f"📦 <b>Товаров:</b> {total_items} шт.",
            f"🔄 <b>Статус:</b> {order.get_status_display()}",
            f"💳 <b>Оплата:</b> {order.get_payment_status_display()}",
            "",
            "<b>Товары в заказе:</b>"
        ])
        
        for item in order.items.all():
            message_parts.append(
                f"• {item.product.name} ({item.size}, {item.color}) "
                f"x{item.quantity} = {item.get_total_price()} ₸"
            )
        
        return "\n".join(message_parts)
    
    def test_connection(self):
        """
        Test Telegram bot connection.
        
        Returns:
            bool: True if connection is successful, False otherwise
        """
        if not self.is_configured():
            return False
        
        try:
            response = requests.get(f"{self.api_url}/getMe", timeout=10)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Telegram connection test failed: {str(e)}")
            return False
