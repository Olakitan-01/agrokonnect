from django.urls import path
from .views import ProductListingCreateAPIView, MarketplaceListAPIView,SavedListCreateAPIView, SavedListDestroyAPIView, FarmerListManagementAPIView

urlpatterns = [
    # API endpoint for creating a listing
    path('listings/create/', ProductListingCreateAPIView.as_view(), name='listing-create'),
    path('listings/manage/<int:pk>/', FarmerListManagementAPIView.as_view(), name='listing-manage'),
    path('listings/browse/', MarketplaceListAPIView.as_view(), name='market-place'),
    path('favorites/', SavedListCreateAPIView.as_view(), name='favorites-list-create'),
    path('favorites/<int:list_pk>/', SavedListDestroyAPIView.as_view(), name='favorites-delete'),
]