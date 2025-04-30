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
from django.http import *
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.http import HttpResponseRedirect
from .decorators import admin_required
from django.contrib.auth.models import Group
from django.views.decorators.http import require_POST
from django.utils import timezone
from datetime import timedelta
import os
import requests
from django.views.decorators.csrf import csrf_exempt
import stripe
import json

stripe.api_key = settings.STRIPE_SECRET_KEY

@admin_required
def view_admin_page(request):
    return render(request, 'bs-binary-admin/index.html')

@admin_required
def view_admin_chart(request):
    return render(request, 'bs-binary-admin/chart.html')

@admin_required
def view_admin_forms(request):
    
    products = Products.objects.all()

    selected_product = None
    selected_product_id = request.POST.get('product_id') or request.GET.get('product_id')

    
    if selected_product_id:
        selected_product = get_object_or_404(Products, id=selected_product_id)

    
    form = None

    if request.method == 'POST':
        if 'edit_product' in request.POST:
            product_id = request.POST.get('product_id')
            
            if not product_id:
                messages.error(request, "Please select a product to edit.")
                return redirect('forms')

            
            product = get_object_or_404(Products, id=product_id)
            form = CreateProductForm(request.POST, request.FILES, instance=product)

            if form.is_valid():
                print("Form is valid, saving product.")
                form.save()
                messages.success(request, "Product updated successfully!")
                
                return redirect('forms')  
            else:
                print("Form errors:", form.errors)
                print(form.errors)
                messages.error(request, "There was an error updating the product. Please check the form.")
        
        
        elif 'delete_product' in request.POST:
            product_id = request.POST.get('product_id')
            if not product_id:
                messages.error(request, "Please select a product to delete.")
                return redirect('forms') 

            
            product = get_object_or_404(Products, id=product_id)
            product.delete()
            messages.success(request, "Product deleted successfully!")
            return redirect('forms')
        elif 'create_product' in request.POST:
            form = CreateProductForm(request.POST, request.FILES)
            if form.is_valid():
                form.save()
                messages.success(request, "Product created successfully!")
                return redirect('forms')  
            else:
                messages.error(request, "There was an error creating the product. Please check the form.") 

    else:
        
        form = CreateProductForm()

    
    return render(request, 'bs-binary-admin/form.html', {
        'form': form,
        'products': products,
        'selected_product_id': selected_product_id,  
        'selected_product': selected_product, 
    })

@admin_required
def view_admin_tabs(request):
    return render(request, 'bs-binary-admin/tab-panel.html')

@admin_required
def view_admin_ui(request):
    return render(request, 'bs-binary-admin/ui.html')

@admin_required
def view_admin_tables(request):
    # Get all users (excluding superusers, you can adjust this filter as needed)
    users = User.objects.all()

    # Get all coaches
    coaches = Coach.objects.all()

    return render(request, 'bs-binary-admin/table.html', {
        'users': users,
        'coaches': coaches,
    })

@admin_required
def admin_add_remove_coaches(request):
    if request.method == 'POST':
        # Check if the 'selected_users' or 'selected_coaches' form was submitted
        selected_users_ids = request.POST.getlist('selected_users')
        selected_coaches_ids = request.POST.getlist('selected_coaches')

        try:
            coaches_group = Group.objects.get(name='Coaches')
        except Group.DoesNotExist:
            messages.error(request, "Coaches group does not exist!")
            return redirect('tables')

        # Add new users to the coaches group
        for user_id in selected_users_ids:
            user = User.objects.get(id=user_id)
            
            if coaches_group not in user.groups.all():
                user.groups.add(coaches_group)
                Coach.objects.get_or_create(user=user)
                messages.success(request, f"{user.username} has been added as a coach.")
            else:
                messages.info(request, f"{user.username} is already a coach.")

        # Remove selected coaches from the coaches group
        for coach_id in selected_coaches_ids:
            coach = Coach.objects.get(id=coach_id)
            user = coach.user

            if coaches_group in user.groups.all():
                user.groups.remove(coaches_group)
                coach.delete()
                messages.success(request, f"{user.username} has been removed from coaches.")
            else:
                messages.info(request, f"{user.username} was not a coach.")

        return redirect('tables')  # Redirect to the table page after submission

    else:
        return redirect('tables')


class SuccessView(TemplateView):
    template_name = "store/success.html"

