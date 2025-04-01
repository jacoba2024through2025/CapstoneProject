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


class ScheduleForm(forms.ModelForm):
    class Meta:
        model = Schedule
        fields = ['start_date', 'end_date']

    


class TimeSlotForm(forms.ModelForm):
    class Meta:
        model = TimeSlot
        fields = ['fitness_plan', 'day_of_week', 'start_time', 'end_time']

class ActivityForm(forms.ModelForm):
    class Meta:
        model = Activity
        fields = ['timeslot', 'description']

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
        fields = ['title', 'description', 'start_date', 'end_date']
        widgets = {
            'start_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }