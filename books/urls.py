from django.urls import path, include
from .views import AddBookAPI, UpdateBookAPI, IncreaseBookQuantityAPI, BookViewSet
from .views import NextPaginatorAPI, PreviousPaginatorAPI, CacheBookSearchAPI, cac, BookViewAPI
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
#router.register(r'', BookViewSet)
#path('', include(router.urls)),
urlpatterns = [
    path('add-book/', AddBookAPI.as_view(), name='add-book'),
    path('update-book/<int:pk>/', UpdateBookAPI.as_view(), name='update-book'),
    path('increase-book-quantity/', IncreaseBookQuantityAPI.as_view(), name='increase-book-quantity'),
    path('next-paginator/', NextPaginatorAPI.as_view(), name='next-paginator'),
    path('previous-paginator/', PreviousPaginatorAPI.as_view(), name='previous-paginator'),
    path('book-vi/', cac, name='book-v'),
    path('book-view/', BookViewAPI.as_view(), name='book-view'),
    path('cache-book-search/', CacheBookSearchAPI.as_view(), name='cache-book-search'),
    
    
]
