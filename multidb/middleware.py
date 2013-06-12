from django.conf import settings

from .pinning import pin_this_thread, unpin_this_thread, \
                     set_db_write_for_this_thread_if_needed, \
                     this_thread_has_db_write_set, \
                     unset_db_write_for_this_thread


# The name of the cookie that directs a request's reads to the master DB
PINNING_COOKIE = getattr(settings, 'MULTIDB_PINNING_COOKIE',
                         'multidb_pin_writes')


# The number of seconds for which reads are directed to the master DB after a
# write
PINNING_SECONDS = int(getattr(settings, 'MULTIDB_PINNING_SECONDS', 15))


class PinningRouterMiddleware(object):
    """Middleware to support the PinningMasterSlaveRouter

    If the request is a POST or is listed in MULTIDB_PINNING_VIEWS, it
    pins it to the master; it also attaches a cookie to a user agent
    who has just written, causing subsequent DB reads (for some period
    of time, hopefully exceeding replication lag) to be handled by the
    master.

    When the cookie is detected on a request, it pins to the master.
    """
    def process_request(self, request):
        """Set the thread's pinning flag according to the presence of the
        incoming cookie."""
        unset_db_write_for_this_thread()
        set_db_write_for_this_thread_if_needed(request)
        if PINNING_COOKIE in request.COOKIES or this_thread_has_db_write_set():
            pin_this_thread()
        else:
            # In case the last request this thread served was pinned:
            unpin_this_thread()

    def process_view(self, request, view_func, view_args, view_kwargs):
        """Pin the thread if the current view is in MULTIDB_PINNING_VIEWS."""
        set_db_write_for_this_thread_if_needed(request, view_func)
        if this_thread_has_db_write_set():
            pin_this_thread()

    def process_response(self, request, response):
        """If there is reason to think there was a DB write, set the cookie.

        Even if it was already set, reset its expiration time.
        """
        if this_thread_has_db_write_set() or getattr(response, '_db_write',
                                                     False):
            response.set_cookie(PINNING_COOKIE, value='y',
                                max_age=PINNING_SECONDS)
        return response
