# 🔧 Notification Issues - Diagnosis & Fixes

## Issues Identified and Fixed

### ❌ **Issue 1: Duplicate Telegram Messages**

**Root Cause**: The test command was triggering notifications twice:
1. Automatically via Django signal when `Order.objects.create()` was called
2. Manually via `notification_service.send_order_notifications(order)` in the test command

**Fix Applied**: ✅
- Modified `test_notifications.py` to remove the manual notification trigger
- Now only the Django signal sends notifications (preventing duplicates)

### ❌ **Issue 2: Missing Email Notifications**

**Root Cause**: Email backend was set to `console.EmailBackend` which only prints emails to console instead of actually sending them.

**Fix Applied**: ✅
- Updated Django settings to use SMTP backend for real email delivery
- Added proper email configuration with environment variable support
- Created email testing commands for debugging

## 🛠️ **Fixes Implemented**

### 1. Fixed Duplicate Notifications

**File**: `store/management/commands/test_notifications.py`
- Removed manual notification trigger in test command
- Now relies only on Django signal for automatic notifications

### 2. Fixed Email Configuration

**File**: `onerai/settings.py`
```python
# Updated email settings
EMAIL_BACKEND = os.environ.get('EMAIL_BACKEND', 'django.core.mail.backends.smtp.EmailBackend')
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '587'))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
```

### 3. Added Email Testing Tools

**New File**: `store/management/commands/test_email.py`
- Check email configuration
- Send simple test emails
- Test order notification templates

## 📧 **Email Configuration Setup**

To receive real email notifications, you need to configure SMTP settings:

### Option 1: Using Gmail (Recommended)

1. **Enable 2-Factor Authentication** on your Gmail account
2. **Generate App Password**:
   - Go to Google Account settings
   - Security → 2-Step Verification → App passwords
   - Generate password for "Mail"
3. **Set Environment Variables**:

```bash
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your_email@fastdev.org
EMAIL_HOST_PASSWORD=your_16_character_app_password
```

### Option 2: Console Backend (Development Only)

```bash
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

## 🧪 **Testing Commands**

### Test Email Configuration
```bash
python manage.py test_email --check-config
```

### Send Simple Test Email
```bash
python manage.py test_email --simple
```

### Test Order Notification Template
```bash
python manage.py test_email --order-template
```

### Test Complete Notification System (Fixed)
```bash
python manage.py test_notifications --create-test-order
```

### Test Services Configuration
```bash
python manage.py test_notifications --test-services
```

## ✅ **Verification Steps**

### 1. Check Email Configuration
```bash
python manage.py test_email --check-config
```
**Expected Output**:
- EMAIL_BACKEND: django.core.mail.backends.smtp.EmailBackend
- EMAIL_HOST: smtp.gmail.com
- EMAIL_HOST_USER: your_email@fastdev.org
- ✅ SMTP backend configured
- ✅ Admin email set to: info@fastdev.org

### 2. Test Simple Email
```bash
python manage.py test_email --simple
```
**Expected**: ✅ Test email sent to info@fastdev.org

### 3. Test Complete System
```bash
python manage.py test_notifications --create-test-order
```
**Expected**:
- ✅ One email notification to info@fastdev.org
- ✅ One Telegram notification to your chat
- ❌ No duplicate messages

## 🔍 **Troubleshooting Guide**

### Email Issues

#### Problem: "Authentication failed"
**Solution**: 
- Use Gmail App Password (not regular password)
- Enable 2-Factor Authentication first

#### Problem: "SMTPAuthenticationError"
**Solution**:
- Verify EMAIL_HOST_USER and EMAIL_HOST_PASSWORD
- Check if "Less secure app access" is enabled (not recommended)

#### Problem: Emails not received
**Solution**:
- Check spam folder
- Verify ADMIN_EMAIL is correct
- Test with simple email first

### Telegram Issues

#### Problem: Duplicate messages
**Solution**: ✅ Fixed - use only signal-based notifications

#### Problem: No Telegram notifications
**Solution**:
- Check bot token and chat ID
- Run: `python manage.py test_notifications --test-services`

## 🚀 **Production Deployment**

### Environment Variables to Set:
```bash
# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your_email@fastdev.org
EMAIL_HOST_PASSWORD=your_app_password
ADMIN_EMAIL=info@fastdev.org

# Telegram Configuration (already set)
TELEGRAM_BOT_TOKEN=7616528096:AAFEgelyZX5sPOz1hT5-xmL0sk0ssiL3SFY
TELEGRAM_CHAT_ID=344949399
```

### Deployment Steps:
1. Set environment variables on server
2. Restart Django application
3. Test with: `python manage.py test_notifications --create-test-order`
4. Verify single notifications received

## 📊 **Expected Behavior After Fixes**

### When Customer Places Order:
1. **One email notification** → Sent to info@fastdev.org
2. **One Telegram notification** → Sent to your chat
3. **No duplicates** → Each notification sent exactly once
4. **Real email delivery** → Actual emails (not console output)

### Logging Output:
```
INFO: New order created: #XX
INFO: Sending notifications for order #XX
INFO: Order notification email sent successfully for order #XX
INFO: Telegram notification sent successfully for order #XX
INFO: All notifications sent successfully for order #XX
INFO: Notifications sent successfully for order #XX
```

## ✅ **Status: FIXED**

Both issues have been resolved:
- ✅ Duplicate notifications eliminated
- ✅ Email delivery configured for real SMTP
- ✅ Testing tools added for debugging
- ✅ Documentation updated

The notification system is now ready for reliable production use!
