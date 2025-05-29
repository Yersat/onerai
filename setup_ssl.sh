#!/bin/bash

# SSL Setup Script for OneRai
# This script sets up Let's Encrypt SSL certificates for both domains

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
DOMAIN="onerai.kz"
PARTNERS_DOMAIN="partners.onerai.kz"
EMAIL="admin@onerai.kz"  # Change this to your email

print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

echo -e "${BLUE}🔒 Setting up SSL certificates for OneRai${NC}"

# Install Certbot
print_status "Installing Certbot..."
sudo apt update
sudo apt install -y certbot python3-certbot-nginx

# Stop nginx temporarily
print_status "Stopping Nginx temporarily..."
sudo systemctl stop nginx

# Obtain SSL certificates
print_status "Obtaining SSL certificate for $DOMAIN..."
sudo certbot certonly --standalone -d $DOMAIN -d www.$DOMAIN --email $EMAIL --agree-tos --non-interactive

print_status "Obtaining SSL certificate for $PARTNERS_DOMAIN..."
sudo certbot certonly --standalone -d $PARTNERS_DOMAIN --email $EMAIL --agree-tos --non-interactive

# Create SSL-enabled Nginx configuration
print_status "Creating SSL-enabled Nginx configuration..."

cat > /tmp/nginx_onerai_ssl.conf << 'EOF'
# Nginx configuration for onerai.kz with SSL

# Rate limiting
limit_req_zone $binary_remote_addr zone=onerai_limit:10m rate=10r/s;

# Redirect HTTP to HTTPS for main domain
server {
    listen 80;
    server_name onerai.kz www.onerai.kz;
    return 301 https://$server_name$request_uri;
}

# Redirect HTTP to HTTPS for partners domain
server {
    listen 80;
    server_name partners.onerai.kz;
    return 301 https://$server_name$request_uri;
}

# Main HTTPS server block for onerai.kz
server {
    listen 443 ssl http2;
    server_name onerai.kz www.onerai.kz;
    
    # SSL configuration
    ssl_certificate /etc/letsencrypt/live/onerai.kz/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/onerai.kz/privkey.pem;
    ssl_session_timeout 1d;
    ssl_session_cache shared:MozTLS:10m;
    ssl_session_tickets off;
    
    # Modern SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    
    # HSTS
    add_header Strict-Transport-Security "max-age=63072000" always;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    
    # Rate limiting
    limit_req zone=onerai_limit burst=20 nodelay;
    
    # Client max body size for file uploads
    client_max_body_size 50M;
    
    # Static files
    location /static/ {
        alias /var/www/onerai/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
        access_log off;
    }
    
    # Media files
    location /media/ {
        alias /var/www/onerai/media/;
        expires 1y;
        add_header Cache-Control "public";
    }
    
    # Main application
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}

# Partners HTTPS server block
server {
    listen 443 ssl http2;
    server_name partners.onerai.kz;
    
    # SSL configuration
    ssl_certificate /etc/letsencrypt/live/partners.onerai.kz/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/partners.onerai.kz/privkey.pem;
    ssl_session_timeout 1d;
    ssl_session_cache shared:MozTLS:10m;
    ssl_session_tickets off;
    
    # Modern SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    
    # HSTS
    add_header Strict-Transport-Security "max-age=63072000" always;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    
    # Rate limiting
    limit_req zone=onerai_limit burst=20 nodelay;
    
    # Client max body size for file uploads
    client_max_body_size 50M;
    
    # Static files
    location /static/ {
        alias /var/www/partners_onerai/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
        access_log off;
    }
    
    # Media files
    location /media/ {
        alias /var/www/partners_onerai/media/;
        expires 1y;
        add_header Cache-Control "public";
    }
    
    # Main application
    location / {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
EOF

# Copy the SSL configuration
sudo cp /tmp/nginx_onerai_ssl.conf /etc/nginx/sites-available/onerai
sudo rm /tmp/nginx_onerai_ssl.conf

# Test Nginx configuration
print_status "Testing Nginx configuration..."
sudo nginx -t

# Start Nginx
print_status "Starting Nginx..."
sudo systemctl start nginx

# Set up automatic renewal
print_status "Setting up automatic SSL renewal..."
sudo crontab -l 2>/dev/null | { cat; echo "0 12 * * * /usr/bin/certbot renew --quiet"; } | sudo crontab -

print_status "🎉 SSL setup completed successfully!"
print_status "Your sites are now available at:"
print_status "  - https://$DOMAIN"
print_status "  - https://www.$DOMAIN"
print_status "  - https://$PARTNERS_DOMAIN"

print_warning "Don't forget to update your Django settings to enable SSL:"
print_warning "  - Set SECURE_SSL_REDIRECT = True"
print_warning "  - Set SESSION_COOKIE_SECURE = True"
print_warning "  - Set CSRF_COOKIE_SECURE = True"
