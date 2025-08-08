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
import json
import logging
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from PyQt5 import QtGui
from PyQt5.QtCore import QModelIndex, QMutex, QSize, Qt, pyqtSignal
from PyQt5.QtGui import QColor, QIcon, QKeyEvent, QPixmap, QShowEvent
from PyQt5.QtWidgets import (
    QApplication,
    QComboBox,
    QFileDialog,
    QMainWindow,
    QPushButton,
    QWidget,
)

from tikka import __version__
from tikka.domains.application import Application
from tikka.domains.config import Config
from tikka.domains.entities.account import Account
from tikka.domains.entities.address import DisplayAddress
from tikka.domains.entities.constants import DATA_PATH
from tikka.domains.entities.events import (
    AccountEvent,
    ConnectionsEvent,
    CurrencyEvent,
    UnitEvent,
)
from tikka.slots.pyqt.entities.constants import (
    ICON_ACCOUNT_NO_WALLET,
    ICON_ACCOUNT_WALLET_LOCKED,
    ICON_ACCOUNT_WALLET_UNLOCKED,
    ICON_NETWORK_CONNECTED,
    ICON_NETWORK_DISCONNECTED,
    SAVE_DATA_DEFAULT_DIR_PREFERENCES_KEY,
    SELECTED_TAB_PAGE_PREFERENCES_KEY,
    SELECTED_UNIT_PREFERENCES_KEY,
    TABS_PREFERENCES_KEY,
)
from tikka.slots.pyqt.entities.worker import AsyncQWorker
from tikka.slots.pyqt.resources.gui.windows.main_window_rc import Ui_MainWindow
from tikka.slots.pyqt.widgets.account import AccountWidget
from tikka.slots.pyqt.widgets.account_table import AccountTableWidget
from tikka.slots.pyqt.widgets.account_tree import AccountTreeWidget
from tikka.slots.pyqt.widgets.connection import ConnectionWidget
from tikka.slots.pyqt.widgets.currency import CurrencyWidget
from tikka.slots.pyqt.widgets.licence import LicenceWidget
from tikka.slots.pyqt.widgets.servers import ServersWidget
from tikka.slots.pyqt.widgets.smith import SmithWidget
from tikka.slots.pyqt.widgets.tab_widget import TabWidget
from tikka.slots.pyqt.widgets.technical_committee import TechnicalCommitteeWidget
from tikka.slots.pyqt.windows.about import AboutWindow
from tikka.slots.pyqt.windows.account_create import AccountCreateWindow
from tikka.slots.pyqt.windows.account_import import AccountImportWindow
from tikka.slots.pyqt.windows.address_add import AddressAddWindow
from tikka.slots.pyqt.windows.configuration import ConfigurationWindow
from tikka.slots.pyqt.windows.scan_qr_code_open_cv import ScanQRCodeOpenCVWindow
from tikka.slots.pyqt.windows.transfer import TransferWindow
from tikka.slots.pyqt.windows.v1_account_import import V1AccountImportWindow
from tikka.slots.pyqt.windows.v1_account_import_wizard import (
    V1AccountImportWizardWindow,
)
from tikka.slots.pyqt.windows.v1_file_import import V1FileImportWindow
from tikka.slots.pyqt.windows.vault_import_by_mnemonic import (
    VaultImportByMnemonicWindow,
)
from tikka.slots.pyqt.windows.welcome import WelcomeWindow

if TYPE_CHECKING:
    pass


