from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import CreatorProfile


class CreatorRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    bio = forms.CharField(widget=forms.Textarea, required=False)
    portfolio_url = forms.URLField(required=False)
    instagram_handle = forms.CharField(max_length=30, required=False)

    class Meta:
        model = User
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "password1",
            "password2",
        )

    def save(self, commit=True):
        user = super().save(commit=commit)
        # Create the CreatorProfile
        CreatorProfile.objects.create(
            user=user,
            bio=self.cleaned_data.get("bio", ""),
            portfolio_url=self.cleaned_data.get("portfolio_url", ""),
            instagram_handle=self.cleaned_data.get("instagram_handle", ""),
        )
        return user


class CreatorLoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Username or Email"}
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={"class": "form-control", "placeholder": "Password"}
        )
    )
