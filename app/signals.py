from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group
from .models import Coach

@receiver(post_save, sender=Coach)
def add_coach_to_group(sender, instance, created, **kwargs):
    print(f"Signal received for {instance.user.username}")
    if created:
        print("Coach was successfully created")
        
        try:
            coaches_group = Group.objects.get(name='Coaches')
            instance.user.groups.add(coaches_group)
        except Group.DoesNotExist:
            print("Coaches group does not exist!")
    else:
        print("Coach failed to create!")