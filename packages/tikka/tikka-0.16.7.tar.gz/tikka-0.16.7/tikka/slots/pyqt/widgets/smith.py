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
import time
from typing import Dict, Optional

from PyQt5.QtCore import QLocale, QMutex
from PyQt5.QtGui import QMovie
from PyQt5.QtWidgets import QApplication, QDialog, QMainWindow, QWidget

from tikka.domains.application import Application
from tikka.domains.entities.account import Account
from tikka.domains.entities.authorities import AuthorityStatus
from tikka.domains.entities.constants import DATA_PATH
from tikka.domains.entities.events import AccountEvent, CurrencyEvent
from tikka.domains.entities.identity import IdentityStatus
from tikka.domains.entities.node import Node
from tikka.domains.entities.smith import Smith, SmithStatus
from tikka.interfaces.adapters.network.node.smiths import NodeSmithsException
from tikka.slots.pyqt.entities.constants import (
    ICON_LOADER,
    SMITH_CERTIFY_SELECTED_IDENTITY_INDEX,
    SMITH_INVITE_SELECTED_ACCOUNT_ADDRESS,
    SMITH_SELECTED_ACCOUNT_ADDRESS,
)
from tikka.slots.pyqt.entities.worker import AsyncQWorker
from tikka.slots.pyqt.resources.gui.widgets.smith_rc import Ui_SmithWidget
from tikka.slots.pyqt.windows.account_unlock import AccountUnlockWindow


