"""
Views for the designs app in the partners_onerai project.
"""
import os
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.text import slugify
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from .models import Design, Category
from .forms import DesignForm
from utils.onerai_client import submit_design, get_design_status

@login_required
def add_design(request):
    """View for adding a new design"""
    if request.method == "POST":
        form = DesignForm(request.POST, request.FILES)
        if form.is_valid():
            # Create the design in the partners_onerai database
            design = form.save(commit=False)
            design.creator = request.user
            design.save()
            
            # Prepare data for submission to onerai service
            design_data = {
                "name": design.name,
                "description": design.description,
                "price": str(design.price),
                "tags": design.tags,
                "available_colors": design.available_colors,
                "creator_email": request.user.email,
                "creator_username": request.user.username,
                "creator_first_name": request.user.first_name,
                "creator_last_name": request.user.last_name,
                "category_name": design.category.name,
                "design_position": design.design_position,
            }
            
            try:
                # Submit the design to the onerai service
                response = submit_design(design_data, design.image.path)
                
                if response.get('success'):
                    # Store the onerai product ID for future reference
                    design.onerai_product_id = response.get('product_id')
                    design.save()
                    
                    messages.success(request, "Дизайн успешно отправлен на проверку!")
                    return redirect('designs:submission_confirmation', design_id=design.id)
                else:
                    messages.error(request, f"Ошибка при отправке дизайна: {response.get('error')}")
            except Exception as e:
                messages.error(request, f"Ошибка при отправке дизайна: {str(e)}")
        else:
            messages.error(request, "Пожалуйста, исправьте ошибки в форме.")
    else:
        form = DesignForm()
    
    return render(request, "designs/add_design.html", {"form": form})

@login_required
def my_designs(request):
    """View for showing user's designs"""
    designs = Design.objects.filter(creator=request.user).order_by('-created_at')
    
    # Update status for each design from the onerai service
    for design in designs:
        if design.onerai_product_id:
            try:
                status_response = get_design_status(design.onerai_product_id)
                if status_response.get('success'):
                    design.status = status_response.get('status')
                    design.feedback = status_response.get('feedback')
                    design.save()
            except Exception as e:
                print(f"Error updating design status: {str(e)}")
    
    return render(request, "designs/my_designs.html", {"designs": designs})

@login_required
def design_detail(request, design_id):
    """View for showing design details"""
    design = get_object_or_404(Design, id=design_id, creator=request.user)
    
    # Update status from the onerai service
    if design.onerai_product_id:
        try:
            status_response = get_design_status(design.onerai_product_id)
            if status_response.get('success'):
                design.status = status_response.get('status')
                design.feedback = status_response.get('feedback')
                design.save()
        except Exception as e:
            print(f"Error updating design status: {str(e)}")
    
    return render(request, "designs/design_detail.html", {"design": design})

@login_required
def submission_confirmation(request, design_id):
    """View for showing confirmation after design submission"""
    design = get_object_or_404(Design, id=design_id, creator=request.user)
    return render(request, "designs/submission_confirmation.html", {"design": design})

@csrf_exempt
@require_POST
@login_required
def check_design_status(request, design_id):
    """API endpoint for checking design status"""
    design = get_object_or_404(Design, id=design_id, creator=request.user)
    
    if not design.onerai_product_id:
        return JsonResponse({
            'success': False,
            'error': 'Design has not been submitted to onerai'
        })
    
    try:
        status_response = get_design_status(design.onerai_product_id)
        if status_response.get('success'):
            design.status = status_response.get('status')
            design.feedback = status_response.get('feedback')
            design.save()
            
            return JsonResponse({
                'success': True,
                'status': design.status,
                'feedback': design.feedback
            })
        else:
            return JsonResponse({
                'success': False,
                'error': status_response.get('error')
            })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })
