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
from PyQt5.QtWidgets import QApplication, QMenu, QMessageBox, QWidget

from tikka.domains.application import Application
from tikka.domains.entities.account import Account
from tikka.domains.entities.constants import DATA_PATH
from tikka.slots.pyqt.windows.account_derivation_create import (
    AccountDerivationCreateWindow,
)
from tikka.slots.pyqt.windows.account_rename import AccountRenameWindow
from tikka.slots.pyqt.windows.account_unlock import AccountUnlockWindow
from tikka.slots.pyqt.windows.transfer import TransferWindow
from tikka.slots.pyqt.windows.v1_wallet_restore import V1WalletRestoreWindow
from tikka.slots.pyqt.windows.v1_wallet_restore_from_file import (
    V1WalletRestoreFromFileWindow,
)
from tikka.slots.pyqt.windows.wallet_restore import WalletRestoreWindow


class AccountPopupMenu(QMenu):
    """
    AccountPopupMenu class
    """

    def __init__(
        self,
        application: Application,
        account: Account,
        mutex: QMutex,
        parent: Optional[QWidget] = None,
    ):
        """
        Init AccountPopupMenu instance

        :param application: Application instance
        :param account: Account instance
        :param mutex: QMutex instance
        :param parent: QWidget instance
        """
        super().__init__(parent=parent)

        self.application = application
        self.account = account
        self.mutex = mutex
        self._ = self.application.translator.gettext

        transfer_to_action = self.addAction(self._("Transfer to"))
        transfer_to_action.triggered.connect(self.transfer_to)
        if self.application.wallets.exists(account.address):
            transfer_from_action = self.addAction(self._("Transfer from"))
            transfer_from_action.triggered.connect(self.transfer_from)

        # menu actions
        copy_address_to_clipboard_action = self.addAction(
            self._("Copy address to clipboard")
        )
        copy_address_to_clipboard_action.triggered.connect(
            self.copy_address_to_clipboard
        )
        if self.application.wallets.exists(account.address):
            if self.application.wallets.is_unlocked(account.address) is False:
                unlock_account_action = self.addAction(self._("Unlock account access"))
                unlock_account_action.triggered.connect(self.unlock_account)
            else:
                lock_account_action = self.addAction(self._("Lock account access"))
                lock_account_action.triggered.connect(self.lock_account)

            wallet_forget_action = self.addAction(self._("Forget the wallet"))
            wallet_forget_action.triggered.connect(self.wallet_forget)
        else:
            wallet_restore_action = self.addAction(self._("Store the wallet"))
            wallet_restore_action.triggered.connect(self.wallet_restore)

        # if account is a root account...
        if self.account.root is None:
            wallet_password_forgotten_action = self.addAction(
                self._("Password forgotten / change")
            )
            wallet_password_forgotten_action.triggered.connect(
                self.wallet_password_forgotten
            )
            create_derived_account_action = self.addAction(
                self._("Create derived account")
            )
            create_derived_account_action.triggered.connect(self.create_derived_account)

        rename_account_action = self.addAction(self._("Rename account"))
        rename_account_action.triggered.connect(self.rename_account)

        forget_account_action = self.addAction(self._("Forget account"))
        forget_account_action.triggered.connect(self.confirm_forget_account)

    def copy_address_to_clipboard(self):
        """
        Copy address of selected row to clipboard

        :return:
        """
        clipboard = QApplication.clipboard()
        clipboard.setText(self.account.address)

    def unlock_account(self):
        """
        Open account unlock window

        :return:
        """
        AccountUnlockWindow(self.application, self.account, self).exec_()

    def transfer_to(self):
        """
        Open transfer window with account as recipient

        :return:
        """
        TransferWindow(
            self.application, self.mutex, None, self.account, parent=self
        ).exec_()

    def transfer_from(self):
        """
        Open transfer window with account as sender

        :return:
        """
        TransferWindow(
            self.application, self.mutex, self.account, None, parent=self
        ).exec_()

    def lock_account(self):
        """
        Lock account

        :return:
        """
        self.application.accounts.lock(self.account)

    def wallet_password_forgotten(self):
        """
        Open wallet restore window to reset wallet password

        :return:
        """
        # if wallet type is V2...
        if self.account.legacy_v1 is False:
            WalletRestoreWindow(self.application, self.account, True).exec_()
        # wallet V1
        else:
            if self.account.file_import is True:
                V1WalletRestoreFromFileWindow(
                    self.application, self.account, True
                ).exec_()
            else:
                V1WalletRestoreWindow(self.application, self.account, True).exec_()

    def wallet_restore(self):
        """
        Open wallet restore window

        :return:
        """
        # if wallet type is V2...
        if self.account.legacy_v1 is False:
            WalletRestoreWindow(self.application, self.account).exec_()
        # wallet V1
        else:
            if self.account.file_import is True:
                V1WalletRestoreFromFileWindow(self.application, self.account).exec_()
            else:
                V1WalletRestoreWindow(self.application, self.account).exec_()

    def wallet_forget(self):
        """
        Forget wallet for this account

        :return:
        """
        # display confirm dialog and get response
        button = QMessageBox.question(
            self,
            self._("Forget wallet"),
            self._("Forget wallet for account {address}?").format(
                address=self.account.address
            ),
        )
        if button == QMessageBox.Yes:
            self.application.accounts.forget_wallet(self.account)

    def create_derived_account(self):
        """
        Open create account derivation window

        :return:
        """
        AccountDerivationCreateWindow(self.application, self.account).exec_()

    def rename_account(self):
        """
        Open rename account window

        :return:
        """
        AccountRenameWindow(self.application, self.account).exec_()

    def confirm_forget_account(self):
        """
        Display confirm dialog then forget account if confirmed

        :return:
        """
        # display confirm dialog and get response
        button = QMessageBox.question(
            self,
            self._("Forget account"),
            self._("Forget account {address} (and derived accounts if any)?").format(
                address=self.account.address
            ),
        )
        if button == QMessageBox.Yes:
            for derived_account in self.application.accounts.get_derivation_accounts(
                self.account.address
            ):
                self.application.accounts.delete(derived_account)
            self.application.accounts.delete(self.account)


if __name__ == "__main__":
    qapp = QApplication(sys.argv)

    application_ = Application(DATA_PATH)
    account_ = Account("732SSfuwjB7jkt9th1zerGhphs6nknaCBCTozxUcPWPU")

    menu = AccountPopupMenu(application_, account_, QMutex())
    menu.exec_()

    sys.exit(qapp.exec_())
