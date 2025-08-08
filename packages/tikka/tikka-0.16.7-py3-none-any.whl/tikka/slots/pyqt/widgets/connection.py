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
import sys
from typing import Optional

from PyQt5.QtCore import QMutex
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget

from tikka.domains.application import Application
from tikka.domains.entities.constants import DATA_PATH
from tikka.domains.entities.events import (
    ConnectionsEvent,
    CurrencyEvent,
    IndexersEvent,
    NodesEvent,
)
from tikka.slots.pyqt.entities.constants import (
    ICON_NETWORK_CONNECTED,
    ICON_NETWORK_DISCONNECTED,
)
from tikka.slots.pyqt.entities.worker import AsyncQWorker
from tikka.slots.pyqt.resources.gui.widgets.connection_rc import Ui_ConnectionWidget


class ConnectionWidget(QWidget, Ui_ConnectionWidget):
    """
    ConnectionWidget class
    """

    def __init__(
        self,
        application: Application,
        mutex: QMutex,
        parent: Optional[QWidget] = None,
    ) -> None:
        """
        Init ConnectionWidget instance

        :param application: Application instance
        :param mutex: QMutex instance
        :param parent: MainWindow instance
        """
        super().__init__(parent=parent)
        self.setupUi(self)

        self.application = application
        self.mutex = mutex
        self._ = self.application.translator.gettext

        self.connected_button_text = self._("Disconnect")
        self.disconnected_button_text = self._("Connect")

        self.init_node_urls()
        self.init_indexer_urls()

        if self.application.connections.node.is_connected():
            self._on_node_connected()
        else:
            self._on_node_disconnected()

        if self.application.connections.indexer.is_connected():
            self._on_indexer_connected()
        else:
            self._on_indexer_disconnected()

        # events
        self.nodeUrlsComboBox.activated.connect(
            self.on_node_urls_combobox_index_changed
        )
        self.nodeConnectButton.clicked.connect(
            self._on_node_connect_button_clicked_event
        )
        self.refreshNodeButton.clicked.connect(
            self._on_refresh_node_button_clicked_event
        )

        self.indexerUrlsComboBox.activated.connect(
            self.on_indexer_urls_combobox_index_changed
        )
        self.indexerConnectButton.clicked.connect(
            self._on_indexer_connect_button_clicked_event
        )
        self.refreshIndexerButton.clicked.connect(
            self._on_refresh_indexer_button_clicked_event
        )

        # subscribe to application events
        self.application.event_dispatcher.add_event_listener(
            CurrencyEvent.EVENT_TYPE_CHANGED, self._on_currency_event
        )
        self.application.event_dispatcher.add_event_listener(
            NodesEvent.EVENT_TYPE_LIST_CHANGED,
            lambda event: self.init_node_urls(),
        )
        self.application.event_dispatcher.add_event_listener(
            ConnectionsEvent.EVENT_TYPE_NODE_CONNECTED, self._on_node_connected
        )
        self.application.event_dispatcher.add_event_listener(
            ConnectionsEvent.EVENT_TYPE_NODE_DISCONNECTED, self._on_node_disconnected
        )

        self.application.event_dispatcher.add_event_listener(
            IndexersEvent.EVENT_TYPE_LIST_CHANGED,
            lambda event: self.init_indexer_urls(),
        )
        self.application.event_dispatcher.add_event_listener(
            ConnectionsEvent.EVENT_TYPE_INDEXER_CONNECTED, self._on_indexer_connected
        )
        self.application.event_dispatcher.add_event_listener(
            ConnectionsEvent.EVENT_TYPE_INDEXER_DISCONNECTED,
            self._on_indexer_disconnected,
        )

        ##############################
        # ASYNC METHODS
        ##############################
        # Create a QWorker object
        self.toggle_node_connection_async_qworker = AsyncQWorker(
            self.toggle_node_connection,
            self.mutex,
        )
        self.toggle_node_connection_async_qworker.finished.connect(
            self._on_finished_toggle_node_connection
        )
        self.toggle_indexer_connection_async_qworker = AsyncQWorker(
            self.toggle_indexer_connection,
            self.mutex,
        )
        self.toggle_indexer_connection_async_qworker.finished.connect(
            self._on_finished_toggle_indexer_connection
        )
        self.network_fetch_current_node_async_qworker = AsyncQWorker(
            self.fetch_node_from_network,
            self.mutex,
        )
        self.network_fetch_current_node_async_qworker.finished.connect(
            self._on_finished_fetch_node_from_network
        )

        if self.application.connections.node.is_connected():
            self.network_fetch_current_node_async_qworker.start()

        # Create a QWorker object
        self.network_fetch_current_indexer_async_qworker = AsyncQWorker(
            self.fetch_indexer_from_network,
            self.mutex,
        )
        self.network_fetch_current_indexer_async_qworker.finished.connect(
            self._on_finished_fetch_indexer_from_network
        )

        if self.application.connections.indexer.is_connected():
            self.network_fetch_current_indexer_async_qworker.start()

    def init_node_urls(self) -> None:
        """
        Init combobox with node urls

        :return:
        """
        self.nodeUrlsComboBox.clear()

        urls = [node.url for node in self.application.nodes.list()]
        self.nodeUrlsComboBox.addItems(urls)
        # get current node url from domain
        current_node_url = self.application.nodes.get_current_url()
        if current_node_url in urls:
            self.nodeUrlsComboBox.setCurrentIndex(urls.index(current_node_url))

    def on_node_urls_combobox_index_changed(self):
        """
        Triggered when node url selection is changed

        :return:
        """
        url = self.nodeUrlsComboBox.currentText()
        if url:
            node = self.application.nodes.get(url)
            if node is None:
                # get the first one
                url = self.nodeUrlsComboBox.itemText(0)
            self.application.nodes.set_current_url(url)

            if self.application.connections.node.is_connected():
                self.application.event_dispatcher.dispatch_event(
                    ConnectionsEvent(ConnectionsEvent.EVENT_TYPE_NODE_CONNECTED)
                )
                self.refreshNodeButton.setEnabled(False)
                self.network_fetch_current_node_async_qworker.start()
            else:
                self.application.event_dispatcher.dispatch_event(
                    ConnectionsEvent(ConnectionsEvent.EVENT_TYPE_NODE_DISCONNECTED)
                )

    def _on_node_connect_button_clicked_event(self):
        """
        Triggered when user click on connect button

        :return:
        """
        # Disable button
        self.nodeConnectButton.setDisabled(True)
        self.toggle_node_connection_async_qworker.start()

    def toggle_node_connection(self):
        """
        Toggle node connection

        :return:
        """
        if self.application.connections.node.is_connected():
            self.application.connections.node.disconnect()
            self.application.event_dispatcher.dispatch_event(
                ConnectionsEvent(ConnectionsEvent.EVENT_TYPE_NODE_DISCONNECTED)
            )
        else:
            url = self.nodeUrlsComboBox.currentText()
            if url:
                node = self.application.nodes.get(url)
                if node is not None:
                    self.application.connections.node.connect(node)

                    if self.application.connections.node.is_connected():
                        self.application.event_dispatcher.dispatch_event(
                            ConnectionsEvent(ConnectionsEvent.EVENT_TYPE_NODE_CONNECTED)
                        )

    def _on_finished_toggle_node_connection(self):
        """
        Triggered when toggle_node_connection is finished

        :return:
        """
        self.nodeConnectButton.setDisabled(False)

    def _on_refresh_node_button_clicked_event(self):
        """
        Triggered when user click on refresh node button

        :return:
        """
        # Disable button
        self.refreshNodeButton.setEnabled(False)
        self.network_fetch_current_node_async_qworker.start()

    def fetch_node_from_network(self):
        """
        Update node infos from current url connection

        :return:
        """
        try:
            self.application.nodes.network_fetch_current_node()
        except Exception:
            pass

    def _on_finished_fetch_node_from_network(self):
        """
        Triggered when async request fetch_node_from_network is finished

        :return:
        """
        self.refreshNodeButton.setEnabled(True)
        self._update_ui()

    def init_indexer_urls(self) -> None:
        """
        Init combobox with indexer urls

        :return:
        """
        self.indexerUrlsComboBox.clear()

        urls = [indexer.url for indexer in self.application.indexers.list()]
        self.indexerUrlsComboBox.addItems(urls)
        # get current node url from domain
        current_indexer_url = self.application.indexers.get_current_url()
        if current_indexer_url in urls:
            self.indexerUrlsComboBox.setCurrentIndex(urls.index(current_indexer_url))

    def on_indexer_urls_combobox_index_changed(self):
        """
        Triggered when indexer url selection is changed

        :return:
        """
        url = self.indexerUrlsComboBox.currentText()
        if url:
            indexer = self.application.indexers.get(url)
            if indexer is None:
                # get the first one
                url = self.indexerUrlsComboBox.itemText(0)
            self.application.indexers.set_current_url(url)
            if self.application.connections.indexer.is_connected():
                self.application.event_dispatcher.dispatch_event(
                    ConnectionsEvent(ConnectionsEvent.EVENT_TYPE_INDEXER_CONNECTED)
                )
                self.refreshIndexerButton.setEnabled(False)
                self.network_fetch_current_indexer_async_qworker.start()
            else:
                self.application.event_dispatcher.dispatch_event(
                    ConnectionsEvent(ConnectionsEvent.EVENT_TYPE_INDEXER_DISCONNECTED)
                )

    def _on_indexer_connect_button_clicked_event(self):
        """
        Triggered when user click on indexer connect button

        :return:
        """
        self.indexerConnectButton.setDisabled(True)
        self.toggle_indexer_connection_async_qworker.start()

    def toggle_indexer_connection(self):
        """
        Toggle indexer connection

        :return:
        """
        if self.application.connections.indexer.is_connected():
            self.application.connections.indexer.disconnect()
            self.application.event_dispatcher.dispatch_event(
                ConnectionsEvent(ConnectionsEvent.EVENT_TYPE_INDEXER_DISCONNECTED)
            )
        else:
            url = self.indexerUrlsComboBox.currentText()
            if url:
                indexer = self.application.indexers.get(url)
                if indexer is not None:
                    self.application.connections.indexer.connect(indexer)
                    if self.application.connections.indexer.is_connected():
                        self.application.event_dispatcher.dispatch_event(
                            ConnectionsEvent(
                                ConnectionsEvent.EVENT_TYPE_INDEXER_CONNECTED
                            )
                        )

    def _on_finished_toggle_indexer_connection(self):
        """
        Triggered when toggle_indexer_connection is finished

        :return:
        """
        self.indexerConnectButton.setDisabled(False)

    def _on_refresh_indexer_button_clicked_event(self):
        """
        Triggered when user click on refresh indexer button

        :return:
        """
        # Disable button
        self.refreshIndexerButton.setEnabled(False)
        self.network_fetch_current_indexer_async_qworker.start()

    def fetch_indexer_from_network(self):
        """
        Update indexer infos from current url connection

        :return:
        """
        try:
            self.application.indexers.network_fetch_current_indexer()
        except Exception:
            pass

    def _on_finished_fetch_indexer_from_network(self):
        """
        Triggered when async request fetch_indexer_from_network is finished

        :return:
        """
        self.refreshIndexerButton.setEnabled(True)
        self._update_ui()

    def _update_ui(self):
        """
        Update node infos in UI

        :return:
        """
        node_url = self.nodeUrlsComboBox.currentText()
        if node_url:
            node = self.application.nodes.get(node_url)
            if node is None:
                self.softwareValueLabel.setText("")
                self.versionValueLabel.setText("")
                self.peerIDValueLabel.setText("")
                self.nodeBlockValueLabel.setText("?")
                self.epochValueLabel.setText("?")
                self.unsafeAPIExposedValueLabel.setText("")
            else:
                self.softwareValueLabel.setText(node.software)
                self.versionValueLabel.setText(node.software_version)
                self.peerIDValueLabel.setText(node.peer_id)
                self.nodeBlockValueLabel.setText(str(node.block))
                self.epochValueLabel.setText(str(node.epoch_index))
                self.unsafeAPIExposedValueLabel.setText(
                    self._("Yes") if node.unsafe_api_exposed is True else self._("No")
                )

        indexer_url = self.indexerUrlsComboBox.currentText()
        if indexer_url:
            indexer = self.application.indexers.get(indexer_url)
            if indexer is None or indexer.block is None:
                self.indexerBlockValueLabel.setText("?")
            else:
                self.indexerBlockValueLabel.setText(str(indexer.block))

    def _on_currency_event(self, _):
        """
        When a currency event is triggered

        :param _: CurrencyEvent instance
        :return:
        """
        self.init_node_urls()
        self.init_indexer_urls()

    def _on_node_connected(self, _=None):
        """
        Triggered when node is connected

        :return:
        """
        self.nodeConnectButton.setText(self.connected_button_text)
        self.nodeConnectionStatusLabel.setPixmap(QPixmap(ICON_NETWORK_CONNECTED))

    def _on_node_disconnected(self, _=None):
        """
        Triggered when node is disconnected

        :return:
        """
        self.nodeConnectButton.setText(self.disconnected_button_text)
        self.nodeConnectionStatusLabel.setPixmap(QPixmap(ICON_NETWORK_DISCONNECTED))

    def _on_indexer_connected(self, _=None):
        """
        Triggered when indexer is connected

        :return:
        """
        self.indexerConnectButton.setText(self.connected_button_text)
        self.indexerConnectionStatusLabel.setPixmap(QPixmap(ICON_NETWORK_CONNECTED))

    def _on_indexer_disconnected(self, _=None):
        """
        Triggered when indexer is disconnected

        :return:
        """
        self.indexerConnectButton.setText(self.disconnected_button_text)
        self.indexerConnectionStatusLabel.setPixmap(QPixmap(ICON_NETWORK_DISCONNECTED))


if __name__ == "__main__":
    qapp = QApplication(sys.argv)

    application_ = Application(DATA_PATH)

    main_window = QMainWindow()
    main_window.show()

    main_window.setCentralWidget(ConnectionWidget(application_, QMutex(), main_window))

    sys.exit(qapp.exec_())
