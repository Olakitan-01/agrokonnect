# from rest_framework import serializers
# from django.contrib.auth import get_user_model, authenticate
# from rest_framework_simplejwt.tokens import RefreshToken

# from .models import BuyerProfile, FarmerProfile

# User = get_user_model()

# class BuyerProfileSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = BuyerProfile
#         fields = ('category', 'phone_no', 'address')
#         extra_kwargs = {
#             "category":{"required": False},
#             "phone_no":{"required": False},
#             "address":{"required": False}

#         }
# class FarmerProfileSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = FarmerProfile
#         fields = ('farm_name', 'phone_no', 'farm_address')
#         extra_kwargs = {
#             "farm_name":{"required": False},
#             "phone_no":{"required": False},
#             "farm_address":{"required": False}

#         }


# class SignupSerializer(serializers.ModelSerializer):
#     password = serializers.CharField(write_only=True, min_length=8)
#     buyer_profile = BuyerProfileSerializer(required=False)
#     farmer_profile = FarmerProfileSerializer(required=False)

#     class Meta:
#         model = User
#         fields = (
#             "first_name",
#             "last_name",
#             "username",
#             "email",
#             "password",
#             "gender",
#             "role",
#             "login_type",
#             "buyer_profile",
#             "farmer_profile",
#         )
#     extra_kwargs = {
#         "first_name":{"required":True},
#         "last_name":{"required":True},
#         "login_type":{"required":True},
#         "gender":{"required":True}
#     }

#     def validate_email(self, value):
#         value = value.lower()
#         if User.objects.filter(email=value).exists():
#             raise serializers.ValidationError("This email already exist.")
#         return value

#     def validate(self, data):
#         role = data.get("role")
#         if role == User.Roles.BUYER and not data.get('buyer_profile'):
#             raise serializers.ValidationError({"buyer_profile":"Buyer profile data required for BUYER role"})
#         if role == User.Roles.FARMER and not data.get('farmer_profile'):
#             raise serializers.ValidationError({"farmer_profile":"Farmer profile data required for FARMER role"})
#         return data

#     def create(self, validated_data):
#         buyer_data = validated_data.pop("buyer_profile", None)
#         farmer_data = validated_data.pop("farmer_profile", None)
#         login_type = validated_data.pop("login_type", getattr(User, "LoginTypes").EMAIL)
#         password = validated_data.pop("password")
#         user = User.objects.create_user(
#             email=validated_data.get("email"),
#             login_type=login_type,
#             password=password,
#             username=validated_data.get("username"),
#             first_name=validated_data.get("first_name"),
#             last_name=validated_data.get("last_name"),
#             role=validated_data.get("role"),
#             gender=validated_data.get("gender"),

#         )

#         if user.role == User.Roles.BUYER and buyer_data:
#             BuyerProfile.objects.create(user=user, **buyer_data)
#         if user.role == User.Roles.FARMER and farmer_data:
#             FarmerProfile.objects.create(user=user, **farmer_data)
#         return user

#     def to_representation(self, instance):
#         # Customize returned data after successful signup
#         rep = super().to_representation(instance)
#         rep.pop("password", None)
#         rep["id"] = instance.pk
#         return rep


# class LoginSerializer(serializers.Serializer):
#     email = serializers.EmailField()
#     password = serializers.CharField(write_only=True, trim_whitespace=False)

#     def validate(self, data):
#         email = data.get("email")
#         password = data.get("password")

#         if not email or not password:
#             raise serializers.ValidationError("Email and password are required.")

#         email = email.lower()

#         # authenticate uses USERNAME_FIELD = "email"
#         user = authenticate(username=email, password=password)

#         if not user:
#             raise serializers.ValidationError("Invalid credentials, please try again.")

#         if not user.is_active:
#             raise serializers.ValidationError("User account is disabled.")

#         data["user"] = user
#         return data

#     def create_tokens_for_user(self, user):
#         refresh = RefreshToken.for_user(user)
#         return {
#             "refresh": str(refresh),
#             "access": str(refresh.access_token)
#         }

#     # def create_tokens_for_user(self, user):
#     #     refresh = RefreshToken.for_user(user)
#     #     return {
#     #         "refresh": str(refresh),
#     #         "access": str(refresh.access_token)
#     #     }


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


# --- 2. ONBOARDING SERIALIZER (For Jiji-style promotion) ---

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