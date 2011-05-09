"""An encapsulated thread-local variable that indicates whether future DB
writes should be "stuck" to the master."""

from functools import wraps
import threading


"""
These constants give a reason why a thread was pinned.
* PIN_NONE - It wasn't pinned.
* PIN_POST - The request was a POST.
* PIN_WRITE - There was a DB write.
It's important to distinguish these so we can decide whether or not we need
to re-set the pinning cookie or we can let it expire.
"""
PIN_NONE = 0
PIN_POST = 1
PIN_WRITE = 2
_locals = threading.local()


def this_thread_is_pinned():
    """Return whether the current thread should send all its reads to the
    master DB."""
    return getattr(_locals, 'pinned', PIN_NONE)


def pin_this_thread(reason=PIN_POST):
    """Mark this thread as "stuck" to the master for all DB access."""
    _locals.pinned = reason


def unpin_this_thread():
    """Unmark this thread as "stuck" to the master for all DB access.

    If the thread wasn't marked, do nothing.

    """
    try:
        del _locals.pinned
    except AttributeError:
        pass


class UseMaster(object):
    """A contextmanager/decorator to use the master database."""
    old = False

    def __call__(self, func):
        @wraps(func)
        def decorator(*args, **kw):
            with self:
                return func(*args, **kw)
        return decorator

    def __enter__(self):
        self.old = this_thread_is_pinned()
        pin_this_thread()

    def __exit__(self, type, value, tb):
        if not self.old:
            unpin_this_thread()
        if any((type, value, tb)):
            raise type, value, tb

use_master = UseMaster()
