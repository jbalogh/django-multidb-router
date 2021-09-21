from django.conf import settings

try:
    from django.utils.deprecation import MiddlewareMixin
except ImportError:
    class MiddlewareMixin(object):
        """Dummy class not to break compatibility with django 1.8"""
        pass

from .pinning import pin_this_thread, unpin_this_thread


def pinning_cookie():
    """The name of the cookie that directs a request's reads to the master DB.
    """
    return getattr(settings, 'MULTIDB_PINNING_COOKIE', 'multidb_pin_writes')


def pinning_cookie_httponly():
    return getattr(settings, 'MULTIDB_PINNING_COOKIE_HTTPONLY', False)


def pinning_cookie_samesite():
    return getattr(settings, 'MULTIDB_PINNING_COOKIE_SAMESITE', "Lax")


def pinning_cookie_secure():
    return getattr(settings, 'MULTIDB_PINNING_COOKIE_SECURE', False)


def pinning_seconds():
    """The number of seconds for which reads are directed to the master DB
    after a write.
    """
    return int(getattr(settings, 'MULTIDB_PINNING_SECONDS', 15))


READ_ONLY_METHODS = frozenset(['GET', 'TRACE', 'HEAD', 'OPTIONS'])


class PinningRouterMiddleware(MiddlewareMixin):
    """Middleware to support the PinningReplicaRouter

    Attaches a cookie to a user agent who has just written, causing subsequent
    DB reads (for some period of time, hopefully exceeding replication lag)
    to be handled by the master.

    When the cookie is detected on a request, sets a thread-local to alert the
    DB router.

    """
    def process_request(self, request):
        """Set the thread's pinning flag according to the presence of the
        incoming cookie."""
        if (pinning_cookie() in request.COOKIES or
                request.method not in READ_ONLY_METHODS):
            pin_this_thread()
        else:
            # In case the last request this thread served was pinned:
            unpin_this_thread()

    def process_response(self, request, response):
        """For some HTTP methods, assume there was a DB write and set the
        cookie.

        Even if it was already set, reset its expiration time.

        """
        if (request.method not in READ_ONLY_METHODS or
                getattr(response, '_db_write', False)):
            response.set_cookie(pinning_cookie(), value='y',
                                max_age=pinning_seconds(),
                                secure=pinning_cookie_secure(),
                                httponly=pinning_cookie_httponly(),
                                samesite=pinning_cookie_samesite())
        return response