def empty_cart(request):
    cart_items = Cart.objects.filter(user=request.user)
    for item in cart_items:
        item.delete()
    return redirect('view_cart')

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
            print("Calling send_mail full")
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

    if request.user.is_authenticated:
        user = request.user
        user_role = 'User'
        try:
            coach = Coach.objects.get(user=user)
            
            user_role = 'Coach'
            
        except Coach.DoesNotExist:
            user_role = 'User'

        return render(request, "mainpage.html", {
            'user': user,
            'user_role': user_role,
        })
    else:
        return render(request, "mainpage.html")

    
    

def view_contact_page(request):

    if request.user.is_authenticated:
        user = request.user
        user_role = 'User'
        try:
            coach = Coach.objects.get(user=user)
            
            user_role = 'Coach'
            
        except Coach.DoesNotExist:
            user_role = 'User'

        return render(request, "contact.html", {
            
            'user_role': user_role,
        })

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

        
        return render(request, 'contact.html', {
            "message_name": message_name,
            "message_sent": True,  
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
    if request.method == "POST" and "password1" in request.POST:  
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Account created successfully! Please login.")
            return redirect('register')  

    context = {'form': form}

    
    if request.method == "POST" and "password" in request.POST:  
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        keep_signed_in = request.POST.get('keep_signed_in')  

        print(f"Attempting to authenticate with Username: {username} and Password: {password}")

        user = authenticate(request, username=username, password=password, email=email)

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
    user_role = ''
    if request.user.is_authenticated:
        user = request.user
        user_role = 'User'
        try:
            coach = Coach.objects.get(user=user)
            
            user_role = 'Coach'
            
        except Coach.DoesNotExist:
            user_role = 'User'
    
    products = Products.objects.filter(hidden=False)
    paginator = Paginator(products, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'products': page_obj,
        'user_role': user_role,
    }
    return render(request, 'store/products.html', context)

def viewOneProduct(request, product_id):
    product = get_object_or_404(Products, id=product_id)
    context = {
        'product': product
    }
    return render(request, 'store/apparel.html', context)

def create_product(request):
    if request.method == 'POST':
        form = CreateProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Product created successfully!")
            return redirect('products')  
    else:
        form = CreateProductForm()
    return render(request, 'store/create_product.html', {'form': form})

@login_required
def add_to_cart(request, product_id):
    print(request.POST["JStoPython"])
    product = get_object_or_404(Products, id=product_id)
    cart_item, created = Cart.objects.get_or_create(user=request.user, product=product)
    print(cart_item)
    print(created)
    cart_item.quantity += int(request.POST["JStoPython"]) - 1
    cart_item.save()
    return redirect('view_cart')



@login_required
def view_cart(request):
    cart_items = Cart.objects.filter(user=request.user)
    total_price = sum(item.get_total_price() for item in cart_items)
    cart_count = 0
    for item in cart_items:
        cart_count += item.quantity
    context = {
        'cart_items': cart_items,
        'total_price': total_price,
        "cart_count": cart_count,
    }
    return render(request, 'store/cart.html', context)

def delete_cart_item(request, product_id):
    cart_item = get_object_or_404(Cart, user=request.user, product_id=product_id)
    cart_item.delete()
    messages.success(request, "Item removed from cart.")
    return redirect('view_cart')


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
            product = item.product

            product_data = {
                'name': product.name,
                'metadata': {
                    'product_id': product.id,
                },
                'description': product.long_description,
            }

            
            if product.image:
                product_data['images'] = [request.build_absolute_uri(product.image.url)]

            line_items.append({
                'price_data': {
                    'currency': 'usd',
                    'product_data': product_data,
                    'unit_amount': int(product.price * 100),  # Stripe expects cents
                },
                'quantity': item.quantity,
            })

        try:
            checkout_session = stripe.checkout.Session.create(
                success_url=domain_url + 'success?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=domain_url + 'cancelled/',
                payment_method_types=['card'],
                mode='payment',
                line_items=line_items,
            )
            return JsonResponse({'sessionId': checkout_session['id']})
        except Exception as e:
            print(f"Error creating checkout session: {e}")
            return JsonResponse({'error': str(e)})



def view_schedule_page(request, username):
    user = get_object_or_404(User, username=username)

    try:
        coach = Coach.objects.get(user=user)
        coach_classes = Classes.objects.filter(coach=coach)
        class_count = coach_classes.count()
    except Coach.DoesNotExist:
        coach_classes = []
        class_count = 0
        messages.error(request, "This user does not have any classes")

    
    for class_item in coach_classes:
        if not hasattr(class_item, 'calendar'):
            ClassCalendar.objects.create(class_name=class_item)

    if request.method == 'POST':
        if 'create_event' in request.POST:
            event_form = EventForm(request.POST)
            class_id = request.POST.get('class_id')  # Get class ID from the form

            if event_form.is_valid():
                event = event_form.save(commit=False)
                print("Color from form:", event_form.cleaned_data.get('color'))
                event.class_item = Classes.objects.get(id=class_id)  # Link event to class
                event.save()
                messages.success(request, "Event created successfully!")
                return redirect('schedule', username=username)
    else:
        event_form = EventForm()

    events = Event.objects.all()
    event_data = []
    for event in events:
        event_data.append({
            'id': event.id,
            'title': event.title,
            'start': event.start_date.isoformat(),
            'end': event.end_date.isoformat(),
            'description': event.description,
            'color': event.color,
        })

    return render(request, 'classes/scheduling.html', {
        'user': user,
        'coach_classes': coach_classes,
        'class_count': class_count,
        'event_form': event_form,
        'events': event_data,
    })

@login_required
def find_coach(request):
    approved_classes = request.user.classes.all()
    coach_states = Coach.objects.exclude(state__isnull=True).exclude(state='').values_list('state', flat=True).distinct()
    coach_schools = Coach.objects.exclude(school__isnull=True).exclude(school='').values_list('school', flat=True).distinct()
    return render(request, 'classes/find_coach.html', {
        'approved_classes': approved_classes,
        'coach_states': coach_states,
        'coach_schools': coach_schools,
    })

from django.db.models import Q

@login_required
def search_coaches(request):
    query = request.GET.get('q', '')
    state_filter = request.GET.get('state')
    school_filter = request.GET.get('school')

    coaches = Coach.objects.filter(
        Q(user__username__icontains=query) |
        Q(first_name__icontains=query) |
        Q(last_name__icontains=query)
    )

    if state_filter:
        coaches = coaches.filter(state=state_filter)

    if school_filter:
        coaches = coaches.filter(school=school_filter)

    approved_class_ids = request.user.classes.values_list('id', flat=True)
    pending_notifications = Notification.objects.filter(
        requester=request.user,
        is_read=False
    ).values_list('related_class', flat=True)

    results = []

    for coach in coaches:
        average_rating = coach.get_average_rating()
        coach_classes = Classes.objects.filter(coach=coach)

        class_info = []
        for coach_class in coach_classes:
            has_access = coach_class.id in approved_class_ids
            is_pending = coach_class.id in pending_notifications

            class_info.append({
                'class_id': coach_class.id,
                'class_name': coach_class.name,
                'class_description': coach_class.description,
                'class_price': coach_class.price,
                'class_image': coach_class.class_image.url if coach_class.class_image else '/media/class_images/default.jpg',
                'has_access': has_access,
                'is_pending': is_pending
            })

        results.append({
            'username': coach.user.username,
            'rating': average_rating if average_rating is not None else 'N/A',
            'profile_image': coach.user.profile.image.url if hasattr(coach.user, 'profile') and coach.user.profile.image else '/media/profile_pics/default.jpg',
            'linked_in': coach.linked_in or 'N/A',
            'experience_years': coach.experience_years,
            'expertise': coach.expertise or 'N/A',
            'first_name': coach.first_name or 'N/A',
            'last_name': coach.last_name or 'N/A',
            'email': coach.user.email or 'N/A',
            'state': coach.state or 'N/A',
            'school': coach.school or 'N/A',
            'classes': class_info
        })

    return JsonResponse(results, safe=False)



from django.core.serializers.json import DjangoJSONEncoder
import json


def get_phase_and_meetings_by_grade_range(grade_range):
    lesson_plan = {
        'prek_4th': {
            'phase_1': {
                'meeting_1': 'Stick Handling: Basic grip and cradle introduction.',
                'meeting_2': 'Passing and Catching: Short-distance throwing and basic catching techniques.',
            },
            'phase_2': {
                'meeting_1': 'Ground Balls: Proper stance and basic scooping mechanics.',
                'meeting_2': 'Game Concepts: Introduction to team collaboration and basic game rules.',
            },
        },
        '5th_7th': {
            'phase_1': {
                'meeting_1': 'Position-Specific Skills: Responsibilities and skills for attack, midfield, or defense positions.',
                'meeting_2': 'Ambidexterity: Practice of basic skills with the non-dominant hand.',
            },
            'phase_2': {
                'meeting_1': 'Game Situations: Intermediate strategies and decision-making.',
                'meeting_2': 'Athletic Conditioning: Focus on agility, speed, and fitness.',
            },
        },
        '8th_10th': {
            'phase_1': {
                'meeting_1': 'Advanced Positional Skills: Mastering advanced techniques and positional responsibilities.',
                'meeting_2': 'Game IQ Development: Initial strategy analysis and scenario anticipation.',
            },
            'phase_2': {
                'meeting_1': 'Physical Conditioning: Strength, speed, and injury prevention training.',
                'meeting_2': 'Mental Preparation: Building mental toughness and resilience.',
            },
        },
        '11th_12th_college': {
            'phase_1': {
                'meeting_1': 'Position Mastery: Refinement of advanced positional tactics.',
                'meeting_2': 'Tactical Understanding: Advanced strategies and adaptive gameplay.',
            },
            'phase_2': {
                'meeting_1': 'Leadership & Communication: On-field leadership and decision-making.',
                'meeting_2': 'Strength & Conditioning: Tailored fitness and nutrition for college-level play.',
            },
        },
    }
    
    
    phase_data = lesson_plan.get(grade_range, {})
    return phase_data

@login_required
def class_dashboard(request, class_id):
    class_obj = get_object_or_404(Classes, pk=class_id)

    is_student = request.user in class_obj.students.all()
    is_coach = hasattr(request.user, 'coach') and class_obj.coach and class_obj.coach.user == request.user

    if not (is_student or is_coach):
        return render(request, 'classes/class_dashboard.html', {
            'class_obj': class_obj,
            'error_message': "You are not authorized to access this class."
        })

    
    selected_student = request.user
    if is_coach:
        student_id = request.GET.get('student_id')
        if student_id:
            selected_student = get_object_or_404(class_obj.students, id=student_id)

    
    meeting = Meeting.objects.filter(class_item=class_obj, player=selected_student).first()
    if meeting:
        grade_range = meeting.grade_range  
    else:
        
        grade_range = 'prek_4th'  

    
    completed_meeting_count = Meeting.objects.filter(
        class_item=class_obj,
        player=selected_student,
        status='completed'
    ).count()

    
    events = class_obj.events.all()
    meetings = class_obj.meetings.filter(hidden=False, player=selected_student)

    event_data = []

    for event in events:
        event_data.append({
            'id': event.id,
            'title': event.title,
            'start': event.start_date.isoformat(),
            'end': event.end_date.isoformat(),
            'description': event.description,
            'color': event.color,
        })

    for meeting in meetings:
        end_time = meeting.start_date + timedelta(hours=1)
        event_data.append({
            'id': f"meeting-{meeting.id}",
            'title': f"Meeting: {meeting.name}",
            'start': meeting.start_date.isoformat(),
            'end': end_time.isoformat(),
            'description': f"{meeting.description} (Player: {meeting.player.first_name})",
            'color': '#007bff',
        })

    form = MeetingForm()

    return render(request, 'classes/class_dashboard.html', {
        'completed_meeting_count': completed_meeting_count,
        'class_obj': class_obj,
        'selected_student': selected_student,
        'students': class_obj.students.all(),  
        'events_json': json.dumps(event_data, cls=DjangoJSONEncoder),
        'form': form,
        'grade_range': grade_range,  
    })

@login_required
def upcoming_events(request, class_id):
    
    class_obj = get_object_or_404(Classes, pk=class_id)

    
    now = timezone.now()

    
    events = class_obj.events.filter(start_date__gte=now).order_by('start_date')
    meetings = class_obj.meetings.filter(start_date__gte=now, hidden=False).order_by('start_date')

    
    upcoming_events = list(events) + list(meetings)

    return render(request, 'classes/upcoming_events.html', {
        'class_obj': class_obj,
        'upcoming_events': upcoming_events
    })

@login_required
def past_sessions(request, class_id):
    class_obj = get_object_or_404(Classes, pk=class_id)

    # Get the current time
    now = timezone.now()

    # Get past events and meetings for the specific class (events and meetings that have ended)
    events = class_obj.events.filter(end_date__lte=now).order_by('-end_date')
    meetings = class_obj.meetings.filter(start_date__lte=now, hidden=False).order_by('-start_date')

    
    past_events = list(events) + list(meetings)

    return render(request, 'classes/past_sessions.html', {
        'class_obj': class_obj,
        'past_events': past_events
    })

from django.http import JsonResponse
from .models import Meeting

@require_POST
def delete_meeting(request):
    if request.method == 'POST':
        # Get the meeting ID from the request
        data = json.loads(request.body)
        meeting_id = data.get('meeting_id')

        # Logic to mark the meeting as complete and delete it
        meeting = Meeting.objects.get(id=meeting_id)

        # Mark meeting as completed
        meeting.status = 'completed'  # Use 'status' to mark as completed
        meeting.save()

        # Get the count of completed meetings
        completed_meeting_count = Meeting.objects.filter(status='completed').count()  # Use 'status' here

        # Return updated information in response
        return JsonResponse({
            'status': 'success',
            'completed_meeting_count': completed_meeting_count,
            'updated_description': meeting.description,  # Return updated description
        })



from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from .models import Classes, Meeting
from .forms import MeetingForm
  # import from your store app
from datetime import timedelta

@login_required
def schedule_meeting_from_dashboard(request, class_id):
    class_obj = get_object_or_404(Classes, id=class_id)

    
    existing_pending = Meeting.objects.filter(
        class_item=class_obj,
        player=request.user,
        status='pending'
    ).exists()

    if existing_pending:
        return render(request, 'classes/class_dashboard.html', {
            'class_obj': class_obj,
            'form': MeetingForm(),
            'error_message': "You must complete your current meeting before scheduling a new one."
        })

    if request.method == 'POST':
        form = MeetingForm(request.POST)
        if form.is_valid():
            meeting = form.save(commit=False)
            meeting.class_item = class_obj
            meeting.coach = class_obj.coach
            meeting.player = request.user

            # Grade-based price logic
            exact_grade = request.POST.get('exact_grade', '').strip()
            grade_prices = {
                'PreK': 60,
                'K': 80, '1st': 80, '2nd': 80, '3rd': 80, '4th': 80,
                '5th': 60, '6th': 80, '7th': 80,
                '8th': 80, '9th': 100, '10th': 100,
                '11th': 80, '12th': 100, 'College': 100
            }
            meeting.exact_grade = exact_grade
            meeting.price = grade_prices.get(exact_grade, 45.00)

            
            grade_range = request.POST.get('grade_range', 'prek_4th')
            meeting.grade_range = grade_range

            
            completed_phase1 = Meeting.objects.filter(
                class_item=class_obj,
                player=request.user,
                grade_range=grade_range,
                phase='phase_1',
                status='completed'
            ).count()
            meeting.phase = 'phase_2' if completed_phase1 >= 2 else 'phase_1'
            meeting.description = ''
            meeting.save()

           
            product = Products.objects.create(
                name=f"{class_obj.name} Session - {meeting.start_date.strftime('%b %d, %Y')}",
                price=meeting.price,
                description=f"Session with {meeting.coach.user.username} for {meeting.exact_grade}",
                hidden=True,
                image=None  
            )

            
            Cart.objects.create(
                user=request.user,
                product=product,
                quantity=1
            )

            return redirect('view_cart')
    else:
        form = MeetingForm()

    return render(request, 'classes/class_dashboard.html', {
        'class_obj': class_obj,
        'form': form,
    })


@login_required
def chat_room(request, class_id):
    class_obj = get_object_or_404(Classes, id=class_id)

    # Only allow access to students or the coach
    if request.user not in class_obj.students.all() and request.user != class_obj.coach.user:
        return HttpResponseForbidden("You're not authorized to view this chat.")

    messages = ChatMessage.objects.filter(class_obj=class_obj).order_by('timestamp')

    
    for msg in messages:
        if msg.attachment:
            # Check if the file is an image based on the extension
            msg.is_image = msg.attachment.url.lower().endswith(('.jpg', '.jpeg', '.png', '.gif'))
        else:
            msg.is_image = False

    if request.method == 'POST':
        form = ChatMessageForm(request.POST, request.FILES)
        if form.is_valid():
            chat_message = form.save(commit=False)
            chat_message.user = request.user
            chat_message.class_obj = class_obj
            chat_message.save()
            return redirect('chat_room', class_id=class_obj.id)
    else:
        form = ChatMessageForm()

    return render(request, 'classes/chat_room.html', {
        'form': form,
        'messages': messages,
        'class_obj': class_obj
    })

def get_class_calendar(request, class_id):
    
    class_item = get_object_or_404(Classes, id=class_id)
    
    
    events = Event.objects.filter(class_item=class_item)  
    
    event_data = []
    for event in events:
        event_data.append({
            'id': event.id,
            'title': event.title,
            'start': event.start_date.isoformat(),
            'end': event.end_date.isoformat(),
            'description': event.description,
            'color': event.color,  
        })
    
    return JsonResponse({'events': event_data})


from django.urls import reverse

from django.views.decorators.http import require_POST

@require_POST
def delete_event(request, event_id):
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            event = Event.objects.get(pk=event_id)
            event.delete()
            return JsonResponse({'status': 'success', 'message': 'Event deleted successfully'})
        except Event.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Event not found'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request'})

