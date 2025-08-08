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
import datetime
import sys
from typing import Optional

from PyQt5.QtCore import QMutex
from PyQt5.QtWidgets import QApplication, QMenu, QWidget

from tikka.domains.application import Application
from tikka.domains.entities.account import Account
from tikka.domains.entities.constants import DATA_PATH
from tikka.domains.entities.transfer import Transfer
from tikka.slots.pyqt.windows.transfer import TransferWindow
from tikka.slots.pyqt.windows.transfers_export import TransfersExportWindow


class TransferHistoryPopupMenu(QMenu):
    """
    TransferHistoryPopupMenu class
    """

    def __init__(
        self,
        application: Application,
        account: Account,
        transfer: Transfer,
        mutex: QMutex,
        parent: Optional[QWidget] = None,
    ):
        """
        Init TransferHistoryPopupMenu instance

        :param application: Application instance
        :param account: Account instance
        :param transfer: Transfer instance
        :param mutex: QMutex instance
        :param parent: QWidget instance
        """
        super().__init__(parent=parent)

        self.application = application
        self.account = account
        self.transfer = transfer
        self.mutex = mutex
        self._ = self.application.translator.gettext

        self.contact_address = (
            self.transfer.issuer_address
            if self.transfer.issuer_address != self.account.address
            else self.transfer.receiver_address
        )
        self.contact_identity_name = (
            self.transfer.issuer_identity_name
            if self.transfer.issuer_address != self.account.address
            else self.transfer.receiver_identity_name
        )
        self.contact_identity_index = (
            self.transfer.issuer_identity_index
            if self.transfer.issuer_address != self.account.address
            else self.transfer.receiver_identity_index
        )

        if self.application.wallets.exists(self.account.address):
            transfer_to_action = self.addAction(self._("Transfer to"))
            transfer_to_action.triggered.connect(self.transfer_to)
        if self.application.wallets.exists(self.contact_address):
            transfer_from_action = self.addAction(self._("Transfer from"))
            transfer_from_action.triggered.connect(self.transfer_from)

        # menu actions
        copy_address_to_clipboard_action = self.addAction(
            self._("Copy address to clipboard")
        )
        copy_address_to_clipboard_action.triggered.connect(
            self.copy_address_to_clipboard
        )

        self.contact_account = self.application.accounts.get_by_address(
            self.contact_address
        )
        if self.contact_account is None:
            add_account_address_action = self.addAction(
                self._("Add address to accounts")
            )
            add_account_address_action.triggered.connect(self.add_address_to_accounts)

        if self.application.connections.indexer.is_connected():
            export_ofx_action = self.addAction(self._("Export in OFX file"))
            export_ofx_action.triggered.connect(self.export_ofx)

    def copy_address_to_clipboard(self):
        """
        Copy address of selected row to clipboard

        :return:
        """
        clipboard = QApplication.clipboard()
        clipboard.setText(self.contact_address)

    def transfer_to(self):
        """
        Open transfer window with account as recipient

        :return:
        """
        if self.contact_account is None:
            self.contact_account = Account(
                self.contact_address,
                f"{self.contact_identity_name}#{self.contact_identity_index}",
            )

        TransferWindow(
            self.application,
            self.mutex,
            self.account,
            self.contact_account,
            parent=self,
        ).exec_()

    def transfer_from(self):
        """
        Open transfer window with account as sender

        :return:
        """
        TransferWindow(
            self.application,
            self.mutex,
            self.contact_account,
            self.account,
            parent=self,
        ).exec_()

    def add_address_to_accounts(self):
        """
        Add a new account from contact address

        :return:
        """
        self.contact_account = Account(self.contact_address)

        self.application.accounts.add(self.contact_account)

    def export_ofx(self):
        """
        Export transfers in an OFX file

        :return:
        """
        TransfersExportWindow(
            self.application, self.account.address, self.parentWidget()
        ).exec_()


if __name__ == "__main__":
    qapp = QApplication(sys.argv)

    application_ = Application(DATA_PATH)
    account_ = Account("732SSfuwjB7jkt9th1zerGhphs6nknaCBCTozxUcPWPU")
    transfer = Transfer(
        "id",
        "XXXX",
        1,
        "name issuer",
        "YYY",
        2,
        "name receiver",
        1000,
        datetime.datetime.now(),
        "comment",
        "ASCII",
    )
    menu = TransferHistoryPopupMenu(application_, account_, transfer, QMutex())
    menu.exec_()

    sys.exit(qapp.exec_())
