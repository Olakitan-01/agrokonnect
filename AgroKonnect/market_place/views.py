from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from .serializers import ProductListingSerializer, MarketplaceListSerializer, SavedListSerializer
from .models import *
from .permissions import isListOwner



# Create your views here.
class IsFarmer(IsAuthenticated):
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        
        User = request.user.__class__
        return request.user.role == User.Roles.FARMER


class ProductListingCreateAPIView(generics.CreateAPIView):
    queryset = ProductListing.objects.all()
    serializer_class = ProductListingSerializer
    permission_classes = [IsFarmer]

    def create(self, serializer):
        serializer.save(farmer=self.request.user)

class MarketplaceListAPIView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MarketplaceListSerializer
    # filteres_set = ProductListingFilter

    def get_queryset(self):
        return ProductListing.objects.filter(is_active=True).order_by('-created_at')

class MarketplaceRetrieveAPIView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MarketplaceListSerializer
    queryset = ProductListing.objects.filter(is_active=True)
    lookup_field = 'pk'


class SavedListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = SavedListSerializer

    def get_queryset(self):
        return SavedList.objects.filter(user=self.request.user).order_by('-saved_at')
    
    def create(self, serializer):
        serializer.save(user=self.request.user)

class SavedListDestroyAPIView(generics.DestroyAPIView):
        serializer_class = SavedListSerializer
        queryset = SavedList.objects.all()
        permission_classes = [IsAuthenticated]

        def get_object(self):
        # Get the listing_pk from the URL kwargs (e.g., /favorites/5/)
            list_pk = self.kwargs.get('list_pk')
        
            # Retrieve the SavedListing instance linked to the user and the listing ID
            try:
                return SavedList.objects.get(
                    user=self.request.user, 
                    list__pk=list_pk
                )
            except SavedList.DoesNotExist:
                from rest_framework.exceptions import NotFound
                raise NotFound("Saved lists not found for this user.")
            

class FarmerListManagementAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ProductListingSerializer
    permission_classes = [IsAuthenticated, isListOwner]
    lookup_field = 'pk'