class SmithWidget(QWidget, Ui_SmithWidget):
    """
    SmithWidget class
    """

    DELAY_BEFORE_UPDATE_MEMBERSHIP_STATUS_AFTER_REQUEST = 6

    def __init__(
        self, application: Application, mutex: QMutex, parent: Optional[QWidget] = None
    ) -> None:
        """
        Init SmithWidget instance

        :param application: Application instance
        :param mutex: QMutex instance
        :param parent: MainWindow instance
        """
        super().__init__(parent=parent)
        self.setupUi(self)

        self.application = application
        self._ = self.application.translator.gettext
        self.mutex = mutex

        self.account: Optional[Account] = None
        self.smith: Optional[Smith] = None
        self.authority_status: AuthorityStatus = AuthorityStatus.OFFLINE
        self.smith_certification_names: Dict[int, str] = {}

        self.invite_account: Optional[Account] = None
        self.certify_smith: Optional[Smith] = None
        self.current_node = self.application.nodes.get(
            self.application.nodes.get_current_url()
        )

        # animated loading icon
        self.loader_movie = QMovie(ICON_LOADER)
        self.loader_movie.start()
        self.loaderIconLabel.setMovie(self.loader_movie)
        loader_icon_size_policy = self.loaderIconLabel.sizePolicy()
        loader_icon_size_policy.setRetainSizeWhenHidden(True)
        self.loaderIconLabel.setSizePolicy(loader_icon_size_policy)
        self.loaderIconLabel.hide()

        ##############################
        # ASYNC METHODS
        ##############################
        self.fetch_all_from_network_async_qworker = AsyncQWorker(
            self.fetch_all_from_network, self.mutex
        )
        self.fetch_all_from_network_async_qworker.finished.connect(
            self._on_finished_fetch_all_from_network
        )
        self.fetch_certification_names_from_network_async_qworker = AsyncQWorker(
            self.fetch_certification_names_from_network, self.mutex
        )
        self.fetch_certification_names_from_network_async_qworker.finished.connect(
            self._on_finished_fetch_certification_names_from_network
        )
        self.rotate_keys_async_worker = AsyncQWorker(
            self.network_rotate_keys, self.mutex
        )
        self.rotate_keys_async_worker.finished.connect(
            self._on_network_rotate_keys_finished
        )
        self.publish_keys_async_worker = AsyncQWorker(
            self.network_publish_keys, self.mutex
        )
        self.publish_keys_async_worker.finished.connect(
            self._on_network_publish_keys_finished
        )
        self.invite_member_async_qworker = AsyncQWorker(
            self.network_invite_member, self.mutex
        )
        self.invite_member_async_qworker.finished.connect(
            self._on_network_invite_member_finished
        )
        self.accept_invitation_async_worker = AsyncQWorker(
            self.network_accept_invitation, self.mutex
        )
        self.accept_invitation_async_worker.finished.connect(
            self._on_network_invite_member_finished
        )
        self.certify_smith_async_worker = AsyncQWorker(
            self.network_certify_smith, self.mutex
        )
        self.certify_smith_async_worker.finished.connect(
            self._on_network_certify_smith_finished
        )
        self.go_online_async_worker = AsyncQWorker(self.network_go_online, self.mutex)
        self.go_online_async_worker.finished.connect(
            self._on_network_go_online_finished
        )
        self.go_offline_async_worker = AsyncQWorker(self.network_go_offline, self.mutex)
        self.go_offline_async_worker.finished.connect(
            self._on_network_go_offline_finished
        )

        # events
        self.accountComboBox.activated.connect(self.on_account_combobox_index_changed)
        self.refreshSmithButton.clicked.connect(self._on_refresh_smith_button_clicked)
        self.rotateKeysButton.clicked.connect(self._on_rotate_key_button_clicked)
        self.publishKeysButton.clicked.connect(self._on_publish_key_button_clicked)
        self.goOnlineButton.clicked.connect(self._go_online_button_clicked)
        self.goOfflineButton.clicked.connect(self._go_offline_button_clicked)
        self.acceptInvitationButton.clicked.connect(
            self._on_accept_invitation_button_clicked
        )
        self.inviteButton.clicked.connect(self._on_invite_member_button_clicked)
        self.inviteAccountComboBox.activated.connect(
            self.on_invite_account_combobox_index_changed
        )
        self.certifyButton.clicked.connect(self._on_certify_smith_button_clicked)
        self.certifySmithComboBox.activated.connect(
            self.on_certify_smith_combobox_index_changed
        )

        # subscribe to application events
        self.application.event_dispatcher.add_event_listener(
            CurrencyEvent.EVENT_TYPE_CHANGED, self._on_currency_event
        )

        self.application.event_dispatcher.add_event_listener(
            AccountEvent.EVENT_TYPE_ADD, self.on_add_account_event
        )
        self.application.event_dispatcher.add_event_listener(
            AccountEvent.EVENT_TYPE_DELETE, self.on_delete_account_event
        )
        self.application.event_dispatcher.add_event_listener(
            AccountEvent.EVENT_TYPE_UPDATE, self.on_update_account_event
        )

        # populate form
        self.init_account_combo_box()
        self.init_invite_account_combo_box()
        self.init_certify_smith_combo_box()

        self._update_ui()

    def update_account(self, account: Optional[Account]) -> None:
        """
        Update account and smith and authority status and certification list

        :param account: New account
        :return:
        """
        self.account = account
        self.authority_status = AuthorityStatus.OFFLINE

        if self.account is None:
            self.smith = None
        else:
            self.smith = None
            identity_index = self.application.identities.get_index_by_address(
                self.account.address
            )
            if identity_index is not None:
                # get smith status
                self.smith = self.application.smiths.get(identity_index)

            if self.smith is not None:
                self.authority_status = self.application.authorities.get_status(
                    self.smith.identity_index
                )
                if self.application.connections.indexer.is_connected():
                    self.fetch_certification_names_from_network_async_qworker.start()

        # exclude new operating account from dependant list
        self.init_invite_account_combo_box()
        self.init_certify_smith_combo_box()

    def init_account_combo_box(self) -> None:
        """
        Init combobox with validated identity accounts (with wallets)

        :return:
        """
        self.accountComboBox.clear()
        self.accountComboBox.addItem("-", userData=None)

        for account in self.application.accounts.get_list():
            identity = self.application.identities.get_by_address(account.address)
            if (
                identity is not None
                and identity.status == IdentityStatus.MEMBER
                and self.application.wallets.exists(account.address)
            ):
                self.accountComboBox.addItem(
                    account.name if account.name is not None else account.address,
                    userData=account.address,
                )

        self.account = None
        preference_account_address_selected = self.application.preferences.get(
            SMITH_SELECTED_ACCOUNT_ADDRESS
        )
        if preference_account_address_selected is not None:
            preference_account_selected = self.application.accounts.get_by_address(
                preference_account_address_selected
            )
            if preference_account_selected is not None:
                index = self.accountComboBox.findData(
                    preference_account_address_selected
                )
                if index > -1:
                    self.accountComboBox.setCurrentIndex(index)
                    self.update_account(preference_account_selected)
                else:
                    self.application.preferences.set(
                        SMITH_SELECTED_ACCOUNT_ADDRESS, None
                    )

    def on_account_combobox_index_changed(self):
        """
        Triggered when account selection is changed

        :return:
        """
        address = self.accountComboBox.currentData()
        if address is not None:
            self.update_account(self.application.accounts.get_by_address(address))
        else:
            self.update_account(None)

        self._update_ui()

        self.application.repository.preferences.set(
            SMITH_SELECTED_ACCOUNT_ADDRESS,
            address,
        )

    def init_invite_account_combo_box(self) -> None:
        """
        Init combobox with validated identity accounts (not smith) to invite to be smith

        :return:
        """
        self.inviteAccountComboBox.clear()
        self.inviteAccountComboBox.addItem("-", userData=None)

        for account in self.application.accounts.get_list():
            if self.account is not None and self.account.address != account.address:
                identity = self.application.identities.get_by_address(account.address)
                if (
                    identity is not None
                    and identity.status == IdentityStatus.MEMBER
                    and not self.application.smiths.exists(identity.index)
                ):
                    self.inviteAccountComboBox.addItem(
                        account.name if account.name is not None else account.address,
                        userData=account.address,
                    )

        self.invite_account = None
        preference_invite_account_address_selected = self.application.preferences.get(
            SMITH_INVITE_SELECTED_ACCOUNT_ADDRESS
        )
        if preference_invite_account_address_selected is not None:
            preference_invite_account_selected = (
                self.application.accounts.get_by_address(
                    preference_invite_account_address_selected
                )
            )
            if preference_invite_account_selected is not None:
                index = self.inviteAccountComboBox.findData(
                    preference_invite_account_address_selected
                )
                if index > -1:
                    self.inviteAccountComboBox.setCurrentIndex(index)
                    self.invite_account = preference_invite_account_selected
                else:
                    self.application.preferences.set(
                        SMITH_INVITE_SELECTED_ACCOUNT_ADDRESS, None
                    )

    def on_invite_account_combobox_index_changed(self):
        """
        Triggered when invite account selection is changed

        :return:
        """
        address = self.inviteAccountComboBox.currentData()
        if address is not None:
            self.invite_account = self.application.accounts.get_by_address(address)
        else:
            self.invite_account = None

        self.application.repository.preferences.set(
            SMITH_INVITE_SELECTED_ACCOUNT_ADDRESS,
            None if self.invite_account is None else self.invite_account.address,
        )
        self._update_ui()

    def init_certify_smith_combo_box(self) -> None:
        """
        Init combobox with smith and pending smith accounts to certify

        :return:
        """
        self.certifySmithComboBox.clear()
        self.certifySmithComboBox.addItem("-", userData=None)

        smiths = [
            smith
            for smith in self.application.smiths.list()
            if (
                smith.status == SmithStatus.SMITH or smith.status == SmithStatus.PENDING
            )
        ]

        for smith in smiths:
            identity = self.application.identities.get(smith.identity_index)
            if identity is not None:
                account = self.application.accounts.get_by_address(identity.address)
                if (
                    account is not None
                    and self.account is not None
                    and account.address != self.account.address
                ):
                    self.certifySmithComboBox.addItem(
                        account.name if account.name is not None else account.address,
                        userData=smith.identity_index,
                    )

        self.certify_smith = None
        preference_certify_smith_identity_index_selected = (
            self.application.preferences.get(SMITH_CERTIFY_SELECTED_IDENTITY_INDEX)
        )
        if preference_certify_smith_identity_index_selected is not None:
            preference_certify_smith_selected = self.application.smiths.get(
                int(preference_certify_smith_identity_index_selected)
            )
            if preference_certify_smith_selected is not None:
                index = self.certifySmithComboBox.findData(
                    preference_certify_smith_identity_index_selected
                )
                if index > -1:
                    self.certifySmithComboBox.setCurrentIndex(index)
                    self.certify_smith = preference_certify_smith_selected
                else:
                    self.application.preferences.set(
                        SMITH_CERTIFY_SELECTED_IDENTITY_INDEX, None
                    )

    def on_certify_smith_combobox_index_changed(self):
        """
        Triggered when certify smith selection is changed

        :return:
        """
        identity_index = self.certifySmithComboBox.currentData()
        if identity_index is not None:
            self.certify_smith = self.application.smiths.get(identity_index)
        else:
            self.certify_smith = None

        self.application.repository.preferences.set(
            SMITH_CERTIFY_SELECTED_IDENTITY_INDEX,
            None if self.certify_smith is None else self.certify_smith.identity_index,
        )
        self._update_ui()

    def _on_rotate_key_button_clicked(self):
        """
        Triggered when user click on rotate keys button

        :return:
        """
        self.rotate_keys_async_worker.start()

    def network_rotate_keys(self):
        """
        Triggered when user click on rotate keys button

        :return:
        """
        self.errorLabel.setText("")
        self.rotateKeysButton.setDisabled(True)
        try:
            self.application.authorities.network_rotate_keys(self.current_node)
        except Exception as exception:
            self.errorLabel.setText(self._(str(exception)))

    def _on_network_rotate_keys_finished(self):
        """
        Triggered when network_rotate_keys is finished

        :return:
        """
        self.sessionKeysTextBrowser.setText(self.current_node.session_keys)
        self.errorLabel.setText("")

        self.rotateKeysButton.setEnabled(True)

    def _on_invite_member_button_clicked(self):
        """
        Triggered when user click on invite button

        :return:
        """
        if self.invite_account is None:
            return

        self.errorLabel.setText("")
        self.loader_movie.start()
        self.loaderIconLabel.show()
        self.inviteButton.setDisabled(True)

        # if account is locked...
        if not self.application.wallets.is_unlocked(self.account.address):
            # ask password...
            dialog_code = AccountUnlockWindow(
                self.application, self.account, self
            ).exec_()
            if dialog_code == QDialog.Rejected:
                self.loaderIconLabel.hide()
                return

        self.invite_member_async_qworker.start()

    def network_invite_member(self):
        """
        Send invite smith command to network

        :return:
        """
        identity_index = self.application.identities.get_index_by_address(
            self.invite_account.address
        )
        try:
            self.application.smiths.network_invite_member(
                self.application.wallets.get_keypair(self.account.address),
                identity_index,
            )
        except Exception as exception:
            logging.exception(exception)
            self.errorLabel.setText(self._(str(exception)))
        else:
            try:
                self.application.smiths.network_update_smith(identity_index)
            except Exception as exception:
                logging.exception(exception)
                self.errorLabel.setText(self._(str(exception)))

    def _on_network_invite_member_finished(self):
        """
        Triggered when network_invite_member is finished

        :return:
        """
        self.loaderIconLabel.hide()
        self.inviteButton.setEnabled(True)
        self.init_invite_account_combo_box()
        self._update_ui()
        time.sleep(self.DELAY_BEFORE_UPDATE_MEMBERSHIP_STATUS_AFTER_REQUEST)
        self.fetch_all_from_network_async_qworker.start()

    def _on_accept_invitation_button_clicked(self):
        """
        Triggered when user click on accept invitation button

        :return:
        """
        if self.account is None:
            return

        self.errorLabel.setText("")
        self.loader_movie.start()
        self.loaderIconLabel.show()
        self.acceptInvitationButton.setDisabled(True)

        # if account is locked...
        if not self.application.wallets.is_unlocked(self.account.address):
            # ask password...
            dialog_code = AccountUnlockWindow(
                self.application, self.account, self
            ).exec_()
            if dialog_code == QDialog.Rejected:
                self.loaderIconLabel.hide()
                return
        self.accept_invitation_async_worker.start()

    def network_accept_invitation(self):
        """
        Send accept smith invitation to network

        :return:
        """
        try:
            self.application.smiths.network_accept_invitation(
                self.application.wallets.get_keypair(self.account.address)
            )
        except Exception as exception:
            self.errorLabel.setText(self._(str(exception)))
            logging.exception(exception)
        else:
            identity_index = self.application.identities.get_index_by_address(
                self.account.address
            )
            try:
                self.smith = self.application.smiths.network_update_smith(
                    identity_index
                )
            except Exception as exception:
                logging.exception(exception)
                self.errorLabel.setText(self._(str(exception)))

    def _on_network_accept_invitation_finished(self):
        """
        Triggered when network_invite_member is finished

        :return:
        """
        self.loaderIconLabel.hide()
        self.acceptInvitationButton.setEnabled(True)
        time.sleep(self.DELAY_BEFORE_UPDATE_MEMBERSHIP_STATUS_AFTER_REQUEST)
        self.fetch_all_from_network_async_qworker.start()

    def _on_certify_smith_button_clicked(self):
        """
        Triggered when user click on certify button

        :return:
        """
        if self.certify_smith is None:
            return

        self.errorLabel.setText("")
        self.loader_movie.start()
        self.loaderIconLabel.show()
        self.certifyButton.setDisabled(True)

        # if account is locked...
        if not self.application.wallets.is_unlocked(self.account.address):
            # ask password...
            dialog_code = AccountUnlockWindow(
                self.application, self.account, self
            ).exec_()
            if dialog_code == QDialog.Rejected:
                self.loaderIconLabel.hide()
                self.certifyButton.setEnabled(True)
                return

        self.certify_smith_async_worker.start()

    def network_certify_smith(self):
        """
        Send certify smith to network

        :return:
        """
        try:
            self.application.smiths.network_certify(
                self.application.wallets.get_keypair(self.account.address),
                self.certify_smith.identity_index,
            )
        except NodeSmithsException as exception:
            self.errorLabel.setText(self._(str(exception)))
        else:
            try:
                self.application.smiths.network_update_smith(
                    self.certify_smith.identity_index
                )
            except Exception as exception:
                self.errorLabel.setText(self._(str(exception)))
                logging.exception(exception)
            else:
                try:
                    self.smith = self.application.smiths.network_update_smith(
                        self.smith.identity_index
                    )
                except Exception as exception:
                    self.errorLabel.setText(self._(str(exception)))
                    logging.exception(exception)

    def _on_network_certify_smith_finished(self):
        """
        Triggered when network_certify_smith is finished

        :return:
        """
        self.loaderIconLabel.hide()
        self.certifyButton.setEnabled(True)
        self._update_ui()

        time.sleep(self.DELAY_BEFORE_UPDATE_MEMBERSHIP_STATUS_AFTER_REQUEST)
        self.fetch_all_from_network_async_qworker.start()

    def _on_publish_key_button_clicked(self):
        """
        Triggered when user click on publish keys button

        :return:
        """

        if self.account is None:
            return

        self.errorLabel.setText("")
        self.loader_movie.start()
        self.loaderIconLabel.show()
        self.publishKeysButton.setDisabled(True)

        # if account is locked...
        if not self.application.wallets.is_unlocked(self.account.address):
            # ask password...
            dialog_code = AccountUnlockWindow(
                self.application, self.account, self
            ).exec_()
            if dialog_code == QDialog.Rejected:
                return

        self.publish_keys_async_worker.start()

    def network_publish_keys(self):
        """
        Publish keys of local node to network

        :return:
        """
        try:
            self.application.authorities.network_publish_session_keys(
                self.application.wallets.get_keypair(self.account.address),
                self.current_node.session_keys,
            )
        except Exception as exception:
            self.errorLabel.setText(self._(str(exception)))
            logging.exception(exception)

    def _on_network_publish_keys_finished(self):
        """
        Triggered when network_publish_keys is finished

        :return:
        """
        self.loaderIconLabel.hide()
        self.publishKeysButton.setEnabled(True)

    def _go_online_button_clicked(self):
        """
        Triggered when user click on go online button

        :return:
        """

        if self.account is None:
            return

        self.errorLabel.setText("")
        self.loader_movie.start()
        self.loaderIconLabel.show()
        self.goOnlineButton.setDisabled(True)

        # if account is locked...
        if not self.application.wallets.is_unlocked(self.account.address):
            # ask password...
            dialog_code = AccountUnlockWindow(
                self.application, self.account, self
            ).exec_()
            if dialog_code == QDialog.Rejected:
                return

        self.go_online_async_worker.start()

    def network_go_online(self):
        """
        Triggered when user click on go online button

        :return:
        """
        try:
            self.application.authorities.network_go_online(
                self.application.wallets.get_keypair(self.account.address)
            )
        except Exception as exception:
            self.errorLabel.setText(self._(str(exception)))

    def _on_network_go_online_finished(self):
        """
        Triggered when network_go_online is finished

        :return:
        """
        self.loaderIconLabel.hide()
        self.goOnlineButton.setEnabled(True)

        time.sleep(self.DELAY_BEFORE_UPDATE_MEMBERSHIP_STATUS_AFTER_REQUEST)
        self.fetch_all_from_network_async_qworker.start()

    def _go_offline_button_clicked(self):
        """
        Triggered when user click on go offline button

        :return:
        """

        if self.account is None:
            return

        self.errorLabel.setText("")
        self.loader_movie.start()
        self.loaderIconLabel.show()
        self.goOfflineButton.setDisabled(True)

        # if account is locked...
        if not self.application.wallets.is_unlocked(self.account.address):
            # ask password...
            dialog_code = AccountUnlockWindow(
                self.application, self.account, self
            ).exec_()
            if dialog_code == QDialog.Rejected:
                return

        self.go_offline_async_worker.start()

    def network_go_offline(self):
        """
        Triggered when user click on go offline button

        :return:
        """
        try:
            self.application.authorities.network_go_offline(
                self.application.wallets.get_keypair(self.account.address)
            )
        except Exception as exception:
            self.errorLabel.setText(self._(str(exception)))

    def _on_network_go_offline_finished(self):
        """
        Triggered when network_go_offline is finished

        :return:
        """
        self.loaderIconLabel.hide()
        self.goOfflineButton.setEnabled(True)

        time.sleep(self.DELAY_BEFORE_UPDATE_MEMBERSHIP_STATUS_AFTER_REQUEST)
        self.fetch_all_from_network_async_qworker.start()

    def _on_refresh_smith_button_clicked(self, _):
        """ """
        self.fetch_all_from_network_async_qworker.start()

    def fetch_all_from_network(self):
        """
        Update identities, smiths and authorities from current url connection

        :return:
        """
        self.loader_movie.start()
        self.loaderIconLabel.show()

        addresses = [
            account.address for account in self.application.accounts.get_list()
        ]
        try:
            self.application.identities.network_update_identities(addresses)
        except Exception as exception:
            self.errorLabel.setText(self._(str(exception)))
            logging.exception(exception)
        else:
            identity_indice = self.application.identities.list_indice()
            try:
                self.application.smiths.network_update_smiths(identity_indice)
            except Exception as exception:
                self.errorLabel.setText(self._(str(exception)))
                logging.exception(exception)
            else:
                try:
                    self.application.authorities.network_get_all()
                except Exception as exception:
                    self.errorLabel.setText(self._(str(exception)))
                    logging.exception(exception)

    def _on_finished_fetch_all_from_network(self):
        """
        Triggered when AsyncWorker is finished

        :return:
        """
        self.init_account_combo_box()
        self.init_invite_account_combo_box()
        self.init_certify_smith_combo_box()

        self.refreshSmithButton.setEnabled(True)
        self.loaderIconLabel.hide()

        self._update_ui()

    def fetch_certification_names_from_network(self):
        """
        Load certification identity names from current url connection

        :return:
        """
        if self.smith is not None:
            indice = list(
                set(
                    self.smith.certifications_issued
                    + self.smith.certifications_received
                )
            )
            self.smith_certification_names = (
                self.application.identities.indexer_identities.get_identity_names(
                    indice
                )
            )

    def _on_finished_fetch_certification_names_from_network(self):
        """
        Triggered when AsyncWorker is finished

        :return:
        """
        logging.debug("Smith widget update")

        self._update_ui()

    def _update_ui(self):
        """
        Update node infos in UI

        :return:
        """
        display_smith_status = {
            SmithStatus.INVITED.value: self._("Invited"),
            SmithStatus.PENDING.value: self._("Pending"),
            SmithStatus.SMITH.value: self._("Smith"),
            SmithStatus.EXCLUDED.value: self._("Excluded"),
        }

        # validator node
        if self.current_node.unsafe_api_exposed is True:
            self.validatorNodeGroupBox.show()
        else:
            self.validatorNodeGroupBox.hide()

        self.urlValueLabel.setText(self.current_node.url)

        if self.current_node.session_keys is not None:
            self.sessionKeysTextBrowser.setText(self.current_node.session_keys)
        else:
            self.sessionKeysTextBrowser.setText("")

        # rotate keys only available on localhost via an ssh tunnel or other method...
        self.rotateKeysButton.setEnabled(
            "localhost" in self.application.nodes.get_current_url()
        )

        # disable all buttons
        self.publishKeysButton.setDisabled(True)
        self.inviteButton.setDisabled(True)
        self.inviteAccountComboBox.setDisabled(True)
        self.acceptInvitationButton.setDisabled(True)
        self.certifySmithComboBox.setDisabled(True)
        self.goOnlineButton.setDisabled(True)
        self.goOfflineButton.setDisabled(True)

        if self.account is not None:
            self.refreshSmithButton.setEnabled(True)
            if self.current_node.session_keys is not None:
                self.publishKeysButton.setEnabled(True)
            if self.smith is None:
                pass
            elif self.smith.status == SmithStatus.INVITED:
                self.acceptInvitationButton.setEnabled(True)
            elif self.smith.status == SmithStatus.SMITH:
                self.inviteButton.setEnabled(True)
                if self.inviteAccountComboBox.count() > 1:
                    self.inviteAccountComboBox.setEnabled(True)
                if self.certifySmithComboBox.count() > -1:
                    self.certifySmithComboBox.setEnabled(True)
                self.goOnlineButton.setEnabled(
                    self.authority_status == AuthorityStatus.OFFLINE
                )
                self.goOfflineButton.setEnabled(
                    self.authority_status == AuthorityStatus.ONLINE
                )

        if self.smith is not None:
            status_string = display_smith_status[self.smith.status.value]
            if self.smith.expire_on is not None:
                expire_on_localized_datetime_string = self.locale().toString(
                    self.smith.expire_on,
                    QLocale.dateTimeFormat(self.locale(), QLocale.ShortFormat),
                )
                status_string = (
                    f"{status_string} ({expire_on_localized_datetime_string})"
                )
            self.membershipValueLabel.setText(status_string)

            self.certifiersListWidget.clear()
            for certifier_identity_index in self.smith.certifications_received:
                identity = self.application.identities.get(certifier_identity_index)
                if identity is not None:
                    account = self.application.accounts.get_by_address(identity.address)
                    if account is not None and account.name is not None:
                        self.certifiersListWidget.addItem(account.name)
                else:
                    if certifier_identity_index in self.smith_certification_names:
                        self.certifiersListWidget.addItem(
                            f"{self.smith_certification_names[certifier_identity_index]}#{certifier_identity_index}"
                        )
                    else:
                        self.certifiersListWidget.addItem(
                            f"#{certifier_identity_index}"
                        )

            self.certifiedListWidget.clear()
            for certified_identity_index in self.smith.certifications_issued:
                identity = self.application.identities.get(certified_identity_index)
                if identity is not None:
                    account = self.application.accounts.get_by_address(identity.address)
                    if account is not None and account.name is not None:
                        self.certifiedListWidget.addItem(account.name)
                else:
                    if certified_identity_index in self.smith_certification_names:
                        self.certifiedListWidget.addItem(
                            f"{self.smith_certification_names[certified_identity_index]}#{certified_identity_index}"
                        )
                    else:
                        self.certifiedListWidget.addItem(f"#{certified_identity_index}")
        else:
            self.membershipValueLabel.setText(self._("No"))
            # clear certification list
            self.certifiersListWidget.clear()
            self.certifiedListWidget.clear()

        if self.authority_status == AuthorityStatus.OFFLINE:
            self.authorityValueLabel.setText(self._("No"))
        elif self.authority_status == AuthorityStatus.INCOMING:
            self.authorityValueLabel.setText(self._("Incoming..."))
        elif self.authority_status == AuthorityStatus.ONLINE:
            self.authorityValueLabel.setText(self._("Online"))
        elif self.authority_status == AuthorityStatus.OUTGOING:
            self.authorityValueLabel.setText(self._("Outgoing..."))

    def _on_currency_event(self, _):
        """
        When a currency event is triggered

        :param _: CurrencyEvent instance
        :return:
        """
        self.init_account_combo_box()
        self.init_invite_account_combo_box()
        self.init_certify_smith_combo_box()
        if self.account is not None:
            self.fetch_all_from_network_async_qworker.start()

        self._update_ui()

    def on_connections_event(self, _):
        """
        Triggered when the network connection if connected/disconnected

        :param _: ConnectionsEvent instance
        :return:
        """

        self.current_node = self.application.nodes.get(
            self.application.nodes.get_current_url()
        )
        self.init_account_combo_box()
        self._update_ui()

    def on_add_account_event(self, _):
        """
        Add account is selectors when account is created

        :return:
        """
        self.init_account_combo_box()
        self.init_invite_account_combo_box()
        self.init_certify_smith_combo_box()

    def on_delete_account_event(self, _):
        """
        Remove account from selector when account is deleted

        :return:
        """
        self.init_account_combo_box()
        self.init_invite_account_combo_box()
        self.init_certify_smith_combo_box()

        self._update_ui()

    def on_update_account_event(self, _):
        """
        Update account on page and selector when account is updated

        :return:
        """
        self.init_account_combo_box()
        self.init_invite_account_combo_box()
        self.init_certify_smith_combo_box()

        self._update_ui()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    qapp = QApplication(sys.argv)

    application_ = Application(DATA_PATH)

    main_window = QMainWindow()
    main_window.show()
    validator_node = Node(url="ws://localhost:9944")
    if application_.nodes.get(validator_node.url) is None:
        application_.nodes.add(validator_node)
    application_.nodes.set_current_url(validator_node.url)
    main_window.setCentralWidget(SmithWidget(application_, QMutex(), main_window))

    sys.exit(qapp.exec_())
