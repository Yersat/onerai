from django import forms
from .models import ShippingAddress


class ShippingAddressForm(forms.ModelForm):
    class Meta:
        model = ShippingAddress
        fields = ['full_name', 'phone', 'address', 'city', 'postal_code', 'is_default']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Полное имя', 'required': True}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Номер телефона', 'required': True}),
            'address': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Адрес', 'required': True}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Город', 'required': True}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Почтовый индекс', 'required': True}),
            'is_default': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'full_name': 'Полное имя',
            'phone': 'Номер телефона',
            'address': 'Адрес',
            'city': 'Город',
            'postal_code': 'Почтовый индекс',
            'is_default': 'Использовать как адрес по умолчанию',
        }
