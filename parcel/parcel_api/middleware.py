from django.http import HttpRequest, HttpResponse
from django.utils.cache import has_vary_header
from django.utils.crypto import md5
from django.utils.decorators import decorator_from_middleware_with_args
from django.core.cache import cache
from django.middleware.cache import CacheMiddleware
from django.conf import settings
import typing as tp


def get_cache_key(request: HttpRequest, key_prefix=None, method="GET"):
    """
    Converts a request to a key for caching
    """
    session_key = request.session.session_key
    url = md5(request.path.encode("ascii"), usedforsecurity=False)

    if key_prefix is None:
        key_prefix = settings.CACHE_MIDDLEWARE_KEY_PREFIX
    key = f'parcel.{session_key}.{url.hexdigest()}.{key_prefix}.{method}'
    return key


def clear_parcel_cache():
    """
    Clears parcels's caches.
    Use this function for after creating a new parcel
    or modifying an existing parsel.
    """
    keys = cache.keys('parcel.*')
    cache.delete_many(keys)


def clear_parcels_cache_by_keys(session_key_keys: tp.Iterable):
    """
    Clears caches of parcels by users' session keys.
    Use this function for after creating a new parcel
    or modifying an existing parsel.
    """
    tmp_keys = (cache.keys(f'parcel.{key}.*') for key in session_key_keys)
    keys = []
    for key in tmp_keys:
        keys += key
    cache.delete_many(keys)


def clear_parcel_session_cache(session_key: str):
    """
    Clears parcels' caches of specific user by his session key.
    Use this function for after creating a new parcel
    or modifying an existing parsel.
    """

    keys = cache.keys(f'parcel.{session_key}.*')
    cache.delete_many(keys)


class ParcelNoCacheMiddleware(CacheMiddleware):

    def process_request(self, request: HttpRequest):
        """
        Check whether the page is already cached and return the cached
        version if available.
        """
        if request.method not in ("GET"):
            request._cache_update_cache = False
            return None  # Don't bother checking the cache.

        # try and get the cached GET response
        cache_key = get_cache_key(request, self.key_prefix, "GET")
        if cache_key is None:
            request._cache_update_cache = True
            return None  # No cache information available, need to rebuild.
        response = self.cache.get(cache_key)
        # if it wasn't found and we are looking for a HEAD, try looking just for that
        # if response is None and request.method == "HEAD":
        #     cache_key = get_cache_key(
        #         request, self.key_prefix, "HEAD"
        #     )
        #     response = self.cache.get(cache_key)

        if response is None:
            request._cache_update_cache = True
            return None  # No cache information available, need to rebuild.

        # hit, return cached response
        request._cache_update_cache = False
        return response

    def process_response(self, request: HttpRequest, response: HttpResponse):
        """Set the cache, if needed."""
        if not self._should_update_cache(request, response):
            # We don't need to update the cache, just return.
            return response

        if response.streaming or response.status_code not in (200, 304):
            return response

        # Don't cache responses that set a user-specific (and maybe security
        # sensitive) cookie in response to a cookie-less request.
        if (
            not request.COOKIES
            and response.cookies
            and has_vary_header(response, "Cookie")
        ):
            return response

        # Don't cache a response with 'Cache-Control: private'
        if "private" in response.get("Cache-Control", ()):
            return response

        # Page timeout takes precedence over the "max-age" and the default
        # cache timeout.
        timeout = self.page_timeout
        if timeout is None:
            timeout = self.cache_timeout
            return response
        if timeout and response.status_code == 200:
            cache_key = get_cache_key(request, self.key_prefix, request.method)
            if hasattr(response, "render") and callable(response.render):
                response.add_post_render_callback(
                    lambda r: self.cache.set(cache_key, r, timeout)
                )
            else:
                self.cache.set(cache_key, response, timeout)
        return response


def no_cache_parcel(timeout, *, cache=None, key_prefix=None):
    """
    Decorator from custom CacheMiddleware that is based on
    standarts Django CacheMiddleware.
    """
    return decorator_from_middleware_with_args(ParcelNoCacheMiddleware)(
        page_timeout=timeout,
        cache_alias=cache,
        key_prefix=key_prefix,
    )
