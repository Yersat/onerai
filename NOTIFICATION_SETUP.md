# Order Notification System Setup Guide

This guide explains how to set up and configure the automated notification system for new orders in the onerai.kz marketplace.

## Overview

The notification system automatically sends notifications when customers complete checkout and create new orders. It supports:

- **Email notifications** - Detailed HTML emails with order information
- **Telegram notifications** - Instant messages to your Telegram channel/chat

## Features

- Automatic triggering when new orders are created
- Comprehensive order details in notifications
- Error handling and logging
- Test commands for verification
- Separate development and production configurations

## Setup Instructions

### 1. Email Configuration

#### For Development (Console Output)
The development settings are already configured to print emails to the console. No additional setup needed.

#### For Production (SMTP)
Add these environment variables to your `.env` file:

```bash
# Email settings
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your_email@onerai.kz
EMAIL_HOST_PASSWORD=your_app_password
DEFAULT_FROM_EMAIL=noreply@onerai.kz
ADMIN_EMAIL=info@fastdev.org  # This is where order notifications will be sent
```

**Note**: For Gmail, you'll need to use an App Password instead of your regular password.

### 2. Telegram Configuration (Optional)

#### Step 1: Create a Telegram Bot
1. Message @BotFather on Telegram
2. Send `/newbot` command
3. Follow the instructions to create your bot
4. Save the bot token

#### Step 2: Get Chat ID
1. Add your bot to a channel or group, OR
2. Start a private chat with your bot
3. Send a message to the bot/channel
4. Visit: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
5. Find the `chat.id` in the response

#### Step 3: Configure Environment Variables
Add these to your `.env` file:

```bash
# Telegram settings
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
```

## Testing the System

### Test Notification Services
```bash
python manage.py test_notifications --test-services
```

### Test with Existing Order
```bash
python manage.py test_notifications --order-id 123
```

### Create Test Order and Send Notifications
```bash
python manage.py test_notifications --create-test-order
```

## How It Works

1. **Signal Trigger**: When a new `Order` is created, Django's `post_save` signal triggers
2. **Notification Service**: The signal handler calls `NotificationService.send_order_notifications()`
3. **Email Service**: Sends HTML email with order details to the admin email
4. **Telegram Service**: Sends formatted message to the configured Telegram chat
5. **Error Handling**: Failures are logged but don't break the order creation process

## File Structure

```
store/
├── signals.py                          # Django signal handlers
├── services/
│   ├── __init__.py
│   ├── notification_service.py         # Main notification coordinator
│   ├── email_service.py               # Email notification service
│   └── telegram_service.py            # Telegram notification service
├── management/commands/
│   └── test_notifications.py          # Testing command
└── templates/emails/
    └── new_order_notification.html     # Email template
```

## Notification Content

### Email Notifications Include:
- Order number and date
- Customer information (name, email, phone)
- Shipping address
- Order status and payment status
- Detailed item list with prices
- Total amount
- Professional HTML formatting

### Telegram Notifications Include:
- Order summary with emojis
- Customer details
- Item count and total amount
- Order and payment status
- Compact, mobile-friendly format

## Troubleshooting

### Email Issues
- Check SMTP credentials in environment variables
- Verify Gmail App Password if using Gmail
- Check Django logs for detailed error messages
- Test with console backend first: `EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'`

### Telegram Issues
- Verify bot token is correct
- Ensure bot has permission to send messages to the chat
- Check that chat ID is correct (including negative sign for groups)
- Test bot connection: `python manage.py test_notifications --test-services`

### General Issues
- Check Django logs: `tail -f django.log`
- Verify signal is being triggered by creating a test order
- Ensure all required environment variables are set

## Production Deployment

1. Set all environment variables in your production `.env` file
2. Restart your Django application
3. Test the system with a real order or test command
4. Monitor logs for any issues

## Security Notes

- Keep bot tokens and email passwords secure
- Use environment variables, never hardcode credentials
- Consider using dedicated email service (SendGrid, Mailgun) for production
- Regularly rotate API keys and passwords

## Support

If you encounter issues:
1. Check the Django logs for error messages
2. Use the test commands to isolate problems
3. Verify all environment variables are correctly set
4. Test each service individually
