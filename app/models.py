from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from datetime import datetime
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Avg

US_STATES = [
    ('AL', 'Alabama'),
    ('AK', 'Alaska'),
    ('AZ', 'Arizona'),
    ('AR', 'Arkansas'),
    ('CA', 'California'),
    ('CO', 'Colorado'),
    ('CT', 'Connecticut'),
    ('DE', 'Delaware'),
    ('FL', 'Florida'),
    ('GA', 'Georgia'),
    ('HI', 'Hawaii'),
    ('ID', 'Idaho'),
    ('IL', 'Illinois'),
    ('IN', 'Indiana'),
    ('IA', 'Iowa'),
    ('KS', 'Kansas'),
    ('KY', 'Kentucky'),
    ('LA', 'Louisiana'),
    ('ME', 'Maine'),
    ('MD', 'Maryland'),
    ('MA', 'Massachusetts'),
    ('MI', 'Michigan'),
    ('MN', 'Minnesota'),
    ('MS', 'Mississippi'),
    ('MO', 'Missouri'),
    ('MT', 'Montana'),
    ('NE', 'Nebraska'),
    ('NV', 'Nevada'),
    ('NH', 'New Hampshire'),
    ('NJ', 'New Jersey'),
    ('NM', 'New Mexico'),
    ('NY', 'New York'),
    ('NC', 'North Carolina'),
    ('ND', 'North Dakota'),
    ('OH', 'Ohio'),
    ('OK', 'Oklahoma'),
    ('OR', 'Oregon'),
    ('PA', 'Pennsylvania'),
    ('RI', 'Rhode Island'),
    ('SC', 'South Carolina'),
    ('SD', 'South Dakota'),
    ('TN', 'Tennessee'),
    ('TX', 'Texas'),
    ('UT', 'Utah'),
    ('VT', 'Vermont'),
    ('VA', 'Virginia'),
    ('WA', 'Washington'),
    ('WV', 'West Virginia'),
    ('WI', 'Wisconsin'),
    ('WY', 'Wyoming'),
]

# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='default.jpg', upload_to='profile_pics')
    bio = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return f'{self.user.username} Profile'
    


class Coach(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rating = models.IntegerField(default=0, validators=[MinValueValidator(1), MaxValueValidator(5)])
    experience_years = models.IntegerField(default=0)
    expertise = models.CharField(max_length=255, blank=True, null=True)
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, blank=True, null=True)
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    state = models.CharField(max_length=2, choices=US_STATES, blank=True, null=True)
    school = models.CharField(max_length=255, blank=True, null=True)
    linked_in = models.URLField(blank=True, null=True)
    

    def __str__(self):
        return f"{self.user.username} (Coach)"

    def get_average_rating(self):
        
        average_rating = Review.objects.filter(coach=self).aggregate(Avg('rating'))['rating__avg']
        return round(average_rating, 1) if average_rating else None

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")  # receiver (coach)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    # Optional additions:
    related_class = models.ForeignKey('Classes', on_delete=models.CASCADE, null=True, blank=True)
    requester = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name="class_requests")

    def __str__(self):
        return f"Notification for {self.user.username} - {'Read' if self.is_read else 'Unread'}"

        
class Classes(models.Model):
     name = models.CharField(max_length=255)  
     class_image = models.ImageField(upload_to='class_images', blank=True, null=True, default='default.jpg')
     description = models.TextField()
     price = models.IntegerField()
    
     students = models.ManyToManyField(User, related_name='classes', blank=True)
     coach = models.ForeignKey(Coach, on_delete=models.CASCADE, blank=True, null=True)

class ClassCalendar(models.Model):
    class_name = models.OneToOneField(Classes, on_delete=models.CASCADE, related_name='calendar')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Calendar for {self.class_name.name}"

class Event(models.Model):
    
    title = models.CharField(max_length=100)
    description = models.TextField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    class_item = models.ForeignKey('Classes', on_delete=models.CASCADE, related_name='events', null=True, blank=True)
    color = models.CharField(max_length=7, default="#ff7c00")
    
    def __str__(self):
        return self.title
  
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
    hidden = models.BooleanField(default=False)
    description = models.TextField()
    
    def __str__(self):
        return f"{self.name} - {self.price}"
    
class Meeting(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    price = models.DecimalField(max_digits=10, decimal_places=2, default=45.00)
    hidden = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} ({self.start_date} - {self.end_date})"
    
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