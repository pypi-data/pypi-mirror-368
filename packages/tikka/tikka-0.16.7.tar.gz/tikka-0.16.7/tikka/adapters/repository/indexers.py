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

from typing import List, Optional

from sql import Column, Flavor, Table

from tikka.domains.entities.indexer import Indexer
from tikka.interfaces.adapters.repository.db_repository import DBRepositoryInterface
from tikka.interfaces.adapters.repository.indexers import IndexersRepositoryInterface

TABLE_NAME = "indexers"

# create sql table wrapper
sql_indexers_table = Table(TABLE_NAME)

SQL_COLUMNS = {
    IndexersRepositoryInterface.COLUMN_URL: "url",
    IndexersRepositoryInterface.COLUMN_BLOCK: "block",
}

DEFAULT_LIST_OFFSET = 0
DEFAULT_LIST_LIMIT = 1000


class DBIndexersRepository(IndexersRepositoryInterface, DBRepositoryInterface):
    """
    DBIndexersRepository class
    """

    def list(
        self,
        offset: int = DEFAULT_LIST_OFFSET,
        limit: int = DEFAULT_LIST_LIMIT,
        sort_column: str = IndexersRepositoryInterface.COLUMN_URL,
        sort_order: str = IndexersRepositoryInterface.SORT_ORDER_ASCENDING,
    ) -> List[Indexer]:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            IndexersRepositoryInterface.list.__doc__
        )

        sql_columns = {
            DBIndexersRepository.COLUMN_URL: sql_indexers_table.url,
            DBIndexersRepository.COLUMN_BLOCK: sql_indexers_table.block,
        }

        # if sort column...
        if sort_column is not None:
            # set sort column
            sql_sort_colum: Column = sql_columns[sort_column]
            # create select query wrapper with order by
            sql_select = sql_indexers_table.select(
                order_by=sql_sort_colum.asc
                if sort_order == IndexersRepositoryInterface.SORT_ORDER_ASCENDING
                else sql_sort_colum.desc,
                offset=offset,
                limit=limit,
            )
        else:
            #  create select query wrapper without order by
            sql_select = sql_indexers_table.select(offset=offset, limit=limit)

        # config sql with ? as param style
        Flavor.set(Flavor(paramstyle="qmark"))

        sql, args = tuple(sql_select)
        result_set = self.client.select(sql, args)
        list_ = []
        for row in result_set:
            list_.append(get_indexer_from_row(row))

        return list_

    def add(self, indexer: Indexer) -> None:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            IndexersRepositoryInterface.add.__doc__
        )
        # insert only non-protected fields
        self.client.insert(
            TABLE_NAME,
            **get_fields_from_indexers(indexer),
        )

    def get(self, url: str) -> Optional[Indexer]:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            IndexersRepositoryInterface.list.__doc__
        )

        row = self.client.select_one(f"SELECT * FROM {TABLE_NAME} WHERE url=?", (url,))
        if row is None:
            return None

        return get_indexer_from_row(row)

    def update(self, indexer: Indexer) -> None:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            IndexersRepositoryInterface.update.__doc__
        )

        # update only non hidden fields
        self.client.update(
            TABLE_NAME,
            f"url='{indexer.url}'",
            **get_fields_from_indexers(indexer),
        )

    def delete(self, url: str) -> None:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            IndexersRepositoryInterface.delete.__doc__
        )

        self.client.delete(TABLE_NAME, url=url)

    def delete_all(self) -> None:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            IndexersRepositoryInterface.delete_all.__doc__
        )

        self.client.clear(TABLE_NAME)

    def count(self) -> int:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            IndexersRepositoryInterface.delete.__doc__
        )
        row = self.client.select_one(f"SELECT count(url) FROM {TABLE_NAME}")
        if row is None:
            return 0

        return row[0]

    def get_urls(self) -> List[str]:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            IndexersRepositoryInterface.get_urls.__doc__
        )
        sql = f"SELECT url FROM {TABLE_NAME}"
        result_set = self.client.select(sql)
        list_ = []
        for row in result_set:
            list_.append(row[0])

        return list_


def get_fields_from_indexers(indexer: Indexer) -> dict:
    """
    Return a dict of supported fields with normalized value

    :param indexer: Indexer instance
    :return:
    """
    fields = {}
    for (key, value) in indexer.__dict__.items():
        if key.startswith("_"):
            continue
        elif isinstance(value, bool):
            value = 1 if value is True else 0
        fields[key] = value

    return fields


def get_indexer_from_row(row: tuple) -> Indexer:
    """
    Return an Indexer instance from a result set row

    :param row: Result set row
    :return:
    """
    return Indexer(*row)
