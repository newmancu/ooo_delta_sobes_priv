from celery.utils.log import get_task_logger
from parcel import celery_app
from django.conf import settings
from django.db.models import F
from parcel_api.models import ParcelModel
import requests

logger = get_task_logger(__name__)

def get_usd2rub():
    # returns value from external api

    # I/O task. Can be wrapped with Thread
    try:
        data = requests.get(settings.CONVERTER_URL).json()
        return data['Valute']['USD']['Value']
    except:
        return None

@celery_app.task
def perodic_update(*args, **kwargs):
    USD2RUB = get_usd2rub()
    if USD2RUB is None:
        logger.warn(
            "CONVERTER API doesn't response."
            "Skiping parcel_price updating."
        )
        return None
    (ParcelModel.objects
            .filter(deliver_price=None)
            .update(deliver_price=(
                F('weight') / 2 + F('parcel_price') * USD2RUB / 100
    )))

    logger.info(
        f'set parcel_price to ParcelModel with converter value: {USD2RUB}'
    )
