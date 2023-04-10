from django.urls import path, include
from django.conf import settings
from parcel_api import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('parcels', views.ParcelViewSet, basename='parcel')

urlpatterns = [
    path('api/', include([
        path('', include(router.urls)),
        path('register/', views.RegisterParcelGenerics.as_view(), name='register_parcel'),
        path('types/', views.ListParcelsTypesGenerics.as_view(), name='parcel_types'),
    ])),
]

# Urls for developer
if settings.DEBUG:
    urlpatterns += [
        path('api/update/', views.UpdatePrices.as_view(), name='update_prices')
    ]