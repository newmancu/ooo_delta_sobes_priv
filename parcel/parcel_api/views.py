from django.db.utils import IntegrityError
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie
from django.core.cache import cache

from rest_framework.generics import (
    ListAPIView, 
    CreateAPIView
)
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from parcel_api import serializers as ser
from parcel_api import models
from parcel_api.utils import (
    gen_uuid, 
    DUPLICATION_ERROR_CODE,
    clear_parcels_cache
)

from parcel_api.tasks import perodic_update


class RegisterParcelGenerics(CreateAPIView):
    """
    Concrete view for creating a `ParcelModel` instances
    """
    serializer_class = ser.BaseParcelSerializer

    def create(self, request:Request, *args, **kwargs):
        print('1', self.request.session.session_key)
        if not self.request.session.session_key:
            self.request.session.create()
            print('2', self.request.session.session_key)
        data = dict(request.data)
        data['user'] = self.request.session.session_key
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        ret = Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        clear_parcels_cache(self.request.META)
        return ret

    def perform_create(self, serializer: ser.BaseParcelSerializer):
        passed = False
        while not passed:
            try:
                uuid = gen_uuid()
                passed = True
                serializer.validated_data['id'] = uuid
                serializer.save()
            except IntegrityError as err:
                if err.args[0] != DUPLICATION_ERROR_CODE:
                    raise err


class ListParcelsTypesGenerics(ListAPIView):
    """
    Concrete view for listing `ParcelType`s' instances.
    """
    serializer_class = ser.BaseParcelTypeSerializer
    queryset = models.ParcelTypeModel.objects.all()

    @method_decorator(cache_page(60*60*5))
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class ParcelViewSet(ReadOnlyModelViewSet):
    """
    A viewset for listing and retrieving 
    `ParcelModel`s' instaces for current user session.

    cache_page timeout is equal to `perodic_update` timeout
    """

    serializer_class = ser.GetParcelSerializer

    @method_decorator((vary_on_cookie, cache_page(5*60)))
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
    
    @method_decorator((vary_on_cookie, cache_page(5*60)))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    def get_queryset(self):
        qs = models.ParcelModel.objects.filter(
            user_id=self.request.session.session_key
        ).select_related('type')
        return qs
        

class UpdatePrices(APIView):
    """
    Only for debugging.
    Calls perodic_update on request
    """
    
    def post(self, request: Request, *args, **kwargs):
        perodic_update.delay()
        clear_parcels_cache(self.request.META)
        return Response("updated", status.HTTP_202_ACCEPTED)

    @method_decorator((vary_on_cookie,cache_page(1)))
    def get(self, request: Request, *args, **kwargs):
        key = cache.keys('*')
        kk = None
        return Response({'print':kk,'key':key}, status.HTTP_202_ACCEPTED)