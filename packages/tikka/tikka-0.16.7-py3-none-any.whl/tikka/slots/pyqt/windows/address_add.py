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

from PyQt5.QtCore import QMutex, Qt, QTimer
from PyQt5.QtGui import QFont, QMovie, QPixmap
from PyQt5.QtWidgets import QApplication, QDialog, QWidget
from scalecodec.utils.ss58 import is_valid_ss58_address

from tikka.domains.application import Application
from tikka.domains.entities.account import Account, AccountCryptoType
from tikka.domains.entities.address import DisplayAddress
from tikka.domains.entities.constants import AMOUNT_UNIT_KEY, DATA_PATH
from tikka.domains.entities.identity import Identity, IdentityStatus
from tikka.domains.entities.smith import Smith, SmithStatus
from tikka.libs import crypto_type
from tikka.libs.keypair import Keypair
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
from tikka.slots.pyqt.resources.gui.windows.address_add_rc import Ui_AddressAddDialog


class AddressAddWindow(QDialog, Ui_AddressAddDialog):
    """
    AddressAddWindow class
    """

    display_crypto_type = {
        AccountCryptoType.ED25519: "ED25519",
        AccountCryptoType.SR25519: "SR25519",
    }

    def __init__(
        self, application: Application, mutex: QMutex, parent: Optional[QWidget] = None
    ):
        """
        Init add address window

        :param application: Application instance
        :param mutex: QMutex instance
        :param parent: QWidget instance
        """
        super().__init__(parent=parent)
        self.setupUi(self)

        self.application = application
        self._ = self.application.translator.gettext
        self.mutex = mutex

        self.crypto_type = AccountCryptoType.ED25519

        self.address: Optional[str] = None
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

        # set monospace font to address field
        monospace_font = QFont(ADDRESS_MONOSPACE_FONT_NAME)
        monospace_font.setStyleHint(QFont.Monospace)
        self.addressLineEdit.setFont(monospace_font)

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

        # events
        self.buttonBox.accepted.connect(self.on_accepted_button)
        self.addressLineEdit.textChanged.connect(self.on_address_line_edit_changed)
        self.buttonBox.rejected.connect(self.close)

        # debounce timers
        self.address_debounce_timer = QTimer()
        self.address_debounce_timer.timeout.connect(self._address_debounce_call)

        # Create a QWorker object
        self.network_fetch_account_data_async_qworker = AsyncQWorker(
            self.network_fetch_account_data, self.mutex
        )
        self.network_fetch_account_data_async_qworker.finished.connect(
            self._on_finished_network_fetch_account_data
        )

    def on_address_line_edit_changed(self) -> None:
        """
        Triggered when address line edit is changed

        :return:
        """
        if self.address_debounce_timer.isActive():
            self.address_debounce_timer.stop()
        self.address_debounce_timer.start(DEBOUNCE_TIME)

    def _address_debounce_call(self):
        """
        Debounce function triggered only after idle time when typing address

        :return:
        """
        # stop mnemonic_debounce_timer to avoid infinite loop
        if self.address_debounce_timer.isActive():
            self.address_debounce_timer.stop()

        self._check_address_validity()

        if self.address and self.application.connections.node.is_connected():
            self.loaderIconLabel.show()
            self.network_fetch_account_data_async_qworker.start()

    def _check_address_validity(self) -> Optional[DisplayAddress]:
        """
        Validate address and store it if valid

        :return:
        """

        self.errorLabel.setText("")
        self.address = None
        address = self.addressLineEdit.text().strip()
        if not is_valid_ss58_address(address):
            self.errorLabel.setText(self._("Account address is not valid!"))
            self.keyTypeValueLabel.setText("?")
            self.buttonBox.button(self.buttonBox.Ok).setEnabled(False)
            return None

        if self.application.accounts.get_by_address(address) is not None:
            self.errorLabel.setText(self._("Account already exists!"))
            self.buttonBox.button(self.buttonBox.Ok).setEnabled(False)
            return None

        keypair = Keypair(address)
        try:
            result = crypto_type.is_valid_ed25519(keypair.public_key)
        except AttributeError:
            result = False
        except AssertionError:
            result = False

        if result is True:
            self.crypto_type = AccountCryptoType.ED25519
            self.keyTypeValueLabel.setText(
                self.display_crypto_type[AccountCryptoType.ED25519]
            )
        else:
            try:
                result = crypto_type.is_valid_sr25519(keypair.public_key)
            except AttributeError:
                result = False
            except AssertionError:
                result = False
            if result is True:
                self.crypto_type = AccountCryptoType.SR25519
                self.keyTypeValueLabel.setText(
                    self.display_crypto_type[AccountCryptoType.SR25519]
                )

        self.address = address
        self.buttonBox.button(self.buttonBox.Ok).setEnabled(True)
        return None

    def network_fetch_account_data(self):
        """
        Fetch account data and
        check if account is really a known legacy v1 account

        :return:
        """
        address = self.address
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

    def on_accepted_button(self) -> None:
        """
        Triggered when user click on ok button

        :return:
        """
        if self.address is not None:
            name = self.nameLineEdit.text().strip()

            # create account instance
            account = Account(
                address=self.address, name=name, crypto_type=self.crypto_type
            )

            if self.balance:
                account.balance = self.balance

            self.application.accounts.add(account)

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
    AddressAddWindow(application_, QMutex()).exec_()
