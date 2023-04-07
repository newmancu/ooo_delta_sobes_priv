from rest_framework.generics import (
    ListAPIView, 
    CreateAPIView
)
from rest_framework.viewsets import ReadOnlyModelViewSet

from parcel_api import serializers as ser
from parcel_api import models
from parcel_api.utils import gen_uuid, DUPLICATION_ERROR_CODE
from django.db.utils import IntegrityError


class RegisterParcelGenerics(CreateAPIView):
    serializer_class = ser.BaseParcelSerializer

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
        parcels:list[int] = self.request.session.get('parcels', [])
        print(serializer.validated_data['id'])
        parcels.append(str(serializer.validated_data['id']))
        self.request.session['parcels'] = parcels


class ListParcelsTypesGenerics(ListAPIView):
    serializer_class = ser.BaseParcelTypeSerializer
    queryset = models.ParcelTypeModel.objects.all()


class ParcelViewSet(ReadOnlyModelViewSet):
    
    serializer_class = ser.GetParcelSerializer

    def get_queryset(self):
        qs = models.ParcelModel.objects.filter(
            id__in= self.request.session.get('parcels', [])
        )
        return qs