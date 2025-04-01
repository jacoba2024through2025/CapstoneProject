from django.shortcuts import render
from app.forms import *
from app.models import *
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import send_mail, BadHeaderError
from django.conf import settings
from .forms import ContactForm
from django.shortcuts import reverse
from django.views.generic import TemplateView, FormView
from django.http import HttpResponse
from app.models import *
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect
import os
import requests

class SuccessView(TemplateView):
    template_name = "success.html"


class ContactView(FormView):
    form_class = ContactForm
    template_name = "store/contact.html"

    def get_success_url(self):
        return reverse("contact")

    def form_valid(self, form):
        email = form.cleaned_data.get("email")
        subject = form.cleaned_data.get("subject")
        message = form.cleaned_data.get("message")

        full_message = f"""
            Received message below from {email}, {subject}
            ________________________


            {message}
            """
        try:
            send_mail(
                subject="Received contact form submission",
                message=full_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.CONTACT_EMAIL],
            )
        except BadHeaderError:
            return HttpResponse('Invalid header found.')
        except Exception as e:
            # Log the error or handle it as needed
            print(f"Error sending email: {e}")
            messages.error(self.request, "There was an error sending your message. Please try again later.")
            return self.form_invalid(form)

        return super(ContactView, self).form_valid(form)
    


def view_main_page(request):
    return render(request, "mainpage.html")

def view_contact_page(request):
    if request.method == "POST":
        message_name = request.POST['message-name']
        message_email = request.POST['message-email']
        message_subject = request.POST['message-subject']
        message = request.POST['message']

        # Send the email
        send_mail(
            subject=message_subject,  # Subject of the email
            message=message,          # Body of the email
            from_email=message_email, # From the email entered in the form
            recipient_list=['zombiejake2005@gmail.com'],  # To the admin's email
        )

        # Return a success message or render a thank you page
        return render(request, 'contact.html', {
            "message_name": message_name,
            "message_sent": True,  # Flag to indicate success
        })

    else:
        return render(request, "contact.html", {})

def view_login(request):
    
    
    

    
    return render(request, 'register.html')

def register(request):
    if request.user.is_authenticated:
        return redirect('home')  # If already logged in, redirect to home

    form = CreateUserForm()

    # Handling the registration form
    if request.method == "POST" and "password1" in request.POST:  # Registration form
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created successfully! Please login.")
            return redirect('register')  

    context = {'form': form}

    # Handling the login form
    if request.method == "POST" and "password" in request.POST:  # Login form
        username = request.POST.get('username')
        password = request.POST.get('password')
        keep_signed_in = request.POST.get('keep_signed_in')  # Check if 'Keep me signed in' was checked

        print(f"Attempting to authenticate with Username: {username} and Password: {password}")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            
            if keep_signed_in:
                print("User opted to stay signed in.")
                
            else:
                print("User did not opt to stay signed in.")
                

            return redirect('home')  
        else:
            messages.error(request, "Username or Password is Incorrect")
            print("Authentication failed")

    return render(request, 'register.html', context)

def viewLogout(request):
    logout(request)
    return redirect('register')

def viewProducts(request):
    products = Products.objects.all()
    paginator = Paginator(products, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'products': page_obj
    }
    return render(request, 'store/products.html', context)

def addProducts(request):
    pass



def view_schedule_page(request, username):
    user = get_object_or_404(User, username=username)

    try:
        coach = Coach.objects.get(user=user)
        coach_classes = Classes.objects.filter(coach=coach)
        class_count = coach_classes.count()
    except Coach.DoesNotExist:
        coach_classes = []
        class_count = 0
        messages.error(request, "This user does not have any coaches")

    
    if request.method == 'POST':
        if 'create_event' in request.POST:  
            event_form = EventForm(request.POST)
            if event_form.is_valid():
                event_form.save()  # Save the event
                messages.success(request, "Event created successfully!")
                return redirect('schedule', username=username) 
        else:  
            class_id = request.POST.get('class_id')
            selected_class = Classes.objects.get(id=class_id)

            schedule_form = ScheduleForm(request.POST)
            if schedule_form.is_valid():
                schedule = schedule_form.save(commit=False)
                schedule.scheduled_class = selected_class
                schedule.user = user
                schedule.save()
    else:
        schedule_form = ScheduleForm()
        event_form = EventForm()  

    
    events = Event.objects.all()
    event_data = []
    for event in events:
        event_data.append({
            'title': event.title,
            'start': event.start_date.isoformat(),
            'end': event.end_date.isoformat(),
            'description': event.description,
            'color': '#ff7c00',  
        })
    

    return render(request, 'classes/scheduling.html', {
        'user': user,
        'coach_classes': coach_classes,
        'class_count': class_count,
        'schedule_form': schedule_form,
        'event_form': event_form,  
        'events': event_data,  
    })







def viewUserProfile(request, username):
    user = get_object_or_404(User, username=username)

    profile, created = Profile.objects.get_or_create(user=user)

    
    user_role = 'User'  
    coach_classes = []  
    class_count = 0  

    try:
        coach = Coach.objects.get(user=user)
        user_role = 'Coach'  
        coach_classes = Classes.objects.filter(coach=coach)
        class_count = coach_classes.count() 
    except Coach.DoesNotExist:
        
        if user.is_superuser:
            user_role = 'Superuser'
    
    if request.method == 'POST':
        form = ProfileImageForm(request.POST, request.FILES, instance=profile)
        
        if form.is_valid():
            form.save()  
            return redirect('profile', username=username)  
    else:
        form = ProfileImageForm(instance=profile)

    return render(request, 'profile.html', {
        'form': form,
        'user': user,
        'profile': profile,
        'user_role': user_role,
        'coach_classes': coach_classes,
        'class_count': class_count,
    })

@login_required
def create_class(request):
    
    coach = Coach.objects.get(user=request.user)
    
    if request.method == 'POST':
        form = CreateClassForm(request.POST, request.FILES)
        
        if form.is_valid():
            
            new_class = form.save(commit=False)
            new_class.coach = coach
            new_class.save()
            
            return redirect('profile', username=request.user.username)  
            
    else:
        form = CreateClassForm()
        
    return render(request, 'classes/create_class.html', {'form': form})



def edit_class(request, class_id):
    
    class_instance = get_object_or_404(Classes, id=class_id)
    
    
    if request.user != class_instance.coach.user:
        return redirect('profile', username=request.user.username)

    
    if request.method == 'POST':
        if 'delete_class' in request.POST:  
            
            class_instance.delete()
            return redirect('profile', username=request.user.username)  

        
        form = ClassEditForm(request.POST, request.FILES, instance=class_instance)
        if form.is_valid():
            form.save()
            return redirect('profile', username=request.user.username)  
    else:
        form = ClassEditForm(instance=class_instance)

    return render(request, 'classes/edit_class.html', {'form': form, 'class_instance': class_instance})



