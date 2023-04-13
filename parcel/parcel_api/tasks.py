from celery.utils.log import get_task_logger
from django.conf import settings
from django.db.models import F
from parcel import celery_app
from parcel_api.models import ParcelModel
from parcel_api.middleware import clear_parcels_cache_by_keys
import requests

logger = get_task_logger(__name__)


def get_usd2rub():
    """
    Returns a value from an external api
    """

    # I/O task. Can be wrapped with Thread
    try:
        data = requests.get(settings.CONVERTER_URL).json()
        return data['Valute']['USD']['Value']
    except:
        return None


@celery_app.task
def perodic_update(*args, **kwargs):
    """
    Calculates `deliver_price` for ParcelModel
    with None `deliver_price`.

    This function could be scheduled like a celery task
    """
    USD2RUB = get_usd2rub()
    if USD2RUB is None:
        logger.warn(
            "CONVERTER API doesn't response."
            "Skiping parcel_price updating."
        )
        return None
    filtered = ParcelModel.objects.filter(deliver_price=None)
    keys = filtered.distinct().values_list('user_id', flat=True)
    clear_parcels_cache_by_keys(keys)
    filtered.update(deliver_price=(
        (F('weight') / 2 + F('parcel_price') / 100) * USD2RUB
    ))
    logger.info('Cleared keys: %s', keys)
    logger.info(
        'set parcel_price to ParcelModel with converter value: %s.',
        USD2RUB
    )
