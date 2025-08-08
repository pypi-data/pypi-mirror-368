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
from collections import OrderedDict
from typing import Optional

from mnemonic import Mnemonic
from mnemonic.mnemonic import ConfigurationError
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication, QDialog, QLineEdit, QMessageBox, QWidget

from tikka.domains.application import Application
from tikka.domains.entities.account import Account, AccountCryptoType
from tikka.domains.entities.constants import DATA_PATH, WALLETS_PASSWORD_LENGTH
from tikka.libs.keypair import Keypair, KeypairType
from tikka.libs.secret import generate_alphabetic, sanitize_mnemonic_string
from tikka.slots.pyqt.entities.constants import (
    ADDRESS_MONOSPACE_FONT_NAME,
    DEBOUNCE_TIME,
)
from tikka.slots.pyqt.resources.gui.windows.wallet_restore_rc import (
    Ui_WalletRestoreDialog,
)


class WalletRestoreWindow(QDialog, Ui_WalletRestoreDialog):
    """
    WalletRestoreWindow class
    """

    language_code_map = {
        "english": "en",
        "french": "fr",
        "chinese_simplified": "zh-hans",
        "chinese_traditional": "zh-hant",
        "italian": "it",
        "japanese": "ja",
        "korean": "ko",
        "spanish": "es",
    }

    def __init__(
        self,
        application: Application,
        account: Account,
        reset_password: bool = False,
        parent: Optional[QWidget] = None,
    ):
        """
        Init import account window

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

        # set monospace font to address field
        monospace_font = QFont(ADDRESS_MONOSPACE_FONT_NAME)
        monospace_font.setStyleHint(QFont.Monospace)
        self.addressValueLabel.setFont(monospace_font)

        # Mnemonic language selector translated
        self.mnemonic_language_displayed = OrderedDict(
            [
                ("en", self._("English")),
                ("fr", self._("French")),
                ("zh-hans", self._("Chinese simplified")),
                ("zh-hant", self._("Chinese traditional")),
                ("it", self._("Italian")),
                ("ja", self._("Japanese")),
                ("ko", self._("Korean")),
                ("es", self._("Spanish")),
            ]
        )

        # buttons
        self.buttonBox.button(self.buttonBox.Ok).setEnabled(False)

        # events
        self.mnemonicLineEdit.textChanged.connect(self._on_mnemonic_changed)
        self.showButton.clicked.connect(self.on_show_button_clicked)
        self.passwordChangeButton.clicked.connect(self._generate_wallet_password)
        self.buttonBox.accepted.connect(self.on_accepted_button)
        self.buttonBox.rejected.connect(self.close)

        # debounce timer
        self.mnemonic_debounce_timer = QTimer()
        self.mnemonic_debounce_timer.timeout.connect(self._mnemonic_debounce_call)

        # fill form
        self.storedPasswordFrame.hide()
        self.derivationValueLabel.setText(self.account.path or "")
        self.addressValueLabel.setText(self.account.address)
        self.nameValueLabel.setText(self.account.name)
        self._generate_wallet_password()

    def _on_mnemonic_changed(self):
        """
        Triggered when mnemonic is changed

        :return:
        """
        if self.mnemonic_debounce_timer.isActive():
            self.mnemonic_debounce_timer.stop()
        self.mnemonic_debounce_timer.start(DEBOUNCE_TIME)

    def _mnemonic_debounce_call(self):
        """
        Debounce function triggered only after idle time when typing mnemonic

        :return:
        """
        self._generate_address()

    def _generate_address(self) -> bool:
        """
        Generate address from mnemonic

        :return:
        """
        # stop debounce_timer to avoid infinite loop
        if self.mnemonic_debounce_timer.isActive():
            self.mnemonic_debounce_timer.stop()

        self.errorLabel.setText("")
        mnemonic = sanitize_mnemonic_string(self.mnemonicLineEdit.text())
        try:
            self.language_code = self.language_code_map[
                Mnemonic.detect_language(mnemonic)
            ]
        except ConfigurationError as exception:
            logging.exception(exception)
            self.addressValueLabel.setText("")
            self.errorLabel.setText(self._("Language not detected"))
            self.mnemonicLanguageValueLabel.setText("")
            self.buttonBox.button(self.buttonBox.Ok).setEnabled(False)
            return False

        if not Keypair.validate_mnemonic(mnemonic, self.language_code):
            self.errorLabel.setText(self._("Mnemonic or language not valid!"))
            self.buttonBox.button(self.buttonBox.Ok).setEnabled(False)
            return False

        self.mnemonicLanguageValueLabel.setText(
            self.mnemonic_language_displayed[self.language_code]
        )

        derivation_path = "" if self.account.path is None else self.account.path
        suri = mnemonic + derivation_path
        if suri == "":
            return False
        try:
            address = Keypair.create_from_uri(
                suri,
                ss58_format=self.application.currencies.get_current().ss58_format,
                crypto_type=self.account.crypto_type or KeypairType.ED25519,
                language_code=self.language_code,
            ).ss58_address
        except Exception as exception:
            logging.exception(exception)
            self.errorLabel.setText(self._("Mnemonic or language not valid!"))
            self.buttonBox.button(self.buttonBox.Ok).setEnabled(False)
            return False

        # if mnemonic address is not account address...
        if address != self.account.address:
            self.errorLabel.setText(
                self._("Mnemonic address is not the account address!")
            )
            self.buttonBox.button(self.buttonBox.Ok).setEnabled(False)
            return False

        # if password exists, hide the password field
        root_keypair = Keypair.create_from_mnemonic(
            mnemonic=mnemonic,
            language_code=self.language_code,
            crypto_type=self.account.crypto_type or KeypairType.ED25519,
            ss58_format=self.application.currencies.get_current().ss58_format,
        )
        if (
            self.application.passwords.exists(root_keypair.ss58_address)
            and self.reset_password is False
        ):
            stored_password = self.application.passwords.get_clear_password(
                root_keypair
            )
            self.storedpasswordLineEdit.setText(stored_password)
            self.storedPasswordFrame.show()
            self.passwordFrame.hide()
        else:
            self.storedPasswordFrame.hide()
            self.passwordFrame.show()

        self.buttonBox.button(self.buttonBox.Ok).setEnabled(True)
        return True

    def on_show_button_clicked(self):
        """
        Triggered when user click on show button

        :return:
        """
        if self.mnemonicLineEdit.echoMode() == QLineEdit.Password:
            self.mnemonicLineEdit.setEchoMode(QLineEdit.Normal)
            self.storedpasswordLineEdit.setEchoMode(QLineEdit.Normal)
            self.showButton.setText(self._("Hide"))
        else:
            self.mnemonicLineEdit.setEchoMode(QLineEdit.Password)
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
        # user inputs
        mnemonic = sanitize_mnemonic_string(self.mnemonicLineEdit.text())
        derivation_path = "" if self.account.path is None else self.account.path
        suri = mnemonic + derivation_path

        # generated inputs
        password = self.passwordLineEdit.text()

        # root keypair for password
        root_keypair = Keypair.create_from_mnemonic(
            mnemonic=mnemonic,
            language_code=self.language_code,
            crypto_type=self.account.crypto_type,
            ss58_format=self.application.currencies.get_current().ss58_format,
        )
        # if password exists for root account...
        if (
            self.application.passwords.exists(root_keypair.ss58_address)
            and self.reset_password is False
        ):
            # get stored password
            clear_password = self.application.passwords.get_clear_password(root_keypair)
            if clear_password is not None:
                password = clear_password
        else:
            # store new password
            self.application.passwords.new(root_keypair, password)

        # update all existing wallets for this root account and his derivation with new password
        if self.reset_password:
            self.application.accounts.reset_password(
                root_keypair, mnemonic, self.language_code, password
            )

        # create keypair from mnemonic to get seed as hexadecimal
        keypair = Keypair.create_from_uri(
            suri,
            language_code=self.language_code,
            crypto_type=self.account.crypto_type,
            ss58_format=self.application.currencies.get_current().ss58_format,
        )

        wallet = self.application.wallets.get(keypair.ss58_address)
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

        self.application.accounts.unlock(self.account, password)


if __name__ == "__main__":
    qapp = QApplication(sys.argv)
    application_ = Application(DATA_PATH)
    account_ = application_.accounts.create_new_account(
        "album cute glance oppose hub fury strategy health dust rebuild trophy magic",
        "en",
        derivation="//2",
        crypto_type=AccountCryptoType.ED25519,
        name="test name",
        password="aaaaaa",
    )
    WalletRestoreWindow(application_, account_).exec_()
