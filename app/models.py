from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from datetime import datetime

# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='default.jpg', upload_to='profile_pics')
    bio = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return f'{self.user.username} Profile'

class Schedule(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE) 
    name = models.CharField(max_length=255)  
    start_date = models.DateField()  
    end_date = models.DateField()  
    
    def __str__(self):
        return f"{self.name} ({self.start_date} - {self.end_date})"
    
class TimeSlot(models.Model):
    
    DAY_OF_WEEK_CHOICES = [
        ('Monday', 'Monday'),
        ('Tuesday', 'Tuesday'),
        ('Wednesday', 'Wednesday'),
        ('Thursday', 'Thursday'),
        ('Friday', 'Friday'),
        ('Saturday', 'Saturday'),
        ('Sunday', 'Sunday'),
    ]

    TIME_CHOICES = [
        ('06:00 AM', '06:00 AM'),
        ('06:30 AM', '06:30 AM'),
        ('07:00 AM', '07:00 AM'),
        ('07:30 AM', '07:30 AM'),
        ('08:00 AM', '08:00 AM'),
        ('08:30 AM', '08:30 AM'),
        ('09:00 AM', '09:00 AM'),
        ('09:30 AM', '09:30 AM'),
        ('10:00 AM', '10:00 AM'),
        ('10:30 AM', '10:30 AM'),
        ('11:00 AM', '11:00 AM'),
        ('11:30 AM', '11:30 AM'),
        ('12:00 PM', '12:00 PM'),
        ('12:30 PM', '12:30 PM'),
        ('01:00 PM', '01:00 PM'),
        ('01:30 PM', '01:30 PM'),
        ('02:00 PM', '02:00 PM'),
        ('02:30 PM', '02:30 PM'),
        ('03:00 PM', '03:00 PM'),
        ('03:30 PM', '03:30 PM'),
        ('04:00 PM', '04:00 PM'),
        ('04:30 PM', '04:30 PM'),
        ('05:00 PM', '05:00 PM'),
        ('05:30 PM', '05:30 PM'),
        ('06:00 PM', '06:00 PM'),
        ('06:30 PM', '06:30 PM'),
        ('07:00 PM', '07:00 PM'),
        ('07:30 PM', '07:30 PM'),
        
    ]
    
    fitness_plan = models.ForeignKey(Schedule, related_name='timeslots', on_delete=models.CASCADE)
    day_of_week = models.CharField(
        max_length=9,  
        choices=DAY_OF_WEEK_CHOICES, 
    )
    start_time = models.CharField(
        max_length=8,
        choices=TIME_CHOICES,
          
    )  
    end_time = models.CharField(
        max_length=8,
        choices=TIME_CHOICES,
          
    )
    
    def __str__(self):
        return f"{self.day_of_week} {self.start_time} - {self.end_time}"
    
    
    
class Activity(models.Model):
    timeslot = models.ForeignKey(TimeSlot, related_name='activities', on_delete=models.CASCADE)
    description = models.TextField()  
    
    def __str__(self):
        return f"Activity for {self.timeslot} - {self.description}"

