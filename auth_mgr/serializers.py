from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .models import BuyerProfile, FarmerProfile

User = get_user_model()

# --- 1. BASIC PROFILE SERIALIZERS (For Retrieve/Update) ---

class BuyerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = BuyerProfile
        fields = ('id', 'category')


class FarmerProfileSerializer(serializers.ModelSerializer):
    """Used for viewing or updating an EXISTING farmer profile."""
    class Meta:
        model = FarmerProfile
        fields = (
            'id', 'farm_name', 'farm_address', 'nin', 
            'bank_name', 'account_number', 'account_name', 'is_verified'
        )
        read_only_fields = ('is_verified',)


# --- 2. ONBOARDING SERIALIZER ---

class FarmerOnboardingSerializer(serializers.ModelSerializer):
    """Used specifically for the 'Become a Farmer' process."""
    class Meta:
        model = FarmerProfile
        fields = (
            'farm_name', 'farm_address', 'nin', 
            'bank_name', 'account_number', 'account_name'
        )

    def validate_nin(self, value):
        if not value.isdigit() or len(value) != 11:
            raise serializers.ValidationError("NIN must be exactly 11 digits.")
        return value

    def validate(self, data):
        user = self.context['request'].user
        if FarmerProfile.objects.filter(user=user).exists():
            raise serializers.ValidationError("You are already registered as a farmer.")
        return data

    def create(self, validated_data):
        user = self.context['request'].user
        profile = FarmerProfile.objects.create(user=user, **validated_data)
        
        # Promote the user flags
        user.is_farmer = True
        user.save(update_fields=['is_farmer'])
        return profile


# --- 3. AUTHENTICATION SERIALIZERS ---

class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = (
            "first_name", "last_name", "email", 
            "phone_number", "address", "password", "gender"
        )

    def validate_email(self, value):
        value = value.lower()
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email already exists.")
        return value

    def create(self, validated_data):
        # Create core user (is_buyer=True is default in model)
        user = User.objects.create_user(**validated_data)
        
        # Create default empty BuyerProfile
        BuyerProfile.objects.create(user=user)
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, trim_whitespace=False)

    def validate(self, data):
        email = data.get("email").lower()
        password = data.get("password")

        user = authenticate(username=email, password=password)

        if not user:
            raise serializers.ValidationError("Invalid credentials.")

        if not user.is_active:
            raise serializers.ValidationError("User account is disabled.")

        data["user"] = user
        return data

    def create_tokens_for_user(self, user):
        refresh = RefreshToken.for_user(user)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token)
        }