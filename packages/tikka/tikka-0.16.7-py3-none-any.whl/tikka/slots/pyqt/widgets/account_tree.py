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
import logging
import sys
from typing import Optional

from PyQt5.QtCore import QModelIndex, QMutex, QPoint, QRect, Qt
from PyQt5.QtGui import QBrush, QColor, QFontMetrics, QPainter, QPixmap
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QStyledItemDelegate,
    QStyleOptionViewItem,
    QWidget,
)

from tikka.domains.application import Application
from tikka.domains.entities.account import Account
from tikka.domains.entities.category import Category
from tikka.domains.entities.constants import AMOUNT_UNIT_KEY, DATA_PATH
from tikka.domains.entities.events import (
    AccountEvent,
    CategoryEvent,
    CurrencyEvent,
    UnitEvent,
)
from tikka.slots.pyqt.entities.constants import (
    NUMERIC_DISPLAY_COLOR_BLUE,
    SELECTED_UNIT_PREFERENCES_KEY,
)
from tikka.slots.pyqt.entities.worker import AsyncQWorker
from tikka.slots.pyqt.models.account_tree import (
    AccountTreeModel,
    BalanceStyledRole,
    WalletLockStatusRole,
)
from tikka.slots.pyqt.resources.gui.widgets.account_tree_rc import Ui_AccountTreeWidget
from tikka.slots.pyqt.widgets.account_menu import AccountPopupMenu
from tikka.slots.pyqt.widgets.category_menu import CategoryPopupMenu


class AccountIconsItemDelegate(QStyledItemDelegate):
    """
    Class used to display member status icon for accounts
    """

    def paint(
        self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex
    ) -> None:
        """
        Draw member status icon and wallet lock status icon side by side

        :param painter: QPainter instance
        :param option: QStyleOptionViewItem instance
        :param index: QModelIndex instance
        :return:
        """
        if not index.isValid():
            return
        super().paint(painter, option, index)

        wallet_lock_status_pixmap = index.data(WalletLockStatusRole)
        if isinstance(wallet_lock_status_pixmap, QPixmap):
            icon_x = option.rect.x() - wallet_lock_status_pixmap.rect().width() - 2
            icon_y = (
                option.rect.y()
                + (option.rect.height() - wallet_lock_status_pixmap.height()) // 2
            )
            icon_rect = QRect(
                icon_x,
                icon_y,
                wallet_lock_status_pixmap.width(),
                wallet_lock_status_pixmap.height(),
            )
            painter.drawPixmap(icon_rect, wallet_lock_status_pixmap)


class StyledBalanceItemDelegate(QStyledItemDelegate):
    """
    Class used to display balance with a custom style
    """

    def paint(
        self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex
    ) -> None:
        """
        Return balance with a custom style

        :param painter: QPainter instance
        :param option: QStyleOptionViewItem instance
        :param index: QModelIndex instance
        :return:
        """
        if not index.isValid():
            return
        super().paint(painter, option, index)

        # draw balance with style
        balance_styled: str = index.data(BalanceStyledRole)
        if balance_styled:
            painter.save()

            # Enable anti-aliasing for smoother rendering
            painter.setRenderHint(QPainter.Antialiasing)

            # Set text color and font
            painter.setPen(Qt.white)
            painter.setFont(option.font)

            # Get text size using boundingRect
            font_metrics = QFontMetrics(option.font)
            text_rect = font_metrics.boundingRect(balance_styled)

            # Define padding and right margin
            padding_x, padding_y = 8, 4
            right_margin = 10  # Adjust this value for more space on the right

            # Adjust background rectangle size to include the right margin
            bg_width = text_rect.width() + 2 * padding_x + right_margin
            bg_height = text_rect.height() + 2 * padding_y

            # Position the rectangle to be right-aligned
            rect_x = option.rect.right() - bg_width - 5  # 5px margin from the right
            rect_y = option.rect.center().y() - bg_height // 2  # Centered vertically

            # Draw rounded rectangle
            painter.setBrush(
                QBrush(QColor(NUMERIC_DISPLAY_COLOR_BLUE))
            )  # Blue background
            # painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(QRect(rect_x, rect_y, bg_width, bg_height), 10, 10)

            # Draw text inside the rectangle (horizontally centered with right margin)
            painter.drawText(
                QRect(
                    rect_x + padding_x,
                    rect_y + padding_y,
                    bg_width - padding_x - right_margin,
                    bg_height - 2 * padding_y,
                ),
                Qt.AlignCenter,
                balance_styled,
            )

            painter.restore()


