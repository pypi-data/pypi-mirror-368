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

import abc
from typing import List

from tikka.domains.entities.technical_committee import (
    TechnicalCommitteeMember,
    TechnicalCommitteeProposal,
)
from tikka.interfaces.adapters.network.node.node import NetworkNodeInterface
from tikka.libs.keypair import Keypair


class NodeTechnicalCommitteeInterface(abc.ABC):
    """
    NodeTechnicalCommitteeInterface class
    """

    @abc.abstractmethod
    def __init__(self, node: NetworkNodeInterface) -> None:
        """
        Use node connection to request technical committee information

        :param node: NetworkNodeInterface instance
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def members(self) -> List[TechnicalCommitteeMember]:
        """
        Return list of TechnicalCommitteeMember instance

        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def proposals(self) -> List[TechnicalCommitteeProposal]:
        """
        Return list of Smith instance from list of identity indice

        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def vote(
        self, keypair: Keypair, proposal: TechnicalCommitteeProposal, vote: bool
    ) -> None:
        """
        Send Technical Committee Vote for proposal from Keypair

        :param keypair: Keypair instance
        :param proposal: TechnicalCommitteeProposal instance
        :param vote: True or False
        :return:
        """
        raise NotImplementedError


class NodeTechnicalCommitteeException(Exception):
    """
    NodeTechnicalCommitteeException class
    """
