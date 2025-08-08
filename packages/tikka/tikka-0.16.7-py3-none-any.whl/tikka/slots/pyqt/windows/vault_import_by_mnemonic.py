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
from typing import Dict, List, Optional

from mnemonic import Mnemonic
from mnemonic.mnemonic import ConfigurationError
from PyQt5.QtCore import QModelIndex, QMutex, QRect, QSize, Qt, QTimer
from PyQt5.QtGui import (
    QBrush,
    QColor,
    QFont,
    QFontMetrics,
    QIcon,
    QMovie,
    QPainter,
    QPixmap,
)
from PyQt5.QtWidgets import (
    QApplication,
    QButtonGroup,
    QDialog,
    QLineEdit,
    QStyledItemDelegate,
    QStyleOptionViewItem,
    QTableWidgetItem,
    QWidget,
)

from tikka.domains.application import Application
from tikka.domains.entities.account import Account, AccountCryptoType
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
    NUMERIC_DISPLAY_COLOR_BLUE,
    SELECTED_UNIT_PREFERENCES_KEY,
)
from tikka.slots.pyqt.entities.worker import AsyncQWorker
from tikka.slots.pyqt.resources.gui.windows.vault_import_by_mnemonic_rc import (
    Ui_VaultImportByMnemonicDialog,
)


class StyledBalanceItemDelegate(QStyledItemDelegate):
    """
    Class used to display balance and identity icons with custom style
    """

    def paint(
        self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex
    ) -> None:
        if not index.isValid():
            return

        # Configure painter
        painter.save()
        painter.setRenderHint(QPainter.Antialiasing)

        if index.column() == 3:  # Identity icon column
            # Get icon from item data
            icon = index.data(Qt.DecorationRole)

            if icon and not icon.isNull():
                # Calculate icon position (centered)
                icon_size = QSize(16, 16)
                icon_rect = QRect(
                    option.rect.center().x() - icon_size.width() // 2,
                    option.rect.center().y() - icon_size.height() // 2,
                    icon_size.width(),
                    icon_size.height(),
                )

                # Draw icon
                icon.paint(painter, icon_rect)

        elif index.column() == 4:  # Balance column
            balance_text = index.data(Qt.DisplayRole) or ""

            if balance_text:
                # Text metrics
                font_metrics = QFontMetrics(option.font)
                text_width = font_metrics.horizontalAdvance(balance_text)
                text_height = font_metrics.height()

                # Background rectangle dimensions
                padding = 6
                bg_width = text_width + 2 * padding
                bg_height = text_height + 2 * padding

                # Position (right-aligned with small margin)
                bg_rect = QRect(
                    option.rect.right() - bg_width - 2,  # 2px margin from right
                    option.rect.center().y() - bg_height // 2,
                    bg_width,
                    bg_height,
                )

                # Draw background
                painter.setBrush(QBrush(QColor(NUMERIC_DISPLAY_COLOR_BLUE)))
                painter.setPen(Qt.NoPen)
                painter.drawRoundedRect(bg_rect, 10, 10)

                # Draw text
                painter.setPen(Qt.white)
                painter.drawText(bg_rect, Qt.AlignCenter, balance_text)

        painter.restore()

    def sizeHint(self, option, index):
        if not index.isValid():
            return QSize()

        if index.column() == 3:  # Identity icon
            return QSize(24, 24)  # Fixed size for icons

        elif index.column() == 4:  # Balance
            balance_text = index.data(Qt.DisplayRole) or ""
            font_metrics = QFontMetrics(option.font)
            text_width = font_metrics.horizontalAdvance(balance_text)
            text_height = font_metrics.height()

            return QSize(text_width + 12, text_height + 8)  # With padding

        return super().sizeHint(option, index)


