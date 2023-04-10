import uuid
from django.utils.cache import get_cache_key
from django.urls import reverse
from django.http import HttpRequest
from django.core.cache import cache

# A function for generation uuid
gen_uuid = uuid.uuid4

# Duplicatoin error code in mysql
DUPLICATION_ERROR_CODE = 1062

def clear_parcels_cache(META):
    """
    Clears a parcel's cache.
    Use this function for after creating a new parcel
    or modifying an existing parsel.
    """
    req = HttpRequest()
    req.path = reverse('parcel-list')
    req.META = META

    key = get_cache_key(req)
    if key is None:
        return
    _key = key.split('.')
    key_header = "views.decorators.cache.cache_header.%s.%s.%s.%s" % (
        _key[4],_key[6],_key[8],_key[9]
    )
    print(key)
    print(key_header)
    cache.delete_many((key, key_header))