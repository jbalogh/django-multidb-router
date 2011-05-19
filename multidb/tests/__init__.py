from django.http import HttpRequest, HttpResponse
from django.test import TestCase

from nose.tools import eq_

from multidb import (DEFAULT_DB_ALIAS, MasterSlaveRouter,
    PinningMasterSlaveRouter, get_slave)
from multidb.middleware import (PINNING_COOKIE, PINNING_SECONDS,
    PinningRouterMiddleware)
from multidb.pinning import (this_thread_is_pinned,
    pin_this_thread, unpin_this_thread, use_master, db_write)


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

    def setUp(self):
        super(MiddlewareTests, self).setUp()

        # Every test uses these, so they're okay as attrs.
        self.request = HttpRequest()
        self.middleware = PinningRouterMiddleware()

    def test_pin_on_cookie(self):
        """Thread should pin when the cookie is set."""
        self.request.COOKIES[PINNING_COOKIE] = 'y'
        self.middleware.process_request(self.request)
        assert this_thread_is_pinned()

    def test_unpin_on_no_cookie(self):
        """Thread should unpin when cookie is absent and method isn't POST."""
        pin_this_thread()
        self.middleware.process_request(self.request)
        assert not this_thread_is_pinned()

    def test_pin_on_post(self):
        """Thread should pin when method is POST."""
        self.request.method = 'POST'
        self.middleware.process_request(self.request)
        assert this_thread_is_pinned()

    def test_process_response(self):
        """Make sure the cookie gets set on POST requests and not otherwise."""

        response = self.middleware.process_response(self.request, HttpResponse())
        assert PINNING_COOKIE not in response.cookies

        self.request.method = 'POST'
        response = self.middleware.process_response(self.request, HttpResponse())
        assert PINNING_COOKIE in response.cookies
        eq_(response.cookies[PINNING_COOKIE]['max-age'],
            PINNING_SECONDS)

    def test_attribute(self):
        """The cookie should get set if the _db_write attribute is True."""
        res = HttpResponse()
        res._db_write = True
        response = self.middleware.process_response(self.request, res)
        assert PINNING_COOKIE in response.cookies

    def test_db_write_decorator(self):
        """The @db_write decorator should make any view set the cookie."""
        req = self.request
        req.method = 'GET'
        def view(req):
            return HttpResponse()
        response = self.middleware.process_response(req, view(req))
        assert PINNING_COOKIE not in response.cookies

        @db_write
        def write_view(req):
            return HttpResponse()
        response = self.middleware.process_response(req, write_view(req))
        assert PINNING_COOKIE in response.cookies


class ContextDecoratorTests(TestCase):
    def test_decorator(self):
        @use_master
        def check():
            assert this_thread_is_pinned()
        unpin_this_thread()
        assert not this_thread_is_pinned()
        check()
        assert not this_thread_is_pinned()

    def test_decorator_resets(self):
        @use_master
        def check():
            assert this_thread_is_pinned()
        pin_this_thread()
        assert this_thread_is_pinned()
        check()
        assert this_thread_is_pinned()

    def test_context_manager(self):
        unpin_this_thread()
        assert not this_thread_is_pinned()
        with use_master:
            assert this_thread_is_pinned()
        assert not this_thread_is_pinned()

    def text_context_manager_resets(self):
        pin_this_thread()
        assert this_thread_is_pinned()
        with use_master:
            assert this_thread_is_pinned()
        assert this_thread_is_pinned()

    def test_context_manager_exception(self):
        unpin_this_thread()
        try:
            assert not this_thread_is_pinned()
            with use_master:
                assert this_thread_is_pinned()
                raise ValueError
        except ValueError:
            pass
        assert not this_thread_is_pinned()
