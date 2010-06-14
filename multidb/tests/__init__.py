from django.http import HttpRequest, HttpResponse
from django.test import TestCase

from nose.tools import eq_

from multidb import (DEFAULT_DB_ALIAS, MasterSlaveRouter,
    PinningMasterSlaveRouter, get_slave)
from multidb.middleware import (PINNING_COOKIE, PINNING_SECONDS,
    PinningRouterMiddleware)
from multidb.pinning import (this_thread_is_pinned,
    pin_this_thread, unpin_this_thread)


class UnpinningTestCase(TestCase):
    """Test case that unpins the thread on tearDown"""

    def tearDown(self):
        unpin_this_thread()


class MasterSlaveRouterTests(TestCase):
    """Tests for MasterSlaveRouter"""

    def test_db_for_read(self):
        eq_(MasterSlaveRouter().db_for_read(None), get_slave())
        # TODO: Test the round-robin functionality.

    def test_db_for_write(self):
        eq_(MasterSlaveRouter().db_for_write(None), DEFAULT_DB_ALIAS)

    def test_allow_syncdb(self):
        """Make sure allow_syncdb() does the right thing for both masters and
        slaves"""
        router = MasterSlaveRouter()
        assert router.allow_syncdb(DEFAULT_DB_ALIAS, None)
        assert not router.allow_syncdb(get_slave(), None)


class SettingsTests(TestCase):
    """Tests for settings defaults"""

    def test_cookie_default(self):
        """Check that the cookie name has the right default."""
        eq_(PINNING_COOKIE, 'multidb_pin_writes')

    def test_pinning_seconds_default(self):
        """Make sure the cookie age has the right default."""
        eq_(PINNING_SECONDS, 15)


class PinningTests(UnpinningTestCase):
    """Tests for "pinning" functionality, above and beyond what's inherited
    from MasterSlaveRouter"""

    def test_pinning_encapsulation(self):
        """Check the pinning getters and setters."""
        assert not this_thread_is_pinned(), \
            "Thread started out pinned or this_thread_is_pinned() is broken."

        pin_this_thread()
        assert this_thread_is_pinned(), \
            "pin_this_thread() didn't pin the thread."

        unpin_this_thread()
        assert not this_thread_is_pinned(), \
            "Thread remained pinned after unpin_this_thread()."

    def test_pinned_reads(self):
        """Test PinningMasterSlaveRouter.db_for_read() when pinned and when
        not."""
        router = PinningMasterSlaveRouter()

        eq_(router.db_for_read(None), get_slave())

        pin_this_thread()
        eq_(router.db_for_read(None), DEFAULT_DB_ALIAS)


class MiddlewareTests(UnpinningTestCase):
    """Tests for the middleware that supports pinning"""

    def test_process_request(self):
        """Make sure the thread gets set as pinned when the cookie is on the
        request and as unpinned when it isn't."""
        request = HttpRequest()
        request.COOKIES[PINNING_COOKIE] = 'y'

        middleware = PinningRouterMiddleware()
        middleware.process_request(request)
        assert this_thread_is_pinned()

        del request.COOKIES[PINNING_COOKIE]
        middleware.process_request(request)
        assert not this_thread_is_pinned()

    def test_process_response(self):
        """Make sure the cookie gets set on POST requests and not otherwise."""
        request = HttpRequest()
        middleware = PinningRouterMiddleware()

        response = middleware.process_response(request, HttpResponse())
        assert PINNING_COOKIE not in response.cookies

        request.method = 'POST'
        response = middleware.process_response(request, HttpResponse())
        assert PINNING_COOKIE in response.cookies
        eq_(response.cookies[PINNING_COOKIE]['max-age'],
            PINNING_SECONDS)
