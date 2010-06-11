"""
With :class:`multidb.MasterSlaveRouter` all read queries will go to a slave
database;  all inserts, updates, and deletes will do to the ``default``
database.

First, define ``SLAVE_DATABASES`` in your settings.  It should be a list of
database aliases that can be found in ``DATABASES``::

    DATABASES = {
        'default': {...},
        'shadow-1': {...},
        'shadow-2': {...},
    }
    SLAVE_DATABASES = ['shadow-1', 'shadow-2']

Then put ``multidb.MasterSlaveRouter`` into DATABASE_ROUTERS::

    DATABASE_ROUTERS = ('multidb.MasterSlaveRouter',)

The slave databases will be chosen in round-robin fashion.

If you want to get a connection to a slave in your app, use
:func:`multidb.get_slave`::

    from django.db import connections
    import multidb

    connection = connections[multidb.get_slave()]
"""
import itertools
import random

from django.conf import settings
from django.utils.thread_support import currentThread
from django.core.signals import post_save, post_delete, request_started


DEFAULT_DB_ALIAS = 'default'


if getattr(settings, 'SLAVE_DATABASES'):
    # Shuffle the list so the first slave db isn't slammed during startup.
    dbs = list(settings.SLAVE_DATABASES)
    random.shuffle(dbs)
    slaves = itertools.cycle(dbs)
    # Set the slaves as test mirrors of the master.
    for db in dbs:
        settings.DATABASES[db]['TEST_MIRROR'] = DEFAULT_DB_ALIAS
else:
    slaves = itertools.repeat(DEFAULT_DB_ALIAS)


def get_slave():
    """Returns the alias of a slave database."""
    return slaves.next()


_requests = {}


def get_written():
    return _requests.get(currentThread())


def set_written():
    _requests[currentThread()] = True


def clear_written():
    try:
        del _requests[currentThread()]
    except KeyError:
        pass


request_started.connections(clear_written)
post_save.connect(set_written)
post_delete.connect(set_written)


class MasterSlaveRouter(object):
    """Router that sends all reads to a slave, all writes to default."""

    def db_for_read(self, model, **hints):
        """Send reads to slaves in round-robin."""
        return get_slave()

    def db_for_write(self, model, **hints):
        """Send all writes to the master."""
        return DEFAULT_DB_ALIAS

    def allow_relation(self, obj1, obj2, **hints):
        """Allow all relations, so FK validation stays quiet."""
        return True

    def allow_syncdb(self, db, model):
        """Only allow syncdb on the master."""
        return db == DEFAULT_DB_ALIAS


class StickyMasterSlaveRouter(MasterSlaveRouter):
    """Sends all reads to a slave unless there has already been a write,
    then sends reads to the master for the remainder of the request."""

    def db_for_read(self, model, **hints):
        """Send reads to slaves in round-robin, unless there has been a
        write."""

        if get_written():
            return DEFAULT_DB_ALIAS
        return get_slave()
