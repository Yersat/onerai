"""
Django management command to help get Telegram Chat ID.
"""

import requests
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = 'Get Telegram Chat ID for bot configuration'

    def handle(self, *args, **options):
        bot_token = getattr(settings, 'TELEGRAM_BOT_TOKEN', '')
        
        if not bot_token:
            self.stdout.write(
                self.style.ERROR('TELEGRAM_BOT_TOKEN not configured in settings')
            )
            return
        
        self.stdout.write("🤖 Telegram Bot Setup Helper")
        self.stdout.write("=" * 50)
        
        # Test bot connection
        try:
            response = requests.get(f"https://api.telegram.org/bot{bot_token}/getMe", timeout=10)
            if response.status_code == 200:
                bot_info = response.json()
                if bot_info.get('ok'):
                    bot_data = bot_info['result']
                    self.stdout.write(f"✅ Bot connected successfully!")
                    self.stdout.write(f"   Bot Name: {bot_data.get('first_name')}")
                    self.stdout.write(f"   Username: @{bot_data.get('username')}")
                else:
                    self.stdout.write(self.style.ERROR("❌ Bot token is invalid"))
                    return
            else:
                self.stdout.write(self.style.ERROR(f"❌ Failed to connect to bot: {response.status_code}"))
                return
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error connecting to bot: {str(e)}"))
            return
        
        self.stdout.write("\n📋 To get your Chat ID, follow these steps:")
        self.stdout.write("1. Open Telegram and search for: @oneraineworder_bot")
        self.stdout.write("2. Start a conversation with the bot")
        self.stdout.write("3. Send any message (e.g., 'Hello' or '/start')")
        self.stdout.write("4. Run this command again to see your Chat ID")
        
        # Check for recent messages
        try:
            response = requests.get(f"https://api.telegram.org/bot{bot_token}/getUpdates", timeout=10)
            if response.status_code == 200:
                updates = response.json()
                if updates.get('ok') and updates.get('result'):
                    self.stdout.write("\n💬 Recent messages found:")
                    for update in updates['result'][-5:]:  # Show last 5 messages
                        if 'message' in update:
                            message = update['message']
                            chat = message.get('chat', {})
                            from_user = message.get('from', {})
                            
                            chat_id = chat.get('id')
                            chat_type = chat.get('type')
                            username = from_user.get('username', 'No username')
                            first_name = from_user.get('first_name', 'Unknown')
                            
                            self.stdout.write(f"   Chat ID: {chat_id}")
                            self.stdout.write(f"   Type: {chat_type}")
                            self.stdout.write(f"   From: {first_name} (@{username})")
                            self.stdout.write(f"   Message: {message.get('text', 'No text')}")
                            self.stdout.write("   " + "-" * 30)
                            
                            if chat_type == 'private':
                                self.stdout.write(f"\n🎯 Use this Chat ID for private notifications: {chat_id}")
                                self.stdout.write(f"   Add this to your .env file:")
                                self.stdout.write(f"   TELEGRAM_CHAT_ID={chat_id}")
                else:
                    self.stdout.write("\n📭 No messages found yet.")
                    self.stdout.write("   Please send a message to the bot first.")
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error getting updates: {str(e)}"))
        
        self.stdout.write("\n🔧 Alternative setup options:")
        self.stdout.write("• For group notifications: Add bot to a group and get group Chat ID")
        self.stdout.write("• For channel notifications: Add bot to a channel and get channel Chat ID")
        self.stdout.write("\n📖 For more help, see: NOTIFICATION_SETUP.md")
