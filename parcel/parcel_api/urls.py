from django.urls import path, include
from parcel_api import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('parcels', views.ParcelViewSet, basename='parcel')

urlpatterns = [
    path('api/', include([
        path('', include(router.urls)),
        path('register/', views.RegisterParcelGenerics.as_view(), name='register_parcel'),
        path('types/', views.ListParcelsTypesGenerics.as_view(), name='parcel_types')
    ])),

    
]
