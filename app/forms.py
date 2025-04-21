from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms
from app.models import *
class ProfileImageForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['image', 'bio']

class CreateUserForm(UserCreationForm):
    
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class ContactForm(forms.Form):
    email = forms.EmailField(
        widget=forms.TextInput(attrs={"placeholder": "Your e-mail"})
    )
    subject = forms.CharField(widget=forms.TextInput(attrs={"placeholder": "Subject"}))
    message = forms.CharField(
        widget=forms.Textarea(attrs={"placeholder": "Your message"})
    )

class CreateClassForm(forms.ModelForm):
    class Meta:
        model = Classes
        fields = ['name', 'class_image', 'description', 'price']

        ###Widgets and placeholders
        name = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'placeholder': 'Class Name'}))
        description = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Class Description'}))
        price = forms.IntegerField(widget=forms.NumberInput(attrs={'placeholder': 'Price'}))

class ClassEditForm(forms.ModelForm):
    class Meta:
        model = Classes
        fields = ['name', 'description', 'price', 'class_image']

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'description', 'start_date', 'end_date', 'color']
        widgets = {
            'start_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'color': forms.TextInput(attrs={'type': 'color'}),  # color input
        }

class MeetingForm(forms.ModelForm):
    class Meta:
        model = Meeting
        fields = ['name', 'description', 'start_date', 'end_date']
        widgets = {
            'start_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class ChatMessageForm(forms.ModelForm):
    class Meta:
        model = ChatMessage
        fields = ['message', 'attachment']
        widgets = {
            'message': forms.Textarea(attrs={
                'rows': 2,
                'placeholder': 'Type a message...',
                'class': 'form-control'
            }),
        }

class CreateProductForm(forms.ModelForm):
    class Meta:
        model = Products
        fields = ['name', 'description', 'price', 'image']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Product Name'}),
            'description': forms.Textarea(attrs={'placeholder': 'Product Description'}),
            'price': forms.NumberInput(attrs={'placeholder': 'Price'}),
        }

class CoachProfileForm(forms.ModelForm):
    class Meta:
        model = Coach
        fields = ['first_name', 'last_name', 'expertise', 'experience_years', 'state', 'school', 'linked_in']

        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': 'Enter first name'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Enter last name'}),
            'expertise': forms.TextInput(attrs={'placeholder': 'Enter expertise'}),
            'experience_years': forms.NumberInput(attrs={'placeholder': 'Years of experience'}),
            'state': forms.Select(attrs={'class': 'state-select'}),
            'school': forms.TextInput(attrs={'placeholder': 'Enter school name (optional)'}),
            'linked_in': forms.URLInput(attrs={'placeholder': 'Enter LinkedIn profile URL (optional)'}),
        }