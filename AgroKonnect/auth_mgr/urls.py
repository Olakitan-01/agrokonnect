from django.urls import path
from .views import LoginAPIView, SignupAPIView, BuyerProfileUpdateAPIView, FarmerProfileUpdateAPIView, FarmerOnboardingAPIView, ForgotPasswordAPIView, ResetPasswordAPIView


urlpatterns = [
    path("auth/signup", SignupAPIView.as_view(), name='signup'),
    path("auth/login", LoginAPIView.as_view(), name='login'),
    path("auth/onboard-farmer/", FarmerOnboardingAPIView.as_view(), name='onboard-farmer'),
    path('auth/forgot-password/', ForgotPasswordAPIView.as_view(), name='forgot-password'),
    path('auth/reset-password/', ResetPasswordAPIView.as_view(), name='reset-password'),
    path("profile/buyer/", BuyerProfileUpdateAPIView.as_view(), name='buyer-profile-update'),
    path("profile/farmer/", FarmerProfileUpdateAPIView.as_view(), name='farmer-profile-update')
]