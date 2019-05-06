from django.utils.cache import set_response_etag

from functools import wraps


def public_cache(func):
    @wraps(func)
    def _wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        result['Cache-Control'] = "public, must-revalidate, max-age=1800"
        return result