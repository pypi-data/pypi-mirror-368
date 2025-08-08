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
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from tikka.domains.entities.account import Account


class AccountsRepositoryInterface(abc.ABC):
    """
    AccountRepositoryInterface class
    """

    COLUMN_ADDRESS = "account_address"
    COLUMN_NAME = "account_name"
    COLUMN_CRYPTO_TYPE = "account_crypto_type"
    COLUMN_BALANCE = "account_balance"
    COLUMN_PATH = "account_path"
    COLUMN_ROOT = "account_root"
    COLUMN_FILE_IMPORT = "account_file_import"
    COLUMN_CATEGORY_ID = "account_category_id"
    COLUMN_LEGACY_V1 = "account_legacy_v1"
    COLUMN_TOTAL_TRANSFERS_COUNT = "account_total_transfers_count"

    SORT_ORDER_ASCENDING = "ASC"
    SORT_ORDER_DESCENDING = "DESC"

    TABLE_VIEW_FILTER_BY_CATEGORY_ID = "table_view_filter_category_id"
    TABLE_VIEW_FILTER_BY_WALLET = "table_view_filter_wallet"

    @dataclass
    class TableViewRow:
        wallet_address: Optional[str]
        identity_index: Optional[int]
        identity_name: Optional[str]
        balance: Optional[int]
        name: Optional[str]
        address: str
        path: Optional[str]
        root: Optional[str]
        crypto_type: int
        legacy_v1: bool
        category_name: Optional[str]

    @abc.abstractmethod
    def add(self, account: Account) -> None:
        """
        Add a new account in repository

        :param account: Account instance
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def list(
        self,
        filters: Optional[Dict[str, Any]] = None,
        sort_column: Optional[str] = None,
        sort_order: str = SORT_ORDER_ASCENDING,
    ) -> List[Account]:
        """
        List accounts from repository with optional filters and sort_column

        :param filters: Dict with {column: value} filters or None
        :param sort_column: Sort column constant like COLUMN_ADDRESS or None
        :param sort_order: Sort order constant SORT_ORDER_ASCENDING or SORT_ORDER_DESCENDING
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def table_view(
        self,
        filters: Optional[Dict[str, Any]] = None,
        sort_column_index: Optional[int] = None,
        sort_order: str = SORT_ORDER_ASCENDING,
    ) -> List[TableViewRow]:
        """
        List accounts from repository with optional filters and sort_column

        :param filters: Dict with {column: value} filters or None
        :param sort_column_index: Sort column index or None
        :param sort_order: Sort order constant SORT_ORDER_ASCENDING or SORT_ORDER_DESCENDING
        :return:
        """
        raise NotImplementedError

    def update(self, account: Account) -> None:
        """
        Update account in repository

        :param account: Account instance
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def delete(self, address: str) -> None:
        """
        Delete account with address in repository

        :param address: Account address
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def delete_all(self) -> None:
        """
        Delete all accounts

        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def count(self) -> int:
        """
        Return total number of accounts

        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def total_balance(self) -> int:
        """
        Return total sum of all account balances

        :return:
        """
        raise NotImplementedError
