"""
Client module for interacting with the onerai service API.
"""
import os
import json
import requests
from django.conf import settings
from .shared_media import copy_file_to_shared_storage

# Configuration
ONERAI_API_URL = getattr(settings, 'ONERAI_API_URL', 'http://127.0.0.1:8000')
API_KEY = getattr(settings, 'API_KEY', 'your_secret_api_key')

def submit_design(design_data, image_path):
    """
    Submit a design to the onerai service.
    
    Args:
        design_data: Dictionary containing design information
        image_path: Path to the design image file
        
    Returns:
        Response from the onerai API
    """
    # Copy the image to shared storage
    shared_image_path = copy_file_to_shared_storage(image_path)
    
    # Add the image path to the design data
    design_data['design_image_path'] = shared_image_path
    
    # Submit the design to the onerai API
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f"ApiKey {API_KEY}"
    }
    
    try:
        response = requests.post(
            f"{ONERAI_API_URL}/api/designs/submit/",
            data=json.dumps(design_data),
            headers=headers
        )
        response.raise_for_status()  # Raise exception for HTTP errors
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error submitting design to onerai: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response content: {e.response.content}")
        raise

def get_design_status(product_id):
    """
    Get the status of a design from the onerai service.
    
    Args:
        product_id: ID of the product to check
        
    Returns:
        Status information from the onerai API
    """
    headers = {
        'Authorization': f"ApiKey {API_KEY}"
    }
    
    try:
        response = requests.get(
            f"{ONERAI_API_URL}/api/designs/status/{product_id}/",
            headers=headers
        )
        response.raise_for_status()  # Raise exception for HTTP errors
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error getting design status from onerai: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response content: {e.response.content}")
        raise
