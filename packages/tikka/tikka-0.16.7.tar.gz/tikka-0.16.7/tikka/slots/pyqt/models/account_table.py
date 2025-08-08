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
from __future__ import annotations

from typing import Any, List, Optional

from PyQt5.QtCore import QAbstractItemModel, QLocale, QModelIndex, Qt, QVariant
from PyQt5.QtGui import QFont, QIcon, QPixmap

from tikka.domains.application import Application
from tikka.domains.entities.account import Account
from tikka.domains.entities.constants import AMOUNT_UNIT_KEY
from tikka.domains.entities.identity import IdentityStatus
from tikka.domains.entities.smith import SmithStatus
from tikka.interfaces.adapters.repository.accounts import AccountsRepositoryInterface
from tikka.interfaces.adapters.repository.categories import (
    CategoriesRepositoryInterface,
)
from tikka.interfaces.adapters.repository.identities import (
    IdentitiesRepositoryInterface,
)
from tikka.slots.pyqt.entities.constants import (
    ACCOUNTS_TABLE_CATEGORY_FILTER_PREFERENCES_KEY,
    ACCOUNTS_TABLE_SORT_COLUMN_PREFERENCES_KEY,
    ACCOUNTS_TABLE_SORT_ORDER_PREFERENCES_KEY,
    ACCOUNTS_TABLE_WALLET_FILTER_PREFERENCES_KEY,
    ADDRESS_MONOSPACE_FONT_NAME,
    ICON_ACCOUNT_NO_WALLET,
    ICON_ACCOUNT_WALLET_LOCKED,
    ICON_ACCOUNT_WALLET_UNLOCKED,
    ICON_IDENTITY_MEMBER,
    ICON_IDENTITY_MEMBER_NOT_VALIDATED,
    ICON_IDENTITY_NOT_MEMBER,
    ICON_SMITH,
    SELECTED_UNIT_PREFERENCES_KEY,
)

BalanceStyledRole = Qt.UserRole + 1001


