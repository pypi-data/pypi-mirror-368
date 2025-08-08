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
from typing import List

from PyQt5.QtCore import (
    QAbstractItemModel,
    QAbstractListModel,
    QLocale,
    QModelIndex,
    QSize,
    Qt,
    QVariant,
)
from PyQt5.QtGui import QPainter, QPalette
from PyQt5.QtWidgets import QStyle, QStyledItemDelegate, QStyleOptionViewItem

from tikka.domains.application import Application
from tikka.domains.entities.constants import AMOUNT_UNIT_KEY
from tikka.domains.entities.transfer import Transfer
from tikka.interfaces.adapters.repository.transfers import TransfersRepositoryInterface
from tikka.slots.pyqt.entities.constants import SELECTED_UNIT_PREFERENCES_KEY
from tikka.slots.pyqt.widgets.account_transfer_row import AccountTransferRowWidget


class TransferItemDelegate(QStyledItemDelegate):
    """
    TransferItemDelegate class
    """

    def __init__(self):
        """
        Init TransferItemDelegate instance
        """
        super().__init__()

        # set item height >= AccountTransferRowWidget.height
        self.item_height = 71

    def sizeHint(self, option: QStyleOptionViewItem, index: QModelIndex):
        """
        Return item size

        Force height

        :param option: QStyleOptionViewItem instance
        :param index: QModelIndex instance
        :return:
        """
        return QSize(option.rect.width(), self.item_height)

    def paint(
        self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex
    ) -> None:
        """
        Draw transfer row item in listview

        :param painter: QPainter instance
        :param option: QStyleOptionViewItem instance
        :param index: QModelIndex instance
        :return:
        """
        # Init style option
        style_option = QStyleOptionViewItem(option)
        self.initStyleOption(style_option, index)

        account_address_label = index.data(TransfersListModel.AccountAddressLabelRole)
        account_name_label = index.data(TransfersListModel.AccountNameRole)
        identity_name_label = index.data(TransfersListModel.IdentityNameRole)
        account_has_identity = index.data(TransfersListModel.AccountHasIdentityRole)
        datetime_label = index.data(TransfersListModel.DatetimeLabelRole)
        comment_type = index.data(TransfersListModel.CommentTypeRole)
        comment_label = index.data(TransfersListModel.CommentLabelRole)
        amount_label = index.data(TransfersListModel.AmountLabelRole)

        """ Replace item row by the widget """
        widget = AccountTransferRowWidget(
            account_address_label,
            account_name_label,
            identity_name_label,
            account_has_identity,
            datetime_label,
            amount_label,
            comment_label,
            comment_type,
        )  # Crée le widget

        # set widget background
        # widget.setAutoFillBackground(True)

        # Modify widget palette depending on behavior (hover, selection)
        palette = widget.palette()

        # 🔹 Check if the line number is even (alternate color effect)
        if index.row() % 2 == 1:  # Even lines use AlternateBase color
            base_color = option.palette.color(QPalette.AlternateBase)
        else:
            base_color = option.palette.color(QPalette.Base)

        if option.state & QStyle.State_Selected:
            palette.setColor(
                QPalette.Window, option.palette.highlight().color()
            )  # selection color
        elif option.state & QStyle.State_MouseOver:
            palette.setColor(
                QPalette.Window, option.palette.color(QPalette.Highlight).lighter(200)
            )  # Hover
        else:
            palette.setColor(
                QPalette.Window, base_color
            )  # normal or alternate background

        widget.setPalette(palette)  # Apply palette on widget
        widget.update()  # 🔥 Force display of new colors

        widget.resize(option.rect.size())  # Set size to the row size
        painter.save()
        painter.translate(option.rect.topLeft())  # Place the widget correctly
        widget.render(painter)
        painter.restore()


