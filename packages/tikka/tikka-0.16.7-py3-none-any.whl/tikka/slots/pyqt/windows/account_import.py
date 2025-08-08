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
from PyQt5.QtCore import QMutex, Qt, QTimer
from PyQt5.QtGui import QFont, QMovie, QPixmap
from PyQt5.QtWidgets import QApplication, QButtonGroup, QDialog, QLineEdit, QWidget

from tikka.domains.application import Application
from tikka.domains.entities.account import AccountCryptoType
from tikka.domains.entities.constants import (
    AMOUNT_UNIT_KEY,
    DATA_PATH,
    WALLETS_PASSWORD_LENGTH,
)
from tikka.domains.entities.identity import Identity, IdentityStatus
from tikka.domains.entities.smith import Smith, SmithStatus
from tikka.libs.keypair import Keypair
from tikka.libs.secret import generate_alphabetic, sanitize_mnemonic_string
from tikka.slots.pyqt.entities.constants import (
    ADDRESS_MONOSPACE_FONT_NAME,
    DEBOUNCE_TIME,
    ICON_IDENTITY_MEMBER,
    ICON_IDENTITY_MEMBER_NOT_VALIDATED,
    ICON_IDENTITY_NOT_MEMBER,
    ICON_LOADER,
    ICON_SMITH,
    SELECTED_UNIT_PREFERENCES_KEY,
)
from tikka.slots.pyqt.entities.worker import AsyncQWorker
from tikka.slots.pyqt.resources.gui.windows.account_import_rc import (
    Ui_AccountImportDialog,
)


