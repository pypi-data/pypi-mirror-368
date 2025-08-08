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

from typing import Any, List, Optional

from sql import Column, Flavor, Table

from tikka.domains.entities.node import Node
from tikka.interfaces.adapters.repository.db_repository import DBRepositoryInterface
from tikka.interfaces.adapters.repository.nodes import NodesRepositoryInterface

TABLE_NAME = "nodes"

# create sql table wrapper
sql_nodes_table = Table(TABLE_NAME)

SQL_COLUMNS = {
    NodesRepositoryInterface.COLUMN_URL: "url",
    NodesRepositoryInterface.COLUMN_PEER_ID: "peer_id",
    NodesRepositoryInterface.COLUMN_BLOCK: "block",
    NodesRepositoryInterface.COLUMN_SOFTWARE: "software",
    NodesRepositoryInterface.COLUMN_SOFTWARE_VERSION: "software_version",
    NodesRepositoryInterface.COLUMN_SESSION_KEYS: "session_keys",
    NodesRepositoryInterface.COLUMN_EPOCH_INDEX: "epoch_index",
    NodesRepositoryInterface.COLUMN_UNSAFE_API_EXPOSED: "unsafe_api_exposed",
}

DEFAULT_LIST_OFFSET = 0
DEFAULT_LIST_LIMIT = 1000


class DBNodesRepository(NodesRepositoryInterface, DBRepositoryInterface):
    """
    DBNodesRepository class
    """

    def list(
        self,
        offset: int = DEFAULT_LIST_OFFSET,
        limit: int = DEFAULT_LIST_LIMIT,
        sort_column: str = NodesRepositoryInterface.COLUMN_URL,
        sort_order: str = NodesRepositoryInterface.SORT_ORDER_ASCENDING,
    ) -> List[Node]:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            NodesRepositoryInterface.list.__doc__
        )

        sql_columns = {
            NodesRepositoryInterface.COLUMN_URL: sql_nodes_table.url,
            NodesRepositoryInterface.COLUMN_BLOCK: sql_nodes_table.block,
            NodesRepositoryInterface.COLUMN_SOFTWARE: sql_nodes_table.software,
            NodesRepositoryInterface.COLUMN_PEER_ID: sql_nodes_table.peer_id,
            NodesRepositoryInterface.COLUMN_EPOCH_INDEX: sql_nodes_table.epoch_index,
            NodesRepositoryInterface.COLUMN_UNSAFE_API_EXPOSED: sql_nodes_table.unsafe_api_exposed,
            NodesRepositoryInterface.COLUMN_SESSION_KEYS: sql_nodes_table.session_keys,
            NodesRepositoryInterface.COLUMN_SOFTWARE_VERSION: sql_nodes_table.software_version,
        }
        # if sort column...
        if sort_column is not None:
            # set sort column
            sql_sort_colum: Column = sql_columns[sort_column]
            # create select query wrapper with order by
            sql_select = sql_nodes_table.select(
                order_by=sql_sort_colum.asc
                if sort_order == NodesRepositoryInterface.SORT_ORDER_ASCENDING
                else sql_sort_colum.desc,
                offset=offset,
                limit=limit,
            )
        else:
            #  create select query wrapper without order by
            sql_select = sql_nodes_table.select(offset=offset, limit=limit)

        # config sql with ? as param style
        Flavor.set(Flavor(paramstyle="qmark"))

        sql, args = tuple(sql_select)
        result_set = self.client.select(sql, args)
        list_ = []
        for row in result_set:
            list_.append(get_node_from_row(row))

        return list_

    def add(self, node: Node) -> None:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            NodesRepositoryInterface.add.__doc__
        )
        # insert only non protected fields
        self.client.insert(
            TABLE_NAME,
            **get_fields_from_node(node),
        )

    def get(self, url: str) -> Optional[Node]:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            NodesRepositoryInterface.list.__doc__
        )

        row = self.client.select_one(f"SELECT * FROM {TABLE_NAME} WHERE url=?", (url,))
        if row is None:
            return None

        return get_node_from_row(row)

    def update(self, node: Node) -> None:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            NodesRepositoryInterface.update.__doc__
        )

        # update only non hidden fields
        self.client.update(
            TABLE_NAME,
            f"url='{node.url}'",
            **get_fields_from_node(node),
        )

    def delete(self, url: str) -> None:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            NodesRepositoryInterface.delete.__doc__
        )

        self.client.delete(TABLE_NAME, url=url)

    def delete_all(self) -> None:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            NodesRepositoryInterface.delete_all.__doc__
        )

        self.client.clear(TABLE_NAME)

    def count(self) -> int:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            NodesRepositoryInterface.delete.__doc__
        )
        row = self.client.select_one(f"SELECT count(url) FROM {TABLE_NAME}")
        if row is None:
            return 0

        return row[0]

    def get_urls(self) -> List[str]:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            NodesRepositoryInterface.get_urls.__doc__
        )
        sql = f"SELECT url FROM {TABLE_NAME}"
        result_set = self.client.select(sql)
        list_ = []
        for row in result_set:
            list_.append(row[0])

        return list_


def get_fields_from_node(node: Node) -> dict:
    """
    Return a dict of supported fields with normalized value

    :param node: Node instance
    :return:
    """
    fields = {}
    for (key, value) in node.__dict__.items():
        if key.startswith("_"):
            continue
        elif isinstance(value, bool):
            value = 1 if value is True else 0
        fields[key] = value

    return fields


def get_node_from_row(row: tuple) -> Node:
    """
    Return a Node instance from a result set row

    :param row: Result set row
    :return:
    """
    values: List[Any] = []
    count = 0
    for value in row:
        if count == 7:
            values.append(value == 1)
        else:
            values.append(value)
        count += 1

    return Node(*values)
