from rest_framework import serializers
from .models import Author, BookQuantity, Genre, Book
from django.db import transaction


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = '__all__'
    ###   
    def update(self, instance, validated_data):
        # Update author's name and biography if present
        instance.name = validated_data.get('name', instance.name)
        instance.biography = validated_data.get('biography', instance.biography)
        instance.save()
        return instance

class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = '__all__'
    # For updating genre
    '''def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.save()
        return instance'''

class BookQuantitySerializer(serializers.ModelSerializer):
    class Meta:
        model = BookQuantity
        fields = '__all__'

class BookSerializer(serializers.ModelSerializer):
    author = AuthorSerializer()
    genre = GenreSerializer()

    class Meta:
        model = Book
        fields = ['title', 'publication_date', 'isbn', 'description', 'author', 'genre', 'quantity']
        
        extra_kwargs = {
            'title': {'required': True},
            'author': {
              'name':{'required': True}
            },
            'genre': {
              'name':{'required': True}
            },
            'publication_date': {'required': True},
            'quantity': {'required': True}
        }

    def create(self, validated_data):
        author_data = validated_data.pop('author')
        genre_data = validated_data.pop('genre')
        
        author_instance, _ = Author.objects.get_or_create(**author_data)
        genre_instance, _ = Genre.objects.get_or_create(**genre_data)
        
        book_instance = Book.objects.create(genre=genre_instance, author=author_instance, **validated_data)
        return book_instance


class IncreaseBookQuantitySerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(queryset=Author.objects.all())
    
    class Meta:
        model = Book
        fields = ['title','author','quantity']
        
        extra_kwargs = {
          'title': {'required':True},
          'author': {'required':True},
          'quantity': {'required':True}
        }
        
    def to_internal_value(self, data):
        data = data.copy()  # create a mutable copy
        # Convert the author name to an Author instance
        author_name = data.get('author')
        author = Author.objects.filter(name=author_name).first()
        if author is None:
            raise serializers.ValidationError('Author does not exist')
        data['author'] = author.id

        return super().to_internal_value(data)
        
    @transaction.atomic
    def update(self, instance, validated_data):
        # Increment the book quantity in the Book table
        if validated_data.get('quantity') < 1:
            raise serializers.ValidationError('Quantity must be a positive integer')
        quantity_increment = validated_data.get('quantity')
        if quantity_increment:
            instance.quantity += quantity_increment
            instance.save()

            # Also increment the book quantity in the BookQuantity table
            book_quantity_instance = BookQuantity.objects.get(book=instance)
            book_quantity_instance.quantity += quantity_increment
            book_quantity_instance.save()
        return instance
      
      
class UpdateBookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['title', 'publication_date', 'isbn', 'description', 'quantity']

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)
      
class BookSearchSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.name', read_only=True)
    genre_name = serializers.CharField(source='genre.name', read_only=True)
    biography = serializers.CharField(source='author.biography', read_only=True)

    class Meta:
        model = Book
        fields = ['title', 'author_name', 'genre_name', 'description', 'biography','publication_date', 'isbn']
        
        
from rest_framework import serializers
from .models import Book, BookQuantity

class IncreaseBookQuantitySerializer2(serializers.ModelSerializer):
    #author_name = serializers.CharField(source='author.name')

    class Meta:
        model = Book
        fields = ['title', 'author', 'quantity']

        extra_kwargs = {
            'title': {'required': True},
            'author_name': {'required': True},
            'quantity': {'required': True}
        }

    def validate(self, data):
        # Check if the book title and author name match existing book details
        title = data.get('title')
        author_name = data.get('author')

        try:
            book = Book.objects.get(title=title, author__name=author_name)
            book_quantity = BookQuantity.objects.get(book=book)
        except (Book.DoesNotExist, BookQuantity.DoesNotExist):
            raise serializers.ValidationError("This book and the author name do not match existing book details in the library")

        return data

    @transaction.atomic
    def create(self, instance, validated_data):
        # Increment the book quantity in the Book table
        quantity_increment = validated_data.get('quantity')
        if quantity_increment:
            instance.quantity += quantity_increment
            instance.save()

            # Also increment the book quantity in the BookQuantity table
            book_quantity_instance = BookQuantity.objects.get(book=instance)
            book_quantity_instance.quantity += quantity_increment
            book_quantity_instance.save()

        return instance

        
# Sample JSON data for testing the API


"""{
  "title": "Harry Potter and the Philosopher's Stone",
  "publication_date": "1997-09-19",
  "isbn": "9780747532743",
  "description": "Harry Potter has never even heard of Hogwarts when the letters start dropping on the doormat at number four, Privet Drive. Addressed in green ink on yellowish parchment with a purple seal, they are swiftly confiscated by his grisly aunt and uncle. Then, on Harry's eleventh birthday, a great beetle-eyed giant of a man called Rubeus Hagrid bursts in with some astonishing news: Harry Potter is a wizard, and he has a place at Hogwarts School of Witchcraft and Wizardry.",
  "author": {
    "name": "J.K. Rowling",
    "biography": "J.K. Rowling is a America movie writer, and a public speaker. She was born 1965. With the Harry Potter series, J.K. Rowling became one of the world's most successful authors."
  },
	"quantity":10, 
  "genre": {
    "name": "Fantasy"
  }
}


{
  "title": "Whispers of the Ancients: A Lorian Tal",
  "publication_date": "2026-09-21",
  "isbn": "9781481466815",
  "description": "In the enchanted realm of Lorian, ancient whispers echo through the forest, speaking of a long-forgotten magic.",
  "author": {
    "name": "Ariana Silverwing",
    "biography": "Ariana Silverwing is an acclaimed author in the realm of fantasy literature."
  },
  "quantity": 3,
  "genre": {
    "name": "High Fantasy"
  }
}"""
