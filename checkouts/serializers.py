from rest_framework import serializers
from .models import CheckoutSettings
# i disable time zone setting by doing USE_TZ = False instead of USE_TZ = True
from datetime import datetime, timedelta, timezone
from datetime import datetime, timedelta
from django.db import transaction
from books.models import BookQuantity
from django.contrib.auth.models import User
from .models import Checkout, FinePayment
from books.models import Book
from django.db.models import Q
from rest_framework.response import Response
from rest_framework.exceptions import NotFound

class CheckoutSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CheckoutSettings
        fields = ['id','renewal_limit', 'fine_amount', 'notice', 'due_days']
        read_only_fields = ['id']  # Set the id field as read-only


class CheckoutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Checkout
        fields = ['user', 'book', 'checkout_datetime', 'due_datetime']
        read_only_fields = ['user', 'checkout_datetime', 'due_datetime']
        
    def to_internal_value(self, data):
        data = data.copy()  # create a mutable copy
        book_title = data.get('book')
        book = Book.objects.filter(title__iexact=book_title).first()
        if book is None:
            raise serializers.ValidationError({"book": "The library does not have this book."})
        data['book'] = book.id
        return super().to_internal_value(data)

    def create(self, validated_data):
        book_title = self.context['request'].data.get('book')
        book = Book.objects.get(title__iexact=book_title)
        
        user_id = self.context['request'].user.id
        try:
            user = User.objects.get(id=user_id)
        except user.DoesNotExist:
            raise serializers.ValidationError({"user": "User does not exist."})
        
        # Check if the user has already borrowed a book
        borrowed_book = Checkout.objects.filter(Q(user=user) & Q(return_datetime__isnull=True)).first()
        if borrowed_book:
            raise serializers.ValidationError(f"You have borrowed a book name '{borrowed_book.book.title}' , and you need to return it. Before you can checkout any other book.")
        
        checkout_settings = CheckoutSettings.objects.first()
        checkout_datetime = datetime.now()
        due_datetime = checkout_datetime + timedelta(days=checkout_settings.due_days)
        
        with transaction.atomic():
            # Get the BookQuantity instance for the book
            book_quantity = BookQuantity.objects.get(book=book)

            # Check if the book is available
            if book_quantity.quantity > 0:
                # Decrement the book quantity by 1
                book_quantity.quantity -= 1
                book_quantity.save()

                # Create the Checkout instance
                return Checkout.objects.create(user=user, book=book, checkout_datetime=checkout_datetime, due_datetime=due_datetime)
            else:
                raise serializers.ValidationError("The book is currently unavailable and only available for reservation.")


class ReturnBookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Checkout
        fields = ['user', 'book', 'return_datetime', 'fine_amount', 'fine_paid']
        read_only_fields = ['return_datetime', 'fine_amount', 'fine_paid']
        
    def to_internal_value(self, data):
        # Make a mutable copy of the QueryDict
        data = data.copy()

        # Get the username and book name from the request data
        username = data.get('username')
        book_name = data.get('book')

        # Get the user and book objects
        user = User.objects.get(username__iexact=username)
        book = Book.objects.get(title__iexact=book_name)

        # Replace the username and book_name in the request data with their respective primary keys
        data['user'] = user.pk
        data['book'] = book.pk

        return super().to_internal_value(data)
        
    def update(self, instance, validated_data):
        # Check if the book is not already returned
        if instance.return_datetime is not None:
            raise serializers.ValidationError("This book is already returned.")

        # Check if the user has a fine
        if instance.fine_amount > 0:
            raise serializers.ValidationError(f"You need to pay the stipulated fine amount of #{instance.fine_amount}. Due to not returning the book on time.")

        # Update the return_datetime and fine_paid fields
        instance.return_datetime = datetime.now()
        instance.fine_paid = True
        instance.save()

        return instance
    
    
    
    
class FinePaymentSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = FinePayment
        fields = ['paid_by', 'paid_to', 'book', 'amount_paid', 'datetime']
        read_only_fields = ['paid_to', 'datetime']
        
    def to_internal_value(self, data):
        data = data.copy()  # create a mutable copy
        username = data.get('paid_by')
        book_name = data.get('book')
        user = User.objects.get(username__iexact=username)
        book = Book.objects.get(title__iexact=book_name)
        
        data['paid_by'] = user.pk
        data['book'] = book.pk
        return super().to_internal_value(data)

    def validate(self, data):
        
        return data

    def create(self, validated_data):
        # Get the username and book name from the validated data
        username = validated_data.pop('paid_by')
        book_name = validated_data.pop('book')

        # Get the user and book objects
        paid_by = User.objects.get(username__iexact=username)
        book = Book.objects.get(Q(title__iexact=book_name.title))
        checkout = Checkout.objects.get(Q(user=paid_by) & Q(book=book) & Q(return_datetime__isnull=True))
        
        with transaction.atomic():
            # Staff ID that is performing the fine payment
            user_id = self.context['request'].user.id
            try:
                user = User.objects.get(id=user_id)
            except user.DoesNotExist:
                raise serializers.ValidationError({"user": "User does not exist."})
            pay_datetime = datetime.now()
            pay_datetime = timezone.make_aware(pay_datetime)
            
            # Update the return_datetime and fine_paid fields in the checkout table
            checkout.return_datetime = pay_datetime
            checkout.fine_paid = True
            checkout.save()
            # Create the FinePayment object
            fine_payment = FinePayment.objects.create(paid_by=paid_by, paid_to=user, datetime= pay_datetime, book=book_name, **validated_data)

            return fine_payment
