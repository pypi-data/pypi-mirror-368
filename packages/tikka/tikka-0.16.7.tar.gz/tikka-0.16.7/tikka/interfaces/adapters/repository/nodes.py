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
from typing import List, Optional

from tikka.domains.entities.node import Node


class NodesRepositoryInterface(abc.ABC):
    """
    NodesRepositoryInterface class
    """

    COLUMN_URL = "node_url"
    COLUMN_PEER_ID = "node_peer_id"
    COLUMN_BLOCK = "node_block"
    COLUMN_SOFTWARE = "node_software"
    COLUMN_SOFTWARE_VERSION = "node_software_version"
    COLUMN_SESSION_KEYS = "node_session_keys"
    COLUMN_EPOCH_INDEX = "node_epoch_index"
    COLUMN_UNSAFE_API_EXPOSED = "node_unsafe_api_exposed"

    DEFAULT_LIST_OFFSET = 0
    DEFAULT_LIST_LIMIT = 1000

    SORT_ORDER_ASCENDING = "ASC"
    SORT_ORDER_DESCENDING = "DESC"

    @abc.abstractmethod
    def add(self, node: Node) -> None:
        """
        Add a new node in repository

        :param node: Node instance
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, url: str) -> Optional[Node]:
        """
        Return Node by url from repository

        :param url: Node url
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def update(self, node: Node) -> None:
        """
        Update node in repository

        :param node: Node instance
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def list(
        self,
        offset: int = DEFAULT_LIST_OFFSET,
        limit: int = DEFAULT_LIST_LIMIT,
        sort_column: str = COLUMN_URL,
        sort_order: str = SORT_ORDER_ASCENDING,
    ) -> List[Node]:
        """
        List nodes from repository

        :param offset: Offset index to get rows from
        :param limit: Number of rows to return
        :param sort_column: Sort column, default to NodesRepositoryInterface.COLUMN_URL
        :param sort_order: Sort order, default to NodesRepositoryInterface.ASC
        :param limit: Number of rows to return
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def delete(self, url: str) -> None:
        """
        Delete node by url in repository

        :param url: Url of Node to delete
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def delete_all(self) -> None:
        """
        Delete all nodes in repository

        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def count(self) -> int:
        """
        Return number of nodes in repository

        :return:
        """
        raise NotImplementedError

    def get_urls(self) -> List[str]:
        """
        Get all urls of nodes from repository

        :return:
        """
        raise NotImplementedError