class VaultImportByMnemonicWindow(QDialog, Ui_VaultImportByMnemonicDialog):
    """
    VaultImportByMnemonicWindow class
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
        Init import vault by mnemonic window

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
        self.derived_accounts: List[Account] = []
        self.identities: Dict[str, Identity] = {}
        self.smiths: Dict[int, Smith] = {}

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
        self.cryptoTypeGroup = QButtonGroup(self)
        self.cryptoTypeGroup.addButton(self.ed25519RadioButton)
        self.cryptoTypeGroup.addButton(self.sr25519RadioButton)
        self.ed25519RadioButton.setChecked(True)
        self.crypto_type = (
            AccountCryptoType.ED25519
            if self.ed25519RadioButton.isChecked()
            else AccountCryptoType.SR25519
        )
        self.buttonBox.button(self.buttonBox.Ok).setEnabled(False)

        delegate = StyledBalanceItemDelegate()
        self.derivedAccountsTableWidget.setItemDelegateForColumn(3, delegate)
        self.derivedAccountsTableWidget.setItemDelegateForColumn(4, delegate)

        # events
        self.mnemonicLineEdit.textChanged.connect(self._on_mnemonic_changed)
        self.showButton.clicked.connect(self.on_show_button_clicked)
        self.cryptoTypeGroup.buttonClicked.connect(self.on_crypto_type_changed)
        self.passwordChangeButton.clicked.connect(self._generate_wallet_password)
        self.buttonBox.accepted.connect(self.on_accepted_button)
        self.buttonBox.rejected.connect(self.close)

        # debounce timers
        self.mnemonic_debounce_timer = QTimer()
        self.mnemonic_debounce_timer.timeout.connect(self._mnemonic_debounce_call)

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
            self._generate_address()
        except Exception:
            self.errorLabel.setText(self._("Mnemonic or language not valid!"))
            self.buttonBox.button(self.buttonBox.Ok).setEnabled(False)
            return

        self._update_wallet_password_fields()

        self.buttonBox.button(self.buttonBox.Ok).setEnabled(True)

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
        self.crypto_type = (
            AccountCryptoType.ED25519
            if self.ed25519RadioButton.isChecked()
            else AccountCryptoType.SR25519
        )

        try:
            self._generate_address()
        except Exception:
            self.errorLabel.setText(self._("Mnemonic or language not valid!"))
            self.buttonBox.button(self.buttonBox.Ok).setEnabled(False)
            return

        self._update_wallet_password_fields()

        self.buttonBox.button(self.buttonBox.Ok).setEnabled(True)

        if self.application.connections.node.is_connected():
            self.loaderIconLabel.show()
            self.network_fetch_account_data_async_qworker.start()

    def _generate_address(self) -> str:
        """
        Generate, display and return address

        :return:
        """
        # sanitize mnemonic string
        mnemonic = sanitize_mnemonic_string(self.mnemonicLineEdit.text())

        address = Keypair.create_from_uri(
            suri=mnemonic,
            ss58_format=self.application.currencies.get_current().ss58_format,
            crypto_type=self.crypto_type,
            language_code=self.language_code,
        ).ss58_address

        self.addressValueLabel.setText(address)
        return address

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

        mnemonic = sanitize_mnemonic_string(self.mnemonicLineEdit.text())
        self.derived_accounts = self.application.vaults.network_get_derived_accounts(
            address, mnemonic, self.language_code, self.crypto_type
        )
        derived_addresses = [
            derived_account.address for derived_account in self.derived_accounts
        ]
        self.identities = self.application.identities.network_get_identities(
            derived_addresses
        )
        identity_indice = [identity.index for identity in self.identities.values()]
        self.smiths = self.application.smiths.network_get_smiths(identity_indice)

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

        # derived account table
        self.derivedAccountsTableWidget.clear()
        self.derivedAccountsTableWidget.setColumnCount(5)
        self.derivedAccountsTableWidget.setRowCount(len(self.derived_accounts))
        self.derivedAccountsTableWidget.setHorizontalHeaderLabels(
            (
                self._("Derivation"),
                self._("Address"),
                self._("Name"),
                self._("Identity"),
                self._("Balance"),
            )
        )
        row = 0
        for derived_account in self.derived_accounts:
            # derivation
            derivation_item = QTableWidgetItem(derived_account.path)
            self.derivedAccountsTableWidget.setItem(row, 0, derivation_item)

            # address
            address_item = QTableWidgetItem(derived_account.address)
            self.derivedAccountsTableWidget.setItem(row, 1, address_item)

            # name or identity name#index
            existing_account = self.application.accounts.get_by_address(
                derived_account.address
            )
            if existing_account is not None and existing_account.name is not None:
                name_text = existing_account.name
                name_text_color = QColor("black")
            elif derived_account.address in self.identities:
                name_text = f"{self.identities[derived_account.address].name}#{self.identities[derived_account.address].index}"
                name_text_color = QColor("blue")
            else:
                name_text = ""
                name_text_color = QColor("black")
            identity_item = QTableWidgetItem(name_text)
            identity_item.setForeground(name_text_color)
            self.derivedAccountsTableWidget.setItem(row, 2, identity_item)

            if derived_account.address in self.identities:
                # identity icon
                identity_icon_item = QTableWidgetItem()
                identity_icon_item.setIcon(
                    QIcon(
                        self.display_identity_icon[
                            self.identities[derived_account.address].status.value
                        ].scaled(16, 18, aspectRatioMode=Qt.KeepAspectRatio)
                    )
                )
                # smith icon
                if (
                    self.identities[derived_account.address].index in self.smiths
                    and self.smiths[self.identities[derived_account.address].index]
                    is not None
                ):
                    identity_icon_item = QTableWidgetItem()
                    identity_icon_item.setIcon(
                        QIcon(
                            (
                                QPixmap(ICON_SMITH).scaled(
                                    16, 18, aspectRatioMode=Qt.KeepAspectRatio
                                )
                            )
                        )
                    )
                self.derivedAccountsTableWidget.setItem(row, 3, identity_icon_item)

            # balance
            balance_item = QTableWidgetItem(
                self.locale().toCurrencyString(
                    self.amount.value(derived_account.balance), self.amount.symbol()
                )
            )
            self.derivedAccountsTableWidget.setItem(row, 4, balance_item)

            row += 1
        self.derivedAccountsTableWidget.resizeColumnsToContents()

    def on_accepted_button(self):
        """
        Triggered when user click on ok button

        :return:
        """
        # user inputs
        mnemonic = sanitize_mnemonic_string(self.mnemonicLineEdit.text())
        name = self.nameLineEdit.text().strip()
        if name == "":
            name = None

        # generated inputs
        password = self.passwordLineEdit.text()

        root_keypair = Keypair.create_from_uri(
            mnemonic,
            language_code=self.language_code,
            ss58_format=self.application.currencies.get_current().ss58_format,
            crypto_type=self.crypto_type,
        )
        root_account = self.application.accounts.get_by_address(
            root_keypair.ss58_address
        )
        if root_account is None:
            root_account = self.application.accounts.create_new_root_account(
                mnemonic,
                self.language_code,
                self.crypto_type,
                name,
                password,
                add_event=True,
            )

        if root_account:
            if self.balance:
                root_account.balance = self.balance
                self.application.accounts.update(root_account)
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

        for derived_account in self.derived_accounts:
            existing_account = self.application.accounts.get_by_address(
                derived_account.address
            )
            if existing_account is not None:
                existing_account.balance = derived_account.balance
                self.application.accounts.update(existing_account)
            else:
                account = self.application.accounts.create_new_account(
                    mnemonic,
                    self.language_code,
                    derived_account.path,
                    self.crypto_type,
                    "",
                    password,
                    add_event=False,
                )
                account.balance = derived_account.balance
                self.application.accounts.update(account)

        for identity in self.identities.values():
            if identity:
                if self.application.identities.get(identity.index) is None:
                    self.application.identities.add(identity)
                else:
                    self.application.identities.update(identity)
        for smith in self.smiths.values():
            if smith:
                if self.application.smiths.get(smith.identity_index) is None:
                    self.application.smiths.add(smith)
                else:
                    self.application.smiths.update(smith)


if __name__ == "__main__":
    qapp = QApplication(sys.argv)
    application_ = Application(DATA_PATH)
    VaultImportByMnemonicWindow(application_, QMutex()).exec_()
