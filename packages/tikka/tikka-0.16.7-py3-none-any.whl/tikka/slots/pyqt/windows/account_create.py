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
from collections import OrderedDict
from typing import Optional

from mnemonic import Mnemonic
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication, QButtonGroup, QDialog, QWidget

from tikka.domains.application import Application
from tikka.domains.entities.account import AccountCryptoType
from tikka.domains.entities.constants import (
    DATA_PATH,
    MNEMONIC_WORDS_LENGTH,
    WALLETS_PASSWORD_LENGTH,
)
from tikka.libs.keypair import Keypair
from tikka.libs.secret import generate_alphabetic
from tikka.slots.pyqt.entities.constants import ADDRESS_MONOSPACE_FONT_NAME
from tikka.slots.pyqt.resources.gui.windows.account_create_rc import (
    Ui_AccountCreateDialog,
)


class AccountCreateWindow(QDialog, Ui_AccountCreateDialog):
    """
    AccountCreateWindow class
    """

    language_code_map = {
        "en": "english",
        "fr": "french",
        "zh-hans": "chinese_simplified",
        "zh-hant": "chinese_traditional",
        "it": "italian",
        "ja": "japanese",
        "ko": "korean",
        "es": "spanish",
    }

    def __init__(self, application: Application, parent: Optional[QWidget] = None):
        """
        Init create account window

        :param application: Application instance
        :param parent: QWidget instance
        """
        super().__init__(parent=parent)
        self.setupUi(self)

        self.application = application
        self._ = self.application.translator.gettext

        # Mnemonic language selector translated
        mnemonic_language_selector = OrderedDict(
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
        for language_code, language_name in mnemonic_language_selector.items():
            self.mnemonicLanguageComboBox.addItem(language_name, userData=language_code)
        self.mnemonicLanguageComboBox.setCurrentIndex(
            self.mnemonicLanguageComboBox.findData(
                self.application.config.get("language")[:2]
            )
        )
        self.language_code = self.mnemonicLanguageComboBox.currentData()

        self.cryptoTypeGroup = QButtonGroup(self)
        self.cryptoTypeGroup.addButton(self.ed25519RadioButton)
        self.cryptoTypeGroup.addButton(self.sr25519RadioButton)
        self.ed25519RadioButton.setChecked(True)
        self.crypto_type = (
            AccountCryptoType.ED25519
            if self.ed25519RadioButton.isChecked()
            else AccountCryptoType.SR25519
        )

        monospace_font = QFont(ADDRESS_MONOSPACE_FONT_NAME)
        monospace_font.setStyleHint(QFont.Monospace)
        self.addressValueLabel.setFont(monospace_font)

        # hide all password stuff and button box
        self.passwordFrame.hide()
        self.buttonBox.button(self.buttonBox.Ok).setDisabled(True)

        # events
        self.changeButton.clicked.connect(self._generate_mnemonic_and_address)
        self.mnemonicLanguageComboBox.currentIndexChanged.connect(
            self._on_mnemonic_language_combo_box_index_changed
        )
        self.cryptoTypeGroup.buttonClicked.connect(self.on_crypto_type_changed)
        self.passwordChangeButton.clicked.connect(self._generate_wallet_password)
        self.buttonBox.accepted.connect(self.on_accepted_button)
        self.buttonBox.rejected.connect(self.close)
        self.saveMnemonicCheckBox.stateChanged.connect(
            self.on_save_mnemonic_checkbox_state_changed
        )

        # fill form
        self._generate_mnemonic_and_address()
        self._generate_wallet_password()

    def _on_mnemonic_language_combo_box_index_changed(self):
        """
        Triggered when user change mnemonic language selector

        :return:
        """
        old_mnemonic = self.mnemonicLineEdit.text()

        # use mnemonic utilities to get entropy from user language
        mnemonic_util = Mnemonic(self.language_code_map[self.language_code])
        entropy = mnemonic_util.to_entropy(mnemonic_util.normalize_string(old_mnemonic))

        self.language_code = self.mnemonicLanguageComboBox.currentData()

        # get mnemonic in new language from entropy
        mnemonic_util = Mnemonic(self.language_code_map[self.language_code])
        mnemonic = mnemonic_util.to_mnemonic(entropy)

        self.mnemonicLineEdit.setText(mnemonic)

    def _generate_mnemonic_and_address(self):
        """
        Generate mnemonic passphrase and address

        :return:
        """
        mnemonic = Keypair.generate_mnemonic(MNEMONIC_WORDS_LENGTH, self.language_code)
        self.mnemonicLineEdit.setText(mnemonic)

        self._generate_address()

    def _generate_address(self):
        """
        Generate keypair and address

        :return:
        """
        address = Keypair.create_from_uri(
            suri=self.mnemonicLineEdit.text(),
            ss58_format=self.application.currencies.get_current().ss58_format,
            crypto_type=self.crypto_type,
            language_code=self.language_code,
        ).ss58_address
        self.addressValueLabel.setText(address)

    def on_crypto_type_changed(self):
        """
        Triggered when user click on key type radio button

        :return:
        """
        self.crypto_type = (
            AccountCryptoType.ED25519
            if self.ed25519RadioButton.isChecked()
            else AccountCryptoType.SR25519
        )
        self._generate_address()

    def _generate_wallet_password(self):
        """
        Generate new password for wallet encryption in UI

        :return:
        """
        self.passwordLineEdit.setText(generate_alphabetic(WALLETS_PASSWORD_LENGTH))

    def on_save_mnemonic_checkbox_state_changed(self):
        """
        Triggered when user click on save mnemonic remoinder checkbox

        :return:
        """
        self.buttonBox.button(self.buttonBox.Ok).setEnabled(
            self.saveMnemonicCheckBox.isChecked()
        )
        self.passwordFrame.setHidden(not self.saveMnemonicCheckBox.isChecked())

    def on_accepted_button(self):
        """
        Triggered when user click on ok button

        :return:
        """
        mnemonic = self.mnemonicLineEdit.text()
        language_code = self.mnemonicLanguageComboBox.currentData()
        name = self.nameLineEdit.text().strip()
        password = self.passwordLineEdit.text()

        # create derived account + wallet (and the read-only root account)
        self.application.accounts.create_new_account(
            mnemonic, language_code, "", self.crypto_type, name, password
        )

        # close window
        self.close()


if __name__ == "__main__":
    qapp = QApplication(sys.argv)
    application_ = Application(DATA_PATH)
    AccountCreateWindow(application_).exec_()
