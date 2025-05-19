"""
Views for the partners_onerai project.
"""
import os
from django.shortcuts import render
from django.http import Http404
from django.conf import settings

def legal_document(request, document_name):
    """View for displaying legal documents"""
    # Map URL slugs to actual filenames
    document_map = {
        'terms-of-service': 'terms_of_service.html',
        'privacy-policy': 'privacy_policy.html',
        'cookie-policy': 'cookie_policy.html',
        'return-policy': 'return_policy.html',
        'shipping-policy': 'shipping_policy.html',
        'payment-terms': 'payment_terms.html',
        'content-guidelines': 'content_guidelines.html',
        'creator-agreement': 'creator_agreement.html',
        'intellectual-property-policy': 'intellectual_property_policy.html',
        'dispute-resolution-policy': 'dispute_resolution_policy.html',
        'age-restrictions-policy': 'age_restrictions_policy.html',
    }
    
    # Check if the requested document exists in our map
    if document_name not in document_map:
        raise Http404("Запрашиваемый документ не найден")
    
    # Get the actual filename
    filename = document_map[document_name]
    file_path = os.path.join(settings.BASE_DIR, 'legal', filename)
    
    # Check if the file exists
    if not os.path.exists(file_path):
        raise Http404(f"Документ {filename} не найден")
    
    # Read the file content
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Return the content as a response
    return render(request, 'legal_document.html', {
        'content': content,
        'document_name': document_name,
        'document_title': document_name.replace('-', ' ').title()
    })
