from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
        #fields = ['id', 'username', 'email', 'is_staff', 'is_librarian', 'is_regular_user']
        
        
class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    
    class Meta:
        model = User
        fields = ['username', 'first_name','last_name','email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            email=validated_data['email'],
            first_name = validated_data['first_name'],
            last_name = validated_data['last_name'],
        )
        return user
    
   

class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150, required=True)
    password = serializers.CharField(required=True, style={'input_type': 'password'})

    def validate(self, data):
        username = data.get('username')
        password = data.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError('Unable to log in with provided credentials')
        else:
            raise serializers.ValidationError('Must include "username" and "password".')

        # Add user ID to the data dictionary
        data['user_id'] = user.id

        return data



class StaffUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username']
        
        
class NormalUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username']
        