class AccountTreeWidget(QWidget, Ui_AccountTreeWidget):
    """
    AccountTreeWidget class
    """

    def __init__(
        self,
        application: Application,
        mutex: QMutex,
        parent: Optional[QWidget] = None,
    ) -> None:
        """
        Init AccountTreeWidget instance

        :param application: Application instance
        :param mutex: QMutex instance
        :param parent: QWidget instance
        """
        super().__init__(parent=parent)
        self.setupUi(self)

        self.application = application
        self._ = self.application.translator.gettext
        self.mutex = mutex
        self.error_message: Optional[str] = None

        self.account_tree_model = AccountTreeModel(self.application, self.locale())
        self.treeView.setModel(self.account_tree_model)
        self.treeView.setHeaderHidden(True)
        self.treeView.expandAll()
        self.treeView.resizeColumnToContents(0)

        # set style sheet
        self.treeView.setStyleSheet("QTreeView::item {" "padding: 5px;" "}")
        self.account_icons_item_delegate = AccountIconsItemDelegate()
        self.styled_balance_item_delegate = StyledBalanceItemDelegate()
        self.treeView.setItemDelegateForColumn(0, self.account_icons_item_delegate)
        self.treeView.setItemDelegateForColumn(3, self.styled_balance_item_delegate)

        # init expand/collapse state of categories
        self.recursive_expand_or_collapse_categories(QModelIndex())
        self.treeView.resizeColumnToContents(1)

        ##############################
        # ASYNC METHODS
        ##############################
        # Create a QWorker object
        self.fetch_from_network_async_qworker = AsyncQWorker(
            self.fetch_from_network, self.mutex
        )
        self.fetch_from_network_async_qworker.finished.connect(
            self._on_finished_fetch_from_network
        )

        # events
        self.addCategoryButton.clicked.connect(self.on_add_category_button_clicked)
        self.refreshButton.clicked.connect(self.on_refresh_button_clicked)
        self.treeView.customContextMenuRequested.connect(self.on_context_menu)
        self.treeView.expanded.connect(self.on_expanded)
        self.treeView.collapsed.connect(self.on_collapsed)
        self.treeView.model().dataChanged.connect(self.on_data_changed)

        # application events
        self.application.event_dispatcher.add_event_listener(
            CategoryEvent.EVENT_TYPE_ADD, self.on_category_add_event
        )
        self.application.event_dispatcher.add_event_listener(
            CategoryEvent.EVENT_TYPE_DELETE, self.on_category_delete_event
        )
        self.application.event_dispatcher.add_event_listener(
            UnitEvent.EVENT_TYPE_CHANGED, self.on_unit_event
        )
        self.application.event_dispatcher.add_event_listener(
            CurrencyEvent.EVENT_TYPE_CHANGED, self.on_currency_event
        )
        self.application.event_dispatcher.add_event_listener(
            AccountEvent.EVENT_TYPE_ADD, self.on_add_account_event
        )
        self.application.event_dispatcher.add_event_listener(
            AccountEvent.EVENT_TYPE_DELETE, self.on_delete_account_event
        )
        self.application.event_dispatcher.add_event_listener(
            AccountEvent.EVENT_TYPE_UPDATE, self.on_update_account_event
        )
        # display total balance
        self.update_ui()

    def rename_category(self):
        """
        Set the current selected category in edit mode in tree view

        :return:
        """
        index = self.treeView.currentIndex()
        item = index.internalPointer()
        if isinstance(item.element, Category):
            self.treeView.edit(self.treeView.currentIndex())

    def add_category(self, parent: QModelIndex):
        """
        Add a new category in index in edit mode

        :param parent: Parent QModelIndex instance
        :return:
        """
        self.treeView.model().insertRow(0, parent)
        self.recursive_expand_or_collapse_categories(QModelIndex())
        self.treeView.edit(self.treeView.model().index(0, 0, parent))

    def add_sub_category(self):
        """
        Add new sub category in current selected category

        :return:
        """
        index = self.treeView.currentIndex()
        item = index.internalPointer()
        if isinstance(item.element, Category):
            self.add_category(index)

    def on_data_changed(self, _):
        """
        Triggered when data changed in tree view model

        :return:
        """
        self._update_model()

    def recursive_expand_or_collapse_categories(self, index: QModelIndex) -> None:
        """
        Expand or collapse categories in tree view depending on expanded attribute

        :param index: Index to expand/collapse
        :return:
        """
        item = index.internalPointer()
        if item is not None:
            element = index.internalPointer().element
            if isinstance(element, Category):
                if element.expanded is True:
                    self.treeView.expand(index)
                else:
                    self.treeView.collapse(index)
            else:
                self.treeView.expand(index)
        for row in range(0, self.account_tree_model.rowCount(index)):
            self.recursive_expand_or_collapse_categories(
                self.account_tree_model.index(row, 0, index)
            )
        self.treeView.resizeColumnToContents(0)

    def on_expanded(self, index: QModelIndex) -> None:
        """
        Triggered when user expand a row

        :param index: QModelIndex instance of expanded row
        :return:
        """
        # get selected element
        element = index.internalPointer().element
        if isinstance(element, Category) and element.expanded is False:
            self.application.categories.expand(element)

    def on_collapsed(self, index: QModelIndex) -> None:
        """
        Triggered when user collapse a row

        :param index: QModelIndex instance of collapsed row
        :return:
        """
        # get selected element
        element = index.internalPointer().element
        if isinstance(element, Category) and element.expanded is True:
            self.application.categories.collapse(element)

    def _update_model(self):
        """
        Triggered when adding a category

        :return:
        """
        self.treeView.model().init_data()
        self.treeView.resizeColumnToContents(0)
        self.recursive_expand_or_collapse_categories(QModelIndex())

    def update_ui(self) -> None:
        """
        Update UI data

        :return:
        """
        if self.error_message is None:
            self.errorLabel.setText(self._(self.error_message))
        unit_preference = self.application.repository.preferences.get(
            SELECTED_UNIT_PREFERENCES_KEY
        )
        if unit_preference is not None:
            amount = self.application.amounts.get_amount(unit_preference)
        else:
            amount = self.application.amounts.get_amount(AMOUNT_UNIT_KEY)
        total_balance = self.application.accounts.get_total_balance()
        self.totalBalanceValueLabel.setText(
            self.locale().toCurrencyString(
                amount.value(total_balance),
                amount.symbol(),
            )
        )

    def on_add_category_button_clicked(self):
        """
        Triggered when user click on addCategoryButton

        :return:
        """
        self.add_category(self.treeView.rootIndex())

    def on_refresh_button_clicked(self):
        """
        Triggered when user click on Refresh button

        :return:
        """
        self.refreshButton.setEnabled(False)
        self.errorLabel.setText("")
        self.error_message = None
        self.fetch_from_network_async_qworker.start()

    def on_category_add_event(self, _):
        """
        When add category event is triggered

        :return:
        """
        self._update_model()

    def on_category_delete_event(self, _):
        """
        When delete category event is triggered

        :return:
        """
        self._update_model()
        self.update_ui()

    def on_unit_event(self, _):
        """
        When a unit event is triggered

        :return:
        """
        self._update_model()
        self.update_ui()

    def on_currency_event(self, _):
        """
        When a currency event is triggered

        :return:
        """
        self._update_model()
        self.update_ui()

    def on_add_account_event(self, _):
        """
        Add account row when account is created

        :return:
        """
        self._update_model()
        self.update_ui()

    def on_delete_account_event(self, _):
        """
        Remove account row when account is deleted

        :return:
        """
        self._update_model()
        self.update_ui()

    def on_update_account_event(self, _):
        """
        Update account row when account is updated

        :return:
        """
        self._update_model()
        self.update_ui()

    def on_context_menu(self, position: QPoint):
        """
        When right button on table widget

        :param position: QPoint instance
        :return:
        """
        # get selected account
        current_element = self.treeView.currentIndex().internalPointer().element
        if isinstance(current_element, Account):
            # display account popup menu at click position
            AccountPopupMenu(self.application, current_element, self.mutex, self).exec_(
                self.treeView.mapToGlobal(position)
            )
        else:
            # display category popup menu at click position
            CategoryPopupMenu(
                self.application, current_element, self.mutex, self
            ).exec_(self.treeView.mapToGlobal(position))

    def fetch_from_network(self):
        """
        Fetch table model accounts data from the network

        :return:
        """
        accounts = self.application.accounts.get_list()
        try:
            self.application.accounts.network_update_balances(
                self.application.accounts.get_list()
            )
        except Exception as exception:
            logging.exception(exception)
            self.error_message = str(exception)

        addresses = [account.address for account in accounts]
        try:
            self.application.identities.network_update_identities(addresses)
        except Exception as exception:
            logging.exception(exception)
            self.error_message = str(exception)
        else:
            identity_indice = self.application.identities.list_indice()
            try:
                self.application.smiths.network_update_smiths(identity_indice)
            except Exception as exception:
                logging.exception(exception)
                self.error_message = str(exception)

    def _on_finished_fetch_from_network(self):
        """
        Triggered when async request fetch_from_network is finished

        :return:
        """
        logging.debug("Account tree widget update")

        self.refreshButton.setEnabled(True)
        self._update_model()
        self.update_ui()


if __name__ == "__main__":
    qapp = QApplication(sys.argv)

    application_ = Application(DATA_PATH)

    main_window = QMainWindow()
    main_window.showMaximized()

    main_window.setCentralWidget(AccountTreeWidget(application_, QMutex(), main_window))

    sys.exit(qapp.exec_())
