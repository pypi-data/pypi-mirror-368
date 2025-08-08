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

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QMutex
from PyQt5.QtGui import QKeyEvent, QMovie
from PyQt5.QtWidgets import QApplication, QDialog, QWidget

from tikka.adapters.network.node.node import NetworkNode
from tikka.domains.application import Application
from tikka.domains.entities.constants import DATA_PATH
from tikka.domains.entities.events import NodesEvent
from tikka.domains.entities.node import Node
from tikka.slots.pyqt.entities.constants import ICON_LOADER
from tikka.slots.pyqt.entities.worker import AsyncQWorker
from tikka.slots.pyqt.resources.gui.windows.node_add_rc import Ui_nodeAddDialog


class NodeAddWindow(QDialog, Ui_nodeAddDialog):
    """
    NodeAddWindow class
    """

    def __init__(
        self, application: Application, mutex: QMutex, parent: Optional[QWidget] = None
    ):
        """
        Init add node window

        :param application: Application instance
        :param mutex: QMutex instance
        :param parent: QWidget instance
        """
        super().__init__(parent=parent)
        self.setupUi(self)

        self.application = application
        self._ = self.application.translator.gettext

        self.mutex = mutex

        self.network_node_adapter: Optional[NetworkNode] = None
        self.node: Optional[Node] = None
        self.node_prefix: Optional[int] = None
        self.node_genesis_block_hash: Optional[str] = None

        # buttons
        self.buttonBox.button(self.buttonBox.Ok).setEnabled(False)

        # animated loading icon
        self.loader_movie = QMovie(ICON_LOADER)
        self.loader_movie.start()
        self.loaderIconLabel.setMovie(self.loader_movie)
        loader_icon_size_policy = self.loaderIconLabel.sizePolicy()
        loader_icon_size_policy.setRetainSizeWhenHidden(True)
        self.loaderIconLabel.setSizePolicy(loader_icon_size_policy)
        self.loaderIconLabel.hide()

        # events
        self.urlLineEdit.keyPressEvent = self.on_url_line_edit_key_press_event
        self.testButton.clicked.connect(self._on_test_button_clicked)
        self.buttonBox.accepted.connect(self.on_accepted_button)
        self.buttonBox.rejected.connect(self.close)

        ##############################
        # ASYNC METHODS
        ##############################
        # fetch recipient balance
        self.network_get_node_infos_async_qworker = AsyncQWorker(
            self.network_get_node_infos, self.mutex, self
        )
        self.network_get_node_infos_async_qworker.finished.connect(
            self._on_finished_network_get_node_infos
        )

    def on_url_line_edit_key_press_event(self, event: QKeyEvent):
        """
        Triggered when enter is pressed to validate url in url t line edit

        :param event: QKeyEvent instance
        :return:
        """
        if event.key() == QtCore.Qt.Key_Return:
            self._on_test_button_clicked()
        else:
            QtWidgets.QLineEdit.keyPressEvent(self.urlLineEdit, event)
            # if the key is not return, handle normally

    def _on_test_button_clicked(self):
        """
        Run when use click test button

        :return:
        """
        self.loaderIconLabel.show()
        self.testButton.setDisabled(True)
        self.network_get_node_infos_async_qworker.start()

    def network_get_node_infos(self):
        """
        Fetch node infos from the network

        :return:
        """
        url = self.urlLineEdit.text()
        self.network_node_adapter = self.application.nodes.network_get_node_adapter(url)
        if self.network_node_adapter is not None:
            self.node = self.network_node_adapter.get()
            self.node_prefix = self.network_node_adapter.get_ss58_prefix()
            self.node_genesis_block_hash = (
                self.network_node_adapter.get_genesis_block_hash()
            )
        else:
            self.node = None
            self.node_prefix = None
            self.node_genesis_block_hash = None

    def _on_finished_network_get_node_infos(self):
        """
        WHen async network_get_node_infos is finished

        :return:
        """
        self.testButton.setDisabled(False)
        self.loaderIconLabel.hide()

        if self.node is None:
            self.softwareValueLabel.setText("")
            self.versionValueLabel.setText("")
            self.peerIDValueLabel.setText("")
            self.blockValueLabel.setText("")
            self.currencyHashValueLabel.setText("")
            self.currencyPrefixValueLabel.setText("")
            self.errorLabel.setText(self._("Impossible to connect"))
            self.buttonBox.button(self.buttonBox.Ok).setEnabled(False)
        else:
            self.errorLabel.setText("")
            self.softwareValueLabel.setText(self.node.software)
            self.versionValueLabel.setText(self.node.software_version)
            self.peerIDValueLabel.setText(self.node.peer_id)
            self.blockValueLabel.setText(str(self.node.block))
            self.currencyPrefixValueLabel.setText(str(self.node_prefix))
            self.currencyHashValueLabel.setText(self.node_genesis_block_hash)
            self.buttonBox.button(self.buttonBox.Ok).setEnabled(True)

            if (
                self.node_genesis_block_hash
                != self.application.currencies.get_current().genesis_hash
            ):
                self.errorLabel.setText(
                    self._("Current genesis hash is\n{hash}").format(
                        hash=self.application.currencies.get_current().genesis_hash
                    )
                )
                self.buttonBox.button(self.buttonBox.Ok).setEnabled(False)
            elif (
                self.node_prefix
                != self.application.currencies.get_current().ss58_format
            ):
                self.errorLabel.setText(
                    self._("Current currency prefix is {currency_prefix}").format(
                        currency_prefix=self.application.currencies.get_current().ss58_format
                    )
                )
                self.buttonBox.button(self.buttonBox.Ok).setEnabled(False)

    def on_accepted_button(self) -> None:
        """
        Triggered when user click on ok button

        :return:
        """
        url = self.urlLineEdit.text()
        if self.application.nodes.get(url) is not None:
            return

        self.application.nodes.add(
            Node(
                url=self.urlLineEdit.text(),
                peer_id=self.peerIDValueLabel.text(),
                block=int(self.blockValueLabel.text()),
                software=self.softwareValueLabel.text(),
                software_version=self.versionValueLabel.text(),
            )
        )

        self.application.event_dispatcher.dispatch_event(
            NodesEvent(NodesEvent.EVENT_TYPE_LIST_CHANGED)
        )


if __name__ == "__main__":
    qapp = QApplication(sys.argv)
    application_ = Application(DATA_PATH)
    NodeAddWindow(application_, QMutex()).exec_()
