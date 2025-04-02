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
        
class Classes(models.Model):
    name = models.CharField(max_length=255)  
    class_image = models.ImageField(upload_to='class_images', blank=True, null=True, default='default.jpg')
    description = models.TextField()
    price = models.IntegerField()
    
    students = models.ManyToManyField(User, related_name='classes', blank=True)
    coach = models.ForeignKey(Coach, on_delete=models.CASCADE, blank=True, null=True)



class Event(models.Model):
    
    title = models.CharField(max_length=100)
    description = models.TextField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

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
    description = models.TextField()
    
    def __str__(self):
        return f"{self.name} - {self.price}"
    
