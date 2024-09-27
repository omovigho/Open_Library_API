from datetime import datetime
from django.db import models
from users.models import UserProfile
from books.models import Book
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.
class Checkout(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    book = models.ForeignKey(Book, on_delete=models.SET_NULL, null=True)
    checkout_datetime = models.DateTimeField(default=datetime.now())
    return_datetime = models.DateTimeField(blank=True, null=True)
    due_datetime = models.DateTimeField(blank=True)
    fine_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    fine_paid = models.BooleanField(default=False)
    renewal_count = models.PositiveIntegerField(default=0)
    

class CheckoutSettings(models.Model):
    renewal_limit = models.PositiveIntegerField(default=2)
    fine_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    notice = models.TextField(default="Please return the book on time to avoid fines.")
    due_days = models.PositiveIntegerField(default=14)

    def __str__(self):
        return "Checkout Settings"
    
    
class FinePayment(models.Model):
    paid_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='fine_payments')
    paid_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='received_fine_payments')
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    book = models.ForeignKey(Book, on_delete=models.SET_NULL, null=True)
    datetime = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Fine Payment - {self.id}"

