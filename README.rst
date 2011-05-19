``multidb`` provides two Django database routers useful in master-slave
deployments.


MasterSlaveRouter
-----------------

With ``multidb.MasterSlaveRouter`` all read queries will go to a slave
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
``multidb.get_slave``::

    from django.db import connections
    import multidb

    connection = connections[multidb.get_slave()]


PinningMasterSlaveRouter
------------------------

In some applications, the lag between the master receiving a write and its
replication to the slaves is enough to cause inconsistency for the end user.
For example, imagine a scenario with 1 second of replication lag. If a user
makes a forum post (to the master) and then is redirected to a fully-rendered
view of it (from a slave) 500ms later, the view will fail. If this is a problem
in your application, consider using ``multidb.PinningMasterSlaveRouter``. This
router works in combination with ``multidb.middleware.PinningRouterMiddleware``
to assure that, after writing to the ``default`` database, future reads from
the same user agent are directed to the ``default`` database for a configurable
length of time.

Caveats
=======

``PinningRouterMiddleware`` identifies database writes primarily by request
type, assuming that any ``POST`` request is a write. You can indicate that
any view triggers a database write by using the ``multidb.db_write`` decorator.
You can also manually set ``response._db_write = True`` to indicate that a
write occurred. Either one of these will cause the same result as if the
request was a ``POST``.

This package makes no attempt to redirect database activity that occurs after a
write but during the same request. You application is responsible for manually
directing such activity to ``default`` with, for instance, the ``using`` method
or keyword argument.

Configuration
=============

To use ``PinningMasterSlaveRouter``, put it into ``DATABASE_ROUTERS`` in your
settings::

    DATABASE_ROUTERS = ('multidb.PinningMasterSlaveRouter',)

Then, install the middleware. It must be listed before any other middleware
which performs database writes::

    MIDDLEWARE_CLASSES = (
        'multidb.middleware.PinningRouterMiddleware',
        ...more middleware here...
    )

``PinningRouterMiddleware`` attaches a cookie to any user agent who has just
written. The cookie should be set to expire at a time longer than your
replication lag. By default, its value is a conservative 15 seconds, but it can
be adjusted like so::

    MULTIDB_PINNING_SECONDS = 5

If you need to change the name of the cookie, use the ``MULTIDB_PINNING_COOKIE``
setting::

    MULTIDB_PINNING_COOKIE = 'multidb_pin_writes'


``use_master``
==============

``multidb.pinning.use_master`` is both a context manager and a decorator for
wrapping code to use the master database. You can use it as a context manager::

    from multidb.pinning import use_master

    with use_master:
        touch_the_database()
    touch_another_database()

or as a decorator::

    from multidb.pinning import use_master

    @use_master
    def func(*args, **kw):
        """Touches the master database."""
