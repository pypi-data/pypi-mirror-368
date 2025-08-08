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

from tikka.domains.entities.indexer import Indexer


class IndexersRepositoryInterface(abc.ABC):
    """
    IndexersRepositoryInterface class
    """

    COLUMN_URL = "indexer_url"
    COLUMN_BLOCK = "indexer_block"

    DEFAULT_LIST_OFFSET = 0
    DEFAULT_LIST_LIMIT = 1000

    SORT_ORDER_ASCENDING = "ASC"
    SORT_ORDER_DESCENDING = "DESC"

    @abc.abstractmethod
    def add(self, indexer: Indexer) -> None:
        """
        Add a new indexer in repository

        :param indexer: Indexer instance
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, url: str) -> Optional[Indexer]:
        """
        Return Indexer by url from repository

        :param url: Indexer url
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def update(self, indexer: Indexer) -> None:
        """
        Update indexer in repository

        :param indexer: Indexer instance
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
    ) -> List[Indexer]:
        """
        List indexers from repository

        :param offset: Offset index to get rows from
        :param limit: Number of rows to return
        :param sort_column: Sort column, default to IndexersRepositoryInterface.COLUMN_URL
        :param sort_order: Sort order, default to IndexersRepositoryInterface.ASC
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def delete(self, url: str) -> None:
        """
        Delete indexer by url in repository

        :param url: Url of Indexer to delete
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def delete_all(self) -> None:
        """
        Delete all indexers in repository

        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def count(self) -> int:
        """
        Return number of indexers in repository

        :return:
        """
        raise NotImplementedError

    def get_urls(self) -> List[str]:
        """
        Get all urls of indexers from repository

        :return:
        """
        raise NotImplementedError
