from django.db import models
from django.utils.translation import gettext as _
from django.core.validators import MinValueValidator
from django.contrib.sessions.models import Session
from parcel_api.utils import gen_uuid


# Custom models fields
class NoNegativeFloatField(models.FloatField):
    default_validators = [MinValueValidator(0)]


# Db models
class ParcelTypeModel(models.Model):
    """
    Db model of parcel's type
    """
    name = models.CharField(
        _("Тип товара"),
        max_length=64
    )

    def __repr__(self) -> str:
        return self.name

    def __str__(self) -> str:
        return super().__repr__()


class ParcelModel(models.Model):
    """
    Db model of Parcel
    """
    id = models.UUIDField(
        primary_key=True,
        default=gen_uuid,
        editable=False
    )

    user = models.ForeignKey(
        Session,
        models.CASCADE,
        related_name='parcels',
        verbose_name=_("Пользователь")
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
        related_name='parcels',
        verbose_name=_("Тип посылки")
    )

    parcel_price = NoNegativeFloatField(
        _("Цена ($)"),
    )

    deliver_price = NoNegativeFloatField(
        _("Цена доставки (руб)"),
        null=True,
        blank=True
    )
