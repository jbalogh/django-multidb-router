.. _multidb:

============================
Databases with Read Replicas
============================

.. automodule:: multidb
    :members:


.. _multidb-upgrade:

Upgrading
=========

From <0.9 to >=0.9
------------------

The biggest change from 0.8.x and below is that several names have
changed to de-emphasize the "master/slave" terminology.

* The setting ``SLAVE_DATABASES`` becomes ``REPLICA_DATABASES``.
* ``MasterSlaveRouter`` becomes ``ReplicaRouter``.
* ``PinningMasterSlaveRouter`` becomes ``PinningReplicaRouter``.
* ``get_slave()`` becomes ``get_replica()``.
* ``@use_master`` becomes ``@use_primary_db``

In 0.9, the old names are still available but will print warnings. They
will be removed in a future version.
