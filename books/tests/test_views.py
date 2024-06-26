from django.contrib.auth.models import User
from django.test import TestCase
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from books.models import Author, Genre, Book
from django.urls import reverse, resolve

class AddBookAPITest(TestCase):
    def setUp(self):
        # Create a user with Staff permissions
        self.user = User.objects.create_user(username='philip', password='phi1234dja')
        self.user.is_staff = True
        self.user.save()

        # Generate a JWT token for the user
        refresh = RefreshToken.for_user(self.user)
        self.token = str(refresh.access_token)

    def test_add_book(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

        # Define book data
        book_data = {
            'title': 'The Great Book',
            'publication_date': '2024-04-15',
            'isbn': '9781234567890',
            'description': 'An epic tale',
            'author':{
                'name':'Dan',
                'biography':'Good'
            },
            'genre':{
                'name': "fictional"
            },
            'quantity': 10,
        }
        # Create a book
        response = client.post('http://127.0.0.1:8000/api/books/add-book/', data=book_data, format='json')

        # Assert successful creation
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Book.objects.count(), 1)
        self.assertEqual(Book.objects.first().title, 'The Great Book')

    def test_unauthorized_access(self):
        client = APIClient()

        # Attempt to create a book without authentication
        book_data = {
            # ... (same as above)
        }
        response = client.post('http://127.0.0.1:8000/api/books/add-book/', data=book_data, format='json')

        # Assert unauthorized access
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Book.objects.count(), 0)

    def test_invalid_token(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Bearer invalidtoken')

        # Attempt to create a book with an invalid token
        book_data = {
            # ... (same as above)
        }
        response = client.post('http://127.0.0.1:8000/api/books/add-book/', data=book_data, format='json')

        # Assert invalid token
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Book.objects.count(), 0)


class IncreaseBookQuantityAPITests(APITestCase):
    def setUp(self):
        # Create a staff user and generate a valid token
        self.staff_user = User.objects.create_user(username='staff', password='password', is_staff=True)
        self.token = RefreshToken.for_user(self.staff_user).access_token

        # Create a non-staff user and generate a token
        self.non_staff_user = User.objects.create_user(username='nonstaff', password='password', is_staff=False)
        self.non_staff_token = RefreshToken.for_user(self.non_staff_user).access_token

        # Create an author and a book
        self.author = Author.objects.create(name='Author Name')
        self.book = Book.objects.create(title='Book Title', author=self.author, quantity=5)

        # Set up the API client
        self.client = APIClient()

    def test_access_with_staff_token(self):
        # Authenticate as staff user
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')
        # Make the request
        
        book_data = {
            'title': self.book.title,
            'author': self.author.name,
            'quantity': 10
        }
        response = self.client.post('http://127.0.0.1:8000/api/books/increase-book-quantity/', data=book_data, format='json')
        # Test that the response is 200 OK
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_access_with_non_staff_token(self):
        # Authenticate as non-staff user
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.non_staff_token}')

        # Make the request
        response = self.client.post('http://127.0.0.1:8000/api/books/increase-book-quantity/', {
            'title': self.book.title,
            'author': self.author.id,
            'quantity': 10
        })

        # Test that the response is 403 Forbidden
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_missing_required_fields(self):
        # Authenticate as staff user
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

        # Make the request with missing fields
        response = self.client.post('http://127.0.0.1:8000/api/books/increase-book-quantity/', {
            'title': self.book.title,
            'author': self.author.id
            # 'quantity' is missing
        })

        # Test that the response is 400 Bad Request
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_nonexistent_author_or_book(self):
        # Authenticate as staff user
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

        # Make the request with a non-existent book title
        response = self.client.post('http://127.0.0.1:8000/api/books/increase-book-quantity/', {
            'title': 'Nonexistent Book',
            'author': self.author.id,
            'quantity': 10
        })

        # Test that the response is 400 Bad Request
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_quantity_less_than_one(self):
        # Authenticate as staff user
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

        # Make the request with quantity less than 1
        response = self.client.post('http://127.0.0.1:8000/api/books/increase-book-quantity/', {
            'title': self.book.title,
            'author': self.author.name,
            'quantity': 0
        })

        # Test that the response is 400 Bad Request
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
