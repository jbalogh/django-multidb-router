from django.http import HttpResponse
from django.views.generic import View

from multidb.pinning import this_thread_is_pinned


def _pinned():
    """Return a text/plain HttpResponse with content "pinned" or "not pinned".
    """
    result = "pinned" if this_thread_is_pinned() else "not pinned"
    return HttpResponse(result, content_type="text/plain")


def dummy_view(request):
    return _pinned()


class class_based_dummy_view(View):

    def get(self, request, *args, **kwargs):
        return _pinned()


class object_dummy_view(object):
    """An example of this kind of view is django.contrib.syndication.Feed."""

    def __call__(self, request, *args, **kwargs):
        return _pinned()
