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
from django.http import *
from django.core.paginator import Paginator
import os
import requests
from django.views.decorators.csrf import csrf_exempt
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY


class SuccessView(TemplateView):
    template_name = "store/success.html"

def empty_cart(request):
    cart_items = Cart.objects.filter(user=request.user)
    for item in cart_items:
        item.delete()
    return redirect('home')

def cancel_payment(request):
    return redirect('view_cart')

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     session_id = self.request.GET.get('session_id')
    #     if session_id:
    #         session = stripe.checkout.Session.retrieve(session_id)
    #         context['session'] = session
    #     return context


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

def viewOneProduct(request, product_id):
    product = get_object_or_404(Products, id=product_id)
    context = {
        'product': product
    }
    return render(request, 'store/apparel.html', context)

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Products, id=product_id)
    cart_item, created = Cart.objects.get_or_create(user=request.user, product=product)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    return redirect('view_cart')

@login_required
def view_cart(request):
    cart_items = Cart.objects.filter(user=request.user)
    total_price = sum(item.get_total_price() for item in cart_items)
    context = {
        'cart_items': cart_items,
        'total_price': total_price
    }
    return render(request, 'store/cart.html', context)

def delete_cart_item(request, item_id):
    pass


class StripeConfigView(TemplateView):
    template_name = "store/cart.html"

    
@csrf_exempt
def stripe_config(request):
    stripe_config = {'publicKey': settings.STRIPE_PUBLIC_KEY}
    return JsonResponse(stripe_config, safe=False)

@csrf_exempt
def create_checkout_session(request):
    if request.method == 'GET':
        domain_url = 'http://localhost:8000/'
        stripe.api_key = settings.STRIPE_SECRET_KEY
        cart_items = Cart.objects.filter(user=request.user)
        line_items = []
        for item in cart_items:
                    line_items.append(
                        {
                        'price_data': {
                            'currency': 'usd',
                            'product_data': {
                                'name': item.product.name,
                                'metadata': {
                                    'product_id': item.product.id,
                                },
                                'description': item.product.description,
                                'images': [item.product.image],  # Optional: Include product image
                            },
                            'unit_amount': int(item.product.price * 100),  # Convert to cents
                        },
                        'quantity': item.quantity,
                    }
                )
        try:
            checkout_session = stripe.checkout.Session.create(
                success_url=domain_url + 'success?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=domain_url + 'cancelled/',
                payment_method_types=['card'],
                mode='payment',
                
                line_items=line_items
            )
            return JsonResponse({'sessionId': checkout_session['id']})
        except Exception as e:
            print(f"Error creating checkout session: {e}")
            return JsonResponse({'error': str(e)})

def view_schedule_page(request):
    return render(request, 'classes/scheduling.html')


def viewUserProfile(request, username):

    
    user = get_object_or_404(User, username=username)

    
    profile, created = Profile.objects.get_or_create(user=user)

    try:
        coach = Coach.objects.get(user=user)
        user_role = 'Coach'  # Set the role to 'Coach' if this is a coach
    except Coach.DoesNotExist:
        # If the user is a superuser, set the role to 'Superuser', else 'User'
        if user.is_superuser:
            user_role = 'Superuser'
        else:
            user_role = 'User'

    
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
        'user_role': user_role
         
    })
