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

from PyQt5.QtCore import QModelIndex, QMutex, QPoint, QRect, QSize, Qt
from PyQt5.QtGui import QBrush, QColor, QFontMetrics, QPainter, QPixmap
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QStyledItemDelegate,
    QStyleOptionViewItem,
    QWidget,
)

from tikka.domains.application import Application
from tikka.domains.entities.constants import AMOUNT_UNIT_KEY, DATA_PATH
from tikka.domains.entities.events import AccountEvent, CurrencyEvent, UnitEvent
from tikka.interfaces.adapters.repository.accounts import AccountsRepositoryInterface
from tikka.slots.pyqt.entities.constants import (
    ACCOUNTS_TABLE_CATEGORY_FILTER_PREFERENCES_KEY,
    ACCOUNTS_TABLE_SORT_COLUMN_PREFERENCES_KEY,
    ACCOUNTS_TABLE_SORT_ORDER_PREFERENCES_KEY,
    ACCOUNTS_TABLE_WALLET_FILTER_PREFERENCES_KEY,
    NUMERIC_DISPLAY_COLOR_BLUE,
    SELECTED_UNIT_PREFERENCES_KEY,
)
from tikka.slots.pyqt.entities.worker import AsyncQWorker
from tikka.slots.pyqt.models.account_table import AccountTableModel, BalanceStyledRole
from tikka.slots.pyqt.resources.gui.widgets.account_table_rc import (
    Ui_AccountTableWidget,
)
from tikka.slots.pyqt.widgets.account_menu import AccountPopupMenu


class IconDelegate(QStyledItemDelegate):
    """
    IconDelegate class to center icons in table view
    """

    def initStyleOption(self, option: QStyleOptionViewItem, index: QModelIndex):
        """
        Init Style

        :param option: QStyleOptionViewItem instance
        :param index: QModelIndex instance
        :return:
        """
        super().initStyleOption(option, index)
        # resize width to actual width of icon
        option.decorationSize.setWidth(option.rect.width())


class IconTextDelegate(QStyledItemDelegate):
    def __init__(self, parent=None):
        super().__init__(parent)

    def paint(self, painter: QPainter, option, index):
        """
        Draw a QLabel in the cell


        :param painter: QPainter instance
        :param option:
        :param index:
        :return:
        """
        if not index.isValid():
            return

        # Récupérer l'icône et le texte
        icon = index.data(Qt.DecorationRole)  # Récupère l'icône
        text: str = index.data(Qt.DisplayRole)  # Récupère le texte

        ###########################
        # PURE PAINT
        painter.save()

        # Dessiner l'icône
        if isinstance(icon, QPixmap) and not icon.isNull():
            painter.setPen(QColor("blue"))
            icon_rect = option.rect.adjusted(5, 5, -5, -5)  # Espace autour
            icon_pixmap = icon.scaled(
                16, 16, Qt.KeepAspectRatio
            )  # Ajuste la taille de l'icône
            painter.drawPixmap(icon_rect.left(), icon_rect.top(), icon_pixmap)

            # Décaler le texte pour ne pas recouvrir l'icône
            text_rect: QRect = option.rect.adjusted(25, 0, 0, 0)
        else:
            painter.setPen(QColor("red"))
            text_rect = option.rect

        # set member colors
        painter.drawText(text_rect, int(Qt.AlignVCenter | Qt.AlignLeft), text)

        painter.restore()

        ###########################
        # QLABEL DISPLAY DO NOT WORK !!!
        # # Créer un QLabel temporaire pour afficher l'icône + le texte
        # label = QLabel(text)
        # if isinstance(icon, QPixmap):
        #     label.setPixmap(icon)
        #
        # # label.resize(option.rect.size())  # Set size to the row size
        # label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        # # # Appliquer le style et dessiner le QLabel
        # # #label.setStyleSheet("padding: 2px;")  # Ajoute un petit padding
        # # label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        # label.resize(option.rect.size())  # Ajuste la taille au cadre de la cellule
        # # label.render(painter, option.rect.topLeft())
        #
        # painter.save()
        # painter.translate(option.rect.topLeft())  # Place the widget correctly
        # label.render(painter)
        # painter.restore()

    def sizeHint(self, option, index):
        """
        Retourne la taille suggérée pour la cellule en fonction du texte et de l'icône.
        """
        if not index.isValid():
            return QSize()

        text = index.data(Qt.DisplayRole)  # Texte de la cellule
        icon = index.data(Qt.DecorationRole)  # Icône de la cellule

        fm = option.fontMetrics  # Récupère les métriques de police
        text_width = fm.horizontalAdvance(text) + 10  # Largeur du texte + padding
        text_height = fm.height()  # Hauteur du texte

        icon_size = QSize(0, 0)
        if isinstance(icon, QPixmap) and not icon.isNull():
            icon_size = icon.size()  # Taille réelle de l'icône

        # Largeur totale = icône + texte + espacement
        total_width = (
            icon_size.width() + text_width + 10
            if not icon_size.isEmpty()
            else text_width
        )
        total_height = max(text_height, icon_size.height()) + 6  # Ajuste la hauteur

        return QSize(total_width, total_height)


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

    def sizeHint(self, option, index):
        """
        Return the appropriate size for the cell based on the content.
        """
        balance_styled: str = index.data(BalanceStyledRole) or ""
        font_metrics = QFontMetrics(option.font)

        # Calculate text size
        text_rect = font_metrics.boundingRect(balance_styled)

        # Define padding and right margin (same as used in paint)
        padding_x, padding_y = 8, 4
        right_margin = 10
        width = text_rect.width() + 2 * padding_x + right_margin
        height = text_rect.height() + 2 * padding_y

        return QSize(width, height)


