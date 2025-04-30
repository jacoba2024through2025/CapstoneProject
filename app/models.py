from PIL import Image
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from datetime import datetime
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Avg
from datetime import timedelta
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
    CATEGORY_CHOICES = [
        ('clothing', 'Clothing'),
        ('equipment', 'Equipment'),
        ('accessories', 'Accessories'),
        ('other', 'Other'),
    ]

    image = models.ImageField(upload_to='product_pics', blank=True, null=True)
    name = models.CharField(max_length=255)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='other')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    hidden = models.BooleanField(default=False)
    short_description = models.TextField(blank=True, null=True)
    long_description = models.TextField()
    
    def __str__(self):
        return f"{self.name} - {self.price}"
    
    def save(self, *args, **kwargs):
        super().save()
        img = Image.open(self.image.path)
        width, height = img.size

        if width > 800 or height > 800:
            img.thumbnail((width, height))

        if height < width:
            # make square by cutting off equal amounts left and right
            left = (width - height) / 2
            right = (width + height) / 2
            top = 0
            bottom = height
            img = img.crop((left, top, right, bottom))

        elif width < height:
            # make square by cutting off bottom
            left = (width - height) / 2
            right = width
            top = 0
            bottom = width
            img = img.crop((left, top, right, bottom))

        if width > 800 and height > 800:
            img.thumbnail((width, height))

        img.save(self.image.path)
    
class Meeting(models.Model):
    PHASE_CHOICES = [
        ('phase_1', 'Phase 1: Introduction & Basics'),
        ('phase_2', 'Phase 2: Skill Reinforcement'),
        ('phase_3', 'Phase 3: Custom Session'),
        
    ]
    GRADE_RANGE_CHOICES = [
        ('prek_4th', 'PreK - 4th Grade'),
        ('5th_7th', '5th - 7th Grade'),
        ('8th_10th', '8th - 10th Grade'),
        ('11th_12th_college', '11th - 12th Grade & College Students'),
    ]

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
    ]

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    price = models.DecimalField(max_digits=10, decimal_places=2, default=45.00)
    hidden = models.BooleanField(default=False)
    exact_grade = models.CharField(max_length=20, blank=True, null=True)
    phase = models.CharField(max_length=10, choices=PHASE_CHOICES, default='phase_1')
    grade_range = models.CharField(max_length=20, choices=GRADE_RANGE_CHOICES, default='prek_4th')
    
    class_item = models.ForeignKey(Classes, on_delete=models.CASCADE, related_name='meetings', null=True, blank=True)
    coach = models.ForeignKey(Coach, on_delete=models.SET_NULL, null=True, blank=True)
    player = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    def mark_as_completed(self):
        self.status = 'completed'
        self.description = self.auto_generate_description()  # Update description when marking as completed
        self.save()
    
    def get_reset_completed_count(self):
        raw_completed = Meeting.objects.filter(
            player=self.player,
            class_item=self.class_item,
            status='completed'
        ).count()
        return raw_completed % 4

    def __str__(self):
        return f"{self.name} ({self.start_date} - {self.end_date})"

    def auto_generate_description(self, phase=None):
        if (phase or self.phase) == 'phase_3':  
            return ''
        
        lesson_plan = {
            'prek_4th': {
                'phase_1': {
                    'meeting_1': "Stick Handling: Basic grip and cradle introduction.",
                    'meeting_2': "Passing and Catching: Short-distance throwing and basic catching techniques.",
                },
                'phase_2': {
                    'meeting_1': "Ground Balls: Proper stance and basic scooping mechanics.",
                    'meeting_2': "Game Concepts: Introduction to team collaboration and basic game rules in simplified game scenarios.",
                },
            },
            '5th_7th': {
                'phase_1': {
                    'meeting_1': "Position-Specific Skills: Fundamental responsibilities and skills specific to attack, midfield, or defense positions.",
                    'meeting_2': "Ambidexterity: Initial practice of basic skills using a non-dominant hand.",
                },
                'phase_2': {
                    'meeting_1': "Game Situations: Understanding intermediate strategies and developing decision-making in controlled game scenarios.",
                    'meeting_2': "Athletic Conditioning: Emphasis on agility, speed, and overall fitness improvement.",
                },
            },
            '8th_10th': {
                'phase_1': {
                    'meeting_1': "Advanced Positional Skills: Mastering advanced techniques and positional responsibilities.",
                    'meeting_2': "Game IQ Development: Initial strategy analysis and scenario anticipation.",
                },
                'phase_2': {
                    'meeting_1': "Physical Conditioning: Tailored training for improved strength, speed, and injury prevention.",
                    'meeting_2': "Mental Preparation: Developing mental toughness, resilience, and strategies for competitive pressure.",
                },
            },
            '11th_12th_college': {
                'phase_1': {
                    'meeting_1': "Position Mastery: Refinement of advanced positional tactics and elite skill execution.",
                    'meeting_2': "Tactical Understanding: Deepening knowledge of complex strategies and adaptive gameplay.",
                },
                'phase_2': {
                    'meeting_1': "Leadership & Communication: Developing effective team leadership, on-field communication, and decision-making.",
                    'meeting_2': "Strength & Conditioning: Comprehensive and tailored fitness and nutrition plans suitable for college-level play.",
                },
            },
        }

        effective_phase = phase or self.phase

        # Fetch all completed meetings for this player in the same class, grade range, and phase
        completed_meetings = Meeting.objects.filter(
            class_item=self.class_item,
            player=self.player,
            grade_range=self.grade_range,
            phase=effective_phase,
            status='completed'
        ).count()

        # Determine which meeting (1 or 2) this is
        meeting_key = f"meeting_{completed_meetings + 1}"

        phase_lessons = lesson_plan.get(self.grade_range, {}).get(self.phase, {})
        return phase_lessons.get(meeting_key, "Lesson description not found.")

    def save(self, *args, **kwargs):
        if not self.description:
            self.description = self.auto_generate_description()

        if not self.end_date and self.start_date:
            self.end_date = self.start_date + timedelta(hours=1)

        super().save(*args, **kwargs)
    
class ChatMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    class_obj = models.ForeignKey('Classes', on_delete=models.CASCADE)  
    message = models.TextField(blank=True)
    attachment = models.FileField(upload_to='chat_attachments/', blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} at {self.timestamp}"
    
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