class AccountTableModel(QAbstractItemModel):
    """
    AccountTableModel class that drives the population of table display
    """

    REPOSITORY_COLUMNS = [
        "",
        IdentitiesRepositoryInterface.COLUMN_NAME,
        AccountsRepositoryInterface.COLUMN_NAME,
        AccountsRepositoryInterface.COLUMN_BALANCE,
        AccountsRepositoryInterface.COLUMN_ADDRESS,
        AccountsRepositoryInterface.COLUMN_PATH,
        AccountsRepositoryInterface.COLUMN_ROOT,
        AccountsRepositoryInterface.COLUMN_CRYPTO_TYPE,
        AccountsRepositoryInterface.COLUMN_LEGACY_V1,
        CategoriesRepositoryInterface.COLUMN_NAME,
    ]

    def __init__(self, application: Application, locale: QLocale):
        super().__init__()

        self.application = application
        self._ = self.application.translator.gettext
        # get parent widget locale to localize balance display
        self.locale = locale

        self.display_identity_icon = {
            IdentityStatus.UNCONFIRMED.value: QPixmap(
                ICON_IDENTITY_MEMBER_NOT_VALIDATED
            ),
            IdentityStatus.UNVALIDATED.value: QPixmap(
                ICON_IDENTITY_MEMBER_NOT_VALIDATED
            ),
            IdentityStatus.MEMBER.value: QPixmap(ICON_IDENTITY_MEMBER),
            IdentityStatus.NOT_MEMBER.value: QPixmap(ICON_IDENTITY_NOT_MEMBER),
            IdentityStatus.REVOKED.value: QPixmap(ICON_IDENTITY_NOT_MEMBER),
        }

        # calculate balance display by unit preference
        unit_preference = self.application.repository.preferences.get(
            SELECTED_UNIT_PREFERENCES_KEY
        )
        if unit_preference is not None:
            self.amount = self.application.amounts.get_amount(unit_preference)
        else:
            self.amount = self.application.amounts.get_amount(AMOUNT_UNIT_KEY)

        # drag and drop mime-type
        self.mime_type = "application/vnd.text.list"

        # Number of column displayed, see self.data()
        self._column_count = len(AccountTableModel.REPOSITORY_COLUMNS)

        self.table_view_data: List[AccountsRepositoryInterface.TableViewRow] = []

        self.init_data()

    def init_data(self):
        """
        Fill data from repository

        :return:
        """
        # calculate balance display by unit preference
        unit_preference = self.application.repository.preferences.get(
            SELECTED_UNIT_PREFERENCES_KEY
        )
        if unit_preference is not None:
            self.amount = self.application.amounts.get_amount(unit_preference)
        else:
            self.amount = self.application.amounts.get_amount(AMOUNT_UNIT_KEY)

        sort_column_index = self.application.repository.preferences.get(
            ACCOUNTS_TABLE_SORT_COLUMN_PREFERENCES_KEY
        )
        if sort_column_index is not None:
            sort_column_index = int(sort_column_index)
        repository_sort_order = self.application.repository.preferences.get(
            ACCOUNTS_TABLE_SORT_ORDER_PREFERENCES_KEY
        )

        filters = {}
        category_id_filter = self.application.repository.preferences.get(
            ACCOUNTS_TABLE_CATEGORY_FILTER_PREFERENCES_KEY
        )
        if category_id_filter is not None:
            filters[
                AccountsRepositoryInterface.TABLE_VIEW_FILTER_BY_CATEGORY_ID
            ] = category_id_filter

        wallet_filter_preference = self.application.repository.preferences.get(
            ACCOUNTS_TABLE_WALLET_FILTER_PREFERENCES_KEY
        )
        if wallet_filter_preference is not None:
            # preference store boolean as integer in a string column ("0" or "1")
            # convert it to boolean
            wallet_filter = int(wallet_filter_preference) == 1
            filters[
                AccountsRepositoryInterface.TABLE_VIEW_FILTER_BY_WALLET
            ] = wallet_filter

        if len(filters) == 0:
            filters = None

        self.beginResetModel()
        self.table_view_data = self.application.accounts.repository.table_view(
            filters,
            sort_column_index=sort_column_index,
            sort_order=repository_sort_order,
        )
        self.endResetModel()

    def rowCount(
        self, parent: QModelIndex = QModelIndex()  # pylint: disable=unused-argument
    ) -> int:
        """
        Return row count from account list

        :param parent: QModelIndex instance
        :return:
        """
        return len(self.table_view_data)

    def columnCount(
        self, parent: QModelIndex = QModelIndex()  # pylint: disable=unused-argument
    ) -> int:
        """
        Return column count of parent QModelIndex

        :param parent: QModelIndex instance
        :return:
        """
        return self._column_count

    def index(
        self, row: int, column: int, parent: QModelIndex = QModelIndex()
    ) -> QModelIndex:
        """
        Return QModelIndex for row, column and parent

        :param row: Row index
        :param column: Column index
        :param parent: Parent QModelIndex instance
        :return:
        """
        if not QAbstractItemModel.hasIndex(self, row, column, parent):
            return QModelIndex()

        if row < len(self.table_view_data):
            return QAbstractItemModel.createIndex(
                self, row, column, self.table_view_data[row]
            )

        return QModelIndex()

    def parent(
        self, child: Optional[QModelIndex] = None
    ):  # pylint: disable=unused-argument
        """
        Return parent QModelIndex of child QModelIndex

        :param child: QModelIndex instance
        :return:
        """
        return QModelIndex()

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> Any:
        """
        Return data of cell for column index.column

        :param index: QModelIndex instance
        :param role: Item data role
        :return:
        """
        data = QVariant()
        if not index.isValid():
            return data

        table_view_row = self.table_view_data[index.row()]

        if role == Qt.FontRole:
            font = QFont()
            # display addresses in monospace font
            if index.column() == AccountTableModel.REPOSITORY_COLUMNS.index(
                AccountsRepositoryInterface.COLUMN_ADDRESS
            ) or index.column() == AccountTableModel.REPOSITORY_COLUMNS.index(
                AccountsRepositoryInterface.COLUMN_ROOT
            ):
                font = QFont(ADDRESS_MONOSPACE_FONT_NAME)
                # if font is not found, choose equivalent monospace font on system
                font.setStyleHint(QFont.Monospace)

            # display root accounts with underline
            if table_view_row.root is None:
                font.setUnderline(True)

            return QVariant(font)

        # align right for balance column
        if (
            role == Qt.TextAlignmentRole
            and index.column()
            == AccountTableModel.REPOSITORY_COLUMNS.index(
                AccountsRepositoryInterface.COLUMN_BALANCE
            )
        ):
            return Qt.AlignRight

        # display account properties
        # display wallet lock status icon for account in first column
        if (
            index.column() == AccountTableModel.REPOSITORY_COLUMNS.index("")
            and role == Qt.DecorationRole
        ):
            if (
                table_view_row.wallet_address is not None
                and self.application.wallets.exists(table_view_row.wallet_address)
            ):
                data = (
                    QVariant(QIcon(QPixmap(ICON_ACCOUNT_WALLET_UNLOCKED)))
                    if self.application.wallets.is_unlocked(
                        table_view_row.wallet_address
                    )
                    else QVariant(QIcon(QPixmap(ICON_ACCOUNT_WALLET_LOCKED)))
                )
            else:
                data = QVariant(QIcon(QPixmap(ICON_ACCOUNT_NO_WALLET)))
        elif index.column() == AccountTableModel.REPOSITORY_COLUMNS.index(
            IdentitiesRepositoryInterface.COLUMN_NAME
        ):
            identity = self.application.identities.get_by_address(
                table_view_row.address
            )
            if identity is not None:
                if role == Qt.DecorationRole:
                    smith = self.application.smiths.get(identity.index)
                    if smith is not None and smith.status == SmithStatus.SMITH:
                        data = QVariant(
                            QPixmap(ICON_SMITH).scaled(
                                16, 18, aspectRatioMode=Qt.KeepAspectRatio
                            )
                        )
                    else:
                        data = QVariant(
                            self.display_identity_icon[identity.status.value].scaled(
                                16, 18, aspectRatioMode=Qt.KeepAspectRatio
                            )
                        )
                if role == Qt.DisplayRole:
                    if identity.name is not None:
                        data = QVariant(f"{identity.name}#{identity.index}")
                    else:
                        data = QVariant(f"#{identity.index}")

        elif (
            index.column()
            == AccountTableModel.REPOSITORY_COLUMNS.index(
                AccountsRepositoryInterface.COLUMN_BALANCE
            )
            and role == BalanceStyledRole
            and table_view_row.balance is not None
        ):
            data = QVariant(
                self.locale.toString(self.amount.value(table_view_row.balance), "f", 2)
            )
        elif index.column() == AccountTableModel.REPOSITORY_COLUMNS.index(
            AccountsRepositoryInterface.COLUMN_NAME
        ) and role in (Qt.DisplayRole, Qt.EditRole):
            data = QVariant(table_view_row.name)
        elif (
            index.column()
            == AccountTableModel.REPOSITORY_COLUMNS.index(
                AccountsRepositoryInterface.COLUMN_ADDRESS
            )
            and role == Qt.DisplayRole
        ):
            data = QVariant(table_view_row.address)
        elif (
            index.column()
            == AccountTableModel.REPOSITORY_COLUMNS.index(
                AccountsRepositoryInterface.COLUMN_PATH
            )
            and role == Qt.DisplayRole
        ):
            data = QVariant(table_view_row.path)
        elif (
            index.column()
            == AccountTableModel.REPOSITORY_COLUMNS.index(
                AccountsRepositoryInterface.COLUMN_ROOT
            )
            and role == Qt.DisplayRole
            and table_view_row.root is not None
        ):
            data = QVariant(table_view_row.root)
        elif (
            index.column()
            == AccountTableModel.REPOSITORY_COLUMNS.index(
                AccountsRepositoryInterface.COLUMN_CRYPTO_TYPE
            )
            and role == Qt.DisplayRole
        ):
            data = (
                QVariant("SR25519")
                if table_view_row.crypto_type == 1
                else QVariant("ED25519")
            )
        elif (
            index.column()
            == AccountTableModel.REPOSITORY_COLUMNS.index(
                AccountsRepositoryInterface.COLUMN_LEGACY_V1
            )
            and role == Qt.DisplayRole
            and table_view_row.legacy_v1 is True
        ):
            data = QVariant(
                Account(table_view_row.address).get_v1_address(
                    self.application.currencies.get_current().ss58_format
                )
            )
        elif (
            index.column()
            == AccountTableModel.REPOSITORY_COLUMNS.index(
                CategoriesRepositoryInterface.COLUMN_NAME
            )
            and role == Qt.DisplayRole
        ):
            data = (
                QVariant(table_view_row.category_name)
                if table_view_row.category_name is not None
                else QVariant()
            )

        return data

    def headerData(
        self,
        section: int,
        orientation: Qt.Orientation,  # pylint: disable=unused-argument
        role: int = Qt.DisplayRole,
    ) -> QVariant:
        """
        Return header data

        :param section: Section offset
        :param orientation: Qt Orientation flag
        :param role: Qt Role flag
        :return:
        """
        data = QVariant()
        if (
            section == AccountTableModel.REPOSITORY_COLUMNS.index("")
            and role == Qt.DisplayRole
        ):
            data = QVariant(self._("Wallet"))
        elif (
            section
            == AccountTableModel.REPOSITORY_COLUMNS.index(
                IdentitiesRepositoryInterface.COLUMN_NAME
            )
            and role == Qt.DisplayRole
        ):
            data = QVariant(self._("Identity"))
        elif (
            section
            == AccountTableModel.REPOSITORY_COLUMNS.index(
                AccountsRepositoryInterface.COLUMN_BALANCE
            )
            and role == Qt.DisplayRole
        ):
            data = QVariant(
                self._("Balance ({symbol})").format(symbol=self.amount.symbol())
            )
        elif (
            section
            == AccountTableModel.REPOSITORY_COLUMNS.index(
                AccountsRepositoryInterface.COLUMN_NAME
            )
            and role == Qt.DisplayRole
        ):
            data = QVariant(self._("Name"))
        elif (
            section
            == AccountTableModel.REPOSITORY_COLUMNS.index(
                AccountsRepositoryInterface.COLUMN_ADDRESS
            )
            and role == Qt.DisplayRole
        ):
            data = QVariant(self._("Address"))
        elif (
            section
            == AccountTableModel.REPOSITORY_COLUMNS.index(
                AccountsRepositoryInterface.COLUMN_PATH
            )
            and role == Qt.DisplayRole
        ):
            data = QVariant(self._("Derivation"))
        elif (
            section
            == AccountTableModel.REPOSITORY_COLUMNS.index(
                AccountsRepositoryInterface.COLUMN_ROOT
            )
            and role == Qt.DisplayRole
        ):
            data = QVariant(self._("Root"))
        elif (
            section
            == AccountTableModel.REPOSITORY_COLUMNS.index(
                AccountsRepositoryInterface.COLUMN_CRYPTO_TYPE
            )
            and role == Qt.DisplayRole
        ):
            data = QVariant(self._("Crypto"))
        elif (
            section
            == AccountTableModel.REPOSITORY_COLUMNS.index(
                AccountsRepositoryInterface.COLUMN_LEGACY_V1
            )
            and role == Qt.DisplayRole
        ):
            data = QVariant(self._("V1 Address"))
        elif (
            section
            == AccountTableModel.REPOSITORY_COLUMNS.index(
                CategoriesRepositoryInterface.COLUMN_NAME
            )
            and role == Qt.DisplayRole
        ):
            data = QVariant(self._("Category"))

        return data

    def sort(self, column: int, order: Optional[Qt.SortOrder] = None) -> None:
        """
        Sort by column number in order

        :param column: Column index
        :param order: Qt.SortOrder flag
        :return:
        """
        if column > -1:
            sort_order = (
                AccountsRepositoryInterface.SORT_ORDER_ASCENDING
                if order == Qt.AscendingOrder
                else AccountsRepositoryInterface.SORT_ORDER_DESCENDING
            )
            self.application.repository.preferences.set(
                ACCOUNTS_TABLE_SORT_COLUMN_PREFERENCES_KEY, str(column)
            )
            self.application.repository.preferences.set(
                ACCOUNTS_TABLE_SORT_ORDER_PREFERENCES_KEY, sort_order
            )
            self.init_data()
