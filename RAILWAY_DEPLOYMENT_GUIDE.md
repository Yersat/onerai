# 🚀 Railway Deployment Guide for onerai Marketplace

This guide provides step-by-step instructions for deploying both onerai (main store) and partners_onerai (creator platform) projects on Railway.

## 📋 Prerequisites

1. **Railway Account**: Sign up at [railway.app](https://railway.app)
2. **GitHub Repository**: Both projects should be in your GitHub repository
3. **Domain Names**: onerai.kz and partners.onerai.kz configured

## 🗄️ Required Environment Variables

### **Shared Database Variables (PostgreSQL)**
Both services will use the same PostgreSQL database with these Railway-provided variables:
```
PGDATABASE=railway
PGHOST=containers-us-west-xxx.railway.app
PGPASSWORD=xxx
PGPORT=5432
PGUSER=postgres
```

### **onerai Service Environment Variables**
```bash
# Django Configuration
SECRET_KEY=your-super-secret-key-here-min-50-chars
DJANGO_SETTINGS_MODULE=onerai.settings_production

# Freedom Pay Integration
FREEDOM_PAY_MERCHANT_ID=561533
FREEDOM_PAY_SECRET_KEY=AD0uCy2bDpPkTmZ9
FREEDOM_PAY_API_URL=https://api.freedompay.kz
FREEDOM_PAY_TESTING_MODE=0

# Telegram Notifications
TELEGRAM_BOT_TOKEN=7616528096:AAFEgelyZX5sPOz1hT5-xmL0sk0ssiL3SFY
TELEGRAM_CHAT_ID=344949399

# API Communication
API_KEY=onerai_partners_api_key_2024

# Email Settings (Optional - currently using Telegram only)
EMAIL_BACKEND=django.core.mail.backends.dummy.EmailBackend
DEFAULT_FROM_EMAIL=noreply@onerai.kz
ADMIN_EMAIL=info@fastdev.org
```

### **partners_onerai Service Environment Variables**
```bash
# Django Configuration
PARTNERS_SECRET_KEY=different-super-secret-key-here-min-50-chars
DJANGO_SETTINGS_MODULE=partners_onerai.settings_production

# API Communication with onerai
API_KEY=onerai_partners_api_key_2024
ONERAI_API_URL=https://onerai.kz

# Email Settings (Optional)
EMAIL_BACKEND=django.core.mail.backends.dummy.EmailBackend
DEFAULT_FROM_EMAIL=noreply@partners.onerai.kz
```

## 🔧 Step-by-Step Deployment

### **Step 1: Create Railway Project**
1. Go to [railway.app](https://railway.app) and sign in
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your onerai repository

### **Step 2: Set Up PostgreSQL Database**
1. In your Railway project, click "New Service"
2. Select "Database" → "PostgreSQL"
3. Railway will automatically create the database and provide connection variables

### **Step 3: Deploy onerai Service**
1. Click "New Service" → "GitHub Repo"
2. Select your repository
3. Railway will detect it's a Python project
4. Set the **Root Directory** to `/` (main project)
5. Add all onerai environment variables listed above
6. Deploy will start automatically

### **Step 4: Deploy partners_onerai Service**
1. Click "New Service" → "GitHub Repo"
2. Select the same repository
3. Set the **Root Directory** to `/partners_onerai`
4. Add all partners_onerai environment variables listed above
5. Deploy will start automatically

### **Step 5: Configure Custom Domains**
1. In onerai service settings:
   - Go to "Settings" → "Domains"
   - Add custom domain: `onerai.kz`
   - Configure DNS: Add CNAME record pointing to Railway URL

2. In partners_onerai service settings:
   - Go to "Settings" → "Domains"
   - Add custom domain: `partners.onerai.kz`
   - Configure DNS: Add CNAME record pointing to Railway URL

### **Step 6: Run Database Migrations**
1. In onerai service, go to "Deployments"
2. Click on latest deployment → "View Logs"
3. Migrations should run automatically via Procfile
4. If needed, manually run: `python manage.py migrate`

## 🔍 Verification Steps

### **Test onerai Service**
1. Visit `https://onerai.kz`
2. Check homepage loads correctly
3. Test product browsing
4. Test user registration/login
5. Test Freedom Pay integration

### **Test partners_onerai Service**
1. Visit `https://partners.onerai.kz`
2. Test creator registration
3. Test design upload functionality
4. Verify API communication with onerai

### **Test Inter-Service Communication**
1. Submit a design from partners_onerai
2. Check if it appears in onerai admin
3. Verify file transfers work correctly

## 🚨 Troubleshooting

### **Common Issues**

**Build Failures:**
- Check Python version compatibility
- Verify all dependencies in requirements.txt
- Check Railway build logs

**Database Connection Issues:**
- Verify PostgreSQL service is running
- Check environment variables are set correctly
- Ensure both services use same database

**Static Files Not Loading:**
- Verify `python manage.py collectstatic` runs in Procfile
- Check whitenoise is installed and configured

**API Communication Fails:**
- Verify API_KEY matches in both services
- Check ONERAI_API_URL points to correct domain
- Test internal Railway networking

## 📊 Expected Costs

**Railway Pricing (Estimated Monthly):**
- PostgreSQL Database: ~$5-15
- onerai Service: ~$5-20
- partners_onerai Service: ~$5-15
- **Total: ~$15-50/month**

*Costs depend on usage, storage, and bandwidth*

## 🔄 Deployment Updates

**To update your applications:**
1. Push changes to GitHub
2. Railway automatically redeploys
3. Monitor deployment logs
4. Test functionality after deployment

## 📞 Support

If you encounter issues:
1. Check Railway deployment logs
2. Verify environment variables
3. Test database connectivity
4. Check domain DNS configuration

**Your onerai marketplace is now ready for production on Railway!** 🎉

## 📝 Pre-Deployment Checklist

### **Code Preparation**
- [ ] All missing files created (partners_onerai/manage.py, wsgi.py, etc.)
- [ ] Production settings updated for Railway
- [ ] Requirements.txt includes Railway dependencies
- [ ] Procfile and railway.toml files created
- [ ] Environment variables documented
- [ ] Static files configuration updated

### **Railway Account Setup**
- [ ] Railway account created at railway.app
- [ ] GitHub repository connected
- [ ] Payment method added (if needed)

### **Domain Configuration**
- [ ] onerai.kz DNS configured
- [ ] partners.onerai.kz DNS configured
- [ ] SSL certificates ready

## 🚀 Deployment Execution Checklist

### **Phase 1: Database Setup**
- [ ] PostgreSQL service created in Railway
- [ ] Database connection variables noted
- [ ] Database accessible from Railway dashboard

### **Phase 2: onerai Service Deployment**
- [ ] onerai service created from GitHub repo
- [ ] Root directory set to `/`
- [ ] All environment variables added
- [ ] First deployment successful
- [ ] Migrations completed automatically
- [ ] Static files collected

### **Phase 3: partners_onerai Service Deployment**
- [ ] partners_onerai service created from same repo
- [ ] Root directory set to `/partners_onerai`
- [ ] All environment variables added
- [ ] First deployment successful
- [ ] Migrations completed automatically
- [ ] Static files collected

### **Phase 4: Domain Configuration**
- [ ] onerai.kz domain added to onerai service
- [ ] partners.onerai.kz domain added to partners_onerai service
- [ ] DNS CNAME records configured
- [ ] SSL certificates active
- [ ] Domains accessible via HTTPS

### **Phase 5: Testing & Verification**
- [ ] onerai.kz homepage loads
- [ ] Product browsing works
- [ ] User registration/login functional
- [ ] partners.onerai.kz loads
- [ ] Creator registration works
- [ ] Design upload functional
- [ ] API communication between services works
- [ ] Freedom Pay integration tested
- [ ] Telegram notifications working

## 🔧 Post-Deployment Tasks

### **Monitoring Setup**
- [ ] Railway deployment logs monitored
- [ ] Error tracking configured
- [ ] Performance monitoring active

### **Security Verification**
- [ ] HTTPS enforced on both domains
- [ ] Environment variables secured
- [ ] Database access restricted
- [ ] API keys rotated if needed

### **Backup Strategy**
- [ ] Database backup schedule confirmed
- [ ] Media files backup plan
- [ ] Code repository backup verified

## 📊 Success Metrics

### **Technical Metrics**
- [ ] Both services deploy successfully
- [ ] Response times < 2 seconds
- [ ] Zero deployment errors
- [ ] Database connections stable

### **Functional Metrics**
- [ ] User registration works
- [ ] Product browsing functional
- [ ] Design uploads successful
- [ ] Payment processing active
- [ ] Notifications delivered

### **Business Metrics**
- [ ] onerai.kz accessible to customers
- [ ] partners.onerai.kz accessible to creators
- [ ] API communication seamless
- [ ] All integrations functional
