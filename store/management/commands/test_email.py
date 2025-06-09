"""
Django management command to test email configuration.
"""

from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib.auth import get_user_model
from store.models import Order, ShippingAddress, Product, OrderItem

User = get_user_model()


class Command(BaseCommand):
    help = 'Test email configuration and delivery'

    def add_arguments(self, parser):
        parser.add_argument(
            '--simple',
            action='store_true',
            help='Send a simple test email',
        )
        parser.add_argument(
            '--order-template',
            action='store_true',
            help='Test with order notification template',
        )
        parser.add_argument(
            '--check-config',
            action='store_true',
            help='Check email configuration',
        )

    def handle(self, *args, **options):
        if options['check_config']:
            self.check_email_config()
        elif options['simple']:
            self.send_simple_test_email()
        elif options['order_template']:
            self.send_order_template_test()
        else:
            self.stdout.write(
                self.style.ERROR(
                    'Please specify --simple, --order-template, or --check-config'
                )
            )

    def check_email_config(self):
        """Check email configuration settings."""
        self.stdout.write("📧 Email Configuration Check")
        self.stdout.write("=" * 50)
        
        # Check settings
        email_backend = getattr(settings, 'EMAIL_BACKEND', 'Not set')
        email_host = getattr(settings, 'EMAIL_HOST', 'Not set')
        email_port = getattr(settings, 'EMAIL_PORT', 'Not set')
        email_use_tls = getattr(settings, 'EMAIL_USE_TLS', 'Not set')
        email_host_user = getattr(settings, 'EMAIL_HOST_USER', 'Not set')
        email_host_password = getattr(settings, 'EMAIL_HOST_PASSWORD', 'Not set')
        default_from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'Not set')
        admin_email = getattr(settings, 'ADMIN_EMAIL', 'Not set')
        
        self.stdout.write(f"EMAIL_BACKEND: {email_backend}")
        self.stdout.write(f"EMAIL_HOST: {email_host}")
        self.stdout.write(f"EMAIL_PORT: {email_port}")
        self.stdout.write(f"EMAIL_USE_TLS: {email_use_tls}")
        self.stdout.write(f"EMAIL_HOST_USER: {email_host_user}")
        self.stdout.write(f"EMAIL_HOST_PASSWORD: {'***' if email_host_password else 'Not set'}")
        self.stdout.write(f"DEFAULT_FROM_EMAIL: {default_from_email}")
        self.stdout.write(f"ADMIN_EMAIL: {admin_email}")
        
        # Check if configuration is complete
        if email_backend == 'django.core.mail.backends.console.EmailBackend':
            self.stdout.write(self.style.WARNING("⚠️  Using console backend - emails will only print to console"))
        elif email_backend == 'django.core.mail.backends.smtp.EmailBackend':
            if not email_host_user or not email_host_password:
                self.stdout.write(self.style.ERROR("❌ SMTP backend requires EMAIL_HOST_USER and EMAIL_HOST_PASSWORD"))
            else:
                self.stdout.write(self.style.SUCCESS("✅ SMTP backend configured"))
        
        if not admin_email or admin_email == 'Not set':
            self.stdout.write(self.style.ERROR("❌ ADMIN_EMAIL not configured"))
        else:
            self.stdout.write(self.style.SUCCESS(f"✅ Admin email set to: {admin_email}"))

    def send_simple_test_email(self):
        """Send a simple test email."""
        self.stdout.write("📧 Sending simple test email...")
        
        admin_email = getattr(settings, 'ADMIN_EMAIL', '')
        if not admin_email:
            self.stdout.write(self.style.ERROR("❌ ADMIN_EMAIL not configured"))
            return
        
        try:
            send_mail(
                subject='Test Email from onerai.kz',
                message='This is a test email to verify email configuration is working.',
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@onerai.kz'),
                recipient_list=[admin_email],
                fail_silently=False,
            )
            self.stdout.write(self.style.SUCCESS(f"✅ Test email sent to {admin_email}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Failed to send email: {str(e)}"))

    def send_order_template_test(self):
        """Send test email using order notification template."""
        self.stdout.write("📧 Sending order template test email...")
        
        admin_email = getattr(settings, 'ADMIN_EMAIL', '')
        if not admin_email:
            self.stdout.write(self.style.ERROR("❌ ADMIN_EMAIL not configured"))
            return
        
        try:
            # Create mock data for template
            mock_order = type('MockOrder', (), {
                'id': 999,
                'created_at': '2025-06-09 13:00:00',
                'total_price': 2500.00,
                'get_status_display': lambda: 'Ожидает подтверждения',
                'get_payment_status_display': lambda: 'Ожидает оплаты',
                'payment_status': 'pending'
            })()
            
            mock_user = type('MockUser', (), {
                'get_full_name': lambda: 'Test User',
                'username': 'testuser',
                'email': 'test@onerai.kz'
            })()
            
            mock_address = type('MockAddress', (), {
                'phone': '+77777777777',
                'get_full_address': lambda: 'Test Address 123, Almaty, 050000'
            })()
            
            mock_item = type('MockItem', (), {
                'product': type('MockProduct', (), {'name': 'Test T-Shirt'})(),
                'size': 'M',
                'color': 'Белый',
                'quantity': 1,
                'price': 2500.00,
                'get_total_price': lambda: 2500.00
            })()
            
            context = {
                'order': mock_order,
                'order_items': [mock_item],
                'customer': mock_user,
                'shipping_address': mock_address,
                'total_items': 1,
            }
            
            # Render email template
            html_message = render_to_string('emails/new_order_notification.html', context)
            plain_message = strip_tags(html_message)
            
            send_mail(
                subject='Test Order Notification - onerai.kz',
                message=plain_message,
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@onerai.kz'),
                recipient_list=[admin_email],
                html_message=html_message,
                fail_silently=False,
            )
            self.stdout.write(self.style.SUCCESS(f"✅ Order template test email sent to {admin_email}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Failed to send template email: {str(e)}"))
            import traceback
            self.stdout.write(self.style.ERROR(traceback.format_exc()))