class AccountTableWidget(QWidget, Ui_AccountTableWidget):
    """
    AccountTableWidget class
    """

    def __init__(
        self,
        application: Application,
        mutex: QMutex,
        parent: Optional[QWidget] = None,
    ) -> None:
        """
        Init AccountTableWidget instance

        :param application: Application instance
        :param mutex: QMutex instance
        :param parent: QWidget instance
        """
        super().__init__(parent=parent)
        self.setupUi(self)

        self.application = application
        self.mutex = mutex
        self.account_table_model = AccountTableModel(self.application, self.locale())
        self._ = self.application.translator.gettext

        # use icon delegate to center icons
        wallet_icon_delegate = IconDelegate(self.tableView)
        self.tableView.setItemDelegateForColumn(0, wallet_icon_delegate)
        self.identity_icon_text_delegate = IconTextDelegate()
        self.tableView.setItemDelegateForColumn(1, self.identity_icon_text_delegate)
        self.styled_balance_item_delegate = StyledBalanceItemDelegate()
        self.tableView.setItemDelegateForColumn(3, self.styled_balance_item_delegate)

        # setup table view
        self.tableView.setModel(self.account_table_model)
        # set header sort column and sort order icon
        sort_column_preference = self.application.repository.preferences.get(
            ACCOUNTS_TABLE_SORT_COLUMN_PREFERENCES_KEY
        )
        if sort_column_preference is not None:
            sort_column_index = int(sort_column_preference)
        else:
            sort_column_index = -1
        repository_sort_order = self.application.repository.preferences.get(
            ACCOUNTS_TABLE_SORT_ORDER_PREFERENCES_KEY
        )
        self.tableView.horizontalHeader().setSortIndicator(
            sort_column_index,
            Qt.AscendingOrder
            if repository_sort_order == AccountsRepositoryInterface.SORT_ORDER_ASCENDING
            else Qt.DescendingOrder,
        )
        self.tableView.setSortingEnabled(True)
        self.init_category_filter()
        self.init_wallet_filter()
        self.tableView.resizeColumnsToContents()
        self.tableView.resizeRowsToContents()

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
        self.refreshButton.clicked.connect(self.fetch_from_network_async_qworker.start)

        # table events
        self.tableView.customContextMenuRequested.connect(self.on_context_menu)
        self.tableView.model().dataChanged.connect(self.on_data_changed)
        self.categoryComboBox.currentIndexChanged.connect(
            self.on_category_filter_changed
        )
        self.walletComboBox.currentIndexChanged.connect(self.on_wallet_filter_changed)

        # application events
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

        self._update_ui()

    def init_category_filter(self):
        """
        Fill category filter combo box with all categories and a blank choice

        :return:
        """
        # init combo box
        self.categoryComboBox.addItem(self._("No filter"), userData=None)
        for category in self.application.categories.list_all():
            self.categoryComboBox.addItem(category.name, userData=category.id.hex)

        # set current category filter from preferences
        category_id = self.application.repository.preferences.get(
            ACCOUNTS_TABLE_CATEGORY_FILTER_PREFERENCES_KEY
        )
        self.categoryComboBox.setCurrentIndex(
            self.categoryComboBox.findData(category_id)
        )

    def on_category_filter_changed(self, _):
        """
        Update preferences with category filter for table view

        :return:
        """
        category_id = self.categoryComboBox.currentData()
        self.application.repository.preferences.set(
            ACCOUNTS_TABLE_CATEGORY_FILTER_PREFERENCES_KEY,
            None if category_id is None else str(category_id),
        )
        self._update_model()
        self._update_ui()

    def init_wallet_filter(self):
        """
        Fill wallet filter combo box with None (with and without), True (with) or False (without)

        :return:
        """
        # init combo box
        self.walletComboBox.addItem(self._("No filter"), userData=None)
        self.walletComboBox.addItem(self._("Yes"), userData=True)
        self.walletComboBox.addItem(self._("No"), userData=False)

        # set current category filter from preferences
        wallet_filter_preference = self.application.repository.preferences.get(
            ACCOUNTS_TABLE_WALLET_FILTER_PREFERENCES_KEY
        )
        wallet_filter = None
        if wallet_filter_preference is not None:
            # preference store boolean as integer in a string column ("0" or "1")
            # convert it to boolean
            wallet_filter = int(wallet_filter_preference) == 1
        self.walletComboBox.setCurrentIndex(self.walletComboBox.findData(wallet_filter))

    def on_wallet_filter_changed(self, _):
        """
        Update preferences with wallet filter for table view

        :return:
        """
        wallet_filter = self.walletComboBox.currentData()
        self.application.repository.preferences.set(
            ACCOUNTS_TABLE_WALLET_FILTER_PREFERENCES_KEY, wallet_filter
        )
        self._update_model()
        self._update_ui()

    def on_data_changed(self, _):
        """
        Triggered when data changed in table model

        :return:
        """
        self._update_model()

    def _update_model(self):
        """
        Update all data in model

        :return:
        """
        self.tableView.model().init_data()
        self.tableView.resizeColumnsToContents()
        self.tableView.resizeRowsToContents()

    def _update_ui(self):
        """
        Update GUI

        :return:
        """
        table_total_balance = sum(
            [
                table_view_row.balance
                for table_view_row in self.account_table_model.table_view_data
                if table_view_row.balance is not None
            ]
        )

        unit_preference = self.application.repository.preferences.get(
            SELECTED_UNIT_PREFERENCES_KEY
        )
        if unit_preference is not None:
            amount = self.application.amounts.get_amount(unit_preference)
        else:
            amount = self.application.amounts.get_amount(AMOUNT_UNIT_KEY)

        self.totalBalanceValueLabel.setText(
            self.locale().toCurrencyString(
                amount.value(table_total_balance),
                amount.symbol(),
            )
        )

    def on_unit_event(self, _):
        """
        When a unit event is triggered

        :return:
        """
        self._update_model()
        self._update_ui()

    def on_currency_event(self, _):
        """
        When a currency event is triggered

        :return:
        """
        self._update_model()
        self._update_ui()

    def on_add_account_event(self, _):
        """
        Add account row when account is created

        :return:
        """
        self._update_model()
        self._update_ui()

    def on_delete_account_event(self, _):
        """
        Remove account row when account is deleted

        :return:
        """
        self._update_model()
        self._update_ui()

    def on_update_account_event(self, _):
        """
        Update account row when account is updated

        :return:
        """
        self._update_model()
        self._update_ui()

    def on_context_menu(self, position: QPoint):
        """
        When right button on table widget

        :param position: QPoint instance
        :return:
        """
        # get selected account
        table_view_row = self.tableView.currentIndex().internalPointer()
        account = self.application.accounts.get_by_address(table_view_row.address)
        if account is not None:
            # display popup menu at click position
            AccountPopupMenu(self.application, account, self.mutex, self).exec_(
                self.tableView.mapToGlobal(position)
            )

    def fetch_from_network(self):
        """
        Fetch table model accounts data from the network

        :return:
        """
        self.refreshButton.setEnabled(False)
        self.errorLabel.setText("")
        accounts = self.application.accounts.get_list()
        try:
            self.application.accounts.network_update_balances(accounts)
        except Exception as exception:
            self.errorLabel.setText(self._(str(exception)))

        addresses = [account.address for account in accounts]
        try:
            self.application.identities.network_update_identities(addresses)
        except Exception as exception:
            self.errorLabel.setText(self._(str(exception)))
        else:
            identity_indice = self.application.identities.list_indice()
            try:
                self.application.smiths.network_update_smiths(identity_indice)
            except Exception as exception:
                self.errorLabel.setText(self._(str(exception)))

    def _on_finished_fetch_from_network(self):
        """
        Triggered when async request fetch_from_network is finished

        :return:
        """
        logging.debug("Account table widget update")

        self.refreshButton.setEnabled(True)
        self._update_model()
        self._update_ui()


if __name__ == "__main__":
    qapp = QApplication(sys.argv)

    application_ = Application(DATA_PATH)

    main_window = QMainWindow()
    main_window.show()

    main_window.setCentralWidget(
        AccountTableWidget(application_, QMutex(), main_window)
    )

    sys.exit(qapp.exec_())
