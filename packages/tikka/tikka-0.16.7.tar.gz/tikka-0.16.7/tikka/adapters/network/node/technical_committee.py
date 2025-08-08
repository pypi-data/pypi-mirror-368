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
import json
import logging
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, List

from tikka.domains.entities.technical_committee import (
    TechnicalCommitteeCall,
    TechnicalCommitteeMember,
    TechnicalCommitteeProposal,
    TechnicalCommitteeVoting,
)
from tikka.interfaces.adapters.network.connection import NetworkConnectionError
from tikka.interfaces.adapters.network.node.technical_committee import (
    NodeTechnicalCommitteeException,
    NodeTechnicalCommitteeInterface,
)
from tikka.libs.keypair import Keypair

if TYPE_CHECKING:
    from tikka.adapters.network.node.node import NetworkNode


class NodeTechnicalCommittee(NodeTechnicalCommitteeInterface):
    """
    NodeTechnicalCommittee class
    """

    def __init__(self, node: "NetworkNode") -> None:
        """
        Use NetworkNodeInterface to request/send smiths information

        :param node: NetworkNodeInterface instance
        :return:
        """
        self.node = node

    def members(self) -> List[TechnicalCommitteeMember]:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            NodeTechnicalCommitteeInterface.members.__doc__
        )
        if (
            not self.node.connection.is_connected()
            or self.node.connection.client is None
        ):
            raise NodeTechnicalCommitteeException(NetworkConnectionError())

        try:
            member_addresses = self.node.connection.client.query(
                "TechnicalCommittee", "Members"
            )
        except Exception as exception:
            logging.exception(exception)
            raise NodeTechnicalCommitteeException(exception)

        members = []
        if member_addresses is not None:
            try:
                identities = self.node.identities.get_identities(member_addresses)
            except Exception as exception:
                logging.exception(exception)
                raise NodeTechnicalCommitteeException(exception)

            for address, identity in identities.items():
                members.append(
                    TechnicalCommitteeMember(
                        address=address,
                        identity_index=identity.index if identity else None,  # type: ignore
                    )
                )

        return members

    def proposals(self) -> List[TechnicalCommitteeProposal]:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            NodeTechnicalCommitteeInterface.proposals.__doc__
        )
        if (
            not self.node.connection.is_connected()
            or self.node.connection.client is None
        ):
            raise NodeTechnicalCommitteeException(NetworkConnectionError())

        try:
            result = self.node.connection.client.query(
                "TechnicalCommittee", "Proposals"
            )
        except Exception as exception:
            logging.exception(exception)
            raise NodeTechnicalCommitteeException(exception)

        proposal_hash_256_list = result or []

        try:
            current_block = self.node.connection.client.rpc_request(  # type: ignore
                "system_syncState", []
            ).get("result")["currentBlock"]
        except Exception as exception:
            logging.exception(exception)
            raise NodeTechnicalCommitteeException(exception)

        try:
            result = self.node.connection.client.get_constant(
                "Babe", "ExpectedBlockTime"
            )
        except Exception as exception:
            logging.exception(exception)
            raise NodeTechnicalCommitteeException(exception)

        block_duration_in_ms = result
        current_time = datetime.now()

        proposals = []
        for proposal_hash_256 in proposal_hash_256_list:

            # fetch Voting
            try:
                result = self.node.connection.client.query(
                    "TechnicalCommittee", "Voting", [proposal_hash_256]
                )
            except Exception as exception:
                logging.exception(exception)
                raise NodeTechnicalCommitteeException(exception)

            block_diff = result["end"] - current_block
            if block_diff < 0:
                block_time = current_time - timedelta(
                    milliseconds=abs(block_diff) * block_duration_in_ms
                )
            else:
                block_time = current_time + timedelta(
                    milliseconds=abs(block_diff) * block_duration_in_ms
                )

            voting = TechnicalCommitteeVoting(
                result["index"],
                result["threshold"],
                result["ayes"],
                result["nays"],
                block_time,
            )

            # fetch Call
            try:
                result = self.node.connection.client.query(
                    "TechnicalCommittee", "ProposalOf", [proposal_hash_256]
                )
            except Exception as exception:
                logging.exception(exception)
                raise NodeTechnicalCommitteeException(exception)

            call = TechnicalCommitteeCall(
                result["call_index"],
                result["call_hash"],
                result["call_module"],
                result["call_function"],
                json.dumps(result["call_args"]),
            )
            proposal = TechnicalCommitteeProposal(proposal_hash_256, call, voting)

            proposals.append(proposal)

        return proposals

    def vote(
        self, keypair: Keypair, proposal: TechnicalCommitteeProposal, vote: bool
    ) -> None:
        __doc__ = (  # pylint: disable=redefined-builtin, unused-variable
            NodeTechnicalCommitteeInterface.proposals.__doc__
        )
        if (
            not self.node.connection.is_connected()
            or self.node.connection.client is None
        ):
            raise NodeTechnicalCommitteeException(NetworkConnectionError())

        params = {
            "proposal": proposal.hash,
            "index": proposal.voting.index,
            "approve": vote,
        }

        try:
            call = self.node.connection.client.compose_call(
                call_module="TechnicalCommittee",
                call_function="vote",
                call_params=params,
            )
        except Exception as exception:
            logging.exception(exception)
            raise NodeTechnicalCommitteeException(exception)

        try:
            extrinsic = self.node.connection.client.create_signed_extrinsic(
                call=call, keypair=keypair
            )
        except Exception as exception:
            logging.exception(exception)
            raise NodeTechnicalCommitteeException(exception)

        # fixme: code stuck infinitely if no blocks are created on blockchain
        #       should have a timeout option
        try:
            receipt = self.node.connection.client.submit_extrinsic(
                extrinsic, wait_for_inclusion=True
            )
        except Exception as exception:
            logging.exception(exception)
            raise NodeTechnicalCommitteeException(exception)

        logging.debug(
            "Extrinsic '%s' sent and included in block '%s'",
            receipt.extrinsic_hash,
            receipt.block_hash,
        )

        self.node.connection.client.process_events(receipt)

        if not receipt.is_success:
            logging.error(receipt.error_message)
            message = (
                receipt.error_message.docs[0]
                if receipt.error_message
                else "technical_committee.vote error"
            )
            raise NodeTechnicalCommitteeException(message)
