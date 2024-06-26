import datetime
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.
class Author(models.Model):
    name = models.CharField(max_length=255)
    biography = models.TextField(blank=True)

class Genre(models.Model):
    name = models.CharField(max_length=255)

class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.ForeignKey(Author, on_delete=models.SET_NULL, null=True)
    genre = models.ForeignKey(Genre, on_delete=models.SET_NULL, null=True)
    isbn = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    #publication_date = models.DateField()
    publication_date = models.DateField(default=datetime.date.today)  # Example of setting a default value
    availability = models.BooleanField(default=True)
    quantity = models.IntegerField(default=1)  # Example of setting a default value
    
class BookQuantity(models.Model):
    book = models.ForeignKey(Book, on_delete=models.SET_NULL, null=True)
    author = models.ForeignKey(Author, on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField()

# Signal receiver function to create BookQuantity entry after saving a Book
@receiver(post_save, sender=Book)
def create_book_quantity(sender, instance, created, **kwargs):
    if created:
        # Get the quantity value from the instance (assuming it's a field on the Book model)
        quantity = instance.quantity  # Adjust this according to your actual field name
        
        # Create a new BookQuantity entry with the correct quantity
        BookQuantity.objects.create(book=instance, author=instance.author, quantity=quantity)

