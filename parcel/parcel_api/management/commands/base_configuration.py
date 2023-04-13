from django.core.management.base import BaseCommand
from parcel_api.models import ParcelTypeModel


class Command(BaseCommand):
    help = "startup command"

    def handle(self, *args, **options):
        """
        Initialization ParcelTypeModel with base objects
        """
        ParcelTypeModel.objects.get_or_create(name='Одежда')
        ParcelTypeModel.objects.get_or_create(name='Электроника')
        ParcelTypeModel.objects.get_or_create(name='Разное')
        self.stdout.write(self.style.SUCCESS('Base parcel types were added.'))
