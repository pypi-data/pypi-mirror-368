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
from typing import Dict, List, Optional

from tikka.domains.entities.identity import Certification, Identity
from tikka.interfaces.adapters.network.node.node import NetworkNodeInterface
from tikka.libs.keypair import Keypair


class NodeIdentitiesInterface(abc.ABC):
    """
    NodeIdentitiesInterface class
    """

    @abc.abstractmethod
    def __init__(self, node: NetworkNodeInterface) -> None:
        """
        Use node connection to request identities information

        :param node: NetworkNodeInterface instance
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_identity_index(self, address: str) -> Optional[int]:
        """
        Return the account Identity instance from address if exists

        :param address: Account address
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_identity_indice(self, addresses: List[str]) -> List[Optional[int]]:
        """
        Return the account Identity index from addresses if exists

        :param addresses: Account address
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_identity(self, address: str) -> Optional[Identity]:
        """
        Return the account Identity instance from address if exists

        :param address: Account address
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_identity_by_index(self, index: int) -> Optional[Identity]:
        """
        Return the account Identity instance from index if exists

        :param index: Identity index
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_identities(self, addresses: List[str]) -> Dict[str, Optional[Identity]]:
        """
        Return a dict with address: Identity instance from network

        :param addresses: List of account address
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_identities_by_index(
        self, identity_indice: List[int]
    ) -> Dict[int, Optional[Identity]]:
        """
        Return a dict with identity_index: Identity instance from network

        :param identity_indice: List of identity indice
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def change_owner_key(self, old_keypair: Keypair, new_keypair: Keypair) -> None:
        """
        Change identity owner from old_keypair to new_keypair

        :param old_keypair: Keypair of current identity account
        :param new_keypair: Keypair of new identity account
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def certs_by_receiver(
        self, receiver_address: str, receiver_identity_index: int
    ) -> List[Certification]:
        """
        Return a list of certification received by identity_index

         [
         [identity index, expire on block number],
         [identity index, expire on block number]
         ]

        :param receiver_address: Address of account receiving certs
        :param receiver_identity_index: Index of identity receiving certs
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def claim_uds(self, keypair: Keypair) -> None:
        """
        Add unclaimed UDs of identity to keypair account balance

        :param keypair: Keypair of account
        :return:
        """
        raise NotImplementedError


class NodeIdentitiesException(Exception):
    """
    NodeIdentitiesException class
    """
