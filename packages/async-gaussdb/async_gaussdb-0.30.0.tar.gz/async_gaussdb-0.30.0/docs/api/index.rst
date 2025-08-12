.. _async_gaussdb-api-reference:

=============
API Reference
=============

.. module:: async_gaussdb
    :synopsis: A fast PostgreSQL Database Client Library for Python/asyncio

.. currentmodule:: async_gaussdb


.. _async_gaussdb-api-connection:

Connection
==========

.. autofunction:: async_gaussdb.connection.connect


.. autoclass:: async_gaussdb.connection.Connection
   :members:


.. _async_gaussdb-api-prepared-stmt:

Prepared Statements
===================

Prepared statements are a PostgreSQL feature that can be used to optimize the
performance of queries that are executed more than once.  When a query
is *prepared* by a call to :meth:`Connection.prepare`, the server parses,
analyzes and compiles the query allowing to reuse that work once there is
a need to run the same query again.

.. code-block:: pycon

   >>> import async_gaussdb, asyncio
   >>> async def run():
   ...     conn = await async_gaussdb.connect()
   ...     stmt = await conn.prepare('''SELECT 2 ^ $1''')
   ...     print(await stmt.fetchval(10))
   ...     print(await stmt.fetchval(20))
   ...
   >>> asyncio.run(run())
   1024.0
   1048576.0

.. note::

   async_gaussdb automatically maintains a small LRU cache for queries executed
   during calls to the :meth:`~Connection.fetch`, :meth:`~Connection.fetchrow`,
   or :meth:`~Connection.fetchval` methods.

.. warning::

   If you are using pgbouncer with ``pool_mode`` set to ``transaction`` or
   ``statement``, prepared statements will not work correctly.  See
   :ref:`async_gaussdb-prepared-stmt-errors` for more information.


.. autoclass:: async_gaussdb.prepared_stmt.PreparedStatement()
   :members:


.. _async_gaussdb-api-transaction:

Transactions
============

The most common way to use transactions is through an ``async with`` statement:

.. code-block:: python

   async with connection.transaction():
       await connection.execute("INSERT INTO mytable VALUES(1, 2, 3)")


async_gaussdb supports nested transactions (a nested transaction context will create
a `savepoint`_.):

.. code-block:: python

   async with connection.transaction():
       await connection.execute('CREATE TABLE mytab (a int)')

       try:
           # Create a nested transaction:
           async with connection.transaction():
               await connection.execute('INSERT INTO mytab (a) VALUES (1), (2)')
               # This nested transaction will be automatically rolled back:
               raise Exception
       except:
           # Ignore exception
           pass

       # Because the nested transaction was rolled back, there
       # will be nothing in `mytab`.
       assert await connection.fetch('SELECT a FROM mytab') == []

Alternatively, transactions can be used without an ``async with`` block:

.. code-block:: python

    tr = connection.transaction()
    await tr.start()
    try:
        ...
    except:
        await tr.rollback()
        raise
    else:
        await tr.commit()


See also the
:meth:`Connection.transaction() <async_gaussdb.connection.Connection.transaction>`
function.

.. _savepoint: https://www.postgresql.org/docs/current/static/sql-savepoint.html


.. autoclass:: async_gaussdb.transaction.Transaction()
   :members:

   .. describe:: async with c:

      start and commit/rollback the transaction or savepoint block
      automatically when entering and exiting the code inside the
      context manager block.


.. _async_gaussdb-api-cursor:

Cursors
=======

Cursors are useful when there is a need to iterate over the results of
a large query without fetching all rows at once.  The cursor interface
provided by async_gaussdb supports *asynchronous iteration* via the ``async for``
statement, and also a way to read row chunks and skip forward over the
result set.

To iterate over a cursor using a connection object use
:meth:`Connection.cursor() <async_gaussdb.connection.Connection.cursor>`.
To make the iteration efficient, the cursor will prefetch records to
reduce the number of queries sent to the server:

.. code-block:: python

    async def iterate(con: Connection):
        async with con.transaction():
            # GaussDB requires non-scrollable cursors to be created
            # and used in a transaction.
            async for record in con.cursor('SELECT generate_series(0, 100)'):
                print(record)

