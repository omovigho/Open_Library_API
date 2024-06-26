from rest_framework import status
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView, UpdateAPIView
from .models import Book, Author
from .serializers import BookSerializer, UpdateBookSerializer, AuthorSerializer, GenreSerializer
from .serializers import IncreaseBookQuantitySerializer, BookSearchSerializer
from rest_framework.permissions import AllowAny, BasePermission
from rest_framework import viewsets
from django.core.paginator import Paginator, EmptyPage
from rest_framework.views import APIView
from django.core.cache import cache
from django.views.decorators.cache import cache_page
from django.http import HttpResponse


class IsAdminOrStaffUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_superuser or request.user.is_staff
    
class AddBookAPI(CreateAPIView):
    permission_classes = [IsAdminOrStaffUser]  # Allow unauthenticated access
    queryset = Book.objects.all()
    serializer_class = BookSerializer

    def create(self, request, *args, **kwargs):
        title = request.data.get('title')
        author = request.data.get('author')  # Assuming 'author_name' is a string representing the author's name
        genre = request.data.get('genre')
        publication_date = request.data.get('publication_date')
        quantity = request.data.get('quantity')
        # Check if title, author, genre name, publication date, and quantity have a value
        if (title and author and genre and publication_date and quantity) is None:
           return Response({'message': 'All fields values should be entered.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if a book with the same title and author exists
        existing_books = Book.objects.filter(title=title, author__name=author['name'])

        if existing_books.exists():
            return Response({'message': 'The book already exists'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return super().create(request, *args, **kwargs)


class IncreaseBookQuantityAPI(APIView):
    permission_classes = [IsAdminOrStaffUser]  # Allow staff access
    def post(self, request, *args, **kwargs):
        title = request.data.get('title')
        author_name = request.data.get('author')
        quantity = request.data.get('quantity')
        
        if not title or not author_name or not quantity:
            return Response({"error": "All fields are required"}, status=status.HTTP_400_BAD_REQUEST)

        
        try:
            authors = Author.objects.filter(name__iexact=author_name).first()
            book = Book.objects.get(title__iexact=title)
        except (Author.DoesNotExist, Book.DoesNotExist):
            return Response({"error": "This book and the author name do not match existing book details in the library"}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = IncreaseBookQuantitySerializer(book, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class UpdateBookAPI(UpdateAPIView):
    permission_classes = [AllowAny]  # Allow unauthenticated access
    serializer_class = UpdateBookSerializer
    queryset = Book.objects.all()

    def update(self, request, *args, **kwargs):
        # Extract author data from request
        author_data = request.data.pop('author', None)
        genre_data = request.data.pop('genre', None)
        
        # If author data is present, update the author
        if author_data:
            author_serializer = AuthorSerializer(instance=self.get_object().author, data=author_data)
            if author_serializer.is_valid():
                author_serializer.save()
        
        # If genre data is present, update the genre
        '''if genre_data:
            genre_serializer = GenreSerializer(instance=self.get_object().genre, data=genre_data)
            if genre_serializer.is_valid():
                genre_serializer.save()'''

        # Pass modified request data (without author) to UpdateBookSerializer
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)


#@cache_page(60 * 15)
class BookViewSet(viewsets.ModelViewSet):
    permission_classes = [AllowAny]  # Allow unauthenticated access
    queryset = Book.objects.all()
    serializer_class = BookSearchSerializer

    def get_queryset(self):
        
        queryset = Book.objects.all()
        # Search
        search_query = self.request.query_params.get('search', None)
        if search_query:
            queryset = queryset.filter(title__icontains=search_query) | \
                       queryset.filter(author__name__icontains=search_query) | \
                       queryset.filter(genre__name__icontains=search_query)
        # Filtering
        author_filter = self.request.query_params.get('author', None)
        if author_filter:
            queryset = queryset.filter(author__name=author_filter)
        # Ordering
        order_by = self.request.query_params.get('order_by', None)
        if order_by:
            queryset = queryset.order_by(order_by)
        '''perpage = self.request.query_params.get('perpage', default=3)
        page = self.request.query_params.get('page', default=1)
        paginator = Paginator(queryset, perpage)
        try:
            queryset = paginator.page(number=page)
        except EmptyPage:
            queryset = paginator.page(1)'''
        return queryset
        
    
class NextPaginatorAPI(APIView):
    permission_classes = [AllowAny]  # Allow unauthenticated access
    def get(self, request, *args, **kwargs):
        page = request.query_params.get('page', default=1)
        perpage = request.query_params.get('perpage', default=3)
        queryset = Book.objects.all()
        paginator = Paginator(queryset, perpage)
        try:
            queryset = paginator.page(number=int(page)+1)
        except EmptyPage:
            queryset = paginator.page(paginator.num_pages)
        serializer = BookSearchSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class PreviousPaginatorAPI(APIView):
    permission_classes = [AllowAny]  # Allow unauthenticated access
    def get(self, request, *args, **kwargs):
        page = request.query_params.get('page', default=1)
        perpage = request.query_params.get('perpage', default=3)
        queryset = Book.objects.all()
        paginator = Paginator(queryset, perpage)
        try:
            queryset = paginator.page(number=max(1, int(page)-1))
        except EmptyPage:
            queryset = paginator.page(1)
        serializer = BookSearchSerializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
class BookSearchAPI(APIView):
    permission_classes = [AllowAny]  # Allow unauthenticated access
    
    def get(self, request):
        # Get query parameters from the request
        search_query = request.query_params.get('q', '')  # Search query
        author_name = request.query_params.get('author', '')  # Author name filter
        genre_name = request.query_params.get('genre', '')  # Genre name filter
        order_by = request.query_params.get('order_by', 'publication_date')  # Order by field

         # Check if the data is already cached
        cache_key = f"book_search_{search_query}_{author_name}_{genre_name}_{order_by}"
        cached_books = cache.get(cache_key)
        if cached_books:
            return Response(cached_books, status=status.HTTP_200_OK)
        
        # Filter books based on search query, author name, and genre name
        books = Book.objects.filter(
            title__icontains=search_query,
            author__name__icontains=author_name,
            genre__name__icontains=genre_name
        )

        # Order the books based on the specified field
        books = books.order_by(order_by)
        
        # Pagination 
        perpage = self.request.query_params.get('perpage', default=5)
        page = self.request.query_params.get('page', default=1)
        paginator = Paginator(books, perpage)
        try:
            books = paginator.page(number=page)
        except EmptyPage:
            books = paginator.page(1)
            
        serializer = BookSerializer(books, many=True)
        # Cache the data for 1 hour (adjust as needed)
        cache.set(cache_key, serializer.data, 60) 
        return Response(serializer.data, status=status.HTTP_200_OK)

    
class BookViewAPI(APIView):
    permission_classes = [AllowAny]  # Allow unauthenticated access
    def get(self, request):
        cached_books = cache.get('all_books')
        if cached_books:
            return Response(cached_books, status=status.HTTP_200_OK)
        # Retrieve all books from the database
        books = Book.objects.all()
        serializer = BookSearchSerializer(books, many=True)
        cache.set('all_books', serializer.data, 60)
        return Response(serializer.data, status=status.HTTP_200_OK)

@cache_page(60)  # Cache for 1 minutes    
def cac(request):
    print("gooop")
    books = Book.objects.all()
    serializer = BookSearchSerializer(books, many=True)
    print("poolop iuy")
    print(len(serializer.data))
    return HttpResponse(f'<html><body><p>{serializer.data}</p></body></html>', status=status.HTTP_200_OK)
    #return Response(serializer.data, status=status.HTTP_200_OK)
    
    

class CacheBookSearchAPI(APIView):
    permission_classes = [AllowAny]  # Allow unauthenticated access
    def get(self, request):
        # Get query parameters from the request
        search_query = request.query_params.get('q', '')
        author_name = request.query_params.get('author', '')
        genre_name = request.query_params.get('genre', '')
        order_by = request.query_params.get('order_by', 'publication_date')
        perpage = int(request.query_params.get('perpage', 5))
        page = int(request.query_params.get('page', 1))

        # Construct a cache key based on the query parameters
        cache_key = f"book_search_{search_query}_{author_name}_{genre_name}_{order_by}_{perpage}_{page}"

        # Check if the data is already cached
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data, status=status.HTTP_200_OK)

        # If not cached, retrieve books from the database
        books = Book.objects.filter(
            title__icontains=search_query,
            author__name__icontains=author_name,
            genre__name__icontains=genre_name
        )

        # Order the books based on the specified field
        books = books.order_by(order_by)

        # Create a paginator
        paginator = Paginator(books, perpage)

        # Validate page number
        if page < 1:
            page = 1
        elif page > paginator.num_pages:
            page = paginator.num_pages

        # Get the requested page
        try:
            books_page = paginator.page(number=page)
        except EmptyPage:
            books_page = paginator.page(1)

        serializer = BookSerializer(books_page, many=True)

        # Construct pagination metadata
        pagination_metadata = {
            "page": page,
            "perpage": perpage,
            "total_pages": paginator.num_pages,
            "total_items": paginator.count,
        }

        # Combine data and pagination metadata
        response_data = {
            "data": serializer.data,
            "pagination": pagination_metadata,
        }

        # Cache the data for 1 hour (adjust as needed)
        cache.set(cache_key, response_data, 3600)

        return Response(response_data, status=status.HTTP_200_OK)
