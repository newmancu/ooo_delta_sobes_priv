from rest_framework import serializers as ser
from parcel_api import models


class GetParcelSerializer(ser.ModelSerializer):
    """
    A `GetParcelSerializer` is a ModelSerializer for
    representaiton ParcelModels' objects 
    """

    id = ser.UUIDField(format='hex')
    type = ser.SlugRelatedField(
        read_only=True,
        slug_field='name'
    )

    class Meta:
        model = models.ParcelModel
        exclude = ['user']

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['deliver_price'] = (
            "Не рассчитано" if ret['deliver_price'] is None
            else ret['deliver_price'])
        return ret


class BaseParcelSerializer(ser.ModelSerializer):
    """
    A `BaseParcelSerializer` is a ModelSerializer for
    creating ParcelModels' objects 
    """

    id = ser.UUIDField(format='hex', read_only=True)

    class Meta:
        model = models.ParcelModel
        exclude = ['deliver_price']
        extra_kwargs = {
            'user': {
                'required': False,
                'label': 'auto field'
            }
        }

    def to_representation(self, instance):
        # Change this method for different response representation
        ret = super().to_representation(instance)
        ret.pop('user', '')
        return ret


class BaseParcelTypeSerializer(ser.ModelSerializer):
    """
    A `BaseParcelTypeSerializer` is a ModelSerializer for
    creating and representaiton ParcelTypeModels' objects 
    """

    class Meta:
        model = models.ParcelTypeModel
        fields = '__all__'
