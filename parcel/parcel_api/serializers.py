from rest_framework import serializers as ser
from parcel_api import models


class GetParcelSerializer(ser.ModelSerializer):
    id = ser.UUIDField(format='hex')
    _type = ser.SlugRelatedField(
        read_only=True,
        slug_field='name'
    )

    class Meta:
        model = models.ParcelModel
        fields = '__all__'


class BaseParcelSerializer(ser.ModelSerializer):
    id = ser.UUIDField(format='hex', read_only=True)
    class Meta:
        model = models.ParcelModel
        exclude = ['deliver_price']


    def to_representation(self, instance):
        # change this method if you want another representation
        ret = super().to_representation(instance)
        ret.pop('uuid', '')
        return ret

class BaseParcelTypeSerializer(ser.ModelSerializer):

    class Meta:
        model = models.ParcelTypeModel
        fields = '__all__'
