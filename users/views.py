# users/views.py
from django.contrib.auth.models import User
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from .serializers import UserSerializer, UserRegistrationSerializer, UserLoginSerializer, StaffUserSerializer, NormalUserSerializer
from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser, BasePermission
#from django.contrib.auth import authenticate
from rest_framework_simplejwt.authentication import JWTAuthentication


class UserRegistrationAPIView(APIView):
    permission_classes = [AllowAny]  # Allow unauthenticated access
    
    def get(self, request):
        return Response({"message": "User registration page."})
    
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class UserLoginAPIView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                refresh = RefreshToken.for_user(user)
                access_token = refresh.access_token
                access_token['user_id'] = user.id
                return Response({
                    'message': 'Login successful.',
                    'access_token': str(access_token),
                    'refresh_token': str(refresh)
                })
            else:
                return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class UserLogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get('refresh_token')
        access_token = request.data.get("access")
        if not access_token:
            raise ValueError("Access token is required.")

        if not refresh_token:
            return Response({'error': 'Refresh token is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            token = RefreshToken(refresh_token)
            #token.blacklist()
            return Response({'message': 'Logout successful.'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        

class GetUsernameFromTokenAPIView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        username = request.user.username
        user_id = request.user.id
        return Response({"username": username, "user_id": user_id}, status=status.HTTP_200_OK)
    
class AddStaffAPIView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request):
        username = request.data.get('username')
        try:
            user = User.objects.get(username=username)
            if not user.is_staff:
                user.is_staff = True
                user.save()
                return Response({"message": f"User {username} is now a staff member."}, status=status.HTTP_200_OK)
            else:
                return Response({"error": f"User {username} is already a staff member."}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

    
    
class RemoveStaffAPIView(APIView):
    permission_classes = [IsAdminUser]

    def delete(self, request, username):
        try:
            user = User.objects.get(username=username)
            if user.is_staff:
                user.is_staff = False
                user.save()
                return Response({"message": f"User {username} is no longer a staff member."}, status=status.HTTP_200_OK)
            else:
                return Response({"error": f"User {username} is not a staff member."}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)


class ListStaffUsersAPIView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        staff_users = User.objects.filter(is_staff=True)
        serializer = StaffUserSerializer(staff_users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
class StaffCountAPIView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        staff_count = User.objects.filter(is_staff=True).count()
        return Response({"staff_count": staff_count}, status=status.HTTP_200_OK)


class IsAdminOrStaffUser(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_superuser or request.user.is_staff
    
    
class RemoveNormalUserAPIView(APIView):
    permission_classes = [IsAdminOrStaffUser]

    def delete(self, request, username):
        try:
            user = User.objects.get(username=username)
            if not user.is_staff and not user.is_superuser:
                user.delete()
                return Response({"message": f"User {username} has been deleted."}, status=status.HTTP_200_OK)
            else:
                return Response({"error": f"User {username} cannot be deleted as they are a staff member or superuser."}, status=status.HTTP_400_BAD_REQUEST)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
        

class ListNormalUsersAPIView(APIView):
    permission_classes = [IsAdminOrStaffUser]

    def get(self, request):
        normal_users = User.objects.filter(is_staff=False, is_superuser=False)
        serializer = NormalUserSerializer(normal_users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


'''class UserLogoutAPIView(APIView):
    def post(self, request):
        try:
            access_token = request.data.get("access")
            if not access_token:
                raise ValueError("Access token is required.")
            
            token = AccessToken(access_token)
            # You can add additional checks here if needed
            
            return Response({"message": "User logged out successfully."}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)'''



'''class UserRegistrationAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'user': UserSerializer(user).data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)'''
