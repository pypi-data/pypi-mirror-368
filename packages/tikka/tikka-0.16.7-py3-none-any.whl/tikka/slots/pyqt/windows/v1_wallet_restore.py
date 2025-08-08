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

from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication, QDialog, QLineEdit, QMessageBox, QWidget

from tikka.domains.application import Application
from tikka.domains.entities.account import Account, AccountCryptoType
from tikka.domains.entities.constants import DATA_PATH, WALLETS_PASSWORD_LENGTH
from tikka.libs.keypair import Keypair
from tikka.libs.secret import generate_alphabetic
from tikka.libs.signing_key_v1 import SigningKey
from tikka.slots.pyqt.entities.constants import (
    ADDRESS_MONOSPACE_FONT_NAME,
    DEBOUNCE_TIME,
)
from tikka.slots.pyqt.resources.gui.windows.v1_wallet_restore_rc import (
    Ui_V1WalletRestoreDialog,
)


class V1WalletRestoreWindow(QDialog, Ui_V1WalletRestoreDialog):
    """
    V1WalletRestoreWindow class
    """

    def __init__(
        self,
        application: Application,
        account: Account,
        reset_password: bool = False,
        parent: Optional[QWidget] = None,
    ):
        """
        Init V1 wallet restore window

        :param application: Application instance
        :param account: Account instance
        :param reset_password: Reset password if True (default to False)
        :param parent: QWidget instance
        """
        super().__init__(parent=parent)
        self.setupUi(self)

        self.application = application
        self.account = account
        self.reset_password = reset_password
        self._ = self.application.translator.gettext

        # set monospace font to address fields
        monospace_font = QFont(ADDRESS_MONOSPACE_FONT_NAME)
        monospace_font.setStyleHint(QFont.Monospace)
        self.addressValueLabel.setFont(monospace_font)
        self.v1AddressValueLabel.setFont(monospace_font)

        # buttons
        self.buttonBox.button(self.buttonBox.Ok).setEnabled(False)

        # events
        self.secretIDLineEdit.textChanged.connect(self._on_secret_id_line_edit_changed)
        self.passwordIDLineEdit.textChanged.connect(
            self._on_password_id_line_edit_changed
        )
        self.showButton.clicked.connect(self.on_show_button_clicked)
        self.passwordChangeButton.clicked.connect(self._generate_wallet_password)
        self.buttonBox.accepted.connect(self.on_accepted_button)
        self.buttonBox.rejected.connect(self.close)

        # debounce timer on self._generate_address()
        self.debounce_timer = QTimer()
        self.debounce_timer.timeout.connect(self._generate_address)

        # fill form
        self.storedPasswordFrame.hide()
        self.addressValueLabel.setText(self.account.address)
        self.nameValueLabel.setText(self.account.name)
        self._generate_wallet_password()

    def _on_secret_id_line_edit_changed(self):
        """
        Triggered when text is changed in the secret ID field

        :return:
        """
        if self.debounce_timer.isActive():
            self.debounce_timer.stop()
        self.debounce_timer.start(DEBOUNCE_TIME)

    def _on_password_id_line_edit_changed(self):
        """
        Triggered when text is changed in the password ID field

        :return:
        """
        if self.debounce_timer.isActive():
            self.debounce_timer.stop()
        self.debounce_timer.start(DEBOUNCE_TIME)

    def _generate_address(self):
        """
        Generate address from ID

        :return:
        """
        # stop debounce_timer to avoid infinite loop
        if self.debounce_timer.isActive():
            self.debounce_timer.stop()

        self.v1AddressValueLabel.setText("")
        self.errorLabel.setText("")
        self.buttonBox.button(self.buttonBox.Ok).setEnabled(False)

        secret_id = self.secretIDLineEdit.text().strip()
        password_id = self.passwordIDLineEdit.text().strip()
        if secret_id == "" or password_id == "":
            return

        signing_key = SigningKey.from_credentials(secret_id, password_id)
        try:
            keypair = Keypair.create_from_seed(
                seed_hex=signing_key.seed.hex(),
                ss58_format=self.application.currencies.get_current().ss58_format,
                crypto_type=AccountCryptoType.ED25519,
            )
        except Exception as exception:
            logging.exception(exception)
            self.errorLabel.setText(self._("Error generating account wallet!"))
            return

        address = keypair.ss58_address

        # if credentials address is not account address...
        if address != self.account.address:
            self.errorLabel.setText(
                self._("Generated address is not the account address!")
            )
            self.buttonBox.button(self.buttonBox.Ok).setEnabled(False)
            return

        if self.application.passwords.exists(address) and self.reset_password is False:
            stored_password = self.application.passwords.get_clear_password(keypair)
            self.storedpasswordLineEdit.setText(stored_password)
            self.storedPasswordFrame.show()
            self.passwordFrame.hide()
        else:
            self.storedPasswordFrame.hide()
            self.passwordFrame.show()

        self.v1AddressValueLabel.setText(
            Account(address).get_v1_address(
                self.application.currencies.get_current().ss58_format
            )
        )
        self.buttonBox.button(self.buttonBox.Ok).setEnabled(True)

    def on_show_button_clicked(self):
        """
        Triggered when user click on show button

        :return:
        """
        if self.secretIDLineEdit.echoMode() == QLineEdit.Password:
            self.secretIDLineEdit.setEchoMode(QLineEdit.Normal)
            self.passwordIDLineEdit.setEchoMode(QLineEdit.Normal)
            self.storedpasswordLineEdit.setEchoMode(QLineEdit.Normal)
            self.showButton.setText(self._("Hide"))
        else:
            self.secretIDLineEdit.setEchoMode(QLineEdit.Password)
            self.passwordIDLineEdit.setEchoMode(QLineEdit.Password)
            self.storedpasswordLineEdit.setEchoMode(QLineEdit.Password)
            self.showButton.setText(self._("Show"))

    def _generate_wallet_password(self):
        """
        Generate new password for wallet encryption in UI

        :return:
        """
        self.passwordLineEdit.setText(generate_alphabetic(WALLETS_PASSWORD_LENGTH))

    def on_accepted_button(self):
        """
        Triggered when user click on ok button

        :return:
        """
        secret_id = self.secretIDLineEdit.text().strip()
        password_id = self.passwordIDLineEdit.text().strip()
        password = self.passwordLineEdit.text()
        signing_key = SigningKey.from_credentials(secret_id, password_id)

        keypair = Keypair.create_from_seed(
            seed_hex=signing_key.seed.hex(),
            ss58_format=self.application.currencies.get_current().ss58_format,
            crypto_type=AccountCryptoType.ED25519,
        )
        address = keypair.ss58_address

        # if password exists for root account...
        if self.application.passwords.exists(address) and self.reset_password is False:
            # get stored password
            clear_password = self.application.passwords.get_clear_password(keypair)
            if clear_password is not None:
                password = clear_password
        else:
            # store new password
            self.application.passwords.new(keypair, password)

        wallet = self.application.wallets.get(address)
        if wallet is None:
            # create and store Wallet instance
            wallet = self.application.wallets.create(keypair, password)
            self.application.wallets.add(wallet)
        else:
            # display confirm dialog and get response
            button = QMessageBox.question(
                self,
                self._("Change wallet password?"),
                self._(
                    "A wallet already exists for this account. Change password for {address} wallet?"
                ).format(address=wallet.address),
            )
            if button == QMessageBox.Yes:
                # create and store Wallet instance
                new_wallet = self.application.wallets.create(keypair, password)
                self.application.wallets.update(new_wallet)

        self.account.file_import = False
        self.application.accounts.unlock(self.account, password)


if __name__ == "__main__":
    qapp = QApplication(sys.argv)
    application_ = Application(DATA_PATH)
    account_ = Account(
        "5GAT6CJW8yVKwUuQc7sM5Kk9GZVTpbZYk9PfjNXtvnNgAJZ1",
        name="test name",
        crypto_type=AccountCryptoType.ED25519,
        file_import=True,
    )
    V1WalletRestoreWindow(application_, account_).exec_()
