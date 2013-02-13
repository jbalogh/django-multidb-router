from django.http import HttpResponse
from multidb.pinning import this_thread_is_pinned


def view_that_always_changes_the_db(request):
    result = "pinned" if this_thread_is_pinned() else "not pinned"
    return HttpResponse(result, content_type="text/plain")


def normal_view(request):
    result = "pinned" if this_thread_is_pinned() else "not pinned"
    return HttpResponse(result, content_type="text/plain")
