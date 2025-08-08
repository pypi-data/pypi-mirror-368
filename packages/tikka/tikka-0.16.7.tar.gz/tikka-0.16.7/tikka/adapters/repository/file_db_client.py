# Copyright 2021 Vincent Texier <vit@free.fr>
#
# This software is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
import json
import logging
import sqlite3
from pathlib import Path
from queue import Queue
from typing import Any, List, Optional, Union
from urllib.parse import urlparse

from yoyo import get_backend, read_migrations

from tikka.domains.entities.constants import DATABASE_MIGRATIONS_PATH
from tikka.interfaces.adapters.repository.db_client import DBClientInterface


class FileDBClient(DBClientInterface):
    """
    FileDBClient with connection pool to be threadsafe
    """

    CONNECTIONS_POOL_SIZE = 5

    def __init__(self):
        """
        Init a Sqlite3 database client adapter instance

        Use a connection pool system to be threadsafe and fast
        """
        super().__init__()

        self.uri: Optional[str] = None
        self.db_pool = Queue(self.CONNECTIONS_POOL_SIZE)

    def connect(self, uri: str) -> None:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            DBClientInterface.connect.__doc__
        )
        self.uri = uri

        # update database
        self.migrate()

        # create pool of connections
        self.db_pool = Queue(self.CONNECTIONS_POOL_SIZE)
        for i in range(self.CONNECTIONS_POOL_SIZE):
            connection = sqlite3.connect(
                urlparse(self.uri).path, check_same_thread=False
            )
            connection.execute("PRAGMA foreign_keys = ON;")  # set check on foreign keys
            connection.commit()
            self.db_pool.put(connection)

    def disconnect(self):
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            DBClientInterface.disconnect.__doc__
        )
        while not self.db_pool.not_empty:
            connection = self.db_pool.get()
            connection.close()
        logging.debug("Sqlite3 connection closed.")

    def execute(
        self, request: str, args: Optional[Union[List, tuple]] = None
    ) -> List[Any]:
        """
        Execute SQL request with arg

        :param request: SQL request
        :param args: Arguments of SQL request
        :return:
        """
        if args is None:
            args = tuple()

        # get a connection from pool
        connection = self.db_pool.get()

        cursor = connection.cursor()
        try:
            if args is None:
                cursor.execute(request)
            else:
                cursor.execute(request, args)
            data = cursor.fetchall()
        except Exception as exception:
            logging.debug(request)
            if args:
                logging.debug(args)
            raise exception
        finally:
            connection.commit()
            self.db_pool.put(connection)  # Return connection back to the pool

        return data

    def execute_many(
        self, request: str, args: Optional[List[tuple]] = None
    ) -> List[Any]:
        """
        Execute SQL request with arg

        :param request: SQL request
        :param args: Arguments of SQL request
        :return:
        """
        # get a connection from pool
        connection = self.db_pool.get()

        cursor = connection.cursor()
        try:
            if args is None:
                cursor.executemany(request)
            else:
                cursor.executemany(request, args)
            data = cursor.fetchall()
        finally:
            connection.commit()
            self.db_pool.put(connection)  # Return connection back to the pool

        return data

    def select(
        self, request: str, args: Optional[Union[List, tuple]] = None
    ) -> List[Any]:
        """
        Execute Select request returning an iterator on result set

        :param request: SQL request
        :param args: Arguments of SQL request
        :return:
        """
        return self.execute(request, args)

    def insert(self, table: str, **kwargs):
        """
        Create a new entry in table, with field=value kwargs

        :param table: Table name
        :param kwargs: fields with their values
        :return:
        """
        fields_string = ",".join(kwargs.keys())
        values_string = ",".join(["?" for _ in range(len(kwargs))])
        filtered_values = []
        for value in kwargs.values():
            # serialize dict to json string
            filtered_values.append(
                json.dumps(value) if isinstance(value, dict) else value
            )

        sql = (
            f"INSERT OR IGNORE INTO {table} ({fields_string}) VALUES ({values_string})"
        )
        self.execute(sql, filtered_values)

    def insert_many(self, table: str, entries: List[dict]):
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            DBClientInterface.insert_many.__doc__
        )
        entry_values_list = []
        fields_string = ",".join(entries[0].keys())
        values_string = ",".join(["?" for _ in range(len(entries[0]))])
        for entry in entries:
            filtered_values = []
            for value in entry.values():
                # serialize dict to json string
                filtered_values.append(
                    json.dumps(value) if isinstance(value, dict) else value
                )
            entry_values_list.append(tuple(filtered_values))
        sql = (
            f"INSERT OR IGNORE INTO {table} ({fields_string}) VALUES ({values_string})"
        )
        self.execute_many(sql, entry_values_list)

    def select_one(
        self, sql: str, args: Optional[Union[List, tuple]] = None
    ) -> Optional[Any]:
        """
        Execute SELECT sql query and return first result

        :param sql: SELECT query
        :param args: Query arguments
        :return:
        """
        results = self.select(sql, args)
        if len(results) > 0:
            return results[0]

        return None

    def update(self, table: str, where: str, **kwargs):
        """
        Update rows of table selected by where from **kwargs

        :param table: Table name
        :param where: WHERE statement
        :param kwargs: field=values kwargs
        :return:
        """
        set_statement = ",".join([f"{field}=?" for field in kwargs])

        sql = f"UPDATE OR IGNORE {table} SET {set_statement} WHERE {where}"
        values = tuple(kwargs.values())

        self._update(sql, values)

    def _update(self, sql: str, values: tuple):
        """
        Send update request sql with values

        :param sql: SQL query
        :param values: Values to inject as sql params
        :return:
        """
        filtered_values = []
        for value in values:
            # serialize dict to json string
            filtered_values.append(
                json.dumps(value) if isinstance(value, dict) else value
            )
        self.execute(sql, filtered_values)

    def delete(self, table: str, **kwargs):
        """
        Delete a row from table where key=value (AND) from kwargs

        :param table: Table to delete from
        :param kwargs: Key/Value conditions (AND)
        :return:
        """
        conditions = " AND ".join([f"{key}=?" for key in kwargs])

        sql = f"DELETE FROM {table} WHERE {conditions}"
        self.execute(sql, tuple(kwargs.values()))

    def clear(self, table: str):
        """
        Clear table entries

        :param table: Name of the table
        :return:
        """
        # delete all entries
        self.execute(f"DELETE FROM {table}")

    def migrate(self):
        """
        Use Yoyo Python library to handle current database migrations

        :return:
        """
        migrations_path = str(
            Path(__file__).parent.parent.joinpath(DATABASE_MIGRATIONS_PATH).expanduser()
        )
        migrations = read_migrations(migrations_path)
        if self.uri is not None:

            backend = get_backend("sqlite:///" + urlparse(self.uri).path)
            with backend.lock():
                # Apply any outstanding migrations
                backend.apply_migrations(backend.to_apply(migrations))
                logging.debug(backend.applied_migrations_sql)


class NoConnectionError(Exception):
    pass
