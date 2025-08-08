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

from PyQt5.QtCore import QMutex
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget

from tikka.domains.application import Application
from tikka.domains.entities.constants import AMOUNT_UNIT_KEY, DATA_PATH
from tikka.domains.entities.events import UnitEvent
from tikka.slots.pyqt.entities.constants import SELECTED_UNIT_PREFERENCES_KEY
from tikka.slots.pyqt.entities.worker import AsyncQWorker
from tikka.slots.pyqt.resources.gui.widgets.currency_rc import Ui_currencyWidget


class CurrencyWidget(QWidget, Ui_currencyWidget):
    """
    CurrencyWidget class
    """

    def __init__(
        self,
        application: Application,
        mutex: QMutex,
        parent: Optional[QWidget] = None,
    ):
        """
        Init currency widget

        :param application: Application instance
        :param mutex: QMutex instance
        :param parent: QWidget instance
        """
        super().__init__(parent=parent)
        self.setupUi(self)

        self.application = application
        self._ = self.application.translator.gettext
        self.mutex = mutex
        self._update_ui()

        ##############################
        # ASYNC METHODS
        ##############################
        # Create a QWorker object
        self.fetch_from_network_async_qworker = AsyncQWorker(
            self.fetch_from_network, self.mutex
        )
        self.fetch_from_network_async_qworker.finished.connect(
            self._on_finished_fetch_from_network
        )

        # events
        self.refreshButton.clicked.connect(self.fetch_from_network_async_qworker.start)

        # application events
        self.application.event_dispatcher.add_event_listener(
            UnitEvent.EVENT_TYPE_CHANGED, lambda e: self._update_ui()
        )

    def fetch_from_network(self):
        """
        Fetch last currency data from the network

        :return:
        """
        self.errorLabel.setText("")
        self.refreshButton.setEnabled(False)
        try:
            self.application.currencies.network_update_properties()
        except Exception as exception:
            self.errorLabel.setText(self._(str(exception)))

    def _on_finished_fetch_from_network(self):
        """
        Triggered when async request fetch_from_network is finished

        :return:
        """
        logging.debug("Currency widget update")

        self.refreshButton.setEnabled(True)
        self._update_ui()

    def _get_duration_localized_string(self, seconds: int) -> str:
        """
        Return a human-readable duration string showing all significant time units.

        Examples:
            3661 seconds -> "1 hour 1 minute 1 second"
            86461 seconds -> "1 day 1 minute 1 second"
            0 seconds -> "0 seconds"

        :param seconds: Duration in seconds
        :return: Localized duration string
        """
        if seconds == 0:
            return self._("0 seconds")

        units = [
            (self._("year"), self._("years"), 60 * 60 * 24 * 365),
            (self._("month"), self._("months"), 60 * 60 * 24 * 30),
            (self._("week"), self._("weeks"), 60 * 60 * 24 * 7),
            (self._("day"), self._("days"), 60 * 60 * 24),
            (self._("hour"), self._("hours"), 60 * 60),
            (self._("minute"), self._("minutes"), 60),
            (self._("second"), self._("seconds"), 1),
        ]

        parts = []
        remaining_seconds = seconds

        for singular, plural, unit_seconds in units:
            if remaining_seconds >= unit_seconds:
                value = remaining_seconds // unit_seconds
                remaining_seconds %= unit_seconds
                unit = plural if value > 1 else singular
                parts.append(f"{value} {unit}")

        # if we have parts we join them else display 0
        return " ".join(parts) if parts else self._("0 seconds")

    def _update_ui(self):
        """
        Update UI values

        :return:
        """
        unit_amount = self.application.amounts.get_amount(AMOUNT_UNIT_KEY)
        unit_preference = self.application.repository.preferences.get(
            SELECTED_UNIT_PREFERENCES_KEY
        )
        if unit_preference is not None:
            selected_amount = self.application.amounts.get_amount(unit_preference)
        else:
            selected_amount = self.application.amounts.get_amount(AMOUNT_UNIT_KEY)

        # Currency parameters
        currency = self.application.currencies.get_current()
        self.nameValueLabel.setText(currency.name)
        self.symbolValueLabel.setText(currency.token_symbol)

        self.universalDividendValueLabel.setText(
            "?"
            if currency.universal_dividend is None
            else self.locale().toCurrencyString(
                unit_amount.value(currency.universal_dividend), unit_amount.symbol()
            )
        )
        self.monetaryMassValueLabel.setText(
            "?"
            if currency.monetary_mass is None
            else self.locale().toCurrencyString(
                selected_amount.value(currency.monetary_mass), selected_amount.symbol()
            )
        )
        self.membersValueLabel.setText(
            "?"
            if currency.members_count is None
            else self.locale().toString(currency.members_count)
        )

        # Blockchain parameters
        self.ss58PrefixValueLabel.setText(
            "?" if currency.ss58_format is None else str(currency.ss58_format)
        )

        self.genesisHashValueLabel.setText(
            "?" if currency.genesis_hash is None else currency.genesis_hash
        )

        self.expectedBlockDurationValueLabel.setText(
            "?"
            if currency.block_duration is None
            else self._get_duration_localized_string(currency.block_duration)
        )

        self.expectedEpochDurationValueLabel.setText(
            "?"
            if currency.epoch_duration is None
            else self._get_duration_localized_string(currency.epoch_duration)
        )

        # Identity parameters
        self.automaticRevocationPeriodValueLabel.setText(
            "?"
            if currency.identity_automatic_revocation_period is None
            else self._get_duration_localized_string(
                currency.identity_automatic_revocation_period
            )
        )
        self.minimumDelayBetweenChangingIdentityOwnerAccountValueLabel.setText(
            "?"
            if currency.minimum_delay_between_changing_identity_owner is None
            else self._get_duration_localized_string(
                currency.minimum_delay_between_changing_identity_owner
            )
        )
        self.confirmIdentityPeriodValueLabel.setText(
            "?"
            if currency.confirm_identity_period is None
            else self._get_duration_localized_string(currency.confirm_identity_period)
        )
        self.identityDeletionAfterRevocationValueLabel.setText(
            "?"
            if currency.identity_deletion_after_revocation is None
            else self._get_duration_localized_string(
                currency.identity_deletion_after_revocation
            )
        )
        self.minimumDelayBetweenIdentityCreationValueLabel.setText(
            "?"
            if currency.minimum_delay_between_identity_creation is None
            else self._get_duration_localized_string(
                currency.minimum_delay_between_identity_creation
            )
        )
        self.identityValidationPeriodValueLabel.setText(
            "?"
            if currency.identity_validation_period is None
            else self._get_duration_localized_string(
                currency.identity_validation_period
            )
        )

        # Certification parameters
        self.certificationNumberToBeMemberValueLabel.setText(
            "?"
            if currency.certification_number_to_be_member is None
            else str(currency.certification_number_to_be_member)
        )
        self.minimumCertificationsReceivedToBeCertifierValueLabel.setText(
            "?"
            if currency.epoch_duration is None
            else str(currency.minimum_certifications_received_to_be_certifier)
        )
        self.maximumNumberOfCertificationPerMemberValueLabel.setText(
            "?"
            if currency.maximum_number_of_certifications_per_member is None
            else str(currency.maximum_number_of_certifications_per_member)
        )
        self.validityPeriodOfCertificationValueLabel.setText(
            "?"
            if currency.validity_duration_of_certification is None
            else self._get_duration_localized_string(
                currency.validity_duration_of_certification
            )
        )
        self.minimumDelayBetweenTwoCertificationsValueLabel.setText(
            "?"
            if currency.minimum_delay_between_two_certifications is None
            else self._get_duration_localized_string(
                currency.minimum_delay_between_two_certifications
            )
        )

        # Membership parameters
        self.minimumDelayBetweenTwoMembershipRenewalsValueLabel.setText(
            "?"
            if currency.minimum_delay_between_two_membership_renewals is None
            else self._get_duration_localized_string(
                currency.minimum_delay_between_two_membership_renewals
            )
        )
        self.membershipValidityPeriodValueLabel.setText(
            "?"
            if currency.validity_duration_of_membership is None
            else self._get_duration_localized_string(
                currency.validity_duration_of_membership
            )
        )
        self.maximumDistanceInStepValueLabel.setText(
            "?"
            if currency.maximum_distance_in_step is None
            else str(currency.maximum_distance_in_step)
        )
        self.minimumPercentageOfRemoteReferralMembersToBeMemberValueLabel.setText(
            "?"
            if currency.minimum_percentage_of_remote_referral_members_to_be_member
            is None
            else str(
                f"{currency.minimum_percentage_of_remote_referral_members_to_be_member}%"
            )
        )

        # Smith parameters
        self.maximumCertificationsPerSmithValueLabel.setText(
            "?"
            if currency.maximum_certifications_per_smith is None
            else str(currency.maximum_certifications_per_smith)
        )
        self.numberOfCertificationsToBecomeSmithValueLabel.setText(
            "?"
            if currency.number_of_certifications_to_become_smith is None
            else str(currency.number_of_certifications_to_become_smith)
        )
        self.maximumInactivityDurationAllowedForSmithValueLabel.setText(
            "?"
            if currency.maximum_inactivity_duration_allowed_for_smith is None
            else self._get_duration_localized_string(
                currency.maximum_inactivity_duration_allowed_for_smith
            )
        )

    def _on_refresh_button_clicked_event(self):
        """
        Triggered when user click on refresh button

        :return:
        """
        # Disable button
        self.refreshButton.setEnabled(False)
        # Start the thread
        self.fetch_from_network_async_qworker.start()


if __name__ == "__main__":
    qapp = QApplication(sys.argv)

    application_ = Application(DATA_PATH)

    main_window = QMainWindow()
    main_window.show()

    main_window.setCentralWidget(CurrencyWidget(application_, QMutex(), main_window))

    sys.exit(qapp.exec_())
