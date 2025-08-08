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
from typing import Dict, List

from tikka.domains.entities.authorities import AuthorityStatus
from tikka.interfaces.adapters.network.node.node import NetworkNodeInterface
from tikka.libs.keypair import Keypair


class NodeAuthoritiesInterface(abc.ABC):
    """
    NodeAuthoritiesInterface class
    """

    @abc.abstractmethod
    def __init__(self, node: NetworkNodeInterface) -> None:
        """
        Use node connection to request authorities information

        :param node: NetworkNodeInterface instance
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def rotate_keys(self) -> str:
        """
        Rotate Session keys

        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def has_session_keys(self, session_keys: str) -> bool:
        """
        Return True if the current node keystore store private session keys corresponding to public session_keys

        :param session_keys: Session public keys (hex string "0x123XYZ")
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def publish_session_keys(self, keypair: Keypair, session_keys: str) -> None:
        """
        Set/Change in blockchain the session public keys for the Keypair account

        :param keypair: Owner Keypair
        :param session_keys: Session public keys (hex string "0x123XYZ")
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def go_online(self, keypair: Keypair) -> None:
        """
        Start writing blocks with smith account from keypair

        :param keypair: Smith account Keypair
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def go_offline(self, keypair: Keypair) -> None:
        """
        Stop writing blocks with smith account from keypair

        :param keypair: Smith account Keypair
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_status(self, identity_index: int) -> AuthorityStatus:
        """
        Return AuthorityStatus of identity_index

        :param identity_index: Identity index of Smith to get status of
        :return:
        """
        raise NotImplementedError

    @abc.abstractmethod
    def get_all(self) -> Dict[int, List[int]]:
        """
        Return a dict of list of all identity index in incoming authorities

        {
            AuthorityStatus.INCOMING.value: [identity_indice,...],
            AuthorityStatus.ONLINE.value: [identity_indice,...],
            AuthorityStatus.OUTGOING.value": [identity_indice,...],
        }

        :return:
        """
        raise NotImplementedError


class NodeAuthoritiesException(Exception):
    """
    NodeAuthoritiesException
    """
