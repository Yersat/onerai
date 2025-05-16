"""
Forms for the designs app in the partners_onerai project.
"""
from django import forms
from .models import Design, Category

class DesignForm(forms.ModelForm):
    """Form for creating and editing designs"""
    category_name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control form-control-lg'})
    )
    
    class Meta:
        model = Design
        fields = ['name', 'description', 'price', 'image', 'tags', 'available_colors', 'design_position']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Например: Горы Казахстана'}),
            'description': forms.Textarea(attrs={'class': 'form-control form-control-lg', 'rows': 4, 'placeholder': 'Опишите ваш дизайн...'}),
            'price': forms.NumberInput(attrs={'class': 'form-control form-control-lg', 'min': 0, 'step': '0.01', 'placeholder': 'Например: 5990'}),
            'tags': forms.TextInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Например: природа, горы, Казахстан'}),
            'available_colors': forms.TextInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'black,white,red,blue'}),
            'design_position': forms.HiddenInput(),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk and self.instance.category:
            self.fields['category_name'].initial = self.instance.category.name
    
    def save(self, commit=True):
        design = super().save(commit=False)
        
        # Get or create the category
        category_name = self.cleaned_data.get('category_name')
        if category_name:
            category, created = Category.objects.get_or_create(name=category_name)
            design.category = category
        
        if commit:
            design.save()
        
        return design