class MainWindow(QMainWindow, Ui_MainWindow):
    """
    MainWindow class
    """

    window_shown = pyqtSignal()
    repository_data_updated = pyqtSignal()
    mutex = QMutex()

    def __init__(self, application: Application, parent: Optional[QWidget] = None):
        """
        Init main window

        :param application: Application instance
        :param parent: QWidget instance
        """
        super().__init__(parent=parent)
        self.setupUi(self)

        self.application = application
        self._ = self.application.translator.gettext

        self.update_title()

        # tab widget
        self.tabWidget.close()
        self.tabWidget = TabWidget(self.application)
        self.tabWidget.setParent(self.centralwidget)
        self.tabWidget.setTabsClosable(True)
        self.tabWidget.setMovable(True)
        self.tabWidget.setObjectName("tabWidget")
        self.verticalLayout.addWidget(self.tabWidget)

        # slots
        self.tabWidget.tabCloseRequested.connect(self.close_tab)
        self.window_shown.connect(self.on_window_shown)

        # connect functions to menu actions
        # accounts menu
        self.actionTransfer.triggered.connect(self.open_transfer_window)
        self.actionAccount_tree.triggered.connect(self.add_account_tree_tab)
        self.actionAccount_table.triggered.connect(self.add_account_table_tab)
        self.actionScan_a_QRCode.triggered.connect(self.open_scan_qrcode_window)
        self.actionAdd_an_address.triggered.connect(self.open_add_address_window)
        self.actionImport_account.triggered.connect(self.open_import_account_window)
        self.actionCreate_account.triggered.connect(self.open_create_account_window)
        self.actionQuit.triggered.connect(self.close)

        # Vaults menu
        self.actionImport_by_Mnemonic.triggered.connect(
            self.open_vault_import_by_mnemonic_window
        )

        # V1 accounts menu
        self.actionImport_in_V2_wizard.triggered.connect(
            self.open_v1_import_in_v2_wizard_window
        )
        self.actionV1Import_account.triggered.connect(
            self.open_v1_import_account_window
        )
        self.actionV1Import_file.triggered.connect(self.open_v1_import_file_window)

        # network menu
        self.actionConnection.triggered.connect(self.add_connection_tab)
        self.actionServers.triggered.connect(self.add_servers_tab)

        # advanced menu
        self.actionSmith.triggered.connect(self.add_smith_tab)
        self.actionTechnical_Committee.triggered.connect(
            self.add_technical_committee_tab
        )
        self.actionSave_user_data.triggered.connect(self.open_save_user_data_window)
        self.actionRestore_user_data.triggered.connect(
            self.open_restore_user_data_window
        )
        # help menu
        self.actionWelcome.triggered.connect(self.open_welcome_window)
        self.actionCurrency.triggered.connect(self.add_currency_tab)
        self.actionG1_licence.triggered.connect(self.add_licence_tab)
        self.actionConfiguration.triggered.connect(self.open_configuration_window)
        self.actionAbout.triggered.connect(self.open_about_window)

        # status bar
        # Unit selector
        self.unit_combo_box = QComboBox()
        self.statusbar.addPermanentWidget(self.unit_combo_box)
        self.init_units()

        # Node connection status icon
        self.node_connection_status_icon = QPushButton()
        self.node_connection_status_icon.setFlat(True)
        self.node_connection_status_icon.setFixedSize(QSize(16, 16))
        self.node_connection_status_icon.setToolTip(
            self._("Node connection status. Click to open connection tab.")
        )
        self.statusbar.addPermanentWidget(self.node_connection_status_icon)

        # Indexer connection status icon
        self.indexer_connection_status_icon = QPushButton()
        self.indexer_connection_status_icon.setFlat(True)
        self.indexer_connection_status_icon.setFixedSize(QSize(16, 16))
        self.indexer_connection_status_icon.setToolTip(
            self._("Indexer connection status. Click to open connection tab.")
        )
        self.statusbar.addPermanentWidget(self.indexer_connection_status_icon)
        self.init_connection_status()

        # slots
        self.unit_combo_box.activated.connect(self._on_unit_changed)
        self.node_connection_status_icon.clicked.connect(self.add_connection_tab)
        self.indexer_connection_status_icon.clicked.connect(self.add_connection_tab)

        # application events
        self.application.event_dispatcher.add_event_listener(
            CurrencyEvent.EVENT_TYPE_PRE_CHANGE, self.on_currency_event
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
        self.application.event_dispatcher.add_event_listener(
            ConnectionsEvent.EVENT_TYPE_NODE_CONNECTED, self._on_node_connected
        )
        self.application.event_dispatcher.add_event_listener(
            ConnectionsEvent.EVENT_TYPE_NODE_DISCONNECTED, self._on_node_disconnected
        )
        self.application.event_dispatcher.add_event_listener(
            ConnectionsEvent.EVENT_TYPE_INDEXER_CONNECTED, self._on_indexer_connected
        )
        self.application.event_dispatcher.add_event_listener(
            ConnectionsEvent.EVENT_TYPE_INDEXER_DISCONNECTED,
            self._on_indexer_disconnected,
        )

        #####################################
        # ASYNC WORKERS
        #####################################
        self.connect_to_node_async_worker = AsyncQWorker(
            self.connect_to_node, self.mutex
        )
        self.connect_to_node_async_worker.finished.connect(
            self._on_finished_connect_to_node
        )
        # async connect to indexer
        self.connect_to_indexer_async_worker = AsyncQWorker(
            self.connect_to_indexer, self.mutex
        )
        self.connect_to_indexer_async_worker.finished.connect(
            self._on_finished_connect_to_indexer
        )
        # fetch data from network
        self.fetch_data_from_network_node_async_qworker = AsyncQWorker(
            self.fetch_data_from_network_node, self.mutex
        )
        self.fetch_data_from_network_node_async_qworker.finished.connect(
            self._on_finished_fetch_data_from_network_node
        )
        self.fetch_data_from_network_indexer_async_qworker = AsyncQWorker(
            self.fetch_data_from_network_indexer, self.mutex
        )
        self.fetch_data_from_network_indexer_async_qworker.finished.connect(
            self._on_finished_fetch_data_from_network_indexer
        )

        # open saved tabs
        self.init_tabs()

    def showEvent(self, event: QShowEvent):
        """
        Triggered when the window is shown

        :param event: QEvent instance
        :return:
        """
        super().showEvent(event)

        self.window_shown.emit()

    def on_window_shown(self):
        """
        Triggered when the window is shown

        :return:
        """
        self.statusbar.showMessage(self._("Connecting to servers..."), 10000)
        self.connect_to_node_async_worker.start()
        self.connect_to_indexer_async_worker.start()

    def keyPressEvent(self, event: QKeyEvent) -> None:
        """
        Triggered when user press a key

        :param event: QKeyEvent instance
        :return:
        """
        # close current tab with "ctrl-w"
        if (
            event.key() == Qt.Key_W
            and (event.modifiers() & Qt.ControlModifier) == Qt.ControlModifier
        ):
            self.close_current_tab()

    def closeEvent(
        self, event: QtGui.QCloseEvent  # pylint: disable=unused-argument
    ) -> None:
        """
        Override close event

        :param event:
        :return:
        """
        # save tabs in repository
        self.save_tabs()

        # save tab selection in preferences
        self.application.repository.preferences.set(
            SELECTED_TAB_PAGE_PREFERENCES_KEY, self.tabWidget.currentIndex()
        )

        self.application.close()

    def init_units(self) -> None:
        """
        Init units combobox in status bar

        :return:
        """
        self.unit_combo_box.clear()

        for key, amount in self.application.amounts.register.items():
            self.unit_combo_box.addItem(amount.name(), userData=key)
        preferences_selected_unit = self.application.repository.preferences.get(
            SELECTED_UNIT_PREFERENCES_KEY
        )
        if preferences_selected_unit is None:
            # set first unit in preferences
            self.application.repository.preferences.set(
                SELECTED_UNIT_PREFERENCES_KEY,
                self.application.amounts.get_register_keys()[0],
            )
            preferences_selected_unit = self.application.repository.preferences.get(
                SELECTED_UNIT_PREFERENCES_KEY
            )

        self.unit_combo_box.setCurrentIndex(
            self.unit_combo_box.findData(preferences_selected_unit)
        )

    def init_connection_status(self):
        """
        Init connection status icon

        :return:
        """
        if self.application.connections.node.is_connected():
            self.node_connection_status_icon.setIcon(
                QIcon(QPixmap(ICON_NETWORK_CONNECTED))
            )
        else:
            self.node_connection_status_icon.setIcon(
                QIcon(QPixmap(ICON_NETWORK_DISCONNECTED))
            )
        if self.application.connections.indexer.is_connected():
            self.indexer_connection_status_icon.setIcon(
                QIcon(QPixmap(ICON_NETWORK_CONNECTED))
            )
        else:
            self.indexer_connection_status_icon.setIcon(
                QIcon(QPixmap(ICON_NETWORK_DISCONNECTED))
            )

    def init_tabs(self):
        """
        Init tabs from repository

        :return:
        """
        # close all tabs
        self.tabWidget.clear()

        result = self.application.preferences.get(TABS_PREFERENCES_KEY)
        if result is None:
            return

        opened_tabs: Dict[str, str] = json.loads(result)

        # fetch tabs from repository
        for title, panel_class in opened_tabs.items():
            # if account tab...
            if panel_class == AccountWidget.__name__:
                # get account
                account = self.application.accounts.get_by_address(title)
                if account is not None:
                    self.add_account_tab(account)
            elif panel_class == CurrencyWidget.__name__:
                self.add_currency_tab()
            elif panel_class == LicenceWidget.__name__:
                self.add_licence_tab()
            elif panel_class == AccountTreeWidget.__name__:
                self.add_account_tree_tab()
            elif panel_class == AccountTableWidget.__name__:
                self.add_account_table_tab()
            elif panel_class == ConnectionWidget.__name__:
                self.add_connection_tab()
            elif panel_class == ServersWidget.__name__:
                self.add_servers_tab()
            elif panel_class == SmithWidget.__name__:
                self.add_smith_tab()
            elif panel_class == TechnicalCommitteeWidget.__name__:
                self.add_technical_committee_tab()

        # get preferences
        preferences_selected_page = self.application.repository.preferences.get(
            SELECTED_TAB_PAGE_PREFERENCES_KEY
        )
        if preferences_selected_page is not None:
            self.tabWidget.setCurrentIndex(int(preferences_selected_page))

    def save_tabs(self):
        """
        Save opened tabs in preferences

        :return:
        """
        # save tabwidget tabs in repository
        tabs: Dict[str, str] = {}
        for index in range(0, self.tabWidget.count()):
            widget = self.tabWidget.widget(index)
            if isinstance(widget, AccountWidget):
                # save account tab in repository
                tabs[widget.account.address] = str(widget.__class__.__name__)
            else:
                tabs[str(widget.__class__.__name__)] = str(widget.__class__.__name__)

        self.application.preferences.set(TABS_PREFERENCES_KEY, json.dumps(tabs))

    def close_tab(self, index: int):
        """
        Close tab on signal

        :param index: Index of tab requested to close
        :return:
        """
        self.tabWidget.removeTab(index)

    def close_current_tab(self) -> None:
        """
        Close current tab

        :return:
        """
        self.tabWidget.removeTab(self.tabWidget.currentIndex())

    def add_account_tree_tab(self) -> None:
        """
        Open account tree tab

        :return:
        """
        # select account tree tab if exists
        for widget in self.get_tab_widgets_by_class(AccountTreeWidget):
            self.tabWidget.setCurrentIndex(self.get_tab_index_from_widget(widget))
            return

        # create tab
        account_tree_widget = AccountTreeWidget(
            self.application, self.mutex, self.tabWidget
        )
        self.tabWidget.addTab(account_tree_widget, self._("Account tree"))
        # catch account tree double click signal
        account_tree_widget.treeView.doubleClicked.connect(
            self.on_account_tree_double_click
        )
        self.repository_data_updated.connect(
            account_tree_widget._on_finished_fetch_from_network
        )

        self.tabWidget.setCurrentIndex(self.tabWidget.count() - 1)

    def add_account_table_tab(self) -> None:
        """
        Open account table tab

        :return:
        """
        # select account table tab if exists
        for widget in self.get_tab_widgets_by_class(AccountTableWidget):
            self.tabWidget.setCurrentIndex(self.get_tab_index_from_widget(widget))
            return

        # create tab
        account_table_widget = AccountTableWidget(
            self.application, self.mutex, self.tabWidget
        )
        self.tabWidget.addTab(account_table_widget, self._("Account table"))
        # catch account list double click signal
        account_table_widget.tableView.doubleClicked.connect(
            self.on_account_table_double_click
        )
        self.repository_data_updated.connect(
            account_table_widget._on_finished_fetch_from_network
        )

        self.tabWidget.setCurrentIndex(self.tabWidget.count() - 1)

    def add_account_tab(self, account: Account) -> AccountWidget:
        """
        Open account list tab

        :return:
        """
        # select account tab if exists
        for widget in self.get_tab_widgets_by_class(AccountWidget):
            if (
                isinstance(widget, AccountWidget)
                and widget.account.address == account.address
            ):
                self.tabWidget.setCurrentIndex(self.get_tab_index_from_widget(widget))
                return widget
        account_widget = AccountWidget(
            self.application, account, self.mutex, self.tabWidget
        )
        index = self.tabWidget.addTab(
            account_widget,
            self.get_account_tab_icon(account),
            account.name,
        )
        self.set_account_tab_title(index, account)

        self.repository_data_updated.connect(
            account_widget._on_finished_fetch_from_network
        )

        self.tabWidget.setCurrentIndex(index)

        return account_widget

    def set_account_tab_title(self, index: int, account: Account):
        """
        Set account tab title with text, font and color

        :param index: Index of tab
        :param account: Account instance
        :return:
        """
        set_identity_name_color = False
        if account.name is None:
            identity = self.application.identities.get_by_address(account.address)
            if identity is None:
                tab_title = DisplayAddress(account.address).shorten
            else:
                identity_name = identity.name or ""
                tab_title = f"{identity_name}#{identity.index}"
                set_identity_name_color = True
        else:
            tab_title = account.name
            set_identity_name_color = False

        self.tabWidget.setTabText(index, tab_title)

        if set_identity_name_color is True:
            self.tabWidget.tabBar().setTabTextColor(index, QColor("blue"))
        else:
            self.tabWidget.tabBar().setTabTextColor(index, QColor("black"))

    def get_account_tab_icon(self, account: Account) -> QIcon:
        """
        Return QIcon instance for account tab icon

        :param account: Account instance
        :return:
        """
        if self.application.wallets.exists(account.address):
            if self.application.wallets.is_unlocked(account.address) is True:
                icon = QIcon(ICON_ACCOUNT_WALLET_UNLOCKED)
            else:
                icon = QIcon(ICON_ACCOUNT_WALLET_LOCKED)
        else:
            icon = QIcon(ICON_ACCOUNT_NO_WALLET)

        return icon

    def add_currency_tab(self):
        """
        Open currency tab

        :return:
        """
        # select currency tab if exists
        for widget in self.get_tab_widgets_by_class(CurrencyWidget):
            self.tabWidget.setCurrentIndex(self.get_tab_index_from_widget(widget))
            return

        currency_widget = CurrencyWidget(self.application, self.mutex, self.tabWidget)

        # create tab
        self.tabWidget.addTab(
            currency_widget,
            self._("Currency"),
        )
        self.repository_data_updated.connect(
            currency_widget._on_finished_fetch_from_network
        )

        self.tabWidget.setCurrentIndex(self.tabWidget.count() - 1)

    def add_licence_tab(self):
        """
        Open licence tab

        :return:
        """
        # select tab if exists
        for widget in self.get_tab_widgets_by_class(LicenceWidget):
            self.tabWidget.setCurrentIndex(self.get_tab_index_from_widget(widget))
            return

        # create tab
        self.tabWidget.addTab(
            LicenceWidget(self.application, self.tabWidget), self._("Ğ1 licence")
        )
        self.tabWidget.setCurrentIndex(self.tabWidget.count() - 1)

    def add_connection_tab(self):
        """
        Open network connection tab

        :return:
        """
        # select tab if exists
        for widget in self.get_tab_widgets_by_class(ConnectionWidget):
            self.tabWidget.setCurrentIndex(self.get_tab_index_from_widget(widget))
            return

        connection_widget = ConnectionWidget(
            self.application, self.mutex, self.tabWidget
        )
        # create tab
        self.tabWidget.addTab(
            connection_widget,
            self._("Connection"),
        )
        self.repository_data_updated.connect(
            connection_widget._on_finished_fetch_node_from_network
        )
        self.repository_data_updated.connect(
            connection_widget._on_finished_fetch_indexer_from_network
        )

        self.tabWidget.setCurrentIndex(self.tabWidget.count() - 1)

    def add_servers_tab(self):
        """
        Open network servers tab

        :return:
        """
        # select tab if exists
        for widget in self.get_tab_widgets_by_class(ServersWidget):
            self.tabWidget.setCurrentIndex(self.get_tab_index_from_widget(widget))
            return

        # create tab
        self.tabWidget.addTab(
            ServersWidget(self.application, self.mutex, self.tabWidget),
            self._("Servers"),
        )
        self.tabWidget.setCurrentIndex(self.tabWidget.count() - 1)

    def add_smith_tab(self):
        """
        Open smith tab

        :return:
        """
        # select smith tab if exists
        for widget in self.get_tab_widgets_by_class(SmithWidget):
            self.tabWidget.setCurrentIndex(self.get_tab_index_from_widget(widget))
            return

        smith_widget = SmithWidget(self.application, self.mutex, self.tabWidget)

        # create tab
        self.tabWidget.addTab(
            smith_widget,
            self._("Smith"),
        )

        self.repository_data_updated.connect(
            smith_widget._on_finished_fetch_all_from_network
        )

        self.tabWidget.setCurrentIndex(self.tabWidget.count() - 1)

    def add_technical_committee_tab(self):
        """
        Open technical_committee tab

        :return:
        """
        # select smith tab if exists
        for widget in self.get_tab_widgets_by_class(TechnicalCommitteeWidget):
            self.tabWidget.setCurrentIndex(self.get_tab_index_from_widget(widget))
            return

        technical_committee_widget = TechnicalCommitteeWidget(
            self.application, self.mutex, self.tabWidget
        )

        # create tab
        self.tabWidget.addTab(
            technical_committee_widget,
            self._("Technical Committee"),
        )

        self.repository_data_updated.connect(
            technical_committee_widget._on_fetch_members_from_network_async_worker_finished
        )

        self.tabWidget.setCurrentIndex(self.tabWidget.count() - 1)

    def update_title(self):
        """
        Update window title with version and currency

        :return:
        """
        self.setWindowTitle(
            "Tikka {version} - {currency}".format(  # pylint: disable=consider-using-f-string
                version=__version__,
                currency=self.application.currencies.get_current().name,
            )
        )

    def open_transfer_window(self) -> None:
        """
        Open transfer window

        :return:
        """
        TransferWindow(self.application, self.mutex, None, None, self).exec_()

    def open_scan_qrcode_window(self) -> None:
        """
        Open scan qrcode window

        :return:
        """
        logging.debug("create instance of ScanQRCodeWindow")
        # ScanQRCodeWindow(self.application, self).exec_()
        window = ScanQRCodeOpenCVWindow(self.application, self)
        if window.address is not None:
            # display window
            window.exec_()

    def open_add_address_window(self) -> None:
        """
        Open add address window

        :return:
        """
        AddressAddWindow(self.application, self.mutex, self).exec_()

    def open_import_account_window(self) -> None:
        """
        Open import account window

        :return:
        """
        AccountImportWindow(self.application, self.mutex, self).exec_()

    def open_create_account_window(self) -> None:
        """
        Open create account window

        :return:
        """
        AccountCreateWindow(self.application, self).exec_()

    def open_vault_import_by_mnemonic_window(self) -> None:
        """
        Open import vault by mnemonic window

        :return:
        """
        VaultImportByMnemonicWindow(self.application, self.mutex, self).exec_()

    def open_v1_import_account_window(self) -> None:
        """
        Open V1 import account window

        :return:
        """
        V1AccountImportWindow(self.application, self.mutex, self).exec_()

    def open_v1_import_in_v2_wizard_window(self) -> None:
        """
        Open V1 import in V2 wizard window

        :return:
        """
        V1AccountImportWizardWindow(self.application, self.mutex, self).exec_()

    def open_v1_import_file_window(self) -> None:
        """
        Open V1 import file window

        :return:
        """
        V1FileImportWindow(self.application, self.mutex, self).exec_()

    def open_configuration_window(self) -> None:
        """
        Open configuration window

        :return:
        """
        ConfigurationWindow(self.application, self).exec_()

    def open_about_window(self) -> None:
        """
        Open about window

        :return:
        """
        AboutWindow(self).exec_()

    def open_welcome_window(self) -> None:
        """
        Open welcome window

        :return:
        """
        WelcomeWindow(self.application, self).exec_()

    def open_save_user_data_window(self) -> None:
        """
        Open file dialog to save user data on disk as json file

        :return:
        """
        default_dir = self.application.repository.preferences.get(
            SAVE_DATA_DEFAULT_DIR_PREFERENCES_KEY
        )
        if default_dir is not None:
            default_dir = str(Path(default_dir).expanduser().absolute())
        else:
            default_dir = ""

        result = QFileDialog.getSaveFileName(
            self, self._("Save user data"), default_dir, "JSON Files (*.json)"
        )
        if result[0] == "":
            return None

        self.application.save_data(result[0])

        # update default dir preference
        self.application.repository.preferences.set(
            SAVE_DATA_DEFAULT_DIR_PREFERENCES_KEY,
            str(Path(result[0]).expanduser().absolute().parent),
        )

        self.statusbar.showMessage(self._("User data saved."), 5000)

        return None

    def open_restore_user_data_window(self) -> None:
        """
        Open file dialog to restore user data from json file

        :return:
        """
        default_dir = self.application.repository.preferences.get(
            SAVE_DATA_DEFAULT_DIR_PREFERENCES_KEY
        )
        if default_dir is not None:
            default_dir = str(Path(default_dir).expanduser().absolute())
        else:
            default_dir = ""

        result = QFileDialog.getOpenFileName(
            self, self._("Restore user data"), default_dir, "JSON Files (*.json)"
        )
        if result[0] == "":
            return None

        # disconnect servers
        self.application.connections.disconnect_all()

        # load user data
        self.application.load_data(result[0])

        # refresh widgets
        self.repository_data_updated.emit()
        logging.debug("repository_data_updated. Emit signal to widgets.")

        # connect to servers
        self.connect_to_node_async_worker.start()
        self.connect_to_indexer_async_worker.start()

        # update default dir preference
        self.application.repository.preferences.set(
            SAVE_DATA_DEFAULT_DIR_PREFERENCES_KEY,
            str(Path(result[0]).expanduser().absolute().parent),
        )

        self.statusbar.showMessage(self._("User data restored."), 5000)

        return None

    def on_currency_event(self, event: CurrencyEvent):
        """
        When a currency event is triggered

        :return:
        """
        if event.type == CurrencyEvent.EVENT_TYPE_PRE_CHANGE:
            self.save_tabs()
        else:
            self.update_title()
            self.init_tabs()

    def on_account_tree_double_click(self, index: QModelIndex):
        """
        When a row is double-clicked in account tree view

        :param index: QModelIndex instance
        :return:
        """
        account = index.internalPointer().element
        if isinstance(account, Account):
            fetch_transfers_from_network = False
            if self.get_account_widget(account.address) is None:
                fetch_transfers_from_network = True
            widget = self.add_account_tab(index.internalPointer().element)
            if fetch_transfers_from_network is True:
                widget.fetch_transfers_from_network_async_qworker.start()

    def on_account_table_double_click(self, index: QModelIndex):
        """
        When a row is double-clicked in account table

        :param index: QModelIndex instance
        :return:
        """
        table_view_row = index.internalPointer()
        account = self.application.accounts.get_by_address(table_view_row.address)
        if account is not None:
            fetch_transfers_from_network = False
            if self.get_account_widget(account.address) is None:
                fetch_transfers_from_network = True
            widget = self.add_account_tab(account)
            if fetch_transfers_from_network is True:
                widget.fetch_transfers_from_network_async_qworker.start()

    def on_add_account_event(self, event: AccountEvent) -> None:
        """
        Triggered when an account is created

        :param event: AccountEvent instance
        :return:
        """
        widget = self.add_account_tab(event.account)
        widget.fetch_transfers_from_network_async_qworker.start()

    def on_update_account_event(self, event: AccountEvent) -> None:
        """
        Triggered when an account is updated

        :param event: AccountEvent instance
        :return:
        """
        for index in range(0, self.tabWidget.count()):
            widget = self.tabWidget.widget(index)
            if (
                isinstance(widget, AccountWidget)
                and widget.account.address == event.account.address
            ):
                self.set_account_tab_title(index, widget.account)
                self.tabWidget.setTabIcon(
                    index, self.get_account_tab_icon(widget.account)
                )

    def on_delete_account_event(self, event: AccountEvent) -> None:
        """
        Triggered when an account is deleted

        :param event: AccountEvent instance
        :return:
        """
        for widget in self.get_tab_widgets_by_class(AccountWidget):
            if (
                isinstance(widget, AccountWidget)
                and widget.account.address == event.account.address
            ):
                self.tabWidget.removeTab(self.tabWidget.indexOf(widget))

    def _on_unit_changed(self) -> None:
        """
        Triggered when unit_combo_box selection changed

        :return:
        """
        unit_key = self.unit_combo_box.currentData()

        self.application.repository.preferences.set(
            SELECTED_UNIT_PREFERENCES_KEY, unit_key
        )
        self.application.event_dispatcher.dispatch_event(
            UnitEvent(UnitEvent.EVENT_TYPE_CHANGED)
        )

    def _on_node_connected(self, _=None):
        """
        Triggered when node is connected

        :return:
        """
        self.node_connection_status_icon.setIcon(QIcon(ICON_NETWORK_CONNECTED))
        self.statusbar.showMessage(self._("Loading data from network..."), 3000)
        self.fetch_data_from_network_node_async_qworker.start()

    def _on_node_disconnected(self, _=None):
        """
        Triggered when node is disconnected

        :return:
        """
        self.node_connection_status_icon.setIcon(QIcon(ICON_NETWORK_DISCONNECTED))

    def _on_indexer_connected(self, _=None):
        """
        Triggered when indexer is connected

        :return:
        """
        self.indexer_connection_status_icon.setIcon(QIcon(ICON_NETWORK_CONNECTED))

    def _on_indexer_disconnected(self, _=None):
        """
        Triggered when indexer is disconnected

        :return:
        """
        self.indexer_connection_status_icon.setIcon(QIcon(ICON_NETWORK_DISCONNECTED))

    def get_tab_widgets_by_class(self, widget_class: Any) -> List[QWidget]:
        """
        Return a list of widget which are instance of widget_class

        :param widget_class: Widget class
        :return:
        """
        widgets = []
        for index in range(0, self.tabWidget.count()):
            widget = self.tabWidget.widget(index)
            if isinstance(widget, widget_class):
                widgets.append(widget)

        return widgets

    def get_tab_index_from_widget(self, widget: QWidget) -> Optional[int]:
        """
        Return tab index of widget, or None if no tab with this widget

        :param widget: QWidget inherited instance
        :return:
        """
        for index in range(0, self.tabWidget.count()):
            if widget == self.tabWidget.widget(index):
                return index

        return None

    def get_account_widget(self, address: str) -> Optional[AccountWidget]:
        """
        Return AccountWidget instance if it is opened

        :param address: Account address
        :return:
        """
        for widget in self.get_tab_widgets_by_class(AccountWidget):
            if isinstance(widget, AccountWidget) and widget.account.address == address:
                return widget
        return None

    def connect_to_node(self):

        # init network connections
        if self.application.config.get(Config.RANDOM_CONNECTION_AT_START_KEY) is True:
            self.application.nodes.set_current_url_randomly()
        else:
            current_node = self.application.nodes.get(
                self.application.nodes.get_current_url()
            )
            if current_node is not None:
                # connect to node
                self.application.connections.node.connect(current_node)

    def _on_finished_connect_to_node(self):
        """
        Triggered when connection to node is finished

        :return:
        """
        if self.application.connections.node.is_connected():
            self.application.event_dispatcher.dispatch_event(
                ConnectionsEvent(ConnectionsEvent.EVENT_TYPE_NODE_CONNECTED)
            )

    def connect_to_indexer(self):
        if self.application.config.get(Config.RANDOM_CONNECTION_AT_START_KEY) is True:
            self.application.indexers.set_current_url_randomly()
        else:
            current_indexer = self.application.indexers.get(
                self.application.indexers.get_current_url()
            )
            if current_indexer is not None:
                # connect to indexer
                self.application.connections.indexer.connect(current_indexer)

    def _on_finished_connect_to_indexer(self):
        """
        Triggered when connection to indexer is finished

        :return:
        """
        if self.application.connections.indexer.is_connected():
            self.application.event_dispatcher.dispatch_event(
                ConnectionsEvent(ConnectionsEvent.EVENT_TYPE_INDEXER_CONNECTED)
            )

    def fetch_data_from_network_node(self):
        """
        Fetch data from the network node

        :return:
        """
        self.application.nodes.network_fetch_current_node()
        self.application.currencies.network_update_properties()

        self.application.nodes.network_fetch_endpoints()
        self.application.indexers.network_fetch_endpoints()

        accounts = self.application.accounts.get_list()
        try:
            self.application.accounts.network_update_balances(accounts)
        except Exception as exception:
            logging.exception(exception)

        addresses = [account.address for account in accounts]
        try:
            self.application.identities.network_update_identities(addresses)
        except Exception as exception:
            logging.exception(exception)
        else:
            identity_indice = self.application.identities.list_indice()
            try:
                self.application.smiths.network_update_smiths(identity_indice)
            except Exception as exception:
                logging.exception(exception)
            else:
                self.application.authorities.network_get_all()

        self.application.technical_committee.network_update_members()
        self.application.technical_committee.network_update_proposals()

    def _on_finished_fetch_data_from_network_node(self):
        """
        Triggered when async request fetch_data_from_network_node is finished

        :return:
        """
        self.statusbar.showMessage(self._("Data updated from network node."), 3000)
        self.repository_data_updated.emit()
        logging.debug("Main window network fetch finished....emit signal")

    def fetch_data_from_network_indexer(self):
        """
        Fetch data from the network indexer

        :return:
        """
        self.application.indexers.network_fetch_current_indexer()

    def _on_finished_fetch_data_from_network_indexer(self):
        """
        Triggered when async request fetch_data_from_network_indexer is finished

        :return:
        """
        self.statusbar.showMessage(self._("Data updated from network indexer."), 3000)
        self.repository_data_updated.emit()
        logging.debug("Main window network fetch finished....emit signal")


if __name__ == "__main__":
    qapp = QApplication(sys.argv)
    application_ = Application(DATA_PATH)
    MainWindow(application_).show()
    sys.exit(qapp.exec_())
