from django.shortcuts import render
from .models import *
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import SignupSerializer,FarmerOnboardingSerializer, LoginSerializer, BuyerProfileSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import generics
from drf_spectacular.utils import extend_schema

# Create your views here.

# class SignupAPIView(APIView):
#     permission_classes = [AllowAny]
#     serializer_class = SignupSerializer

    
#     """
#     POST: Register a new user. Expect JSON matching SignupSerializer fields.
#     """
#     @extend_schema(
#         request=SignupSerializer,
#         responses={201: SignupSerializer},
#     )
#     def post(self, request):
#         serializer = SignupSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         user = serializer.save()

#         # Optionally return JWT tokens on signup:
#         login_serializer = LoginSerializer(data={"email": user.email, "password": request.data.get("password")})
#         # we can create tokens without re-authenticating because we have the user object:
#         tokens = LoginSerializer().create_tokens_for_user(user)

#         user_data = {
#             "id": user.pk,
#             "email": user.email,
#             "role": user.role,
#             "username": getattr(user, "username", None),
#         }
#         return Response({"user": user_data, "tokens": tokens}, status=status.HTTP_201_CREATED)


# class LoginAPIView(APIView):
#     permission_classes = [AllowAny]
#     serializer_class = LoginSerializer
#     """
#     POST: Login with email and password. Returns JWT tokens + some user data.
#     """
#     @extend_schema(
#         request=LoginSerializer,
#         responses={200: LoginSerializer},
#     )
#     def post(self, request):
#         serializer = LoginSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         user = serializer.validated_data["user"]
#         tokens = serializer.create_tokens_for_user(user)

#         user_data = {
#             "id": user.pk,
#             "email": user.email,
#             "role": user.role,
#             "username": getattr(user, "username", None),
#         }
#         return Response({"user": user_data, "tokens": tokens}, status=status.HTTP_200_OK)


# class BuyerProfileUpdateAPIView(generics.RetrieveUpdateAPIView):
#     permission_classes = [IsAuthenticated]
#     serializer_class = BuyerProfileSerializer

#     def get_object(self):
#         try:
#             return self.request.user.buyerprofile
#         except BuyerProfile.DoesNotExist:
#             from rest_framework import NotFound
#             raise NotFound("Buyer profile  not found")
        
# class FarmerProfileUpdateAPIView(generics.RetrieveUpdateAPIView):
#     permission_classes = [IsAuthenticated]
#     serializer_class = FarmerProfileSerializer

#     def get_object(self):
#         try:
#             return self.request.user.farmerprofile
#         except FarmerProfile.DoesNotExist:
#             from rest_framework import NotFound
#             raise NotFound("Buyer profile  not found")

# ... other imports ...

import random
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from drf_spectacular.utils import extend_schema
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
from django.conf import settings
from rest_framework.throttling import AnonRateThrottle

# Import your models and serializers
from .models import BuyerProfile, FarmerProfile
from .serializers import (
    SignupSerializer, 
    LoginSerializer, 
    FarmerOnboardingSerializer, 
    BuyerProfileSerializer, 
    FarmerProfileSerializer
)

def send_welcome_email(user_email, first_name):
    subject = "Welcome to Agrokonnect! 🌾"
    message = f"""
    Hi {first_name},
    
    Welcome to Agrokonnect! We're excited to have you on board.
    
    Whether you're here to sell your farm produce or buy the freshest items 
    directly from the source, we've got you covered.
    
    Head over to your dashboard to complete your profile and start exploring.
    
    Best Regards,
    The Agrokonnect Team
    """
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [user_email]
    
    send_mail(subject, message, from_email, recipient_list)

class SignupAPIView(APIView):
    permission_classes = [AllowAny]
    
    @extend_schema(request=SignupSerializer, responses={201: SignupSerializer})
    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # --- TRIGGER THE WELCOME EMAIL HERE ---
        try:
            send_welcome_email(user.email, user.first_name)
        except Exception as e:
            # We use a try-except here so that if the email fails, 
            # the user still gets signed up successfully.
            print(f"Email failed to send: {e}")
        # Create tokens automatically after signup
        tokens = LoginSerializer().create_tokens_for_user(user)
        
        return Response({
            "message": "User created successfully",
            "user": {
                "id": user.pk,
                "email": user.email,
                "is_buyer": user.is_buyer
            },
            "tokens": tokens
        }, status=status.HTTP_201_CREATED)


class LoginRateThrottle(AnonRateThrottle):
    scope = 'burst' # This matches the 'burst' rate we defined in settings

class LoginAPIView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [LoginRateThrottle]
    
    @extend_schema(request=LoginSerializer, responses={200: LoginSerializer})
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        
        tokens = LoginSerializer().create_tokens_for_user(user)
        
        return Response({
            "user": {
                "id": user.pk,
                "email": user.email,
                "is_farmer": user.is_farmer,
                "is_buyer": user.is_buyer
            },
            "tokens": tokens
        }, status=status.HTTP_200_OK)


def send_otp_via_email(email, otp):
    subject = "Agrokonnect Password Reset Code"
    message = f"Your one-time password (OTP) for resetting your Agrokonnect password is: {otp}\nIt expires in 10 minutes."
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject, message, email_from, recipient_list)

# --- The View ---
class ForgotPasswordAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({"error": "Email is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = User.objects.get(email=email)
            # Generate 6-digit code
            otp = str(random.randint(100000, 999999))
            user.otp = otp
            user.otp_expiry = timezone.now() + timedelta(minutes=10)
            user.save()

            # Send the actual email
            send_otp_via_email(user.email, otp)

            return Response({"message": "OTP sent to your email"}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            # For security, don't reveal if the email exists or not
            return Response({"message": "If this email exists, an OTP has been sent."}, status=status.HTTP_200_OK)


class ResetPasswordAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')
        new_password = request.data.get('new_password')

        if not all([email, otp, new_password]):
            return Response({"error": "All fields are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
            
            # 1. Check if OTP matches
            # 2. Check if OTP is expired
            if user.otp != otp or user.otp_expiry < timezone.now():
                return Response({"error": "Invalid or expired OTP"}, status=status.HTTP_400_BAD_REQUEST)

            # Success! Reset password
            user.set_password(new_password)
            user.otp = None  # Clear the OTP so it can't be used again
            user.otp_expiry = None
            user.save()

            return Response({"message": "Password reset successfully"}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

class FarmerOnboardingAPIView(generics.CreateAPIView):
    serializer_class = FarmerOnboardingSerializer
    permission_classes = [IsAuthenticated]


class BuyerProfileUpdateAPIView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = BuyerProfileSerializer

    def get_object(self):
        try:
            return self.request.user.buyer_profile
        except BuyerProfile.DoesNotExist:
            from rest_framework.exceptions import NotFound
            raise NotFound("Buyer profile not found")


class FarmerProfileUpdateAPIView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FarmerProfileSerializer

    def get_object(self):
        try:
            return self.request.user.farmer_profile
        except FarmerProfile.DoesNotExist:
            from rest_framework.exceptions import NotFound
            raise NotFound("Farmer profile not found. Please onboard first.")