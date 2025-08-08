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

from typing import List

from tikka.domains.entities.technical_committee import (
    TechnicalCommitteeMember,
    TechnicalCommitteeProposal,
)
from tikka.domains.events import EventDispatcher
from tikka.interfaces.adapters.network.network import NetworkInterface
from tikka.interfaces.adapters.repository.repository import RepositoryInterface
from tikka.libs.keypair import Keypair


class TechnicalCommittee:
    """
    TechnicalCommittee domain class
    """

    def __init__(
        self,
        repository: RepositoryInterface,
        network: NetworkInterface,
        event_dispatcher: EventDispatcher,
    ):
        """
        Init TechnicalCommittee domain

        :param repository: RepositoryInterface instance
        :param network: NodeTechnicalCommitteeInterface instance
        :param event_dispatcher: EventDispatcher instance
        """
        self.repository = repository
        self.network = network
        self.event_dispatcher = event_dispatcher

    def network_update_members(self) -> None:
        """
        Return all members of Technical Committee from network

        :return:
        """
        members = self.network.node.technical_committee.members()
        if self.network.indexer.connection.is_connected():
            indice = [
                member.identity_index
                for member in members
                if member.identity_index is not None
            ]
            identity_names = self.network.indexer.identities.get_identity_names(indice)
            for member in members:
                if member.identity_index in identity_names:
                    member.identity_name = identity_names[member.identity_index]

        self.repository.technical_committee_members.set_list(members)

    def network_update_proposals(self) -> None:
        """
        Return all proposals with voting infos of Technical Committee from network

        :return:
        """
        proposals = self.network.node.technical_committee.proposals()
        self.repository.technical_committee_proposals.set_list(proposals)

    def network_vote(
        self, keypair: Keypair, proposal: TechnicalCommitteeProposal, vote: bool
    ) -> None:
        """
        Send Technical Committee Vote for proposal from Keypair

        :param keypair: Keypair instance
        :param proposal: TechnicalCommitteeProposal instance
        :param vote: True or False
        :return:
        """
        return self.network.node.technical_committee.vote(keypair, proposal, vote)

    def list_members(self):
        """
        Return list of technical committee members

        :return:
        """
        return self.repository.technical_committee_members.list()

    def set_members_list(self, members: List[TechnicalCommitteeMember]) -> None:
        """
        Set list of technical committee members with members

        :return:
        """
        self.repository.technical_committee_members.set_list(members)

    def list_proposals(self):
        """
        Return list of technical committee proposals

        :return:
        """
        return self.repository.technical_committee_proposals.list()

    def set_proposals_list(self, proposals: List[TechnicalCommitteeProposal]) -> None:
        """
        Set list of technical committee proposals with proposals

        :return:
        """
        self.repository.technical_committee_proposals.set_list(proposals)

    def list_member_addresses(self):
        """
        Return list of technical committee member addresses

        :return:
        """
        return [
            technical_committee_member.address
            for technical_committee_member in self.repository.technical_committee_members.list()
        ]
