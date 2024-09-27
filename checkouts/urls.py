from django.urls import path
from .views import AddCheckoutSettingsAPI, UpdateCheckoutSettingsAPIView, CheckoutNoticeAPIView, CheckoutAPIView
from .views import ReturnBookAPIView, FinePaymentAPIView


urlpatterns = [
    path('add-checkout-settings/', AddCheckoutSettingsAPI.as_view(), name='add-checkout-settings'),
    path('update-checkout-settings/<int:pk>/', UpdateCheckoutSettingsAPIView.as_view(), name='update-checkout-settings'),
    path('checkout-notice/', CheckoutNoticeAPIView.as_view(), name='checkout-notice'),
    path('checkout/', CheckoutAPIView.as_view(), name='checkout'),
    path('return-book/', ReturnBookAPIView.as_view(), name='return-book'),
    path('fine-payment/', FinePaymentAPIView.as_view(), name='fine-payment'),
]