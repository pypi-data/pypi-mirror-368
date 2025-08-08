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
from datetime import datetime
from typing import List, Optional

from tikka.domains.entities.transfer import Transfer
from tikka.interfaces.adapters.network.indexer.indexer import NetworkIndexerInterface


class IndexerTransfersInterface(abc.ABC):
    """
    IndexerTransfersInterface class
    """

    COLUMN_TIMESTAMP = "timestamp"

    SORT_ORDER_ASCENDING = "ASC"
    SORT_ORDER_DESCENDING = "DESC"

    def __init__(self, indexer: NetworkIndexerInterface) -> None:
        """
        Init IndexerTransfersInterface instance

        :param indexer: NetworkIndexerInterface instance
        :return:
        """
        self.indexer = indexer

    @abc.abstractmethod
    def list(
        self,
        address: str,
        limit: int,
        offset: int = 0,
        sort_column: str = COLUMN_TIMESTAMP,
        sort_order: str = SORT_ORDER_DESCENDING,
        from_datetime: Optional[datetime] = None,
        to_datetime: Optional[datetime] = None,
    ) -> List[Transfer]:
        """
        Return list of transfers from and to address

        :param address: Account address
        :param limit: Max number of transfers to return
        :param offset: Offset to paginate results
        :param sort_column: Sort column, default to IndexerTransfersInterface.COLUMN_TIMESTAMP
        :param sort_order: Sort order, default to IndexerTransfersInterface.SORT_ORDER_DESCENDING
        :param from_datetime: Only transfers from datetime, default to None
        :param to_datetime: Only transfers until datetime, default to None
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def count(self, address) -> int:
        """
        Return transfers total count from and to address

        :param address: Account address
        :return:
        """
        raise NotImplementedError


class IndexerTransfersException(Exception):
    """
    IndexerTransfersException class
    """
