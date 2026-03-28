from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.db import models

class BookReview(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    olid = models.CharField(max_length=50)  # Open Library ID
    rating = models.IntegerField()  # 1-5 arası
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.olid} ({self.rating})"

class Book(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    cover_image = models.ImageField(upload_to='books/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
    
def __str__(self):
    return f"{self.user.username} Profile"

class UserBook(models.Model):
    user = models.ForeignKey(User, on_relative=models.CASCADE)
    olid = models.CharField(max_length=100)
    title = models.CharField(max_length=255)
    thumbnail = models.URLField(max_length=500, null=True, blank=True)
    
    is_read = models.BooleanField(default=False)
    is_liked = models.BooleanField(default=False)
    is_watchlist = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'olid')

    def __str__(self):
        return f"{self.user.username} - {self.title}"