Or, alternatively, you can iterate over the cursor manually (cursor
won't be prefetching any rows):

.. code-block:: python

    async def iterate(con: Connection):
        async with con.transaction():
            # GaussDB requires non-scrollable cursors to be created
            # and used in a transaction.

            # Create a Cursor object
            cur = await con.cursor('SELECT generate_series(0, 100)')

            # Move the cursor 10 rows forward
            await cur.forward(10)

            # Fetch one row and print it
            print(await cur.fetchrow())

            # Fetch a list of 5 rows and print it
            print(await cur.fetch(5))

It's also possible to create cursors from prepared statements:

.. code-block:: python

    async def iterate(con: Connection):
        # Create a prepared statement that will accept one argument
        stmt = await con.prepare('SELECT generate_series(0, $1)')

        async with con.transaction():
            # GaussDB requires non-scrollable cursors to be created
            # and used in a transaction.

            # Execute the prepared statement passing `10` as the
            # argument -- that will generate a series or records
            # from 0..10.  Iterate over all of them and print every
            # record.
            async for record in stmt.cursor(10):
                print(record)


.. note::

   Cursors created by a call to
   :meth:`Connection.cursor() <async_gaussdb.connection.Connection.cursor>` or
   :meth:`PreparedStatement.cursor() <async_gaussdb.prepared_stmt.PreparedStatement.cursor>`
   are *non-scrollable*: they can only be read forwards.  To create a scrollable
   cursor, use the ``DECLARE ... SCROLL CURSOR`` SQL statement directly.

.. warning::

   Cursors created by a call to
   :meth:`Connection.cursor() <async_gaussdb.connection.Connection.cursor>` or
   :meth:`PreparedStatement.cursor() <async_gaussdb.prepared_stmt.PreparedStatement.cursor>`
   cannot be used outside of a transaction.  Any such attempt will result in
   :exc:`~async_gaussdb.exceptions.InterfaceError`.

   To create a cursor usable outside of a transaction, use the
   ``DECLARE ... CURSOR WITH HOLD`` SQL statement directly.


.. autoclass:: async_gaussdb.cursor.CursorFactory()
   :members:

   .. describe:: async for row in c

      Execute the statement and iterate over the results asynchronously.

   .. describe:: await c

      Execute the statement and return an instance of
      :class:`~async_gaussdb.cursor.Cursor` which can be used to navigate over and
      fetch subsets of the query results.


.. autoclass:: async_gaussdb.cursor.Cursor()
   :members:


.. _async_gaussdb-api-pool:

Connection Pools
================

.. autofunction:: async_gaussdb.pool.create_pool


.. autoclass:: async_gaussdb.pool.Pool()
   :members:


.. _async_gaussdb-api-record:

Record Objects
==============

Each row (or composite type value) returned by calls to ``fetch*`` methods
is represented by an instance of the :class:`~async_gaussdb.Record` object.
``Record`` objects are a tuple-/dict-like hybrid, and allow addressing of
items either by a numeric index or by a field name:

.. code-block:: pycon

    >>> import async_gaussdb
    >>> import asyncio
    >>> loop = asyncio.get_event_loop()
    >>> conn = loop.run_until_complete(async_gaussdb.connect())
    >>> r = loop.run_until_complete(conn.fetchrow('''
    ...     SELECT oid, rolname, rolsuper FROM pg_roles WHERE rolname = user'''))
    >>> r
    <Record oid=16388 rolname='elvis' rolsuper=True>
    >>> r['oid']
    16388
    >>> r[0]
    16388
    >>> dict(r)
    {'oid': 16388, 'rolname': 'elvis', 'rolsuper': True}
    >>> tuple(r)
    (16388, 'elvis', True)

.. note::

   ``Record`` objects currently cannot be created from Python code.

.. class:: Record()

   A read-only representation of PostgreSQL row.

   .. describe:: len(r)

      Return the number of fields in record *r*.

   .. describe:: r[field]

      Return the field of *r* with field name or index *field*.

   .. describe:: name in r

      Return ``True`` if record *r* has a field named *name*.

   .. describe:: iter(r)

      Return an iterator over the *values* of the record *r*.

   .. describe:: get(name[, default])

      Return the value for *name* if the record has a field named *name*,
      else return *default*. If *default* is not given, return ``None``.

      .. versionadded:: 0.18

   .. method:: values()

      Return an iterator over the record values.

   .. method:: keys()

      Return an iterator over the record field names.

   .. method:: items()

      Return an iterator over ``(field, value)`` pairs.


.. class:: ConnectionSettings()

    A read-only collection of Connection settings.

    .. describe:: settings.setting_name

       Return the value of the "setting_name" setting.  Raises an
       ``AttributeError`` if the setting is not defined.

       Example:

       .. code-block:: pycon

           >>> connection.get_settings().client_encoding
           'UTF8'


Data Types
==========

.. automodule:: async_gaussdb.types
   :members:
