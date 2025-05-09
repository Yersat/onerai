from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .forms import CreatorRegistrationForm, CreatorLoginForm
from .models import CreatorProfile

# Create your views here.


def register_creator(request):
    if request.method == "POST":
        form = CreatorRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Registration successful! Welcome to onerai.")
            next_url = request.POST.get("next") or request.GET.get("next")
            if next_url:
                return redirect(next_url)
            return redirect("store:index")
    else:
        form = CreatorRegistrationForm()
    return render(request, "creators/register.html", {"form": form})


def login_creator(request):
    if request.method == "POST":
        form = CreatorLoginForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {user.get_full_name()}!")
                # Get the next parameter or default to home
                next_url = request.POST.get("next") or request.GET.get("next")
                if next_url:
                    return redirect(next_url)
                return redirect("store:index")
    else:
        form = CreatorLoginForm()
    return render(request, "creators/login.html", {"form": form, "next": request.GET.get("next", "")})


@login_required
def creator_profile(request):
    # Show the creator profile if it exists
    try:
        profile = request.user.creator_profile
    except CreatorProfile.DoesNotExist:
        profile = None
    return render(
        request, "creators/profile.html", {"creator": request.user, "profile": profile}
    )
