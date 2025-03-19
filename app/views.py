from django.shortcuts import render
from app.forms import *
from app.models import *
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages


def view_main_page(request):
    return render(request, "mainpage.html")

def view_login(request):
    if request.user.is_authenticated:
        print("You are already logged in")
        return redirect('home')
    else:
        print("You are not authenticated")

    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        
        print(f"Attempting to authenticate with Username: {username} and Password: {password}")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            
            messages.error(request, "Username or Password is Incorrect")
            print("Authentication failed")

    
    return render(request, 'login.html')

def register(request):
    if request.user.is_authenticated:
        return redirect('home')

    form = CreateUserForm()

    if request.method == "POST":
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created successfully! Please login.")
            return redirect('login')  

    context = {'form': form}
    return render(request, 'register.html', context)

def viewLogout(request):
    logout(request)
    return redirect('login')