def update_event(request, event_id):
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        event = get_object_or_404(Event, id=event_id)
        form = EventForm(request.POST, instance=event)

        if form.is_valid():
            form.save()
           
            username = request.user.username
            redirect_url = reverse('schedule', args=[username])
            return JsonResponse({
                'status': 'success',
                'message': 'Event updated successfully!',
                'redirect_url': redirect_url
            })
        else:
            return JsonResponse({'status': 'error', 'message': 'There was an error updating the event.'})




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
        if user.groups.filter(name='Admin').exists():
            user_role = 'Admin'

    
    if request.method == 'POST':
        form_type = request.POST.get('form_type')

        
        if form_type == 'profile':
            form = ProfileImageForm(request.POST, request.FILES, instance=profile)
            coach_form = CoachProfileForm(instance=coach) if user_role == 'Coach' else None

            if form.is_valid():
                form.save()
                return redirect('profile', username=username)

        
        elif form_type == 'coach' and user_role == 'Coach':
            coach_form = CoachProfileForm(request.POST, instance=coach)
            form = ProfileImageForm(instance=profile)

            if coach_form.is_valid():
                coach_form.save()
                return redirect('profile', username=username)
    else:
        form = ProfileImageForm(instance=profile)
        coach_form = CoachProfileForm(instance=coach) if user_role == 'Coach' else None

    return render(request, 'profile.html', {
        'form': form,
        'coach_form': coach_form,
        'user': user,
        'profile': profile,
        'user_role': user_role,
        'coach_classes': coach_classes,
        'class_count': class_count,
    })

