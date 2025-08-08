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
from typing import List, Optional

from tikka.domains.entities.authorities import Authority, AuthorityStatus
from tikka.domains.entities.node import Node
from tikka.domains.nodes import Nodes
from tikka.domains.smiths import Smiths
from tikka.interfaces.adapters.network.node.authorities import NodeAuthoritiesInterface
from tikka.interfaces.adapters.repository.authorities import (
    AuthoritiesRepositoryInterface,
)
from tikka.libs.keypair import Keypair


class Authorities:

    """
    Authorities domain class
    """

    def __init__(
        self,
        repository: AuthoritiesRepositoryInterface,
        network: NodeAuthoritiesInterface,
        nodes: Nodes,
        smiths: Smiths,
    ):
        """
        Init Authorities domain

        :param repository: AuthoritiesRepositoryInterface instance
        :param network: NodeAuthoritiesInterface instance
        :param nodes: Nodes domain instance
        :param smiths: Smiths domain instance
        """
        self.network = network
        self.repository = repository
        self.nodes = nodes
        self.smiths = smiths

    @staticmethod
    def create(identity_index: int, status: AuthorityStatus):
        """
        Return Authority instance from parameters

        :param identity_index: Identity index
        :param status: AuthorityStatus enum
        :return:
        """
        return Authority(identity_index, status)

    def add(self, authority: Authority) -> None:
        """
        Add Authority in repository

        :param authority: Authority instance
        :return:
        """
        self.repository.add(authority)

    def get(self, identity_index: int) -> Optional[Authority]:
        """
        Get Authority by identity index from repository

        :param identity_index: Identity index
        :return:
        """
        return self.repository.get(identity_index)

    def update(self, authority: Authority):
        """
        Update authority in repository

        :param authority: Authority instance
        :return:
        """
        self.repository.update(authority)

    def delete(self, identity_index: int) -> None:
        """
        Delete Authority in repository

        :param identity_index: Identity index to delete
        :return:
        """
        self.repository.delete(identity_index)

    def delete_all(self) -> None:
        """
        Delete all authorities in repository

        :return:
        """
        self.repository.delete_all()

    def exists(self, identity_index: int) -> bool:
        """
        Return True if Authority exists in repository

        :param identity_index: Identity index to check
        :return:
        """
        return self.repository.exists(identity_index)

    def list(self) -> List[Authority]:
        """
        Return list of all Authority in repository

        :return:
        """
        return self.repository.list()

    def get_status(self, identity_index: int) -> AuthorityStatus:
        """
        Return AuthorityStatus enum for identity_index

        :param identity_index: Identity index
        :return:
        """
        if not self.repository.exists(identity_index):
            return AuthorityStatus.OFFLINE

        authority = self.repository.get(identity_index)
        if authority is None:
            return AuthorityStatus.OFFLINE

        return authority.status

    def network_rotate_keys(self, node: Node) -> Optional[str]:
        """
        Change node session keys and return them

        :param node: Node instance
        :return:
        """
        session_keys = self.network.rotate_keys()
        if session_keys is not None:
            node.session_keys = session_keys
            self.nodes.update(node)
        return session_keys

    def network_has_session_keys(self, session_keys: str) -> Optional[bool]:
        """
        Return True if the current node keystore store private session keys corresponding to public session_keys

        :param session_keys: Session public keys (hex string "0x123XYZ")
        :return:
        """
        return self.network.has_session_keys(session_keys)

    def network_publish_session_keys(self, keypair: Keypair, session_keys: str) -> None:
        """
        Set/Change in blockchain the session public keys for the Keypair account

        :param keypair: Owner Keypair
        :param session_keys: Session public keys (hex string "0x123XYZ")
        :return:
        """
        return self.network.publish_session_keys(keypair, session_keys)

    def network_go_online(self, keypair: Keypair) -> None:
        """
        Start writing blocks with smith account from keypair

        :param keypair: Smith account Keypair
        :return:
        """
        return self.network.go_online(keypair)

    def network_go_offline(self, keypair: Keypair) -> None:
        """
        Stop writing blocks with smith account from keypair

        :param keypair: Smith account Keypair
        :return:
        """
        return self.network.go_offline(keypair)

    def network_get_status(self, identity_index: int) -> AuthorityStatus:
        """
        Return AuthorityStatus enum for identity_index

        :param identity_index: Identity index
        :return:
        """
        return self.network.get_status(identity_index)

    def network_get_all(self) -> None:
        """
        Get all authorities by status

        :return:
        """
        network_authorities = self.network.get_all()

        # list of known smith
        smith_identity_indice = [smith.identity_index for smith in self.smiths.list()]
        authorities = self.list()

        # purge obsolete authorities
        for authority in authorities:
            if authority.identity_index not in smith_identity_indice:
                self.delete(authority.identity_index)

        for authority in authorities:
            if (
                authority.identity_index
                in network_authorities[AuthorityStatus.ONLINE.value]
            ):
                authority.status = AuthorityStatus.ONLINE
            elif (
                authority.identity_index
                in network_authorities[AuthorityStatus.INCOMING.value]
            ):
                authority.status = AuthorityStatus.INCOMING
            elif (
                authority.identity_index
                in network_authorities[AuthorityStatus.OUTGOING.value]
            ):
                authority.status = AuthorityStatus.OUTGOING
            else:
                authority.status = AuthorityStatus.OFFLINE
            self.update(authority)

        # new smiths
        authority_identity_indice = [
            authority.identity_index for authority in authorities
        ]
        for identity_index in smith_identity_indice:
            if identity_index not in authority_identity_indice:
                authority = self.create(identity_index, AuthorityStatus.OFFLINE)
                if (
                    authority.identity_index
                    in network_authorities[AuthorityStatus.ONLINE.value]
                ):
                    authority.status = AuthorityStatus.ONLINE
                elif (
                    authority.identity_index
                    in network_authorities[AuthorityStatus.INCOMING.value]
                ):
                    authority.status = AuthorityStatus.INCOMING
                elif (
                    authority.identity_index
                    in network_authorities[AuthorityStatus.OUTGOING.value]
                ):
                    authority.status = AuthorityStatus.OUTGOING
                self.add(authority)
