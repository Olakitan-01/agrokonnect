from django.db import models
from django.conf import settings
# Create your models here.

class ProductListing(models.Model):
    farmer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='listings')
    product_name = models.CharField(max_length=100)
    quantity = models.DecimalField(max_digits=20, decimal_places=2)
    unit_of_measure = models.CharField(max_length=10,default="KG", verbose_name="unit")
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    product_img = models.ImageField(null=True, blank=True) # REMEMBER TO COME BACK TO REMOVE NULL AND BLANK
    available_from = models.DateField()
    address = models.CharField(max_length=100, verbose_name="Pickup location")
    description = models.CharField(max_length=1000, blank=False, null=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"{self.product_name} by {self.farmer.email} - {self.quantity} {self.unit_of_measure}"

class SavedList(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='saved_list')
    list = models.ForeignKey(ProductListing, on_delete=models.CASCADE, related_name='saves')
    saved_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} saved {self.listing.product_name}"