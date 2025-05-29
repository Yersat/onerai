# Freedom Pay Integration Guide

## Overview

This document describes the Freedom Pay payment gateway integration for the onerai.kz marketplace. The integration uses Freedom Pay's Merchant API with the Payment Page method for secure payment processing.

## Features

- **Secure Payment Processing**: Uses Freedom Pay's hosted payment pages
- **Multiple Payment Methods**: Supports bank cards, mobile commerce, and e-wallets
- **Real-time Payment Status**: Automatic order status updates via callbacks
- **Test Mode Support**: Full testing capabilities with test cards
- **Signature Verification**: All requests and responses are cryptographically signed

## Architecture

### Components

1. **FreedomPayService** (`store/freedompay_service.py`): Core service class handling API communication
2. **Payment Views** (`store/views.py`): Django views for handling payment callbacks and redirects
3. **Order Model Updates**: Enhanced with payment status tracking
4. **URL Configuration**: Payment-specific routes for callbacks

### Payment Flow

1. **Checkout Initiation**: User completes checkout form
2. **Payment Initialization**: System calls Freedom Pay API to create payment
3. **User Redirect**: User is redirected to Freedom Pay payment page
4. **Payment Processing**: User completes payment on Freedom Pay
5. **Callback Processing**: Freedom Pay sends result to our callback URL
6. **Order Update**: System updates order status based on payment result
7. **User Redirect**: User is redirected back to confirmation page

## Configuration

### Environment Variables

Create a `.env` file with the following variables:

```bash
# Freedom Pay settings
FREEDOM_PAY_MERCHANT_ID=your_merchant_id_here
FREEDOM_PAY_SECRET_KEY=your_secret_key_here
FREEDOM_PAY_API_URL=https://test-api.freedompay.kz  # Use https://api.freedompay.kz for production
FREEDOM_PAY_TESTING_MODE=1  # 1 for test, 0 for production
```

### Django Settings

The following settings are automatically configured in `onerai/settings.py`:

- `FREEDOM_PAY_MERCHANT_ID`: Your merchant ID from Freedom Pay
- `FREEDOM_PAY_SECRET_KEY`: Your secret key for signature generation
- `FREEDOM_PAY_API_URL`: API endpoint (test or production)
- `FREEDOM_PAY_TESTING_MODE`: Test mode flag

## API Endpoints

### Callback URLs

- **Result URL**: `/payment/freedompay/result/` - Receives payment status from Freedom Pay
- **Success URL**: `/payment/freedompay/success/` - User redirect after successful payment
- **Failure URL**: `/payment/freedompay/failure/` - User redirect after failed payment

### Security

All API communications use MD5 signature verification:

1. Parameters are sorted alphabetically
2. Script name and secret key are added
3. MD5 hash is calculated and included as `pg_sig`

## Testing

### Test Cards

Use these test cards in test mode:

**Successful Payments:**
- VISA: 4400444400004440, CVV: 123, Expiry: 12/2030
- MasterCard: 5555555555555599, CVV: 123, Expiry: 12/2030

**Failed Payments:**
- VISA: 4400444400004441, CVV: 123, Expiry: 12/2030 (Unknown error)
- VISA: 4400444400004443, CVV: 123, Expiry: 12/2030 (Insufficient funds)

### Test Mobile Numbers

For mobile commerce testing:
- Kcell: +77017777777, OTP: 111111
- Activ: +77027777777, OTP: 111111

## Order Status Management

### Payment Status Values

- `pending`: Awaiting payment
- `paid`: Payment successful
- `failed`: Payment failed
- `refunded`: Payment refunded

### Order Status Values

- `pending`: Awaiting confirmation
- `processing`: Payment received, order in processing
- `shipped`: Order shipped
- `delivered`: Order delivered
- `cancelled`: Order cancelled

## Error Handling

The integration includes comprehensive error handling:

1. **API Errors**: Network issues, invalid responses
2. **Signature Errors**: Invalid or missing signatures
3. **Order Errors**: Missing or invalid orders
4. **Payment Errors**: Failed payments, timeouts

## Deployment Considerations

### Production Setup

1. **Update API URL**: Change to `https://api.freedompay.kz`
2. **Set Testing Mode**: Set `FREEDOM_PAY_TESTING_MODE=0`
3. **SSL Certificate**: Ensure HTTPS is enabled for callbacks
4. **Firewall**: Allow Freedom Pay IP addresses for callbacks

### Monitoring

Monitor the following:

- Payment success/failure rates
- Callback response times
- Order status consistency
- Error logs for payment issues

## Support

For technical issues:
- Check Django logs for error details
- Verify signature generation
- Test with Freedom Pay test environment
- Contact Freedom Pay support for API issues

For Freedom Pay documentation: https://freedompay.kz/docs
