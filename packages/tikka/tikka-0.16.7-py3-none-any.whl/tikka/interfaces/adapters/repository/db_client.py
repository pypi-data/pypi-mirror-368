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

import abc
from typing import Any, List, Optional, Union


class DBClientInterface(abc.ABC):
    """
    DBClientInterface class
    """

    @abc.abstractmethod
    def connect(self, uri: str) -> None:
        """
        Connect to database

        :param uri: Uri of file or server, or absolute path of file
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def disconnect(self) -> None:
        """
        Disconnect connection to database

        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def execute(
        self, request: str, args: Optional[Union[List, tuple]] = None
    ) -> List[Any]:
        """
        Execute Select request returning an iterator on result set

        :param request: DB request
        :param args: Arguments of DB request
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def select(
        self, request: str, args: Optional[Union[List, tuple]] = None
    ) -> List[tuple]:
        """
        Execute Select request returning an iterator on result set

        :param request: DB request
        :param args: Arguments of DB request
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def insert(self, table: str, **kwargs):
        """
        Create a new entry in table, with field=value kwargs

        :param table: Table name
        :param kwargs: fields with their values
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def insert_many(self, table: str, entries: List[dict]):
        """
        Batch insert of entries in table, with each dict = {field: value}

        :param table: Table name
        :param entries: List of entries
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def select_one(
        self, sql: str, args: Optional[Union[List, tuple]] = None
    ) -> Optional[tuple]:
        """
        Execute SELECT sql query and return first result

        :param sql: SELECT query
        :param args: Query arguments
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def update(self, table: str, where: str, **kwargs):
        """
        Update rows of table selected by where from **kwargs

        :param table: Table name
        :param where: WHERE statement
        :param kwargs: field=values kwargs
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def delete(self, table: str, **kwargs):
        """
        Delete a row from table where key=value (AND) from kwargs

        :param table: Table to delete from
        :param kwargs: Key/Value conditions (AND)
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def clear(self, table: str):
        """
        Clear table entries

        :param table: Name of the table
        :return:
        """
        raise NotImplementedError
