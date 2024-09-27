from django.db import models

# Create your models here.
class UserProfile(models.Model):
    username = models.CharField(max_length=255, unique=True)
    first_name = models.CharField(max_length=255, blank=False)
    last_name = models.CharField(max_length=255, blank=False)
    email = models.EmailField(blank=False, unique=True)
    password = models.CharField(max_length=255)
    is_staff = models.BooleanField(default=False)
    is_librarian = models.BooleanField(default=False)