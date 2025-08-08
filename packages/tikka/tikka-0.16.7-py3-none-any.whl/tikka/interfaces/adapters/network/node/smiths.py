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
from __future__ import annotations

import abc
from typing import TYPE_CHECKING, List, Optional

from tikka.domains.entities.smith import Smith
from tikka.libs.keypair import Keypair

if TYPE_CHECKING:
    from interfaces.adapters.network.node.node import NetworkNodeInterface


class NodeSmithsInterface(abc.ABC):
    """
    NodeSmithsInterface class
    """

    @abc.abstractmethod
    def __init__(self, node: NetworkNodeInterface) -> None:
        """
        Use NetworkNodeInterface to request/send smiths information

        :param node: NetworkNodeInterface instance
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_smith(self, identity_index: int) -> Optional[Smith]:
        """
        Return Smith instance

        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_smiths(self, identity_indice: List[int]) -> List[Optional[Smith]]:
        """
        Return list of Smith instance from list of identity indice

        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def invite(self, keypair: Keypair, identity_index: int) -> None:
        """
        The Keypair account invite a member address to be a smith

        :param keypair: Issuer Keypair
        :param identity_index: Recipient identity index
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def accept_invitation(self, keypair: Keypair) -> None:
        """
        The Keypair account accept an invitation to be a smith

        :param keypair: Invited Keypair
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def certify(self, keypair: Keypair, identity_index: int) -> None:
        """
        The smith account Keypair certify a member address to be a smith

        :param keypair: Issuer Keypair
        :param identity_index: Recipient identity index
        :return:
        """
        raise NotImplementedError


class NodeSmithsException(Exception):
    """
    NodeSmithsException class
    """
