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
from typing import Dict, Optional, OrderedDict

from PyQt5.QtCore import QMutex, Qt
from PyQt5.QtGui import QFont, QMovie
from PyQt5.QtWidgets import QApplication, QCompleter, QDialog, QWidget
from scalecodec.utils.ss58 import is_valid_ss58_address

from tikka.domains.application import Application
from tikka.domains.entities.account import Account, AccountCryptoType
from tikka.domains.entities.constants import AMOUNT_UNIT_KEY, DATA_PATH
from tikka.libs.keypair import Keypair
from tikka.slots.pyqt.entities.constants import (
    ADDRESS_MONOSPACE_FONT_NAME,
    ICON_LOADER,
    SELECTED_UNIT_PREFERENCES_KEY,
    TRANSFER_RECIPIENT_ADDRESS_PREFERENCES_KEY,
    TRANSFER_SENDER_ADDRESS_PREFERENCES_KEY,
)
from tikka.slots.pyqt.entities.worker import AsyncQWorker
from tikka.slots.pyqt.resources.gui.windows.transfer_rc import Ui_TransferDialog
from tikka.slots.pyqt.windows.account_unlock import AccountUnlockWindow


class TransferWindow(QDialog, Ui_TransferDialog):
    """
    TransferWindow class
    """

    def __init__(
        self,
        application: Application,
        mutex: QMutex,
        sender: Optional[Account] = None,
        recipient: Optional[Account] = None,
        parent: Optional[QWidget] = None,
    ):
        """
        Init transfer window

        :param application: Application instance
        :param mutex: QMutex instance
        :param sender: Sender Account instance or None
        :param recipient: Recipient Account instance or None
        :param parent: QWidget instance
        """
        super().__init__(parent=parent)
        self.setupUi(self)

        self.application = application

        preferences_sender_address = self.application.repository.preferences.get(
            TRANSFER_SENDER_ADDRESS_PREFERENCES_KEY
        )
        if sender is None and preferences_sender_address is not None:
            preferences_sender_account = self.application.accounts.get_by_address(
                preferences_sender_address
            )
            if preferences_sender_account is not None:
                sender = preferences_sender_account

        preferences_recipient_address = self.application.repository.preferences.get(
            TRANSFER_RECIPIENT_ADDRESS_PREFERENCES_KEY
        )
        if recipient is None and preferences_recipient_address is not None:
            preferences_recipient_account = self.application.accounts.get_by_address(
                preferences_recipient_address
            )
            if preferences_recipient_account is not None:
                recipient = preferences_recipient_account

        self.sender_account = sender
        self.recipient_account = recipient
        self.mutex = mutex
        self._ = self.application.translator.gettext

        # substrate error message for gettext extraction
        self._("Transfer/payment would kill account")
        self._("Balance too low to send value")

        self.monospace_font = QFont(ADDRESS_MONOSPACE_FONT_NAME)
        self.monospace_font.setStyleHint(QFont.Monospace)

        # init unit from preference or default
        unit_preference = self.application.repository.preferences.get(
            SELECTED_UNIT_PREFERENCES_KEY
        )
        if unit_preference is not None:
            self.unit = unit_preference
        else:
            self.unit = AMOUNT_UNIT_KEY

        self.init_units()

        self.amount_value = 0
        self.fees = None
        self.transfer_success: Optional[bool] = None

        if self.sender_account is not None:
            if self.sender_account.name is None:
                self.senderNameOrAddressLineEdit.setText(self.sender_account.address)
                self.senderNameOrAddressLineEdit.setFont(self.monospace_font)
                self.senderNameOrAddressValueLabel.setText("")
            else:
                self.senderNameOrAddressLineEdit.setText(self.sender_account.name)
                self.senderNameOrAddressLineEdit.setFont(QFont())
                self.senderNameOrAddressValueLabel.setText(self.sender_account.address)
                self.senderNameOrAddressValueLabel.setFont(self.monospace_font)

        if self.recipient_account is not None:
            if self.recipient_account.name is None:
                self.recipientNameOrAddressLineEdit.setText(
                    self.recipient_account.address
                )
                self.recipientNameOrAddressLineEdit.setFont(self.monospace_font)
                self.recipientNameOrAddressValueLabel.setText("")
            else:
                self.recipientNameOrAddressLineEdit.setText(self.recipient_account.name)
                self.recipientNameOrAddressLineEdit.setFont(QFont())
                self.recipientNameOrAddressValueLabel.setText(
                    self.recipient_account.address
                )
                self.recipientNameOrAddressValueLabel.setFont(self.monospace_font)

        # animated loading icon
        self.loader_movie = QMovie(ICON_LOADER)
        self.loader_movie.start()
        self.loaderIconLabel.setMovie(self.loader_movie)
        loader_icon_size_policy = self.loaderIconLabel.sizePolicy()
        loader_icon_size_policy.setRetainSizeWhenHidden(True)
        self.loaderIconLabel.setSizePolicy(loader_icon_size_policy)
        self.loaderIconLabel.hide()

        # autocomplete  (dirty version)
        # todo: create a model to fetch only a filtered list from database on edit
        self.account_address_by_name: Dict[str, str] = {}
        account_address_by_name_duplicate_count = 2
        for account_instance in self.application.accounts.get_list():
            if (
                account_instance.name in self.account_address_by_name
                and account_instance.name is not None
            ):
                self.account_address_by_name[
                    f"{account_instance.name} ({account_address_by_name_duplicate_count})"
                ] = account_instance.address
                account_address_by_name_duplicate_count += 1
            else:
                if account_instance.name is None:
                    self.account_address_by_name[
                        account_instance.address
                    ] = account_instance.address
                else:
                    self.account_address_by_name[
                        account_instance.name
                    ] = account_instance.address

        identities_by_address = self.application.identities.get_by_addresses(
            list(self.account_address_by_name.values())
        )
        for address, identity in identities_by_address.items():
            if identity is not None:
                if identity.name in self.account_address_by_name:
                    self.account_address_by_name[
                        f"{identity.name} ({account_address_by_name_duplicate_count})"
                    ] = address
                    account_address_by_name_duplicate_count += 1
                if identity.name is not None:
                    self.account_address_by_name[identity.name] = address

        # sender autocomplete only on accounts with wallet
        self.sender_account_wordlist = []
        for account_name, account_address in self.account_address_by_name.items():
            if account_address in self.application.wallets.list_addresses():
                self.sender_account_wordlist.append(account_name)
                self.sender_account_wordlist.append(account_address)
        sender_completer = QCompleter(self.sender_account_wordlist)
        self.senderNameOrAddressLineEdit.setCompleter(sender_completer)
        self.senderNameOrAddressLineEdit.completer().setCaseSensitivity(
            Qt.CaseInsensitive
        )

        # recipient autocomplete
        self.recipient_account_wordlist = list(
            self.account_address_by_name.keys()
        ) + list(self.account_address_by_name.values())
        self.recipient_account_wordlist = list(
            OrderedDict.fromkeys(self.recipient_account_wordlist)
        )
        recipient_completer = QCompleter(self.recipient_account_wordlist)
        self.recipientNameOrAddressLineEdit.setCompleter(recipient_completer)
        self.recipientNameOrAddressLineEdit.completer().setCaseSensitivity(
            Qt.CaseInsensitive
        )

        self._update_ui()

        # events
        self.senderNameOrAddressLineEdit.textChanged.connect(
            self._on_sender_address_line_edit_changed
        )
        self.recipientNameOrAddressLineEdit.textChanged.connect(
            self._on_recipient_address_line_edit_changed
        )
        self.amountDoubleSpinBox.valueChanged.connect(
            self._on_amount_double_spin_box_changed
        )
        self.amountUnitComboBox.activated.connect(self._on_unit_changed)
        self.feesButton.clicked.connect(self._on_fees_button_clicked)
        self.sendButton.clicked.connect(self._on_send_button_clicked)
        self.buttonBox.button(self.buttonBox.Close).clicked.connect(self.close)

        ##############################
        # ASYNC METHODS
        ##############################
        # fetch recipient balance
        self.fetch_recipient_balance_from_network_async_qworker = AsyncQWorker(
            self.fetch_recipient_balance_from_network, self.mutex, self
        )
        self.fetch_recipient_balance_from_network_async_qworker.finished.connect(
            self._on_finished_fetch_recipient_balance_from_network
        )
        # fetch sender balance
        self.fetch_sender_balance_from_network_async_qworker = AsyncQWorker(
            self.fetch_sender_balance_from_network, self.mutex, self
        )
        self.fetch_sender_balance_from_network_async_qworker.finished.connect(
            self._on_finished_fetch_sender_balance_from_network
        )

        # fetch fees from network
        self.fetch_fees_from_network_async_qworker = AsyncQWorker(
            self.fetch_fees_from_network, self.mutex, self
        )
        self.fetch_fees_from_network_async_qworker.finished.connect(
            self._on_finished_fetch_fees_from_network
        )
        # send transfer to network
        self.send_tranfer_to_network_async_qworker = AsyncQWorker(
            self.send_transfer_to_network, self.mutex, self
        )
        self.send_tranfer_to_network_async_qworker.finished.connect(
            self._on_finished_send_transfer_to_network
        )

        # Receiver is a history account, not stored...
        if (
            self.recipient_account is not None
            and self.application.accounts.get_by_address(self.recipient_account.address)
            is None
        ):
            # get balance from node
            self.fetch_recipient_balance_from_network_async_qworker.start()

    def _on_unit_changed(self):
        """
        Triggered when unit combo box is changed

        :return:
        """
        self.unit = self.amountUnitComboBox.currentData()
        self._update_ui()

    def _on_amount_double_spin_box_changed(self):
        """
        Triggered when the amount spin box is changed

        :return:
        """
        self.amount_value = self.amountDoubleSpinBox.value()
        self._update_ui()

    def fetch_recipient_balance_from_network(self):
        """
        Fetch last account data from the network

        :return:
        """
        self.loaderIconLabel.show()
        try:
            # if account not in stored accounts...
            if (
                self.application.accounts.get_by_address(self.recipient_account.address)
                is None
            ):
                self.recipient_account.balance = (
                    self.application.accounts.network_get_balance(
                        self.recipient_account.address
                    )
                )
            else:
                self.recipient_account = (
                    self.application.accounts.network_update_balance(
                        self.recipient_account
                    )
                )
        except Exception as exception:
            # keep balance from cache DB if network failure
            self.errorLabel.setText(self._(str(exception)))
            logging.exception(exception)

    def _on_finished_fetch_recipient_balance_from_network(self):
        """
        Triggered when async request fetch_from_network is finished

        :return:
        """
        self.loaderIconLabel.hide()
        self._update_ui()

    def fetch_sender_balance_from_network(self):
        """
        Fetch last sender account data from the network

        :return:
        """
        self.loaderIconLabel.show()

        try:
            self.sender_account = self.application.accounts.network_update_balance(
                self.sender_account
            )
        except Exception as exception:
            # keep balance from cache DB if network failure
            self.errorLabel.setText(self._(str(exception)))
            logging.exception(exception)

    def _on_finished_fetch_sender_balance_from_network(self):
        """
        Triggered when async request fetch_from_network is finished

        :return:
        """
        self.loaderIconLabel.hide()
        self._update_ui()

    def _on_sender_address_line_edit_changed(self):
        """
        Triggered when text in the sender address field is changed

        :return:
        """
        self.errorLabel.setText("")
        address_or_name = self.senderNameOrAddressLineEdit.text().strip()

        try:
            address_is_valid = is_valid_ss58_address(address_or_name)
        except IndexError:
            address_is_valid = False

        if not address_is_valid:
            # if entry is a known account name...
            if address_or_name in self.account_address_by_name:
                self.senderNameOrAddressLineEdit.setFont(QFont())
                # display address under the name
                self.senderNameOrAddressValueLabel.setFont(self.monospace_font)
                self.senderNameOrAddressValueLabel.setText(
                    self.account_address_by_name[address_or_name]
                )
                self._get_sender_account(self.account_address_by_name[address_or_name])
            else:
                self.senderNameOrAddressValueLabel.setText("")
                self.senderBalanceValueLabel.setText("?")
                self.errorLabel.setStyleSheet("color: red;")
                self.errorLabel.setText(
                    self._("Invalid address! Please check it again.")
                )
                self.sender_account = None

        else:
            self.senderNameOrAddressLineEdit.setFont(self.monospace_font)
            # display name under the address
            for key, value in self.account_address_by_name.items():
                if value == address_or_name:
                    self.senderNameOrAddressValueLabel.setFont(QFont())
                    self.senderNameOrAddressValueLabel.setText(key)
            self._get_sender_account(address_or_name)

        self._update_ui()

    def _on_recipient_address_line_edit_changed(self):
        """
        Triggered when text in the recipient address field is changed

        :return:
        """
        self.errorLabel.setText("")
        address_or_name = self.recipientNameOrAddressLineEdit.text().strip()

        try:
            address_is_valid = is_valid_ss58_address(address_or_name)
        except IndexError:
            address_is_valid = False

        if not address_is_valid:
            # if entry is a known account name...
            if address_or_name in self.account_address_by_name:
                self.recipientNameOrAddressLineEdit.setFont(QFont())
                # display address under the name
                self.recipientNameOrAddressValueLabel.setFont(self.monospace_font)
                self.recipientNameOrAddressValueLabel.setText(
                    self.account_address_by_name[address_or_name]
                )
                self._get_recipient_account(
                    self.account_address_by_name[address_or_name]
                )
            else:
                self.recipientNameOrAddressValueLabel.setText("")
                self.recipientBalanceValueLabel.setText("?")
                self.errorLabel.setStyleSheet("color: red;")
                self.errorLabel.setText(
                    self._("Invalid address! Please check it again.")
                )
                self.recipient_account = None
        else:
            self.recipientNameOrAddressLineEdit.setFont(self.monospace_font)
            # display name under the address
            for key, value in self.account_address_by_name.items():
                if value == address_or_name:
                    self.recipientNameOrAddressValueLabel.setFont(QFont())
                    self.recipientNameOrAddressValueLabel.setText(key)
            self._get_recipient_account(address_or_name)

        self._update_ui()

    def _get_sender_account(self, address: str) -> None:
        """
        Get sender account

        :return:
        """
        self.sender_account = None
        try:
            Keypair(
                ss58_address=address,
                ss58_format=self.application.currencies.get_current().ss58_format,
            )
        except ValueError as exception:
            logging.exception(exception)
            self.transfer_success = False
            self.errorLabel.setStyleSheet("color: red;")
            self.errorLabel.setText(self._("Invalid address! Please check it again."))
            self.sender_account = None
            return None

        # save in preferences
        self.application.repository.preferences.set(
            TRANSFER_SENDER_ADDRESS_PREFERENCES_KEY, address
        )

        # search in local account list
        for account in self.application.accounts.get_list():
            if account.address == address:
                self.sender_account = account
                self._update_ui()
                return None

        # create account
        self.sender_account = Account(address)
        # fetch balance
        self.fetch_sender_balance_from_network_async_qworker.start()

        return None

    def _get_recipient_account(self, address: str) -> None:
        """
        Get recipient account

        :return:
        """
        self.recipient_account = None
        try:
            Keypair(
                ss58_address=address,
                ss58_format=self.application.currencies.get_current().ss58_format,
            )
        except ValueError as exception:
            logging.exception(exception)
            self.errorLabel.setStyleSheet("color: red;")
            self.errorLabel.setText(self._("Invalid address! Please check it again."))
            self.recipient_account = None
            return None

        # save in preferences
        self.application.repository.preferences.set(
            TRANSFER_RECIPIENT_ADDRESS_PREFERENCES_KEY, address
        )

        # search in local account list
        for account in self.application.accounts.get_list():
            if account.address == address:
                self.recipient_account = account
                self._update_ui()
                return None

        # create account
        self.recipient_account = Account(address)
        # fetch balance
        self.fetch_recipient_balance_from_network_async_qworker.start()

        return None

    def _update_ui(self):
        """
        Update UI

        :return:
        """
        # balances amount
        amount = self.application.amounts.get_amount(self.unit)
        if self.sender_account is not None:
            if self.sender_account.balance is None:
                self.senderBalanceValueLabel.setText("?")
            else:
                self.senderBalanceValueLabel.setText(
                    self.locale().toCurrencyString(
                        amount.value(self.sender_account.balance), amount.symbol()
                    )
                )

        if self.recipient_account is not None:
            if self.recipient_account.balance is None:
                self.recipientBalanceValueLabel.setText("?")
                self.recipientBalanceValueLabel.setToolTip(
                    self._(
                        "Account balance unknown! Send only one unit and make sure the owner can get it"
                    )
                )
            else:
                self.recipientBalanceValueLabel.setText(
                    self.locale().toCurrencyString(
                        amount.value(self.recipient_account.balance), amount.symbol()
                    )
                )
                self.recipientBalanceValueLabel.setToolTip("")

        # fees amount
        if self.fees is not None:
            self.feesValueLabel.setText(
                self.locale().toCurrencyString(amount.value(self.fees), amount.symbol())
            )
        else:
            self.feesValueLabel.setText("?")

        # buttons
        if (
            self.sender_account is not None
            and self.recipient_account is not None
            and self.amount_value > 0
        ):
            self.sendButton.setDisabled(False)
            self.feesButton.setDisabled(False)
        else:
            self.feesButton.setDisabled(True)
            self.sendButton.setDisabled(True)

    def init_units(self) -> None:
        """
        Init units combobox for transfer amount

        :return:
        """
        self.amountUnitComboBox.clear()

        for key, amount in self.application.amounts.register.items():
            self.amountUnitComboBox.addItem(amount.name(), userData=key)
        self.amountUnitComboBox.setCurrentIndex(
            self.amountUnitComboBox.findData(self.unit)
        )

    def _on_fees_button_clicked(self):
        """
        Triggered when user click on Fees button

        :return:
        """
        # sender account locked...
        if not self.application.wallets.is_unlocked(self.sender_account.address):
            # ask password...
            dialog_code = AccountUnlockWindow(
                self.application, self.sender_account, self
            ).exec_()
            if dialog_code == QDialog.Rejected:
                return

        self.feesButton.setDisabled(True)
        self.loaderIconLabel.show()

        self.fetch_fees_from_network_async_qworker.start()

    def fetch_fees_from_network(self):
        """
        Fetch fees amount from network

        :return:
        """
        amount = self.application.amounts.get_amount(self.unit)
        # get value as blockchain units
        blockchain_value = amount.blockchain_value(self.amountDoubleSpinBox.value())
        sender_keypair = self.application.wallets.get_keypair(
            self.sender_account.address
        )
        try:
            self.fees = self.application.transfers.network_fees(
                sender_keypair, self.recipient_account.address, blockchain_value
            )
        except Exception as exception:
            self.errorLabel.setText(self._(str(exception)))
            logging.exception(exception)

    def _on_finished_fetch_fees_from_network(self):
        """
        Triggered when async request fetch_from_network is finished

        :return:
        """
        self.loaderIconLabel.hide()
        self.feesButton.setDisabled(False)
        self._update_ui()

    def _on_send_button_clicked(self):
        """
        Triggered when user click on Send button

        :return:
        """
        # sender account locked...
        if not self.application.wallets.is_unlocked(self.sender_account.address):
            # ask password...
            dialog_code = AccountUnlockWindow(
                self.application, self.sender_account, self
            ).exec_()
            if dialog_code == QDialog.Rejected:
                return

        self.sendButton.setDisabled(True)
        self.loaderIconLabel.show()
        # send transfer to network
        self.send_tranfer_to_network_async_qworker.start()

    def send_transfer_to_network(self):
        """
        Send transfer to network

        :return:
        """
        self.errorLabel.setText("")
        # get value as blockchain units
        amount = self.application.amounts.get_amount(self.unit)
        blockchain_value = amount.blockchain_value(self.amountDoubleSpinBox.value())
        sender_keypair = self.application.wallets.get_keypair(
            self.sender_account.address
        )
        comment = self.commentLineEdit.text().strip()

        try:
            ascii_comment = comment.encode("ascii")
        except UnicodeEncodeError:
            self.errorLabel.setStyleSheet("color: red;")
            self.errorLabel.setText(self._("Invalid character in comment"))
            return

        if sender_keypair is None:
            return

        try:
            if comment == "":
                extrinsic_receipt = self.application.transfers.network_send(
                    sender_keypair, self.recipient_account.address, blockchain_value
                )
            else:
                extrinsic_receipt = (
                    self.application.transfers.network_send_with_comment(
                        sender_keypair,
                        self.recipient_account.address,
                        blockchain_value,
                        ascii_comment,
                    )
                )
        except Exception as exception:
            self.transfer_success = False
            self.errorLabel.setStyleSheet("color: red;")
            self.errorLabel.setText(self._(str(exception)))
            logging.exception(exception)
        else:
            if extrinsic_receipt is None:
                self.transfer_success = False
                self.errorLabel.setStyleSheet("color: red;")
                self.errorLabel.setText(
                    self._("Transfer failed. Please check logs to understand why")
                )
            elif extrinsic_receipt.is_success is False:
                self.transfer_success = False
                self.errorLabel.setStyleSheet("color: red;")
                self.errorLabel.setText(self._(extrinsic_receipt.error_message["name"]))
            else:
                self.transfer_success = True
                self.errorLabel.setStyleSheet("color: green;")
                self.errorLabel.setText(self._("Transfer done"))

    def _on_finished_send_transfer_to_network(self):
        """
        Triggered when async request send_transfer_to_network is finished

        :return:
        """
        self.loaderIconLabel.hide()
        self.sendButton.setDisabled(False)
        self.fetch_sender_balance_from_network_async_qworker.start()
        self.fetch_recipient_balance_from_network_async_qworker.start()


if __name__ == "__main__":
    qapp = QApplication(sys.argv)
    application_ = Application(DATA_PATH)

    account1 = application_.accounts.create_new_root_account(
        "album cute glance oppose hub fury strategy health dust rebuild trophy magic",
        "en",
        AccountCryptoType.ED25519,
        "test account",
        "aaaaaa",
    )
    if account1 is not None:
        account1.balance = 1000
    account2 = application_.accounts.create_new_account(
        "album cute glance oppose hub fury strategy health dust rebuild trophy magic",
        "en",
        "//1",
        AccountCryptoType.ED25519,
        "test account",
        "aaaaaa",
    )
    if account2 is not None:
        account2.balance = 0

    TransferWindow(application_, QMutex(), None, account2).exec_()
