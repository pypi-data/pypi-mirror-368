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
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QKeyEvent
from PyQt5.QtWidgets import QApplication, QDialog, QLineEdit, QWidget

from tikka.domains.application import Application
from tikka.domains.entities.account import Account, AccountCryptoType
from tikka.domains.entities.constants import DATA_PATH
from tikka.libs.keypair import Keypair, KeypairType
from tikka.libs.secret import sanitize_mnemonic_string
from tikka.slots.pyqt.entities.constants import (
    ADDRESS_MONOSPACE_FONT_NAME,
    DEBOUNCE_TIME,
)
from tikka.slots.pyqt.resources.gui.windows.account_derivation_create_rc import (
    Ui_AccountDerivationCreateDialog,
)


class AccountDerivationCreateWindow(QDialog, Ui_AccountDerivationCreateDialog):
    """
    AccountDerivationCreateWindow class
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
        parent: Optional[QWidget] = None,
    ):
        """
        Init import account window

        :param application: Application instance
        :param account: Account instance
        :param parent: QWidget instance
        """
        super().__init__(parent=parent)
        self.setupUi(self)

        self.application = application
        self.account = account
        self._ = self.application.translator.gettext
        self.keypair = None
        self.password = None

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

        # derivation selector
        for derivation_path in self.application.accounts.get_available_derivation_list(
            self.account
        ):
            self.derivationComboBox.addItem(derivation_path, userData=derivation_path)
        monospace_font = QFont(ADDRESS_MONOSPACE_FONT_NAME)
        monospace_font.setStyleHint(QFont.Monospace)
        self.addressValueLabel.setFont(monospace_font)
        self.rootAddressValueLabel.setFont(monospace_font)

        # buttons
        self.buttonBox.button(self.buttonBox.Ok).setEnabled(False)

        # events
        self.mnemonicLineEdit.textChanged.connect(self._on_mnemonic_changed)
        self.showButton.clicked.connect(self.on_show_button_clicked)
        self.derivationComboBox.lineEdit().keyPressEvent = (
            self._on_derivation_keypress_event
        )
        self.derivationComboBox.currentIndexChanged.connect(self._generate_address)
        self.buttonBox.accepted.connect(self.on_accepted_button)
        self.buttonBox.rejected.connect(self.close)

        # debounce timer
        self.mnemonic_debounce_timer = QTimer()
        self.mnemonic_debounce_timer.timeout.connect(self._mnemonic_debounce_call)

        # fill form
        self.rootAddressValueLabel.setText(self.account.address)

    def _on_derivation_keypress_event(self, event: QKeyEvent):
        """

        :param event:
        :return:
        """
        if event.key() == Qt.Key_Return:
            return
        # if the key is not return, handle normally
        QLineEdit.keyPressEvent(self.derivationComboBox.lineEdit(), event)
        self._generate_address()

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
        # stop mnemonic_debounce_timer to avoid infinite loop
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

        self.mnemonicLanguageValueLabel.setText(
            self.mnemonic_language_displayed[self.language_code]
        )

        derivation_path = self.derivationComboBox.currentText()
        suri = mnemonic + derivation_path
        if not Keypair.validate_mnemonic(mnemonic, self.language_code):
            self.errorLabel.setText(self._("Mnemonic or language not valid!"))
            self.buttonBox.button(self.buttonBox.Ok).setEnabled(False)
            return False

        try:
            root_keypair = Keypair.create_from_mnemonic(
                mnemonic=mnemonic,
                ss58_format=self.application.currencies.get_current().ss58_format,
                crypto_type=self.account.crypto_type,
                language_code=self.language_code,
            )
        except Exception as exception:
            logging.exception(exception)
            self.errorLabel.setText(self._("Mnemonic or language not valid!"))
            self.buttonBox.button(self.buttonBox.Ok).setEnabled(False)
            return False

        # if mnemonic address is not account address...
        if root_keypair.ss58_address != self.account.address:
            self.errorLabel.setText(
                self._("Mnemonic address is not the root account address!")
            )
            self.buttonBox.button(self.buttonBox.Ok).setEnabled(False)
            return False

        try:
            self.keypair = Keypair.create_from_uri(  # type: ignore
                suri=suri,
                ss58_format=self.application.currencies.get_current().ss58_format,
                crypto_type=self.account.crypto_type or KeypairType.ED25519,
                language_code=self.language_code,
            )
        except Exception as exception:
            logging.exception(exception)
            self.errorLabel.setText(self._("Mnemonic or language not valid!"))
            self.buttonBox.button(self.buttonBox.Ok).setEnabled(False)
            return False

        if self.keypair is not None:
            self.addressValueLabel.setText(self.keypair.ss58_address)

            if (
                self.application.accounts.get_by_address(self.keypair.ss58_address)
                is not None
            ):
                self.errorLabel.setText(self._("Account already exists!"))
                self.buttonBox.button(self.buttonBox.Ok).setEnabled(False)
                return False

            stored_password = self.application.passwords.get_clear_password(
                root_keypair
            )
            self.storedpasswordLineEdit.setText(stored_password)
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

    def on_accepted_button(self):
        """
        Triggered when user click on ok button

        :return:
        """
        # user inputs
        mnemonic = sanitize_mnemonic_string(self.mnemonicLineEdit.text())
        derivation_path = self.derivationComboBox.currentText()
        name = self.nameLineEdit.text().strip()

        # generated inputs
        root_keypair = Keypair.create_from_mnemonic(
            mnemonic=mnemonic,
            language_code=self.language_code,
            crypto_type=self.account.crypto_type,
            ss58_format=self.application.currencies.get_current().ss58_format,
        )
        password = self.application.passwords.get_clear_password(root_keypair)
        assert password is not None

        # create derived account + wallet (and the read-only root account if not exists)
        self.application.accounts.create_new_account(
            mnemonic,
            self.language_code,
            derivation_path,
            self.account.crypto_type,
            name,
            password,
        )


if __name__ == "__main__":
    qapp = QApplication(sys.argv)
    application_ = Application(DATA_PATH)
    account_ = application_.accounts.create_new_root_account(
        "album cute glance oppose hub fury strategy health dust rebuild trophy magic",
        "en",
        AccountCryptoType.ED25519,
        "test root account",
        "aaaaaa",
    )
    assert account_ is not None
    AccountDerivationCreateWindow(application_, account_).exec_()
