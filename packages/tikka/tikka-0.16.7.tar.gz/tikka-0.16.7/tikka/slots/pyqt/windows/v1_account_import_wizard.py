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

from PyQt5.QtCore import QMutex, QSize
from PyQt5.QtGui import QFont, QMovie
from PyQt5.QtWidgets import QApplication, QDialog, QWidget, QWizard

from tikka.domains.application import Application
from tikka.domains.entities.constants import AMOUNT_UNIT_KEY, DATA_PATH
from tikka.interfaces.adapters.repository.accounts import AccountsRepositoryInterface
from tikka.slots.pyqt.entities.constants import (
    ADDRESS_MONOSPACE_FONT_NAME,
    ICON_LOADER,
    SELECTED_UNIT_PREFERENCES_KEY,
)
from tikka.slots.pyqt.entities.worker import AsyncQWorker
from tikka.slots.pyqt.resources.gui.windows.v1_account_import_wizard_rc import (
    Ui_importAccountV1Wizard,
)
from tikka.slots.pyqt.windows.account_unlock import AccountUnlockWindow


class V1AccountImportWizardWindow(QWizard, Ui_importAccountV1Wizard):
    """
    V1AccountImportWizardWindow class
    """

    def __init__(
        self, application: Application, mutex: QMutex, parent: Optional[QWidget] = None
    ):
        """
        Init import V1 account wizard window

        :param application: Application instance
        :param mutex: QMutex instance
        :param parent: QWidget instance
        """
        super().__init__(parent=parent)
        self.setupUi(self)

        self.application = application
        self._ = self.application.translator.gettext
        self.mutex = mutex

        unit_preference = self.application.repository.preferences.get(
            SELECTED_UNIT_PREFERENCES_KEY
        )
        if unit_preference is not None:
            self.amount = self.application.amounts.get_amount(unit_preference)
        else:
            self.amount = self.application.amounts.get_amount(AMOUNT_UNIT_KEY)

        # source account
        self.source_account = None

        # destination account
        self.destination_account = None
        self.destination_mnemonic = None
        self.destination_account = None
        self.destination_keypair = None

        # set monospace font to address fields
        self.monospace_font = QFont(ADDRESS_MONOSPACE_FONT_NAME)
        self.monospace_font.setStyleHint(QFont.Monospace)
        self.sourceV1AddressValueImportLabel.setFont(self.monospace_font)
        self.sourceAddressValueImportLabel.setFont(self.monospace_font)
        self.destinationAddressValueImportLabel.setFont(self.monospace_font)

        # animated loading icon
        self.loader_movie = QMovie(ICON_LOADER)
        self.loader_movie.setScaledSize(QSize(16, 16))
        self.loader_movie.start()

        ##############################
        # ASYNC METHODS
        ##############################
        # Create a QWorker object
        self.import_source_into_destination_on_network_async_qworker = AsyncQWorker(
            self.network_import_source_into_destination, self.mutex
        )
        self.wizard_page2_init()

    def wizard_page2_init(self):
        """
        Initialize page 2 form

        :return:
        """
        # fonts
        self.sourceV1AddressValueLabel.setFont(self.monospace_font)
        self.sourceAddressValueLabel.setFont(self.monospace_font)

        # page next button status handling
        self.wizardPage2.isComplete = self.wizard_page2_is_complete
        self.wizardPage2.validatePage = self.wizard_page2_validate_page

        # empty selection
        self.sourceV1AccountComboBox.addItem(
            "",
            userData=None,
        )
        # build selector
        for account in self.application.accounts.get_list(
            filters={
                AccountsRepositoryInterface.COLUMN_LEGACY_V1: True,
            }
        ):
            # only accounts with password (user owns it)
            if account.balance is not None and self.application.passwords.exists(
                account.address
            ):
                account_label = (
                    account.name if account.name is not None else account.address
                )
                identity = self.application.identities.get_by_address(account.address)

                if identity is not None and identity.name is not None:
                    account_label = f"{identity.name}#{identity.index}"
                self.sourceV1AccountComboBox.addItem(
                    account_label,
                    userData=account.address,
                )

        # events
        self.sourceV1AccountComboBox.currentIndexChanged.connect(
            self._source_generate_address
        )

    def wizard_page2_validate_page(self):
        """
        Ask password if source account unlocked to allow to go to next page

        :return:
        """
        if not self.application.wallets.is_unlocked(self.source_account.address):
            # ask password...
            dialog_code = AccountUnlockWindow(
                self.application, self.source_account, self
            ).exec_()
            if dialog_code == QDialog.Rejected:
                return False

        self.wizard_page3_init()
        return True

    def wizard_page2_is_complete(self) -> bool:
        """
        Function to overload V1AccountImportWizardWindow->Page2->IsComplete() method

        :return:
        """
        result = False

        if self.source_account is not None and self.source_account.balance is not None:
            result = True

        return result

    def _source_generate_address(self):
        """
        Generate address from ID

        :return:
        """
        self.sourceErrorLabel.setText("")

        selected_address = self.sourceV1AccountComboBox.currentData()
        if selected_address is None:
            self.sourceV1AddressValueLabel.setText("")
            self.sourceAddressValueLabel.setText("")
            self.sourceBalanceValueLabel.setText("?")
            self.sourceIdentityValueLabel.setText("")
            return

        self.source_account = self.application.accounts.get_by_address(
            self.sourceV1AccountComboBox.currentData()
        )

        # display v1 address
        self.sourceV1AddressValueLabel.setText(
            self.source_account.get_v1_address(
                self.application.currencies.get_current().ss58_format
            )
        )

        # if account name displayed in combobox...
        if (
            self.sourceV1AccountComboBox.currentText()
            != self.sourceV1AccountComboBox.currentData()
        ):
            self.sourceAddressValueLabel.setText(self.source_account.address)
        else:
            self.sourceAddressValueLabel.setText("")

        self.sourceBalanceValueLabel.setText(
            self.locale().toCurrencyString(
                self.amount.value(self.source_account.balance),
                self.amount.symbol(),
            )
        )
        identity = self.application.identities.get_by_address(
            self.source_account.address
        )
        if identity is not None:
            identity_name = identity.name or ""
            self.sourceIdentityValueLabel.setText(f"{identity_name}#{identity.index}")
        else:
            self.sourceIdentityValueLabel.setText(self._("None"))

        self.wizardPage2.completeChanged.emit()

    def wizard_page3_init(self):
        """
        Initialize page 3 form

        :return:
        """
        # fonts
        self.destinationAccountComboBox.setFont(self.monospace_font)
        self.destinationAddressValueLabel.setFont(self.monospace_font)

        # page next button status handling
        self.wizardPage3.isComplete = self.wizard_page3_is_complete
        self.wizardPage3.validatePage = self.wizard_page3_validate_page

        # init V2 accounts combo box
        identity_idx_source = self.application.identities.get_index_by_address(
            self.source_account.address
        )
        self.destinationAccountComboBox.addItem("", None)
        for account in self.application.accounts.get_list():
            # we can not transfer a source identity on a destination account with already an identity
            identity_idx = self.application.identities.get_index_by_address(
                account.address
            )
            if identity_idx_source is not None and identity_idx is not None:
                continue
            if self.source_account.address == account.address:
                continue
            # only accounts with password (user owns it)
            if self.application.passwords.exists(account.address):
                self.destinationAccountComboBox.addItem(
                    account.name if account.name is not None else account.address,
                    userData=account.address,
                )

        # events
        self.destinationAccountComboBox.currentIndexChanged.connect(
            self._generate_destination_address
        )

    def wizard_page3_is_complete(self) -> bool:
        """
        Function to overload V1AccountImportWizardWindow->Page3->IsComplete() method

        :return:
        """
        result = False

        if self.destination_account is not None and (
            self.application.identities.get_index_by_address(
                self.source_account.address
            )
            is None
            or (
                self.application.identities.get_index_by_address(
                    self.source_account.address
                )
                is not None
                and self.application.identities.get_index_by_address(
                    self.destination_account.address
                )
                is None
            )
        ):
            result = True

        return result

    def wizard_page3_validate_page(self):
        """
        Ask password if destination account unlocked to allow to go to next page

        :return:
        """
        if not self.application.wallets.is_unlocked(self.destination_account.address):
            # ask password...
            dialog_code = AccountUnlockWindow(
                self.application, self.destination_account, self
            ).exec_()
            if dialog_code == QDialog.Rejected:
                return False

        self.wizard_page4_init()
        return True

    def _generate_destination_address(self):
        """
        Generate destination address

        :return:
        """
        self.destination_account = self.application.accounts.get_by_address(
            self.destinationAccountComboBox.currentData()
        )
        self.destinationErrorLabel.setText("")

        if self.destination_account is None:
            self.destinationDerivationValueLabel.setText("")
            self.destinationAddressValueLabel.setText("")
            self.destinationBalanceValueLabel.setText("?")
            return

        self.destinationDerivationValueLabel.setText(self.destination_account.path)
        self.destinationAddressValueLabel.setText(self.destination_account.address)
        if self.destination_account.balance is not None:
            self.sourceBalanceValueLabel.setText(
                self.locale().toCurrencyString(
                    self.amount.value(self.source_account.balance),
                    self.amount.symbol(),
                )
            )
        else:
            self.destinationBalanceValueLabel.setText("?")

        self.wizardPage3.completeChanged.emit()

    def wizard_page4_init(self):
        """
        Initialize page 4 form

        :return:
        """
        # fonts
        self.sourceV1AddressValueImportLabel.setFont(self.monospace_font)
        self.sourceAddressValueImportLabel.setFont(self.monospace_font)
        self.destinationAddressValueImportLabel.setFont(self.monospace_font)

        self.sourceV1AddressValueImportLabel.setText(
            self.source_account.get_v1_address(
                self.application.currencies.get_current().ss58_format
            )
        )
        self.sourceAddressValueImportLabel.setText(self.source_account.address)
        if self.source_account is not None:
            if self.source_account.balance is not None:
                self.sourceBalanceValueImportLabel.setText(
                    self.locale().toCurrencyString(
                        self.amount.value(self.source_account.balance),
                        self.amount.symbol(),
                    )
                )
            identity = self.application.identities.get_by_address(
                self.source_account.address
            )
            if identity is not None:
                identity_name = identity.name or ""
                self.sourceIdentityValueImportLabel.setText(
                    f"{identity_name}#{identity.index}"
                )
            else:
                self.sourceIdentityValueImportLabel.setText(self._("None"))
        else:
            self.sourceIdentityValueImportLabel.setText(self._("None"))

        self.destinationAddressValueImportLabel.setText(
            self.destination_account.address
        )
        if self.destination_account.balance is not None:
            self.destinationBalanceValueImportLabel.setText(
                self.locale().toCurrencyString(
                    self.amount.value(self.destination_account.balance),
                    self.amount.symbol(),
                )
            )
        self.destinationIdentityValueImportLabel.setText(self._("None"))

        # page next button status handling
        self.wizardPage4.isComplete = self.wizard_page4_is_complete

        # events
        self.importButton.clicked.connect(self.on_import_button_clicked)

        ##############################
        # ASYNC METHODS
        ##############################
        self.import_source_into_destination_on_network_async_qworker.finished.connect(
            self._on_finished_import_source_into_destination_on_network
        )

    def wizard_page4_is_complete(self) -> bool:
        """
        Function to overload V1AccountImportWizardWindow->Page4->IsComplete() method

        :return:
        """
        result = False

        if (
            self.source_account is not None
            and (
                self.source_account.balance == 0 or self.source_account.balance is None
            )
            and self.application.identities.get_index_by_address(
                self.source_account.address
            )
            is None
        ):
            result = True

        return result

    def on_import_button_clicked(self):
        """
        Triggered when user click on import button

        :return:
        """
        self.importButton.setDisabled(True)
        self.importErrorLabel.setMovie(self.loader_movie)

        self.import_source_into_destination_on_network_async_qworker.start()

    def network_import_source_into_destination(self):
        """
        Send changeOwnerKey for identity if any and tranfer money from V1 source account to V2 destination account

        :return:
        """
        self.importErrorLabel.setText("")

        source_keypair = self.application.wallets.get_keypair(
            self.source_account.address
        )
        destination_keypair = self.application.wallets.get_keypair(
            self.destination_account.address
        )

        if (
            self.application.identities.get_index_by_address(
                self.source_account.address
            )
            is not None
        ):
            try:
                self.application.identities.network_change_owner_key(
                    source_keypair, destination_keypair
                )
            except Exception as exception:
                self.importErrorLabel.setText(self._(str(exception)))
                # do not transfer all the money if identity transfer failed,
                # because identity transfer requires fees from sender account
                logging.exception(exception)
                return

        if self.source_account.balance is not None and self.source_account.balance > 0:
            try:
                self.application.transfers.network_send_all(
                    source_keypair, self.destination_account.address, False
                )
            except Exception as exception:
                self.importErrorLabel.setText(self._(str(exception)))
                logging.exception(exception)
                return
        try:
            self.source_account = self.application.accounts.network_update_balance(
                self.source_account
            )
        except Exception as exception:
            self.importErrorLabel.setText(self._(str(exception)))
            logging.exception(exception)
            return

        try:
            self.application.identities.network_update_identity(
                self.source_account.address
            )
        except Exception as exception:
            self.importErrorLabel.setText(self._(str(exception)))
            logging.exception(exception)
            return

        try:
            self.destination_account = self.application.accounts.network_update_balance(
                self.destination_account
            )
        except Exception as exception:
            self.importErrorLabel.setText(self._(str(exception)))
            logging.exception(exception)
            return

        try:
            self.application.identities.network_update_identity(
                self.destination_account.address
            )
        except Exception as exception:
            self.importErrorLabel.setText(self._(str(exception)))
            logging.exception(exception)

    def _on_finished_import_source_into_destination_on_network(self):
        """
        Triggered when async request import_source_into_destination_on_network is finished

        :return:
        """
        self.importErrorLabel.setMovie(None)

        if self.source_account is not None:
            if self.source_account.balance is not None:
                self.sourceBalanceValueImportLabel.setText(
                    self.locale().toCurrencyString(
                        self.amount.value(self.source_account.balance),
                        self.amount.symbol(),
                    )
                )
            else:
                # empty account deleted from blockchain
                self.sourceBalanceValueImportLabel.setText("?")

        identity_index = self.application.identities.get_index_by_address(
            self.source_account.address
        )
        if identity_index is not None:
            identity = self.application.identities.get(identity_index)
            identity_name = identity.name or ""
            self.sourceIdentityValueImportLabel.setText(
                f"{identity_name}#{identity.index}"
            )
        else:
            self.sourceIdentityValueImportLabel.setText(self._("None"))

        if self.destination_account.balance is not None:
            self.destinationBalanceValueImportLabel.setText(
                self.locale().toCurrencyString(
                    self.amount.value(self.destination_account.balance),
                    self.amount.symbol(),
                )
            )
        else:
            self.destinationBalanceValueImportLabel.setText("?")

        identity_index = self.application.identities.get_index_by_address(
            self.destination_account.address
        )
        if identity_index is not None:
            identity = self.application.identities.get(identity_index)
            identity_name = identity.name or ""
            self.destinationIdentityValueImportLabel.setText(
                f"{identity_name}#{identity.index}"
            )
        else:
            self.destinationIdentityValueImportLabel.setText(self._("None"))

        self.wizardPage4.completeChanged.emit()

        if self.wizardPage4.isComplete():
            self.importButton.setDisabled(True)
            self.importErrorLabel.setStyleSheet("color: green;")
            self.importErrorLabel.setText(self._("Account imported successfully!"))
            if (
                self.application.accounts.get_by_address(
                    self.destination_account.address
                )
                is None
            ):
                self.application.accounts.add(self.destination_account)
            else:
                self.application.accounts.update(self.destination_account)
        else:
            self.importButton.setDisabled(False)
            self.importErrorLabel.setStyleSheet("color: red;")
            if (
                self.source_account.balance is not None
                and self.source_account.balance > 0
            ):
                self.importErrorLabel.setText(self._("Error importing money!"))
            elif (
                self.application.identities.get_index_by_address(
                    self.destination_account.address
                )
                is None
            ):
                self.importErrorLabel.setText(self._("Error importing identity!"))


if __name__ == "__main__":
    qapp = QApplication(sys.argv)
    application_ = Application(DATA_PATH)
    V1AccountImportWizardWindow(application_, QMutex()).exec_()
