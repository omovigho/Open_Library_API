from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.UserRegistrationAPIView.as_view(), name='user-registration'),
    path('login/', views.UserLoginAPIView.as_view(), name='user-login'),
    path('logout/', views.UserLogoutAPIView.as_view(), name='user-logout'),
    path('get-username/', views.GetUsernameFromTokenAPIView.as_view(), name='get-username'),
    path('add-staff/', views.AddStaffAPIView.as_view(), name='add-staff'),
    path('remove-staff/<str:username>/', views.RemoveStaffAPIView.as_view(), name='remove-staff'),
    path('staff-count/', views.StaffCountAPIView.as_view(), name='staff-count'),
    path('list-staff-users/', views.ListStaffUsersAPIView.as_view(), name='list-staff-users'),
    path('remove-normal-user/<str:username>/', views.RemoveNormalUserAPIView.as_view(), name='remove-normal-user'),
    path('list-normal-users/', views.ListNormalUsersAPIView.as_view(), name='list-normal-users'),
]
