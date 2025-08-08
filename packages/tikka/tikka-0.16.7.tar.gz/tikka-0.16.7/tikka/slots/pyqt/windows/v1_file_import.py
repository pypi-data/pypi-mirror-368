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
from pathlib import Path
from typing import TYPE_CHECKING, Optional

from PyQt5.QtCore import QMutex, QTimer
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication, QDialog, QFileDialog, QLineEdit, QWidget

from tikka.domains.application import Application
from tikka.domains.entities.account import Account, AccountCryptoType
from tikka.domains.entities.constants import DATA_PATH, WALLETS_PASSWORD_LENGTH
from tikka.domains.entities.wallet import V1FileWallet
from tikka.libs.keypair import Keypair
from tikka.libs.secret import generate_alphabetic
from tikka.slots.pyqt.entities.constants import (
    ADDRESS_MONOSPACE_FONT_NAME,
    DEBOUNCE_TIME,
    WALLET_LOAD_DEFAULT_DIRECTORY_PREFERENCES_KEY,
)
from tikka.slots.pyqt.entities.worker import AsyncQWorker
from tikka.slots.pyqt.resources.gui.windows.v1_file_import_rc import (
    Ui_V1FileImportDialog,
)

if TYPE_CHECKING:
    pass


class V1FileImportWindow(QDialog, Ui_V1FileImportDialog):
    """
    V1FileImportWindow class
    """

    def __init__(
        self,
        application: Application,
        mutex: QMutex,
        parent: Optional[QWidget] = None,
    ):
        """
        Init V1 import wallet window

        :param application: Application instance
        :param mutex: QMutex instance
        :param parent: QWidget instance
        """
        super().__init__(parent=parent)
        self.setupUi(self)

        self.application = application
        self.v1_file_wallet: Optional[V1FileWallet] = None
        self._ = self.application.translator.gettext
        self.mutex = mutex

        # set monospace font to address fields
        monospace_font = QFont(ADDRESS_MONOSPACE_FONT_NAME)
        monospace_font.setStyleHint(QFont.Monospace)
        self.addressValueLabel.setFont(monospace_font)
        self.v1AddressValueLabel.setFont(monospace_font)

        # events
        self.showButton.clicked.connect(self._on_show_button_clicked)
        self.browseFilesButton.clicked.connect(self._on_browse_files_button_clicked)
        self.filePasswordLineEdit.textChanged.connect(
            self._on_password_line_edit_changed
        )
        self.buttonBox.rejected.connect(self.close)
        self.buttonBox.accepted.connect(self._on_accepted_button)
        self.changeButton.clicked.connect(self._generate_wallet_password)

        # debounce timer
        self.debounce_timer = QTimer()
        self.debounce_timer.timeout.connect(self._load_v1_file_wallet)
        # Create a QWorker object
        self.network_check_legacy_v1_async_qworker = AsyncQWorker(
            self.network_check_legacy_v1, self.mutex
        )
        self.network_check_legacy_v1_async_qworker.finished.connect(
            self._on_finished_network_check_legacy_v1
        )

        # fill form
        self.buttonBox.button(self.buttonBox.Ok).setEnabled(False)
        self._generate_wallet_password()

    def _generate_wallet_password(self):
        """
        Generate new password for wallet encryption in UI

        :return:
        """
        self.passwordLineEdit.setText(generate_alphabetic(WALLETS_PASSWORD_LENGTH))

    def _on_show_button_clicked(self):
        """
        Triggered when user click on show button

        :return:
        """
        if self.filePasswordLineEdit.echoMode() == QLineEdit.Password:
            self.filePasswordLineEdit.setEchoMode(QLineEdit.Normal)
            self.showButton.setText(self._("Hide"))
        else:
            self.filePasswordLineEdit.setEchoMode(QLineEdit.Password)
            self.showButton.setText(self._("Show"))

    def _on_browse_files_button_clicked(self):
        """
        Triggered when user click on browse files button

        :return:
        """
        # clear path
        self.pathValueLabel.setText("")
        self.filePasswordLineEdit.setText("")

        # open file dialog
        filepath = self.open_file_dialog()
        if filepath is not None:
            # update default dir preference
            self.application.repository.preferences.set(
                WALLET_LOAD_DEFAULT_DIRECTORY_PREFERENCES_KEY,
                str(Path(filepath).expanduser().absolute().parent),
            )
            self.pathValueLabel.setText(filepath)

    def _load_v1_file_wallet(self):
        """
        Load V1 file wallet

        :return:
        """
        # stop debounce_timer to avoid infinite loop
        if self.debounce_timer.isActive():
            self.debounce_timer.stop()

        password = self.filePasswordLineEdit.text().strip()
        try:
            self.v1_file_wallet = self.application.repository.v1_file_wallets.load(
                self.pathValueLabel.text(), password
            )
        except Exception:
            self.errorLabel.setText(self._("Unable to decrypt file!"))
            self.buttonBox.button(self.buttonBox.Ok).setEnabled(False)
            return

        if not self.v1_file_wallet.signing_key:
            self.errorLabel.setText(self._("File password is not valid!"))
            self.buttonBox.button(self.buttonBox.Ok).setEnabled(False)
            return

        # wallet decrypted
        keypair = Keypair.create_from_seed(
            seed_hex=self.v1_file_wallet.signing_key.seed.hex(),
            ss58_format=self.application.currencies.get_current().ss58_format,
            crypto_type=AccountCryptoType.ED25519,
        )
        self.v1AddressValueLabel.setText(
            Account(keypair.ss58_address).get_v1_address(
                self.application.currencies.get_current().ss58_format
            )
        )
        self.addressValueLabel.setText(keypair.ss58_address)
        if self.application.accounts.get_by_address(keypair.ss58_address) is not None:
            self.errorLabel.setText(self._("Account already exists!"))
            self.buttonBox.button(self.buttonBox.Ok).setEnabled(False)
        else:
            self.errorLabel.setText("")
            self.network_check_legacy_v1_async_qworker.start()

    def open_file_dialog(self) -> Optional[str]:
        """
        Open file dialog and return the selected filepath or None

        :return:
        """
        default_dir = self.application.repository.preferences.get(
            WALLET_LOAD_DEFAULT_DIRECTORY_PREFERENCES_KEY
        )
        if default_dir is not None:
            default_dir = str(Path(default_dir).expanduser().absolute())
        else:
            default_dir = ""

        result = QFileDialog.getOpenFileName(
            self, self._("Choose wallet file"), default_dir, "EWIF Files (*.dunikey)"
        )
        if result[0] == "":
            return None

        return result[0]

    def _on_password_line_edit_changed(self):
        """
        Triggered when text is changed in the password field

        :return:
        """
        if self.debounce_timer.isActive():
            self.debounce_timer.stop()
        self.debounce_timer.start(DEBOUNCE_TIME)

    def network_check_legacy_v1(self):
        """
        Check if account is really a known legacy v1 account

        :return:
        """
        address = self.addressValueLabel.text().strip()
        try:
            self.is_legacy_v1 = self.application.accounts.network_is_legacy_v1(address)
        except Exception as exception:
            self.errorLabel.setText(self._(str(exception)))
            logging.exception(exception)

    def _on_finished_network_check_legacy_v1(self):
        """
        Triggered when async request network_check_legacy_v1 is finished

        :return:
        """
        if self.is_legacy_v1 is not None:
            if not self.is_legacy_v1:
                self.errorLabel.setText(self._("V1 account unknown!"))
                self.buttonBox.button(self.buttonBox.Ok).setEnabled(False)
            else:
                self.errorLabel.setText("")
                self.buttonBox.button(self.buttonBox.Ok).setEnabled(True)

    def _on_accepted_button(self):
        """
        Triggered when user click on cancel button

        :return:
        """
        if self.v1_file_wallet is None:
            return

        name = self.nameLineEdit.text().strip()
        password = self.passwordLineEdit.text()

        account = self.application.accounts.create_new_root_account_v1_from_seed(
            self.v1_file_wallet.signing_key.seed.hex(), name, password
        )
        if account is not None:
            # set account from file flag
            account.file_import = True
            self.application.accounts.update(account)


if __name__ == "__main__":
    qapp = QApplication(sys.argv)
    application_ = Application(DATA_PATH)
    V1FileImportWindow(application_, QMutex()).exec_()
