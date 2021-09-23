django-multidb-router
=====================

.. image:: https://img.shields.io/github/workflow/status/jbalogh/django-multidb-router/CI?label=CI&logo=github&branch=master
    :alt: Build Status
    :target: https://github.com/jbalogh/django-multidb-router/actions?query=workflow%3ACI


.. image:: https://img.shields.io/pypi/v/django-multidb-router.svg
    :target: https://pypi.python.org/pypi/django-multidb-router


``multidb`` provides two Django database routers useful in primary-replica database
deployments.


ReplicaRouter
-----------------

With ``multidb.ReplicaRouter`` all read queries will go to a replica
database;  all inserts, updates, and deletes will go to the ``default``
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
``multidb.get_replica``::

    from django.db import connections
    import multidb

    connection = connections[multidb.get_replica()]


PinningReplicaRouter
------------------------

In some applications, the lag between the primary database receiving a write and its
replication to the replicas is enough to cause inconsistency for the end user.
For example, imagine a scenario with 1 second of replication lag. If a user
makes a forum post (to the primary) and then is redirected to a fully-rendered
view of it (from a replica) 500ms later, the view will fail. If this is a problem
in your application, consider using ``multidb.PinningReplicaRouter``. This
router works in combination with ``multidb.middleware.PinningRouterMiddleware``
to assure that, after writing to the ``default`` database, future reads from
the same user agent are directed to the ``default`` database for a configurable
length of time.

Caveats
=======

``PinningRouterMiddleware`` identifies database writes primarily by request
type, assuming that requests with HTTP methods that are not ``GET``, ``TRACE``,
``HEAD``, or ``OPTIONS`` are writes. You can indicate that any view writes to
the database by using the ``multidb.db_write`` decorator. This will cause the
same result as if the request were, e.g., a ``POST``.

You can also manually set ``response._db_write = True`` to indicate that a
write occurred. This will not result in using the ``default`` database in this
request, but only in the next request.

Configuration
=============

To use ``PinningReplicaRouter``, put it into ``DATABASE_ROUTERS`` in your
settings::

    DATABASE_ROUTERS = ('multidb.PinningReplicaRouter',)

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


You may also set the 'Secure', 'HttpOnly', and 'SameSite' cookie attributes by
using the following settings. These settings are based on Django's settings for
the session and CSRF cookies::

    MULTIDB_PINNING_COOKIE_SECURE = False
    MULTIDB_PINNING_COOKIE_HTTPONLY = False
    MULTIDB_PINNING_COOKIE_SAMESITE = 'Lax'

Note: the 'SameSite' attribute is only `available on django 2.1 and higher
<https://docs.djangoproject.com/en/2.1/releases/2.1/>`_.

``use_primary_db``
==================

``multidb.pinning.use_primary_db`` is both a context manager and a decorator for
wrapping code to use the primary database. You can use it as a context manager::

    from multidb.pinning import use_primary_db

    with use_primary_db:
        touch_the_database()
    touch_another_database()

or as a decorator::

    from multidb.pinning import use_primary_db

    @use_primary_db
    def func(*args, **kw):
        """Touches the primary database."""


Running the Tests
-----------------

To run the tests, you'll need to install the development requirements::

    pip install -r requirements.txt
    ./run.sh test

Alternatively, you can run the tests with several versions of Django
and Python using tox:

    $ pip install tox

    $ tox
