from django.urls import path
from .views import CustomerSignupView, SellerSignupView, LoginView
from rest_framework_simplejwt.views import TokenRefreshView

app_name = 'Core'

urlpatterns = [
    path('auth/signup/customer/', CustomerSignupView.as_view(), name='customer_signup'),
    path('auth/signup/seller/', SellerSignupView.as_view(), name='seller_signup'),
    path('auth/login/', LoginView.as_view(), name='login'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]