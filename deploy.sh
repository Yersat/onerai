#!/bin/bash

# OneRai Deployment Script
# This script deploys both onerai and partners_onerai projects to production

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SERVER_IP="195.49.212.182"
DOMAIN="onerai.kz"
PARTNERS_DOMAIN="partners.onerai.kz"
PROJECT_DIR="/var/www"
ONERAI_DIR="$PROJECT_DIR/onerai"
PARTNERS_DIR="$PROJECT_DIR/partners_onerai"

echo -e "${BLUE}🚀 Starting OneRai Deployment${NC}"

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root for security reasons"
   exit 1
fi

# Update system packages
print_status "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install required packages
print_status "Installing required packages..."
sudo apt install -y python3 python3-pip python3-venv postgresql postgresql-contrib nginx redis-server git curl

# Install Node.js for Tailwind CSS
print_status "Installing Node.js..."
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Create project directories
print_status "Creating project directories..."
sudo mkdir -p $ONERAI_DIR $PARTNERS_DIR
sudo mkdir -p /var/log/onerai /var/log/partners_onerai
sudo mkdir -p /var/run/onerai /var/run/partners_onerai

# Set ownership
sudo chown -R $USER:www-data $PROJECT_DIR
sudo chown -R $USER:www-data /var/log/onerai /var/log/partners_onerai
sudo chown -R $USER:www-data /var/run/onerai /var/run/partners_onerai

# Clone or update repositories
if [ -d "$ONERAI_DIR/.git" ]; then
    print_status "Updating onerai repository..."
    cd $ONERAI_DIR
    git pull origin main
else
    print_status "Cloning onerai repository..."
    git clone https://github.com/yourusername/onerai.git $ONERAI_DIR
    cd $ONERAI_DIR
fi

# Create virtual environment for onerai
print_status "Setting up Python virtual environment for onerai..."
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn redis

# Install additional production packages
pip install psycopg2-binary

# Copy partners_onerai if it's in the same repo
if [ -d "partners_onerai" ]; then
    print_status "Copying partners_onerai..."
    cp -r partners_onerai/* $PARTNERS_DIR/
fi

# Setup partners_onerai virtual environment
print_status "Setting up Python virtual environment for partners_onerai..."
cd $PARTNERS_DIR
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r $ONERAI_DIR/requirements.txt
pip install gunicorn

# Install Tailwind CSS dependencies
print_status "Installing Tailwind CSS dependencies..."
cd $ONERAI_DIR
npm install

cd $PARTNERS_DIR
npm install

# Setup PostgreSQL databases
print_status "Setting up PostgreSQL databases..."
sudo -u postgres psql -c "CREATE DATABASE onerai_prod;" || true
sudo -u postgres psql -c "CREATE DATABASE partners_onerai_prod;" || true
sudo -u postgres psql -c "CREATE USER onerai_user WITH PASSWORD 'onerai_password';" || true
sudo -u postgres psql -c "CREATE USER partners_onerai_user WITH PASSWORD 'partners_onerai_password';" || true
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE onerai_prod TO onerai_user;" || true
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE partners_onerai_prod TO partners_onerai_user;" || true

# Copy configuration files
print_status "Copying configuration files..."
cd $ONERAI_DIR

# Copy Gunicorn configs
cp gunicorn_onerai.conf.py $ONERAI_DIR/
cp gunicorn_partners.conf.py $PARTNERS_DIR/

# Copy systemd service files
sudo cp deployment/onerai.service /etc/systemd/system/
sudo cp deployment/partners-onerai.service /etc/systemd/system/

# Copy Nginx configuration
sudo cp deployment/nginx_onerai.conf /etc/nginx/sites-available/onerai
sudo ln -sf /etc/nginx/sites-available/onerai /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Create .env file if it doesn't exist
if [ ! -f "$ONERAI_DIR/.env" ]; then
    print_warning "Creating .env file from template..."
    cp .env.example .env
    print_warning "Please edit .env file with your production settings!"
fi

# Run migrations
print_status "Running database migrations..."
cd $ONERAI_DIR
source venv/bin/activate
export DJANGO_SETTINGS_MODULE=onerai.settings_production
python manage.py migrate

cd $PARTNERS_DIR
source venv/bin/activate
export DJANGO_SETTINGS_MODULE=partners_onerai.settings_production
python manage.py migrate

# Collect static files
print_status "Collecting static files..."
cd $ONERAI_DIR
source venv/bin/activate
python manage.py collectstatic --noinput

cd $PARTNERS_DIR
source venv/bin/activate
python manage.py collectstatic --noinput

# Set proper permissions
print_status "Setting file permissions..."
sudo chown -R www-data:www-data $ONERAI_DIR/media $PARTNERS_DIR/media
sudo chown -R www-data:www-data $ONERAI_DIR/static $PARTNERS_DIR/static
sudo chmod -R 755 $ONERAI_DIR $PARTNERS_DIR

# Enable and start services
print_status "Enabling and starting services..."
sudo systemctl daemon-reload
sudo systemctl enable onerai partners-onerai nginx postgresql redis-server
sudo systemctl restart postgresql redis-server
sudo systemctl restart onerai partners-onerai
sudo systemctl restart nginx

# Test Nginx configuration
print_status "Testing Nginx configuration..."
sudo nginx -t

print_status "🎉 Deployment completed successfully!"
print_warning "Don't forget to:"
print_warning "1. Configure your domain DNS to point to $SERVER_IP"
print_warning "2. Set up SSL certificates with Let's Encrypt"
print_warning "3. Update .env file with production settings"
print_warning "4. Create superuser accounts"

echo -e "${BLUE}📋 Service Status:${NC}"
sudo systemctl status onerai --no-pager -l
sudo systemctl status partners-onerai --no-pager -l
sudo systemctl status nginx --no-pager -l
