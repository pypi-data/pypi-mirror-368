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
from typing import TYPE_CHECKING

from tikka.domains.entities.currency import Currency
from tikka.interfaces.adapters.network.connection import NetworkConnectionError
from tikka.interfaces.adapters.network.node.currency import (
    NodeCurrencyException,
    NodeCurrencyInterface,
)

if TYPE_CHECKING:
    from tikka.adapters.network.node.node import NetworkNode


class NodeCurrency(NodeCurrencyInterface):
    """
    NodeCurrency class
    """

    def __init__(self, node: "NetworkNode") -> None:
        """
        Use NetworkNodeInterface to request/send smiths information

        :param node: NetworkNodeInterface instance
        :return:
        """
        self.node = node

    def get_instance(self) -> Currency:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            NodeCurrencyInterface.get_instance.__doc__
        )
        if (
            not self.node.connection.is_connected()
            or self.node.connection.client is None
        ):
            raise NodeCurrencyException(NetworkConnectionError())

        try:
            chain_name = str(
                self.node.connection.client.rpc_request("system_chain", []).get(
                    "result"
                )
            )
        except Exception as exception:
            logging.exception(exception)
            raise NodeCurrencyException(exception)

        try:
            genesis_hash = self.node.get_genesis_block_hash()
        except Exception as exception:
            logging.exception(exception)
            raise NodeCurrencyException(exception)

        try:
            result = self.node.connection.client.rpc_request(
                "system_properties", []
            ).get("result")
        except Exception as exception:
            logging.exception(exception)
            raise NodeCurrencyException(exception)

        assert result is not None
        token_decimals = result["tokenDecimals"]
        token_symbol = result["tokenSymbol"]

        try:
            multi_result = self.node.connection.client.query_multi(
                [
                    ("UniversalDividend", "CurrentUd", []),
                    ("UniversalDividend", "MonetaryMass", []),
                    ("Membership", "CounterForMembership", []),
                ]
            )
        except Exception as exception:
            logging.exception(exception)
            raise NodeCurrencyException(exception)

        current_ud = multi_result[0]
        monetary_mass = multi_result[1]
        counter_for_membership = multi_result[2]

        expected_block_time_in_seconds = int(
            self.node.connection.client.get_constant("Babe", "ExpectedBlockTime") / 1000
        )
        epoch_duration_in_blocks = self.node.connection.client.get_constant(
            "Babe", "EpochDuration"
        )
        ss58_format = self.node.connection.client.get_constant("System", "SS58Prefix")
        system_infos = self.node.connection.client.get_constant("System", "Version")

        certification_number_to_be_member = self.node.connection.client.get_constant(
            "Wot", "MinCertForMembership"
        )

        minimum_delay_between_two_membership_renewals_in_blocks = (
            self.node.connection.client.get_constant(
                "Membership", "MembershipRenewalPeriod"
            )
        )
        validity_duration_of_membership_in_blocks = (
            self.node.connection.client.get_constant("Membership", "MembershipPeriod")
        )

        minimum_certifications_received_to_be_certifier = (
            self.node.connection.client.get_constant(
                "Certification", "MinReceivedCertToBeAbleToIssueCert"
            )
        )
        validity_duration_of_certification_in_blocks = (
            self.node.connection.client.get_constant("Certification", "ValidityPeriod")
        )
        minimum_delay_between_two_certifications_in_blocks = (
            self.node.connection.client.get_constant("Certification", "CertPeriod")
        )
        maximum_number_of_certifications_per_member = (
            self.node.connection.client.get_constant("Certification", "MaxByIssuer")
        )

        maximum_distance_in_step = self.node.connection.client.get_constant(
            "Distance", "MaxRefereeDistance"
        )
        minimum_percentage_of_remote_referral_members_to_be_member = (
            self.node.connection.client.get_constant(
                "Distance", "MinAccessibleReferees"
            )
            / 10000000
        )

        identity_automatic_revocation_period_in_blocks = (
            self.node.connection.client.get_constant("Identity", "AutorevocationPeriod")
        )
        minimum_delay_between_changing_identity_owner_in_blocks = (
            self.node.connection.client.get_constant("Identity", "ChangeOwnerKeyPeriod")
        )
        confirm_identity_period_in_blocks = self.node.connection.client.get_constant(
            "Identity", "ConfirmPeriod"
        )
        identity_deletion_after_revocation_in_blocks = (
            self.node.connection.client.get_constant("Identity", "DeletionPeriod")
        )
        minimum_delay_between_identity_creation_in_blocks = (
            self.node.connection.client.get_constant("Identity", "IdtyCreationPeriod")
        )
        identity_validation_period_in_blocks = self.node.connection.client.get_constant(
            "Identity", "ValidationPeriod"
        )
        maximum_certifications_per_smith = self.node.connection.client.get_constant(
            "SmithMembers", "MaxByIssuer"
        )
        number_of_certifications_to_become_smith = (
            self.node.connection.client.get_constant(
                "SmithMembers", "MinCertForMembership"
            )
        )
        maximum_inactivity_duration_allowed_for_smith_in_blocks = (
            self.node.connection.client.get_constant(
                "SmithMembers", "SmithInactivityMaxDuration"
            )
        )

        return Currency(
            code_name=system_infos["spec_name"],
            name=chain_name,
            ss58_format=ss58_format,
            token_decimals=token_decimals,
            token_symbol=token_symbol,
            universal_dividend=current_ud,
            monetary_mass=monetary_mass,
            members_count=counter_for_membership,
            block_duration=expected_block_time_in_seconds,
            epoch_duration=epoch_duration_in_blocks * expected_block_time_in_seconds,
            certification_number_to_be_member=certification_number_to_be_member,
            minimum_delay_between_two_membership_renewals=minimum_delay_between_two_membership_renewals_in_blocks
            * expected_block_time_in_seconds,
            validity_duration_of_membership=validity_duration_of_membership_in_blocks
            * expected_block_time_in_seconds,
            minimum_certifications_received_to_be_certifier=minimum_certifications_received_to_be_certifier,
            validity_duration_of_certification=validity_duration_of_certification_in_blocks
            * expected_block_time_in_seconds,
            minimum_delay_between_two_certifications=minimum_delay_between_two_certifications_in_blocks
            * expected_block_time_in_seconds,
            maximum_number_of_certifications_per_member=maximum_number_of_certifications_per_member,
            maximum_distance_in_step=maximum_distance_in_step,
            minimum_percentage_of_remote_referral_members_to_be_member=minimum_percentage_of_remote_referral_members_to_be_member,
            identity_automatic_revocation_period=identity_automatic_revocation_period_in_blocks
            * expected_block_time_in_seconds,
            minimum_delay_between_changing_identity_owner=minimum_delay_between_changing_identity_owner_in_blocks
            * expected_block_time_in_seconds,
            confirm_identity_period=confirm_identity_period_in_blocks
            * expected_block_time_in_seconds,
            identity_deletion_after_revocation=identity_deletion_after_revocation_in_blocks
            * expected_block_time_in_seconds,
            minimum_delay_between_identity_creation=minimum_delay_between_identity_creation_in_blocks
            * expected_block_time_in_seconds,
            identity_validation_period=identity_validation_period_in_blocks
            * expected_block_time_in_seconds,
            maximum_certifications_per_smith=maximum_certifications_per_smith,
            number_of_certifications_to_become_smith=number_of_certifications_to_become_smith,
            maximum_inactivity_duration_allowed_for_smith=maximum_inactivity_duration_allowed_for_smith_in_blocks
            * expected_block_time_in_seconds,
            genesis_hash=genesis_hash,
        )
