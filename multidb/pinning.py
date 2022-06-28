"""An encapsulated thread-local variable that indicates whether future DB
writes should be "stuck" to the master."""

from functools import wraps
import threading
import warnings


__all__ = ['this_thread_is_pinned', 'pin_this_thread', 'unpin_this_thread',
           'use_primary_db', 'use_secondary_db', 'use_master', 'db_write']


_locals = threading.local()


def this_thread_is_pinned():
    """Return whether the current thread should send all its reads to the
    master DB."""
    return getattr(_locals, 'pinned', False)


def pin_this_thread():
    """Mark this thread as "stuck" to the master for all DB access."""
    _locals.pinned = True


def unpin_this_thread():
    """Unmark this thread as "stuck" to the master for all DB access.

    If the thread wasn't marked, do nothing.

    """
    _locals.pinned = False


class _UseDB(object):
    """A contextmanager/decorator to use the specified database."""
    def __call__(self, func):
        @wraps(func)
        def decorator(*args, **kw):
            with self:
                return func(*args, **kw)
        return decorator

    def __enter__(self):
        _locals.old = getattr(_locals, 'old', [])
        _locals.old.append(this_thread_is_pinned())

    def __exit__(self, type, value, tb):
        previous_state = _locals.old.pop()
        if previous_state:
            pin_this_thread()
        else:
            unpin_this_thread()


class UsePrimaryDB(_UseDB):
    """A contextmanager/decorator to use the primary database."""
    def __enter__(self):
        super(UsePrimaryDB, self).__enter__()
        pin_this_thread()


class UseSecondaryDB(_UseDB):
    """A contextmanager/decorator to use the secondary database."""
    def __enter__(self):
        super(UseSecondaryDB, self).__enter__()
        unpin_this_thread()


class DeprecatedUseMaster(UsePrimaryDB):
    def __enter__(self):
        warnings.warn(
            '[multidb] @use_master has been deprecated, please switch to '
            '@use_primary_db',
            DeprecationWarning,
        )
        return super(DeprecatedUseMaster, self).__enter__()


use_primary_db = UsePrimaryDB()
use_secondary_db = UseSecondaryDB()
use_master = DeprecatedUseMaster()


def mark_as_write(response):
    """Mark a response as having done a DB write."""
    response._db_write = True
    return response


def db_write(fn):
    @wraps(fn)
    def _wrapped(*args, **kw):
        with use_primary_db:
            response = fn(*args, **kw)
        return mark_as_write(response)
    return _wrapped
