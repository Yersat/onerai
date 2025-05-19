#!/usr/bin/env python
"""
Script to create superusers for onerai and partners_onerai projects.
"""
import os
import sys
import django
from pathlib import Path

# Define paths
BASE_DIR = Path(__file__).resolve().parent

def create_superuser(settings_module, username, email, password):
    """
    Create a superuser for a project.
    """
    print(f"\nCreating superuser for {settings_module}...")
    
    # Set the DJANGO_SETTINGS_MODULE environment variable
    os.environ["DJANGO_SETTINGS_MODULE"] = settings_module
    
    # Initialize Django
    django.setup()
    
    # Import the User model
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    # Check if the superuser already exists
    if User.objects.filter(username=username).exists():
        print(f"Superuser {username} already exists.")
        return True
    
    # Create the superuser
    try:
        User.objects.create_superuser(username=username, email=email, password=password)
        print(f"Superuser {username} created successfully!")
        return True
    except Exception as e:
        print(f"Error creating superuser: {e}")
        return False

def main():
    """
    Main function to create superusers for both projects.
    """
    print("Starting superuser creation...\n")
    
    # Create superuser for onerai project
    create_superuser(
        settings_module="onerai.settings",
        username="onerai_admin",
        email="admin@onerai.kz",
        password="onerai_admin_password"
    )
    
    # Create superuser for partners_onerai project
    create_superuser(
        settings_module="partners_onerai.settings",
        username="partners_admin",
        email="admin@partners.onerai.kz",
        password="partners_admin_password"
    )
    
    print("\nSuperuser creation completed!")

if __name__ == "__main__":
    main()