@login_required
def request_class_access(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        class_id = data.get('class_id')
        
        
        class_obj = Classes.objects.get(id=class_id)
        coach = class_obj.coach.user
        
        
        Notification.objects.create(
            user=coach,  
            message=f"{request.user.username} has requested access to your class: {class_obj.name}.",
            related_class=class_obj,
            requester=request.user
        )
        
        return JsonResponse({'status': 'success', 'message': 'Request sent to the coach.'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})

def approve_class_access(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id)

    if notification.user != request.user:
        return JsonResponse({'status': 'error', 'message': 'You are not authorized to approve this request.'})

    class_obj = notification.related_class
    requester = notification.requester

    
    requester.classes.add(class_obj)

    
    notification.is_read = True
    notification.save()

    
    return redirect('notifications')

@login_required
def deny_class_access(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id)

    if notification.user != request.user:
        messages.error(request, 'You are not authorized to deny this request.')
        return redirect('notifications')

    
    notification.is_read = True
    notification.save()

    messages.info(request, 'You denied the class access request.')
    return redirect('notifications')

@login_required
def notifications_view(request):
    unread_notifications = request.user.notifications.filter(is_read=False).order_by('-timestamp')
    read_notifications = request.user.notifications.filter(is_read=True).order_by('-timestamp')
    
    return render(request, 'store/notifications.html', {
        'unread_notifications': unread_notifications,
        'read_notifications': read_notifications,
        'unread_count': unread_notifications.count(),
    })

@login_required
def approved_classes_view(request):
    if request.user.is_authenticated:
        user = request.user
        user_role = 'User'
        try:
            coach = Coach.objects.get(user=user)
            
            user_role = 'Coach'
            
        except Coach.DoesNotExist:
            user_role = 'User'


    approved_classes = request.user.classes.all()  
    return render(request, 'store/approved_classes.html', {
        'approved_classes': approved_classes,
        "user_role": user_role,
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



        