class AccountImportWindow(QDialog, Ui_AccountImportDialog):
    """
    AccountImportWindow class
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
        self, application: Application, mutex: QMutex, parent: Optional[QWidget] = None
    ):
        """
        Init import account window

        :param application: Application instance
        :param mutex: QMutex instance
        :param parent: QWidget instance
        """
        super().__init__(parent=parent)
        self.setupUi(self)

        self.application = application
        self._ = self.application.translator.gettext
        self.language_code = "en"
        self.mutex = mutex

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

        self.balance: Optional[int] = None
        self.identity: Optional[Identity] = None
        self.smith: Optional[Smith] = None

        self.display_identity_icon = {
            IdentityStatus.UNCONFIRMED.value: QPixmap(
                ICON_IDENTITY_MEMBER_NOT_VALIDATED
            ),
            IdentityStatus.UNVALIDATED.value: QPixmap(
                ICON_IDENTITY_MEMBER_NOT_VALIDATED
            ),
            IdentityStatus.MEMBER.value: QPixmap(ICON_IDENTITY_MEMBER),
            IdentityStatus.NOT_MEMBER.value: QPixmap(ICON_IDENTITY_NOT_MEMBER),
            IdentityStatus.REVOKED.value: QPixmap(ICON_IDENTITY_NOT_MEMBER),
        }

        # calculate balance display by unit preference
        unit_preference = self.application.repository.preferences.get(
            SELECTED_UNIT_PREFERENCES_KEY
        )
        if unit_preference is not None:
            self.amount = self.application.amounts.get_amount(unit_preference)
        else:
            self.amount = self.application.amounts.get_amount(AMOUNT_UNIT_KEY)

        monospace_font = QFont(ADDRESS_MONOSPACE_FONT_NAME)
        monospace_font.setStyleHint(QFont.Monospace)
        self.addressValueLabel.setFont(monospace_font)

        # animated loading icon
        self.loader_movie = QMovie(ICON_LOADER)
        self.loader_movie.start()
        self.loaderIconLabel.setMovie(self.loader_movie)
        loader_icon_size_policy = self.loaderIconLabel.sizePolicy()
        loader_icon_size_policy.setRetainSizeWhenHidden(True)
        self.loaderIconLabel.setSizePolicy(loader_icon_size_policy)
        self.loaderIconLabel.hide()

        # buttons
        self.buttonBox.button(self.buttonBox.Ok).setEnabled(False)

        self.cryptoTypeGroup = QButtonGroup(self)
        self.cryptoTypeGroup.addButton(self.ed25519RadioButton)
        self.cryptoTypeGroup.addButton(self.sr25519RadioButton)
        self.ed25519RadioButton.setChecked(True)
        self.crypto_type = (
            AccountCryptoType.ED25519
            if self.ed25519RadioButton.isChecked()
            else AccountCryptoType.SR25519
        )

        # events
        self.mnemonicLineEdit.textChanged.connect(self._on_mnemonic_changed)
        self.showButton.clicked.connect(self.on_show_button_clicked)
        self.derivationLineEdit.textChanged.connect(self._on_derivation_changed)
        self.cryptoTypeGroup.buttonClicked.connect(self.on_crypto_type_changed)
        self.passwordChangeButton.clicked.connect(self._generate_wallet_password)
        self.buttonBox.accepted.connect(self.on_accepted_button)
        self.buttonBox.rejected.connect(self.close)

        # debounce timers
        self.mnemonic_debounce_timer = QTimer()
        self.mnemonic_debounce_timer.timeout.connect(self._mnemonic_debounce_call)
        self.derivation_debounce_timer = QTimer()
        self.derivation_debounce_timer.timeout.connect(self._derivation_debounce_call)

        # Create a QWorker object
        self.network_fetch_account_data_async_qworker = AsyncQWorker(
            self.network_fetch_account_data, self.mutex
        )
        self.network_fetch_account_data_async_qworker.finished.connect(
            self._on_finished_network_fetch_account_data
        )

        # fill form
        self.storedPasswordFrame.hide()
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
        # stop mnemonic_debounce_timer to avoid infinite loop
        if self.mnemonic_debounce_timer.isActive():
            self.mnemonic_debounce_timer.stop()

        self.errorLabel.setText("")

        if self.verify_user_entry() is not True:
            return

        try:
            address = self._generate_address()
        except Exception:
            self.errorLabel.setText(self._("Mnemonic or language not valid!"))
            self.buttonBox.button(self.buttonBox.Ok).setEnabled(False)
            return

        if self.address_already_exists(address):
            return

        self._update_wallet_password_fields()

        if self.application.connections.node.is_connected():
            self.loaderIconLabel.show()
            self.network_fetch_account_data_async_qworker.start()

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

    def _on_derivation_changed(self):
        """
        Triggered when user enter text in derivationLineEdit

        :return:
        """
        if self.derivation_debounce_timer.isActive():
            self.derivation_debounce_timer.stop()
        self.derivation_debounce_timer.start(DEBOUNCE_TIME)

    def _derivation_debounce_call(self):
        """
        Debounce function triggered only after idle time when typing derivation

        :return:
        """
        # stop derivation_debounce_timer to avoid infinite loop
        if self.derivation_debounce_timer.isActive():
            self.derivation_debounce_timer.stop()

        self.errorLabel.setText("")

        try:
            address = self._generate_address()
        except Exception:
            self.errorLabel.setText(self._("Derivation is not valid!"))
            self.buttonBox.button(self.buttonBox.Ok).setEnabled(False)
            return

        if self.address_already_exists(address):
            return

        self._update_wallet_password_fields()

        if self.application.connections.node.is_connected():
            self.loaderIconLabel.show()
            self.network_fetch_account_data_async_qworker.start()

    def _update_wallet_password_fields(self):
        """
        Show stored password or new password depending on root account exists or not

        :return:
        """
        # if root account exists, hide the password field
        mnemonic = sanitize_mnemonic_string(self.mnemonicLineEdit.text())
        root_keypair = Keypair.create_from_mnemonic(
            mnemonic=mnemonic,
            language_code=self.language_code,
            crypto_type=self.crypto_type,
            ss58_format=self.application.currencies.get_current().ss58_format,
        )
        if self.application.passwords.exists(root_keypair.ss58_address):
            stored_password = self.application.passwords.get_clear_password(
                root_keypair
            )
            self.storedpasswordLineEdit.setText(stored_password)
            self.storedPasswordFrame.show()
            self.passwordFrame.hide()
        else:
            self.storedPasswordFrame.hide()
            self.passwordFrame.show()

    def on_crypto_type_changed(self):
        """
        Triggered when user click on key type radio button

        :return:
        """
        self.errorLabel.setText("")
        self.crypto_type = (
            AccountCryptoType.ED25519
            if self.ed25519RadioButton.isChecked()
            else AccountCryptoType.SR25519
        )
        if self.mnemonicLineEdit.text().strip() != "":
            address = self._generate_address()
            if not self.address_already_exists(address):
                self.buttonBox.button(self.buttonBox.Ok).setEnabled(True)

    def _generate_address(self) -> str:
        """
        Generate, display and return address

        :return:
        """
        # sanitize mnemonic string
        mnemonic = sanitize_mnemonic_string(self.mnemonicLineEdit.text())

        derivation = self.derivationLineEdit.text().strip()
        address = Keypair.create_from_uri(
            suri=mnemonic + derivation,
            ss58_format=self.application.currencies.get_current().ss58_format,
            crypto_type=self.crypto_type,
            language_code=self.language_code,
        ).ss58_address

        self.addressValueLabel.setText(address)
        return address

    def address_already_exists(self, address: str) -> bool:
        """
        Modify form if address already exists

        :param address: Address to check
        :return:
        """
        if self.application.accounts.get_by_address(address) is not None:
            self.errorLabel.setText(self._("Account already exists!"))
            self.buttonBox.button(self.buttonBox.Ok).setEnabled(False)
            return True

        return False

    def verify_user_entry(self) -> bool:
        """
        Verify user entry, return True if OK, False otherwise

        :return:
        """
        # verify mnemonic
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
            self.addressValueLabel.setText("")
            self.errorLabel.setText(self._("Mnemonic not valid!"))
            self.mnemonicLanguageValueLabel.setText("")
            self.buttonBox.button(self.buttonBox.Ok).setEnabled(False)
            return False

        self.mnemonicLanguageValueLabel.setText(
            self.mnemonic_language_displayed[self.language_code]
        )

        return True

    def _generate_wallet_password(self):
        """
        Generate new password for wallet encryption in UI

        :return:
        """
        self.passwordLineEdit.setText(generate_alphabetic(WALLETS_PASSWORD_LENGTH))

    def network_fetch_account_data(self):
        """
        Fetch account data and
        check if account is really a known legacy v1 account

        :return:
        """
        address = self.addressValueLabel.text().strip()
        self.balance = None
        self.identity = None
        self.smith = None

        try:
            self.balance = self.application.accounts.network_get_balance(address)
        except Exception as exception:
            self.errorLabel.setText(self._(str(exception)))
            logging.exception(exception)
        else:
            try:
                self.identity = self.application.identities.network_get_identity(
                    address
                )
            except Exception as exception:
                self.errorLabel.setText(self._(str(exception)))
                logging.exception(exception)
            else:
                if self.identity is not None:
                    try:
                        self.smith = self.application.smiths.network_get_smith(
                            self.identity.index
                        )
                    except Exception as exception:
                        self.errorLabel.setText(self._(str(exception)))
                        logging.exception(exception)

    def _on_finished_network_fetch_account_data(self):
        """
        Triggered when async request network_fetch_account_data_async_qworker is finished

        :return:
        """
        self.loaderIconLabel.hide()

        if self.balance is not None:
            self.balanceValueLabel.setText(
                self.locale().toCurrencyString(
                    self.amount.value(self.balance), self.amount.symbol()
                )
            )
        else:
            self.balanceValueLabel.setText("?")
        if self.identity:
            self.identityIconLabel.setPixmap(
                self.display_identity_icon[self.identity.status.value].scaled(
                    16, 18, aspectRatioMode=Qt.KeepAspectRatio
                )
            )
            identity_name = self.identity.name or ""
            self.identityNameAndIndexValuelabel.setText(
                f"{identity_name}#{self.identity.index}"
            )
            if self.smith is not None and self.smith.status == SmithStatus.SMITH:
                self.identityIconLabel.setPixmap(
                    QPixmap(ICON_SMITH).scaled(
                        16, 18, aspectRatioMode=Qt.KeepAspectRatio
                    )
                )
        else:
            self.identityNameAndIndexValuelabel.setText("")
            self.identityIconLabel.clear()

        self.buttonBox.button(self.buttonBox.Ok).setEnabled(True)

    def on_accepted_button(self):
        """
        Triggered when user click on ok button

        :return:
        """
        # user inputs
        mnemonic = sanitize_mnemonic_string(self.mnemonicLineEdit.text())
        derivation_ = self.derivationLineEdit.text().strip()
        name = self.nameLineEdit.text().strip()

        # generated inputs
        password = self.passwordLineEdit.text()

        account = self.application.accounts.create_new_account(
            mnemonic, self.language_code, derivation_, self.crypto_type, name, password
        )
        if account:
            if self.balance:
                account.balance = self.balance
                self.application.accounts.update(account)
            if self.identity:
                if self.application.identities.get(self.identity.index) is None:
                    self.application.identities.add(self.identity)
                else:
                    self.application.identities.update(self.identity)
                if self.smith:
                    if self.application.smiths.get(self.identity.index) is None:
                        self.application.smiths.add(self.smith)
                    else:
                        self.application.smiths.update(self.smith)


if __name__ == "__main__":
    qapp = QApplication(sys.argv)
    application_ = Application(DATA_PATH)
    AccountImportWindow(application_, QMutex()).exec_()
