from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.db import models

class Book(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    cover_image = models.ImageField(upload_to='books/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
def __str__(self):
    return f"{self.user.username} Profile"


