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
from typing import Optional

from PyQt5.QtCore import QLocale, QMutex, pyqtSignal
from PyQt5.QtWidgets import QDialog, QWidget

from tikka.domains.application import Application
from tikka.domains.entities.technical_committee import TechnicalCommitteeProposal
from tikka.slots.pyqt.entities.constants import (
    TECHNICAL_COMMITTEE_SELECTED_ACCOUNT_ADDRESS,
)
from tikka.slots.pyqt.entities.worker import AsyncQWorker
from tikka.slots.pyqt.resources.gui.widgets.technical_committee_proposal_rc import (
    Ui_TechnicalCommitteeProposalWidget,
)
from tikka.slots.pyqt.windows.account_unlock import AccountUnlockWindow


class TechnicalCommitteeProposalWidget(QWidget, Ui_TechnicalCommitteeProposalWidget):
    """
    TechnicalCommitteeProposalWidget class
    """

    vote_for_proposal_done = pyqtSignal()

    def __init__(
        self,
        application: Application,
        proposal: TechnicalCommitteeProposal,
        mutex: QMutex,
        parent: Optional[QWidget] = None,
    ) -> None:
        """
        Init TechnicalCommitteeWidget instance

        :param application: TechnicalCommitteeProposal instance
        :param proposal: Application instance
        :param mutex: QMutex instance
        :param parent: QWidget instance
        """
        super().__init__(parent=parent)
        self.setupUi(self)

        self.application = application
        self._ = self.application.translator.gettext
        self.mutex = mutex

        self.proposal = proposal
        self.vote = False
        self.proposalGroupBox.setTitle(self.proposal.hash)

        self.callIndexValueLabel.setText(str(self.proposal.call.index))
        self.callHashValueLabel.setText(self.proposal.call.hash)
        self.callModuleValueLabel.setText(str(self.proposal.call.module))
        self.callFunctionValueLabel.setText(str(self.proposal.call.function))
        self.callArgumentsValueLabel.setText(str(self.proposal.call.args))

        self.votingIndexValueLabel.setText(str(self.proposal.voting.index))
        self.votingThresholdValueLabel.setText(str(self.proposal.voting.threshold))
        yes_address_names = []
        for address in self.proposal.voting.ayes:
            account = self.application.accounts.get_by_address(address)
            if account is not None:
                yes_address_names.append(
                    f"{address}{' - ' + account.name if account.name is not None else ''}"
                )
        self.votingAyesValueLabel.setText("\n".join(yes_address_names))
        no_address_names = []
        for address in self.proposal.voting.nays:
            account = self.application.accounts.get_by_address(address)
            if account is not None:
                no_address_names.append(
                    f"{address}{' - ' + account.name if account.name is not None else ''}"
                )
        self.votingNaysValueLabel.setText("\n".join(no_address_names))
        end_localized_datetime_string = self.locale().toString(
            self.proposal.voting.end,
            QLocale.dateTimeFormat(self.locale(), QLocale.ShortFormat),
        )
        self.votingEndValueLabel.setText(end_localized_datetime_string)

        # events
        self.yesButton.clicked.connect(self._on_yes_button_clicked)
        self.noButton.clicked.connect(self._on_no_button_clicked)

        # async method
        self.network_vote_async_worker = AsyncQWorker(
            self.network_vote_for_proposal, self.mutex
        )
        self.network_vote_async_worker.finished.connect(
            self._on_network_vote_async_worker_finished
        )

    def _on_yes_button_clicked(self, _):
        """
        Triggered when user click on Yes Button

        :param _:
        :return:
        """
        self.vote = True
        self.network_vote_async_worker.start()

    def _on_no_button_clicked(self, _):
        """
        Triggered when user click on No Button

        :param _:
        :return:
        """
        self.vote = False
        self.network_vote_async_worker.start()

    def network_vote_for_proposal(self):
        """
        Vote and refresh data of technical committee from network

        :return:
        """
        self.errorLabel.setText("")
        preference_account_address_selected = self.application.preferences.get(
            TECHNICAL_COMMITTEE_SELECTED_ACCOUNT_ADDRESS
        )
        if preference_account_address_selected is None:
            self.errorLabel.setText(self._("No technical committee account selected"))
            return

        account = self.application.accounts.get_by_address(
            preference_account_address_selected
        )
        if account is None:
            self.errorLabel.setText(self._("Unknown account"))
            return

        # if account is locked...
        if not self.application.wallets.is_unlocked(
            preference_account_address_selected
        ):
            # ask password...
            dialog_code = AccountUnlockWindow(self.application, account, self).exec_()
            if dialog_code == QDialog.Rejected:
                return

        try:
            self.application.technical_committee.network.vote(
                self.application.wallets.get_keypair(account.address),
                self.proposal,
                self.vote,
            )
        except Exception as exception:
            self.errorLabel.setText(self._(str(exception)))
            logging.exception(exception)

    def _on_network_vote_async_worker_finished(self):
        """
        Triggered when async worker is finished

        :return:
        """
        self.vote_for_proposal_done.emit()
