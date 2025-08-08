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

import pickle
from typing import Any, Iterable, List, Optional, Tuple, Type, Union
from uuid import UUID

from PyQt5.QtCore import (
    QAbstractItemModel,
    QLocale,
    QMimeData,
    QModelIndex,
    Qt,
    QVariant,
)
from PyQt5.QtGui import QColor, QFont, QPixmap

from tikka.domains.application import Application
from tikka.domains.entities.account import Account
from tikka.domains.entities.category import Category
from tikka.domains.entities.constants import AMOUNT_UNIT_KEY
from tikka.domains.entities.identity import IdentityStatus
from tikka.domains.entities.smith import SmithStatus
from tikka.slots.pyqt.entities.constants import (
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

WalletLockStatusRole = Qt.UserRole + 1000
BalanceStyledRole = Qt.UserRole + 1001


class TreeItem:
    def __init__(
        self, element: Optional[Union[Category, Account]], parent: Optional[TreeItem]
    ) -> None:
        """
        Init TreeItem instance with element and parent

        :param element: Category or Account instance
        :param parent: TreeItem instance
        """
        self.element = element
        self._children: List[TreeItem] = []
        self._parent = parent
        self._row = 0

    def child_count(self):
        """
        Return number of children

        :return:
        """
        return len(self._children)

    def child(self, row) -> Optional[TreeItem]:
        """
        Return child at row

        :param row: Row number
        :return:
        """
        if 0 <= row < self.child_count():
            return self._children[row]
        return None

    def parent(self) -> Optional[TreeItem]:
        """
        Return parent

        :return:
        """
        return self._parent

    def row(self):
        """
        Return row number in parent's children

        :return:
        """
        return self._row

    def insert_child(self, position: int, child: TreeItem) -> bool:
        """
        Insert child at position row

        :param position: Row to insert child
        :param child: TreeItem instance
        :return:
        """
        self._children.insert(position, child)
        return True

    def add_child(self, child: TreeItem) -> None:
        """
        Add a child to item

        :param child: TreeItem instance
        :return:
        """
        child.set_parent(self)
        child.set_row(len(self._children))
        self._children.append(child)

    def set_parent(self, parent: TreeItem) -> None:
        """
        Set parent item

        :param parent: TreeItem instance
        :return:
        """
        self._parent = parent

    def set_row(self, row: int) -> None:
        """
        Set row value

        :param row: Row value
        :return:
        """
        self._row = row


class AccountTreeModel(QAbstractItemModel):
    """
    AccountTreeModel class that drives the population of tree display
    """

    def __init__(self, application: Application, locale: QLocale):
        """
        Init AccountTreeModel

        :param application: Application instance
        :param locale: QLocale instance
        """
        super().__init__()

        self.application = application
        self._ = self.application.translator.gettext

        # get parent widget locale to localize balance display
        self.locale = locale

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
        self._column_count = 4

        self.root_item = TreeItem(None, None)
        self.categories: List[Category] = []
        self.accounts: List[Account] = []

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

        self.beginResetModel()
        self.root_item = TreeItem(None, None)
        self.categories = self.application.categories.list_all()
        self.accounts = self.application.accounts.get_list()
        self.recursive_append_children(None, self.root_item)
        self.endResetModel()

    def account_list_by_category_id(self, category_id: Optional[UUID]) -> List[Account]:
        """
        Return all accounts in category_id

        :param category_id: Category ID
        :return:
        """
        result = []
        for account in self.accounts:
            # do not list derived accounts
            if account.category_id is None and account.root is not None:
                continue
            if account.category_id == category_id:
                result.append(account)

        return result

    def category_children(self, category_id: Optional[UUID]) -> List[Category]:
        """
        Return categories with parent category_id

        :param category_id: Parent category ID
        :return:
        """
        return [
            category
            for category in self.categories
            if category.parent_id == category_id
        ]

    def get_derivation_accounts(self, address: str) -> List[Account]:
        """
        Return derived accounts from root address

        :param address: Root account address
        :return:
        """
        return sorted(
            [account for account in self.accounts if account.root == address],
            key=lambda account: account.path,  # type: ignore
        )

    def recursive_append_children(
        self, element: Optional[Union[Category, Account]], item: TreeItem
    ) -> int:
        """
        Add children items from element to item

        :param element: Account or Category instance or None
        :param item: TreeItem instance
        :return:
        """
        children_balance = 0
        if element is None or isinstance(element, Category):
            parent_category_id = None if element is None else element.id

            # list of categories in category
            for category in self.category_children(parent_category_id):
                category_item = TreeItem(category, self.root_item)
                item.add_child(category_item)
                children_balance += self.recursive_append_children(
                    category, category_item
                )

            # list of accounts in category
            for account in self.account_list_by_category_id(parent_category_id):
                account_item = TreeItem(account, item)
                item.add_child(account_item)
                children_balance += self.recursive_append_children(
                    account, account_item
                )
                if account.balance is not None:
                    children_balance += account.balance

        elif isinstance(element, Account):
            # list of derivation from this account
            for account in self.get_derivation_accounts(element.address):
                if account.balance is not None:
                    children_balance += account.balance
                account_item = TreeItem(account, item)
                item.add_child(account_item)

        if isinstance(element, Category):
            element.balance = children_balance

        return children_balance

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
        if not parent or not parent.isValid():
            parent_item = self.root_item
        else:
            parent_item = parent.internalPointer()

        if not QAbstractItemModel.hasIndex(self, row, column, parent):
            return QModelIndex()

        child_item = parent_item.child(row)
        if child_item:
            return QAbstractItemModel.createIndex(self, row, column, child_item)

        return QModelIndex()

    def parent(self, child: QModelIndex) -> QModelIndex:  # type: ignore
        """
        Return parent QModelIndex of child QModelIndex

        :param child: QModelIndex instance
        :return:
        """
        if child.isValid():
            parent_item = child.internalPointer().parent()
            if parent_item:
                return QAbstractItemModel.createIndex(
                    self, parent_item.row(), 0, parent_item
                )
        return QModelIndex()

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        """
        Return row count of parent QModelIndex

        :param parent: QModelIndex instance
        :return:
        """
        if parent.isValid():
            return parent.internalPointer().child_count()
        return self.root_item.child_count()

    def columnCount(
        self, parent: QModelIndex = QModelIndex()  # pylint: disable=unused-argument
    ) -> int:
        """
        Return column count of parent QModelIndex

        :param parent: QModelIndex instance
        :return:
        """
        return self._column_count

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> QVariant:
        """
        Return data of cell for column index.column

        :param index: QModelIndex instance
        :param role: Item data role
        :return:
        """
        data = QVariant()
        if not index.isValid():
            return data

        tree_item = index.internalPointer()
        # display account address or name or identity name#index or category name in first column
        # only this column is indented
        if index.column() == 0 and role in (Qt.DisplayRole, Qt.EditRole):
            if isinstance(tree_item.element, Account):
                if tree_item.element.name is None:
                    identity = self.application.identities.get_by_address(
                        tree_item.element.address
                    )
                    if identity is not None:
                        if identity.name is not None:
                            data = QVariant(f"{identity.name}#{identity.index}")
                        else:
                            data = QVariant(f"#{identity.index}")
                else:
                    data = QVariant(tree_item.element.name)
            else:
                # category name
                data = QVariant(tree_item.element.name)

        # display wallet lock status icon for account in first column
        if (
            index.column() == 0
            and role == WalletLockStatusRole
            and isinstance(tree_item.element, Account)
        ):
            if self.application.wallets.exists(tree_item.element.address):
                data = (
                    QVariant(
                        QPixmap(ICON_ACCOUNT_WALLET_UNLOCKED).scaled(
                            16,
                            18,
                            aspectRatioMode=Qt.KeepAspectRatio,
                            transformMode=Qt.SmoothTransformation,
                        )
                    )
                    if self.application.wallets.is_unlocked(tree_item.element.address)
                    else QVariant(
                        QPixmap(ICON_ACCOUNT_WALLET_LOCKED).scaled(
                            16,
                            18,
                            aspectRatioMode=Qt.KeepAspectRatio,
                            transformMode=Qt.SmoothTransformation,
                        )
                    )
                )
            else:
                data = QVariant(
                    QPixmap(ICON_ACCOUNT_NO_WALLET).scaled(
                        16,
                        18,
                        aspectRatioMode=Qt.KeepAspectRatio,
                        transformMode=Qt.SmoothTransformation,
                    )
                )

        # display icon of identity membership status
        if (
            index.column() == 0
            and role == Qt.DecorationRole
            and isinstance(tree_item.element, Account)
        ):
            identity = self.application.identities.get_by_address(
                tree_item.element.address
            )
            if identity is not None:
                data = QVariant(
                    self.display_identity_icon[identity.status.value].scaled(
                        16, 18, aspectRatioMode=Qt.KeepAspectRatio
                    )
                )
                smith = self.application.smiths.get(identity.index)
                if smith is not None and smith.status == SmithStatus.SMITH:
                    data = QVariant(
                        QPixmap(ICON_SMITH).scaled(
                            16, 18, aspectRatioMode=Qt.KeepAspectRatio
                        )
                    )

        # display account address
        if (
            index.column() == 1
            and role == Qt.DisplayRole
            and isinstance(tree_item.element, Account)
        ):
            data = QVariant(tree_item.element.address)
        if (
            index.column() == 1
            and role == Qt.ToolTipRole
            and isinstance(tree_item.element, Account)
            and tree_item.element.legacy_v1 is True
        ):
            data = QVariant(
                tree_item.element.get_v1_address(
                    self.application.currencies.get_current().ss58_format
                )
            )

        # font style
        if role == Qt.FontRole and isinstance(tree_item.element, Account):
            if index.column() == 1:
                # display addresses in monospace font
                font = QFont(ADDRESS_MONOSPACE_FONT_NAME)
                # if font is not found, choose equivalent monospace font on system
                font.setStyleHint(QFont.Monospace)
                # font.setBold(True)
                # display root account with underline
                if tree_item.element.root is None:
                    font.setUnderline(True)
            else:
                font = QFont()

            return QVariant(font)

        # display account derivation path
        if (
            index.column() == 2
            and role == Qt.DisplayRole
            and isinstance(tree_item.element, Account)
        ):
            if tree_item.element.path is not None:
                data = QVariant(tree_item.element.path)

        # display account balance
        if (
            index.column() == 3
            and role == BalanceStyledRole
            and tree_item.element.balance is not None
        ):
            data = QVariant(
                self.locale.toCurrencyString(
                    self.amount.value(tree_item.element.balance), self.amount.symbol()
                )
            )

        if role == Qt.TextColorRole and index.column() == 0:
            if isinstance(tree_item.element, Account):
                if tree_item.element.name is None:
                    identity = self.application.identities.get_by_address(
                        tree_item.element.address
                    )
                    if identity is not None:
                        data = QVariant(QColor("blue"))

        return data

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        """
        Return Qt.ItemFlags for index

        :param index: QModelIndex instance
        :return:
        """
        flags = super().flags(index)
        tree_item: TreeItem = index.internalPointer()

        if index.column() == 0:
            if isinstance(tree_item.element, Category):
                # category name is editable, can be dragged and dropped on
                return (
                    flags
                    | Qt.ItemIsEditable
                    | Qt.ItemIsDragEnabled
                    | Qt.ItemIsDropEnabled
                )
            # account can be dragged and dropped on
            return flags | Qt.ItemIsDragEnabled | Qt.ItemIsDropEnabled

        return flags

    def setData(self, index: QModelIndex, value: Any, role: int = 0) -> bool:
        """
        Set data after treeView editing

        :param index: QModelIndex instance
        :param value: Editor Value
        :param role: Role flag
        :return:
        """
        super().setData(index, role)

        tree_item: TreeItem = index.internalPointer()
        # if category name edited (not dropped where value is None)...
        if (
            role == Qt.EditRole
            and index.column() == 0
            and isinstance(tree_item.element, Category)
            and value is not None
        ):
            # update name
            tree_item.element.name = value
            # update repository
            self.application.categories.update(tree_item.element)

        self.dataChanged.emit(index, index)
        return True

    def insertRow(self, row: int, parent: QModelIndex = QModelIndex()) -> bool:
        """
        Insert row in parent index

        :param row: Index of row from 0 in parent children
        :param parent: QModelIndex instance
        :return:
        """
        self.beginInsertRows(parent, row, row)
        parent_item: TreeItem = parent.internalPointer()
        parent_id = None
        if parent_item is None:
            parent_item = self.root_item
        elif isinstance(parent_item.element, Category):
            parent_id = parent_item.element.id
        category = self.application.categories.create("", parent_id)
        success = parent_item.insert_child(row, TreeItem(category, parent_item))
        self.application.categories.repository.add(category)
        self.endInsertRows()
        return success

    def supportedDropActions(self):
        """
        Return supported drop action flags

        :return:
        """
        return Qt.MoveAction

    def mimeTypes(self) -> List[str]:
        """
        Return supported mime types for drag and drop

        :return:
        """
        return [self.mime_type]

    def mimeData(self, indexes: Iterable[QModelIndex]) -> QMimeData:
        """
        Return encoded mime-type values for indexes

        :param indexes: List of indexes
        :return:
        """
        sorted_indices = sorted(
            [index for index in indexes if index.isValid()],
            key=lambda index: index.row(),
        )

        data_list: List[Tuple[Union[Type[Category], Type[Account]], str]] = []
        for index in sorted_indices:
            if not index.isValid():
                continue
            if index.column() == 0:
                tree_item: TreeItem = index.internalPointer()
                if tree_item is None:
                    continue
                if isinstance(tree_item.element, Category):
                    data_list.append(
                        (tree_item.element.__class__, tree_item.element.id.hex)
                    )
                elif isinstance(tree_item.element, Account):
                    data_list.append(
                        (tree_item.element.__class__, tree_item.element.address)
                    )

        encoded_data = pickle.dumps(data_list)
        mime_data = QMimeData()
        mime_data.setData(self.mime_type, encoded_data)
        return mime_data

    def dropMimeData(
        self,
        data: QMimeData,
        action: Qt.DropAction,
        row: int,  # pylint: disable=unused-argument
        column: int,
        parent: QModelIndex,
    ) -> bool:
        """
        Handle dropped data

        :param data: QMimeData instance
        :param action: Action flag
        :param row: Row dropped on
        :param column: Column dropped on
        :param parent: QModelIndex instance
        :return:
        """
        if action == Qt.IgnoreAction:
            return True
        if not data.hasFormat(self.mime_type) or column > 0 or not parent.isValid():
            return False

        encoded_data = data.data(self.mime_type)
        decoded_data = pickle.loads(bytes(encoded_data))
        parent_tree_item: TreeItem = parent.internalPointer()

        # if dropped on no item or on item without element...
        if parent_tree_item is None or parent_tree_item.element is None:
            return False

        parent_category_id = None

        # if dropped on a category...
        if isinstance(parent_tree_item.element, Category):
            parent_category_id = parent_tree_item.element.id
        elif isinstance(parent_tree_item.element, Account):
            # if dropped on a derived account...
            if parent_tree_item.element.root is not None:
                # get root account category
                root_account = self.application.accounts.get_by_address(
                    parent_tree_item.element.root
                )
                if root_account is not None:
                    parent_category_id = root_account.category_id
                else:
                    return False
            else:
                # get root account category
                root_account = self.application.accounts.get_by_address(
                    parent_tree_item.element.address
                )
                if root_account is not None:
                    parent_category_id = root_account.category_id
                else:
                    return False

        for element_data in decoded_data:
            element_class, element_pk = element_data
            if element_class == Category:
                category = self.application.categories.get(UUID(hex=element_pk))
                if category is not None:
                    category.parent_id = parent_category_id
                    self.application.categories.repository.update(category)
            else:
                account = self.application.accounts.get_by_address(element_pk)
                if account is not None:
                    # if root account...
                    if account.root is None:
                        account.category_id = parent_category_id
                        self.application.accounts.repository.update(account)
                    else:
                        # get root account
                        root_account = self.application.accounts.get_by_address(
                            account.root
                        )
                        if root_account is not None:
                            root_account.category_id = parent_category_id
                            self.application.accounts.repository.update(root_account)
        return True
