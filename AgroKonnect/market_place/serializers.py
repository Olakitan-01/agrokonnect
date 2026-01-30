from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator
from .models import ProductListing, SavedList
from django.contrib.auth import get_user_model


User = get_user_model()


class ProductListingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductListing
        fields = (
            'id',
            'product_name',
            'quantity',
            'unit_of_measure',
            'price_per_unit',
            'product_img',
            'available_from',
            'address',
            'description',
            'is_active',
            'created_at',
        )
        read_only_fields = ("id",)

class FarmListDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name')


class MarketplaceListSerializer(serializers.ModelSerializer):
    farmer = FarmListDetailSerializer(read_only=True)
    
    class Meta:
        model = ProductListing
        fields = (
            'id',
            'farmer',
            'product_name',
            'quantity',
            'unit_of_measure',
            'price_per_unit',
            'available_from',
            'address',
            'description',
            'created_at',
            'product_img',
        )
        read_only_fields = fields

class SavedListSerializer(serializers.ModelSerializer):
    list_id = serializers.PrimaryKeyRelatedField(queryset = ProductListing.objects.all(), source = 'list', write_only=True)
    list_details = MarketplaceListSerializer(source = 'list', read_only = True)
    class Meta:
        model = SavedList
        fields = (
            'id',
            'list_id',
            'saved_at',
            'list_details',
        )
        validators = [
            UniqueTogetherValidator(
                queryset = SavedList.objects.all(), 
                fields = ['user','list'], 
                message ="List saved"
            )
        ]
