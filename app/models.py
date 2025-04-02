from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from datetime import datetime
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Avg

# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='default.jpg', upload_to='profile_pics')
    bio = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return f'{self.user.username} Profile'
    

class Classes(models.Model):
    name = models.CharField(max_length=255)  
    class_image = models.ImageField(upload_to='class_images', blank=True, null=True, default='default.jpg')
    description = models.TextField()
    price = models.IntegerField()
    schedules = models.OneToOneField('Schedule', on_delete=models.CASCADE)
    students = models.ManyToManyField(User, related_name='classes', blank=True)
    
    def __str__(self):
        return f"{self.name} ({self.start_time} - {self.end_time})"
    
    def clean(self):
        if self.start_time > self.end_time:
            raise ValidationError("Start time must be before end time")
        if self.start_time < datetime.now():
            raise ValidationError("Start time must be in the future")

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


class Coach(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rating = models.IntegerField(default=0, validators=[MinValueValidator(1), MaxValueValidator(5)])
    experience_years = models.IntegerField(default=0)
    expertise = models.CharField(max_length=255, blank=True, null=True)
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} (Coach)"

    def get_average_rating(self):
        
        average_rating = Review.objects.filter(coach=self).aggregate(Avg('rating'))['rating__avg']
        return round(average_rating, 1) if average_rating else None


class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # User who is leaving the review
    coach = models.ForeignKey(Coach, on_delete=models.CASCADE)  # Coach being reviewed
    rating = models.IntegerField(default=1, validators=[MinValueValidator(1), MaxValueValidator(5)])  # Rating from 1 to 5
    comment = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"Review by {self.user.username} for {self.coach.user.username} - Rating: {self.rating}"
    
    def clean(self):
        # Ensure rating is between 1 and 5
        if self.rating < 1 or self.rating > 5:
            raise ValidationError('Rating must be between 1 and 5.')
        
class Products(models.Model):
    image = models.ImageField(upload_to='product_pics')
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    
    def __str__(self):
        return f"{self.name} - {self.price}"
    
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    
    def __str__(self):
        return f"Cart for {self.user.username} - {self.product.name} (x{self.quantity})"
    
    def get_total_price(self):
        return self.product.price * self.quantity
    
class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(max_length=50)  # e.g., 'Credit Card', 'PayPal', etc.
    
    def __str__(self):
        return f"Payment by {self.user.username} - Amount: {self.amount}"