"""
Utility module for handling shared media files between partners_onerai and onerai services.
"""
import os
import uuid
import shutil
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import requests
from urllib.parse import urlparse

# Configuration
ONERAI_API_URL = getattr(settings, 'ONERAI_API_URL', 'http://127.0.0.1:8000')
ONERAI_MEDIA_ROOT = getattr(settings, 'ONERAI_MEDIA_ROOT', None)  # Path to onerai media directory for direct file system access
USE_DIRECT_COPY = getattr(settings, 'USE_DIRECT_COPY', True)  # Use direct file system copy if possible
USE_API_TRANSFER = getattr(settings, 'USE_API_TRANSFER', False)  # Use API to transfer files if direct copy not possible

def copy_file_to_shared_storage(source_file_path, destination_path=None):
    """
    Copy a file to the shared storage location.
    
    Args:
        source_file_path: Path to the source file
        destination_path: Optional destination path (if None, will generate one)
        
    Returns:
        The path to the file in shared storage
    """
    if not os.path.exists(source_file_path):
        raise FileNotFoundError(f"Source file not found: {source_file_path}")
    
    # Generate destination path if not provided
    if destination_path is None:
        file_ext = os.path.splitext(source_file_path)[1]
        filename = f"design_{uuid.uuid4().hex}{file_ext}"
        destination_path = os.path.join('products', filename)
    
    # If using direct file system access
    if USE_DIRECT_COPY and ONERAI_MEDIA_ROOT:
        full_dest_path = os.path.join(ONERAI_MEDIA_ROOT, destination_path)
        os.makedirs(os.path.dirname(full_dest_path), exist_ok=True)
        shutil.copy2(source_file_path, full_dest_path)
        return destination_path
    
    # If using cloud storage (S3, etc.)
    with open(source_file_path, 'rb') as f:
        file_content = f.read()
        default_storage.save(destination_path, ContentFile(file_content))
    
    return destination_path

def submit_design_to_onerai(design_data, image_path):
    """
    Submit a design to the onerai service.
    
    Args:
        design_data: Dictionary containing design information
        image_path: Path to the design image file
        
    Returns:
        Response from the onerai API
    """
    import json
    import requests
    
    # Copy the image to shared storage
    shared_image_path = copy_file_to_shared_storage(image_path)
    
    # Add the image path to the design data
    design_data['design_image_path'] = shared_image_path
    
    # Submit the design to the onerai API
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f"ApiKey {settings.API_KEY}"
    }
    
    response = requests.post(
        f"{ONERAI_API_URL}/api/designs/submit/",
        data=json.dumps(design_data),
        headers=headers
    )
    
    return response.json()

def get_design_status(product_id):
    """
    Get the status of a design from the onerai service.
    
    Args:
        product_id: ID of the product to check
        
    Returns:
        Status information from the onerai API
    """
    import requests
    
    headers = {
        'Authorization': f"ApiKey {settings.API_KEY}"
    }
    
    response = requests.get(
        f"{ONERAI_API_URL}/api/designs/status/{product_id}/",
        headers=headers
    )
    
    return response.json()
