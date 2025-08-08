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
from typing import Any, Dict, List, Optional

from tikka.domains.entities.transfer import Transfer


class TransfersRepositoryInterface(abc.ABC):
    """
    TransfersRepositoryInterface class
    """

    COLUMN_ID = "transfer_id"
    COLUMN_ISSUER_ADDRESS = "transfer_issuer_address"
    COLUMN_ISSUER_IDENTITY_INDEX = "transfer_issuer_identity_index"
    COLUMN_ISSUER_IDENTITY_NAME = "transfer_issuer_identity_name"
    COLUMN_RECEIVER_ADDRESS = "transfer_receiver_address"
    COLUMN_RECEIVER_IDENTITY_INDEX = "transfer_receiver_identity_index"
    COLUMN_RECEIVER_IDENTITY_NAME = "transfer_receiver_identity_name"
    COLUMN_AMOUNT = "transfer_amount"
    COLUMN_TIMESTAMP = "transfer_timestamp"
    COLUMN_COMMENT = "transfer_comment"
    COLUMN_COMMENT_TYPE = "transfer_comment_type"

    SORT_ORDER_ASCENDING = "ASC"
    SORT_ORDER_DESCENDING = "DESC"

    @abc.abstractmethod
    def add(self, address: str, transfer: Transfer) -> None:
        """
        Add a new transfer to account history in repository

        :param address: Account address
        :param transfer: Transfer instance
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def set_history(self, address: str, transfers: List[Transfer]) -> None:
        """
        Set account transfers history in repository

        :param address: Account address
        :param transfers: List of Transfer instances
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def list(
        self,
        address: str,
        filters: Optional[Dict[str, Any]] = None,
        sort_column: str = COLUMN_TIMESTAMP,
        sort_order: str = SORT_ORDER_DESCENDING,
        limit: int = 10,
        offset: int = 0,
    ) -> List[Transfer]:
        """
        List transfers from and to address, from repository with optional filters and sort_column

        :param address: Account address
        :param filters: Dict with {column: value} filters or None
        :param sort_column: Sort column constant, default to COLUMN_TIMESTAMP
        :param sort_order: Sort order constant SORT_ORDER_ASCENDING or SORT_ORDER_DESCENDING
        :param limit: Number of rows to return
        :param offset: Offset of first row to return
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def delete(self, transfer_id: str) -> None:
        """
        Delete transfer with transfer_id in repository

        :param transfer_id: Transfer ID to delete
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def delete_all(self) -> None:
        """
        Delete all transfers in repository

        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def count(self, address) -> int:
        """
        Return total number of transfers issued and received by address

        :return:
        """
        raise NotImplementedError
