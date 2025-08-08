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

import qrcode
from PyQt5.QtCore import QEvent, QMutex, QPoint, pyqtSignal
from PyQt5.QtGui import QFont, QPixmap, QWheelEvent
from PyQt5.QtWidgets import QApplication, QDialog, QListView, QMainWindow, QWidget

from tikka.domains.application import Application
from tikka.domains.entities.account import Account
from tikka.domains.entities.address import DisplayAddress
from tikka.domains.entities.constants import AMOUNT_UNIT_KEY, DATA_PATH
from tikka.domains.entities.events import (
    AccountEvent,
    ConnectionsEvent,
    TransferEvent,
    UnitEvent,
)
from tikka.domains.entities.identity import IdentityStatus
from tikka.domains.entities.smith import SmithStatus
from tikka.slots.pyqt.entities.constants import (
    ADDRESS_MONOSPACE_FONT_NAME,
    ICON_ACCOUNT_NO_WALLET,
    ICON_ACCOUNT_WALLET_LOCKED,
    ICON_ACCOUNT_WALLET_UNLOCKED,
    ICON_IDENTITY_MEMBER,
    ICON_IDENTITY_MEMBER_NOT_VALIDATED,
    ICON_IDENTITY_NOT_MEMBER,
    SELECTED_UNIT_PREFERENCES_KEY,
)
from tikka.slots.pyqt.entities.qrcode_image import QRCodeImage
from tikka.slots.pyqt.entities.worker import AsyncQWorker
from tikka.slots.pyqt.models.transfers import TransferItemDelegate, TransfersListModel
from tikka.slots.pyqt.resources.gui.widgets.account_rc import Ui_AccountWidget
from tikka.slots.pyqt.widgets.account_menu import AccountPopupMenu
from tikka.slots.pyqt.widgets.transfer_history_menu import TransferHistoryPopupMenu
from tikka.slots.pyqt.windows.account_unlock import AccountUnlockWindow
from tikka.slots.pyqt.windows.transfer import TransferWindow


class TransfersListView(QListView):
    """
    TransfersListView class
    """

    scroll_offset_changed = pyqtSignal(int)

    def __init__(
        self,
        application: Application,
        address: str,
        page_size: int,
        parent: Optional[QWidget] = None,
    ):
        """
        Init TransfersListView instance

        :param application: Application instance
        :param address: Account address
        :param page_size: Nb of transfers per page
        :param parent: QWidget instance, default None
        """
        super().__init__(parent)

        self.application = application
        self.address = address
        self.scroll_offset = 0
        self.page_size = page_size

    def wheelEvent(self, event: QWheelEvent):
        """
        Override Wheel event

        :param event: QEvent instance
        :return:
        """
        delta = event.angleDelta().y()
        if not self.verticalScrollBar().isVisible():
            if delta < 0:  # 🔽 Scroll vers le bas (charger plus)
                if (
                    self.scroll_offset + self.page_size
                    < self.application.transfers.count(self.address)
                ):
                    self.scroll_offset += self.page_size
                    self.model().init_data(self.scroll_offset, self.page_size)  # type: ignore
                    self.scroll_offset_changed.emit(self.scroll_offset)

            elif delta > 0:  # 🔼 Scroll vers le haut (charger page précédente si dispo)
                self.scroll_offset -= self.page_size
                if self.scroll_offset < 0:
                    self.scroll_offset = 0
                self.model().init_data(self.scroll_offset, self.page_size)  # type: ignore
                self.scroll_offset_changed.emit(self.scroll_offset)
        else:
            # wheel backward and scroll bar maximum down...
            if (
                delta < 0
                and self.verticalScrollBar().value()
                == self.verticalScrollBar().maximum()
            ):

                if (
                    self.scroll_offset + self.page_size
                    < self.application.transfers.count(self.address)
                ):
                    self.scroll_offset += self.page_size
                    self.model().init_data(self.scroll_offset, self.page_size)  # type: ignore
                    self.scroll_offset_changed.emit(self.scroll_offset)

            # wheel forward and scroll bar maximum top...
            elif (
                delta > 0
                and self.verticalScrollBar().value()
                == self.verticalScrollBar().minimum()
            ):
                self.scroll_offset -= self.page_size
                if self.scroll_offset < 0:
                    self.scroll_offset = 0
                self.model().init_data(self.scroll_offset, self.page_size)  # type: ignore
                self.scroll_offset_changed.emit(self.scroll_offset)

        super().wheelEvent(event)


