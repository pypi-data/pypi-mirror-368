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
from typing import Dict, List, Optional

from tikka.domains.entities.identity import Certification, Identity, IdentityStatus
from tikka.interfaces.adapters.network.indexer.identities import (
    IndexerIdentitiesInterface,
)
from tikka.interfaces.adapters.network.node.identities import NodeIdentitiesInterface
from tikka.interfaces.adapters.repository.identities import (
    IdentitiesRepositoryInterface,
)
from tikka.libs.keypair import Keypair


class Identities:

    """
    Identities domain class
    """

    def __init__(
        self,
        repository: IdentitiesRepositoryInterface,
        node_identities: NodeIdentitiesInterface,
        indexer_identities: IndexerIdentitiesInterface,
    ):
        """
        Init Identities domain

        :param repository: IdentitiesRepositoryInterface instance
        :param node_identities: NodeIdentitiesInterface instance
        :param indexer_identities: IndexerIdentitiesInterface instance
        """
        self.repository = repository
        self.node_identities = node_identities
        self.indexer_identities = indexer_identities

    @staticmethod
    def create(
        index: int,
        removable_on: int,
        next_creatable_on: int,
        address: str,
        old_address: Optional[str],
        status: IdentityStatus = IdentityStatus.UNCONFIRMED,
        first_eligible_ud: int = 0,
    ):
        """
        Return an identity instance from params

        :param index: Index number in blockchain
        :param removable_on: Identity expiration timestamp
        :param next_creatable_on: Date after which a new identity can be created
        :param address: Account address
        :param old_address: Previous account address
        :param status: Identity status
        :param first_eligible_ud: First elligible UD index
        :return:
        """
        return Identity(
            index=index,
            name=None,
            removable_on=removable_on,
            next_creatable_on=next_creatable_on,
            status=status,
            address=address,
            old_address=old_address,
            first_eligible_ud=first_eligible_ud,
        )

    def add(self, identity: Identity):
        """
        Add identity in repository

        :param identity: Identity instance
        :return:
        """
        self.repository.add(identity)

    def update(self, identity: Identity):
        """
        Update identity in repository

        :param identity: Identity instance
        :return:
        """
        self.repository.update(identity)

    def get(self, index: int) -> Optional[Identity]:
        """
        Get identity instance

        :param index: Identity index
        :return:
        """
        return self.repository.get(index)

    def get_by_address(self, address: str) -> Optional[Identity]:
        """
        Return Identity instance from account address or None

        :param address: Account address
        :return:
        """
        return self.repository.get_by_address(address)

    def get_by_addresses(self, addresses: List[str]) -> Dict[str, Optional[Identity]]:
        """
        Return Identity instance from account address or None

        :param addresses: List of Account addresses
        :return:
        """
        return self.repository.get_by_addresses(addresses)

    def get_index_by_address(self, address: str) -> Optional[int]:
        """
        Return identity index from account address or None

        :param address: Account address
        :return:
        """
        return self.repository.get_index_by_address(address)

    def delete(self, index: int) -> None:
        """
        Delete identity in repository

        :param index: Identity index to delete
        :return:
        """
        self.repository.delete(index)

    def delete_all(self) -> None:
        """
        Delete all identities in repository

        :return:
        """
        self.repository.delete_all()

    def exists(self, index: int) -> bool:
        """
        Return True if identity exists in repository

        :param index: Identity index to check
        :return:
        """
        return self.repository.exists(index)

    def list(self):
        """
        Return list of all identities

        :return:
        """
        return self.repository.list()

    def list_indice(self):
        """
        Return list of all identity indice

        :return:
        """
        return self.repository.list_indice()

    def is_validated(self, index: int) -> bool:
        """
        Return True if identity status is validated

        :param index: Identity index to check
        :return:
        """
        identity = self.get(index)
        if identity is None:
            return False
        return identity.status == IdentityStatus.MEMBER

    def network_update_identity(self, address: str) -> Optional[Identity]:
        """
        Update and return Identity instance by address from network if any

        :param address: Owner account address
        :return:
        """
        identity = self.node_identities.get_identity(address)
        if identity is None:
            old_identity = self.get_by_address(address)
            if old_identity is not None:
                self.delete(old_identity.index)
        else:
            if self.indexer_identities.indexer.connection.is_connected():
                identity.name = self.indexer_identities.get_identity_name(
                    identity.index
                )
            stored_identity = self.get(identity.index)
            if stored_identity is not None:
                self.update(identity)
            else:
                self.add(identity)

        return identity

    def network_get_identity(self, address: str) -> Optional[Identity]:
        """
        Return Identity instance by address from network if any

        :param address: Owner account address
        :return:
        """
        identity = self.node_identities.get_identity(address)

        if identity and self.indexer_identities.indexer.connection.is_connected():
            identity.name = self.indexer_identities.get_identity_name(identity.index)

        return identity

    def network_update_identities(self, addresses: List[str]) -> None:
        """
        Update repository Identities by account address list from network

        :param addresses: Account address list
        :return:
        """
        identities = self.network_get_identities(addresses)
        for address, identity in identities.items():
            if identity is None:
                old_identity = self.get_by_address(address)
                if old_identity is not None:
                    self.delete(old_identity.index)
            else:
                stored_identity = self.get(identity.index)
                if stored_identity is not None:
                    self.update(identity)
                else:
                    self.add(identity)

    def network_get_identities(
        self, addresses: List[str]
    ) -> Dict[str, Optional[Identity]]:
        """
        Return Identity instances by account address list from network

        :param addresses: Account address list
        :return:
        """
        identities = self.node_identities.get_identities(addresses)
        indice = [
            identity.index for identity in identities.values() if identity is not None
        ]
        if self.indexer_identities.indexer.connection.is_connected():
            names = self.indexer_identities.get_identity_names(indice)
            for identity in identities.values():
                if identity is None:
                    continue
                identity.name = names[identity.index]

        return identities

    def network_change_owner_key(
        self, old_keypair: Keypair, new_keypair: Keypair
    ) -> None:
        """
        Change identity owner from old_keypair to new_keypair on blockchain

        :param old_keypair: Keypair of current identity account
        :param new_keypair: Keypair of new identity account
        :return:
        """
        return self.node_identities.change_owner_key(old_keypair, new_keypair)

    def network_get_certs_by_receiver(
        self, receiver_address: str, receiver_identity_index: int
    ) -> Optional[List[Certification]]:
        """
        Get certification (identity index, expire on block number) list for identity index from network if any

        :param receiver_address: Address of receiver account
        :param receiver_identity_index: Identity index of receiver
        :return:
        """
        return self.node_identities.certs_by_receiver(
            receiver_address, receiver_identity_index
        )

    def network_claim_uds(self, keypair: Keypair) -> None:
        """
        Add unclaimed UDs of identity to keypair account balance

        :param keypair: Keypair of account
        :return:
        """
        return self.node_identities.claim_uds(keypair)
