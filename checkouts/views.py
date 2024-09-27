from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from checkouts.models import CheckoutSettings
from .serializers import CheckoutSettingsSerializer, FinePaymentSerializer
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated, BasePermission
from rest_framework.generics import UpdateAPIView, CreateAPIView
from .serializers import CheckoutSerializer
from .models import Checkout
from django.contrib.auth.models import User
from django.db.models import Q
from .serializers import ReturnBookSerializer
from books.models import Book
from rest_framework.exceptions import NotFound

# Create your views here.

class IsAdminOrStaffUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_superuser or request.user.is_staff
    
    
class AddCheckoutSettingsAPI(APIView):
    permission_classes = [IsAuthenticated]  # Allow authenticated access
    def post(self, request, format=None):
        existing_table = CheckoutSettings.objects.filter(id=1)
        if existing_table.exists():
            return Response({'message': 'Checkout settings already exist. Update values of table instead.'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = CheckoutSettingsSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    

class UpdateCheckoutSettingsAPIView(UpdateAPIView):
    permission_classes = [IsAdminUser]  # Allow only admin users to access
    queryset = CheckoutSettings.objects.all()
    serializer_class = CheckoutSettingsSerializer
    
    
class CheckoutNoticeAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        checkout_settings = CheckoutSettings.objects.first()  # Assuming there's only one checkout settings instance
        if checkout_settings:
            notice = checkout_settings.notice
            return Response({"notice": notice})
        else:
            return Response({"message": "Checkout settings not found."}, status=404)


class CheckoutAPIView(CreateAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Checkout.objects.all()
    serializer_class = CheckoutSerializer
    

class ReturnBookAPIView(APIView):
    permission_classes = [IsAdminOrStaffUser]

    def post(self, request, *args, **kwargs):
        # Get the username and book name from the request data
        username = request.data.get('username')
        book_name = request.data.get('book')

        # Get the user and book objects
        try:
            user = User.objects.get(username__iexact=username)
        except User.DoesNotExist:
            raise NotFound(detail="User does not exist.", code=404)
        try:
            book = Book.objects.get(title__iexact=book_name)
        except Book.DoesNotExist:
            raise NotFound(detail="The library does not have this book.", code=404)
        # Get the checkout object
        try:
            checkout = Checkout.objects.get(Q(user=user) & Q(book=book) & Q(return_datetime__isnull=True))
        except Checkout.DoesNotExist:
            raise NotFound(detail=f"{user} did not borrow this book.", code=404)

        # Create a serializer instance
        serializer = ReturnBookSerializer(checkout, data=request.data, partial=True)

        # Validate and save the serializer
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        
class FinePaymentAPIView(APIView):
    permission_classes = [IsAdminOrStaffUser]

    def post(self, request, *args, **kwargs):
        username = request.data.get('paid_by')
        book_name = request.data.get('book')
        try:
            user = User.objects.get(username__iexact=username)
        except User.DoesNotExist:
            raise NotFound(detail="User does not exist.", code=404)
        try:
            book = Book.objects.get(title__iexact=book_name)
        except Book.DoesNotExist:
            raise NotFound(detail="The library does not have this book.", code=404)
        # Get the checkout object
        try:
            checkout = Checkout.objects.get(Q(user=user) & Q(book=book) & Q(return_datetime__isnull=True))
        except Checkout.DoesNotExist:
            raise NotFound(detail=f"{user} did not borrow this book.", code=404)
        # Check is amount paid is same with the fine payment of the user
        if int(request.data.get('amount_paid')) != int(checkout.fine_amount):
            raise NotFound(detail=f"The amount paid by the user is not the same as the fine overdue payment, which is #{checkout.fine_amount}", code=404)
        # Create a serializer instance
        #serializer = FinePaymentSerializer(data=request.data)
        serializer = FinePaymentSerializer(data=request.data, context={'request': request})


        # Validate and save the serializer
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    