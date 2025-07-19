#!/bin/bash

# Railway Deployment Script for onerai Marketplace
# This script helps prepare and deploy both onerai and partners_onerai projects

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Railway Deployment Preparation for onerai Marketplace${NC}"

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

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if we're in the right directory
if [ ! -f "manage.py" ]; then
    print_error "Please run this script from the onerai project root directory"
    exit 1
fi

print_status "Checking project structure..."

# Check if all required files exist
required_files=(
    "manage.py"
    "requirements.txt"
    "Procfile"
    "railway.toml"
    "onerai/settings_production.py"
    "partners_onerai/manage.py"
    "partners_onerai/wsgi.py"
    "partners_onerai/requirements.txt"
    "partners_onerai/Procfile"
    "partners_onerai/railway.toml"
    "partners_onerai/settings_production.py"
)

missing_files=()
for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        missing_files+=("$file")
    fi
done

if [ ${#missing_files[@]} -ne 0 ]; then
    print_error "Missing required files:"
    for file in "${missing_files[@]}"; do
        echo "  - $file"
    done
    print_info "Please run the Railway preparation script first"
    exit 1
fi

print_status "All required files present"

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    print_warning "Railway CLI not found. Install it from: https://docs.railway.app/develop/cli"
    print_info "You can still deploy manually through the Railway dashboard"
else
    print_status "Railway CLI found"
fi

# Validate environment variables template
print_info "Creating environment variables template..."

cat > .env.railway.template << EOF
# onerai Service Environment Variables
SECRET_KEY=your-super-secret-key-here-min-50-chars
DJANGO_SETTINGS_MODULE=onerai.settings_production
FREEDOM_PAY_MERCHANT_ID=561533
FREEDOM_PAY_SECRET_KEY=AD0uCy2bDpPkTmZ9
FREEDOM_PAY_API_URL=https://api.freedompay.kz
FREEDOM_PAY_TESTING_MODE=0
TELEGRAM_BOT_TOKEN=7616528096:AAFEgelyZX5sPOz1hT5-xmL0sk0ssiL3SFY
TELEGRAM_CHAT_ID=344949399
API_KEY=onerai_partners_api_key_2024

# partners_onerai Service Environment Variables
PARTNERS_SECRET_KEY=different-super-secret-key-here-min-50-chars
ONERAI_API_URL=https://onerai.kz
EOF

print_status "Environment variables template created: .env.railway.template"

# Check Git status
if [ -d ".git" ]; then
    if [ -n "$(git status --porcelain)" ]; then
        print_warning "You have uncommitted changes. Consider committing them before deployment."
        git status --short
    else
        print_status "Git repository is clean"
    fi
else
    print_warning "Not a Git repository. Railway deployment requires Git."
fi

print_info "Deployment preparation complete!"
print_info ""
print_info "Next steps:"
print_info "1. Commit and push your changes to GitHub"
print_info "2. Follow the Railway Deployment Guide (RAILWAY_DEPLOYMENT_GUIDE.md)"
print_info "3. Create Railway project and services"
print_info "4. Configure environment variables using .env.railway.template"
print_info "5. Set up custom domains"
print_info ""
print_status "Ready for Railway deployment! 🚀"
