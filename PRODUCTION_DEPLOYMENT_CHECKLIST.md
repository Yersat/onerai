# 🚀 Production Deployment Checklist - Telegram Notification System

## ✅ **Pre-Deployment Status**

### **Git Repository**
- ✅ **Committed**: All notification system files committed to main branch
- ✅ **Pushed**: Latest code pushed to GitHub repository
- ✅ **Commit Hash**: `92787e9` - "Implement Telegram-only notification system for order alerts"
- ✅ **Files Added**: 21 files changed, 1940 insertions

### **Local Testing**
- ✅ **Telegram notifications**: Working correctly
- ✅ **Email backend**: Configured as dummy (no SMTP errors)
- ✅ **Single notifications**: No duplicates
- ✅ **Signal system**: Automatic triggering verified

## 🌐 **Production Server Deployment Steps**

### **Step 1: Server Access**
```bash
ssh root@195.49.212.182
# or
ssh your_user@195.49.212.182
```

### **Step 2: Navigate to Project Directory**
```bash
cd /var/www/onerai
```

### **Step 3: Pull Latest Code**
```bash
git pull origin main
```
**Expected output**: Should show the new notification system files being pulled

### **Step 4: Activate Virtual Environment**
```bash
source venv/bin/activate
```

### **Step 5: Install Dependencies** (if needed)
```bash
pip install -r requirements.txt
```
**Note**: No new dependencies were added, but run this to be safe

### **Step 6: Configure Environment Variables**
```bash
nano .env
```

**Add/Update these variables**:
```bash
# Telegram Notifications (REQUIRED)
TELEGRAM_BOT_TOKEN=7616528096:AAFEgelyZX5sPOz1hT5-xmL0sk0ssiL3SFY
TELEGRAM_CHAT_ID=344949399

# Email Backend (DISABLED)
EMAIL_BACKEND=django.core.mail.backends.dummy.EmailBackend

# Other existing variables...
SECRET_KEY=your_production_secret_key
DEBUG=False
ALLOWED_HOSTS=onerai.kz,www.onerai.kz,195.49.212.182
# ... rest of your existing configuration
```

### **Step 7: Run Database Migrations**
```bash
python manage.py migrate
```

### **Step 8: Collect Static Files**
```bash
python manage.py collectstatic --noinput
```

### **Step 9: Test Notification System**
```bash
# Test services configuration
python manage.py test_notifications --test-services
```
**Expected output**:
```
Email service: ✓ Configured
Telegram service: ✓ Connected
```

```bash
# Test complete system
python manage.py test_notifications --create-test-order
```
**Expected**: Single Telegram notification sent to your chat

### **Step 10: Restart Services**
```bash
sudo systemctl restart onerai
sudo systemctl restart nginx
```

### **Step 11: Check Service Status**
```bash
sudo systemctl status onerai
sudo systemctl status nginx
```

## 🔍 **Post-Deployment Verification**

### **1. Website Accessibility**
- [ ] Visit https://onerai.kz - loads correctly
- [ ] Django admin accessible
- [ ] No 500 errors in browser

### **2. Notification System Test**
- [ ] Run: `python manage.py test_notifications --test-services`
- [ ] Result: Both services show as configured/connected
- [ ] Run: `python manage.py test_notifications --create-test-order`
- [ ] Result: Single Telegram message received

### **3. Real Order Test**
- [ ] Place a real test order through the website
- [ ] Verify single Telegram notification received
- [ ] Check order appears in Django admin
- [ ] No errors in application logs

### **4. Log Monitoring**
```bash
# Check application logs
tail -f /var/log/onerai/django.log

# Check for notification-related logs
grep -i "notification" /var/log/onerai/django.log

# Check for errors
grep -i "error" /var/log/onerai/django.log
```

## 📱 **Expected Telegram Notification Format**

When orders are placed, you should receive:

```
🛍️ Новый заказ на onerai.kz!

📋 Заказ: #XX
📅 Дата: DD.MM.YYYY HH:MM
👤 Клиент: Customer Name
📧 Email: customer@email.com
📞 Телефон: +7XXXXXXXXX
📍 Адрес: Full Address
💰 Сумма: XXXX ₸
📦 Товаров: X шт.
🔄 Статус: Ожидает подтверждения
💳 Оплата: Status

Товары в заказе:
• Product Name (Size, Color) xQuantity = Price ₸
```

## 🚨 **Troubleshooting**

### **Issue: Telegram notifications not working**
```bash
# Check bot token and chat ID
python manage.py test_notifications --test-services

# Check environment variables
echo $TELEGRAM_BOT_TOKEN
echo $TELEGRAM_CHAT_ID

# Check logs for Telegram errors
grep -i "telegram" /var/log/onerai/django.log
```

### **Issue: Django application not starting**
```bash
# Check service status
sudo systemctl status onerai

# Check logs
sudo journalctl -u onerai -f

# Check for syntax errors
python manage.py check
```

### **Issue: Website not accessible**
```bash
# Check Nginx status
sudo systemctl status nginx

# Check Nginx configuration
sudo nginx -t

# Check Nginx logs
sudo tail -f /var/log/nginx/error.log
```

## 📊 **Success Criteria**

### **✅ Deployment Successful When:**
1. **Website loads**: onerai.kz accessible without errors
2. **Telegram bot responds**: Test services show "Connected"
3. **Notifications work**: Test order creates single Telegram message
4. **No errors**: Application logs show no critical errors
5. **Real orders work**: Actual customer orders trigger notifications

### **📈 Monitoring**
- **Check logs daily**: Monitor for any notification failures
- **Test weekly**: Run test notifications to ensure system health
- **Monitor chat**: Ensure you're receiving order notifications

## 🎯 **Deployment Complete!**

Once all steps are completed and verified:

- ✅ **Telegram notifications**: Active for all new orders
- ✅ **No email errors**: Dummy backend prevents SMTP issues
- ✅ **Single notifications**: No duplicates
- ✅ **Production ready**: System monitoring customer orders

**Your onerai.kz marketplace now has a reliable, Telegram-only notification system!** 🎉

## 📞 **Support Commands**

Keep these handy for ongoing maintenance:

```bash
# Test notification system
python manage.py test_notifications --test-services
python manage.py test_notifications --create-test-order

# Check logs
tail -f /var/log/onerai/django.log

# Restart services
sudo systemctl restart onerai

# Check service status
sudo systemctl status onerai nginx
```
