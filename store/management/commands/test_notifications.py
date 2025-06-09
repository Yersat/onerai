"""
Django management command to test the notification system.
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from store.models import Order, ShippingAddress, Product, OrderItem
from store.services.notification_service import NotificationService

User = get_user_model()


class Command(BaseCommand):
    help = 'Test the notification system with a sample order'

    def add_arguments(self, parser):
        parser.add_argument(
            '--order-id',
            type=int,
            help='Test notifications for an existing order ID',
        )
        parser.add_argument(
            '--create-test-order',
            action='store_true',
            help='Create a test order and send notifications',
        )
        parser.add_argument(
            '--test-services',
            action='store_true',
            help='Test notification services configuration',
        )

    def handle(self, *args, **options):
        notification_service = NotificationService()
        
        if options['test_services']:
            self.test_services(notification_service)
            return
        
        if options['order_id']:
            self.test_existing_order(options['order_id'], notification_service)
        elif options['create_test_order']:
            self.create_and_test_order(notification_service)
        else:
            self.stdout.write(
                self.style.ERROR(
                    'Please specify either --order-id <id>, --create-test-order, or --test-services'
                )
            )

    def test_services(self, notification_service):
        """Test notification services configuration."""
        self.stdout.write("Testing notification services configuration...")
        
        results = notification_service.test_all_services()
        
        self.stdout.write(f"Email service: {'✓ Configured' if results['email'] else '✗ Not configured'}")
        
        if results['telegram'] is None:
            self.stdout.write("Telegram service: ⚠ Not configured")
        elif results['telegram']:
            self.stdout.write("Telegram service: ✓ Connected")
        else:
            self.stdout.write("Telegram service: ✗ Connection failed")

    def test_existing_order(self, order_id, notification_service):
        """Test notifications for an existing order."""
        try:
            order = Order.objects.get(id=order_id)
            self.stdout.write(f"Testing notifications for order #{order.id}...")
            
            results = notification_service.send_order_notifications(order)
            
            self.stdout.write(f"Email notification: {'✓ Sent' if results['email'] else '✗ Failed'}")
            self.stdout.write(f"Telegram notification: {'✓ Sent' if results['telegram'] else '✗ Failed'}")
            
            if results['errors']:
                self.stdout.write(self.style.ERROR("Errors:"))
                for error in results['errors']:
                    self.stdout.write(self.style.ERROR(f"  - {error}"))
            
        except Order.DoesNotExist:
            self.stdout.write(self.style.ERROR(f"Order #{order_id} not found"))

    def create_and_test_order(self, notification_service):
        """Create a test order and test notifications."""
        self.stdout.write("Creating test order...")
        
        # Get or create test user
        user, created = User.objects.get_or_create(
            username='test_notification_user',
            defaults={
                'email': 'test@onerai.kz',
                'first_name': 'Test',
                'last_name': 'User'
            }
        )
        
        if created:
            self.stdout.write("Created test user")
        
        # Get or create shipping address
        shipping_address, created = ShippingAddress.objects.get_or_create(
            user=user,
            defaults={
                'full_name': 'Test User',
                'phone': '+77777777777',
                'address': 'Test Address 123',
                'city': 'Almaty',
                'postal_code': '050000'
            }
        )
        
        if created:
            self.stdout.write("Created test shipping address")
        
        # Get a product for the order (or create a dummy one)
        product = Product.objects.filter(approval_status='approved').first()
        if not product:
            self.stdout.write(self.style.WARNING("No approved products found. Creating dummy product..."))
            product = Product.objects.create(
                name='Test T-Shirt',
                description='Test product for notification testing',
                price=2500.00,
                approval_status='approved'
            )
        
        # Create test order
        order = Order.objects.create(
            user=user,
            shipping_address=shipping_address,
            total_price=2500.00,
            status=Order.STATUS_PENDING,
            payment_status=Order.PAYMENT_STATUS_PENDING
        )
        
        # Create order item
        OrderItem.objects.create(
            order=order,
            product=product,
            size='M',
            color='Белый',
            quantity=1,
            price=product.price
        )
        
        self.stdout.write(f"Created test order #{order.id}")

        # Note: Notifications are automatically sent via Django signal when order is created
        # No need to manually trigger them again to avoid duplicates
        self.stdout.write("✅ Notifications automatically sent via Django signal")
        self.stdout.write("📧 Check your email and Telegram for notifications")

        self.stdout.write(f"Test order created with ID: {order.id}")
        self.stdout.write("You can delete this test order from the Django admin if needed.")