class AccountWidget(QWidget, Ui_AccountWidget):
    """
    AccountWidget class
    """

    def __init__(
        self,
        application: Application,
        account: Account,
        mutex: QMutex,
        parent: Optional[QWidget] = None,
    ) -> None:
        """
        Init AccountWidget instance

        :param application: Application instance
        :param account: Account instance
        :param mutex: QMutex instance
        :param parent: QWidget instance
        """
        super().__init__(parent=parent)
        self.setupUi(self)

        self.application = application
        self._ = self.application.translator.gettext

        self.account = account
        self.mutex = mutex
        self.unclaimed_ud_balance = 0
        self.history_limit = 100
        self.history_page_size = 100
        self.history_scroll_offset = 0

        self.monospace_font = QFont(ADDRESS_MONOSPACE_FONT_NAME)
        self.monospace_font.setStyleHint(QFont.Monospace)
        self.addressValueLabel.setFont(self.monospace_font)
        self.addressValueLabel.setText(self.account.address)
        if self.account.legacy_v1 is True:
            self.v1AddressValueLabel.setText(
                self.account.get_v1_address(
                    self.application.currencies.get_current().ss58_format
                )
            )

        # creating a pix map of qr code
        qr_code_pixmap = qrcode.make(
            self.account.address, image_factory=QRCodeImage
        ).pixmap()

        # set qrcode to the label
        self.QRCodeAddressLabel.setPixmap(qr_code_pixmap)

        self.transfers_model = TransfersListModel(
            application, self.account.address, self.locale()
        )

        # self.transfersListView.hide()
        # self.transfersListView = TransfersListView(
        #     application, self.account.address, self.history_page_size, self.groupBox
        # )
        #
        # self.transfersListView.setMouseTracking(False)
        # self.transfersListView.setEditTriggers(QAbstractItemView.NoEditTriggers)
        # self.transfersListView.setAlternatingRowColors(True)
        # self.transfersListView.setSelectionMode(QAbstractItemView.NoSelection)
        # self.transfersListView.setObjectName("transfersListView")
        # self.verticalLayout_4.addWidget(self.transfersListView)

        self.transfersListView.setModel(self.transfers_model)
        self.transfersListView.setItemDelegate(TransferItemDelegate())
        self.transfersListView.setResizeMode(QListView.Adjust)

        ##############################
        # ASYNC METHODS
        ##############################
        # Create a QWorker object
        self.fetch_from_network_async_qworker = AsyncQWorker(
            self.fetch_account_from_network, self.mutex
        )
        self.fetch_from_network_async_qworker.finished.connect(
            self._on_finished_fetch_from_network
        )
        self.network_claim_uds_async_qworker = AsyncQWorker(
            self.network_claim_uds, self.mutex
        )
        self.network_claim_uds_async_qworker.finished.connect(
            self._on_finished_network_claim_uds
        )
        self.fetch_transfers_from_network_async_qworker = AsyncQWorker(
            self.fetch_transfers_from_network, self.mutex
        )
        self.fetch_transfers_from_network_async_qworker.finished.connect(
            self._on_finished_fetch_transfers_from_network
        )

        # events
        self.refreshButton.clicked.connect(self._on_refresh_button_clicked)
        self.transferToButton.clicked.connect(self.transfer)
        self.customContextMenuRequested.connect(self.on_context_menu)
        self.claimUdsButton.clicked.connect(self.on_claim_uds_button_clicked)
        # self.transfersListView.scroll_offset_changed.connect(self._update_ui)
        self.transfersListView.customContextMenuRequested.connect(
            self.on_transfer_history_context_menu
        )
        # application events
        self.application.event_dispatcher.add_event_listener(
            AccountEvent.EVENT_TYPE_UPDATE, lambda e: self._update_ui()
        )
        self.application.event_dispatcher.add_event_listener(
            UnitEvent.EVENT_TYPE_CHANGED, lambda e: self._on_unit_changed_event()
        )
        self.application.event_dispatcher.add_event_listener(
            TransferEvent.EVENT_TYPE_SENT, lambda e: self._on_transfer_sent()
        )
        self.application.event_dispatcher.add_event_listener(
            ConnectionsEvent.EVENT_TYPE_INDEXER_CONNECTED,
            lambda e: self._on_indexer_connected(),
        )

        self.transfers_model.init_data(
            self.history_scroll_offset, self.history_page_size
        )
        self._update_ui()

    def transfer(self):
        """
        When user click on transfer to button

        :return:
        """
        TransferWindow(
            self.application, self.mutex, None, self.account, parent=self.parent()
        ).exec_()

    def _on_refresh_button_clicked(self, _: QEvent):
        """
        Triggered when user click on Refresh button

        :param _: QEvent instance
        :return:
        """
        self.errorLabel.setText("")
        self.fetch_from_network_async_qworker.start()
        self.fetch_transfers_from_network_async_qworker.start()

    def _on_indexer_connected(self):
        """ "
        Triggered when the indexer is connected
        """
        self.fetch_transfers_from_network_async_qworker.start()

    def _on_transfer_sent(self):
        """
        Triggered after a successful transfer event

        :return:
        """
        # update account balance from network
        self.fetch_from_network_async_qworker.start()
        self.fetch_transfers_from_network_async_qworker.start()

    def _on_unit_changed_event(self):
        """
        Triggered when user change money units

        :return:
        """
        self._update_ui()
        self.transfers_model.init_data(
            self.history_scroll_offset, self.history_page_size
        )

    def fetch_account_from_network(self):
        """
        Get last account data from the network

        :return:
        """
        if not self.application.connections.node.is_connected():
            return

        self.refreshButton.setEnabled(False)

        try:
            self.account = self.application.accounts.network_update_account(
                self.account
            )
        except Exception as exception:
            self.errorLabel.setText(self._(str(exception)))
            logging.exception(exception)
        else:
            try:
                identity = self.application.identities.network_update_identity(
                    self.account.address
                )
            except Exception as exception:
                self.errorLabel.setText(self._(str(exception)))
                logging.exception(exception)
            else:
                if identity is not None:
                    try:
                        self.application.smiths.network_update_smith(identity.index)
                    except Exception as exception:
                        self.errorLabel.setText(self._(str(exception)))
                        logging.exception(exception)

                    self.unclaimed_ud_balance = (
                        self.application.accounts.network_get_unclaimed_ud_balance(
                            identity
                        )
                    )

    def _on_finished_fetch_from_network(self):
        """
        Triggered when async request fetch_account_from_network is finished

        :return:
        """
        self.application.accounts.update(self.account)
        self.refreshButton.setEnabled(True)
        logging.debug("Account widget update")

    def fetch_transfers_from_network(self):
        """
        Get transfers data from the network

        :return:
        """
        if not self.application.connections.indexer.is_connected():
            return

        self.refreshButton.setEnabled(False)

        try:
            self.application.transfers.network_fetch_history_for_account(
                self.account, self.history_limit
            )
        except Exception as exception:
            self.errorLabel.setText(self._(str(exception)))
            logging.exception(exception)

        try:
            self.account.total_transfers_count = (
                self.application.transfers.network_fetch_total_count_for_address(
                    self.account.address
                )
            )
        except Exception as exception:
            self.errorLabel.setText(self._(str(exception)))
            logging.exception(exception)

    def _on_finished_fetch_transfers_from_network(self):
        """
        Triggered when async request fetch_transfers_from_network is finished

        :return:
        """
        self.application.accounts.update(self.account)
        self.transfers_model.init_data(
            self.history_scroll_offset, self.history_page_size
        )
        self.refreshButton.setEnabled(True)
        logging.debug(
            "Finished fetch account transfers %s %s",
            self.account.name,
            self.account.address,
        )

    def _update_ui(self):
        """
        Update UI from self.account

        :return:
        """
        display_identity_status = {
            IdentityStatus.UNCONFIRMED.value: self._("Unconfirmed"),
            IdentityStatus.UNVALIDATED.value: self._("Unvalidated"),
            IdentityStatus.MEMBER.value: self._("Member"),
            IdentityStatus.NOT_MEMBER.value: self._("Not member"),
            IdentityStatus.REVOKED.value: self._("Revoked"),
        }

        display_identity_icon = {
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

        display_smith_status = {
            SmithStatus.INVITED.value: self._("Invited"),
            SmithStatus.PENDING.value: self._("Pending"),
            SmithStatus.SMITH.value: self._("Smith"),
            SmithStatus.EXCLUDED.value: self._("Excluded"),
        }

        unit_preference = self.application.repository.preferences.get(
            SELECTED_UNIT_PREFERENCES_KEY
        )
        if unit_preference is not None:
            amount = self.application.amounts.get_amount(unit_preference)
        else:
            amount = self.application.amounts.get_amount(AMOUNT_UNIT_KEY)

        if self.account.balance is None:
            self.balanceLabel.setText("?")
        else:
            self.balanceLabel.setText(
                self.locale().toCurrencyString(
                    amount.value(self.account.balance), amount.symbol()
                )
            )
        if self.unclaimed_ud_balance > 0:

            display_unclaimed_uds_balance = self.locale().toCurrencyString(
                amount.value(self.unclaimed_ud_balance), amount.symbol()
            )
            if self.application.wallets.exists(self.account.address):
                self.claimUdsButton.setText(f"+{display_unclaimed_uds_balance}")
                self.claimUdsButton.setVisible(True)
                self.unclaimedUdsLabel.setVisible(False)
            else:
                self.unclaimedUdsLabel.setText(f"+{display_unclaimed_uds_balance}")
                self.unclaimedUdsLabel.setVisible(True)
                self.claimUdsButton.setVisible(False)
        else:
            self.claimUdsButton.setVisible(False)
            self.unclaimedUdsLabel.setVisible(False)

        if self.application.wallets.exists(self.account.address):
            if self.application.wallets.is_unlocked(self.account.address):
                self.lockStatusIcon.setPixmap(QPixmap(ICON_ACCOUNT_WALLET_UNLOCKED))
            else:
                self.lockStatusIcon.setPixmap(QPixmap(ICON_ACCOUNT_WALLET_LOCKED))
        else:
            self.lockStatusIcon.setPixmap(QPixmap(ICON_ACCOUNT_NO_WALLET))

        identity = self.application.identities.get_by_address(self.account.address)
        if identity is not None:
            self.identityStatusIconLabel.setPixmap(
                display_identity_icon[identity.status.value]
            )
            identity_name = identity.name or ""
            self.identityNameValueLabel.setText(f"{identity_name}#{identity.index}")
            self.identityValueLabel.setText(
                display_identity_status[identity.status.value]
            )
            smith = self.application.smiths.get(identity.index)
            if smith is not None:
                self.smithValuelabel.setText(display_smith_status[smith.status.value])
            else:
                self.smithValuelabel.setText(self._("No"))
            if self.account.name is None:
                self.accountNameValueLabel.setText("")
            else:
                self.accountNameValueLabel.setText(f" - {self.account.name}")
        else:
            self.identityStatusIconLabel.setPixmap(QPixmap(ICON_IDENTITY_NOT_MEMBER))
            self.identityNameValueLabel.setText("")
            self.identityValueLabel.setText(self._("No"))
            self.smithValuelabel.setText(self._("No"))
            if self.account.name is None:
                self.accountNameValueLabel.setText("")
            else:
                self.accountNameValueLabel.setText(self.account.name)

        if self.account.root is None and self.account.path is None:
            self.derivationValueLabel.setText(self._("Root"))
        else:
            root_account = self.application.accounts.get_by_address(self.account.root)
            if root_account is not None and root_account.name is not None:
                self.derivationValueLabel.setFont(QFont())
                self.derivationValueLabel.setText(root_account.name + self.account.path)
            else:
                self.derivationValueLabel.setFont(self.monospace_font)
                self.derivationValueLabel.setText(
                    DisplayAddress(self.account.root).shorten + self.account.path
                )

        # transfers
        self.transfersCountValueLabel.setText(
            f"1...{self.history_limit}/{self.account.total_transfers_count}"
        )
        # current_page = int(
        #     (self.transfersListView.scroll_offset / self.history_page_size) + 1
        # )
        # self.transfersCountValueLabel.setText(
        #     str(
        #         f"Page {current_page}/{self.history_page_size} |"
        #         f"1...{self.history_limit}/{self.account.total_transfers_count}"
        #     )
        # )

    def on_context_menu(self, position: QPoint):
        """
        When right button on account tab

        :return:
        """
        # display popup menu at click position
        menu = AccountPopupMenu(self.application, self.account, self.mutex, self)
        menu.exec_(self.mapToGlobal(position))

    def on_transfer_history_context_menu(self, position: QPoint):
        """
        When right button on transfer history listview

        :return:
        """
        # get selected transfer
        transfer = self.transfersListView.currentIndex().internalPointer()
        if transfer is not None:
            # display popup menu at click position
            menu = TransferHistoryPopupMenu(
                self.application, self.account, transfer, self.mutex, self
            )
            menu.exec_(self.transfersListView.mapToGlobal(position))

    def on_claim_uds_button_clicked(self, event: QEvent):
        """
        Triggered when user click on claim uds button

        :param event: QEvent instance
        :return:
        """
        if not self.application.connections.node.is_connected():
            return

        # if account locked...
        if not self.application.wallets.is_unlocked(self.account.address):
            # ask password...
            dialog_code = AccountUnlockWindow(
                self.application, self.account, self
            ).exec_()
            if dialog_code == QDialog.Rejected:
                return

        self.network_claim_uds_async_qworker.start()

    def network_claim_uds(self):
        """
        Send claim UDs request to network

        :return:
        """
        self.claimUdsButton.setDisabled(True)
        try:
            self.application.identities.network_claim_uds(
                self.application.wallets.get_keypair(self.account.address)
            )
        except Exception as exception:
            self.errorLabel.setText(self._(str(exception)))

    def _on_finished_network_claim_uds(self):
        """
        Triggered when the claim uds function is finished

        :return:
        """
        self.claimUdsButton.setDisabled(False)
        self.fetch_from_network_async_qworker.start()


if __name__ == "__main__":
    qapp = QApplication(sys.argv)

    application_ = Application(DATA_PATH)
    account_ = Account("5GrwvaEF5zXb26Fz9rcQpDWS57CtERHpNehXCPcNoHGKutQY")

    main_window = QMainWindow()
    main_window.show()

    main_window.setCentralWidget(
        AccountWidget(application_, account_, QMutex(), main_window)
    )

    sys.exit(qapp.exec_())
