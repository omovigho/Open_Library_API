from django.test import SimpleTestCase
from django.urls import reverse, resolve
from books.views import AddBookAPI, UpdateBookAPI, IncreaseBookQuantityAPI, BookViewAPI, CacheBookSearchAPI


class TestUrls(SimpleTestCase):
    
    def test_add_book(self):
        url = reverse('add-book')
        self.assertEqual(resolve(url).func.view_class, AddBookAPI)
        
    def test_update_book(self):
        url = reverse('update-book', args=[1])
        self.assertEqual(resolve(url).func.view_class, UpdateBookAPI)
        
    def test_increase_book_quantity(self):
        url = reverse('increase-book-quantity')
        self.assertEqual(resolve(url).func.view_class, IncreaseBookQuantityAPI)
        
    def test_book_view(self):
        url = reverse('book-view')
        self.assertEqual(resolve(url).func.view_class, BookViewAPI)
        
    def test_cache_book_search(self):
        url = reverse('cache-book-search')
        self.assertEqual(resolve(url).func.view_class, CacheBookSearchAPI)