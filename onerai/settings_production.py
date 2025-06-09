"""
Production settings for onerai project.
"""

from .settings import *
import os

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# Production secret key - should be set via environment variable
SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable must be set in production")

# Production allowed hosts
ALLOWED_HOSTS = [
    'onerai.kz',
    'www.onerai.kz',
    '195.49.212.182',  # Your server IP
    'localhost',  # For local testing
]

# Security settings for production
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# SSL settings (enable when you have SSL certificate)
# SECURE_SSL_REDIRECT = True
# SESSION_COOKIE_SECURE = True
# CSRF_COOKIE_SECURE = True

# Database for production
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('ONERAI_DB_NAME', 'onerai_prod'),
        'USER': os.environ.get('ONERAI_DB_USER', 'onerai_user'),
        'PASSWORD': os.environ.get('ONERAI_DB_PASSWORD'),
        'HOST': os.environ.get('ONERAI_DB_HOST', 'localhost'),
        'PORT': os.environ.get('ONERAI_DB_PORT', '5432'),
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

# Static files for production
STATIC_ROOT = '/var/www/onerai/static/'
MEDIA_ROOT = '/var/www/onerai/media/'

# Freedom Pay production settings
FREEDOM_PAY_API_URL = os.environ.get('FREEDOM_PAY_API_URL', 'https://api.freedompay.kz')
FREEDOM_PAY_TESTING_MODE = os.environ.get('FREEDOM_PAY_TESTING_MODE', '0')  # Production mode

# Logging for production
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/onerai/django.log',
            'maxBytes': 1024*1024*10,  # 10MB
            'backupCount': 5,
            'formatter': 'verbose',
        },
        'error_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/onerai/django_error.log',
            'maxBytes': 1024*1024*10,  # 10MB
            'backupCount': 5,
            'formatter': 'verbose',
            'level': 'ERROR',
        },
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'root': {
        'handlers': ['file', 'console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'error_file'],
            'level': 'INFO',
            'propagate': False,
        },
        'store.freedompay_service': {
            'handlers': ['file', 'error_file'],
            'level': 'WARNING',  # Reduce noise in production
            'propagate': False,
        },
    },
}

# Email settings for production - Currently using dummy backend (Telegram-only notifications)
# To enable email notifications, change EMAIL_BACKEND to 'django.core.mail.backends.smtp.EmailBackend'
# and configure EMAIL_HOST_USER and EMAIL_HOST_PASSWORD environment variables
EMAIL_BACKEND = os.environ.get('EMAIL_BACKEND', 'django.core.mail.backends.dummy.EmailBackend')
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', '587'))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@onerai.kz')
ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL', 'info@fastdev.org')

# Telegram notification settings
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '7616528096:AAFEgelyZX5sPOz1hT5-xmL0sk0ssiL3SFY')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID', '344949399')

# Cache settings for production
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}

# Session settings
SESSION_COOKIE_AGE = 86400  # 24 hours
SESSION_SAVE_EVERY_REQUEST = True
SESSION_EXPIRE_AT_BROWSER_CLOSE = False
