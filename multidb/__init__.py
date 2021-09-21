"""
With :class:`multidb.ReplicaRouter` all read queries will go to a replica
database;  all inserts, updates, and deletes will do to the ``default``
database.

First, define ``REPLICA_DATABASES`` in your settings.  It should be a list of
database aliases that can be found in ``DATABASES``::

    DATABASES = {
        'default': {...},
        'shadow-1': {...},
        'shadow-2': {...},
    }
    REPLICA_DATABASES = ['shadow-1', 'shadow-2']

Then put ``multidb.ReplicaRouter`` into DATABASE_ROUTERS::

    DATABASE_ROUTERS = ('multidb.ReplicaRouter',)

The replica databases will be chosen in round-robin fashion.

If you want to get a connection to a replica in your app, use
:func:`multidb.get_replica`::

    from django.db import connections
    import multidb

    connection = connections[multidb.get_replica()]
"""
import itertools
import random
import warnings

from django.conf import settings

from .pinning import this_thread_is_pinned, db_write  # noqa


VERSION = (0, 10, 0)
__version__ = '.'.join(map(str, VERSION))

DEFAULT_DB_ALIAS = 'default'


replicas = None


def _get_replica_list():
    global replicas
    if replicas is not None:
        return replicas

    dbs = None
    if hasattr(settings, 'REPLICA_DATABASES'):
        dbs = list(settings.REPLICA_DATABASES)
    elif hasattr(settings, 'SLAVE_DATABASES'):
        warnings.warn(
            '[multidb] The SLAVE_DATABASES setting has been deprecated. '
            'Please switch to the REPLICA_DATABASES setting.',
            DeprecationWarning,
        )
        dbs = list(settings.SLAVE_DATABASES)

    if not dbs:
        warnings.warn(
            '[multidb] No replica databases are configured! '
            'You can configure them with the REPLICA_DATABASES setting.',
            UserWarning,
        )
        replicas = itertools.repeat(DEFAULT_DB_ALIAS)
        return replicas

    # Shuffle the list so the first replica isn't slammed during startup.
    random.shuffle(dbs)

    # Set the replicas as test mirrors of the master.
    for db in dbs:
        settings.DATABASES[db].get('TEST', {})['MIRROR'] = DEFAULT_DB_ALIAS

    replicas = itertools.cycle(dbs)
    return replicas


def get_replica():
    """Returns the alias of a replica database."""
    return next(_get_replica_list())


def get_slave():
    warnings.warn(
        '[multidb] The get_slave() method has been deprecated. '
        'Please switch to the get_replica() method.',
        DeprecationWarning,
    )
    return get_replica()


class DeprecationMixin(object):
    def __init__(self, *args, **kwargs):
        warnings.warn(
            '[multidb] The MasterSlaveRouter and PinningMasterSlaveRouter '
            'classes have been deprecated. Please switch to the ReplicaRouter '
            'and PinningReplicaRouter classes respectively.',
            DeprecationWarning,
        )
        super(DeprecationMixin, self).__init__(*args, **kwargs)


class ReplicaRouter(object):
    """Router that sends all reads to a replica, all writes to default."""

    def db_for_read(self, model, **hints):
        """Send reads to replicas in round-robin."""
        return get_replica()

    def db_for_write(self, model, **hints):
        """Send all writes to the master."""
        return DEFAULT_DB_ALIAS

    def allow_relation(self, obj1, obj2, **hints):
        """Allow all relations, so FK validation stays quiet."""
        return True

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        return db == DEFAULT_DB_ALIAS

    def allow_syncdb(self, db, model):
        """Only allow syncdb on the master."""
        return db == DEFAULT_DB_ALIAS


class PinningReplicaRouter(ReplicaRouter):
    """Router that sends reads to master if a certain flag is set. Writes
    always go to master.

    Typically, we set a cookie in middleware for certain request HTTP methods
    and give it a max age that's certain to be longer than the replication lag.
    The flag comes from that cookie.

    """
    def db_for_read(self, model, **hints):
        """Send reads to replicas in round-robin unless this thread is "stuck" to
        the master."""
        return DEFAULT_DB_ALIAS if this_thread_is_pinned() else get_replica()


class MasterSlaveRouter(DeprecationMixin, ReplicaRouter):
    pass


class PinningMasterSlaveRouter(DeprecationMixin, PinningReplicaRouter):
    pass
