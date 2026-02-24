# from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
# from django.db import models
# from django.utils import timezone
# from django.utils.text import gettext_lazy as _
 
 
# class CustomerUserManager(BaseUserManager):
#     def create_user(self, email, login_type, password=None, **extra_fields):
#         if not email:
#             raise ValueError("The Email field must be set")
#         email = self.normalize_email(email)
#         user = self.model(email=email, login_type=login_type, **extra_fields)
#         user.set_password(password)
#         user.save(using=self._db)
#         return user
 
#     def create_superuser(self, email, login_type, password=None, **extra_fields):
#         extra_fields.setdefault("is_staff", True)
#         extra_fields.setdefault("is_superuser", True)
#         return self.create_user(email, login_type, password, **extra_fields)
 
 
# class User(AbstractBaseUser, PermissionsMixin):
#     class LoginTypes(models.TextChoices):
#         GOOGLE = 'GO', _('Google')
#         EMAIL = 'EM', _('Email')

#     class Roles(models.TextChoices):
#         BUYER = "BUYER", "Buyer"
#         FARMER = "FARMER", "Farmer"

#     class GenderChoices(models.TextChoices):
#         MALE = "M", "Male"
#         FEMALE = "F", "Female"
#         OTHER = "O", "Other"
 
#     username = models.CharField(_("Username"), max_length=70, unique=False, blank=True, null=True)
#     email = models.EmailField(_('Email'), unique=True)
#     role = models.CharField(_('Roles'), choices=Roles.choices, max_length=10)
#     first_name = models.CharField(_('First Name'), max_length=30, blank=True)
#     last_name = models.CharField(_('Last Name'), max_length=30, blank=True)
#     gender = models.CharField(max_length=10, choices=GenderChoices.choices)
#     login_type = models.CharField(_('Login Type'), choices=LoginTypes.choices,max_length=10, default=LoginTypes.EMAIL)
#     is_partner = models.BooleanField(_('Is Partner'), default=False)
#     is_active = models.BooleanField(_('Is Active'), default=True)
#     is_staff = models.BooleanField(_('Is Staff'), default=False)
#     date_joined = models.DateTimeField(default=timezone.now)
 
#     objects = CustomerUserManager()
 
#     USERNAME_FIELD = "email"
#     REQUIRED_FIELDS = ["role"]
 
#     # @property
#     # def user_station_type(self):
#     #     station_type = self.station.station_type
#     #     if int(station_type) is int:
#     #         return station_type
#     #     else:
#     #         return 0
 
#     def __str__(self):
#         return self.email

# class BuyerProfile(models.Model):
#     class Category(models.TextChoices):
#         WHOLESALES = "W", "Wholesales"
#         RETAIL = "R", "Retail"
#         CONSUMER = "C", "Consumer"

#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     category = models.CharField(choices=Category.choices,max_length=15, default=Category.CONSUMER)
#     phone_no = models.CharField(max_length=20)
#     address = models.CharField(max_length=50, null=False)
#     # profile_image = models.ImageField()

#     def __str__(self):
#         return f"Buyer Profile — {self.user.email}"

# class FarmerProfile(models.Model):
#     user = models.OneToOneField(User, on_delete=models.CASCADE)
#     phone_no = models.CharField(max_length=20)
#     farm_name = models.CharField(max_length=50)
#     farm_address = models.CharField(max_length=100)

#     def __str__(self):
#         return f"Farmer Profile — {self.user.email}"


from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _ 
from django.conf import settings

class CustomerUserManager(BaseUserManager):
    def create_user(self, email, phone_number, address, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        if not phone_number:
            raise ValueError("The Phone Number must be set")
        
        email = self.normalize_email(email)
        # Default every new user to be a Buyer
        extra_fields.setdefault("is_buyer", True)
        
        user = self.model(
            email=email, 
            phone_number=phone_number, 
            address=address, 
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, phone_number, address, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(email, phone_number, address, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    class LoginTypes(models.TextChoices):
        GOOGLE = 'GO', _('Google')
        EMAIL = 'EM', _('Email')

    class GenderChoices(models.TextChoices):
        MALE = "M", "Male"
        FEMALE = "F", "Female"
        OTHER = "O", "Other"

    email = models.EmailField(_('Email'), unique=True)
    first_name = models.CharField(_('First Name'), max_length=30)
    last_name = models.CharField(_('Last Name'), max_length=30)
    phone_number = models.CharField(_('Phone Number'), max_length=20, unique=True)
    address = models.CharField(_('Home/Business Address'), max_length=255)
    is_farmer = models.BooleanField(_('Is Farmer'), default=False)
    is_buyer = models.BooleanField(_('Is Buyer'), default=True)
    gender = models.CharField(max_length=10, choices=GenderChoices.choices, null=True, blank=True)
    login_type = models.CharField(_('Login Type'), choices=LoginTypes.choices, max_length=10, default=LoginTypes.EMAIL)
    is_active = models.BooleanField(_('Is Active'), default=True)
    is_staff = models.BooleanField(_('Is Staff'), default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    otp = models.CharField(max_length=6, blank=True, null=True)
    otp_expiry = models.DateTimeField(blank=True, null=True)
    
    objects = CustomerUserManager()

    USERNAME_FIELD = "email"
    # Fields required when creating via createsuperuser command
    REQUIRED_FIELDS = ["first_name", "last_name", "phone_number", "address"]

    def __str__(self):
        return self.email

class BuyerProfile(models.Model):
    class Category(models.TextChoices):
        WHOLESALE = "W", "Wholesale"
        RETAIL = "R", "Retail"
        CONSUMER = "C", "Consumer"

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="buyer_profile")
    category = models.CharField(choices=Category.choices, max_length=15, default=Category.CONSUMER)
    # phone and address are now on User, so we don't need them here unless they are "Shipping specific"

    def __str__(self):
        return f"Buyer Profile — {self.user.email}"

class FarmerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="farmer_profile")
    farm_name = models.CharField(max_length=100)
    farm_address = models.CharField(max_length=255) # Can be different from User.address
    is_verified = models.BooleanField(default=False)
    nin = models.CharField(max_length=11, unique=True, verbose_name="National Identity Number")
    is_verified = models.BooleanField(default=False)
    bank_name = models.CharField(max_length=100, null=False, blank=False)
    account_number = models.CharField(max_length=10, unique=True, null=False, blank=False)
    account_name = models.CharField(max_length=150, null=False, blank=False)

    def __str__(self):
        return f"Farmer Profile — {self.user.email} ({self.farm_name})"