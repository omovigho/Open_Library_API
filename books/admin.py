# books/admin.py
from django.contrib import admin
from .models import Book, Author, Genre

# Register the Book, Author, and Genre models in the Django admin
admin.site.register(Book)
admin.site.register(Author)
admin.site.register(Genre)


# Create a custom admin class for the Book model
"""class BookAdmin(admin.ModelAdmin):
    # Customize the list display of books
    list_display = ('title', 'author', 'publication_date', 'availability')

    # Add filters for easy searching and filtering
    list_filter = ('author', 'publication_date', 'availability')

    # Add search fields for searching books by title
    search_fields = ('title',)

    # Customize the fields displayed in the detail view
    fields = ('title', 'author', 'genre', 'ISBN', 'description', 'publication_date', 'availability', 'quantity')

# Register the BookAdmin class with the Django admin
admin.site.register(Book, BookAdmin)"""