class TransfersListModel(QAbstractListModel):
    """
    TransfersListModel class that drives the population of list display
    """

    (
        AccountAddressLabelRole,
        AccountHasIdentityRole,
        AccountNameRole,
        IdentityNameRole,
        DatetimeLabelRole,
        CommentLabelRole,
        CommentTypeRole,
        AmountLabelRole,
    ) = range(Qt.UserRole, Qt.UserRole + 8)

    def __init__(self, application: Application, address: str, locale: QLocale):
        """
        Init TransfersListModel with account address to get account transfers list


        :param application: Application instance
        :param address: Account address
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

        self.address = address
        self.transfers: List[Transfer] = []

    def init_data(self, offset: int = 0, limit: int = 10):
        """
        Fill data from repository

        :param offset: Offset in DB list to paginate
        :param limit: Limit page size
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
        self.transfers = self.application.transfers.repository.list(
            self.address,
            offset=offset,
            limit=limit,
            sort_column=TransfersRepositoryInterface.COLUMN_TIMESTAMP,
            sort_order=TransfersRepositoryInterface.SORT_ORDER_DESCENDING,
        )
        self.endResetModel()

    def rowCount(self, _: QModelIndex = QModelIndex()) -> int:
        """
        Return row count

        :param _: QModelIndex instance
        :return:
        """
        return len(self.transfers)

    def index(  # type: ignore
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

        if row < len(self.transfers):
            return QAbstractItemModel.createIndex(
                self, row, column, self.transfers[row]
            )

        return QModelIndex()

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole) -> QVariant:
        """
        Return data of cell for column index.column

        :param index: QModelIndex instance
        :param role: Item data role
        :return:
        """
        row = index.row()
        transfer = self.transfers[row]
        data = QVariant()

        if role == self.AccountAddressLabelRole:
            # return address issuer
            if transfer.issuer_address != self.address:
                return QVariant(
                    f"{transfer.issuer_address[:4]}…{transfer.issuer_address[-5:]}"
                )
            else:
                return QVariant(
                    f"{transfer.receiver_address[:4]}…{transfer.receiver_address[-5:]}"
                )

        if role == self.AccountHasIdentityRole:
            if transfer.issuer_address != self.address:
                return QVariant(transfer.issuer_identity_index is not None)
            else:
                return QVariant(transfer.receiver_identity_index is not None)

        if role == self.AccountNameRole:
            # return transfer received
            if transfer.issuer_address != self.address:
                account = self.application.accounts.get_by_address(
                    transfer.issuer_address
                )
                if account is not None and account.name is not None:
                    return QVariant(account.name)
                else:
                    return QVariant()

            # display transfer issued
            else:
                account = self.application.accounts.get_by_address(
                    transfer.receiver_address
                )
                if account is not None and account.name is not None:
                    return QVariant(account.name)
                else:
                    return QVariant()

        if role == self.IdentityNameRole:

            # return transfer received
            if transfer.issuer_address != self.address:
                if transfer.issuer_identity_index is not None:
                    return QVariant(
                        f"{transfer.issuer_identity_name}#{transfer.issuer_identity_index}"
                    )
                else:
                    return QVariant()

            # display transfer issued
            else:
                if transfer.receiver_identity_index is not None:
                    return QVariant(
                        f"{transfer.receiver_identity_name}#{transfer.receiver_identity_index}"
                    )
                else:
                    return QVariant()

        if role == self.DatetimeLabelRole:
            # datetime
            datetime_label = self.locale.toString(
                transfer.timestamp.astimezone(),
                QLocale.dateTimeFormat(self.locale, QLocale.ShortFormat),
            )
            return QVariant(datetime_label)

        if role == self.CommentTypeRole:
            return QVariant(transfer.comment_type)

        if role == self.CommentLabelRole:
            # comment
            comment_label = ""
            if transfer.comment is not None:
                if (
                    transfer.comment_type == "ASCII"
                    or transfer.comment_type == "UNICODE"
                ):
                    comment_label = transfer.comment
                elif transfer.comment_type == "RAW":
                    comment_label = (
                        f"RAW:{transfer.comment[:min(len(transfer.comment),10)]}..."
                        f"{transfer.comment[max(-len(transfer.comment),-10):]}"
                    )
                elif transfer.comment_type == "CID":
                    comment_label = f"CID:{transfer.comment}"

            return QVariant(comment_label)

        if role == self.AmountLabelRole:
            # display transfer received
            if transfer.issuer_address != self.address:
                amount_sign = ""
            else:
                amount_sign = "-"
            # amount
            amount = self.locale.toCurrencyString(
                self.amount.value(transfer.amount), self.amount.symbol()
            )
            return QVariant(f"{amount_sign}{amount}")

        return data
