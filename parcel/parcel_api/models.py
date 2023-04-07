from django.db import models
from django.utils.translation import gettext as _
from django.core.validators import MinValueValidator
from parcel_api.utils import gen_uuid


class NoNegativeFloatField(models.FloatField):
    default_validators = [MinValueValidator(0)]


class ParcelTypeModel(models.Model):
    name = models.CharField(
        _("Тип товара"),
        max_length=64
    )

    def __repr__(self) -> str:
        return self.name

    def __str__(self) -> str:
        return super().__repr__()

class ParcelModel(models.Model):
    id = models.UUIDField(
        primary_key=True,
        default=gen_uuid,
        editable=False
    )
    name = models.CharField(
        _("Название"),
        max_length=128
    )

    weight = NoNegativeFloatField(
        _("Вес")
    )

    type = models.ForeignKey(
        ParcelTypeModel,
        models.CASCADE,
        related_name='types',
        related_query_name="type",
    )

    parcel_price = NoNegativeFloatField(
        _("Цена ($)"),
    )

    deliver_price = NoNegativeFloatField(
        _("Цена доставки (руб)"),
        null=True,
        blank=True
    )
